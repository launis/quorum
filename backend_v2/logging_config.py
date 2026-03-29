"""Logging configuration module."""

import logging
import os
import sys
from typing import Any

# Force UTF-8 on Windows to prevent Logfire/Rich box-drawing crashes (cp1252 to undefined)
if sys.platform == "win32":
    try:
        sys_stdout_reconfigure = getattr(sys.stdout, "reconfigure", None)
        if sys_stdout_reconfigure:
            sys_stdout_reconfigure(encoding="utf-8")
        sys_stderr_reconfigure = getattr(sys.stderr, "reconfigure", None)
        if sys_stderr_reconfigure:
            sys_stderr_reconfigure(encoding="utf-8")
    except Exception:
        pass

from backend_v2.context import get_execution_context
from backend_v2.exceptions import AppException, ErrorCodes

try:
    import logfire
except ImportError:
    logfire: Any = None  # type: ignore
    logging.getLogger(__name__).info("Logfire module not found. Cloud observability will be disabled.")
except Exception as e:
    logging.getLogger(__name__).error("Unexpected error importing logfire.", exc_info=True)
    raise AppException(
        message="Unexpected error importing logfire.", details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
    ) from e

_LOGFIRE_CONFIGURED = False


class ContextFilter(logging.Filter):
    """Injects execution_id from contextvars into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter record to inject execution or request ID."""
        from backend_v2.context import get_request_context

        exec_id = get_execution_context()
        req_id = get_request_context()

        # Priority: Execution ID > Request ID > SYSTEM
        if exec_id:
            record.context_id = f"EXEC:{exec_id[:8]}"  # Shorten for readability
            record.execution_id = exec_id  # Keep full ID for JSON
        elif req_id:
            record.context_id = f"REQ:{req_id[:8]}"
            record.execution_id = req_id  # Reuse field for aggregation
        else:
            record.context_id = "SYSTEM"
            record.execution_id = "SYSTEM"

        return True


def configure_logfire() -> None:
    """Configures Logfire for observability.

    Should be called early in the application lifecycle.
    """
    if logfire is None:
        return
    global _LOGFIRE_CONFIGURED
    # Idempotency check to prevent double initialization/logging
    if _LOGFIRE_CONFIGURED:
        return
    _LOGFIRE_CONFIGURED = True

    if os.getenv("DISABLE_LOGFIRE", "").lower() == "true":
        logging.getLogger(__name__).info("Logfire disabled via DISABLE_LOGFIRE environment variable.")
        return

    try:
        # Force Logfire to use the EU endpoint since the token is an EU token
        # but automatic detection occasionally fails.
        os.environ.setdefault("LOGFIRE_BASE_URL", "https://api-eu.pydantic.dev/")
        os.environ.setdefault("LOGFIRE_SEND_TO_LOGFIRE", "true")

        # Completely disable the Rich Console exporter to prevent cp1252 Unicode crashes on Windows.
        # We already have a standard Python logging StreamHandler anyway.
        os.environ["LOGFIRE_CONSOLE"] = "false"

        # send_to_logfire=True explicitly enables the cloud exporter.
        logfire.configure(send_to_logfire=True)
        logfire.instrument_pydantic()
        logfire.instrument_httpx()
        # logfire.instrument_redis() # Spams the console with Arq queue polling (ZRANGEBYSCORE/ZCARD) every 0.5s

        import litellm

        litellm.success_callback = ["logfire"]  # Instrument LLM Calls
        litellm.failure_callback = ["logfire"]
    except Exception as e:
        msg = f"[LoggingConfig] {ErrorCodes.CONFIGURATION_ERROR.name}: Logfire validation failed: {e}."
        logging.getLogger(__name__).warning(f"{msg} Observability disabled.", exc_info=True)


