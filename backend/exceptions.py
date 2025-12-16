from typing import Dict, Any

class AppException(Exception):
    """Base class for application exceptions."""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class ResourceNotFoundError(AppException):
    """Raised when a requested resource (Workflow, Step, Execution) is not found."""
    def __init__(self, resource_type: str, resource_id: str):
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' not found", 
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )

class WorkflowNotFoundError(ResourceNotFoundError):
    def __init__(self, workflow_id: str):
        super().__init__("Workflow", workflow_id)

class StepNotFoundError(ResourceNotFoundError):
    def __init__(self, step_id: str):
        super().__init__("Step", step_id)

class ExecutionNotFoundError(ResourceNotFoundError):
    def __init__(self, execution_id: str):
        super().__init__("Execution", execution_id)

class AgentExecutionError(AppException):
    """Raised when an agent fails to execute its task."""
    def __init__(self, agent_name: str, step_id: str, original_error: Exception):
        super().__init__(
            message=f"Agent '{agent_name}' failed at step '{step_id}': {str(original_error)}",
            status_code=500,
            details={"agent": agent_name, "step_id": step_id, "original_error": str(original_error)}
        )

class FatalInterruption(AppException):
    """
    Raised when a critical error requires stopping the entire workflow execution immediately.
    This is favored over silent failures or partial execution.
    """
    def __init__(self, step_name: str, reason: str, details: Dict[str, Any] = None):
        if details is None:
            details = {}
        # Ensure minimal structure
        details.update({"step": step_name, "reason": reason})
        
        super().__init__(
            message=f"Fatal Interruption at {step_name}: {reason}",
            status_code=500,
            details=details
        )
        self.step_name = step_name
        self.reason = reason

class ConfigurationError(AppException):
    """Raised when there is a misconfiguration (e.g. missing API key)."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)
