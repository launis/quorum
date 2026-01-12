"""Logging configuration module."""

import logging
import os
import sys
from typing import Any

try:
    import logfire
except Exception:
    logfire: Any = None  # type: ignore

_LOGFIRE_CONFIGURED = False

from backend.context import get_execution_context


class ContextFilter(logging.Filter):
    """Injects execution_id from contextvars into log records."""

    def filter(self, record):
        """Filter record to inject execution ID."""
        exec_id = get_execution_context()
        record.execution_id = exec_id if exec_id else "SYSTEM"
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
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | [%(execution_id)s] | %(name)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Context Filter
    context_filter = ContextFilter()

    # 1. File Handler (UTF-8)
    file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(context_filter)  # Add Filter
    file_handler.setLevel(log_level)

    # 2. Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(context_filter)  # Add Filter
    console_handler.setLevel(log_level)

    # Configure Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates (e.g. uvicorn's default)
    if root_logger.handlers:
        root_logger.handlers = []

    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Set external libraries to warning to reduce noise
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    # LiteLLM is extremely verbose on DEBUG
    logging.getLogger("LiteLLM").setLevel(logging.WARNING)
    try:
        import litellm

        litellm.set_verbose = False
    except Exception:
        pass

    logging.info(f"Logging configured. Writing to: {log_file_path}")
