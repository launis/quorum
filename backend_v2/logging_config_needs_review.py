"""Logging configuration module conforming to modern V2 standards."""

import json
import logging
import os
import re
import sys
from typing import Any

from backend_v2.context import get_execution_context, get_request_context
from backend_v2.exceptions import AppException, ErrorCodes

# Force UTF-8 on Windows to prevent Logfire/Rich box-drawing crashes (cp1252 to undefined)
if sys.platform == "win32":
    try:
        sys_stdout_reconfigure = getattr(sys.stdout, "reconfigure", None)
        if sys_stdout_reconfigure:
            sys_stdout_reconfigure(encoding="utf-8")
        sys_stderr_reconfigure = getattr(sys.stderr, "reconfigure", None)
        if sys_stderr_reconfigure:
            sys_stderr_reconfigure(encoding="utf-8")
    except Exception as e:
        print("Warning: Failed to set UTF-8 console encoding on Windows:", e, file=sys.stderr)

_LOGFIRE_CONFIGURED = False


class ContextFilter(logging.Filter):
    """Injects execution_id from contextvars into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter record to inject execution or request ID."""
        exec_id = get_execution_context()
        req_id = get_request_context()

        # Priority: Execution ID > Request ID > SYSTEM
        if exec_id:
            record.context_id = f"EXEC:{exec_id[:8]}"
            record.execution_id = exec_id
        elif req_id:
            record.context_id = f"REQ:{req_id[:8]}"
            record.execution_id = req_id
        else:
            record.context_id = "SYSTEM"
            record.execution_id = "SYSTEM"

        return True


class UvicornPollingFilter(logging.Filter):
    """Filters out repetitive 202 Accepted /render polling logs to reduce noise."""

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        if '"GET /api/v2/execution/executions/' in msg and "/render" in msg and '" 202' in msg:
            return False
        return True


def configure_logfire() -> None:
    """Configures Logfire for observability dynamically with deferred imports."""
    try:
        import logfire
    except ImportError:
        logging.getLogger(__name__).info("Logfire module not found. Cloud observability will be disabled.")
        return
    except Exception as e:
        logging.getLogger(__name__).error("Unexpected error importing logfire.", exc_info=True)
        raise AppException(
            message="Unexpected error importing logfire.",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        ) from e

    litellm_mod: Any = None
    try:
        import litellm

        litellm_mod = litellm
    except ImportError:
        pass

    global _LOGFIRE_CONFIGURED
    if _LOGFIRE_CONFIGURED:
        return
    _LOGFIRE_CONFIGURED = True

    if os.getenv("DISABLE_LOGFIRE", "").lower() == "true":
        logging.getLogger(__name__).info("Logfire disabled via DISABLE_LOGFIRE environment variable.")
        return

    try:
        os.environ.setdefault("LOGFIRE_BASE_URL", "https://api-eu.pydantic.dev/")
        os.environ.setdefault("LOGFIRE_SEND_TO_LOGFIRE", "true")
        os.environ["LOGFIRE_CONSOLE"] = "false"

        logfire.configure(send_to_logfire=True)
        logfire.instrument_pydantic()
        logfire.instrument_httpx()

        if litellm_mod is not None:
            litellm_mod.success_callback = ["logfire"]
            litellm_mod.failure_callback = ["logfire"]
    except Exception as e:
        msg = f"[LoggingConfig] Logfire validation failed: {e}. Observability disabled."
        logging.getLogger(__name__).warning(
            msg, exc_info=True, extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
        )


def setup_logging(log_level: int = logging.INFO) -> None:
    """Configures the root logger to write to a file and the console using settings dynamically."""
    from backend_v2.settings import get_settings

    configure_logfire()

    settings = get_settings()
    log_file_path = settings.log_file_path

    log_dir = os.path.dirname(log_file_path)
    if log_dir and not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception as e:
            raise AppException(
                message=f"FAILED TO CREATE LOG DIRECTORY {log_dir}: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            ) from e

    formatter: logging.Formatter
    if settings.use_json_logging:
        formatter = JSONFormatter(
            "%(asctime)s | %(levelname)s | [%(context_id)s] | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | [%(context_id)s] | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    context_filter = ContextFilter()

    file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(context_filter)
    file_handler.setLevel(log_level)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if root_logger.handlers:
        root_logger.handlers = []

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    try:
        import logfire

        if _LOGFIRE_CONFIGURED:
            logfire_handler = logfire.LogfireLoggingHandler()
            logfire_handler.setFormatter(formatter)
            logfire_handler.addFilter(context_filter)
            root_logger.addHandler(logfire_handler)
    except Exception as e:
        msg = f"[LoggingConfig] {ErrorCodes.CONFIGURATION_ERROR.name}: Failed to attach Logfire: {e}"
        logging.getLogger(__name__).warning(msg, exc_info=True)

    polling_filter = UvicornPollingFilter()
    for uvicorn_logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True
        uvicorn_logger.setLevel(logging.INFO)
        if uvicorn_logger_name == "uvicorn.access":
            uvicorn_logger.addFilter(polling_filter)

    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("arq").setLevel(logging.WARNING)
    logging.getLogger("opentelemetry.sdk.trace").setLevel(logging.ERROR)

    for llm_logger_name in ["LiteLLM", "LiteLLM Router"]:
        llm_logger = logging.getLogger(llm_logger_name)
        llm_logger.handlers = []
        llm_logger.propagate = True
        llm_logger.setLevel(logging.INFO)

    try:
        import litellm

        litellm.set_verbose = False
        litellm.suppress_debug_info = True
    except ImportError:
        logging.getLogger(__name__).info("LiteLLM module not found. Skipping LiteLLM debug configuration.")
    except Exception as e:
        logging.getLogger(__name__).error("Unexpected error configuring LiteLLM.", exc_info=True)
        raise AppException(
            message="Failed to configure LiteLLM logging.",
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
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

        if hasattr(record, "error_code"):
            log_record["error_code"] = record.error_code
        if hasattr(record, "details"):
            log_record["details"] = record.details

        return json.dumps(log_record)


def log_error(logger: logging.Logger, exc: Exception, message: str = "An error occurred") -> None:
    """Standardized error logging helper conforming to ErrorCodes."""
    error_code: Any = "INTERNAL_ERROR"
    details = None

    if hasattr(exc, "error_code"):
        error_code = exc.error_code
    elif hasattr(exc, "details"):
        pass
    else:
        class_name = exc.__class__.__name__
        error_code = re.sub(r"(?<!^)(?=[A-Z])", "_", class_name).upper()

    if hasattr(exc, "details"):
        details = exc.details
    elif hasattr(exc, "detail"):
        details = exc.detail

    extra = {"error_code": error_code.name if hasattr(error_code, "name") else str(error_code)}
    if details:
        extra["details"] = details

    logger.error("[App] %s: %s", message, str(exc), exc_info=True, extra=extra)
