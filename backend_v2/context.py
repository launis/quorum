"""Context management for Execution and Request IDs."""

import logging
from contextvars import ContextVar

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

# Global context variable for Execution ID (Workflow Runs)
execution_id_var: ContextVar[str | None] = ContextVar("execution_id", default=None)

# Global context variable for Request ID (API Requests)
request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_execution_context(execution_id: str) -> None:
    """Set the current thread's execution ID.

    Raises:
        AppException: If execution_id is empty (Fail Fast).
    """
    if not execution_id or not execution_id.strip():
        msg = "Cannot set empty execution context."
        logger.error("[Context] %s", msg, extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value})
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        )
    execution_id_var.set(execution_id)


def get_execution_context() -> str | None:
    """Get the current thread's execution ID."""
    return execution_id_var.get()


def clear_execution_context() -> None:
    """Clear the current thread's execution ID."""
    execution_id_var.set(None)


def set_request_context(request_id: str) -> None:
    """Set the current thread's request ID.

    Raises:
        AppException: If request_id is empty (Fail Fast).
    """
    if not request_id or not request_id.strip():
        msg = "Cannot set empty request context."
        logger.error("[Context] %s", msg, extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value})
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        )
    request_id_var.set(request_id)


def get_request_context() -> str | None:
    """Get the current thread's request ID."""
    return request_id_var.get()


def clear_request_context() -> None:
    """Clear the current thread's request ID."""
    request_id_var.set(None)
