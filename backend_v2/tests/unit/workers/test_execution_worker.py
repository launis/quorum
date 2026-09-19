"""Unit tests for execution worker enforcing Tripartite Phase 1 Sovereignty."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.workers.execution_worker import execute_workflow_job


@pytest.mark.asyncio
async def test_execution_worker_sets_status_passed_and_no_synthetic_steps() -> None:
    """Verify that execute_workflow_job marks execution PASSED and injects zero sys_render steps."""
    mock_workflow = Workflow(
        id="wor_0123456789abcdef",
        slug="test-workflow",
        name="Test Workflow",
        description="Test Description",
        status="active",
        version=1,
        default_strictness_level=1,
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )
    mock_record = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        status=ExecutionStatus.PENDING,
        target_locale="fi",
        progress=None,
        status_message=None,
        steps=[
            ExecutionStep(
                id="stp_0123456789abcdef",
                label="Analytical Step",
                status=ExecutionStatus.PASSED,
            )
        ],
    )

    mock_repo = MagicMock()
    mock_repo.get_workflow = AsyncMock(return_value=mock_workflow)
    mock_repo.get_execution = AsyncMock(return_value=mock_record)
    mock_repo.update_execution = AsyncMock()

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=mock_record)

    mock_preflight = MagicMock()
    mock_preflight.run = AsyncMock()

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "preflight_service": mock_preflight,
        "redis": None,
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs={},
        execution_id="exe_0123456789abcdef",
    )

    assert result["status"] == "COMPLETED"
    assert mock_repo.update_execution.called
    update_call = mock_repo.update_execution.call_args
    update_dto = update_call[0][1]

    # Invariant 1: status is PASSED immediately upon DAG completion
    assert update_dto.status == ExecutionStatus.PASSED
    assert update_dto.completed_at is not None

    # Invariant 2: zero synthetic sys_render steps in steps list
    step_ids = [s.id for s in update_dto.steps]
    for s_id in step_ids:
        assert not s_id.startswith("sys_render"), f"Found synthetic render step: {s_id}"


@pytest.mark.asyncio
async def test_execution_worker_enqueues_zero_downstream_jobs() -> None:
    """Verify that execute_workflow_job does NOT auto-enqueue any background report/render jobs."""
    mock_workflow = Workflow(
        id="wor_0123456789abcdef",
        slug="test-workflow",
        name="Test Workflow",
        description="Test Description",
        status="active",
        version=1,
        default_strictness_level=50,
        model_registry_id="sys_e26807f3bfa3454d",
        historical_context_mode=HistoricalContextMode.DISABLED,
        steps=[],
    )
    mock_record = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        status=ExecutionStatus.PENDING,
        target_locale="fi",
        progress=None,
        status_message=None,
        steps=[],
    )

    mock_repo = MagicMock()
    mock_repo.get_workflow = AsyncMock(return_value=mock_workflow)
    mock_repo.get_execution = AsyncMock(return_value=mock_record)
    mock_repo.update_execution = AsyncMock()

    mock_engine = MagicMock()
    mock_engine.execute_workflow = AsyncMock(return_value=mock_record)

    mock_redis = AsyncMock()

    ctx = {
        "repository": mock_repo,
        "engine": mock_engine,
        "preflight_service": MagicMock(run=AsyncMock()),
        "redis": mock_redis,
    }

    result = await execute_workflow_job(
        ctx=ctx,
        workflow_id="wor_0123456789abcdef",
        inputs={},
        execution_id="exe_0123456789abcdef",
    )

    assert result["status"] == "COMPLETED"
    # Verify redis.enqueue_job was never called
    assert not hasattr(mock_redis, "enqueue_job") or not mock_redis.enqueue_job.called
