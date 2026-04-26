from typing import Any

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookResult, HookState
from backend_v2.hooks.atom_flattening import process_matrix_flattening


class MockRepository:
    def __init__(self, step_data: dict[str, Any], blocks_data: list[dict[str, Any]]) -> None:
        self.step_data = step_data
        self.blocks_data = blocks_data

    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        return self.step_data

    async def get_all_prompt_blocks(self) -> list[dict[str, Any]]:
        return self.blocks_data

def _build_valid_pb(pb_id: str) -> dict[str, Any]:
    return {
        "id": pb_id,
        "slug": "test_slug",
        "label": {"default_locale": "en", "translations": {"en": "Label"}},
        "description": {"default_locale": "en", "translations": {"en": "Desc"}},
        "ai_description": "AI desc",
        "type": "float",
        "category_id": "matrix",
        "scale_min": 1,
        "scale_max": 5,
        "scales": [
            {
                "score": 1,
                "name": {"default_locale": "en", "translations": {"en": "Score 1"}},
                "ai_label": "Score 1",
                "claims": [{"label": {"default_locale": "en", "translations": {"en": "Claim 1"}}, "ai_description": "desc", "micro_atoms": ["atom_1_a", "atom_1_b"]}]
            },
            {
                "score": 5,
                "name": {"default_locale": "en", "translations": {"en": "Score 5"}},
                "ai_label": "Score 5",
                "claims": [{"label": {"default_locale": "en", "translations": {"en": "Claim 5"}}, "ai_description": "desc", "micro_atoms": ["atom_5_a", "atom_5_b"]}]
            }
        ]
    }

@pytest.mark.asyncio
async def test_atom_flattening_success() -> None:
    pb_id = "pb_1234567890123456"
    step_data = {
        "id": "st_1234567890123456",
        "slug": "step_1",
        "name": {"default_locale": "en", "translations": {"en": "Step 1"}},
        "type": "logic",
        "hook": "atom_flattening_hook",
        "prompt_blocks": [pb_id]
    }
    blocks_data = [_build_valid_pb(pb_id)]

    state = HookState(
        execution_id="exec_123",
        workflow_id="test_wf",
        step_id="step_1",
        task_blueprint="test_blueprint",
        metadata={"matrix_sampling_strategy": 1},
        inputs={},
        global_context_vars={}
    )
    deps = HookDependencies(repository=MockRepository(step_data, blocks_data))  # type: ignore

    result: HookResult = await process_matrix_flattening(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    shuffled_atoms = result.state_delta.get("shuffled_atoms", [])

    # 2 scales * 1 sampled atom per scale = 2 total atoms
    assert len(shuffled_atoms) == 2
    assert "atom_id" in shuffled_atoms[0]
    assert "question" in shuffled_atoms[0]
