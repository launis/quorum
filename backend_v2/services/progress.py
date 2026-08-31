"""Progress Tracking Service for async operations."""

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict

from backend_v2.database.interfaces import IExecutionRepository
from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

# Standard Progress States
STATUS_STARTED = "started"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"


class ProgressState(BaseModel):
    """Pydantic model representing in-memory progress state."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    status: str
    timestamp: str
    stage: str | None = None
    percent: int | None = None
    error: str | None = None
    result: dict[str, Any] | None = None
    details: dict[str, Any] | None = None


class ProgressTracker(ABC):
    """Abstract Base Class for unified progress reporting across the application.

    Enforces standardized states (STARTED, RUNNING, COMPLETED, FAILED).
    """

    @abstractmethod
    async def start(self, details: dict[str, Any] | None = None) -> None:
        """Signals the process has started.

        Args:
            details (Dict[str, Any], optional): Initial metadata.

        """
        ...

    @abstractmethod
    async def update(self, stage: str, percent: int, details: dict[str, Any] | None = None) -> None:
        """Updates progress with current stage and percentage.

        Args:
            stage (str): Description of current activity.
            percent (int): Completion percentage (0-100).
            details (Dict[str, Any], optional): Metadata updates.

        """
        ...

    @abstractmethod
    async def complete(self, result: dict[str, Any] | None = None) -> None:
        """Signals successful completion.

        Args:
            result (Dict[str, Any], optional): Final result data.

        """
        ...

    @abstractmethod
    async def fail(self, error: str, details: dict[str, Any] | None = None) -> None:
        """Signals failure/halt.

        Args:
            error (str): Error message.
            details (Dict[str, Any], optional): Error context.

        """
        ...


class DatabaseProgressTracker(ProgressTracker):
    """Tracks progress by updating the 'executions' table in the database.

    Used by WorkflowEngine to persist state across server restarts.
    """

    def __init__(self, repository: IExecutionRepository, execution_id: str):
        """Initializes the tracker for a specific execution.

        Args:
            repository (IExecutionRepository): Data access layer.
            execution_id (str): UUID of the execution.

        """
        self.repository = repository
        self.execution_id = execution_id

    async def start(self, details: dict[str, Any] | None = None) -> None:
        """Sets status to 'started'.

        Args:
            details (dict[str, Any] | None, optional): Initial metadata.

        Returns:
            None

        Raises:
            AppException: If updating the execution in the repository fails.
        """
        try:
            payload = {"status": STATUS_STARTED, "start_time": datetime.now(timezone.utc).isoformat()}
            if details:
                # Fail-Fast: Prevent un-audited state mutation bypasses
                for k in payload:
                    if k in details:
                        raise ValueError(f"Progress property bypass attempt: '{k}'")
                payload.update(details)
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to start progress tracking for {self.execution_id}"
            logger.error("[ProgressTracker] %s: %s - %s", ErrorCodes.PROGRESS_UPDATE_FAILED.name, msg, e)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e

    async def update(self, stage: str, percent: int, details: dict[str, Any] | None = None) -> None:
        """Updates 'current_step' and 'progress' fields in DB.

        Args:
            stage (str): Description of current activity.
            percent (int): Completion percentage (0-100).
            details (dict[str, Any] | None, optional): Metadata updates.

        Returns:
            None

        Raises:
            AppException: If updating the execution in the repository fails.
        """
        try:
            payload = {
                "status": STATUS_RUNNING,
                "current_step": stage,
                "current_step_name": stage,
                "progress": percent,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            if details:
                for k in payload:
                    if k in details:
                        raise ValueError(f"Progress property bypass attempt for managed key: '{k}'")
                payload.update(details)
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to update progress for {self.execution_id}"
            logger.error("[ProgressTracker] %s: %s - %s", ErrorCodes.PROGRESS_UPDATE_FAILED.name, msg, e)
            # We strictly Fail Fast here based on the mandate.
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e

    async def complete(self, result: dict[str, Any] | None = None) -> None:
        """Sets status to 'completed' and saves final result.

        Args:
            result (dict[str, Any] | None, optional): Final result data.

        Returns:
            None

        Raises:
            AppException: If updating the execution in the repository fails.
        """
        try:
            payload: dict[str, Any] = {"status": STATUS_COMPLETED, "end_time": datetime.now(timezone.utc).isoformat()}
            if result:
                payload["result"] = result
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to complete progress tracking for {self.execution_id}"
            logger.error("[ProgressTracker] %s: %s - %s", ErrorCodes.PROGRESS_UPDATE_FAILED.name, msg, e)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.PROGRESS_UPDATE_FAILED, "original_error": str(e)},
            ) from e

    async def fail(self, error: str, details: dict[str, Any] | None = None) -> None:
        """Sets status to 'failed' and saves error message.

        Args:
            error (str): Error message.
            details (dict[str, Any] | None, optional): Error context.

        Returns:
            None

        Raises:
            AppException: If updating the execution in the repository fails.
        """
        try:
            payload: dict[str, Any] = {
                "status": STATUS_FAILED,
                "error": error,
                "end_time": datetime.now(timezone.utc).isoformat(),
            }
            if details:
                payload["result"] = details
            await self.repository.update_execution(self.execution_id, payload)
        except Exception as e:
            msg = f"Failed to report failure for {self.execution_id}"
            # If we fail to report failure, log critically with standard format.
            logger.critical("[ProgressTracker] %s: %s - %s", ErrorCodes.PROGRESS_UPDATE_FAILED.name, msg, e)
            raise AppException(
                message=msg,
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
        self.current_state: ProgressState | None = None

    def _emit(self, status: str, payload: dict[str, Any]) -> None:
        """Internal helper to emit status.

        Args:
            status (str): Current status code.
            payload (dict[str, Any]): Data payload.

        Returns:
            None
        """
        base: dict[str, Any] = {"status": status, "timestamp": datetime.now(timezone.utc).isoformat()}
        for k in base:
            if k in payload:
                raise ValueError(f"InMemory Tracker property bypass attempt: '{k}'")

        known_fields = {"stage", "percent", "error", "result", "details"}
        extra_details: dict[str, Any] = {}
        for k, v in payload.items():
            if k in known_fields:
                base[k] = v
            else:
                extra_details[k] = v

        if extra_details:
            base["details"] = extra_details

        self.current_state = ProgressState.model_validate(base)
        # Pass the simplified view expected by API consumers
        dumped = self.current_state.model_dump(exclude_none=True)
        match dumped.pop("details", None):
            case dict() as details_dict:
                dumped.update(details_dict)
            case _:
                pass
        self.callback(dumped)

    async def start(self, details: dict[str, Any] | None = None) -> None:
        """Signals start.

        Args:
            details (dict[str, Any] | None, optional): Initial metadata.

        Returns:
            None
        """
        self._emit(STATUS_STARTED, details or {})

    async def update(self, stage: str, percent: int, details: dict[str, Any] | None = None) -> None:
        """Signals update.

        Args:
            stage (str): Description of current activity.
            percent (int): Completion percentage (0-100).
            details (dict[str, Any] | None, optional): Metadata updates.

        Returns:
            None
        """
        data = {"stage": stage, "percent": percent}
        if details:
            for k in data:
                if k in details:
                    raise ValueError(f"InMemory Tracker property bypass attempt: '{k}'")
            data.update(details)
        self._emit(STATUS_RUNNING, data)

    async def complete(self, result: dict[str, Any] | None = None) -> None:
        """Signals completion.

        Args:
            result (dict[str, Any] | None, optional): Final result data.

        Returns:
            None
        """
        data: dict[str, Any] = {"percent": 100}
        if result:
            data["result"] = result
        self._emit(STATUS_COMPLETED, data)

    async def fail(self, error: str, details: dict[str, Any] | None = None) -> None:
        """Signals failure.

        Args:
            error (str): Error message.
            details (dict[str, Any] | None, optional): Error context.

        Returns:
            None
        """
        data = {"error": error}
        if details:
            for k in data:
                if k in details:
                    raise ValueError(f"InMemory Tracker property bypass attempt: '{k}'")
            data.update(details)
        self._emit(STATUS_FAILED, data)


class ProgressService:
    """Service for real-time progress reporting via Redis."""

    def __init__(self, redis_client: Any):
        """Initialize with a Redis client (ArqRedis or compatible).

        Args:
            redis_client (Any): Redis client instance.
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