def setup_logging(log_level: int = logging.INFO) -> None:
    """Configures the root logger to write to a file and the console.

    Log File: backend_debug.log (in the project root)
    Format: timestamp | level | logger_name | message
    """
    # Configure Logfire (Observability) - Ensuring it's configured if not already
    # But ideally called explicitly early.
    configure_logfire()

    # Determine path to log file in project root
    # backend/logging_config.py -> backend/ -> root/
    from backend_v2.settings import get_settings

    settings = get_settings()
    log_file_path = settings.log_file_path

    # Ensure the directory exists (CRITICAL for custom paths)
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            # FAIL FAST: Cannot start without logging capabilities
            raise AppException(
                message=f"FAILED TO CREATE LOG DIRECTORY {log_dir}: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            ) from e

    # Create formatters
    formatter: logging.Formatter
    # MODIFIED: Only force JSON if explicitly requested.
    # This allows 'production' environment (now default) to still use readable logs locally.
    if settings.use_json_logging:
        formatter = JSONFormatter(
            "%(asctime)s | %(levelname)s | [%(context_id)s] | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        # Standard Dev Formatter
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | [%(context_id)s] | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    # Context Filter
    context_filter = ContextFilter()

    # 1. File Handler (UTF-8)
    file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(context_filter)  # Add Filter
    file_handler.setLevel(log_level)

    # 2. Console Handler is created but NOT added to root logger
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)

    # Configure Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates (e.g. uvicorn's default)
    if root_logger.handlers:
        root_logger.handlers = []

    root_logger.addHandler(file_handler)

    # Re-enable Console Logging for Debugging Worker Crashes
    root_logger.addHandler(console_handler)

    if logfire and _LOGFIRE_CONFIGURED:
        try:
            logfire_handler = logfire.LogfireLoggingHandler()
            logfire_handler.setFormatter(formatter)
            logfire_handler.addFilter(context_filter)
            root_logger.addHandler(logfire_handler)
        except Exception as e:
            msg = f"[LoggingConfig] {ErrorCodes.CONFIGURATION_ERROR.name}: Failed to attach Logfire: {e}"
            logging.getLogger(__name__).warning(msg, exc_info=True)

    # Set external libraries to warning to reduce noise
    # Configure uvicorn to use our format (propagate to root handler)
    for uvicorn_logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers = []  # Remove default handlers
        uvicorn_logger.propagate = True  # Use root logger handlers
        uvicorn_logger.setLevel(logging.INFO)

    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("arq").setLevel(logging.WARNING)
    logging.getLogger("opentelemetry.sdk.trace").setLevel(logging.ERROR)

    # LiteLLM is extremely verbose on DEBUG, but we want INFO for Router
    # Explicitly clear handlers to prevent them from writing to console (if they add their own)
    for llm_logger_name in ["LiteLLM", "LiteLLM Router"]:
        llm_logger = logging.getLogger(llm_logger_name)
        llm_logger.handlers = []
        llm_logger.propagate = True
        llm_logger.setLevel(logging.INFO)

    try:
        import litellm

        litellm.set_verbose = False  # type: ignore[attr-defined]
        litellm.suppress_debug_info = True  # Suppress print statements
    except ImportError:
        logging.getLogger(__name__).info("LiteLLM module not found. Skipping LiteLLM debug configuration.")
    except Exception as e:
        logging.getLogger(__name__).error("Unexpected error configuring LiteLLM.", exc_info=True)
        raise AppException(
            message="Failed to configure LiteLLM logging.", details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
        ) from e

    logging.info(f"Logging configured. Writing to: {log_file_path}")


class JSONFormatter(logging.Formatter):
    """JSON Formatter for Production Logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format the record as JSON."""
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "execution_id": getattr(record, "execution_id", "SYSTEM"),
            "context_id": getattr(record, "context_id", "SYSTEM"),
        }

        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)

        # Merge 'extra' context (e.g. error_code, details)
        if hasattr(record, "error_code"):
            log_record["error_code"] = record.error_code
        if hasattr(record, "details"):
            log_record["details"] = record.details

        import json

        return json.dumps(log_record)


def log_error(logger: logging.Logger, exc: Exception, message: str = "An error occurred") -> None:
    """Standardized error logging helper.

    Extracts error_code and details from the exception if available,
    aligning the log output with the APIError schema.
    """
    import re

    error_code = "INTERNAL_ERROR"
    details = None

    # 1. Try to extract from AppException (duck typing)
    if hasattr(exc, "error_code"):
        error_code = exc.error_code
    elif hasattr(exc, "details"):
        # FastAPI HTTPException doesn't have error_code but might have detail
        pass
    else:
        # 2. Fallback: Derive from Class Name
        class_name = exc.__class__.__name__
        # CameCase -> SNAKE_CASE
        error_code = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).upper()

    # 3. Extract Details
    if hasattr(exc, "details"):
        details = exc.details
    elif hasattr(exc, "detail"):
        details = exc.detail

    extra = {"error_code": error_code.name if hasattr(error_code, "name") else str(error_code)}
    if details:
        extra["details"] = details

    # Build the strict log prefix
    code_str = error_code.name if hasattr(error_code, "name") else str(error_code)
    logger.error(f"[App] {code_str}: {message}: {str(exc)}", exc_info=True, extra=extra)
