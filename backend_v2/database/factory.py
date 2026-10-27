"""Database Factory Module.

Centralizes the creation of Repository drivers and PostgreSQL 19 QuorumUnitOfWork
instances based on Application Settings.
"""

import logging

from google.cloud import firestore

from backend_v2.database.driver import StorageDriver
from backend_v2.database.firestore_driver import FirestoreDriver
from backend_v2.database.interfaces import QuorumUnitOfWork
from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.database.postgres.uow import PostgresUnitOfWork

# Drivers
from backend_v2.database.tinydb_driver import TinyDBDriver
from backend_v2.database.wrapper import AbstractDatabase, TinyDBClient
from backend_v2.exceptions import ConfigurationError, ErrorCodes
from backend_v2.settings import Settings, StorageBackend

logger = logging.getLogger(__name__)

__all__ = [
    "create_unit_of_work",
    "get_driver",
]


async def get_driver(settings: Settings, db_client: AbstractDatabase | None = None) -> StorageDriver:
    """Instantiate the appropriate Async Storage Driver for document-store backends.

    Args:
        settings: Application settings object containing 'active_backend'.
        db_client: Optional pre-initialized database client for testing or dependency injection.

    Returns:
        An initialized StorageDriver instance (TinyDBDriver or FirestoreDriver).

    Raises:
        ConfigurationError: If POSTGRES (which requires create_unit_of_work) or an unknown
            storage backend is configured.
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

        case StorageBackend.POSTGRES:
            msg = (
                "StorageBackend.POSTGRES uses Zero-ORM QuorumUnitOfWork via create_unit_of_work(); "
                "legacy document StorageDriver is disabled under Clean-Slate Cutover."
            )
            logger.error(
                "[Factory] %s: %s",
                ErrorCodes.CONFIGURATION_ERROR.name,
                msg,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
            raise ConfigurationError(msg)

        case _:
            msg = f"Unknown storage backend: {backend}"
            logger.error(
                "[Factory] %s: %s",
                ErrorCodes.CONFIGURATION_ERROR.name,
                msg,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )
            raise ConfigurationError(msg)


def create_unit_of_work(
    settings: Settings,
    pool_manager: PostgresPoolManager | None = None,
) -> QuorumUnitOfWork:
    """Instantiate a PostgreSQL 19 Post-Wave Atomic QuorumUnitOfWork.

    Args:
        settings: Application Settings instance configured with StorageBackend.POSTGRES.
        pool_manager: Optional pre-initialized PostgresPoolManager instance.

    Returns:
        Configured PostgresUnitOfWork conforming to QuorumUnitOfWork.

    Raises:
        ConfigurationError: If settings.active_backend is not StorageBackend.POSTGRES.
    """
    backend = settings.active_backend
    if backend != StorageBackend.POSTGRES:
        msg = f"create_unit_of_work requires StorageBackend.POSTGRES, but active_backend is '{backend.value}'."
        logger.error(
            "[Factory] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
        raise ConfigurationError(msg)

    resolved_pool_manager: PostgresPoolManager
    if pool_manager is not None:
        resolved_pool_manager = pool_manager
    else:
        resolved_pool_manager = PostgresPoolManager(settings=settings)
    return PostgresUnitOfWork(pool_manager=resolved_pool_manager)
