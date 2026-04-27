from typing import Any, cast
from unittest.mock import AsyncMock

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.synthesis import text_consolidation_hook


@pytest.fixture
def valid_workflow_data() -> dict[str, Any]:
    return {
        "id": "wf_1234567890abcdef1234567890abcdef",
        "slug": "test_workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "status": "draft",
        "version": 1,
        "default_profile_id": "prof_1234567890abcdef1234567890abcdef",
        "expected_inputs": [],
        "steps": [],
    }


@pytest.fixture
def valid_execution_data() -> dict[str, Any]:
    return {
        "id": "exe_1234567890abcdef1234567890abcdef",
        "workflow_id": "wf_1234567890abcdef1234567890abcdef",
        "organization_id": "org_1",
        "status": "running",
        "output_profile_id": "prof_1234567890abcdef1234567890abcdef",
    }


@pytest.fixture
def valid_output_profile_data() -> dict[str, Any]:
    return {
        "id": "prof_1234567890abcdef1234567890abcdef",
        "slug": "test_profile",
        "workflow_id": "wf_1234567890abcdef1234567890abcdef",
        "name": {"default_locale": "en", "translations": {"en": "Test Profile"}},
        "display_scale": "original",
        "synthesis": {
            "system_prompt": "You are a synthesizer.",
            "historical_context_mode": "DISABLED",
            "enable_pii_masking": False,
            "omit_empty_sections": True,
            "allowed_exports": ["pdf", "raw_json"],
            "allowed_mcp_tools": [],
        },
        "layouts": [],
    }


@pytest.mark.asyncio
async def test_synthesis_fails_fast_on_invalid_metadata(
    valid_workflow_data: dict[str, Any], valid_execution_data: dict[str, Any], valid_output_profile_data: dict[str, Any]
) -> None:  # noqa: E501
    """Test that missing target_locale triggers AppException due to strict Pydantic parsing."""
    state = HookState(
        execution_id="exe_1234567890abcdef1234567890abcdef",
        workflow_id=valid_workflow_data["id"],
        inputs={},
        metadata={},  # Missing target_locale
        global_context_vars={},
    )
    mock_repo = AsyncMock()
    mock_repo.get_workflow_by_id.return_value = valid_workflow_data
    mock_repo.get_execution.return_value = valid_execution_data
    mock_repo.get_output_profile_by_id.return_value = valid_output_profile_data
    deps = HookDependencies(repository=mock_repo)

    from collections.abc import Awaitable

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], text_consolidation_hook(state, deps))

    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "Strict Fail-Fast Enforced" in exc_info.value.message


@pytest.mark.asyncio
async def test_synthesis_fails_fast_on_invalid_step_data(
    valid_workflow_data: dict[str, Any], valid_execution_data: dict[str, Any], valid_output_profile_data: dict[str, Any]
) -> None:  # noqa: E501
    """Test that non-dict/model step data triggers AppException enforcing Phase 9 logic."""
    state = HookState(
        execution_id="exe_1234567890abcdef1234567890abcdef",
        workflow_id=valid_workflow_data["id"],
        inputs={"step_1": 12345},  # Invalid structured data
        metadata={"target_locale": "en", "step_results": {"step_1": 12345}},
        global_context_vars={},
    )

    mock_repo = AsyncMock()
    mock_repo.get_workflow_by_id.return_value = valid_workflow_data
    mock_repo.get_execution.return_value = valid_execution_data
    mock_repo.get_output_profile_by_id.return_value = valid_output_profile_data

    deps = HookDependencies(repository=mock_repo)

    from collections.abc import Awaitable

    with pytest.raises(AppException) as exc_info:
        await cast(Awaitable[HookResult], text_consolidation_hook(state, deps))

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert "must be a structured model" in exc_info.value.message


@pytest.mark.asyncio
async def test_synthesis_empty_inputs_returns_early(
    valid_workflow_data: dict[str, Any], valid_execution_data: dict[str, Any], valid_output_profile_data: dict[str, Any]
) -> None:  # noqa: E501
    """Test that valid metadata and empty inputs safely return a HookResult without calling the LLM."""
    state = HookState(
        execution_id="exe_1234567890abcdef1234567890abcdef",
        workflow_id=valid_workflow_data["id"],
        inputs={},
        metadata={"target_locale": "en", "step_results": {"dummy_step": {}}},
        global_context_vars={},
    )

    mock_repo = AsyncMock()
    mock_repo.get_workflow_by_id.return_value = valid_workflow_data
    mock_repo.get_execution.return_value = valid_execution_data
    mock_repo.get_output_profile_by_id.return_value = valid_output_profile_data

    deps = HookDependencies(repository=mock_repo)

    from collections.abc import Awaitable

    result = await cast(Awaitable[HookResult], text_consolidation_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "synthesized_markdown" in result.state_delta
    assert result.state_delta["synthesized_markdown"] == "*NO_DATA_AVAILABLE*"


def test_compress_synthesis_payload_strips_heavy_keys() -> None:
    """Test that _compress_synthesis_payload removes log-heavy keys but retains quotes and reasoning."""
    import json

    from backend_v2.hooks.synthesis import _compress_synthesis_payload

    payload = {
        "step_1": {
            "result": "success",
            "evaluations": [{"score": 1}],
            "shuffled_atoms": ["a", "b"],
            "quote": "test",
            "reasoning": "because",
            "nested": {"evaluations": "remove me too", "keep_me": True},
        }
    }

    compressed_str = _compress_synthesis_payload(payload)
    compressed = json.loads(compressed_str)

    assert "evaluations" not in compressed["step_1"]
    assert "shuffled_atoms" not in compressed["step_1"]
    assert "quote" in compressed["step_1"]
    assert "reasoning" in compressed["step_1"]
    assert "evaluations" not in compressed["step_1"]["nested"]
    assert compressed["step_1"]["nested"]["keep_me"] is True


def test_build_title_map() -> None:
    """Test that _build_title_map successfully resolves localized Step and Input names."""
    from backend_v2.hooks.synthesis import _build_title_map
    from backend_v2.models.v2_core import I18nText, Step, Workflow

    wf = Workflow(
        id="wf_1234567890abcdef1234567890abcdef",
        slug="test",
        name=I18nText(default_locale="en", translations={"en": "Test"}),
        description=I18nText(default_locale="en", translations={"en": "Desc"}),
        status="draft",
        version=1,
        default_profile_id="prof_1234567890abcdef1234567890abcdef",
        steps=cast(
            Any,
            [
                {
                    "id": "node_1111111111abcdef1111111111abcdef",
                    "task_blueprint": "step_2222222222abcdef2222222222abcdef",
                }
            ],
        ),
        expected_inputs=cast(
            Any,
            [
                {
                    "input_key": "input_x",
                    "label": I18nText(default_locale="en", translations={"en": "Input X", "fi": "Syöte X"}),
                    "required": True,
                    "input_modes": ["text"],
                    "description": I18nText(default_locale="en", translations={"en": "Desc"}),
                }
            ],
        ),
    )

    step = Step(
        id="step_2222222222abcdef2222222222abcdef",
        slug="test_step",
        name=I18nText(default_locale="en", translations={"en": "Test Step", "fi": "Testi Vaihe"}),
        type="llm",
        model_strategy="fast",
        prompt_blocks=["block_1"],
    )

    title_map = _build_title_map(wf, [step], language="fi")

    assert title_map["node_1111111111abcdef1111111111abcdef"] == "Testi Vaihe"
    assert title_map["input_x"] == "Syöte X"
