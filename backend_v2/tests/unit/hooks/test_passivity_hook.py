"""Unit tests for passivity_penalty scoring hook.

Validates passivity detection, minimum mathematical score triggering,
schema validation, RFC 7807 dual-reporting, and Fail-Fast error boundaries.
"""

from __future__ import annotations

from typing import Any

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    HookDeltaDTO,
    HookDependencies,
    HookState,
)
from backend_v2.database.interfaces import IPromptBlockRepository, IWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.hooks.scoring.matrix_hook import MatrixAggregationStateDTO
from backend_v2.hooks.scoring.passivity_hook import enforce_passivity_penalty_hook
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.step import Step
from backend_v2.models.dtos.hook_delta import PassivityDetectionResultDTO
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, LightweightMatrixOutput
from backend_v2.models.enums import PromptBlockCategory
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _build_test_matrix_block(pb_id: str, scales: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Construct a valid MatrixPromptBlock dictionary."""
    if scales is None:
        scales = [
            {"score": 1, "ai_label": "Foundational", "claims": []},
            {"score": 5, "ai_label": "Exemplary", "claims": []},
        ]
    return {
        "id": pb_id,
        "slug": "leadership_matrix",
        "category_id": PromptBlockCategory.MATRIX.value,
        "label": {"translations": {"en": "Leadership Dimension"}},
        "description": {"translations": {"en": "Evaluates leadership"}},
        "type": "float",
        "ai_description": "Evaluates leadership maturity.",
        "scales": scales,
    }


def _build_test_step(step_id: str, criteria_block_ids: list[str]) -> dict[str, Any]:
    """Construct a valid Step dictionary."""
    return {
        "id": step_id,
        "slug": "leadership_eval_step",
        "name": {"translations": {"en": "Leadership Evaluation"}},
        "type": "logic",
        "hook": "enforce_passivity_penalty",
        "criteria_block_ids": criteria_block_ids,
    }


def _build_repo(
    step: Step | dict[str, Any] | None = None,
    prompt_block: MatrixPromptBlock | dict[str, Any] | None = None,
) -> InMemoryUnifiedWorkflowRepository:
    """Build a stateful in-memory repository seeded with test fixtures."""
    repo = InMemoryUnifiedWorkflowRepository()
    if step is not None:
        if isinstance(step, Step):
            repo._workflows._steps[step.id] = step
        else:
            repo._workflows._steps[step["id"]] = step
    if prompt_block is not None:
        if isinstance(prompt_block, MatrixPromptBlock):
            repo._prompt_blocks._storage[prompt_block.id] = prompt_block
        else:
            repo._prompt_blocks._storage[prompt_block["id"]] = prompt_block
    return repo


def _build_mock_deps(
    workflow_repo: IWorkflowRepository | None | object = ...,
    prompt_block_repo: IPromptBlockRepository | None | object = ...,
    repo: InMemoryUnifiedWorkflowRepository | None = None,
) -> HookDependencies:
    """Build mock HookDependencies container."""
    base_repo = repo if repo is not None else InMemoryUnifiedWorkflowRepository()
    wf = base_repo if workflow_repo is ... else workflow_repo
    pb = base_repo if prompt_block_repo is ... else prompt_block_repo
    return HookDependencies(
        exec_repo=base_repo,
        workflow_repo=wf,  # type: ignore[arg-type]
        comp_repo=base_repo,
        prompt_block_repo=pb,  # type: ignore[arg-type]
        output_profile_repo=base_repo,
        identity_repo=base_repo,
        system_repo=base_repo,
        audit_repo=base_repo,
    )


@pytest.mark.asyncio
async def test_passivity_hook_missing_state_raises() -> None:
    """Test that enforce_passivity_penalty_hook raises VALIDATION_FAILED when state is None."""
    deps = _build_mock_deps()
    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(None, deps)
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.name


@pytest.mark.asyncio
async def test_passivity_hook_missing_workflow_repo_raises() -> None:
    """Test that enforce_passivity_penalty_hook raises HOOK_EXECUTION_FAILED when workflow_repo is None."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id="stp_1111222233334444",
        metadata=ExecutionMetadata(),
    )
    deps = _build_mock_deps(workflow_repo=None)
    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)
    assert exc_info.value.error_code == ErrorCodes.HOOK_EXECUTION_FAILED.name


