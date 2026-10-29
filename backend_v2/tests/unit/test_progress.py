"""Unit tests for progress tracking service and classes."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from fakeredis import FakeServer
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.enums import EntityPrefix, ExecutionStatus
from backend_v2.services.progress import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_RUNNING,
    STATUS_STARTED,
    DatabaseProgressTracker,
    InMemoryProgressTracker,
    ProgressService,
    ProgressState,
    ProgressTrackerProtocol,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.utils.redis_patcher import ArqCompatibleFakeRedis


def test_progress_state_extra_field_forbidden() -> None:
    """ISTQB Negative Test: Extra fields on ProgressState must trigger ValidationError."""
    with pytest.raises(ValidationError):
        ProgressState(status="running", timestamp="2026-08-31T00:00:00Z", extra_key=123)


def test_progress_state_strict_types() -> None:
    """ISTQB Boundary Test: Invalid field types must trigger ValidationError in strict mode."""
    with pytest.raises(ValidationError):
        ProgressState(status=123, timestamp="2026-08-31T00:00:00Z")


@pytest.mark.asyncio
async def test_database_progress_tracker() -> None:
    """Tests DatabaseProgressTracker lifecycle and stateful repository roundtrip updates."""
    fake_repo = InMemoryUnifiedWorkflowRepository()
    exec_id = generate_opaque_id(EntityPrefix.EXECUTION)
    wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    mock_record = ExecutionRecord(
        id=exec_id,
        workflow_id=wf_id,
        status=ExecutionStatus.PENDING,
        target_locale="fi",
    )
    await fake_repo.save_execution(mock_record)
    tracker = DatabaseProgressTracker(repository=fake_repo, execution_id=exec_id)
    assert isinstance(tracker, ProgressTrackerProtocol)

    # Test start
    await tracker.start()
    record = await fake_repo.get_execution(exec_id)
    assert record is not None
    assert record.status == STATUS_STARTED
    assert record.created_at is not None

    # Test update
    await tracker.update(current_step="processing", progress=50)
    record = await fake_repo.get_execution(exec_id)
    assert record is not None
    assert record.status == STATUS_RUNNING
    assert record.progress == 50
    assert record.status_message == "processing"

    # Test complete
    await tracker.complete()
    record = await fake_repo.get_execution(exec_id)
    assert record is not None
    assert record.status == STATUS_COMPLETED
    assert record.completed_at is not None

    # Test fail
    await tracker.fail(error="fatal error")
    record = await fake_repo.get_execution(exec_id)
    assert record is not None
    assert record.status == STATUS_FAILED
    assert record.error == "fatal error"
    assert record.completed_at is not None


def test_database_progress_tracker_invalid_execution_id() -> None:
    """ISTQB Negative Boundary Test: Empty or whitespace execution_id raises AppException."""
    fake_repo = InMemoryUnifiedWorkflowRepository()
    for invalid_id in ("", "   "):
        with pytest.raises(AppException) as exc_info:
            DatabaseProgressTracker(repository=fake_repo, execution_id=invalid_id)
        assert exc_info.value.status_code == 400
        assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


@pytest.mark.asyncio
async def test_database_progress_tracker_exceptions() -> None:
    """Tests DatabaseProgressTracker error handling on repository failure with deterministic fault cleanup."""
    fake_repo = InMemoryUnifiedWorkflowRepository()
    exec_id = generate_opaque_id(EntityPrefix.EXECUTION)
    tracker = DatabaseProgressTracker(repository=fake_repo, execution_id=exec_id)

    fake_repo.inject_fault("update_execution", Exception("DB Connection Lost"), trigger_count=4)
    try:
        with pytest.raises(AppException) as exc_start:
            await tracker.start()
        assert exc_start.value.details["error_code"] == ErrorCodes.PROGRESS_UPDATE_FAILED

        with pytest.raises(AppException) as exc_update:
            await tracker.update(current_step="step1", progress=10)
        assert exc_update.value.details["error_code"] == ErrorCodes.PROGRESS_UPDATE_FAILED

        with pytest.raises(AppException) as exc_complete:
            await tracker.complete()
        assert exc_complete.value.details["error_code"] == ErrorCodes.PROGRESS_UPDATE_FAILED

        with pytest.raises(AppException) as exc_fail:
            await tracker.fail(error="boom")
        assert exc_fail.value.details["error_code"] == ErrorCodes.PROGRESS_UPDATE_FAILED
    finally:
        fake_repo.clear_faults()


@pytest.mark.asyncio
async def test_in_memory_progress_tracker() -> None:
    """Tests InMemoryProgressTracker typed state emission via callback."""
    emitted: list[ProgressState] = []

    def callback(data: ProgressState) -> None:
        emitted.append(data)

    tracker = InMemoryProgressTracker(callback=callback)
    assert isinstance(tracker, ProgressTrackerProtocol)

    # Test start
    await tracker.start()
    assert len(emitted) == 1
    assert emitted[-1].status == STATUS_STARTED
    assert isinstance(tracker.current_state, ProgressState)

    # Test update
    await tracker.update(current_step="working", progress=30)
    assert len(emitted) == 2
    assert emitted[-1].status == STATUS_RUNNING
    assert emitted[-1].current_step == "working"
    assert emitted[-1].progress == 30

    # Test complete
    await tracker.complete()
    assert len(emitted) == 3
    assert emitted[-1].status == STATUS_COMPLETED
    assert emitted[-1].progress == 100

    # Test fail
    await tracker.fail(error="crash")
    assert len(emitted) == 4
    assert emitted[-1].status == STATUS_FAILED
    assert emitted[-1].error == "crash"


@pytest.mark.asyncio
async def test_in_memory_progress_tracker_boundary_validation() -> None:
    """ISTQB Boundary Value Analysis: Out-of-bounds progress or empty step raises AppException."""
    tracker = InMemoryProgressTracker(callback=lambda _: None)

    for invalid_progress in (-1, 101):
        with pytest.raises(AppException) as exc_info:
            await tracker.update(current_step="valid_step", progress=invalid_progress)
        assert exc_info.value.status_code == 400
        assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    for invalid_step in ("", "   "):
        with pytest.raises(AppException) as exc_step:
            await tracker.update(current_step=invalid_step, progress=50)
        assert exc_step.value.status_code == 400
        assert exc_step.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


@pytest.mark.asyncio
async def test_progress_service() -> None:
    """Tests ProgressService emitting events to FakeRedis and handling failures."""
    fake_redis = ArqCompatibleFakeRedis(server=FakeServer())
    service = ProgressService(redis_client=fake_redis)
    exec_id = generate_opaque_id(EntityPrefix.EXECUTION)

    await service.emit_progress(
        execution_id=exec_id,
        task_key="task_a",
        message="Running",
        progress=0.75,
    )

    key = f"progress:{exec_id}:task_a"
    raw_stored = await fake_redis.get(key)
    assert raw_stored is not None
    ttl = await fake_redis.ttl(key)
    assert 0 < ttl <= 3600

    payload = json.loads(raw_stored)
    assert payload["execution_id"] == exec_id
    assert payload["task_key"] == "task_a"
    assert payload["message"] == "Running"
    assert payload["progress"] == 0.75

    # Test Redis failure
    failing_redis = AsyncMock(spec=ArqCompatibleFakeRedis)
    failing_redis.set.side_effect = RuntimeError("Redis Down")
    failing_service = ProgressService(redis_client=failing_redis)
    with pytest.raises(AppException) as exc_info:
        await failing_service.emit_progress(exec_id, "task_a", "msg", 1.0)

    assert exc_info.value.details["error_code"] == ErrorCodes.PROGRESS_UPDATE_FAILED


@pytest.mark.asyncio
async def test_progress_service_boundary_validation() -> None:
    """ISTQB Boundary Value Analysis: Invalid execution_id, task_key, or progress raises AppException."""
    fake_redis = ArqCompatibleFakeRedis(server=FakeServer())
    service = ProgressService(redis_client=fake_redis)
    exec_id = generate_opaque_id(EntityPrefix.EXECUTION)

    with pytest.raises(AppException) as exc_id_err:
        await service.emit_progress(execution_id="   ", task_key="task_a", message="Running", progress=0.5)
    assert exc_id_err.value.status_code == 400
    assert exc_id_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    with pytest.raises(AppException) as exc_task_err:
        await service.emit_progress(execution_id=exec_id, task_key="", message="Running", progress=0.5)
    assert exc_task_err.value.status_code == 400
    assert exc_task_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    for invalid_progress in (-0.01, 1.01):
        with pytest.raises(AppException) as exc_prog_err:
            await service.emit_progress(
                execution_id=exec_id, task_key="task_a", message="Running", progress=invalid_progress
            )
        assert exc_prog_err.value.status_code == 400
        assert exc_prog_err.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED
