"""Unit tests for the Synthesis Hook."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.synthesis import text_consolidation_hook


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
        inputs={"content": "test text", "empty_key": "", "language": "en"}
    )


@pytest.mark.asyncio
async def test_synthesis_hook_success(mock_repo: MagicMock, base_state: HookState) -> None:
    """Test that synthesis hook injects config constraints correctly."""
    mock_workflow = {
        "id": "wf_1",
        "default_profile_id": "prf_test",
        "output_profiles": {
            "prf_test": {
                "synthesis": {
                    "length_constraint": 500,
                    "preamble_text": {"en": "Always be concise."},
                    "omit_empty_sections": True
                }
            }
        }
    }
    mock_repo.get_workflow_by_id.return_value = mock_workflow
    deps = HookDependencies(repository=mock_repo)

    result = await text_consolidation_hook(base_state, deps)

    assert result.success is True
    delta = result.state_delta
    assert delta is not None

    inst = delta["synthesis_instructions"]
    assert inst["synthesis_length_limit"] == 500
    assert inst["synthesis_preamble"] == "Always be concise."

    # Validate empty_key was omitted
    cons = delta["consolidated_inputs"]
    assert "content" in cons
    assert "empty_key" not in cons


@pytest.mark.asyncio
async def test_synthesis_hook_workflow_not_found(mock_repo: MagicMock, base_state: HookState) -> None:
    """Test that missing workflow throws an AppException."""
    mock_repo.get_workflow_by_id.return_value = None
    deps = HookDependencies(repository=mock_repo)

    with pytest.raises(AppException) as exc_info:
        await text_consolidation_hook(base_state, deps)
    
    assert exc_info.value.status_code == 404
