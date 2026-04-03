"""Unit tests for the Synthesis Hook."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.synthesis import text_consolidation_hook, SynthesisOutputDTO


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
        inputs={"content": "test text abc@example.com", "empty_key": "", "language": "en"},
        global_context_vars={"language": "en"},
        step_metadata={}
    )


@pytest.mark.asyncio
@patch("backend_v2.hooks.synthesis.LLMClient")
async def test_synthesis_hook_success(mock_llm_client_class: MagicMock, mock_repo: MagicMock, base_state: HookState) -> None:
    """Test that synthesis hook injects config constraints correctly and calls LLM."""
    mock_workflow = {
        "id": "wf_1",
        "default_profile_id": "prf_test",
        "output_profiles": {
            "prf_test": {
                "synthesis": {
                    "length_constraint": 500,
                    "preamble_text": {"en": "Always be concise."},
                    "omit_empty_sections": True,
                    "enable_pii_masking": True
                }
            }
        }
    }
    mock_repo.get_workflow_by_id.return_value = mock_workflow
    deps = HookDependencies(repository=mock_repo)

    # Setup the mock LLM Client Instance
    mock_client_instance = AsyncMock()
    mock_llm_client_class.from_strategy.return_value = mock_client_instance
    
    # Return (SynthesisOutputDTO, token_usage_dict) from run_structured_task
    mock_dto = SynthesisOutputDTO(synthesized_markdown="Synthesized [1]", cited_sources=["source1"])
    mock_client_instance.run_structured_task.return_value = (mock_dto, {"total_tokens": 100})

    result = await text_consolidation_hook(base_state, deps)

    assert result.success is True
    delta = result.state_delta
    assert delta is not None

    # Verify that LLM was called
    mock_client_instance.run_structured_task.assert_called_once()
    
    # Check if PII was masked (the email inside inputs should be [REDACTED EMAIL])
    call_args = mock_client_instance.run_structured_task.call_args
    messages = call_args.kwargs.get("messages", [])
    user_msg = next((m for m in messages if m["role"] == "user"), {})
    sys_msg = next((m for m in messages if m["role"] == "system"), {})
    
    assert "[REDACTED EMAIL]" in user_msg.get("content", "")
    assert "abc@example.com" not in user_msg.get("content", "")
    
    # Check if empty_key was omitted
    assert "empty_key" not in user_msg.get("content", "")
    
    # Check length constraint & preamble
    assert "LENGTH CONSTRAINT: The output should be approximately 500 characters." in sys_msg.get("content", "")
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
        await text_consolidation_hook(base_state, deps)
    
    assert exc_info.value.status_code == 404
