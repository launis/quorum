"""Manual entrypoint for Arq Worker."""

import asyncio
import logging
from typing import Any, cast

from arq.worker import create_worker

from backend.worker import WorkerSettings

# Force loop policy for Windows if needed, though asyncio.run usually handles it.
# On Windows, SelectorEventLoop is default in 3.14? Proactor?
# Arq expects to just work on the loop.


async def main():
    """Manual entrypoint for Arq Worker to avoid CLI loop issues."""
    try:
        worker = create_worker(cast(Any, WorkerSettings))
        logging.info("Starting Arq Worker (Manual Script)...")
        await worker.async_run()
    except KeyboardInterrupt:
        logging.info("Worker stopped by user.")
    except Exception as e:
        logging.error(f"Worker crashed: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
