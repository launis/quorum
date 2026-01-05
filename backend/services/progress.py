import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from typing import Any

from backend.database.repository import AbstractWorkflowRepository

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
    async def start(self, details: dict[str, Any] = None):
        """Signals the process has started.

        Args:
            details (Dict[str, Any], optional): Initial metadata.

        """
        pass

    @abstractmethod
    async def update(self, stage: str, percent: int, details: dict[str, Any] = None):
        """Updates progress with current stage and percentage.

        Args:
            stage (str): Description of current activity.
            percent (int): Completion percentage (0-100).
            details (Dict[str, Any], optional): Metadata updates.

        """
        pass

    @abstractmethod
    async def complete(self, result: dict[str, Any] = None):
        """Signals successful completion.

        Args:
            result (Dict[str, Any], optional): Final result data.

        """
        pass

    @abstractmethod
    async def fail(self, error: str, details: dict[str, Any] = None):
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

    async def start(self, details: dict[str, Any] = None):
        """Sets status to 'started'.
        """
        payload = {"status": STATUS_STARTED, "start_time": datetime.now().isoformat()}
        if details:
            payload.update(details)
        await self.repository.update_execution(self.execution_id, payload)

    async def update(self, stage: str, percent: int, details: dict[str, Any] = None):
        """Updates 'current_step' and 'progress' fields in DB.
        """
        # We map 'stage' to 'current_step' or just stick it in a visible field?
        # The UI likely looks at 'current_step' and 'logs'.
        # For compatibility, we set 'current_step' = stage.
        payload = {
            "status": STATUS_RUNNING,
            "current_step": stage,
            "progress": percent,
            "last_updated": datetime.now().isoformat(),
        }
        if details:
            payload.update(details)
        await self.repository.update_execution(self.execution_id, payload)

    async def complete(self, result: dict[str, Any] = None):
        """Sets status to 'completed' and saves final result.
        """
        payload = {"status": STATUS_COMPLETED, "end_time": datetime.now().isoformat()}
        if result:
            payload["result"] = result
        await self.repository.update_execution(self.execution_id, payload)

    async def fail(self, error: str, details: dict[str, Any] = None):
        """Sets status to 'failed' and saves error message.
        """
        payload = {"status": STATUS_FAILED, "error": error, "end_time": datetime.now().isoformat()}
        if details:
            payload["result"] = details  # Halt details often go to result
        await self.repository.update_execution(self.execution_id, payload)


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
        self.current_state = {}

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

    async def start(self, details: dict[str, Any] = None):
        """Signals start."""
        self._emit(STATUS_STARTED, details or {})

    async def update(self, stage: str, percent: int, details: dict[str, Any] = None):
        """Signals update."""
        data = {"stage": stage, "percent": percent}
        if details:
            data.update(details)
        self._emit(STATUS_RUNNING, data)

    async def complete(self, result: dict[str, Any] = None):
        """Signals completion."""
        data = {"percent": 100}
        if result:
            data["result"] = result
        self._emit(STATUS_COMPLETED, data)

    async def fail(self, error: str, details: dict[str, Any] = None):
        """Signals failure."""
        data = {"error": error}
        if details:
            data.update(details)
        self._emit(STATUS_FAILED, data)
