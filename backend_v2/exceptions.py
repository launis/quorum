"""Custom Exceptions for the application.

RFC 7807 Problem Details Compatible (https://tools.ietf.org/html/rfc7807).

================================================================================
USAGE GUIDE (Mandatory Pattern)
================================================================================

1. RAISING EXCEPTIONS (Backend):

    from backend_v2.exceptions import AppException
    from fastapi import status
    import logging

    logger = logging.getLogger(__name__)

    try:
        # ... business logic ...
    except Exception as e:
        error_code = "DOMAIN_REASON_DETAIL"  # e.g. "EXECUTION_FETCH_FAILED"
        logger.error("An error occurred: %s", str(e), exc_info=True, extra={"error_code": error_code})
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

import logging
from enum import Enum
from typing import Any

from fastapi import status
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class ErrorCodes(str, Enum):
    """Standardized Error Codes for the application.

    These codes are used by the Frontend for localization lookup.
    """

    # General
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"
    CONFIGURATION_ERROR = "CONFIGURATION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    CONFLICT_ERROR = "CONFLICT_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"

    # Validation
    EMPTY_INPUT = "EMPTY_INPUT"
    INVALID_JSON_PAYLOAD = "INVALID_JSON_PAYLOAD"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    INVALID_OUTPUT_SCHEMA = "INVALID_OUTPUT_SCHEMA"
    MISSING_WORKFLOW_ID = "MISSING_WORKFLOW_ID"
    UNSUPPORTED_CONTENT_TYPE = "UNSUPPORTED_CONTENT_TYPE"
    REPORT_GENERATION_FAILED = "REPORT_GENERATION_FAILED"
    REPORT_NOT_READY = "REPORT_NOT_READY"

    # Resources
    EXECUTION_NOT_FOUND = "EXECUTION_NOT_FOUND"
    WORKFLOW_NOT_FOUND = "WORKFLOW_NOT_FOUND"
    JOB_NOT_FOUND = "JOB_NOT_FOUND"

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
    SERVICE_DISABLED = "SERVICE_DISABLED"
    CAPABILITY_NOT_SUPPORTED = "CAPABILITY_NOT_SUPPORTED"
    TOKEN_LIMIT_EXCEEDED = "TOKEN_LIMIT_EXCEEDED"

    # Model Config
    INVALID_REGISTRY_STRUCTURE = "INVALID_REGISTRY_STRUCTURE"
    MODEL_LIST_FAILED = "MODEL_LIST_FAILED"
    INVALID_MODEL_ID = "INVALID_MODEL_ID"
    MODEL_UPDATE_FAILED = "MODEL_UPDATE_FAILED"
    DELETE_BLOCKED_SYSTEM_DEFAULT = "DELETE_BLOCKED_SYSTEM_DEFAULT"
    DELETE_BLOCKED_BY_USAGE = "DELETE_BLOCKED_BY_USAGE"
    MODEL_DELETE_FAILED = "MODEL_DELETE_FAILED"

    # Ontology / Dimensions
    DIMENSION_LIST_FAILED = "DIMENSION_LIST_FAILED"
    DIMENSION_NOT_FOUND = "DIMENSION_NOT_FOUND"
    DIMENSION_DELETE_FAILED = "DIMENSION_DELETE_FAILED"
    DIMENSION_UPDATE_FAILED = "DIMENSION_UPDATE_FAILED"
    DIMENSION_ID_MISMATCH = "DIMENSION_ID_MISMATCH"

    # Scoring
    SCORING_MISSING_FIELD = "SCORING_MISSING_FIELD"
    SCORING_LEGACY_DATA_REJECTED = "SCORING_LEGACY_DATA_REJECTED"
    SCORING_MISSING_SCALE_MAX = "SCORING_MISSING_SCALE_MAX"
    SCORING_MISSING_JUDGE_OUTPUT = "SCORING_MISSING_JUDGE_OUTPUT"
    CALCULATION_FAILED = "CALCULATION_FAILED"

    # State Presenter
    STATE_INTEGRITY_ERROR = "STATE_INTEGRITY_ERROR"

    # Reference Manager
    KNOWLEDGE_BASE_INVALID = "KNOWLEDGE_BASE_INVALID"
    CITATION_PARSING_FAILED = "CITATION_PARSING_FAILED"

    # Prompt Builder
    PROMPT_CONSTRUCTION_FAILED = "PROMPT_CONSTRUCTION_FAILED"

    # Storage
    STORAGE_CONFIG_ERROR = "STORAGE_CONFIG_ERROR"
    STORAGE_ACCESS_FAILED = "STORAGE_ACCESS_FAILED"
    FILESYSTEM_VIOLATION = "FILESYSTEM_VIOLATION"
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    STORAGE_BUCKET_NOT_FOUND = "STORAGE_BUCKET_NOT_FOUND"
    DATA_CORRUPTION = "DATA_CORRUPTION"
    FILE_LOCKED_ERROR = "FILE_LOCKED_ERROR"

    # Progress
    PROGRESS_UPDATE_FAILED = "PROGRESS_UPDATE_FAILED"

    # Web Fetcher
    FETCH_FAILED = "FETCH_FAILED"
    URL_INVALID = "URL_INVALID"

    # Usage Service
    USAGE_TRACKING_FAILED = "USAGE_TRACKING_FAILED"
    QUOTA_CHECK_FAILED = "QUOTA_CHECK_FAILED"

    # Validation Service
    REGISTRY_CORRUPTION = "REGISTRY_CORRUPTION"
    STEP_LIST_FAILED = "STEP_LIST_FAILED"
    STEP_FETCH_FAILED = "STEP_FETCH_FAILED"
    STEP_CREATE_FAILED = "STEP_CREATE_FAILED"
    STEP_UPDATE_FAILED = "STEP_UPDATE_FAILED"
    STEP_DELETE_FAILED = "STEP_DELETE_FAILED"
    WORKFLOW_LIST_FAILED = "WORKFLOW_LIST_FAILED"
    WORKFLOW_FETCH_FAILED = "WORKFLOW_FETCH_FAILED"
    WORKFLOW_CREATE_FAILED = "WORKFLOW_CREATE_FAILED"
    WORKFLOW_UPDATE_FAILED = "WORKFLOW_UPDATE_FAILED"
    WORKFLOW_DELETE_FAILED = "WORKFLOW_DELETE_FAILED"
    WORKFLOW_COPY_FAILED = "WORKFLOW_COPY_FAILED"

    # PDF / Reports
    PDF_DOWNLOAD_FAILED = "PDF_DOWNLOAD_FAILED"
    PDF_GENERATION_FAILED = "PDF_GENERATION_FAILED"
    PDF_TEXT_EXTRACTION_FAILED = "PDF_TEXT_EXTRACTION_FAILED"

    # Network / Infra
    NETWORK_UNAVAILABLE = "NETWORK_UNAVAILABLE"
    SERVICE_DEPENDENCY_MISSING = "SERVICE_DEPENDENCY_MISSING"

    # Client Telemetry
    CLIENT_ERROR = "CLIENT_ERROR"

    # Documents
    DOCUMENT_PROCESSING_FAILED = "DOCUMENT_PROCESSING_FAILED"

    INVALID_FILE_FORMAT = "INVALID_FILE_FORMAT"

    # Engine / Workflow
    WORKFLOW_COMPILATION_ERROR = "WORKFLOW_COMPILATION_ERROR"
    HOOK_EXECUTION_FAILED = "HOOK_EXECUTION_FAILED"
    INPUT_RESOLUTION_FAILED = "INPUT_RESOLUTION_FAILED"
    TASK_NOT_FOUND = "TASK_NOT_FOUND"
    COMPONENT_NOT_FOUND = "COMPONENT_NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    MISSING_XAI_EXTENSION = "MISSING_XAI_EXTENSION"
    MISSING_ROUTING_MODE = "MISSING_ROUTING_MODE"

    # Knowledge Base
    KNOWLEDGE_INGESTION_FAILED = "KNOWLEDGE_INGESTION_FAILED"
    KNOWLEDGE_ARCHIVAL_FAILED = "KNOWLEDGE_ARCHIVAL_FAILED"
    KNOWLEDGE_RESET_FAILED = "KNOWLEDGE_RESET_FAILED"
    KNOWLEDGE_RETRIEVAL_FAILED = "KNOWLEDGE_RETRIEVAL_FAILED"
    KNOWLEDGE_NOT_INGESTED = "KNOWLEDGE_NOT_INGESTED"
    PARSING_FAILED = "PARSING_FAILED"

    # Search / External Tools
    SEARCH_CONFIG_ERROR = "SEARCH_CONFIG_ERROR"
    SEARCH_EXECUTION_FAILED = "SEARCH_EXECUTION_FAILED"
    SEARCH_MISSING_INPUT = "SEARCH_MISSING_INPUT"
    SEARCH_QUOTA_EXCEEDED = "SEARCH_QUOTA_EXCEEDED"

    # Security
    SECURITY_CONFIG_ERROR = "SECURITY_CONFIG_ERROR"
    SECURITY_DB_ERROR = "SECURITY_DB_ERROR"
    SECURITY_SCAN_FAILED = "SECURITY_SCAN_FAILED"
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    SECURITY_BANNED_PHRASE_DETECTED = "SECURITY_BANNED_PHRASE_DETECTED"

    # Role Specific
    AGENT_MISSING_INSTRUCTION = "AGENT_MISSING_INSTRUCTION"
    AGENT_NOT_CONFIGURED = "AGENT_NOT_CONFIGURED"
    AGENT_RESPONSE_MALFORMED = "AGENT_RESPONSE_MALFORMED"
    AGENT_RESPONSE_PARSING_FAILED = "AGENT_RESPONSE_PARSING_FAILED"
    AGENT_SCHEMA_VALIDATION_FAILED = "AGENT_SCHEMA_VALIDATION_FAILED"
    AGENT_LOGICAL_VALIDATION_FAILED = "AGENT_LOGICAL_VALIDATION_FAILED"
    AGENT_INVALID_INPUT = "AGENT_INVALID_INPUT"


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
        logger.error("An error occurred: %s", str(e), exc_info=True, extra={"error_code": error_code})
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
        details: dict[str, Any] | None = None,
    ):
        """Initialize the exception."""
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}

    @property
    def error_code(self) -> str:
        """Extract error_code from details for convenience."""
        val = self.details.get("error_code", "INTERNAL_SERVER_ERROR")
        return str(val)

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

        # Include any extra details, ensuring error_code is always present for L10n
        extra = self.details.copy() if self.details else {}

        # Ensure error_code is in extensions even if redundant with type URI
        if "error_code" not in extra:
            extra["error_code"] = self.error_code

        if extra:
            problem["extensions"] = extra

        return problem


class ResourceNotFoundError(AppException):
    """Raised when a requested resource (Workflow, Step, Execution) is not found."""

    def __init__(self, resource_type: str, resource_id: str = "", details: dict[str, Any] | None = None):
        """Initialize the exception."""
        error_details = {
            "resource_type": resource_type,
            "resource_id": resource_id,
            "error_code": ErrorCodes.RESOURCE_NOT_FOUND,
        }
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
        super().__init__("Workflow", workflow_id, details={"error_code": ErrorCodes.WORKFLOW_NOT_FOUND})


class StepNotFoundError(ResourceNotFoundError):
    """Raised when a specific Step ID is not found."""

    def __init__(self, step_id: str):
        """Initialize the exception."""
        super().__init__("Step", step_id, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND})


class ExecutionNotFoundError(ResourceNotFoundError):
    """Raised when a specific Execution ID is not found."""

    def __init__(self, execution_id: str):
        """Initialize the exception."""
        super().__init__("Execution", execution_id, details={"error_code": ErrorCodes.EXECUTION_NOT_FOUND})


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
            formatted_cause = format_validation_error(original_error)
            msg += f" - Cause: {formatted_cause}"

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
        self.original_error = original_error

    def _format_cause(self, exc: Exception) -> str:
        """Legacy wrapper for format_validation_error."""
        return format_validation_error(exc)


def format_validation_error(exc: Exception) -> str:
    """Formats the exception into a human-readable string, specifically handling Pydantic ValidationErrors."""
    try:
        if isinstance(exc, ValidationError):
            errors = exc.errors()
            missing_fields = []
            other_errors = []

            for err in errors:
                # Parse location (e.g. ['body', 'field'] -> body.field)
                loc = ".".join(str(loc_item) for loc_item in err.get("loc", []))
                msg = err.get("msg", "Unknown error")
                err_type = err.get("type", "")

                if err_type == "missing":
                    missing_fields.append(loc)
                else:
                    other_errors.append(f"{loc}: {msg}")

            parts = []
            if missing_fields:
                parts.append(f"Missing required fields: {', '.join(missing_fields)}")
            if other_errors:
                parts.append("; ".join(other_errors))

            # Use title if available (e.g. "ContextData")
            title = getattr(exc, "title", "Schema")
            return f"{title} validation failed. " + "; ".join(parts)
    except Exception as e:
        logger.error(f"Failed to format validation error for {type(exc).__name__}", exc_info=True)
        raise AppException(
            message="Internal error during error formatting.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e

    return str(exc)


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

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize the exception."""
        d = {"error_code": ErrorCodes.CONFIGURATION_ERROR}
        if details:
            d.update(details)
        super().__init__(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details=d)


