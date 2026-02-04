"""Logging configuration module."""

import logging
import os
import sys
from typing import Any

from backend.context import get_execution_context

try:
    import logfire
except Exception:
    logfire: Any = None  # type: ignore

_LOGFIRE_CONFIGURED = False


class ContextFilter(logging.Filter):
    """Injects execution_id from contextvars into log records."""

    def filter(self, record):
        """Filter record to inject execution or request ID."""
        from backend.context import get_request_context

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


def configure_logfire():
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
        logfire.configure()
        logfire.instrument_pydantic()
    except Exception as e:
        logging.getLogger(__name__).warning(
            f"Logfire validation failed (likely no token): {e}. Observability disabled."
        )


def setup_logging(log_level=logging.INFO):
    """Configures the root logger to write to a file and the console.

    Log File: backend_debug.log (in the project root)
    Format: timestamp | level | logger_name | message
    """
    # Configure Logfire (Observability) - Ensuring it's configured if not already
    # But ideally called explicitly early.
    configure_logfire()

    # Determine path to log file in project root
    # backend/logging_config.py -> backend/ -> root/
    from backend.settings import get_settings

    settings = get_settings()
    log_file_path = settings.log_file_path

    # Ensure the directory exists (CRITICAL for custom paths)
    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            # Fallback to stdout only if we can't create the file,
            # effectively disabling file logging to prevent crash.
            print(f"FAILED TO CREATE LOG DIRECTORY {log_dir}: {e}")
            # Reset to None so FileHandler is skipped?
            # Actually easier to let it fail or wrap in try/except block below.
            pass

    # Create formatters
    formatter: logging.Formatter
    if settings.environment.lower() == "production" or settings.use_json_logging:
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

    # 2. Console Handler (Silent Mode: WARNING+)
    # We want minimal console output, so we mute INFO logs here.
    # Users should check backend_debug.log for INFO/DEBUG details.
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)  # Add Filter
    console_handler.setLevel(logging.WARNING)

    # Configure Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates (e.g. uvicorn's default)
    if root_logger.handlers:
        root_logger.handlers = []

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

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

    # LiteLLM is extremely verbose on DEBUG
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    try:
        import litellm

        litellm.set_verbose = False
    except Exception:
        pass

    logging.info(f"Logging configured. Writing to: {log_file_path}")


class JSONFormatter(logging.Formatter):
    """JSON Formatter for Production Logging."""

    def format(self, record):
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


def log_error(logger: logging.Logger, exc: Exception, message: str = "An error occurred"):
    """Standardized error logging helper.

    Extracts error_code and details from the exception if available,
    aligning the log output with the APIError schema.
    """
    import re

    error_code = "INTERNAL_ERROR"
    details = None

    # 1. Try to extract from AppException (duck typing)
    if hasattr(exc, "error_code"):
        error_code = exc.error_code  # type: ignore
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
        details = exc.details  # type: ignore
    elif hasattr(exc, "detail"):
        details = exc.detail  # type: ignore

    extra = {"error_code": error_code}
    if details:
        extra["details"] = details

    logger.error(f"{message}: {str(exc)}", exc_info=True, extra=extra)