@pytest.mark.asyncio
async def test_passivity_hook_missing_blueprint_id_raises() -> None:
    """Test that enforce_passivity_penalty_hook raises VALIDATION_FAILED when blueprint_id is missing."""
    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=None,
        task_blueprint=None,
        metadata=ExecutionMetadata(),
    )
    deps = _build_mock_deps()
    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.name


@pytest.mark.asyncio
async def test_passivity_hook_step_not_found_raises() -> None:
    """Test that enforce_passivity_penalty_hook raises RESOURCE_NOT_FOUND when step is not found."""
    deps = _build_mock_deps()

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id="stp_nonexistent1234",
        metadata=ExecutionMetadata(),
    )
    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)
    assert exc_info.value.error_code == ErrorCodes.RESOURCE_NOT_FOUND.name


@pytest.mark.asyncio
async def test_passivity_hook_step_validation_error_raises() -> None:
    """Test that enforce_passivity_penalty_hook wraps Step ValidationError in VALIDATION_FAILED."""
    repo = _build_repo(step={"id": "stp_1111222233334444", "invalid_key": "missing_required_fields"})
    deps = _build_mock_deps(repo=repo)

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id="stp_1111222233334444",
        metadata=ExecutionMetadata(),
    )
    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.name


@pytest.mark.asyncio
async def test_passivity_hook_matrix_has_no_scales_raises() -> None:
    """Test that enforce_passivity_penalty_hook raises CONFIGURATION_ERROR when scales are empty."""
    step_id = "stp_1111222233334444"
    pb_id = "blk_1111222233334444"

    repo = _build_repo(
        step=_build_test_step(step_id, [pb_id]),
        prompt_block=_build_test_matrix_block(pb_id, scales=[]),
    )
    deps = _build_mock_deps(repo=repo)

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
    )
    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)
    assert exc_info.value.error_code in (
        ErrorCodes.CONFIGURATION_ERROR.name,
        ErrorCodes.VALIDATION_FAILED.name,
    )


@pytest.mark.asyncio
async def test_passivity_hook_non_matrix_prompt_block_skipped() -> None:
    """Test that enforce_passivity_penalty_hook cleanly skips non-matrix prompt blocks."""
    step_id = "stp_1111222233334444"
    pb_id = "blk_1111222233334444"

    non_matrix_pb = {
        "id": pb_id,
        "slug": "system_instruction",
        "category_id": "system_rule",
        "label": {"translations": {"en": "Instruction"}},
        "description": {"translations": {"en": "Instruction desc"}},
        "instruction_text": "System rule instruction",
    }
    repo = _build_repo(step=_build_test_step(step_id, [pb_id]), prompt_block=non_matrix_pb)
    deps = _build_mock_deps(repo=repo)

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={pb_id: {"raw_score": 1.0}}),
    )
    result = await enforce_passivity_penalty_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is None or delta == {}


@pytest.mark.asyncio
async def test_passivity_hook_legacy_score_card_raises() -> None:
    """Test that enforce_passivity_penalty_hook raises VALIDATION_FAILED if legacy score_card is found."""
    step_id = "stp_1111222233334444"
    repo = _build_repo(step=_build_test_step(step_id, []))
    deps = _build_mock_deps(repo=repo)

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={"score_card": {"dim": 1.0}}),
    )
    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.name
    assert "score_card" in exc_info.value.message


@pytest.mark.asyncio
async def test_passivity_hook_corrupted_matrix_payload_raises() -> None:
    """Test that enforce_passivity_penalty_hook raises VALIDATION_FAILED on corrupted matrix payload."""
    step_id = "stp_1111222233334444"
    pb_id = "blk_1111222233334444"

    repo = _build_repo(step=_build_test_step(step_id, [pb_id]), prompt_block=_build_test_matrix_block(pb_id))
    deps = _build_mock_deps(repo=repo)

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO.model_construct(
            raw_inputs={pb_id: {"raw_score": "not_a_valid_float", "normalized_score": 10.0, "justification": "text"}}
        ),
    )
    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.name


