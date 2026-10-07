from typing import Any

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.atom_flattening import process_matrix_flattening
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.step import Step
from backend_v2.models.dtos.dag_models import CausalEdge
from backend_v2.models.dtos.hook_delta import FlatteningHookOutput
from backend_v2.models.enums import BlockDataType, CognitiveTier, ExecutionStatus, PromptBlockCategory
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _make_deps(
    workflow_repo: Any = ...,
    comp_repo: Any = None,
) -> HookDependencies:
    default_fake = InMemoryUnifiedWorkflowRepository()
    wf = default_fake if workflow_repo is ... else workflow_repo
    comp = default_fake if comp_repo is None else comp_repo
    return HookDependencies(
        exec_repo=default_fake,
        workflow_repo=wf,
        comp_repo=comp,
        prompt_block_repo=comp,
        output_profile_repo=default_fake,
        identity_repo=default_fake,
        audit_repo=default_fake,
        system_repo=default_fake,
    )


def create_mock_matrix_block(block_id: str, num_atoms_per_scale: int) -> MatrixPromptBlock:
    """Creates a mock matrix PromptBlock with specific scales for testing."""
    scales = []
    for score in [1, 5]:
        claims = [
            MatrixClaim(
                label=I18nText(translations={"en": f"Claim {score}", "fi": f"Claim {score}"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id=f"tda_{score:016x}{i:016x}",
                        concept_description=f"Concept Atom {score}-{i}",
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

    return MatrixPromptBlock(
        id=block_id,
        slug=f"slug-{block_id}",
        label=I18nText(translations={"en": f"Label {block_id}", "fi": f"Label {block_id}"}),
        description=I18nText(translations={"en": f"Desc {block_id}", "fi": f"Desc {block_id}"}),
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
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(matrix_sampling_strategy=1),
    )


@pytest.fixture
def mock_step() -> Step:
    return Step(
        id="step_0123456789abcdef0123456789abcdef",
        name=I18nText(translations={"en": "Test Step", "fi": "Test Step"}),
        slug="test-step",
        role_block_id=None,
        extraction_protocol_block_id="blk_573802341db9d68c",
        criteria_block_ids=["blk_0123456789abcdef0123456789abcdef", "blk_1123456789abcdef0123456789abcdef"],
        cognitive_tier=CognitiveTier.FAST,
    )


@pytest.mark.asyncio
async def test_atom_flattening_missing_strategy_fails_fast(base_hook_state: HookState, mock_step: Step) -> None:
    """Test that invalid negative matrix_sampling_strategy triggers fail-fast."""
    state = base_hook_state.model_copy(
        update={"metadata": ExecutionMetadata.model_construct(matrix_sampling_strategy=-5)}
    )

    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_step(mock_step)
    deps = _make_deps(workflow_repo=repo)

    with pytest.raises(AppException) as exc_info:
        await process_matrix_flattening(state, deps)

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR.value
    assert "Invalid matrix_sampling_strategy" in exc_info.value.message


@pytest.mark.asyncio
async def test_atom_flattening_invalid_strategy_fails_fast(base_hook_state: HookState, mock_step: Step) -> None:
    """Test that invalid matrix_sampling_strategy triggers fail-fast."""
    state = base_hook_state.model_copy(
        update={"metadata": ExecutionMetadata.model_construct(matrix_sampling_strategy=-1)}
    )

    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_step(mock_step)
    deps = _make_deps(workflow_repo=repo)

    with pytest.raises(AppException) as exc_info:
        await process_matrix_flattening(state, deps)

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR.value
    assert "Invalid matrix_sampling_strategy" in exc_info.value.message


@pytest.mark.asyncio
async def test_atom_flattening_stratified_sampling(base_hook_state: HookState, mock_step: Step) -> None:
    """Test Stratified sampling selects exactly N elements per scale."""
    mock_block = create_mock_matrix_block("blk_0123456789abcdef0123456789abcdef", num_atoms_per_scale=10)
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_step(mock_step)
    await repo.create_prompt_block(mock_block)
    deps = _make_deps(workflow_repo=repo, comp_repo=repo)

    # Use STRATIFIED_3
    state = base_hook_state.model_copy(update={"metadata": ExecutionMetadata(matrix_sampling_strategy=3)})

    result = await process_matrix_flattening(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, FlatteningHookOutput)

    shuffled_atoms = result.state_delta.delta.shuffled_atoms
    assert isinstance(shuffled_atoms, list)
    # 2 scales (1 and 5), 3 samples each = 6 total atoms
    assert len(shuffled_atoms) == 6

    # Verify keys
    for item in shuffled_atoms:
        assert item.atom_id
        assert item.question


@pytest.mark.asyncio
async def test_atom_flattening_all_strategy_no_sampling(base_hook_state: HookState, mock_step: Step) -> None:
    """Test ALL sampling strategy flattens everything without dropping."""
    mock_block = create_mock_matrix_block("blk_0123456789abcdef0123456789abcdef", num_atoms_per_scale=5)
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_step(mock_step)
    await repo.create_prompt_block(mock_block)
    deps = _make_deps(workflow_repo=repo, comp_repo=repo)

    # Use ALL
    state = base_hook_state.model_copy(update={"metadata": ExecutionMetadata(matrix_sampling_strategy=0)})

    result = await process_matrix_flattening(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, FlatteningHookOutput)

    shuffled_atoms = result.state_delta.delta.shuffled_atoms
    assert isinstance(shuffled_atoms, list)
    # 2 scales (1 and 5), 5 samples each = 10 total atoms
    assert len(shuffled_atoms) == 10

    # Semantic micro-batching requirement: ensure deterministic sorting based on atom_id
    sorted_ids = [item.atom_id for item in shuffled_atoms]
    assert sorted_ids == sorted(sorted_ids), "Atoms are not deterministically sorted by atom_id"


@pytest.mark.asyncio
async def test_atom_flattening_no_task_blueprint(base_hook_state: HookState) -> None:
    """Test hook exits cleanly when no task_blueprint is set."""
    state = base_hook_state.model_copy(update={"task_blueprint": None})
    deps = _make_deps()
    result = await process_matrix_flattening(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


@pytest.mark.asyncio
async def test_atom_flattening_missing_workflow_repo(base_hook_state: HookState) -> None:
    """Test hook raises AppException if workflow_repo dependency is missing."""
    state = base_hook_state
    deps = _make_deps(workflow_repo=None)
    with pytest.raises(AppException) as exc_info:
        await process_matrix_flattening(state, deps)
    assert exc_info.value.status_code == 500
    assert exc_info.value.error_code == ErrorCodes.EXECUTION_NOT_FOUND.value


@pytest.mark.asyncio
async def test_atom_flattening_step_not_found(base_hook_state: HookState) -> None:
    """Test hook returns empty state delta if step blueprint not found."""
    mock_workflow_repo = InMemoryUnifiedWorkflowRepository()
    deps = _make_deps(workflow_repo=mock_workflow_repo)
    result = await process_matrix_flattening(base_hook_state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


@pytest.mark.asyncio
async def test_atom_flattening_empty_criteria_blocks(base_hook_state: HookState, mock_step: Step) -> None:
    """Test hook returns empty state delta if step has no criteria blocks."""
    step_no_blocks = mock_step.model_copy(update={"type": "logic", "hook": "some_hook", "criteria_block_ids": []})
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_step(step_no_blocks)
    deps = _make_deps(workflow_repo=repo)
    result = await process_matrix_flattening(base_hook_state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


@pytest.mark.asyncio
async def test_atom_flattening_invalid_block_format_fails_fast(base_hook_state: HookState, mock_step: Step) -> None:
    """Test hook raises VALIDATION_FAILED when raw block fails Pydantic validation."""
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_step(mock_step)
    repo._prompt_blocks._storage["invalid"] = {"invalid": "format_no_id"}
    deps = _make_deps(workflow_repo=repo, comp_repo=repo)
    with pytest.raises(AppException) as exc_info:
        await process_matrix_flattening(base_hook_state, deps)
    assert exc_info.value.status_code == 500
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_atom_flattening_no_matching_matrix_blocks(base_hook_state: HookState, mock_step: Step) -> None:
    """Test hook returns empty state delta if all_blocks has no matching IDs."""
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_step(mock_step)
    deps = _make_deps(workflow_repo=repo, comp_repo=repo)
    result = await process_matrix_flattening(base_hook_state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


@pytest.mark.asyncio
async def test_atom_flattening_propagates_causal_dependencies(base_hook_state: HookState, mock_step: Step) -> None:
    """Test that depends_on causal preconditions in TDAAssertion are preserved in FlattenedAtom."""
    edge = CausalEdge(
        edge_reasoning="Parent prerequisite must pass before child evaluation.",
        tda_id="tda_00000000000000010000000000000000",
        source_id="chk_source_1",
        expected_status=ExecutionStatus.PASSED,
    )
    parent_tda = TDAAssertion(
        tda_id="tda_00000000000000010000000000000000",
        concept_description="Parent Root Assertion",
        inverse_evidence=False,
        aggregation_mode="EXISTS",
    )
    child_tda = TDAAssertion(
        tda_id="tda_00000000000000010000000000000001",
        concept_description="Child Dependent Assertion",
        inverse_evidence=False,
        aggregation_mode="EXISTS",
        depends_on=(edge,),
    )
    claim = MatrixClaim(
        label=I18nText(translations={"en": "Claim With Deps", "fi": "Claim With Deps"}),
        tda_assertions=[parent_tda, child_tda],
    )
    scale = MatrixScale(score=1, ai_label="Level 1", claims=[claim])
    mock_block = MatrixPromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="slug-test-deps",
        label=I18nText(translations={"en": "Label", "fi": "Label"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        scales=[scale],
    )

    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_step(mock_step)
    await repo.create_prompt_block(mock_block)
    deps = _make_deps(workflow_repo=repo, comp_repo=repo)

    state = base_hook_state.model_copy(update={"metadata": ExecutionMetadata(matrix_sampling_strategy=0)})
    result = await process_matrix_flattening(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, FlatteningHookOutput)
    shuffled = result.state_delta.delta.shuffled_atoms
    assert len(shuffled) == 2

    child_atom = next(a for a in shuffled if a.atom_id == "tda_00000000000000010000000000000001")
    assert child_atom.depends_on is not None
    assert len(child_atom.depends_on) == 1
    assert child_atom.depends_on[0].tda_id == "tda_00000000000000010000000000000000"
    assert child_atom.depends_on[0].expected_status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_atom_flattening_transitive_causal_closure(base_hook_state: HookState, mock_step: Step) -> None:
    """Test that Stratified Sampling retains ancestor atoms via Transitive Causal Closure."""
    # 3-tier causal chain: A -> B -> C
    edge_a_to_b = CausalEdge(
        edge_reasoning="A is precondition for B",
        tda_id="tda_0000000000000001000000000000000a",
        source_id="chk_1",
        expected_status=ExecutionStatus.PASSED,
    )
    edge_b_to_c = CausalEdge(
        edge_reasoning="B is precondition for C",
        tda_id="tda_0000000000000001000000000000000b",
        source_id="chk_1",
        expected_status=ExecutionStatus.PASSED,
    )

    atom_a = TDAAssertion(
        tda_id="tda_0000000000000001000000000000000a",
        concept_description="Root Atom A",
        inverse_evidence=False,
        aggregation_mode="EXISTS",
    )
    atom_b = TDAAssertion(
        tda_id="tda_0000000000000001000000000000000b",
        concept_description="Middle Atom B",
        inverse_evidence=False,
        aggregation_mode="EXISTS",
        depends_on=(edge_a_to_b,),
    )
    atom_c = TDAAssertion(
        tda_id="tda_0000000000000001000000000000000c",
        concept_description="Leaf Atom C",
        inverse_evidence=False,
        aggregation_mode="EXISTS",
        depends_on=(edge_b_to_c,),
    )

    # Put all 3 atoms in scale 1 with 7 filler atoms (10 total)
    fillers = [
        TDAAssertion(
            tda_id=f"tda_0000000000000001{i:016x}",
            concept_description=f"Filler Atom {i}",
            inverse_evidence=False,
            aggregation_mode="EXISTS",
        )
        for i in range(1, 8)
    ]
    claim = MatrixClaim(
        label=I18nText(translations={"en": "Scale 1", "fi": "Scale 1"}),
        tda_assertions=[atom_a, atom_b, atom_c, *fillers],
    )
    scale = MatrixScale(score=1, ai_label="Level 1", claims=[claim])
    mock_block = MatrixPromptBlock(
        id="blk_0123456789abcdef0123456789abcdef",
        slug="slug-transitive",
        label=I18nText(translations={"en": "Label", "fi": "Label"}),
        description=I18nText(translations={"en": "Desc", "fi": "Desc"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        scales=[scale],
    )

    repo = InMemoryUnifiedWorkflowRepository()
    await repo.save_step(mock_step)
    await repo.create_prompt_block(mock_block)
    deps = _make_deps(workflow_repo=repo, comp_repo=repo)

    # Use sampling strategy 1 (select 1 atom initially)
    state = base_hook_state.model_copy(update={"metadata": ExecutionMetadata(matrix_sampling_strategy=1)})
    result = await process_matrix_flattening(state, deps)

    assert result.success is True
    assert result.state_delta is not None
    assert isinstance(result.state_delta.delta, FlatteningHookOutput)
    shuffled = result.state_delta.delta.shuffled_atoms
    atom_ids = {a.atom_id for a in shuffled}

    # If atom_c was selected, atom_b and atom_a MUST also be in the output set
    if "tda_0000000000000001000000000000000c" in atom_ids:
        assert "tda_0000000000000001000000000000000b" in atom_ids
        assert "tda_0000000000000001000000000000000a" in atom_ids

    # If atom_b was selected, atom_a MUST also be in the output set
    if "tda_0000000000000001000000000000000b" in atom_ids:
        assert "tda_0000000000000001000000000000000a" in atom_ids
