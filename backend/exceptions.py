"""Custom Exceptions for the application.

RFC 7807 Problem Details Compatible (https://tools.ietf.org/html/rfc7807).

================================================================================
USAGE GUIDE (Mandatory Pattern)
================================================================================

1. RAISING EXCEPTIONS (Backend):

    from backend.exceptions import AppException
    from fastapi import status
    import logging

    logger = logging.getLogger(__name__)

    try:
        # ... business logic ...
    except Exception as e:
        error_code = "DOMAIN_REASON_DETAIL"  # e.g. "EXECUTION_FETCH_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code}
        ) from e

2. ERROR CODE NAMING CONVENTION:
   
   Format: DOMAIN_REASON_DETAIL
   
   Examples:
   - EXECUTION_NOT_FOUND      (404)
   - WORKFLOW_EXECUTION_FAILED (500)
   - INVALID_JSON_PAYLOAD     (400)
   - MISSING_WORKFLOW_ID      (400)
   - AUTH_TOKEN_EXPIRED       (401)
   - PERMISSION_DENIED        (403)

3. FIELD PURPOSES:

   | Field       | Purpose                                    | Consumer          |
   |-------------|--------------------------------------------|--------------------|
   | error_code  | Machine-readable key for localization      | Flutter l10n       |
   | message     | Debug info (NEVER shown to user)           | Logs, DevTools     |
   | status_code | HTTP standard code                         | HTTP layer         |

4. RFC 7807 RESPONSE FORMAT (via to_problem_detail()):

   {
     "type": "https://api.quorum.fi/errors/execution-not-found",
     "title": "Execution Not Found",
     "status": 404,
     "detail": "Execution 'abc-123' not found.",
     "instance": "/executions/abc-123"
   }

5. EXCEPTION HANDLER (main.py - update required for RFC 7807):

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content=exc.to_problem_detail(instance=str(request.url.path)),
            media_type="application/problem+json",
        )

6. FLUTTER CLIENT (update required for RFC 7807):

    on DioException catch (e) {
      final problem = ProblemDetail.fromJson(e.response?.data);
      throw AppError(
        code: problem.errorCode,  // Extracted from 'type' URI
        message: problem.detail,
      );
    }

================================================================================
BANNED PATTERNS
================================================================================

❌ raise HTTPException(status_code=..., detail=str(e))  # Loses error_code!
❌ Showing raw 'message' or 'detail' to end users
❌ Hardcoded error messages in Flutter UI

================================================================================
"""

from typing import Any

from enum import Enum
from fastapi import status


class ErrorCodes(str, Enum):
    """Standardized Error Codes for the application.
    
    These codes are used by the Frontend for localization lookup.
    """
    # General
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    
    # Validation
    EMPTY_INPUT = "EMPTY_INPUT"
    INVALID_JSON_PAYLOAD = "INVALID_JSON_PAYLOAD"
    MISSING_WORKFLOW_ID = "MISSING_WORKFLOW_ID"
    UNSUPPORTED_CONTENT_TYPE = "UNSUPPORTED_CONTENT_TYPE"
    
    # Resources
    EXECUTION_NOT_FOUND = "EXECUTION_NOT_FOUND"
    WORKFLOW_NOT_FOUND = "WORKFLOW_NOT_FOUND"
    
    # Visualization
    CHART_GENERATION_FAILED = "CHART_GENERATION_FAILED"
    
    # Execution
    WORKFLOW_EXECUTION_FAILED = "WORKFLOW_EXECUTION_FAILED"
    AGENT_EXECUTION_CRITICAL = "AGENT_EXECUTION_CRITICAL"
    
    # Auth
    AUTH_TOKEN_EXPIRED = "AUTH_TOKEN_EXPIRED"
    PERMISSION_DENIED = "PERMISSION_DENIED"

    # LLM Infra
    MODEL_OUTPUT_LIMIT_EXCEEDED = "MODEL_OUTPUT_LIMIT_EXCEEDED"
    UPSTREAM_TIMEOUT = "UPSTREAM_TIMEOUT"

    # PDF / Reports
    PDF_DOWNLOAD_FAILED = "PDF_DOWNLOAD_FAILED"
    PDF_GENERATION_FAILED = "PDF_GENERATION_FAILED"


class AppException(Exception):
    """Base class for application exceptions (RFC 7807 compatible).

    Provides both legacy format (message/details) and RFC 7807 Problem Details
    format via to_problem_detail() method.

    Args:
        message: Debug message for logs (NEVER shown to end user).
        status_code: HTTP status code (default 500).
        details: Dict containing 'error_code' for frontend localization.

    Example:
        error_code = "WORKFLOW_NOT_FOUND"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_404_NOT_FOUND,
            details={"error_code": error_code}
        ) from e

    RFC 7807 Example:
        exc = AppException(
            message="Execution 'abc' not found",
            status_code=404,
            details={"error_code": "EXECUTION_NOT_FOUND"}
        )
        response = exc.to_problem_detail(instance="/executions/abc")
        # Returns:
        # {
        #   "type": "https://api.quorum.fi/errors/execution-not-found",
        #   "title": "Execution Not Found",
        #   "status": 404,
        #   "detail": "Execution 'abc' not found",
        #   "instance": "/executions/abc"
        # }
    """

    # Base URI for RFC 7807 'type' field - customize per deployment
    PROBLEM_BASE_URI = "https://api.quorum.fi/errors"

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

    @property
    def error_code(self) -> str:
        """Extract error_code from details for convenience."""
        return self.details.get("error_code", "INTERNAL_SERVER_ERROR")

    def to_problem_detail(self, instance: str | None = None) -> dict[str, Any]:
        """Convert to RFC 7807 Problem Details format.

        Args:
            instance: Optional URI identifying this specific error occurrence
                      (typically the request path, e.g. "/executions/abc-123").

        Returns:
            Dict conforming to RFC 7807 Problem Details specification:
            - type: URI identifying the error type (links to documentation)
            - title: Human-readable error title (from error_code)
            - status: HTTP status code
            - detail: Specific error message for this occurrence
            - instance: Optional URI for this specific error

        Example:
            {
                "type": "https://api.quorum.fi/errors/execution-not-found",
                "title": "Execution Not Found",
                "status": 404,
                "detail": "Execution 'abc-123' not found.",
                "instance": "/executions/abc-123"
            }
        """
        # Convert EXECUTION_NOT_FOUND -> execution-not-found
        slug = self.error_code.lower().replace("_", "-")

        # Convert EXECUTION_NOT_FOUND -> "Execution Not Found"
        title = self.error_code.replace("_", " ").title()

        problem = {
            "type": f"{self.PROBLEM_BASE_URI}/{slug}",
            "title": title,
            "status": self.status_code,
            "detail": self.message,
        }

        if instance:
            problem["instance"] = instance

        # Include any extra details (excluding error_code which is in 'type')
        extra = {k: v for k, v in self.details.items() if k != "error_code"}
        if extra:
            problem["extensions"] = extra

        return problem


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


class SecurityViolationError(AppException):
    """Raised when a security policy (e.g. banned phrases) is violated (400 or 403)."""

    def __init__(self, message: str, details: dict | None = None):
        """Initialize the exception."""
        # 400 Bad Request matches "Client sent invalid content"
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST, details=details)


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
        error_details.update({"step_id": step_id, "task_key": task_key, "cause": str(original_error)})

        super().__init__(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details,
        )
        self.original_error = original_error
