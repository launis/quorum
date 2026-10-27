"""PostgreSQL 19 Zero-ORM Connection Pool Manager & Binary JSONB Codec Infrastructure.

Encapsulates asyncpg pool lifecycle, @runtime_checkable driver protocols,
binary pydantic_core (0x01 wire header) JSONB codecs, explicit timeouts from settings.py,
and idempotent SQL migration execution.
"""

from __future__ import annotations

import importlib
import logging
from collections.abc import AsyncIterator, Callable, Sequence
from contextlib import asynccontextmanager
from pathlib import Path
from types import TracebackType
from typing import Protocol, Self, runtime_checkable
from urllib.parse import quote_plus

from fastapi import status
from pydantic_core import from_json, to_json

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.settings import Settings

logger = logging.getLogger(__name__)

_DEFAULT_MIGRATION_PATH: Path = Path(__file__).resolve().parent.parent / "migrations" / "001_pg19_uuidv7_schema.sql"
_JSONB_BINARY_VERSION_BYTE: int = 1
_JSONB_BINARY_HEADER: bytes = b"\x01"

__all__ = [
    "AsyncPgConnectionProtocol",
    "AsyncPgPoolProtocol",
    "AsyncPgRecordProtocol",
    "AsyncPgTransactionProtocol",
    "PostgresPoolManager",
    "decode_jsonb_binary",
    "encode_jsonb_binary",
    "init_connection",
]


@runtime_checkable
class AsyncPgRecordProtocol(Protocol):
    """Standalone structural protocol for asyncpg Record rows without Mapping inheritance."""

    def __getitem__(self, key: str) -> object:
        """Retrieve column value by column name.

        Args:
            key: Column identifier in the result row.

        Returns:
            Decoded column value.
        """
        ...

    def __contains__(self, key: object) -> bool:
        """Return whether column name exists in record.

        Args:
            key: Candidate column key to check.

        Returns:
            True if the column exists in the record, otherwise False.
        """
        ...


