"""Manual entrypoint for Arq Worker.

This module initializes and runs the Arq worker using global, absolute import paths
to ensure immediate fail-fast logging configuration on startup.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging

from arq.typing import WorkerSettingsType
from arq.worker import create_worker

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.logging_config import configure_logfire, setup_logging
from backend_v2.settings import get_settings
from backend_v2.utils.redis_patcher import _patch_arq_logging
from backend_v2.worker import WorkerSettings

__all__ = [
    "_HEALTH_RESPONSE_BYTES",
    "_handle_health_probe",
    "cli_entrypoint",
    "main",
]

# 1. Setup Logging immediately as the script starts (Fail-Fast logging)
setup_logging()
configure_logfire()
_patch_arq_logging()

logger = logging.getLogger(__name__)

_HEALTH_RESPONSE_BYTES: bytes = (
    b"HTTP/1.1 200 OK\r\n"
    b"Content-Type: application/json\r\n"
    b"Content-Length: 15\r\n"
    b"Connection: close\r\n\r\n"
    b'{"status":"ok"}'
)


async def _handle_health_probe(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
) -> None:
    """Handles Cloud Run TCP/HTTP startup and liveness health probe connections.

    Args:
        reader: Incoming asyncio stream reader for the probe socket.
        writer: Outgoing asyncio stream writer for the probe socket.
    """
    try:
        with contextlib.suppress(TimeoutError, OSError):
            await asyncio.wait_for(
                reader.read(1024),
                timeout=get_settings().http_client_timeout_seconds,
            )
            writer.write(_HEALTH_RESPONSE_BYTES)
            await writer.drain()
    finally:
        writer.close()


async def main() -> None:
    """Manual entrypoint for Arq Worker to avoid CLI loop issues.

    Executes the worker configuration async loop alongside a lightweight
    asyncio health probe listener and handles critical exit paths.

    Raises:
        AppException: If the worker or health listener fails to instantiate or run,
            conveying a SERVICE_UNAVAILABLE error_code.
        SystemExit: If the worker process receives a keyboard interrupt.
    """
    try:
        logger.info("Starting Arq Worker (Manual Script)...")

        # 2. Validate Settings (Implicitly via import/create_worker)
        settings = get_settings()
        worker_settings: WorkerSettingsType = WorkerSettings
        worker = create_worker(worker_settings)

        health_server = await asyncio.start_server(
            _handle_health_probe,
            host="0.0.0.0",
            port=settings.worker_health_port,
        )
        logger.info(
            "Worker health probe listener active on 0.0.0.0:%d",
            settings.worker_health_port,
        )
        async with health_server:
            await worker.async_run()
    except KeyboardInterrupt:
        logger.info("Worker stopped by user.")
        raise SystemExit(0) from None
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
    """CLI entrypoint wrapping main() execution with clean exit handling.

    Raises:
        AppException: If unhandled worker failure occurs outside main loop.
        SystemExit: Upon user interrupt or clean shutdown.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker process interrupted by user. Shutting down.")
        raise SystemExit(0) from None
    except SystemExit:
        raise
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
