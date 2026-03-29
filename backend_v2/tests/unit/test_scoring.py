from typing import Any

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException
from backend_v2.hooks.scoring import normalize_matrix_scores_hook


class MockRepository:
    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        return {"prompt_blocks": ["test_block"]}

    async def get_prompt_block_by_id(self, slug: str) -> dict[str, Any]:
        return {"scales": [{"score": "not_a_number"}]}


@pytest.mark.asyncio
async def test_normalize_matrix_scores_fails_on_corrupt_scale() -> None:
    """Test that setting a corrupted non-float scale in PromptBlocks causes a fail fast AppException."""
    state = HookState(
        execution_id="test_exec",
        workflow_id="test_wf",
        step_id="test_step",
        task_blueprint="test_blueprint",
        inputs={"test_block": 5.0},
        global_context_vars={},
    )
    deps = HookDependencies(repository=MockRepository())  # type: ignore

    with pytest.raises(AppException) as exc_info:
        await normalize_matrix_scores_hook(state, deps)  # type: ignore[misc]

    assert exc_info.value.error_code == "CONFIGURATION_ERROR"
    assert "Corrupted scale value 'not_a_number' in PromptBlock 'test_block'" in exc_info.value.message
