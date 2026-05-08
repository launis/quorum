"""Database Factory Module.

Centralizes the creation of Repository instances based on Application Settings.
Enforces the Async-First mandate and handles both TinyDB (Local/Mock) and Firestore
via the UnifiedWorkflowRepository and StorageDriver pattern.
"""

import logging

from google.cloud import firestore  # type: ignore[attr-defined]

from backend_v2.database.driver import StorageDriver
from backend_v2.database.firestore_driver import FirestoreDriver

# Drivers
from backend_v2.database.tinydb_driver import TinyDBDriver
from backend_v2.database.wrapper import AbstractDatabase, TinyDBClient
from backend_v2.exceptions import ConfigurationError
from backend_v2.settings import Settings, StorageBackend

logger = logging.getLogger(__name__)


async def get_driver(settings: Settings, db_client: AbstractDatabase | None = None) -> StorageDriver:
    """Factory function to instantiate the appropriate Async Storage Driver.

    Args:
        settings: The application settings object containing 'active_backend'.
        db_client: Optional pre-initialized database client (e.g. for Tests/Dependency Injection).

    Returns:
        An instance of StorageDriver (TinyDB/Firestore).

    Raises:
        ValueError: If an unknown storage backend is configured.
    """
    backend = settings.active_backend
    logger.debug("[Factory] Initializing Storage Driver for Backend: %s", backend.value)

    match backend:
        case StorageBackend.FIRESTORE:
            # Credentials are implicitly handled by GOOGLE_APPLICATION_CREDENTIALS env var
            # set by the .bat files.
            # We use the AsyncClient directly for the driver
            client = firestore.AsyncClient()
            driver = FirestoreDriver(client)
            return driver

        case StorageBackend.LOCAL:
            # Local uses TinyDB
            db_client_local: TinyDBClient

            if db_client and isinstance(db_client, TinyDBClient):
                db_client_local = db_client
            else:
                db_path = settings.prod_db_path
                logger.debug("[Factory] Using LOCAL configuration. Path: %s", db_path)
                db_client_local = TinyDBClient(db_path)

            local_driver = TinyDBDriver(db_client_local)
            return local_driver

        case _:
            raise ConfigurationError(f"Unknown storage backend: {backend}")