@pytest.mark.asyncio
async def test_passivity_hook_penalty_triggered_when_score_at_min() -> None:
    """Test that enforce_passivity_penalty_hook detects passivity when raw_score <= math_min."""
    step_id = "stp_1111222233334444"
    pb_id = "blk_1111222233334444"

    repo = _build_repo(step=_build_test_step(step_id, [pb_id]), prompt_block=_build_test_matrix_block(pb_id))
    deps = _build_mock_deps(repo=repo)

    matrix_output = LightweightMatrixOutput(
        raw_score=1.0,
        normalized_score=0.0,
        justification="Minimum baseline performance.",
    )

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={pb_id: matrix_output.model_dump(mode="json")}),
    )
    result = await enforce_passivity_penalty_hook(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta == PassivityDetectionResultDTO(passivity_detected=True)


@pytest.mark.asyncio
async def test_passivity_hook_no_penalty_when_score_above_min() -> None:
    """Test that enforce_passivity_penalty_hook does not penalize scores strictly above math_min."""
    step_id = "stp_1111222233334444"
    pb_id = "blk_1111222233334444"

    repo = _build_repo(step=_build_test_step(step_id, [pb_id]), prompt_block=_build_test_matrix_block(pb_id))
    deps = _build_mock_deps(repo=repo)

    matrix_output = LightweightMatrixOutput(
        raw_score=3.5,
        normalized_score=62.5,
        justification="Satisfactory performance.",
    )

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={pb_id: matrix_output.model_dump(mode="json")}),
    )
    result = await enforce_passivity_penalty_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is None


@pytest.mark.asyncio
async def test_passivity_hook_raw_score_none_does_not_trigger_penalty() -> None:
    """Test that enforce_passivity_penalty_hook ignores raw_score=None."""
    step_id = "stp_1111222233334444"
    pb_id = "blk_1111222233334444"

    repo = _build_repo(step=_build_test_step(step_id, [pb_id]), prompt_block=_build_test_matrix_block(pb_id))
    deps = _build_mock_deps(repo=repo)

    matrix_output = LightweightMatrixOutput(
        raw_score=None,
        normalized_score=None,
        justification="No evaluation performed.",
    )

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={pb_id: matrix_output.model_dump(mode="json")}),
    )
    result = await enforce_passivity_penalty_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is None


@pytest.mark.asyncio
async def test_passivity_hook_dynamic_inputs_preference() -> None:
    """Test that dynamic_inputs takes precedence over raw_inputs."""
    step_id = "stp_1111222233334444"
    pb_id = "blk_1111222233334444"

    repo = _build_repo(step=_build_test_step(step_id, [pb_id]), prompt_block=_build_test_matrix_block(pb_id))
    deps = _build_mock_deps(repo=repo)

    # raw_inputs has high score, dynamic_inputs has minimum score
    high_matrix = LightweightMatrixOutput(raw_score=5.0, normalized_score=100.0, justification="High")
    low_matrix = LightweightMatrixOutput(raw_score=1.0, normalized_score=0.0, justification="Low")

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(
            raw_inputs={pb_id: high_matrix.model_dump(mode="json")},
            dynamic_inputs={pb_id: low_matrix.model_dump(mode="json")},
        ),
    )
    result = await enforce_passivity_penalty_hook(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta == PassivityDetectionResultDTO(passivity_detected=True)


@pytest.mark.asyncio
async def test_passivity_hook_with_base_model_input() -> None:
    """Test that enforce_passivity_penalty_hook handles
    LightweightMatrixOutput model instances directly in raw_inputs.
    """
    step_id = "stp_1111222233334444"
    pb_id = "blk_1111222233334444"

    repo = _build_repo(step=_build_test_step(step_id, [pb_id]), prompt_block=_build_test_matrix_block(pb_id))
    deps = _build_mock_deps(repo=repo)

    matrix_model = LightweightMatrixOutput(raw_score=1.0, normalized_score=0.0, justification="Low score via BaseModel")

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(raw_inputs={pb_id: matrix_model}),
    )
    result = await enforce_passivity_penalty_hook(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta == PassivityDetectionResultDTO(passivity_detected=True)


@pytest.mark.asyncio
async def test_passivity_hook_empty_inputs_continues_cleanly() -> None:
    """Test that enforce_passivity_penalty_hook cleanly handles empty inputs."""
    step_id = "stp_1111222233334444"
    repo = _build_repo(step=_build_test_step(step_id, []))
    deps = _build_mock_deps(repo=repo)

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(),
    )
    result = await enforce_passivity_penalty_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert delta is None or delta == {}


