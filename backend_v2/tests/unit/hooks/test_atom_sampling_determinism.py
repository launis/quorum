"""Unit tests for atom sampling determinism and boundary value analysis."""

from unittest.mock import AsyncMock

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
from backend_v2.models.dtos.hook_delta import FlatteningHookOutput
from backend_v2.models.enums import BlockDataType, CognitiveTier, PromptBlockCategory
from backend_v2.models.execution_core import ExecutionMetadata


def _build_test_matrix_block(block_id: str, num_atoms_per_scale: int = 10) -> MatrixPromptBlock:
    """Builds a test MatrixPromptBlock with multiple scales and atoms."""
    scales: list[MatrixScale] = []
    for score in [1, 2, 3, 4, 5]:
        claims = [
            MatrixClaim(
                label=I18nText(translations={"en": f"Claim {score}", "fi": f"Väite {score}"}),
                tda_assertions=[
                    TDAAssertion(
                        tda_id=f"tda_{score:016x}{i:016x}",
                        concept_description=f"Concept Scale {score} Item {i}",
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
                ai_label=f"Scale {score}",
                claims=claims,
            )
        )

    return MatrixPromptBlock(
        id=block_id,
        slug=f"slug-{block_id}",
        label=I18nText(translations={"en": f"Label {block_id}", "fi": f"Nimi {block_id}"}),
        description=I18nText(translations={"en": f"Desc {block_id}", "fi": f"Kuvaus {block_id}"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        scales=scales,
    )


def _build_test_step(step_id: str, block_id: str) -> Step:
    """Builds a minimal Step referencing the matrix block."""
    return Step(
        id=step_id,
        name=I18nText(translations={"en": "Step", "fi": "Askel"}),
        slug="step-test",
        role_block_id=None,
        extraction_protocol_block_id="blk_573802341db9d68c",
        criteria_block_ids=[block_id],
        cognitive_tier=CognitiveTier.FAST,
    )


def _build_dependencies(step: Step, block: MatrixPromptBlock) -> HookDependencies:
    """Creates mocked HookDependencies returning the test step and block."""
    mock_workflow_repo = AsyncMock()
    mock_workflow_repo.get_step_by_id.return_value = step.model_dump(mode="json")
    mock_comp_repo = AsyncMock()
    mock_comp_repo.get_all_prompt_blocks.return_value = [block.model_dump(mode="json")]

    return HookDependencies(
        exec_repo=AsyncMock(),
        workflow_repo=mock_workflow_repo,
        comp_repo=mock_comp_repo,
        prompt_block_repo=mock_comp_repo,
        output_profile_repo=AsyncMock(),
        identity_repo=AsyncMock(),
        audit_repo=AsyncMock(),
        system_repo=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_sampling_determinism_across_distinct_execution_ids() -> None:
    """Positive: Two executions with distinct execution_id but identical workflow_id yield identical sampled atoms."""
    block_id = "blk_0123456789abcdef0123456789abcdef"
    step_id = "stp_0123456789abcdef0123456789abcdef"
    block = _build_test_matrix_block(block_id, num_atoms_per_scale=10)
    step = _build_test_step(step_id, block_id)
    deps = _build_dependencies(step, block)

    shared_workflow_id = "wf_01a1d71000000001"

    state_run1 = HookState(
        step_id=step_id,
        execution_id="exe_run_1_aaaaaaaaaaaaaaaa",
        workflow_id=shared_workflow_id,
        task_blueprint=step_id,
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(matrix_sampling_strategy=2),
    )

    state_run2 = HookState(
        step_id=step_id,
        execution_id="exe_run_2_bbbbbbbbbbbbbbbb",
        workflow_id=shared_workflow_id,
        task_blueprint=step_id,
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(matrix_sampling_strategy=2),
    )

    res1 = await process_matrix_flattening(state_run1, deps)
    res2 = await process_matrix_flattening(state_run2, deps)

    assert res1.success is True
    assert res2.success is True
    assert res1.state_delta is not None
    assert res2.state_delta is not None
    assert isinstance(res1.state_delta.delta, FlatteningHookOutput)
    assert isinstance(res2.state_delta.delta, FlatteningHookOutput)

    atoms1 = [item.atom_id for item in res1.state_delta.delta.shuffled_atoms]
    atoms2 = [item.atom_id for item in res2.state_delta.delta.shuffled_atoms]

    # 5 scales * 2 samples = 10 atoms
    assert len(atoms1) == 10
    assert len(atoms2) == 10
    # Crucial proof: 100% deterministic identical selection across runs
    assert atoms1 == atoms2


@pytest.mark.asyncio
async def test_sampling_divergence_across_distinct_workflow_ids() -> None:
    """Positive (Variation Partition): Distinct workflow_ids generate distinct PRNG seeds."""
    block_id = "blk_0123456789abcdef0123456789abcdef"
    step_id = "stp_0123456789abcdef0123456789abcdef"
    block = _build_test_matrix_block(block_id, num_atoms_per_scale=20)
    step = _build_test_step(step_id, block_id)
    deps = _build_dependencies(step, block)

    state_wf1 = HookState(
        step_id=step_id,
        execution_id="exe_1111111111111111",
        workflow_id="wf_alpha_01a1d71000000001",
        task_blueprint=step_id,
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(matrix_sampling_strategy=1),
    )

    state_wf2 = HookState(
        step_id=step_id,
        execution_id="exe_2222222222222222",
        workflow_id="wf_beta_9999999999999999",
        task_blueprint=step_id,
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(matrix_sampling_strategy=1),
    )

    res1 = await process_matrix_flattening(state_wf1, deps)
    res2 = await process_matrix_flattening(state_wf2, deps)

    assert res1.state_delta is not None
    assert res2.state_delta is not None
    assert isinstance(res1.state_delta.delta, FlatteningHookOutput)
    assert isinstance(res2.state_delta.delta, FlatteningHookOutput)

    atoms1 = [item.atom_id for item in res1.state_delta.delta.shuffled_atoms]
    atoms2 = [item.atom_id for item in res2.state_delta.delta.shuffled_atoms]

    assert len(atoms1) == 5
    assert len(atoms2) == 5
    # With 20 atoms per scale and sampling 1, seeds derived from distinct workflow_ids should differ
    assert set(atoms1) != set(atoms2)


@pytest.mark.asyncio
async def test_sampling_boundary_values_bva() -> None:
    """Boundary Value Analysis: Strategy 0 (all), strategy == scale size (exact bound), strategy 1 (min limit)."""
    block_id = "blk_0123456789abcdef0123456789abcdef"
    step_id = "stp_0123456789abcdef0123456789abcdef"
    block = _build_test_matrix_block(block_id, num_atoms_per_scale=5)
    step = _build_test_step(step_id, block_id)
    deps = _build_dependencies(step, block)

    # 1. BVA Min Boundary (strategy=0: all 25 atoms retained)
    state_all = HookState(
        step_id=step_id,
        execution_id="exe_all",
        workflow_id="wf_bva",
        task_blueprint=step_id,
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(matrix_sampling_strategy=0),
    )
    res_all = await process_matrix_flattening(state_all, deps)
    assert res_all.state_delta is not None
    assert isinstance(res_all.state_delta.delta, FlatteningHookOutput)
    assert len(res_all.state_delta.delta.shuffled_atoms) == 25

    # 2. BVA Exact Boundary (strategy=5: exactly equal to num_atoms_per_scale, all 25 retained)
    state_exact = HookState(
        step_id=step_id,
        execution_id="exe_exact",
        workflow_id="wf_bva",
        task_blueprint=step_id,
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(matrix_sampling_strategy=5),
    )
    res_exact = await process_matrix_flattening(state_exact, deps)
    assert res_exact.state_delta is not None
    assert isinstance(res_exact.state_delta.delta, FlatteningHookOutput)
    assert len(res_exact.state_delta.delta.shuffled_atoms) == 25

    # 3. BVA Minimum Sampling (strategy=1: 1 per scale = 5 atoms)
    state_min = HookState(
        step_id=step_id,
        execution_id="exe_min",
        workflow_id="wf_bva",
        task_blueprint=step_id,
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata(matrix_sampling_strategy=1),
    )
    res_min = await process_matrix_flattening(state_min, deps)
    assert res_min.state_delta is not None
    assert isinstance(res_min.state_delta.delta, FlatteningHookOutput)
    assert len(res_min.state_delta.delta.shuffled_atoms) == 5


@pytest.mark.asyncio
async def test_sampling_negative_strategy_fails_fast() -> None:
    """Negative: Invalid negative sampling strategy raises AppException(CONFIGURATION_ERROR)."""
    block_id = "blk_0123456789abcdef0123456789abcdef"
    step_id = "stp_0123456789abcdef0123456789abcdef"
    block = _build_test_matrix_block(block_id, num_atoms_per_scale=5)
    step = _build_test_step(step_id, block_id)
    deps = _build_dependencies(step, block)

    state_invalid = HookState(
        step_id=step_id,
        execution_id="exe_invalid",
        workflow_id="wf_bva",
        task_blueprint=step_id,
        inputs=ExecutionInputsDTO(raw_inputs={}),
        global_context_vars=GlobalContextVarsDTO(),
        metadata=ExecutionMetadata.model_construct(matrix_sampling_strategy=-1),
    )

    with pytest.raises(AppException) as exc_info:
        await process_matrix_flattening(state_invalid, deps)

    assert exc_info.value.status_code == 400
    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR.value
