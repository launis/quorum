"""PostgreSQL 19 Post-Wave Atomic Unit of Work (PostgresUnitOfWork).

Implements QuorumUnitOfWork over asyncpg repeatable_read transactions with
PEP 765 pure finally connection cleanup and RFC 7807 structured error translation.
"""

from __future__ import annotations

import logging
from types import TracebackType
from typing import Self

from fastapi import status

from backend_v2.database.interfaces import (
    CausalReasoningPort,
    EntityPersistencePort,
    GraphMutationPort,
    TopologyResolutionPort,
)
from backend_v2.database.postgres.entity_adapter import PostgresEntityAdapter
from backend_v2.database.postgres.graph_adapter import PostgresGraphAdapter
from backend_v2.database.postgres.pool import (
    AsyncPgConnectionProtocol,
    AsyncPgPoolProtocol,
    AsyncPgTransactionProtocol,
    PostgresPoolManager,
    init_connection,
)
from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

__all__ = [
    "PostgresUnitOfWork",
]


class PostgresUnitOfWork:
    """Post-Wave Atomic Unit of Work coordinating PostgreSQL 19 graph and entity adapters.

    Acquires an asyncpg connection strictly upon entering the Unit of Work context,
    opens a repeatable_read transaction, binds GraphMutationPort, TopologyResolutionPort,
    CausalReasoningPort, and EntityPersistencePort adapters, and deterministically
    releases the connection back to the pool in the finally block.

    Attributes:
        graph: Active GraphMutationPort bound to the current transaction.
        topology: Active TopologyResolutionPort bound to the current transaction.
        reasoning: Active CausalReasoningPort bound to the current transaction.
        entities: Active EntityPersistencePort bound to the current transaction.
    """

    graph: GraphMutationPort
    topology: TopologyResolutionPort
    reasoning: CausalReasoningPort
    entities: EntityPersistencePort

    def __init__(self, pool_manager: PostgresPoolManager) -> None:
        """Initialize the PostgreSQL Unit of Work with a pool manager.

        Args:
            pool_manager: Configured PostgresPoolManager managing asyncpg connections.
        """
        self._pool_manager: PostgresPoolManager = pool_manager
        self._pool: AsyncPgPoolProtocol | None = None
        self._conn: AsyncPgConnectionProtocol | None = None
        self._tx: AsyncPgTransactionProtocol | None = None
        self._finalized: bool = False

    async def __aenter__(self) -> Self:
        """Acquire a connection, start a repeatable_read transaction, and bind CQRS ports.

        Returns:
            Initialized PostgresUnitOfWork instance.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if connection acquisition or transaction start fails.
        """
        timeout_sec = self._pool_manager.settings.postgres_command_timeout_seconds
        pool = await self._pool_manager.connect()
        self._pool = pool

        try:
            conn = await pool.acquire(timeout=timeout_sec)
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to acquire PostgreSQL connection for Unit of Work: {exc}"
            logger.error(
                "[PostgresUnitOfWork] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

        self._conn = conn
        try:
            await init_connection(conn)
            tx = conn.transaction(isolation="repeatable_read")
            await tx.start()
            self._tx = tx
        except Exception as exc:
            await pool.release(conn, timeout=timeout_sec)
            self._conn = None
            self._tx = None
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to start repeatable_read transaction in PostgresUnitOfWork: {exc}"
            logger.error(
                "[PostgresUnitOfWork] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

        self._finalized = False
        graph_adapter = PostgresGraphAdapter(
            connection=conn,
            command_timeout_seconds=timeout_sec,
        )
        entity_adapter = PostgresEntityAdapter(
            connection=conn,
            command_timeout_seconds=timeout_sec,
        )
        self.graph = graph_adapter
        self.topology = graph_adapter
        self.reasoning = graph_adapter
        self.entities = entity_adapter
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Finalize the repeatable_read transaction and release the connection in a pure finally block.

        Args:
            exc_type: Exception class if an error occurred inside the context block.
            exc_val: Exception instance if an error occurred inside the context block.
            exc_tb: Traceback if an error occurred inside the context block.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if commit or rollback fails.
        """
        timeout_sec = self._pool_manager.settings.postgres_command_timeout_seconds
        try:
            if exc_type is not None:
                if not self._finalized:
                    await self.rollback()
            elif not self._finalized:
                await self.commit()
        finally:
            conn = self._conn
            pool = self._pool
            self._conn = None
            self._tx = None
            self._pool = None
            if conn is not None and pool is not None:
                await pool.release(conn, timeout=timeout_sec)

    async def commit(self) -> None:
        """Commit the active repeatable_read transaction.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if no transaction is active or commit fails.
        """
        if self._tx is None:
            msg = "Cannot commit PostgresUnitOfWork: no active transaction."
            logger.error(
                "[PostgresUnitOfWork] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )
        if self._finalized:
            return
        try:
            await self._tx.commit()
            self._finalized = True
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to commit PostgresUnitOfWork transaction: {exc}"
            logger.error(
                "[PostgresUnitOfWork] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

    async def rollback(self) -> None:
        """Roll back the active repeatable_read transaction.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if no transaction is active or rollback fails.
        """
        if self._tx is None:
            msg = "Cannot roll back PostgresUnitOfWork: no active transaction."
            logger.error(
                "[PostgresUnitOfWork] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )
        if self._finalized:
            return
        try:
            await self._tx.rollback()
            self._finalized = True
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to roll back PostgresUnitOfWork transaction: {exc}"
            logger.error(
                "[PostgresUnitOfWork] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc
