"""Progress Tracking Service for async operations."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Annotated, Protocol, override, runtime_checkable

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.database.interfaces import IExecutionRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.trace import ExecutionUpdateDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.settings import get_settings
from backend_v2.utils.redis_patcher import ArqCompatibleFakeRedis

logger = logging.getLogger(__name__)

# Standard Progress States
STATUS_STARTED = ExecutionStatus.RUNNING
STATUS_RUNNING = ExecutionStatus.RUNNING
STATUS_COMPLETED = ExecutionStatus.PASSED
STATUS_FAILED = ExecutionStatus.FAILED

__all__ = [
    "DatabaseProgressTracker",
    "InMemoryProgressTracker",
    "ProgressService",
    "ProgressState",
    "ProgressTrackerProtocol",
    "STATUS_COMPLETED",
    "STATUS_FAILED",
    "STATUS_RUNNING",
    "STATUS_STARTED",
]


class ProgressState(BaseModel):
    """Pydantic model representing in-memory progress state.

    Attributes:
        status: Progress state status ('started', 'running', 'completed', 'failed').
        timestamp: ISO-8601 UTC timestamp string.
        current_step: Current active step or task name.
        progress: Completion progress percentage (0-100).
        error: Error message string if failed.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    status: Annotated[str, Field(description="Progress state status")]
    timestamp: Annotated[str, Field(description="ISO-8601 UTC timestamp string")]
    current_step: Annotated[str | None, Field(default=None, description="Current active step or task name")] = None
    progress: Annotated[int | None, Field(default=None, description="Completion progress percentage (0-100)")] = None
    error: Annotated[str | None, Field(default=None, description="Error message string if failed")] = None


@runtime_checkable
class ProgressTrackerProtocol(Protocol):
    """Protocol defining structural interface contract for unified progress reporting.

    Enforces standardized states (STARTED, RUNNING, COMPLETED, FAILED).
    """

    async def start(self) -> None:
        """Signal that the process has started.

        Returns:
            None

        Raises:
            AppException: With ErrorCodes.PROGRESS_UPDATE_FAILED if starting progress tracking fails.
        """
        ...

    async def update(self, current_step: str, progress: int) -> None:
        """Update progress with current step and progress percentage.

        Args:
            current_step: Description of current activity or step name.
            progress: Completion percentage (0-100).

        Returns:
            None

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED or ErrorCodes.PROGRESS_UPDATE_FAILED
                if updating progress fails.
        """
        ...

    async def complete(self) -> None:
        """Signal successful completion.

        Returns:
            None

        Raises:
            AppException: With ErrorCodes.PROGRESS_UPDATE_FAILED if completing progress tracking fails.
        """
        ...

    async def fail(self, error: str) -> None:
        """Signal failure or halt.

        Args:
            error: Error message describing the failure.

        Returns:
            None

        Raises:
            AppException: With ErrorCodes.PROGRESS_UPDATE_FAILED if recording failure state fails.
        """
        ...