class ConflictError(AppException):
    """Raised when a request conflicts with the current state of the server (409)."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize the exception."""
        d = {"error_code": ErrorCodes.CONFLICT_ERROR}
        if details:
            d.update(details)
        super().__init__(message, status_code=status.HTTP_409_CONFLICT, details=d)


class PermissionDeniedError(AppException):
    """Raised when the user does not have permission to access the resource (403)."""

    def __init__(self, message: str = "Permission denied", details: dict[str, Any] | None = None):
        """Initialize the exception."""
        d = {"error_code": ErrorCodes.PERMISSION_DENIED}
        if details:
            d.update(details)
        super().__init__(message, status_code=status.HTTP_403_FORBIDDEN, details=d)


class ServiceUnavailableError(AppException):
    """Raised when a service is temporarily unavailable (503)."""

    def __init__(self, message: str = "Service unavailable", details: dict[str, Any] | None = None):
        """Initialize the exception."""
        d = {"error_code": ErrorCodes.SERVICE_UNAVAILABLE}
        if details:
            d.update(details)
        super().__init__(message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE, details=d)


class AuthenticationError(AppException):
    """Raised when authentication fails (401)."""

    def __init__(self, message: str = "Authentication failed", details: dict[str, Any] | None = None):
        """Initialize the exception."""
        d = {"error_code": ErrorCodes.AUTHENTICATION_FAILED}
        if details:
            d.update(details)
        super().__init__(message, status_code=status.HTTP_401_UNAUTHORIZED, details=d)


