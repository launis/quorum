"""Unit tests for the Synthesis Hook."""

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState, hook_registry
from backend_v2.exceptions import AppException
from backend_v2.hooks.synthesis import text_consolidation_hook
from backend_v2.services.mcp.mcp_tool_loop import MCPToolLoopResult


@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.get_workflow_by_id = AsyncMock()
    repo.get_all = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def base_state() -> HookState:
    return HookState(
        execution_id="exe_1",
        workflow_id="wf_1",
        step_id="step_1",
        inputs={
            "step_1": {"reasoning_trace": "test text abc@example.com"},
            "step_2": {"locale": "en"},
        },
        global_context_vars={"language": "en"},
        metadata={
            "target_locale": "en",
            "step_results": [
                {
                    "step_id": "step_1",
                    "block_id": "b1",
                    "data_type": "text",
                    "payload": {"reasoning_trace": "test text abc@example.com"},
                },  # noqa: E501
                {"step_id": "step_2", "block_id": "b2", "data_type": "text", "payload": {"locale": "en"}},
            ],
        },
    )


@pytest.mark.asyncio
@patch("backend_v2.hooks.synthesis.execute_tool_loop")
@patch("backend_v2.hooks.synthesis.LLMClient")
async def test_synthesis_hook_success(
    mock_llm_client_class: AsyncMock, mock_execute_tool_loop: AsyncMock, mock_repo: AsyncMock, base_state: HookState
) -> None:
    """Test that synthesis hook injects config constraints correctly and calls LLM."""
    mock_repo.get_workflow_by_id = AsyncMock()
    mock_repo.get_execution = AsyncMock(
        return_value={
            "id": "exe_1111111111111111",
            "workflow_id": "wf_1111111111111111",
            "status": "completed",
            "strictness_level": 50,
            "output_profile_id": "prf_test",
        }
    )
    mock_workflow: dict[str, Any] = {
        "id": "wf_1111111111111111",
        "slug": "test-workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "status": "published",
        "version": 1,
        "default_profile_id": "prf_test",
        "output_profiles": {
            "prf_test": {
                "name": {"default_locale": "en", "translations": {"en": "Profile Test"}},
                "layouts": [{"target_blocks": ["*"], "preset_view": "default"}],
                "synthesis": {
                    "system_prompt": "Test sys prompt",
                    "length_constraint": 500,
                    "preamble_text": {"default_locale": "en", "translations": {"en": "Always be concise."}},
                    "omit_empty_sections": True,
                    "enable_pii_masking": True,
                },
            }
        },
    }
    mock_repo.get_workflow_by_id.return_value = mock_workflow
    prof_data = dict(mock_workflow["output_profiles"]["prf_test"])
    prof_data.update({"id": "prf_test", "slug": "profile-test", "workflow_id": "wf_1111111111111111"})
    mock_repo.get_output_profile_by_id = AsyncMock(return_value=prof_data)
    mock_repo.get_step_by_id.return_value = {"id": "step_111111111111111111111111"}
    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )

    # Setup the mock LLM Client Instance
    mock_client_instance = AsyncMock()
    mock_llm_client_class.from_strategy = AsyncMock(return_value=mock_client_instance)

    # Return MCPToolLoopResult
    mock_dto_dict = {
        "synthesized_markdown": "Synthesized [1]",
        "cited_sources": ["source1"],
        "section_syntheses": [],
        "xai_highlights": [],
    }
    mock_execute_tool_loop.return_value = MCPToolLoopResult(
        result_data=mock_dto_dict, audit_traces=[], usage={"total_tokens": 100}
    )

    result = await text_consolidation_hook(base_state, deps)  # type: ignore[misc]

    assert result.success is True
    delta = result.state_delta
    assert delta is not None

    # Verify that LLM tools loop was called
    mock_execute_tool_loop.assert_called_once()

    # Check if PII was masked (the email inside inputs should be [REDACTED EMAIL])
    call_args = mock_execute_tool_loop.call_args
    messages = call_args.kwargs.get("messages", [])
    user_msg: dict[str, Any] = next((m for m in messages if m["role"] == "user"), {})
    sys_msg: dict[str, Any] = next((m for m in messages if m["role"] == "system"), {})

    assert "[REDACTED_EMAIL]" in user_msg.get("content", "")
    assert "abc@example.com" not in user_msg.get("content", "")

    # Check if PII was masked (the email inside inputs should be [REDACTED EMAIL])
    assert "<global_length_constraint_chars>500</global_length_constraint_chars>" in sys_msg.get("content", "")
    assert "Always be concise." in sys_msg.get("content", "")

    assert delta["synthesized_markdown"] == "Synthesized [1]\n\n### BIBLIOGRAPHY_HEADER\n[1] source1"
    assert delta["cited_sources"] == ["source1"]
    assert "token_usage" in delta["step_metadata_updates"]
    assert delta["step_metadata_updates"]["token_usage"]["total_tokens"] == 100


