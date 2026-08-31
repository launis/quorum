"""Unit tests for progress tracking service and classes."""

import json
from unittest.mock import AsyncMock

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.progress import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_RUNNING,
    STATUS_STARTED,
    DatabaseProgressTracker,
    InMemoryProgressTracker,
    ProgressService,
    ProgressState,
)


def test_progress_state_extra_field_forbidden() -> None:
    """ISTQB Negative Test: Extra fields on ProgressState must trigger ValidationError."""
    with pytest.raises(ValidationError):
        ProgressState(status="running", timestamp="2026-08-31T00:00:00Z", extra_key=123)  # type: ignore[call-arg]


def test_progress_state_strict_types() -> None:
    """ISTQB Boundary Test: Invalid field types must trigger ValidationError in strict mode."""
    with pytest.raises(ValidationError):
        ProgressState(status=123, timestamp="2026-08-31T00:00:00Z")  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_database_progress_tracker() -> None:
    """Tests DatabaseProgressTracker lifecycle and repository updates."""
    mock_repo = AsyncMock()
    tracker = DatabaseProgressTracker(repository=mock_repo, execution_id="exe_123")

    # Test start
    await tracker.start()
    mock_repo.update_execution.assert_called_once()
    call_args = mock_repo.update_execution.call_args[0]
    assert call_args[0] == "exe_123"
    assert call_args[1]["status"] == STATUS_STARTED
    assert "created_at" in call_args[1]

    # Test update
    mock_repo.reset_mock()
    await tracker.update(current_step="processing", progress=50)
    mock_repo.update_execution.assert_called_once()
    payload = mock_repo.update_execution.call_args[0][1]
    assert payload["status"] == STATUS_RUNNING
    assert payload["progress"] == 50
    assert payload["current_step"] == "processing"
    assert payload["current_step_name"] == "processing"

    # Test complete
    mock_repo.reset_mock()
    await tracker.complete()
    mock_repo.update_execution.assert_called_once()
    payload = mock_repo.update_execution.call_args[0][1]
    assert payload["status"] == STATUS_COMPLETED
    assert "completed_at" in payload

    # Test fail
    mock_repo.reset_mock()
    await tracker.fail(error="fatal error")
    mock_repo.update_execution.assert_called_once()
    payload = mock_repo.update_execution.call_args[0][1]
    assert payload["status"] == STATUS_FAILED
    assert payload["error"] == "fatal error"
    assert "completed_at" in payload


@pytest.mark.asyncio
async def test_database_progress_tracker_exceptions() -> None:
    """Tests DatabaseProgressTracker error handling on repository failure."""
    mock_repo = AsyncMock()
    mock_repo.update_execution.side_effect = Exception("DB Connection Lost")
    tracker = DatabaseProgressTracker(repository=mock_repo, execution_id="exe_123")

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


@pytest.mark.asyncio
async def test_in_memory_progress_tracker() -> None:
    """Tests InMemoryProgressTracker typed state emission via callback."""
    emitted: list[ProgressState] = []

    def callback(data: ProgressState) -> None:
        emitted.append(data)

    tracker = InMemoryProgressTracker(callback=callback)

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
async def test_progress_service() -> None:
    """Tests ProgressService emitting events to Redis."""
    mock_redis = AsyncMock()
    service = ProgressService(redis_client=mock_redis)

    await service.emit_progress(
        execution_id="exe_456",
        task_key="task_a",
        message="Running",
        progress=0.75,
    )

    mock_redis.set.assert_called_once()
    call_args = mock_redis.set.call_args
    key = call_args[0][0]
    payload_str = call_args[0][1]
    kwargs = call_args[1]

    assert key == "progress:exe_456:task_a"
    assert kwargs["ex"] == 3600

    payload = json.loads(payload_str)
    assert payload["execution_id"] == "exe_456"
    assert payload["task_key"] == "task_a"
    assert payload["message"] == "Running"
    assert payload["progress"] == 0.75

    # Test Redis failure
    mock_redis.set.side_effect = Exception("Redis Down")
    with pytest.raises(AppException) as exc_info:
        await service.emit_progress("exe", "task", "msg", 1.0)

    assert exc_info.value.details["error_code"] == ErrorCodes.PROGRESS_UPDATE_FAILED
