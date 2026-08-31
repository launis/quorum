from __future__ import annotations

"""Manual entrypoint for Arq Worker.

This module initializes and runs the Arq worker using global, absolute import paths
to ensure immediate fail-fast logging configuration on startup.
"""

import asyncio
import logging
import sys
from typing import Any  # noqa: F401

from arq.typing import WorkerSettingsType
from arq.worker import create_worker

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.logging_config import configure_logfire, setup_logging
from backend_v2.worker import WorkerSettings

# 1. Setup Logging immediately as the script starts (Fail-Fast logging)
setup_logging()
configure_logfire()

logger = logging.getLogger(__name__)


async def main() -> None:
    """Manual entrypoint for Arq Worker to avoid CLI loop issues.

    Executes the worker configuration async loop and handles critical exit paths.

    Raises:
        AppException: If the worker fails to instantiate or run, conveying a
            SERVICE_UNAVAILABLE error_code.
    """
    try:
        logger.info("Starting Arq Worker (Manual Script)...")

        # 2. Validate Settings (Implicitly via import/create_worker)
        worker_settings: WorkerSettingsType = WorkerSettings
        worker = create_worker(worker_settings)

        await worker.async_run()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")
        sys.exit(0)
    except Exception as e:
        # 3. Fail Fast with structured error
        msg = f"[Worker] Worker startup failed: {e}"
        logger.critical(
            "[Worker] Worker startup failed: %s",
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
        )
        raise AppException(
            message=msg,
            status_code=503,
            details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
        ) from e


def cli_entrypoint() -> None:
    """CLI entrypoint wrapping main() execution with clean exit handling."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker process interrupted by user. Shutting down.")
        sys.exit(0)
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        logger.critical(
            "Worker crashed outside main loop: %s",
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.UNKNOWN_ERROR.value},
        )
        raise AppException(
            message=f"Worker crashed outside main loop: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.UNKNOWN_ERROR.value},
        ) from e


if __name__ == "__main__":  # pragma: no cover
    cli_entrypoint()
