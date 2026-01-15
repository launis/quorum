"""Custom Exceptions for the application."""

from typing import Any

from fastapi import status


class AppException(Exception):
    """Base class for application exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict | None = None,
    ):
        """Initialize the exception."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ResourceNotFoundError(AppException):
    """Raised when a requested resource (Workflow, Step, Execution) is not found."""

    def __init__(self, resource_type: str, resource_id: str = "", details: dict | None = None):
        """Initialize the exception."""
        error_details = {"resource_type": resource_type, "resource_id": resource_id}
        if details:
            error_details.update(details)
        
        super().__init__(
            message=f"{resource_type} with ID '{resource_id}' not found" if resource_id else resource_type,
            status_code=status.HTTP_404_NOT_FOUND,
            details=error_details,
        )


class WorkflowNotFoundError(ResourceNotFoundError):
    """Raised when a specific Workflow ID is not found."""

    def __init__(self, workflow_id: str):
        """Initialize the exception."""
        super().__init__("Workflow", workflow_id)


class StepNotFoundError(ResourceNotFoundError):
    """Raised when a specific Step ID is not found."""

    def __init__(self, step_id: str):
        """Initialize the exception."""
        super().__init__("Step", step_id)


class ExecutionNotFoundError(ResourceNotFoundError):
    """Raised when a specific Execution ID is not found."""

    def __init__(self, execution_id: str):
        """Initialize the exception."""
        super().__init__("Execution", execution_id)


class AgentExecutionError(AppException):
    """Raised when an agent fails to execute its task.

    Adheres to Echo Protocol:
    raise AgentExecutionError(detail=error_code, original_error=e)
    """

    def __init__(
        self,
        detail: str,
        original_error: Exception | None = None,
        agent_name: str | None = None,
        step_id: str | None = None,
    ):
        """Initialize the exception.

        Args:
            detail (str): The error code or message (e.g. AGENT_EXECUTION_CRITICAL).
            original_error (Optional[Exception]): The caught exception.
            agent_name (Optional[str]): Legacy/Optional context.
            step_id (Optional[str]): Legacy/Optional context.
        """
        msg = f"{detail}"
        if original_error:
            msg += f" - Cause: {str(original_error)}"

        error_details = {"error_code": detail}
        if original_error:
            error_details["original_error"] = str(original_error)
        if agent_name:
            error_details["agent"] = agent_name
        if step_id:
            error_details["step_id"] = step_id

        super().__init__(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details,
        )


class FatalInterruption(AppException):
    """Raised when a critical error requires stopping the entire workflow execution immediately.

    This is favored over silent failures or partial execution.
    """

    def __init__(self, step_name: str, reason: str, details: dict[str, Any] | None = None):
        """Initialize the exception."""
        if details is None:
            details = {}
        # Ensure minimal structure
        details.update({"step": step_name, "reason": reason})

        super().__init__(
            message=f"Fatal Interruption at {step_name}: {reason}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )
        self.step_name = step_name
        self.reason = reason


class ConfigurationError(AppException):
    """Raised when there is a misconfiguration (e.g. missing API key)."""

    def __init__(self, message: str):
        """Initialize the exception."""
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ConflictError(AppException):
    """Raised when a request conflicts with the current state of the server (409)."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, status_code=status.HTTP_409_CONFLICT, details=details)


class PermissionDeniedError(AppException):
    """Raised when the user does not have permission to access the resource (403)."""

    def __init__(self, message: str = "Permission denied", details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN, details=details)


class ServiceUnavailableError(AppException):
    """Raised when a service is temporarily unavailable (503)."""

    def __init__(self, message: str = "Service unavailable", details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE, details=details)


class AuthenticationError(AppException):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Authentication failed", details: dict | None = None):
        """Initialize the exception."""
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED, details=details)


class WorkflowExecutionError(AppException):
    """Raised when a specific step in a workflow fails."""

    def __init__(
        self,
        step_id: str,
        task_key: str,
        original_error: Exception,
        details: dict | None = None,
    ):
        """Initialize the exception."""
        msg = f"Step '{step_id}' (Task: '{task_key}') failed: {str(original_error)}"
        
        error_details = details or {}
        error_details.update({
            "step_id": step_id,
            "task_key": task_key,
            "cause": str(original_error)
        })

        super().__init__(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details,
        )
        self.original_error = original_error
