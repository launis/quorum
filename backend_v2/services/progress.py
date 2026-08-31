"""Progress Tracking Service for async operations."""

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.database.interfaces import IExecutionRepository
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.utils.redis_patcher import ArqCompatibleFakeRedis

logger = logging.getLogger(__name__)

# Standard Progress States
STATUS_STARTED = "started"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"


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


class ProgressTracker(ABC):
    """Abstract Base Class for unified progress reporting across the application.

    Enforces standardized states (STARTED, RUNNING, COMPLETED, FAILED).
    """

    @abstractmethod
    async def start(self) -> None:
        """Signals the process has started.

        Returns:
            None
        """
        ...

    @abstractmethod
    async def update(self, current_step: str, progress: int) -> None:
        """Updates progress with current step and progress percentage.

        Args:
            current_step: Description of current activity or step name.
            progress: Completion percentage (0-100).

        Returns:
            None
        """
        ...

    @abstractmethod
    async def complete(self) -> None:
        """Signals successful completion.

        Returns:
            None
        """
        ...

    @abstractmethod
    async def fail(self, error: str) -> None:
        """Signals failure/halt.

        Args:
            error: Error message.

        Returns:
            None
        """
        ...


class DatabaseProgressTracker(ProgressTracker):
    """Tracks progress by updating the 'executions' table in the database.

    Used by WorkflowEngine to persist state across server restarts.

    Attributes:
        repository: Data access layer interface.
        execution_id: UUID of the execution.
    """

    def __init__(self, repository: IExecutionRepository, execution_id: str) -> None:
        """Initializes the tracker for a specific execution.

        Args:
            repository: Data access layer.
            execution_id: UUID of the execution.
        """
        self.repository = repository
        self.execution_id = execution_id

    async def start(self) -> None:
        """Sets status to 'started'.

        Returns:
            None

        Raises:
            AppException: If updating the execution in the repository fails.
        """
        try:
            now_iso = datetime.now(timezone.utc).isoformat()
            payload = {
                "status": STATUS_STARTED,
                "created_at": now_iso,
                "updated_at": now_iso,
            }
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to start progress tracking for {self.execution_id}"
            logger.error("[ProgressTracker] %s: %s - %s", ErrorCodes.PROGRESS_UPDATE_FAILED.name, msg, e)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e

    async def update(self, current_step: str, progress: int) -> None:
        """Updates 'current_step' and 'progress' fields in DB.

        Args:
            current_step: Description of current activity or step name.
            progress: Completion percentage (0-100).

        Returns:
            None

        Raises:
            AppException: If updating the execution in the repository fails.
        """
        try:
            payload = {
                "status": STATUS_RUNNING,
                "current_step": current_step,
                "current_step_name": current_step,
                "progress": progress,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to update progress for {self.execution_id}"
            logger.error("[ProgressTracker] %s: %s - %s", ErrorCodes.PROGRESS_UPDATE_FAILED.name, msg, e)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e

    async def complete(self) -> None:
        """Sets status to 'completed'.

        Returns:
            None

        Raises:
            AppException: If updating the execution in the repository fails.
        """
        try:
            now_iso = datetime.now(timezone.utc).isoformat()
            payload = {
                "status": STATUS_COMPLETED,
                "completed_at": now_iso,
                "updated_at": now_iso,
            }
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to complete progress tracking for {self.execution_id}"
            logger.error("[ProgressTracker] %s: %s - %s", ErrorCodes.PROGRESS_UPDATE_FAILED.name, msg, e)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e

    async def fail(self, error: str) -> None:
        """Sets status to 'failed' and saves error message.

        Args:
            error: Error message.

        Returns:
            None

        Raises:
            AppException: If updating the execution in the repository fails.
        """
        try:
            now_iso = datetime.now(timezone.utc).isoformat()
            payload = {
                "status": STATUS_FAILED,
                "error": error,
                "completed_at": now_iso,
                "updated_at": now_iso,
            }
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to report failure for {self.execution_id}"
            logger.critical("[ProgressTracker] %s: %s - %s", ErrorCodes.PROGRESS_UPDATE_FAILED.name, msg, e)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e


class InMemoryProgressTracker(ProgressTracker):
    """Tracks progress in-memory via a callback function emitting ProgressState.

    Used by short-lived API tasks like File Ingestion.

    Attributes:
        callback: Function receiving ProgressState updates.
        current_state: Current active ProgressState.
    """

    def __init__(self, callback: Callable[[ProgressState], None]) -> None:
        """Initializes the tracker with a ProgressState callback.

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
        """Internal helper to emit structured ProgressState.

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
            timestamp=datetime.now(timezone.utc).isoformat(),
            current_step=current_step,
            progress=progress,
            error=error,
        )
        self.current_state = state
        self.callback(state)

    async def start(self) -> None:
        """Signals start.

        Returns:
            None
        """
        self._emit(status=STATUS_STARTED)

    async def update(self, current_step: str, progress: int) -> None:
        """Signals update.

        Args:
            current_step: Description of current activity or step name.
            progress: Completion percentage (0-100).

        Returns:
            None
        """
        self._emit(status=STATUS_RUNNING, current_step=current_step, progress=progress)

    async def complete(self) -> None:
        """Signals completion.

        Returns:
            None
        """
        self._emit(status=STATUS_COMPLETED, progress=100)

    async def fail(self, error: str) -> None:
        """Signals failure.

        Args:
            error: Error message.

        Returns:
            None
        """
        self._emit(status=STATUS_FAILED, error=error)


class ProgressService:
    """Service for real-time progress reporting via Redis."""

    def __init__(self, redis_client: ArqCompatibleFakeRedis) -> None:
        """Initialize with a Redis client (ArqRedis, ArqCompatibleFakeRedis, or compatible).

        Args:
            redis_client: Redis client instance.
        """
        self.redis = redis_client

    async def emit_progress(self, execution_id: str, task_key: str, message: str, progress: float) -> None:
        """Emits a progress event to Redis.

        Args:
            execution_id: The ID of the execution.
            task_key: Identifier for the task (e.g., 'pdf_gen').
            message: Human-readable status message.
            progress: Float between 0.0 and 1.0.

        Returns:
            None

        Raises:
            AppException: If Redis connection fails.
        """
        key = f"progress:{execution_id}:{task_key}"
        payload = {
            "execution_id": execution_id,
            "task_key": task_key,
            "message": message,
            "progress": progress,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        try:
            # Set with 1-hour expiry
            await self.redis.set(key, json.dumps(payload), ex=3600)

            # Optionally publish for real-time websockets if needed
            # await self.redis.publish(f"progress_updates:{execution_id}", json.dumps(payload))
        except Exception as e:
            msg = "Failed to emit progress update."
            logger.error("[ProgressService] %s: %s - %s", ErrorCodes.PROGRESS_UPDATE_FAILED.name, msg, e)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e
