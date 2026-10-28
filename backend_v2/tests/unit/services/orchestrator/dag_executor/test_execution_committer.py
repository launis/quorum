"""Unit tests for backend_v2.services.orchestrator.dag_executor.execution_committer.

Verifies ExecutionCommitter initialization, commit_trace state persistence into
InMemoryUnifiedWorkflowRepository, and RFC 7807 PROGRESS_UPDATE_FAILED error propagation.
"""

from __future__ import annotations

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import (
    ExecutionRecord,
    ExecutionStep,
    ExecutionStepState,
    FrozenContext,
)
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.state import TraceEvent
from backend_v2.services.orchestrator.dag_executor.execution_committer import ExecutionCommitter
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.mark.asyncio
async def test_execution_committer_dual_storage_and_lightweight_db_update() -> None:
    """Verify ExecutionCommitter.commit_trace persists trace, frozen_context, and step_states."""
    repo = InMemoryUnifiedWorkflowRepository()
    execution_id = "exe_1111222233334444"
    initial_record = ExecutionRecord(
        id=execution_id,
        workflow_id="wf_1111222233334444",
        target_locale="en",
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "initial content"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.PENDING,
        steps=[],
        step_states={},
        output_profile_id="prf_1111222233334444",
    )
    repo.set_execution(initial_record)

    committer = ExecutionCommitter(exec_repo=repo, execution_id=execution_id)
    assert committer.exec_repo is repo
    assert committer.execution_id == execution_id

    step_item = ExecutionStep(
        id="stp_1111222233334444",
        label="Step 1",
        status=ExecutionStatus.PASSED,
        progress=100,
    )
    step_state = ExecutionStepState(
        id="stp_1111222233334444",
        status=ExecutionStatus.PASSED,
        progress=100,
        label="Step 1",
    )
    trace_events = [
        TraceEvent(
            step_name="stp_1111222233334444",
            event_type="output",
            content="completed",
        )
    ]
    frozen_ctx = FrozenContext()
    ctx_vars = ContextVariablesDTO()

    await committer.commit_trace(
        trace=trace_events,
        status=ExecutionStatus.RUNNING,
        step_states={"stp_1111222233334444": step_state},
        error=None,
        frozen_context=frozen_ctx,
        context_variables=ctx_vars,
        steps=[step_item],
    )

    updated = await repo.get_execution(execution_id)
    assert isinstance(updated, ExecutionRecord)
    assert updated.status == ExecutionStatus.RUNNING
    assert len(updated.execution_trace) == 1
    assert updated.execution_trace[0].step_name == "stp_1111222233334444"
    assert "stp_1111222233334444" in updated.step_states
    assert updated.step_states["stp_1111222233334444"].status == ExecutionStatus.PASSED
    assert len(updated.steps) == 1
    assert updated.steps[0].id == "stp_1111222233334444"


@pytest.mark.asyncio
async def test_execution_committer_repository_failure_raises_progress_update_failed() -> None:
    """Verify ExecutionCommitter.commit_trace logs and raises PROGRESS_UPDATE_FAILED on DB failure."""
    repo = InMemoryUnifiedWorkflowRepository()
    execution_id = "exe_5555666677778888"
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
    execution_id = "exe_9999000011112222"
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