class DatabaseProgressTracker(ProgressTrackerProtocol):
    """Tracks progress by updating the 'executions' table in the database.

    Used by WorkflowEngine to persist state across server restarts.

    Attributes:
        repository: Data access layer interface.
        execution_id: Opaque identifier of the execution.
    """

    def __init__(self, repository: IExecutionRepository, execution_id: str) -> None:
        """Initialize the tracker for a specific execution.

        Args:
            repository: Data access layer.
            execution_id: Opaque identifier of the execution.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if execution_id is empty or whitespace.
        """
        if not execution_id or not execution_id.strip():
            msg = "DatabaseProgressTracker requires a non-empty execution_id."
            logger.error(
                "[ProgressTracker] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
            )
        self.repository = repository
        self.execution_id = execution_id

    @override
    async def start(self) -> None:
        """Set execution status to 'started' in the database.

        Returns:
            None

        Raises:
            AppException: With ErrorCodes.PROGRESS_UPDATE_FAILED if updating the execution in the repository fails.
        """
        try:
            now_dt = datetime.now(UTC)
            payload = ExecutionUpdateDTO(
                status=STATUS_STARTED,
                created_at=now_dt,
                updated_at=now_dt,
            )
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to start progress tracking for {self.execution_id}"
            logger.error(
                "[ProgressTracker] %s: %s - %s",
                ErrorCodes.PROGRESS_UPDATE_FAILED.name,
                msg,
                e,
                extra={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e

    @override
    async def update(self, current_step: str, progress: int) -> None:
        """Update 'current_step' and 'progress' fields in the database.

        Args:
            current_step: Description of current activity or step name.
            progress: Completion percentage (0-100).

        Returns:
            None

        Raises:
            AppException: With ErrorCodes.PROGRESS_UPDATE_FAILED if updating the execution in the repository fails.
        """
        try:
            payload = ExecutionUpdateDTO(
                status=STATUS_RUNNING,
                current_step=current_step,
                current_step_name=current_step,
                progress=progress,
                updated_at=datetime.now(UTC),
            )
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to update progress for {self.execution_id}"
            logger.error(
                "[ProgressTracker] %s: %s - %s",
                ErrorCodes.PROGRESS_UPDATE_FAILED.name,
                msg,
                e,
                extra={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e

    @override
    async def complete(self) -> None:
        """Set execution status to 'completed' in the database.

        Returns:
            None

        Raises:
            AppException: With ErrorCodes.PROGRESS_UPDATE_FAILED if updating the execution in the repository fails.
        """
        try:
            now_dt = datetime.now(UTC)
            payload = ExecutionUpdateDTO(
                status=STATUS_COMPLETED,
                completed_at=now_dt,
                updated_at=now_dt,
            )
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to complete progress tracking for {self.execution_id}"
            logger.error(
                "[ProgressTracker] %s: %s - %s",
                ErrorCodes.PROGRESS_UPDATE_FAILED.name,
                msg,
                e,
                extra={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e

    @override
    async def fail(self, error: str) -> None:
        """Set execution status to 'failed' and persist error message in the database.

        Args:
            error: Error message describing the failure.

        Returns:
            None

        Raises:
            AppException: With ErrorCodes.PROGRESS_UPDATE_FAILED if updating the execution in the repository fails.
        """
        try:
            now_dt = datetime.now(UTC)
            payload = ExecutionUpdateDTO(
                status=STATUS_FAILED,
                error=error,
                completed_at=now_dt,
                updated_at=now_dt,
            )
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to report failure for {self.execution_id}"
            logger.error(
                "[ProgressTracker] %s: %s - %s",
                ErrorCodes.PROGRESS_UPDATE_FAILED.name,
                msg,
                e,
                extra={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e


class InMemoryProgressTracker(ProgressTrackerProtocol):
    """Tracks progress in-memory via a callback function emitting ProgressState.

    Used by short-lived API tasks such as file ingestion.

    Attributes:
        callback: Function receiving ProgressState updates.
        current_state: Current active ProgressState.
    """

    def __init__(self, callback: Callable[[ProgressState], None]) -> None:
        """Initialize the tracker with a ProgressState callback.

        Args:
            callback: Function receiving ProgressState updates.
        """
        self.callback = callback
        self.current_state: ProgressState | None = None

    def _emit(
        self,
        status: str,
        current_step: str | None = None,
        progress: int | None = None,
        error: str | None = None,
    ) -> None:
        """Emit structured ProgressState to the registered callback.

        Args:
            status: Status string.
            current_step: Optional active step name.
            progress: Optional progress percentage (0-100).
            error: Optional error message.

        Returns:
            None
        """
        state = ProgressState(
            status=status,
            timestamp=datetime.now(UTC).isoformat(),
            current_step=current_step,
            progress=progress,
            error=error,
        )
        self.current_state = state
        self.callback(state)

    @override
    async def start(self) -> None:
        """Signal start of in-memory progress tracking.

        Returns:
            None
        """
        self._emit(status=STATUS_STARTED)

    @override
    async def update(self, current_step: str, progress: int) -> None:
        """Signal progress update after validating step name and percentage bounds.

        Args:
            current_step: Description of current activity or step name.
            progress: Completion percentage (0-100).

        Returns:
            None

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if current_step is empty
                or progress is outside [0, 100].
        """
        if not current_step or not current_step.strip():
            msg = "InMemoryProgressTracker.update requires a non-empty current_step."
            logger.error(
                "[InMemoryProgressTracker] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
            )
        if not 0 <= progress <= 100:
            msg = f"Invalid progress={progress} in InMemoryProgressTracker.update; must be within [0, 100]."
            logger.error(
                "[InMemoryProgressTracker] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
            )
        self._emit(status=STATUS_RUNNING, current_step=current_step, progress=progress)

    @override
    async def complete(self) -> None:
        """Signal completion of in-memory progress tracking.

        Returns:
            None
        """
        self._emit(status=STATUS_COMPLETED, progress=100)

    @override
    async def fail(self, error: str) -> None:
        """Signal failure of in-memory progress tracking.

        Args:
            error: Error message describing the failure.

        Returns:
            None
        """
        self._emit(status=STATUS_FAILED, error=error)


class ProgressService:
    """Service for real-time progress reporting via Redis.

    Attributes:
        redis: Asynchronous Redis client instance.
    """

    def __init__(self, redis_client: ArqCompatibleFakeRedis) -> None:
        """Initialize with a Redis client (ArqRedis, ArqCompatibleFakeRedis, or compatible).

        Args:
            redis_client: Redis client instance.
        """
        self.redis = redis_client

    async def emit_progress(self, execution_id: str, task_key: str, message: str, progress: float) -> None:
        """Emit a progress event to Redis with TTL governed by Settings SSOT.

        Args:
            execution_id: Opaque identifier of the execution.
            task_key: Identifier for the task.
            message: Human-readable status message.
            progress: Completion ratio between 0.0 and 1.0.

        Returns:
            None

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if execution_id, task_key, or progress
                is invalid, or ErrorCodes.PROGRESS_UPDATE_FAILED if Redis persistence fails.
        """
        if not execution_id or not execution_id.strip():
            msg = "ProgressService.emit_progress requires a non-empty execution_id."
            logger.error(
                "[ProgressService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
            )
        if not task_key or not task_key.strip():
            msg = "ProgressService.emit_progress requires a non-empty task_key."
            logger.error(
                "[ProgressService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
            )
        if not 0.0 <= progress <= 1.0:
            msg = f"Invalid progress={progress} in ProgressService.emit_progress; must be within [0.0, 1.0]."
            logger.error(
                "[ProgressService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED},
            )

        settings = get_settings()
        key = f"progress:{execution_id}:{task_key}"
        payload = {
            "execution_id": execution_id,
            "task_key": task_key,
            "message": message,
            "progress": progress,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        try:
            await self.redis.set(key, json.dumps(payload), ex=settings.context_cache_passive_ttl_seconds)
        except Exception as e:
            msg = "Failed to emit progress update."
            logger.error(
                "[ProgressService] %s: %s - %s",
                ErrorCodes.PROGRESS_UPDATE_FAILED.name,
                msg,
                e,
                extra={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED.value},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e
