from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from datetime import datetime
import logging
from backend.database.repository import AbstractWorkflowRepository

logger = logging.getLogger(__name__)

# Standard Progress States
STATUS_STARTED = "started"
STATUS_RUNNING = "running"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

class ProgressTracker(ABC):
    """
    Abstract Base Class for unified progress reporting across the application.
    Enforces standardized states (STARTED, RUNNING, COMPLETED, FAILED).
    """
    
    @abstractmethod
    def start(self, details: Dict[str, Any] = None):
        """
        Signals the process has started.
        
        Args:
            details (Dict[str, Any], optional): Initial metadata.
        """
        pass

    @abstractmethod
    def update(self, stage: str, percent: int, details: Dict[str, Any] = None):
        """
        Updates progress with current stage and percentage.
        
        Args:
            stage (str): Description of current activity.
            percent (int): Completion percentage (0-100).
            details (Dict[str, Any], optional): Metadata updates.
        """
        pass

    @abstractmethod
    def complete(self, result: Dict[str, Any] = None):
        """
        Signals successful completion.
        
        Args:
            result (Dict[str, Any], optional): Final result data.
        """
        pass

    @abstractmethod
    def fail(self, error: str, details: Dict[str, Any] = None):
        """
        Signals failure/halt.
        
        Args:
            error (str): Error message.
            details (Dict[str, Any], optional): Error context.
        """
        pass


class DatabaseProgressTracker(ProgressTracker):
    """
    Tracks progress by updating the 'executions' table in the database.
    Used by WorkflowEngine to persist state across server restarts.
    """
    def __init__(self, repository: AbstractWorkflowRepository, execution_id: str):
        """
        Initializes the tracker for a specific execution.

        Args:
            repository (AbstractWorkflowRepository): Data access layer.
            execution_id (str): UUID of the execution.
        """
        self.repository = repository
        self.execution_id = execution_id

    def start(self, details: Dict[str, Any] = None):
        """
        Sets status to 'started'.
        """
        payload = {'status': STATUS_STARTED, 'start_time': datetime.now().isoformat()}
        if details: payload.update(details)
        self.repository.update_execution(self.execution_id, payload)

    def update(self, stage: str, percent: int, details: Dict[str, Any] = None):
        """
        Updates 'current_step' and 'progress' fields in DB.
        """
        # We map 'stage' to 'current_step' or just stick it in a visible field?
        # The UI likely looks at 'current_step' and 'logs'.
        # For compatibility, we set 'current_step' = stage.
        payload = {
            'status': STATUS_RUNNING, 
            'current_step': stage, 
            'progress': percent,
            'last_updated': datetime.now().isoformat()
        }
        if details: payload.update(details)
        self.repository.update_execution(self.execution_id, payload)

    def complete(self, result: Dict[str, Any] = None):
        """
        Sets status to 'completed' and saves final result.
        """
        payload = {
            'status': STATUS_COMPLETED,
            'end_time': datetime.now().isoformat()
        }
        if result: payload['result'] = result
        self.repository.update_execution(self.execution_id, payload)

    def fail(self, error: str, details: Dict[str, Any] = None):
        """
        Sets status to 'failed' and saves error message.
        """
        payload = {
            'status': STATUS_FAILED,
            'error': error,
            'end_time': datetime.now().isoformat()
        }
        if details: payload['result'] = details # Halt details often go to result
        self.repository.update_execution(self.execution_id, payload)


class InMemoryProgressTracker(ProgressTracker):
    """
    Tracks progress in-memory via a callback function.
    Used by short-lived API tasks like File Ingestion.
    """
    def __init__(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Initializes the tracker.

        Args:
            callback (Callable[[Dict[str, Any]], None]): Function receiving status updates.
        """
        self.callback = callback
        self.current_state = {}

    def _emit(self, status: str, payload: Dict[str, Any]):
        """Internal helper to emit status."""
        base = {"status": status, "timestamp": datetime.now().isoformat()}
        base.update(payload)
        self.current_state = base
        # Pass the simplified view expected by API consumers
        self.callback(base)

    def start(self, details: Dict[str, Any] = None):
        """Signals start."""
        self._emit(STATUS_STARTED, details or {})

    def update(self, stage: str, percent: int, details: Dict[str, Any] = None):
        """Signals update."""
        data = {"stage": stage, "percent": percent}
        if details: data.update(details)
        self._emit(STATUS_RUNNING, data)

    def complete(self, result: Dict[str, Any] = None):
        """Signals completion."""
        data = {"percent": 100}
        if result: data["result"] = result
        self._emit(STATUS_COMPLETED, data)

    def fail(self, error: str, details: Dict[str, Any] = None):
        """Signals failure."""
        data = {"error": error}
        if details: data.update(details)
        self._emit(STATUS_FAILED, data)
