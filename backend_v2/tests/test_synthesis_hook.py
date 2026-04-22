from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.synthesis import (
    _build_title_map,
    _compress_synthesis_payload,
    _fetch_historical_context,
    text_consolidation_hook,
)
from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.models.enums import HistoricalContextMode
from backend_v2.models.v2_core import SynthesisConfigDTO


@pytest.fixture
def mock_deps() -> MagicMock:
    """Mocked HookDependencies for isolated testing."""
    from backend_v2.models.v2_core import ExecutionRecord, Workflow

    deps = MagicMock(spec=HookDependencies)
    deps.repository = AsyncMock()

    # Mock workflow and execution to bypass Pydantic model_validate errors
    wf_mock = Workflow.model_construct(id="wf_1", steps=[], expected_inputs=[])
    deps.repository.get_workflow_by_id.return_value = wf_mock

    exec_mock = ExecutionRecord.model_construct(id="exec_1", output_profile_id="test_profile")
    deps.repository.get_execution.return_value = exec_mock

    return deps


@pytest.fixture
def mock_profile() -> OutputProfileResponseDTO:
    """Valid standard profile with no sections, to bypass deep validation."""
    return OutputProfileResponseDTO.model_construct(
        id="test_profile",
        name="Test Profile",
        layouts=[],
        visible_extensions=[],
        synthesis=SynthesisConfigDTO.model_construct(
            system_prompt="Test global prompt", historical_context_mode=HistoricalContextMode.DISABLED
        ),
    )


@pytest.mark.asyncio
async def test_target_locale_strictness(mock_deps: MagicMock, mock_profile: OutputProfileResponseDTO) -> None:
    """FAIL-FAST MANDATE:
    If 'target_locale' is missing from metadata, the system MUST abort
    immediately with a 400 Validation Error. No fallbacks allowed.
    """
    mock_deps.repository.get_output_profile_by_id.return_value = mock_profile

    # State missing target_locale
    state_missing = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        metadata={"output_profile_id": "test_profile"},  # Missing target_locale!
        inputs={},
        global_context_vars={},
    )

    with pytest.raises(AppException) as excinfo:
        await text_consolidation_hook(state_missing, mock_deps)  # type: ignore[misc]

    assert excinfo.value.status_code == 400
    assert excinfo.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "target_locale" in excinfo.value.message


@pytest.mark.asyncio
async def test_output_profile_strictness(mock_deps: MagicMock) -> None:
    """FAIL-FAST MANDATE:
    If 'output_profile_id' cannot be resolved in the DB, it MUST fail
    with a 404 Resource Not Found.
    """
    mock_deps.repository.get_output_profile_by_id.return_value = None

    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        metadata={"output_profile_id": "non_existent_profile", "target_locale": "fi"},
        inputs={},
        global_context_vars={},
    )

    with pytest.raises(AppException) as excinfo:
        await text_consolidation_hook(state, mock_deps)  # type: ignore[misc]

    assert excinfo.value.status_code == 404
    assert excinfo.value.details["error_code"] == ErrorCodes.RESOURCE_NOT_FOUND.value
    assert "not found in SSOT database" in excinfo.value.message


# --- UNIT TESTS FOR PURE FUNCTIONS ---


def test_compress_synthesis_payload() -> None:
    """Ensure deep recursive dictionary values (like 'shuffled_atoms', 'quote')
    are completely scrubbed before they reach the LLM, but boolean evaluations remain.
    """
    raw_payload = {
        "metadata": {"shuffled_atoms": [1, 2, 3], "valid_key": "valid_value"},
        "evaluations": [
            {"boolean": True, "quote": "ignore me", "reasoning": "ignore this too"},
            {"boolean": False, "shuffled_atoms": "remove"},
        ],
        "nested": {"quote": "delete", "keep": "this"},
    }

    compressed_json_str = _compress_synthesis_payload(raw_payload)
    import json

    compressed = json.loads(compressed_json_str)

    assert "shuffled_atoms" not in compressed["metadata"]
    assert "valid_key" in compressed["metadata"]
    assert "quote" not in compressed["nested"]
    assert "keep" in compressed["nested"]

    # Token Shield removes evaluations entirely
    assert "evaluations" not in compressed


def test_build_title_map_empty() -> None:
    """If workflow_data is missing, it should just return an empty dict safely."""
    assert _build_title_map(None, [], "en") == {}


@pytest.mark.asyncio
async def test_fetch_historical_context_disabled(mock_deps: MagicMock) -> None:
    """If mode is DISABLED, it should return an empty string without touching the database."""
    result = await _fetch_historical_context(
        mode=HistoricalContextMode.DISABLED,
        inputs={"user_id": "u1"},
        deps=mock_deps,
        state=MagicMock(),
        profile_to_use="default",
    )
    assert result == ""
    mock_deps.repository.get_all_executions.assert_not_called()


# --- INTEGRATION TEST FOR THE ORCHESTRATOR ---


@pytest.mark.asyncio
async def test_text_consolidation_hook_success(
    mock_deps: MagicMock, mock_profile: OutputProfileResponseDTO, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ensure the main orchestrator (hook) successfully calls the LLM, compiles the prompt,
    translates if necessary, and returns a valid HookResult WITHOUT catching random exceptions.
    """
    mock_deps.repository.get_output_profile_by_id.return_value = mock_profile
    mock_deps.repository.get_all.return_value = []  # Mock missing steps/blocks for simplicity

    # State with valid locale and profile
    state = HookState(
        execution_id="exec_1",
        workflow_id="wf_1",
        metadata={"output_profile_id": "test_profile", "target_locale": "en"},
        inputs={"input1": {"reasoning_trace": "test_data"}},
        global_context_vars={},
    )

    # 1. Mock LLMClient.from_strategy
    mock_llm_client = AsyncMock()

    async def mock_from_strategy(*args: Any, **kwargs: Any) -> AsyncMock:
        return mock_llm_client

    monkeypatch.setattr("backend_v2.hooks.synthesis.LLMClient.from_strategy", mock_from_strategy)

    # 2. Mock execute_tool_loop
    class MockToolRes:
        result_data = {
            "synthesized_markdown": "# Mocked Synthesis",
            "section_syntheses": [],
            "cited_sources": ["Source 1"],
            "xai_highlights": [],
        }
        usage = {"completion_tokens": 100}
        audit_traces: list[Any] = []

    mock_execute = AsyncMock(return_value=MockToolRes())
    monkeypatch.setattr("backend_v2.hooks.synthesis.execute_tool_loop", mock_execute)

    # 3. Execute
    result = await text_consolidation_hook(state, mock_deps)  # type: ignore[misc]

    # 4. Assert
    assert result.success is True
    assert result.state_delta is not None
    assert "# Mocked Synthesis" in result.state_delta["synthesized_markdown"]
    assert "Source 1" in result.state_delta["cited_sources"]
    assert result.state_delta["step_metadata_updates"]["token_usage"] == {"completion_tokens": 100}

    # Verify LLM was called with the correct parameters
    mock_execute.assert_called_once()
    call_kwargs = mock_execute.call_args.kwargs
    assert call_kwargs["target_language"] == "en"
    assert call_kwargs["step_name"] == "text_consolidation_hook"

    # Assert that the prompt messages included the compressed inputs
    messages = call_kwargs["messages"]
    assert any("test_data" in m["content"] for m in messages if m["role"] == "user")
