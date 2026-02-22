"""Progress Tracking Service for async operations."""

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from typing import Any

from backend.database.repository import AbstractWorkflowRepository
from backend.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

# Standard Progress States
STATUS_STARTED = "started"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"


class ProgressTracker(ABC):
    """Abstract Base Class for unified progress reporting across the application.

    Enforces standardized states (STARTED, RUNNING, COMPLETED, FAILED).
    """

    @abstractmethod
    async def start(self, details: dict[str, Any] | None = None):
        """Signals the process has started.

        Args:
            details (Dict[str, Any], optional): Initial metadata.

        """
        pass

    @abstractmethod
    async def update(self, stage: str, percent: int, details: dict[str, Any] | None = None):
        """Updates progress with current stage and percentage.

        Args:
            stage (str): Description of current activity.
            percent (int): Completion percentage (0-100).
            details (Dict[str, Any], optional): Metadata updates.

        """
        pass

    @abstractmethod
    async def complete(self, result: dict[str, Any] | None = None):
        """Signals successful completion.

        Args:
            result (Dict[str, Any], optional): Final result data.

        """
        pass

    @abstractmethod
    async def fail(self, error: str, details: dict[str, Any] | None = None):
        """Signals failure/halt.

        Args:
            error (str): Error message.
            details (Dict[str, Any], optional): Error context.

        """
        pass


class DatabaseProgressTracker(ProgressTracker):
    """Tracks progress by updating the 'executions' table in the database.

    Used by WorkflowEngine to persist state across server restarts.
    """

    def __init__(self, repository: AbstractWorkflowRepository, execution_id: str):
        """Initializes the tracker for a specific execution.

        Args:
            repository (AbstractWorkflowRepository): Data access layer.
            execution_id (str): UUID of the execution.

        """
        self.repository = repository
        self.execution_id = execution_id

    async def start(self, details: dict[str, Any] | None = None):
        """Sets status to 'started'."""
        try:
            payload = {"status": STATUS_STARTED, "start_time": datetime.now()}
            if details:
                payload.update(details)
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            raise AppException(
                message=f"Failed to start progress tracking for {self.execution_id}",
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e

    async def update(self, stage: str, percent: int, details: dict[str, Any] | None = None):
        """Updates 'current_step' and 'progress' fields in DB."""
        try:
            payload = {
                "status": STATUS_RUNNING,
                "current_step": stage,
                "current_step_name": stage,
                "progress": percent,
                "last_updated": datetime.now(),
            }
            if details:
                payload.update(details)
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            logger.error(f"Progress Update Failed: {e}")
            # We might strictly Fail Fast here, or log and continue depending on criticality.
            # Mandate says Fail Fast.
            raise AppException(
                message=f"Failed to update progress for {self.execution_id}",
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e

    async def complete(self, result: dict[str, Any] | None = None):
        """Sets status to 'completed' and saves final result."""
        try:
            payload: dict[str, Any] = {"status": STATUS_COMPLETED, "end_time": datetime.now()}
            if result:
                payload["result"] = result
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            raise AppException(
                message=f"Failed to complete progress tracking for {self.execution_id}",
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e

    async def fail(self, error: str, details: dict[str, Any] | None = None):
        """Sets status to 'failed' and saves error message."""
        try:
            payload: dict[str, Any] = {"status": STATUS_FAILED, "error": error, "end_time": datetime.now()}
            if details:
                payload["result"] = details
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            # If we fail to report failure, log critically.
            logger.critical(f"Failed to report failure for {self.execution_id}: {e}")
            raise AppException(
                message=f"Failed to report failure for {self.execution_id}",
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e


class InMemoryProgressTracker(ProgressTracker):
    """Tracks progress in-memory via a callback function.

    Used by short-lived API tasks like File Ingestion.
    """

    def __init__(self, callback: Callable[[dict[str, Any]], None]):
        """Initializes the tracker.

        Args:
            callback (Callable[[Dict[str, Any]], None]): Function receiving status updates.

        """
        self.callback = callback
        self.current_state: dict[str, Any] = {}

    def _emit(self, status: str, payload: dict[str, Any]):
        """Internal helper to emit status.

        Args:
            status (str): Current status code.
            payload (dict): Data payload.
        """
        base = {"status": status, "timestamp": datetime.now().isoformat()}
        base.update(payload)
        self.current_state = base
        # Pass the simplified view expected by API consumers
        self.callback(base)

    async def start(self, details: dict[str, Any] | None = None):
        """Signals start."""
        self._emit(STATUS_STARTED, details or {})

    async def update(self, stage: str, percent: int, details: dict[str, Any] | None = None):
        """Signals update."""
        data = {"stage": stage, "percent": percent}
        if details:
            data.update(details)
        self._emit(STATUS_RUNNING, data)

    async def complete(self, result: dict[str, Any] | None = None):
        """Signals completion."""
        data: dict[str, Any] = {"percent": 100}
        if result:
            data["result"] = result
        self._emit(STATUS_COMPLETED, data)

    async def fail(self, error: str, details: dict[str, Any] | None = None):
        """Signals failure."""
        data = {"error": error}
        if details:
            data.update(details)
        self._emit(STATUS_FAILED, data)


class ProgressService:
    """Service for real-time progress reporting via Redis."""

    def __init__(self, redis_client: Any):
        """Initialize with a Redis client (ArqRedis or compatible)."""
        self.redis = redis_client

    async def emit_progress(self, execution_id: str, task_key: str, message: str, progress: float) -> None:
        """Emits a progress event to Redis.

        Args:
            execution_id: The ID of the execution.
            task_key: Identifier for the task (e.g., 'pdf_gen').
            message: Human-readable status message.
            progress: Float between 0.0 and 1.0.

        Raises:
            AppException: If Redis connection fails.
        """
        import json

        key = f"progress:{execution_id}:{task_key}"
        payload = {
            "execution_id": execution_id,
            "task_key": task_key,
            "message": message,
            "progress": progress,
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Set with 1-hour expiry
            await self.redis.set(key, json.dumps(payload), ex=3600)

            # Optionally publish for real-time websockets if needed
            # await self.redis.publish(f"progress_updates:{execution_id}", json.dumps(payload))
        except Exception as e:
            logger.error(f"Redis Progress Emit Failed: {e}")
            raise AppException(
                message="Failed to emit progress update.",
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e
