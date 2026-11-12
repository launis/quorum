"""Database Factory Module.

Centralizes the creation of PostgreSQL 19 PostgresPoolManager and QuorumUnitOfWork
instances based on Application Settings.
"""

from __future__ import annotations

import asyncio
import logging

from backend_v2.database.interfaces import QuorumUnitOfWork, register_default_uow_factory
from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.database.postgres.uow import PostgresUnitOfWork
from backend_v2.exceptions import ConfigurationError, ErrorCodes
from backend_v2.settings import Settings, StorageBackend, get_settings

logger = logging.getLogger(__name__)

_SHARED_POOL_MANAGER: PostgresPoolManager | None = None
_POOL_MANAGER_LOCK: asyncio.Lock = asyncio.Lock()

__all__ = [
    "close_shared_pool_manager",
    "create_unit_of_work",
    "get_shared_pool_manager",
]


def get_shared_pool_manager(settings: Settings | None = None) -> PostgresPoolManager:
    """Return the shared PostgresPoolManager singleton, creating it if uninitialized.

    Args:
        settings: Application Settings instance configured with StorageBackend.POSTGRES.

    Returns:
        Shared PostgresPoolManager singleton instance.

    Raises:
        ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if active_backend
            is not StorageBackend.POSTGRES.
    """
    global _SHARED_POOL_MANAGER
    resolved_settings = settings if settings is not None else get_settings()
    backend = resolved_settings.active_backend
    if backend != StorageBackend.POSTGRES:
        msg = f"get_shared_pool_manager requires StorageBackend.POSTGRES, but active_backend is '{backend.value}'."
        logger.error(
            "[Factory] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            exc_info=True,
        )
        raise ConfigurationError(msg)

    if _SHARED_POOL_MANAGER is None:
        _SHARED_POOL_MANAGER = PostgresPoolManager(settings=resolved_settings)
    return _SHARED_POOL_MANAGER


async def close_shared_pool_manager() -> None:
    """Close and reset the shared PostgresPoolManager singleton if initialized.

    Raises:
        AppException: With ErrorCodes.STORAGE_ACCESS_FAILED if closing the underlying pool fails.
    """
    global _SHARED_POOL_MANAGER
    async with _POOL_MANAGER_LOCK:
        manager = _SHARED_POOL_MANAGER
        _SHARED_POOL_MANAGER = None

    if manager is not None:
        await manager.close()


def create_unit_of_work(
    settings: Settings | None = None,
    pool_manager: PostgresPoolManager | None = None,
) -> QuorumUnitOfWork:
    """Instantiate a PostgreSQL 19 Post-Wave Atomic QuorumUnitOfWork.

    Args:
        settings: Application Settings instance configured with StorageBackend.POSTGRES.
        pool_manager: Optional pre-initialized PostgresPoolManager instance.

    Returns:
        Configured PostgresUnitOfWork conforming to QuorumUnitOfWork.

    Raises:
        ConfigurationError: With ErrorCodes.CONFIGURATION_ERROR if settings.active_backend
            is not StorageBackend.POSTGRES.
    """
    resolved_settings = settings if settings is not None else get_settings()
    backend = resolved_settings.active_backend
    if backend != StorageBackend.POSTGRES:
        msg = f"create_unit_of_work requires StorageBackend.POSTGRES, but active_backend is '{backend.value}'."
        logger.error(
            "[Factory] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            exc_info=True,
        )
        raise ConfigurationError(msg)

    resolved_pool_manager: PostgresPoolManager
    if pool_manager is not None:
        resolved_pool_manager = pool_manager
    else:
        resolved_pool_manager = get_shared_pool_manager(resolved_settings)
    return PostgresUnitOfWork(pool_manager=resolved_pool_manager)


register_default_uow_factory(create_unit_of_work)