@runtime_checkable
class AsyncPgTransactionProtocol(Protocol):
    """Structural protocol for asyncpg transaction context managers."""

    async def start(self) -> None:
        """Begin the database transaction."""
        ...

    async def commit(self) -> None:
        """Commit the active database transaction."""
        ...

    async def rollback(self) -> None:
        """Roll back the active database transaction."""
        ...

    async def __aenter__(self) -> Self:
        """Enter the transaction context manager.

        Returns:
            Active transaction protocol instance.
        """
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the transaction context manager.

        Args:
            exc_type: Exception class if raised within the context block.
            exc_val: Exception instance if raised within the context block.
            exc_tb: Traceback object if raised within the context block.
        """
        ...


@runtime_checkable
class AsyncPgConnectionProtocol(Protocol):
    """Structural protocol for asyncpg connections."""

    async def execute(self, query: str, *args: object, timeout: float | None = None) -> str:
        """Execute a SQL statement and return command status tag.

        Args:
            query: SQL statement string to execute.
            *args: Positional query bind parameters.
            timeout: Optional execution timeout in seconds.

        Returns:
            PostgreSQL command completion status tag.
        """
        ...

    async def executemany(
        self,
        command: str,
        args: Sequence[Sequence[object]],
        *,
        timeout: float | None = None,
    ) -> None:
        """Execute a SQL statement across a batch of parameter sequences.

        Args:
            command: Parameterized SQL statement string.
            args: Sequence of positional parameter tuples.
            timeout: Optional execution timeout in seconds.
        """
        ...

    async def fetch(
        self,
        query: str,
        *args: object,
        timeout: float | None = None,
    ) -> Sequence[AsyncPgRecordProtocol]:
        """Execute a SQL query and return all matching records.

        Args:
            query: SQL query string to execute.
            *args: Positional query bind parameters.
            timeout: Optional execution timeout in seconds.

        Returns:
            Sequence of records conforming to AsyncPgRecordProtocol.
        """
        ...

    async def fetchrow(
        self,
        query: str,
        *args: object,
        timeout: float | None = None,
    ) -> AsyncPgRecordProtocol | None:
        """Execute a SQL query and return the first matching record or None.

        Args:
            query: SQL query string to execute.
            *args: Positional query bind parameters.
            timeout: Optional execution timeout in seconds.

        Returns:
            First matching record or None if no rows matched.
        """
        ...

    async def set_type_codec(
        self,
        typename: str,
        *,
        encoder: Callable[[object], bytes],
        decoder: Callable[[bytes | bytearray | memoryview], object],
        schema: str = "pg_catalog",
        format: str = "binary",
    ) -> None:
        """Register a custom binary wire codec for a PostgreSQL type.

        Args:
            typename: Target PostgreSQL data type name.
            encoder: Callable serializing Python values into wire bytes.
            decoder: Callable deserializing wire bytes into Python values.
            schema: PostgreSQL schema owning the type.
            format: Wire transfer format identifier.
        """
        ...

    def transaction(self, *, isolation: str = "repeatable_read") -> AsyncPgTransactionProtocol:
        """Create a transaction context with the specified isolation level.

        Args:
            isolation: PostgreSQL transaction isolation level name.

        Returns:
            Transaction context manager conforming to AsyncPgTransactionProtocol.
        """
        ...


@runtime_checkable
class AsyncPgPoolProtocol(Protocol):
    """Structural protocol for asyncpg connection pools."""

    async def acquire(self, *, timeout: float | None = None) -> AsyncPgConnectionProtocol:
        """Acquire a database connection from the pool.

        Args:
            timeout: Optional acquisition timeout in seconds.

        Returns:
            Acquired connection conforming to AsyncPgConnectionProtocol.
        """
        ...

    async def release(
        self,
        connection: AsyncPgConnectionProtocol,
        *,
        timeout: float | None = None,
    ) -> None:
        """Release a database connection back to the pool.

        Args:
            connection: Previously acquired database connection.
            timeout: Optional release timeout in seconds.
        """
        ...

    async def close(self) -> None:
        """Close all connections in the pool."""
        ...


@runtime_checkable
class _AsyncPgModuleProtocol(Protocol):
    """Structural protocol for lazily imported asyncpg module."""

    async def create_pool(
        self,
        dsn: str,
        *,
        min_size: int,
        max_size: int,
        command_timeout: float,
        timeout: float,
        init: Callable[[AsyncPgConnectionProtocol], object],
    ) -> AsyncPgPoolProtocol:
        """Create an asyncpg connection pool.

        Args:
            dsn: PostgreSQL connection URI.
            min_size: Minimum number of pooled connections.
            max_size: Maximum number of pooled connections.
            command_timeout: Default command execution timeout in seconds.
            timeout: Connection establishment timeout in seconds.
            init: Per-connection initialization callback registering codecs.

        Returns:
            Initialized connection pool conforming to AsyncPgPoolProtocol.
        """
        ...


# Frame binary pydantic_core JSONB payloads with PostgreSQL \x01 wire version byte
def encode_jsonb_binary(value: object) -> bytes:
    """Serialize a Python or Pydantic value into PostgreSQL binary JSONB wire format.

    Prepends PostgreSQL's mandatory 1-byte version header (0x01) to the UTF-8 JSON bytes
    generated by Rust pydantic_core.to_json.

    Args:
        value: Arbitrary serializable object or Pydantic model.

    Returns:
        Binary JSONB wire payload prefixed with the 0x01 version byte.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if JSON serialization fails.
    """
    try:
        json_bytes: bytes = to_json(value)
    except (TypeError, ValueError) as exc:
        msg = f"Failed to encode payload to binary JSONB: {exc}"
        logger.error(
            "[PostgresPool] %s: %s",
            ErrorCodes.STORAGE_ACCESS_FAILED.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        ) from exc
    return _JSONB_BINARY_HEADER + json_bytes


def decode_jsonb_binary(raw: bytes | bytearray | memoryview) -> object:
    """Deserialize PostgreSQL binary JSONB wire bytes via Rust pydantic_core.from_json.

    Verifies the 1-byte PostgreSQL JSONB wire format version header (0x01) fail-fast
    before passing the slice to pydantic_core.from_json.

    Args:
        raw: Raw binary JSONB buffer received from PostgreSQL.

    Returns:
        Decoded Python value ready for Pydantic model validation.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if the buffer is empty, has an unsupported
            JSONB version header, or contains malformed JSON.
    """
    view = memoryview(raw)
    if len(view) < 1:
        msg = "Unsupported or empty PostgreSQL binary JSONB wire header: buffer is empty."
        logger.error(
            "[PostgresPool] %s: %s",
            ErrorCodes.STORAGE_ACCESS_FAILED.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        )
    if view[0] != _JSONB_BINARY_VERSION_BYTE:
        msg = f"Unsupported PostgreSQL binary JSONB wire header: expected version 1, got {view[0]!r}."
        logger.error(
            "[PostgresPool] %s: %s",
            ErrorCodes.STORAGE_ACCESS_FAILED.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        )
    try:
        return from_json(bytes(view[1:]))
    except ValueError as exc:
        msg = f"Failed to decode PostgreSQL binary JSONB payload: {exc}"
        logger.error(
            "[PostgresPool] %s: %s",
            ErrorCodes.STORAGE_ACCESS_FAILED.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        ) from exc


async def init_connection(conn: AsyncPgConnectionProtocol) -> None:
    """Register binary pydantic_core JSONB codecs on a newly acquired asyncpg connection.

    Args:
        conn: Connection conforming to AsyncPgConnectionProtocol.

    Raises:
        AppException: With STORAGE_ACCESS_FAILED if codec registration fails.
    """
    try:
        await conn.set_type_codec(
            "jsonb",
            encoder=encode_jsonb_binary,
            decoder=decode_jsonb_binary,
            schema="pg_catalog",
            format="binary",
        )
    except Exception as exc:
        if isinstance(exc, AppException):
            raise
        msg = f"Failed to register binary JSONB codec on PostgreSQL connection: {exc}"
        logger.error(
            "[PostgresPool] %s: %s",
            ErrorCodes.STORAGE_ACCESS_FAILED.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
        ) from exc


def _import_asyncpg_module() -> object:
    """Lazily import the asyncpg driver module at connection time.

    Returns:
        Imported asyncpg module object.

    Raises:
        ModuleNotFoundError: If asyncpg is not installed in the active environment.
    """
    return importlib.import_module("asyncpg")


class PostgresPoolManager:
    """Manages the PostgreSQL 19 asyncpg connection pool, binary codecs, and DDL migrations.

    Attributes:
        settings: Application Settings instance providing pool bounds and timeouts.
    """

    def __init__(
        self,
        settings: Settings,
        pool: AsyncPgPoolProtocol | None = None,
        migration_sql_path: Path | None = None,
    ) -> None:
        """Initialize the PostgreSQL pool manager.

        Args:
            settings: Central Settings instance.
            pool: Optional pre-configured pool conforming to AsyncPgPoolProtocol.
            migration_sql_path: Optional override path to the SQL DDL schema file.
        """
        self.settings: Settings = settings
        self._pool: AsyncPgPoolProtocol | None = pool
        self._migration_sql_path: Path = (
            migration_sql_path if migration_sql_path is not None else _DEFAULT_MIGRATION_PATH
        )

    def resolve_dsn(self) -> str:
        """Build the PostgreSQL connection DSN from environment-injected settings.

        Returns:
            Connection DSN string.
        """
        if self.settings.postgres_dsn is not None and self.settings.postgres_dsn.strip():
            return self.settings.postgres_dsn.strip()

        user_encoded = quote_plus(self.settings.postgres_user)
        db_encoded = quote_plus(self.settings.postgres_db)
        host = self.settings.postgres_host
        port = self.settings.postgres_port

        if self.settings.postgres_password is not None and self.settings.postgres_password:
            password_encoded = quote_plus(self.settings.postgres_password)
            return f"postgresql://{user_encoded}:{password_encoded}@{host}:{port}/{db_encoded}"
        return f"postgresql://{user_encoded}@{host}:{port}/{db_encoded}"

    async def connect(self) -> AsyncPgPoolProtocol:
        """Initialize or return the active asyncpg connection pool.

        Returns:
            Active pool conforming to AsyncPgPoolProtocol.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if asyncpg is unavailable or connection fails.
        """
        if self._pool is not None:
            return self._pool

        dsn = self.resolve_dsn()
        timeout_sec = self.settings.postgres_command_timeout_seconds
        try:
            raw_module: object = _import_asyncpg_module()
            if not isinstance(raw_module, _AsyncPgModuleProtocol):
                msg = "Imported asyncpg module does not conform to _AsyncPgModuleProtocol."
                logger.error(
                    "[PostgresPool] %s: %s",
                    ErrorCodes.STORAGE_ACCESS_FAILED.name,
                    msg,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                )
            self._pool = await raw_module.create_pool(
                dsn,
                min_size=self.settings.postgres_min_pool_size,
                max_size=self.settings.postgres_max_pool_size,
                command_timeout=timeout_sec,
                timeout=timeout_sec,
                init=init_connection,
            )
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to initialize PostgreSQL 19 connection pool: {exc}"
            logger.error(
                "[PostgresPool] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc
        return self._pool

    @asynccontextmanager
    async def acquire_connection(self) -> AsyncIterator[AsyncPgConnectionProtocol]:
        """Acquire a codec-initialized connection with bounded timeout and guaranteed release.

        Yields:
            Connection conforming to AsyncPgConnectionProtocol.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if pool acquisition or codec registration fails.
        """
        pool = await self.connect()
        timeout_sec = self.settings.postgres_command_timeout_seconds
        try:
            conn = await pool.acquire(timeout=timeout_sec)
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to acquire connection from PostgreSQL pool within {timeout_sec}s: {exc}"
            logger.error(
                "[PostgresPool] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc

        try:
            await init_connection(conn)
            yield conn
        finally:
            await pool.release(conn, timeout=timeout_sec)

    async def apply_migrations(self) -> None:
        """Execute the idempotent PostgreSQL 19 UUIDv7 DDL migration script.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if the migration file is missing or execution fails.
        """
        if not self._migration_sql_path.exists():
            msg = f"PostgreSQL DDL migration file not found: {self._migration_sql_path}"
            logger.error(
                "[PostgresPool] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )

        ddl_sql = self._migration_sql_path.read_text(encoding="utf-8")
        timeout_sec = self.settings.postgres_command_timeout_seconds
        async with self.acquire_connection() as conn:
            try:
                await conn.execute(ddl_sql, timeout=timeout_sec)
            except Exception as exc:
                if isinstance(exc, AppException):
                    raise
                msg = f"Failed to apply PostgreSQL 19 DDL migration: {exc}"
                logger.error(
                    "[PostgresPool] %s: %s",
                    ErrorCodes.STORAGE_ACCESS_FAILED.name,
                    msg,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                )
                raise AppException(
                    message=msg,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
                ) from exc

    async def close(self) -> None:
        """Close the active connection pool if initialized.

        Raises:
            AppException: With STORAGE_ACCESS_FAILED if closing the pool fails.
        """
        if self._pool is None:
            return
        pool = self._pool
        self._pool = None
        try:
            await pool.close()
        except Exception as exc:
            if isinstance(exc, AppException):
                raise
            msg = f"Failed to close PostgreSQL connection pool: {exc}"
            logger.error(
                "[PostgresPool] %s: %s",
                ErrorCodes.STORAGE_ACCESS_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value},
            ) from exc