@pytest.mark.asyncio
async def test_synthesis_hook_workflow_not_found(mock_repo: AsyncMock, base_state: HookState) -> None:
    """Test that missing workflow throws an AppException."""
    mock_repo.get_workflow_by_id.return_value = None
    mock_repo.get_step_by_id.return_value = {"id": "step_111111111111111111111111"}
    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )

    with pytest.raises(AppException) as exc_info:
        await text_consolidation_hook(base_state, deps)  # type: ignore[misc]

    assert exc_info.value.status_code == 404


@pytest.mark.asyncio
@patch("backend_v2.hooks.synthesis.execute_tool_loop")
@patch("backend_v2.hooks.synthesis.LLMClient")
async def test_synthesis_hook_multi_profile_routing(
    mock_llm_client_class: AsyncMock, mock_execute_tool_loop: AsyncMock, mock_repo: AsyncMock, base_state: HookState
) -> None:
    """Test that synthesis routes to requested target_profile_id and uses its distinct rules."""
    mock_repo.get_execution = AsyncMock(
        return_value={
            "id": "exe_1111111111111111",
            "workflow_id": "wf_1111111111111111",
            "status": "completed",
            "strictness_level": 50,
            "output_profile_id": "prof_b",
        }
    )

    mock_workflow: dict[str, Any] = {
        "id": "wf_1111111111111111",
        "slug": "test-workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "status": "published",
        "version": 1,
        "default_profile_id": "prof_a",
        "output_profiles": {
            "prof_a": {
                "name": {"default_locale": "en", "translations": {"en": "A"}},
                "layouts": [{"target_blocks": ["*"], "preset_view": "default"}],
                "synthesis": {
                    "system_prompt": "Test sys prompt",
                    "length_constraint": 100,
                    "preamble_text": {"default_locale": "en", "translations": {"en": "Alpha"}},
                },
            },
            "prof_b": {
                "name": {"default_locale": "en", "translations": {"en": "B"}},
                "layouts": [{"target_blocks": ["*"], "preset_view": "default"}],
                "synthesis": {
                    "system_prompt": "Test sys prompt",
                    "length_constraint": 900,
                    "preamble_text": {"default_locale": "en", "translations": {"en": "Beta"}},
                },
            },
        },
    }
    mock_repo.get_workflow_by_id = AsyncMock(return_value=mock_workflow)
    prof_data = dict(mock_workflow["output_profiles"]["prof_b"])
    prof_data.update({"id": "prof_b", "slug": "prof-b", "workflow_id": "wf_1111111111111111"})
    mock_repo.get_output_profile_by_id = AsyncMock(return_value=prof_data)
    mock_repo.get_step_by_id.return_value = {"id": "step_111111111111111111111111"}
    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )

    # Force the hook to use prof_b
    base_state.metadata["target_profile_id"] = "prof_b"

    mock_client_instance = AsyncMock()
    mock_llm_client_class.from_strategy = AsyncMock(return_value=mock_client_instance)
    mock_execute_tool_loop.return_value = MCPToolLoopResult(
        result_data={
            "synthesized_markdown": "Beta result",
            "cited_sources": [],
            "section_syntheses": [],
            "xai_highlights": [],
        },
        audit_traces=[],
        usage={"total_tokens": 50},
    )

    result = await text_consolidation_hook(base_state, deps)  # type: ignore[misc]
    assert result.success is True

    call_args = mock_execute_tool_loop.call_args
    sys_msg: dict[str, Any] = next((m for m in call_args.kwargs.get("messages", []) if m["role"] == "system"), {})

    # Assert Prof B's constraints are found, NOT Prof A's
    assert "<global_length_constraint_chars>900</global_length_constraint_chars>" in sys_msg.get("content", "")
    assert "Beta" in sys_msg.get("content", "")
    assert "Alpha" not in sys_msg.get("content", "")
    assert "<global_length_constraint_chars>100</global_length_constraint_chars>" not in sys_msg.get("content", "")