class SecurityViolationError(AppException):
    """Raised when a security policy (e.g. banned phrases) is violated (400 or 403)."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """Initialize the exception."""
        # 400 Bad Request matches "Client sent invalid content"
        d = {"error_code": ErrorCodes.SECURITY_VIOLATION}
        if details:
            d.update(details)
        super().__init__(message, status_code=status.HTTP_400_BAD_REQUEST, details=d)


class WorkflowExecutionError(AppException):
    """Raised when a specific step in a workflow fails."""

    def __init__(
        self,
        step_id: str,
        task_key: str,
        original_error: Exception,
        details: dict[str, Any] | None = None,
    ):
        """Initialize the exception."""
        msg = f"Step '{step_id}' (Task: '{task_key}') failed: {str(original_error)}"

        error_details = details or {}
        error_details.update({"step_id": step_id, "task_key": task_key, "cause": str(original_error)})
        if "error_code" not in error_details:
            error_details["error_code"] = ErrorCodes.WORKFLOW_EXECUTION_FAILED

        super().__init__(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=error_details,
        )
        self.original_error = original_error


class WorkflowCompilationError(AppException):
    """Raised when a workflow fails semantic Pre-Flight validation statically."""

    def __init__(self, step_id: str | None, message: str):
        """Initialize the exception.

        Args:
            step_id: The ID of the specific workflow step causing the failure, if applicable.
            message: Human-readable technical error explanation.
        """
        details = {"error_code": ErrorCodes.WORKFLOW_COMPILATION_ERROR, "step_id": step_id}
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, details=details)
        self.step_id = step_id


class TokenLimitExceededError(AppException):
    """Raised when token length of the LLM context exceeds the safe threshold."""

    def __init__(self, message: str = "Token limit exceeded", details: dict[str, Any] | None = None):
        """Initialize the exception."""
        d = {"error_code": ErrorCodes.TOKEN_LIMIT_EXCEEDED}
        if details:
            d.update(details)
        super().__init__(message, status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, details=d)


class MissingInputMappingError(AppException):
    """Raised when safe dot-notation traversal fails to find a valid key/attribute."""

    def __init__(self, path: str, state_type: str, reason: str):
        """Initialize the exception.

        Args:
            path: The dot-notation path that failed.
            state_type: The type of the object being traversed.
            reason: Specific technical reason (e.g., KeyError, AttributeError).
        """
        msg = f"Failed to resolve path '{path}' in {state_type}: {reason}"
        details = {
            "error_code": ErrorCodes.INPUT_RESOLUTION_FAILED.value,
            "path": path,
            "state_type": state_type,
            "reason": reason,
        }
        super().__init__(message=msg, status_code=status.HTTP_400_BAD_REQUEST, details=details)


class MissingXaiExtensionError(AppException):
    """Raised when an extension is requested by UI but missing in TraceEvent."""

    def __init__(self, extension_name: str, step_id: str | None = None):
        """Initialize the exception."""
        details = {"error_code": ErrorCodes.MISSING_XAI_EXTENSION, "extension": extension_name}
        if step_id:
            details["step_id"] = step_id
        super().__init__(
            message=f"XAI Extension '{extension_name}' is missing but required by UI Output Profile.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class MissingRoutingModeError(AppException):
    """Raised when step-to-step mapping lacks a routing_mode instruction."""

    def __init__(self, mapping_path: str):
        """Initialize the exception."""
        details = {"error_code": ErrorCodes.MISSING_ROUTING_MODE, "mapping_path": mapping_path}
        super().__init__(
            message=f"Routing mode is missing for mapping '{mapping_path}'.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class LLMSchemaValidationError(AppException):
    """Raised when the LLM returns structured output that fails Pydantic schema validation.

    This exception safely carries the raw JSON payload and EOF status to the orchestrator
    for Self-Healing retry attempts.
    """

    def __init__(
        self,
        raw_llm_payload: str,
        validation_error_msg: str,
        is_eof: bool = False,
        token_usage: Any | None = None,
    ):
        """Initialize the exception."""
        details = {
            "error_code": ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED,
            "raw_llm_payload": raw_llm_payload,
            "validation_error_msg": validation_error_msg,
            "is_eof": is_eof,
        }
        super().__init__(
            message=f"LLM Schema Validation Failed: {validation_error_msg}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )
        self.raw_llm_payload = raw_llm_payload
        self.validation_error_msg = validation_error_msg
        self.is_eof = is_eof
        self.token_usage = token_usage


class LogicalValidationError(AppException):
    """Raised by asynchronous domain-level validator hooks when cognitive validation fails.

    This explicitly signals to the LLMTaskExecutor that the output is structurally sound
    but contextually/logically flawed, triggering Semantic Self-Healing.
    """

    def __init__(self, validation_error_msg: str):
        """Initialize the exception."""
        details = {
            "error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED,
            "validation_error_msg": validation_error_msg,
        }
        super().__init__(
            message=f"Logical Validation Failed: {validation_error_msg}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=details,
        )
        self.validation_error_msg = validation_error_msg


class PydanticSyntaxError(LLMSchemaValidationError):
    """Raised when LLM returns unstructured output that fails pure syntax checks."""

    pass


class SemanticEvidenceError(AppException):
    """Raised when an atom fails semantic O(1) anchoring. Directly routes to DLQ without AI reasoning."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details or {"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED},
        )
