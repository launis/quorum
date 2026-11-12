"""Base repository coordinating UnitOfWorkFactory and EntityPersistencePort sessions."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from backend_v2.database.interfaces import (
    EntityPersistencePort,
    UnitOfWorkFactory,
    get_registered_uow_factory,
    open_uow_session,
)
from backend_v2.exceptions import ConfigurationError, ErrorCodes

logger = logging.getLogger(__name__)

__all__ = ["BaseRepository"]


class BaseRepository:
    """Base repository providing context-propagated EntityPersistencePort session acquisition."""

    _uow_factory: UnitOfWorkFactory | None

    def __init__(self, uow_factory: UnitOfWorkFactory | None = None) -> None:
        """Initialize the repository with an optional explicit UnitOfWorkFactory.

        Args:
            uow_factory: Optional zero-argument callable returning a QuorumUnitOfWork.
                Falls back to the process-registered UnitOfWorkFactory when omitted.
        """
        self._uow_factory = uow_factory

    def _resolve_uow_factory(self) -> UnitOfWorkFactory | None:
        """Resolve the configured or process-registered UnitOfWorkFactory.

        Returns:
            Callable UnitOfWorkFactory if available, otherwise None.
        """
        if self._uow_factory is not None:
            return self._uow_factory
        return get_registered_uow_factory()

    @asynccontextmanager
    async def _acquire_entities(self) -> AsyncIterator[EntityPersistencePort]:
        """Enter or reuse the active QuorumUnitOfWork session and yield its EntityPersistencePort.

        Yields:
            Active EntityPersistencePort bound to the current transaction scope.

        Raises:
            ConfigurationError: With CONFIGURATION_ERROR if no UnitOfWorkFactory is registered.
        """
        async with open_uow_session(self._resolve_uow_factory()) as uow:
            if uow is None:
                msg = f"QuorumUnitOfWork factory is not configured for {type(self).__name__}."
                logger.error(
                    "[BaseRepository] %s: %s",
                    ErrorCodes.CONFIGURATION_ERROR.name,
                    msg,
                    extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )
                raise ConfigurationError(message=msg)
            yield uow.entities
