"""Database Factory Module.

Centralizes the creation of Repository instances based on Application Settings.
Enforces the Async-First mandate and handles both TinyDB (Local/Mock) and Firestore
via the UnifiedWorkflowRepository and StorageDriver pattern.
"""

import logging

from backend_v2.database.firestore_driver import FirestoreDriver
from backend_v2.database.repository import AbstractWorkflowRepository, AppendOnlyRepository

# Drivers
from backend_v2.database.tinydb_driver import TinyDBDriver
from backend_v2.database.wrapper import AbstractDatabase, TinyDBClient
from backend_v2.settings import Settings, StorageBackend

logger = logging.getLogger(__name__)


async def get_repository(settings: Settings, db_client: AbstractDatabase | None = None) -> AbstractWorkflowRepository:
    """Factory function to instantiate the appropriate Async Workflow Repository.

    Args:
        settings: The application settings object containing 'active_backend'.
        db_client: Optional pre-initialized database client (e.g. for Tests/Dependency Injection).

    Returns:
        An instance of AppendOnlyRepository configured with the correct driver.

    Raises:
        ValueError: If an unknown storage backend is configured.
    """
    backend = settings.active_backend
    logger.info(f"[Factory] Initializing Unified Repository for Backend: {backend.value}")

    match backend:
        case StorageBackend.FIRESTORE:
            # Lazy import to avoid hard dependency on google-cloud-firestore if not used everywhere
            from google.cloud import firestore  # type: ignore

            # Credentials are implicitly handled by GOOGLE_APPLICATION_CREDENTIALS env var
            # set by the .bat files.
            # We use the AsyncClient directly for the driver
            client = firestore.AsyncClient()
            driver = FirestoreDriver(client)
            return AppendOnlyRepository(driver)

        case StorageBackend.MOCK | StorageBackend.LOCAL:
            # Both Mock and Local use TinyDB, just different paths or injected clients

            db_client_local: TinyDBClient

            if db_client and isinstance(db_client, TinyDBClient):
                db_client_local = db_client
            else:
                # Determine path based on mode
                if backend == StorageBackend.MOCK:
                    db_path = settings.mock_db_path
                    logger.info(f"[Factory] Using MOCK configuration. Path: {db_path}")
                else:
                    db_path = settings.prod_db_path
                    logger.info(f"[Factory] Using LOCAL configuration. Path: {db_path}")

                db_client_local = TinyDBClient(db_path)

            local_driver = TinyDBDriver(db_client_local)
            return AppendOnlyRepository(local_driver)

        case _:
            raise ValueError(f"Unknown storage backend: {backend}")
