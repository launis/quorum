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


@pytest.mark.asyncio
async def test_normalize_matrix_scores_tapa_2_string_mapping() -> None:
    """Test that Tapa 2 string PromptBlocks preserve XAI variables without crashing the float scaler (Epic 12)."""

    class MockRepoTapa2:
        async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
            return {"prompt_blocks": ["toulmin_text_block"]}

        async def get_prompt_block_by_id(self, pb_id: str) -> dict[str, Any]:
            return {"scales": []}  # Emulate non-evaluative / string-only Tapa 2 block

    state = HookState(
        execution_id="test_exec",
        workflow_id="test_wf",
        step_id="test_step",
        task_blueprint="test_blueprint",
        inputs={
            "toulmin_text_block": {
                "evaluation_notes": "Tämä on perustelu",
                "step_1_evidence_quote": "Ote lähteestä",
                "step_2_falsification": "Vastalause",
                "step_3_logical_friction": "Kitkaa on",
            }
        },
        global_context_vars={},
    )
    deps = HookDependencies(repository=MockRepoTapa2())  # type: ignore

    result = await normalize_matrix_scores_hook(state, deps)  # type: ignore[misc]

    assert result.success is True
    delta = result.state_delta
    assert delta is not None

    # Must natively map textual displays without numeric scoring triggering graceful degradation
    assert delta["toulmin_text_block_cited_text_quote"] == "Ote lähteestä"
    assert delta["toulmin_text_block_falsification"] == "Vastalause"

    # Must cleanly pipe notes to justification without '1 Evidence Quote' markdown formatting
    justification = delta["toulmin_text_block_justification"]
    assert "Tämä on perustelu" in justification
    assert "Kitkaa on" in justification

    # Must not contain mathematical keys for text-blocks
    assert "toulmin_text_block_scaled" not in delta