@pytest.mark.asyncio
async def test_passivity_hook_uses_task_blueprint_fallback() -> None:
    """Test that enforce_passivity_penalty_hook falls back to task_blueprint when step_id is None."""
    blueprint_id = "stp_1234567890abcdef"
    repo = _build_repo(step=_build_test_step(blueprint_id, []))
    deps = _build_mock_deps(repo=repo)

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=None,
        task_blueprint=blueprint_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(),
    )
    result = await enforce_passivity_penalty_hook(state, deps)
    assert result.success is True
    assert "get_step_by_id" in repo._workflows._call_counts
    assert repo._workflows._call_counts["get_step_by_id"] >= 1


@pytest.mark.asyncio
async def test_passivity_hook_prompt_block_validation_error_raises() -> None:
    """Test that enforce_passivity_penalty_hook wraps PromptBlock ValidationError in VALIDATION_FAILED."""
    step_id = "stp_1111222233334444"
    pb_id = "blk_1111222233334444"

    repo = _build_repo(
        step=_build_test_step(step_id, [pb_id]),
        prompt_block={"id": pb_id, "category_id": PromptBlockCategory.MATRIX.value},
    )
    deps = _build_mock_deps(repo=repo)

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
    )
    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED.name


@pytest.mark.asyncio
async def test_passivity_hook_matrix_aggregation_state_dto_passive_detected() -> None:
    """Test passivity detection when MatrixAggregationStateDTO only has minimum scale hits."""
    step_id = "stp_1111222233334444"
    pb_id = "blk_1111222233334444"

    repo = _build_repo(step=_build_test_step(step_id, [pb_id]), prompt_block=_build_test_matrix_block(pb_id))
    deps = _build_mock_deps(repo=repo)

    aggregation_state = MatrixAggregationStateDTO(
        scale_stats={
            1.0: LevelStatsDTO(hits=2, total=2),
            5.0: LevelStatsDTO(hits=0, total=2),
        }
    )

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(dynamic_inputs={pb_id: aggregation_state}),
    )

    result = await enforce_passivity_penalty_hook(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta == PassivityDetectionResultDTO(passivity_detected=True)


@pytest.mark.asyncio
async def test_passivity_hook_matrix_aggregation_state_dto_not_passive() -> None:
    """Test that passivity is not detected when higher scale levels have hits."""
    step_id = "stp_1111222233334444"
    pb_id = "blk_1111222233334444"

    repo = _build_repo(step=_build_test_step(step_id, [pb_id]), prompt_block=_build_test_matrix_block(pb_id))
    deps = _build_mock_deps(repo=repo)

    aggregation_state = MatrixAggregationStateDTO(
        scale_stats={
            1.0: LevelStatsDTO(hits=1, total=2),
            5.0: LevelStatsDTO(hits=1, total=2),
        }
    )

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
        inputs=ExecutionInputsDTO(dynamic_inputs={pb_id: aggregation_state}),
    )

    result = await enforce_passivity_penalty_hook(state, deps)
    assert result.success is True
    assert result.state_delta is not None
    assert result.state_delta.delta is None


@pytest.mark.asyncio
async def test_passivity_hook_empty_scales_raises_configuration_error() -> None:
    """Test that enforce_passivity_penalty_hook raises CONFIGURATION_ERROR if matrix block has empty scales."""
    step_id = "stp_1111222233334444"
    pb_id = "blk_1111222233334444"

    repo = _build_repo(
        step=_build_test_step(step_id, [pb_id]),
        prompt_block=MatrixPromptBlock.model_construct(id=pb_id, slug="leadership_matrix", scales=[]),
    )
    deps = _build_mock_deps(repo=repo)

    state = HookState(
        execution_id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        step_id=step_id,
        metadata=ExecutionMetadata(),
    )
    with pytest.raises(AppException) as exc_info:
        await enforce_passivity_penalty_hook(state, deps)
    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR.name
