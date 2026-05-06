from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.hooks.synthesis import text_consolidation_hook


@pytest.fixture
def valid_workflow_data_for_synthesis() -> dict[str, Any]:
    return {
        "id": "wf_00000000000000000000",
        "slug": "test_workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "status": "draft",
        "version": 1,
        "default_profile_id": "prof_00000000000000000000",
        "expected_inputs": [],
        "steps": [],
    }


@pytest.fixture
def valid_execution_data_for_synthesis() -> dict[str, Any]:
    return {
        "id": "exe_00000000000000000000",
        "workflow_id": "wf_00000000000000000000",
        "organization_id": "org_00000000000000000000",
        "status": "running",
        "output_profile_id": "prof_00000000000000000000",
    }


@pytest.fixture
def valid_output_profile_data_for_synthesis() -> dict[str, Any]:
    return {
        "id": "prof_00000000000000000000",
        "slug": "test_profile",
        "workflow_id": "wf_00000000000000000000",
        "name": {"default_locale": "en", "translations": {"en": "Test Profile"}},
        "strictness_level": 50,
        "scoring_strategy": "WATERFALL",
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
@patch("backend_v2.hooks.synthesis.execute_tool_loop")
@patch("backend_v2.hooks.synthesis.LLMClient.from_strategy")
async def test_synthesis_happy_path(
    mock_from_strategy: AsyncMock,
    mock_tool_loop: AsyncMock,
    valid_workflow_data_for_synthesis: dict[str, Any],
    valid_execution_data_for_synthesis: dict[str, Any],
    valid_output_profile_data_for_synthesis: dict[str, Any],
) -> None:
    # Setup mock returns
    mock_client = AsyncMock()
    mock_from_strategy.return_value = mock_client

    class DummyToolRes:
        result_data = {
            "synthesized_markdown": "Happy summary",
            "cited_sources": [],
            "section_syntheses": [],
            "xai_highlights": [],
        }
        from backend_v2.models.domain.usage import TokenUsage

        usage = TokenUsage(completion_tokens=10, prompt_tokens=0, total_tokens=10)
        from typing import Any

        audit_traces: list[Any] = []

    mock_tool_loop.return_value = DummyToolRes()

    state = HookState(
        execution_id="exe_00000000000000000000",
        workflow_id="wf_00000000000000000000",
        inputs={
            "steps": {
                "step_1": {
                    "text_response": "Some text",
                    "reasoning_trace": {
                        "thought_process": "Some thought",
                        "conclusion": "Some conclusion",
                        "confidence_score": 0.9,
                    },
                }
            }
        },
        metadata={
            "target_locale": "en",
            "step_results": [
                {
                    "step_id": "step_1",
                    "block_id": "b",
                    "data_type": "text",
                    "payload": {
                        "text_response": "Some text",
                        "reasoning_trace": {
                            "thought_process": "Some thought",
                            "conclusion": "Some conclusion",
                            "confidence_score": 0.9,
                        },
                    },
                }
            ],
        },  # noqa: E501
        global_context_vars={},
    )

    mock_repo = AsyncMock()
    mock_repo.get_workflow_by_id.return_value = valid_workflow_data_for_synthesis
    mock_repo.get_execution.return_value = valid_execution_data_for_synthesis
    mock_repo.get_output_profile_by_id.return_value = valid_output_profile_data_for_synthesis
    mock_repo.get_all.return_value = []

    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )
    # mock_repo)

    from collections.abc import Awaitable
    from typing import cast

    from backend_v2.core.hook_registry import HookResult

    result = await cast(Awaitable[HookResult], text_consolidation_hook(state, deps))

    assert result.success is True
    assert result.state_delta is not None
    assert "synthesized_markdown" in result.state_delta
    assert result.state_delta["synthesized_markdown"] == "Happy summary"
