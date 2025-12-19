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
        """Signals the process has started."""
        pass

    @abstractmethod
    def update(self, stage: str, percent: int, details: Dict[str, Any] = None):
        """Updates progress with current stage and percentage."""
        pass

    @abstractmethod
    def complete(self, result: Dict[str, Any] = None):
        """Signals successful completion."""
        pass

    @abstractmethod
    def fail(self, error: str, details: Dict[str, Any] = None):
        """Signals failure/halt."""
        pass


class DatabaseProgressTracker(ProgressTracker):
    """
    Tracks progress by updating the 'executions' table in the database.
    Used by WorkflowEngine.
    """
    def __init__(self, repository: AbstractWorkflowRepository, execution_id: str):
        self.repository = repository
        self.execution_id = execution_id

    def start(self, details: Dict[str, Any] = None):
        payload = {'status': STATUS_STARTED, 'start_time': datetime.now().isoformat()}
        if details: payload.update(details)
        self.repository.update_execution(self.execution_id, payload)

    def update(self, stage: str, percent: int, details: Dict[str, Any] = None):
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
        payload = {
            'status': STATUS_COMPLETED,
            'end_time': datetime.now().isoformat()
        }
        if result: payload['result'] = result
        self.repository.update_execution(self.execution_id, payload)

    def fail(self, error: str, details: Dict[str, Any] = None):
        payload = {
            'status': STATUS_FAILED,
            'error': error,
            'end_time': datetime.now().isoformat()
        }
        if details: payload['result'] = details # Halt details often go to result
        self.repository.update_execution(self.execution_id, payload)


class InMemoryProgressTracker(ProgressTracker):
    """
    Tracks progress in-memory or via a callback.
    Used by File Ingestion API (KnowledgeBaseService).
    """
    def __init__(self, callback: Callable[[str, Dict[str, Any]], None]):
        """
        :param callback: Function(job_id, status_dict) -> None
        A callback that receives the updated status dictionary directly.
        """
        self.callback = callback
        self.current_state = {}

    def _emit(self, status: str, payload: Dict[str, Any]):
        base = {"status": status, "timestamp": datetime.now().isoformat()}
        base.update(payload)
        self.current_state = base
        # Pass the simplified view expected by API consumers
        self.callback(base)

    def start(self, details: Dict[str, Any] = None):
        self._emit(STATUS_STARTED, details or {})

    def update(self, stage: str, percent: int, details: Dict[str, Any] = None):
        data = {"stage": stage, "percent": percent}
        if details: data.update(details)
        self._emit(STATUS_RUNNING, data)

    def complete(self, result: Dict[str, Any] = None):
        data = {"percent": 100}
        if result: data["result"] = result
        self._emit(STATUS_COMPLETED, data)

    def fail(self, error: str, details: Dict[str, Any] = None):
        data = {"error": error}
        if details: data.update(details)
        self._emit(STATUS_FAILED, data)
