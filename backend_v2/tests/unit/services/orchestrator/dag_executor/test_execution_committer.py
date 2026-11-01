"""Unit tests for backend_v2.services.orchestrator.dag_executor.execution_committer.

Verifies ExecutionCommitter initialization, commit_trace state persistence into
InMemoryUnifiedWorkflowRepository, and RFC 7807 PROGRESS_UPDATE_FAILED error propagation.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import (
    ExecutionRecord,
    ExecutionStep,
    ExecutionStepState,
    FrozenContext,
)
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.matrix_scorecard import (
    HumanOverrideDTO,
    ScorecardAtomDTO,
)
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus, VisualIntent
from backend_v2.models.state import TraceEvent
from backend_v2.services.orchestrator.dag_executor.execution_committer import ExecutionCommitter
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.mark.asyncio
async def test_execution_committer_dual_storage_and_lightweight_db_update() -> None:
    """Verify ExecutionCommitter.commit_trace persists trace, frozen_context, and step_states."""
    repo = InMemoryUnifiedWorkflowRepository()
    execution_id = "exe_0195f3a0000070018111222233334444"
    initial_record = ExecutionRecord(
        id=execution_id,
        workflow_id="wf_0195f3a0000070018111222233334444",
        target_locale="en",
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "initial content"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.PENDING,
        steps=[],
        step_states={},
        output_profile_id="prf_0195f3a0000070018111222233334444",
    )
    repo.set_execution(initial_record)

    committer = ExecutionCommitter(exec_repo=repo, execution_id=execution_id)
    assert committer.exec_repo is repo
    assert committer.execution_id == execution_id

    step_item = ExecutionStep(
        id="stp_0195f3a0000070018111222233334444",
        label="Step 1",
        status=ExecutionStatus.PASSED,
        progress=100,
    )
    step_state = ExecutionStepState(
        id="stp_0195f3a0000070018111222233334444",
        status=ExecutionStatus.PASSED,
        progress=100,
        label="Step 1",
    )
    trace_events = [
        TraceEvent(
            step_name="stp_0195f3a0000070018111222233334444",
            event_type="output",
            content="completed",
        )
    ]
    frozen_ctx = FrozenContext()
    ctx_vars = ContextVariablesDTO()

    await committer.commit_trace(
        trace=trace_events,
        status=ExecutionStatus.RUNNING,
        step_states={"stp_0195f3a0000070018111222233334444": step_state},
        error=None,
        frozen_context=frozen_ctx,
        context_variables=ctx_vars,
        steps=[step_item],
    )

    updated = await repo.get_execution(execution_id)
    assert isinstance(updated, ExecutionRecord)
    assert updated.status == ExecutionStatus.RUNNING
    assert len(updated.execution_trace) == 1
    assert updated.execution_trace[0].step_name == "stp_0195f3a0000070018111222233334444"
    assert "stp_0195f3a0000070018111222233334444" in updated.step_states
    assert updated.step_states["stp_0195f3a0000070018111222233334444"].status == ExecutionStatus.PASSED
    assert len(updated.steps) == 1
    assert updated.steps[0].id == "stp_0195f3a0000070018111222233334444"


@pytest.mark.asyncio
async def test_execution_committer_repository_failure_raises_progress_update_failed() -> None:
    """Verify ExecutionCommitter.commit_trace logs and raises PROGRESS_UPDATE_FAILED on DB failure."""
    repo = InMemoryUnifiedWorkflowRepository()
    execution_id = "exe_0195f3a0000070058555666677778888"
    committer = ExecutionCommitter(exec_repo=repo, execution_id=execution_id)

    repo.inject_fault("update_execution", RuntimeError("Simulated database outage"))
    try:
        with pytest.raises(AppException) as exc_info:
            await committer.commit_trace(
                trace=[],
                status=ExecutionStatus.FAILED,
                step_states={},
                error="Step failed",
            )
    finally:
        repo.clear_faults()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.PROGRESS_UPDATE_FAILED.value
    assert execution_id in exc_info.value.message


@pytest.mark.asyncio
@pytest.mark.parametrize("invalid_exec_id", ["", "   "])
async def test_execution_committer_empty_execution_id_raises_progress_update_failed(
    invalid_exec_id: str,
) -> None:
    """Verify ExecutionCommitter.commit_trace fails fast when execution_id is empty or whitespace."""
    repo = InMemoryUnifiedWorkflowRepository()
    committer = ExecutionCommitter(exec_repo=repo, execution_id=invalid_exec_id)

    with pytest.raises(AppException) as exc_info:
        await committer.commit_trace(
            trace=[],
            status=ExecutionStatus.RUNNING,
            step_states={},
        )

    assert exc_info.value.status_code == 500
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.PROGRESS_UPDATE_FAILED.value


@pytest.mark.asyncio
async def test_execution_committer_timeout_failure_raises_progress_update_failed() -> None:
    """Verify ExecutionCommitter.commit_trace translates repository TimeoutError into AppException."""
    repo = InMemoryUnifiedWorkflowRepository()
    execution_id = "exe_0195f3a0000070098999000011112222"
    committer = ExecutionCommitter(exec_repo=repo, execution_id=execution_id)

    repo.inject_fault("update_execution", TimeoutError("Database commit timed out"))
    try:
        with pytest.raises(AppException) as exc_info:
            await committer.commit_trace(
                trace=[],
                status=ExecutionStatus.RUNNING,
                step_states={},
            )
    finally:
        repo.clear_faults()

    assert exc_info.value.status_code == 500
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.PROGRESS_UPDATE_FAILED.value
    assert execution_id in exc_info.value.message


@pytest.mark.asyncio
async def test_execution_committer_preserves_concurrent_human_overrides_and_increments_state_version() -> None:
    """Verify commit_trace preserves concurrent human overrides and advances state_version cleanly."""
    repo = InMemoryUnifiedWorkflowRepository()
    execution_id = "exe_0195f3a0000070108111222233334444"
    step_id = "stp_0195f3a0000070108111222233334444"
    extra_step_id = "stp_0195f3a0000070108111222233335555"
    atom_id = "tda_0195f3a0000070108111222233334444"
    extra_atom_id = "tda_0195f3a0000070108111222233335555"

    base_atom = ScorecardAtomDTO(
        atom_id=atom_id,
        level=1,
        level_name="L1",
        claim_label="Claim",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="p",
            step_2_scan_source="s",
            step_3_evaluate_anti_patterns="a",
            step_4_final_conclusion="c",
        ),
        status=ExecutionStatus.FAILED,
        semantic_reasoning="initial",
        contextual_override=False,
        structural_location=None,
        chart_display_label="L1",
        visual_intent=VisualIntent.NEUTRAL,
    )
    initial_step_state = ExecutionStepState(
        id=step_id,
        status=ExecutionStatus.PASSED,
        progress=100,
        label="Step 1",
        scorecard_atoms={atom_id: base_atom},
    )
    extra_step_state = ExecutionStepState(
        id=extra_step_id,
        status=ExecutionStatus.PASSED,
        progress=100,
        label="Extra Step",
    )
    initial_record = ExecutionRecord(
        id=execution_id,
        workflow_id="wf_0195f3a0000070108111222233334444",
        target_locale="en",
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "initial content"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.RUNNING,
        steps=[],
        step_states={step_id: initial_step_state, extra_step_id: extra_step_state},
        output_profile_id="prf_0195f3a0000070108111222233334444",
    )
    repo.set_execution(initial_record)

    # Simulate a concurrent human override persisted to the repository while worker holds un-overridden step_state.
    override_dto = HumanOverrideDTO(
        new_status=ExecutionStatus.PASSED,
        reason="Verified manually by auditor",
        evidence_quotes=[],
        overridden_by="usr_0195f3a0000070108111222233334444",
        overridden_at=datetime.now(timezone.utc),
    )
    overridden_atom = base_atom.model_copy(
        update={
            "status": ExecutionStatus.PASSED,
            "human_override": override_dto,
        }
    )
    extra_overridden_atom = base_atom.model_copy(
        update={
            "atom_id": extra_atom_id,
            "status": ExecutionStatus.PASSED,
            "human_override": override_dto,
        }
    )
    overridden_step_state = initial_step_state.model_copy(
        update={"scorecard_atoms": {atom_id: overridden_atom, extra_atom_id: extra_overridden_atom}}
    )
    override_event = TraceEvent(
        step_name="manual_override",
        event_type="evidence_override",
        content="manual_override_event",
    )
    await repo.update_execution(
        execution_id,
        ExecutionUpdateDTO(
            step_states={step_id: overridden_step_state, extra_step_id: extra_step_state},
            execution_trace=[override_event],
            expected_state_version=1,
        ),
    )
    after_override = await repo.get_execution(execution_id)
    assert after_override is not None
    assert after_override.state_version == 2

    # Worker commits its trace with the older in-memory step_state lacking human_override and extra_step_id.
    committer = ExecutionCommitter(exec_repo=repo, execution_id=execution_id)
    await committer.commit_trace(
        trace=[TraceEvent(step_name=step_id, event_type="output", content="done")],
        status=ExecutionStatus.PASSED,
        step_states={step_id: initial_step_state},
    )

    committed = await repo.get_execution(execution_id)
    assert committed is not None
    assert committed.state_version == 3
    assert committed.status == ExecutionStatus.PASSED
    assert extra_step_id in committed.step_states
    preserved_atom = committed.step_states[step_id].scorecard_atoms[atom_id]
    assert preserved_atom.human_override is not None
    assert preserved_atom.human_override.reason == "Verified manually by auditor"
    assert preserved_atom.status == ExecutionStatus.PASSED
    assert extra_atom_id in committed.step_states[step_id].scorecard_atoms
    assert any(evt.event_type == "evidence_override" for evt in committed.execution_trace)