@pytest.mark.asyncio
@patch("backend_v2.hooks.synthesis.execute_tool_loop")
@patch("backend_v2.hooks.synthesis.LLMClient")
async def test_synthesis_hook_target_blocks_wildcard_bypass(
    mock_llm_client_class: AsyncMock, mock_execute_tool_loop: AsyncMock, mock_repo: AsyncMock, base_state: HookState
) -> None:
    """Test the dual-layer filter: AI traces are included by *, explicit Python variables bypass the check."""
    mock_repo.get_execution = AsyncMock(
        return_value={
            "id": "exe_1111111111111111",
            "workflow_id": "wf_1111111111111111",
            "status": "completed",
            "strictness_level": 50,
            "output_profile_id": "prof_a",
        }
    )

    mock_workflow: dict[str, Any] = {
        "id": "wf_1111111111111111",
        "slug": "test-workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "status": "published",
        "version": 1,
        "default_profile_id": "prof_a",
        "output_profiles": {
            "prof_a": {
                "name": {"default_locale": "en", "translations": {"en": "A"}},
                "layouts": [
                    {"target_blocks": ["step_2"], "preset_view": "default"},
                    {"target_blocks": ["*"], "preset_view": "default"},
                ],
                "synthesis": {
                    "system_prompt": "Test sys prompt",
                    "length_constraint": 100,
                    "preamble_text": {"default_locale": "en", "translations": {"en": "Alpha"}},
                },
            }
        },
    }
    mock_repo.get_workflow_by_id = AsyncMock(return_value=mock_workflow)
    prof_data = dict(mock_workflow["output_profiles"]["prof_a"])
    prof_data.update({"id": "prof_a", "slug": "prof-a", "workflow_id": "wf_1111111111111111"})
    mock_repo.get_output_profile_by_id = AsyncMock(return_value=prof_data)
    mock_repo.get_step_by_id.return_value = {"id": "step_111111111111111111111111"}
    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )

    base_state = base_state.model_copy(
        update={
            "inputs": {
                "step_1": {"reasoning_trace": "AI says hello"},
                "step_2": {"result": 1337},
                "step_3": {"value": "this should be blocked by wildcard"},
            },
            "metadata": {
                "target_locale": "en",
                "step_results": [
                    {
                        "step_id": "step_1",
                        "block_id": "b1",
                        "data_type": "text",
                        "payload": {"reasoning_trace": "AI says hello"},
                    },  # noqa: E501
                    {"step_id": "step_2", "block_id": "b2", "data_type": "text", "payload": {"result": 1337}},
                    {
                        "step_id": "step_3",
                        "block_id": "b3",
                        "data_type": "text",
                        "payload": {"value": "this should be blocked by wildcard"},
                    },  # noqa: E501
                ],
            },
        }
    )

    mock_client_instance = AsyncMock()
    mock_llm_client_class.from_strategy = AsyncMock(return_value=mock_client_instance)
    mock_execute_tool_loop.return_value = MCPToolLoopResult(
        result_data={
            "synthesized_markdown": "Summary",
            "cited_sources": [],
            "section_syntheses": [],
            "xai_highlights": [],
        },
        audit_traces=[],
        usage={"total_tokens": 10},
    )

    result = await text_consolidation_hook(base_state, deps)  # type: ignore[misc]
    assert result.success is True

    call_args = mock_execute_tool_loop.call_args
    user_msg: dict[str, Any] = next((m for m in call_args.kwargs.get("messages", []) if m["role"] == "user"), {})
    content = user_msg.get("content", "")

    # Assert AI trace is in
    assert "step_1" in content
    assert "AI says hello" in content

    # Assert python math bypassed the wildcard shield
    assert "step_2" in content
    assert "1337" in content

    # Assert garbage metadata was properly shielded
    assert "step_3" not in content
    assert "this should be blocked" not in content


def test_synthesis_hook_is_registered() -> None:
    """Test that text_consolidation_hook is correctly registered in the HookRegistry to prevent regressions."""
    # Ensure hooks are initialized (this triggers decorators in tests if not already done)
    import backend_v2.hooks  # noqa: F401

    hook = hook_registry.get_hook("text_consolidation_hook")
    assert hook is not None
    assert hook == text_consolidation_hook


