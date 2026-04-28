import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.services.progress import (
    DatabaseProgressTracker,
    InMemoryProgressTracker,
    ProgressService,
    ProgressState,
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_RUNNING,
    STATUS_STARTED,
)


@pytest.mark.asyncio
async def test_database_progress_tracker() -> None:
    mock_repo = AsyncMock(spec=AbstractWorkflowRepository)
    tracker = DatabaseProgressTracker(repository=mock_repo, execution_id="exe_123")

    # Test start
    await tracker.start(details={"foo": "bar"})
    mock_repo.update_execution.assert_called_once()
    call_args = mock_repo.update_execution.call_args[0]
    assert call_args[0] == "exe_123"
    assert call_args[1]["status"] == STATUS_STARTED
    assert call_args[1]["foo"] == "bar"

    # Test bypass attempt
    with pytest.raises(AppException) as exc_info:
        await tracker.start(details={"status": "bypass"})
    assert exc_info.value.details["error_code"] == ErrorCodes.PROGRESS_UPDATE_FAILED

    # Test update
    mock_repo.reset_mock()
    await tracker.update(stage="processing", percent=50, details={"extra": "data"})
    mock_repo.update_execution.assert_called_once()
    payload = mock_repo.update_execution.call_args[0][1]
    assert payload["status"] == STATUS_RUNNING
    assert payload["progress"] == 50
    assert payload["current_step"] == "processing"
    assert payload["extra"] == "data"

    # Test update bypass attempt
    with pytest.raises(AppException):
        await tracker.update(stage="x", percent=10, details={"progress": 99})

    # Test complete
    mock_repo.reset_mock()
    await tracker.complete(result={"output": "success"})
    payload = mock_repo.update_execution.call_args[0][1]
    assert payload["status"] == STATUS_COMPLETED
    assert payload["result"]["output"] == "success"

    # Test fail
    mock_repo.reset_mock()
    await tracker.fail(error="fatal error", details={"context": "test"})
    payload = mock_repo.update_execution.call_args[0][1]
    assert payload["status"] == STATUS_FAILED
    assert payload["error"] == "fatal error"
    assert payload["result"]["context"] == "test"


@pytest.mark.asyncio
async def test_in_memory_progress_tracker() -> None:
    emitted = []

    def callback(data: dict) -> None:
        emitted.append(data)

    tracker = InMemoryProgressTracker(callback=callback)

    # Test start
    await tracker.start(details={"meta": "info"})
    assert len(emitted) == 1
    assert emitted[-1]["status"] == STATUS_STARTED
    assert emitted[-1]["meta"] == "info"
    assert isinstance(tracker.current_state, ProgressState)

    # Test start bypass attempt
    with pytest.raises(ValueError):
        await tracker.start(details={"timestamp": "hacked"})

    # Test update
    await tracker.update(stage="working", percent=30, details={"chunk": 1})
    assert emitted[-1]["status"] == STATUS_RUNNING
    assert emitted[-1]["stage"] == "working"
    assert emitted[-1]["percent"] == 30

    # Test complete
    await tracker.complete(result={"doc": "pdf"})
    assert emitted[-1]["status"] == STATUS_COMPLETED
    assert emitted[-1]["percent"] == 100
    assert emitted[-1]["result"] == {"doc": "pdf"}

    # Test fail
    await tracker.fail(error="crash", details={"stack": "trace"})
    assert emitted[-1]["status"] == STATUS_FAILED
    assert emitted[-1]["error"] == "crash"
    assert emitted[-1]["stack"] == "trace"


@pytest.mark.asyncio
async def test_progress_service() -> None:
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
