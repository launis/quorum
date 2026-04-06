"""Unit tests for the Synthesis Hook."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.synthesis import SynthesisOutputDTO, text_consolidation_hook


@pytest.fixture
def mock_repo() -> MagicMock:
    repo = MagicMock()
    repo.get_workflow_by_id = AsyncMock()
    return repo


@pytest.fixture
def base_state() -> HookState:
    return HookState(
        execution_id="exe_1",
        workflow_id="wf_1",
        step_id="step_1",
        inputs={
            "content": {"reasoning_trace": "test text abc@example.com"},
            "empty_key": {"reasoning_trace": ""},
            "language": "en",
        },
        global_context_vars={"language": "en"},
        metadata={},
    )


@pytest.mark.asyncio
@patch("backend_v2.hooks.synthesis.LLMClient")
async def test_synthesis_hook_success(
    mock_llm_client_class: MagicMock, mock_repo: MagicMock, base_state: HookState
) -> None:
    """Test that synthesis hook injects config constraints correctly and calls LLM."""
    mock_repo.get_workflow_by_id = AsyncMock()
    mock_repo.get_execution = AsyncMock(return_value=None)
    mock_workflow = {
        "id": "wf_1",
        "default_profile_id": "prf_test",
        "output_profiles": {
            "prf_test": {
                "synthesis": {
                    "length_constraint": 500,
                    "preamble_text": {"en": "Always be concise."},
                    "omit_empty_sections": True,
                    "enable_pii_masking": True,
                }
            }
        },
    }
    mock_repo.get_workflow_by_id.return_value = mock_workflow
    deps = HookDependencies(repository=mock_repo)

    # Setup the mock LLM Client Instance
    mock_client_instance = AsyncMock()
    mock_llm_client_class.from_strategy = AsyncMock(return_value=mock_client_instance)

    # Return (SynthesisOutputDTO, token_usage_dict) from run_structured_task
    mock_dto = SynthesisOutputDTO(synthesized_markdown="Synthesized [1]", cited_sources=["source1"])
    mock_client_instance.run_structured_task.return_value = (mock_dto, {"total_tokens": 100})

    result = await text_consolidation_hook(base_state, deps)  # type: ignore[misc]

    assert result.success is True
    delta = result.state_delta
    assert delta is not None

    # Verify that LLM was called
    mock_client_instance.run_structured_task.assert_called_once()

    # Check if PII was masked (the email inside inputs should be [REDACTED EMAIL])
    call_args = mock_client_instance.run_structured_task.call_args
    messages = call_args.kwargs.get("messages", [])
    user_msg: dict[str, Any] = next((m for m in messages if m["role"] == "user"), {})
    sys_msg: dict[str, Any] = next((m for m in messages if m["role"] == "system"), {})

    assert "[REDACTED EMAIL]" in user_msg.get("content", "")
    assert "abc@example.com" not in user_msg.get("content", "")

    # Check if PII was masked (the email inside inputs should be [REDACTED EMAIL])
    assert "GLOBAL SYNTHESIS LENGTH CONSTRAINT: The global output should be ~500 characters." in sys_msg.get(
        "content", ""
    )
    assert "Always be concise." in sys_msg.get("content", "")

    assert delta["synthesized_markdown"] == "Synthesized [1]"
    assert delta["cited_sources"] == ["source1"]
    assert "token_usage" in delta["step_metadata_updates"]
    assert delta["step_metadata_updates"]["token_usage"]["total_tokens"] == 100


@pytest.mark.asyncio
async def test_synthesis_hook_workflow_not_found(mock_repo: MagicMock, base_state: HookState) -> None:
    """Test that missing workflow throws an AppException."""
    mock_repo.get_workflow_by_id.return_value = None
    deps = HookDependencies(repository=mock_repo)

    with pytest.raises(AppException) as exc_info:
        await text_consolidation_hook(base_state, deps)  # type: ignore[misc]

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
@patch("backend_v2.hooks.synthesis.LLMClient")
async def test_synthesis_hook_multi_profile_routing(
    mock_llm_client_class: MagicMock, mock_repo: MagicMock, base_state: HookState
) -> None:
    """Test that synthesis routes to requested target_profile_id and uses its distinct rules."""
    mock_repo.get_execution = AsyncMock(return_value=None)

    mock_workflow = {
        "id": "wf_1",
        "default_profile_id": "prof_a",
        "output_profiles": {
            "prof_a": {"synthesis": {"length_constraint": 100, "preamble_text": {"en": "Alpha"}}},
            "prof_b": {"synthesis": {"length_constraint": 900, "preamble_text": {"en": "Beta"}}},
        },
    }
    mock_repo.get_workflow_by_id = AsyncMock(return_value=mock_workflow)
    deps = HookDependencies(repository=mock_repo)

    # Force the hook to use prof_b
    base_state.metadata["target_profile_id"] = "prof_b"

    mock_client_instance = AsyncMock()
    mock_llm_client_class.from_strategy = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.run_structured_task.return_value = (
        SynthesisOutputDTO(synthesized_markdown="Beta result", cited_sources=[]),
        {"total_tokens": 50},
    )

    result = await text_consolidation_hook(base_state, deps)  # type: ignore[misc]
    assert result.success is True

    call_args = mock_client_instance.run_structured_task.call_args
    sys_msg: dict[str, Any] = next((m for m in call_args.kwargs.get("messages", []) if m["role"] == "system"), {})

    # Assert Prof B's constraints are found, NOT Prof A's
    assert "900 characters" in sys_msg.get("content", "")
    assert "Beta" in sys_msg.get("content", "")
    assert "Alpha" not in sys_msg.get("content", "")
    assert "100 characters" not in sys_msg.get("content", "")


@pytest.mark.asyncio
@patch("backend_v2.hooks.synthesis.LLMClient")
async def test_synthesis_hook_target_blocks_wildcard_bypass(
    mock_llm_client_class: MagicMock, mock_repo: MagicMock, base_state: HookState
) -> None:
    """Test the dual-layer filter: AI traces are included by *, explicit Python variables bypass the check."""
    mock_repo.get_execution = AsyncMock(return_value=None)

    mock_workflow = {
        "id": "wf_1",
        "default_profile_id": "prof_a",
        "output_profiles": {
            "prof_a": {
                "layouts": [
                    {"target_blocks": ["my_python_math"]},  # explicit callout
                    {"target_blocks": ["*"]},  # wildcard callout
                ]
            }
        },
    }
    mock_repo.get_workflow_by_id = AsyncMock(return_value=mock_workflow)
    deps = HookDependencies(repository=mock_repo)

    base_state = base_state.model_copy(
        update={
            "inputs": {
                "valid_ai_trace": {"reasoning_trace": "AI says hello"},
                "my_python_math": 1337,
                "garbage_metadata": "this should be blocked by wildcard",
            }
        }
    )

    mock_client_instance = AsyncMock()
    mock_llm_client_class.from_strategy = AsyncMock(return_value=mock_client_instance)
    mock_client_instance.run_structured_task.return_value = (
        SynthesisOutputDTO(synthesized_markdown="Summary", cited_sources=[]),
        {"total_tokens": 10},
    )

    result = await text_consolidation_hook(base_state, deps)  # type: ignore[misc]
    assert result.success is True

    call_args = mock_client_instance.run_structured_task.call_args
    user_msg: dict[str, Any] = next((m for m in call_args.kwargs.get("messages", []) if m["role"] == "user"), {})
    content = user_msg.get("content", "")

    # Assert AI trace is in
    assert "valid_ai_trace" in content
    assert "AI says hello" in content

    # Assert python math bypassed the wildcard shield
    assert "my_python_math" in content
    assert "1337" in content

    # Assert garbage metadata was properly shielded
    assert "garbage_metadata" not in content
    assert "this should be blocked" not in content
