"""Manual entrypoint for Arq Worker."""

import asyncio
import logging
import sys
from typing import Any, cast

from arq.worker import create_worker

from backend_v2.exceptions import ErrorCodes
from backend_v2.logging_config import configure_logfire, setup_logging

# 1. Setup Logging immediately as the script starts (Fail-Fast logging)
setup_logging()
configure_logfire()

try:
    # 2. Lazy import the worker settings so that if any module fails to compile,
    # it gets caught and written to the newly configured file log!
    from backend_v2.worker import WorkerSettings
except Exception as e:
    logging.critical(f"[Worker] {ErrorCodes.INTERNAL_SERVER_ERROR.name}: Failed to import worker module (Crash on start): {e}", exc_info=True)
    sys.exit(1)

# Force loop policy for Windows if needed, though asyncio.run usually handles it.
# On Windows, SelectorEventLoop is default in 3.14? Proactor?
# Arq expects to just work on the loop.


async def main():
    """Manual entrypoint for Arq Worker to avoid CLI loop issues."""
    try:
        logging.info("Starting Arq Worker (Manual Script)...")

        # Cast to Any to satisfy type checker if WorkerSettings structure is strict
        # 2. Validate Settings (Implicitly via import/create_worker)
        worker = create_worker(cast(Any, WorkerSettings))

        await worker.async_run()
    except KeyboardInterrupt:
        logging.info("Worker stopped by user.")
        sys.exit(0)
    except Exception as e:
        # 3. Fail Fast with structured error
        logging.critical(f"[Worker] {ErrorCodes.SERVICE_UNAVAILABLE.name}: Worker startup failed: {e}", exc_info=True)
        # Re-raise as SystemExit to ensure non-zero exit code
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except SystemExit as e:
        sys.exit(e.code)
    except Exception as e:
        print(f"CRITICAL [Worker] {ErrorCodes.UNKNOWN_ERROR.name}: Worker crashed outside main loop: {e}")
        sys.exit(1)
