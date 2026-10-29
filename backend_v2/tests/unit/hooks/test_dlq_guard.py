"""Unit tests for the Dead Letter Queue (DLQ) strict mode guard hook."""

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookResult,
    HookState,
)
from backend_v2.exceptions import AppException
from backend_v2.hooks.dlq_guard import dlq_strict_mode_guard_hook
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.inputs import DLQAtomSchema
from backend_v2.models.dtos.atom_result import AtomResultDTO, ErrorDetailsDTO
from backend_v2.models.enums import EntityPrefix, ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def dummy_deps() -> HookDependencies:
    """Create hermetic in-memory HookDependencies for testing.

    Returns:
        HookDependencies wired to InMemoryUnifiedWorkflowRepository.
    """
    repo = InMemoryUnifiedWorkflowRepository()
    return HookDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
    )


def test_dlq_guard_success_no_dlqs(dummy_deps: HookDependencies) -> None:
    """Verify that dlq_strict_mode_guard passes when there are no DLQs."""
    state = HookState(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "evaluations": [
                    DLQAtomSchema(atom_id="atom_1", status="PASS"),
                    DLQAtomSchema(atom_id="atom_2", status="FAIL"),
                    DLQAtomSchema(atom_id="atom_3", status="PASS"),
                ]
            }
        ),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )

    result = dlq_strict_mode_guard_hook(state, dummy_deps)

    assert isinstance(result, HookResult)
    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


def test_dlq_guard_success_under_threshold(dummy_deps: HookDependencies) -> None:
    """Verify that dlq_strict_mode_guard passes when DLQ ratio is exactly at or under 10%."""
    # 1 DLQ out of 10 atoms = 10% (boundary value: should pass)
    state = HookState(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "evaluations": [
                    DLQAtomSchema(atom_id="atom_1", status="DLQ"),
                    *[DLQAtomSchema(atom_id=f"atom_{i}", status="PASS") for i in range(2, 11)],
                ]
            }
        ),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )

    result = dlq_strict_mode_guard_hook(state, dummy_deps)

    assert isinstance(result, HookResult)
    assert result.success is True
    assert result.state_delta is not None
    assert not result.state_delta.delta


def test_dlq_guard_fails_over_threshold(dummy_deps: HookDependencies) -> None:
    """Verify that dlq_strict_mode_guard raises AppException when DLQ ratio > 10%."""
    # 2 DLQs out of 10 atoms = 20% > 10% (should fail fast)
    state = HookState(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "evaluations": [
                    DLQAtomSchema(atom_id="atom_1", status="DLQ"),
                    DLQAtomSchema(atom_id="atom_2", status="DLQ"),
                    *[DLQAtomSchema(atom_id=f"atom_{i}", status="PASS") for i in range(3, 11)],
                ]
            }
        ),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        dlq_strict_mode_guard_hook(state, dummy_deps)

    assert exc_info.value.status_code == 500
    assert "Strict Fail-Fast: DLQ ratio" in exc_info.value.message
    assert "exceeded the 10.00% absolute limit." in exc_info.value.message


def test_dlq_guard_atom_result_dto_system_error_fails_over_threshold(dummy_deps: HookDependencies) -> None:
    """Verify that AtomResultDTO with SYSTEM_ERROR is counted toward DLQ threshold."""
    state = HookState(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        inputs=ExecutionInputsDTO(
            raw_inputs={
                "evaluations": [
                    AtomResultDTO(
                        tda_id="tda_0195f3a0000070008000000000000001",
                        status=ExecutionStatus.SYSTEM_ERROR,
                        error_details=ErrorDetailsDTO(error_code="LLM_TIMEOUT", message="Timeout"),
                    ),
                    AtomResultDTO(
                        tda_id="tda_0195f3a0000070008000000000000002",
                        status=ExecutionStatus.PASSED,
                        evaluation_reasoning="Verified claim.",
                        source_quotes=("Exact quote",),
                    ),
                ]
            }
        ),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        dlq_strict_mode_guard_hook(state, dummy_deps)

    assert exc_info.value.status_code == 500
    assert "50.00%" in exc_info.value.message


def test_dlq_guard_unhydrated_dlq_atom_validation_fails_over_threshold(dummy_deps: HookDependencies) -> None:
    """Verify that unhydrated raw evaluation entries are validated via DLQAtomSchema.model_validate."""
    unhydrated_inputs = ExecutionInputsDTO.model_construct(
        raw_inputs={
            "evaluations": [
                {"atom_id": "atom_1", "status": "DLQ"},
                {"atom_id": "atom_2", "status": "PASS"},
            ]
        }
    )
    state = HookState.model_construct(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        inputs=unhydrated_inputs,
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )

    with pytest.raises(AppException) as exc_info:
        dlq_strict_mode_guard_hook(state, dummy_deps)

    assert exc_info.value.status_code == 500
    assert "50.00%" in exc_info.value.message


def test_dlq_guard_missing_inputs_bypasses(dummy_deps: HookDependencies) -> None:
    """Verify that empty raw_inputs bypasses the DLQ guard cleanly."""
    state = HookState(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        inputs=ExecutionInputsDTO(raw_inputs={}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    result = dlq_strict_mode_guard_hook(state, dummy_deps)
    assert result.success is True


def test_dlq_guard_missing_evaluations_bypasses(dummy_deps: HookDependencies) -> None:
    """Verify that missing 'evaluations' key in raw_inputs bypasses the DLQ guard cleanly."""
    state = HookState(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        inputs=ExecutionInputsDTO(raw_inputs={"other_key": "val"}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    result = dlq_strict_mode_guard_hook(state, dummy_deps)
    assert result.success is True


def test_dlq_guard_evaluations_not_list_raises(dummy_deps: HookDependencies) -> None:
    """Verify that non-list 'evaluations' raises AppException with HTTP 500."""
    state = HookState(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        inputs=ExecutionInputsDTO(raw_inputs={"evaluations": "not_a_list"}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    with pytest.raises(AppException) as exc:
        dlq_strict_mode_guard_hook(state, dummy_deps)
    assert exc.value.status_code == 500
    assert "'evaluations' must be a list" in exc.value.message


def test_dlq_guard_evaluations_atom_malformed_raises(dummy_deps: HookDependencies) -> None:
    """Verify that a malformed evaluation atom raises AppException with HTTP 500."""
    state = HookState(
        execution_id=generate_opaque_id(EntityPrefix.EXECUTION),
        workflow_id=generate_opaque_id(EntityPrefix.WORKFLOW),
        inputs=ExecutionInputsDTO(raw_inputs={"evaluations": ["invalid_atom_not_dict"]}),
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
    )
    with pytest.raises(AppException) as exc:
        dlq_strict_mode_guard_hook(state, dummy_deps)
    assert exc.value.status_code == 500
    assert "Evaluation atom malformed" in exc.value.message
