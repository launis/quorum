from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.core.hook_registry import HookDependencies, HookState
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.atom_flattening import process_matrix_flattening
from backend_v2.models.enums import BlockDataType, PromptBlockCategory
from backend_v2.models.v2_core import (
    I18nText,
    MatrixClaim,
    MatrixScale,
    PromptBlock,
    Step,
    TDAAssertion,
)


class MockRepository:
    """A minimal repository mock for testing atomization hooks."""

    def __init__(self, step: Step, blocks: list[PromptBlock]) -> None:
        self._step = step
        self._blocks = blocks

    async def get_step_by_id(self, step_id: str) -> dict[str, Any]:
        if step_id == self._step.id:
            return self._step.model_dump()
        return {}

    async def get_all_prompt_blocks(self) -> list[dict[str, Any]]:
        return [b.model_dump() for b in self._blocks]


def create_mock_matrix_block(block_id: str, num_atoms_per_scale: int) -> PromptBlock:
    """Creates a mock matrix PromptBlock with specific scales for testing."""
    scales = []
    for score in [1, 5]:
        claims = [
            MatrixClaim(
                label=I18nText(default_locale="en", translations={"en": f"Claim {score}", "fi": f"Claim {score}"}),
                ai_description=f"Desc {score}",
                tda_assertions=[
                    TDAAssertion(
                        tda_id=f"tda_{score:016x}{i:016x}",
                        concept_description=f"Atom {score}-{i}",
                        inverse_evidence=False,
                        aggregation_mode="EXISTS",
                    )
                    for i in range(num_atoms_per_scale)
                ],
            )
        ]
        scales.append(
            MatrixScale(
                score=score,
                ai_label=f"Label {score}",
                claims=claims,
            )
        )

    return PromptBlock(
        id=block_id,
        slug=f"slug-{block_id}",
        label=I18nText(default_locale="en", translations={"en": f"Label {block_id}", "fi": f"Label {block_id}"}),
        description=I18nText(default_locale="en", translations={"en": f"Desc {block_id}", "fi": f"Desc {block_id}"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        scales=scales,
    )


@pytest.fixture
def base_hook_state() -> HookState:
    return HookState(
        step_id="step_1",
        execution_id="exec_123",
        workflow_id="wf_123",
        task_blueprint="step_0123456789abcdef0123456789abcdef",
        inputs={},
        global_context_vars={},
        metadata={"matrix_sampling_strategy": 1},
    )


@pytest.fixture
def mock_step() -> Step:
    return Step(
        id="step_0123456789abcdef0123456789abcdef",
        name=I18nText(default_locale="en", translations={"en": "Test Step", "fi": "Test Step"}),
        slug="test-step",
        role_block_id=None,
        extraction_protocol_block_id="blk_573802341db9d68c",
        criteria_block_ids=["blk_0123456789abcdef0123456789abcdef", "blk_1123456789abcdef0123456789abcdef"],
        model_strategy="fast",
    )


@pytest.mark.asyncio
async def test_atom_flattening_missing_strategy_fails_fast(base_hook_state: HookState, mock_step: Step) -> None:
    """Test that missing matrix_sampling_strategy triggers fail-fast."""
    state = base_hook_state.model_copy(update={"metadata": {}})  # Empty metadata

    mock_workflow_repo = AsyncMock()
    mock_workflow_repo.get_step_by_id.return_value = mock_step.model_dump(mode="json")
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=mock_workflow_repo,
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )
    # repo)  # type: ignore[arg-type]

    with pytest.raises(AppException) as exc_info:
        await process_matrix_flattening(state, deps)  # type: ignore[misc]

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR.value
    assert "requires 'matrix_sampling_strategy'" in exc_info.value.message


@pytest.mark.asyncio
async def test_atom_flattening_invalid_strategy_fails_fast(base_hook_state: HookState, mock_step: Step) -> None:
    """Test that invalid matrix_sampling_strategy triggers fail-fast."""
    state = base_hook_state.model_copy(update={"metadata": {"matrix_sampling_strategy": -1}})  # Invalid negative limit

    mock_workflow_repo = AsyncMock()
    mock_workflow_repo.get_step_by_id.return_value = mock_step.model_dump(mode="json")
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=mock_workflow_repo,
        comp_repo=AsyncMock(),
        prompt_block_repo=AsyncMock(),
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )
    # repo)  # type: ignore[arg-type]

    with pytest.raises(AppException) as exc_info:
        await process_matrix_flattening(state, deps)  # type: ignore[misc]

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR.value
    assert "Invalid matrix_sampling_strategy" in exc_info.value.message


@pytest.mark.asyncio
async def test_atom_flattening_stratified_sampling(base_hook_state: HookState, mock_step: Step) -> None:
    """Test Stratified sampling selects exactly N elements per scale."""
    mock_block = create_mock_matrix_block("blk_0123456789abcdef0123456789abcdef", num_atoms_per_scale=10)
    mock_workflow_repo = AsyncMock()
    mock_workflow_repo.get_step_by_id.return_value = mock_step.model_dump(mode="json")
    mock_comp_repo = AsyncMock()
    mock_comp_repo.get_all_prompt_blocks.return_value = [mock_block.model_dump(mode="json")]
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=mock_workflow_repo,
        comp_repo=mock_comp_repo,
        prompt_block_repo=mock_comp_repo,
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )
    # repo)  # type: ignore[arg-type]

    # Use STRATIFIED_3
    state = base_hook_state.model_copy(update={"metadata": {"matrix_sampling_strategy": 3}})

    result = await process_matrix_flattening(state, deps)  # type: ignore[misc]

    assert result.success is True
    assert "shuffled_atoms" in result.state_delta

    shuffled_atoms = result.state_delta["shuffled_atoms"]
    assert isinstance(shuffled_atoms, list)
    # 2 scales (1 and 5), 3 samples each = 6 total atoms
    assert len(shuffled_atoms) == 6

    # Verify keys
    for item in shuffled_atoms:
        assert "atom_id" in item
        assert "question" in item


@pytest.mark.asyncio
async def test_atom_flattening_all_strategy_no_sampling(base_hook_state: HookState, mock_step: Step) -> None:
    """Test ALL sampling strategy flattens everything without dropping."""
    mock_block = create_mock_matrix_block("blk_0123456789abcdef0123456789abcdef", num_atoms_per_scale=5)
    mock_workflow_repo = AsyncMock()
    mock_workflow_repo.get_step_by_id.return_value = mock_step.model_dump(mode="json")
    mock_comp_repo = AsyncMock()
    mock_comp_repo.get_all_prompt_blocks.return_value = [mock_block.model_dump(mode="json")]
    deps = HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=mock_workflow_repo,
        comp_repo=mock_comp_repo,
        prompt_block_repo=mock_comp_repo,
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )
    # repo)  # type: ignore[arg-type]

    # Use ALL
    state = base_hook_state.model_copy(update={"metadata": {"matrix_sampling_strategy": 0}})

    result = await process_matrix_flattening(state, deps)  # type: ignore[misc]

    assert result.success is True
    assert "shuffled_atoms" in result.state_delta

    shuffled_atoms = result.state_delta["shuffled_atoms"]
    assert isinstance(shuffled_atoms, list)
    # 2 scales (1 and 5), 5 samples each = 10 total atoms
    assert len(shuffled_atoms) == 10

    # Semantic micro-batching requirement: ensure deterministic sorting based on atom_id
    sorted_ids = [item["atom_id"] for item in shuffled_atoms]
    assert sorted_ids == sorted(sorted_ids), "Atoms are not deterministically sorted by atom_id"
