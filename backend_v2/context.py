"""Context management for Execution and Request IDs."""

from contextvars import ContextVar

from backend_v2.exceptions import AppException, ErrorCodes

# Global context variable for Execution ID (Workflow Runs)
execution_id_var: ContextVar[str | None] = ContextVar("execution_id", default=None)

# Global context variable for Request ID (API Requests)
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_execution_context(execution_id: str):
    """Set the current thread's execution ID.

    Raises:
        AppException: If execution_id is empty (Fail Fast).
    """
    if not execution_id or not execution_id.strip():
        raise AppException(
            message="Cannot set empty execution context.",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR},
        )
    execution_id_var.set(execution_id)


def get_execution_context() -> str | None:
    """Get the current thread's execution ID."""
    return execution_id_var.get()


def clear_execution_context():
    """Clear the current thread's execution ID."""
    execution_id_var.set(None)


def set_request_context(request_id: str):
    """Set the current thread's request ID.

    Raises:
        AppException: If request_id is empty (Fail Fast).
    """
    if not request_id or not request_id.strip():
        raise AppException(
            message="Cannot set empty request context.",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR},
        )
    request_id_var.set(request_id)


def get_request_context() -> str | None:
    """Get the current thread's request ID."""
    return request_id_var.get()


def clear_request_context():
    """Clear the current thread's request ID."""
    request_id_var.set(None)
