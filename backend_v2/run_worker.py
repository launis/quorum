"""Manual entrypoint for Arq Worker."""

import asyncio
import logging
import sys
from typing import Any, cast

from arq.worker import create_worker

from backend_v2.logging_config import configure_logfire, setup_logging
from backend_v2.worker import WorkerSettings

# Force loop policy for Windows if needed, though asyncio.run usually handles it.
# On Windows, SelectorEventLoop is default in 3.14? Proactor?
# Arq expects to just work on the loop.


async def main():
    """Manual entrypoint for Arq Worker to avoid CLI loop issues."""
    try:
        # 1. Setup Logging (FAIL FAST if config missing)
        setup_logging()
        configure_logfire()

        logging.info("Starting Arq Worker (Manual Script)...")

        # Cast to Any to satisfy type checker if WorkerSettings structure is strict
        # 2. Validate Settings (Implicitly via import/create_worker)
        worker = create_worker(cast(Any, WorkerSettings))

        await worker.async_run()
    except KeyboardInterrupt:
        logging.info("Worker stopped by user.")
    except Exception as e:
        # 3. Fail Fast with structured error
        logging.critical(f"Worker startup failed: {e}", exc_info=True)
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
        print(f"CRITICAL: Worker crashed outside main loop: {e}")
        sys.exit(1)
