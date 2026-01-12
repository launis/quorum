"""Database Factory Module.

Centralizes the creation of Repository instances based on Application Settings.
Enforces the Async-First mandate and handles both TinyDB (Local/Mock) and Firestore.
"""

import logging

from backend.database.firestore_repo import FirestoreWorkflowRepository
from backend.database.repository import AbstractWorkflowRepository, TinyDBRepository
from backend.database.wrapper import TinyDBClient
from backend.settings import Settings, StorageBackend

logger = logging.getLogger(__name__)


async def get_repository(settings: Settings) -> AbstractWorkflowRepository:
    """Factory function to instantiate the appropriate Async Workflow Repository.

    Args:
        settings: The application settings object containing 'active_backend'.

    Returns:
        An instance of AbstractWorkflowRepository (TinyDBRepository or FirestoreWorkflowRepository).

    Raises:
        ValueError: If an unknown storage backend is configured.
    """
    backend = settings.active_backend
    logger.info(f"[Factory] Initializing Repository for Backend: {backend.value}")

    match backend:
        case StorageBackend.FIRESTORE:
            # Lazy import to avoid hard dependency on google-cloud-firestore if not used everywhere
            from google.cloud import firestore

            # Credentials are implicitly handled by GOOGLE_APPLICATION_CREDENTIALS env var
            # set by the .bat files.
            client = firestore.AsyncClient()
            return FirestoreWorkflowRepository(client)

        case StorageBackend.MOCK:
            # Mock DB Path: backend/database/db_mock.json
            # Strictly usage settings.mock_db_path as source of truth.
            db_path = settings.mock_db_path
            logger.info(f"[Factory] Using MOCK configuration. Path: {db_path}")
            client = TinyDBClient(db_path)
            return TinyDBRepository(client)

        case StorageBackend.LOCAL:
            # Prod Local Path: data/db.json
            # Strictly usage settings.prod_db_path as source of truth.
            db_path = settings.prod_db_path
            logger.info(f"[Factory] Using LOCAL configuration. Path: {db_path}")
            client = TinyDBClient(db_path)
            return TinyDBRepository(client)

        case _:
            raise ValueError(f"Unknown storage backend: {backend}")