@pytest.mark.asyncio
@patch("backend_v2.hooks.synthesis.execute_tool_loop")
@patch("backend_v2.hooks.synthesis.LLMClient")
async def test_synthesis_hook_historical_context_mode(
    mock_llm_client_class: AsyncMock, mock_execute_tool_loop: AsyncMock, mock_repo: AsyncMock, base_state: HookState
) -> None:
    """Test that SLIDING_WINDOW_3 fetches valid past executions and ignores failed ones."""
    mock_repo.get_execution = AsyncMock(
        return_value={
            "id": "exe_1111111111111111",
            "workflow_id": "wf_1111111111111111",
            "status": "completed",
            "strictness_level": 50,
            "output_profile_id": "prf_test",
        }
    )

    mock_workflow: dict[str, Any] = {
        "id": "wf_1111111111111111",
        "slug": "test-workflow",
        "name": {"default_locale": "en", "translations": {"en": "Test"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "status": "published",
        "version": 1,
        "default_profile_id": "prf_test",
        "output_profiles": {
            "prf_test": {
                "name": {"default_locale": "en", "translations": {"en": "Profile Test"}},
                "layouts": [{"target_blocks": ["*"], "preset_view": "default"}],
                "synthesis": {
                    "historical_context_mode": "SLIDING_WINDOW_3",
                    "system_prompt": "Test sys prompt",
                    "preamble_text": {"default_locale": "en", "translations": {"en": "Alpha"}},
                    "length_constraint": 100,
                },
            }
        },
    }
    mock_repo.get_workflow_by_id = AsyncMock(return_value=mock_workflow)

    # Mocking past executions
    from datetime import datetime, timezone

    mock_past_exec = AsyncMock()
    mock_past_exec.id = "exe_past_1"
    mock_past_exec.status.value = "completed"
    mock_past_exec.created_at = datetime.now(timezone.utc)
    mock_past_exec.completed_at = datetime.now(timezone.utc)

    mock_cache = AsyncMock()
    mock_cache.synthesized_markdown = "Past history text"
    mock_past_exec.profile_syntheses = {"prf_test": mock_cache}

    mock_failed_exec = AsyncMock()
    mock_failed_exec.id = "exe_past_2"
    mock_failed_exec.status.value = "failed"

    mock_repo.get_all_executions = AsyncMock(return_value=[mock_failed_exec, mock_past_exec])
    prof_data = dict(mock_workflow["output_profiles"]["prf_test"])
    prof_data.update({"id": "prf_test", "slug": "profile-test", "workflow_id": "wf_1111111111111111"})
    mock_repo.get_output_profile_by_id = AsyncMock(return_value=prof_data)

    mock_repo.get_step_by_id.return_value = {"id": "step_111111111111111111111111"}
    deps = HookDependencies(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        comp_repo=mock_repo,
        identity_repo=mock_repo,
        audit_repo=mock_repo,
        system_repo=mock_repo,
    )

    mock_client_instance = AsyncMock()
    mock_llm_client_class.from_strategy = AsyncMock(return_value=mock_client_instance)
    mock_execute_tool_loop.return_value = MCPToolLoopResult(
        result_data={
            "synthesized_markdown": "Summary",
            "cited_sources": [],
            "section_syntheses": [],
            "xai_highlights": [],
        },
        audit_traces=[],
        usage={"total_tokens": 10},
    )

    base_state = base_state.model_copy(
        update={
            "inputs": {"step_1": {"reasoning_trace": "AI says hello"}},
            "global_context_vars": {"user_id": "usr_123"},
            "metadata": {
                "target_locale": "en",
                "step_results": [
                    {
                        "step_id": "step_1",
                        "block_id": "b1",
                        "data_type": "text",
                        "payload": {"reasoning_trace": "AI says hello"},
                    }
                ],
            },  # noqa: E501
        }
    )

    result = await text_consolidation_hook(base_state, deps)  # type: ignore[misc]
    assert result.success is True

    # Verify historical context was fetched
    mock_repo.get_all_executions.assert_called_once()

    call_args = mock_execute_tool_loop.call_args
    user_msg: dict[str, Any] = next((m for m in call_args.kwargs.get("messages", []) if m["role"] == "user"), {})
    content = user_msg.get("content", "")

    # Assert valid past text was included
    assert "Past history text" in content
    assert "<HistoricalContext>" in content
