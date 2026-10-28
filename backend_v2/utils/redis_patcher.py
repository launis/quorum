"""Redis patching utilities."""

import contextvars
import logging
from typing import Any, cast

import arq.connections
import arq.worker
from arq.connections import ArqRedis
from fakeredis import FakeServer
from fakeredis.aioredis import FakeRedis
from fastapi import status
from redis.asyncio.connection import ConnectionPool

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.settings import get_settings

__all__ = [
    "ASYNC_ACCUMULATOR_LUA",
    "ArqCompatibleFakeRedis",
    "MockRetry",
    "get_patched_fakeredis_pool",
]

logger = logging.getLogger(__name__)

ASYNC_ACCUMULATOR_LUA = """
-- Lua script for atomic state accumulation
-- KEYS[1] = Hash key (e.g., 'exec:123:step:abc')
-- ARGV[1] = total chunks
-- ARGV[2] = chunk state payload (JSON string)
-- ARGV[3] = chunk index

local hkey = KEYS[1]
local total_chunks = tonumber(ARGV[1])
local payload = ARGV[2]
local index = ARGV[3]

-- Save the chunk payload
redis.call('HSET', hkey, 'chunk_' .. index, payload)

-- Increment completed counter
local completed = redis.call('HINCRBY', hkey, 'completed', 1)

if completed == total_chunks then
    -- Return 1 to indicate all chunks are done
    return 1
else
    return 0
end
"""

_last_response_var: contextvars.ContextVar[Any] = contextvars.ContextVar("fake_redis_last_response", default=None)


class MockRetry:
    """Mock retry handler for Arq compatibility."""

    async def call_with_retry(self, func: Any, on_error: Any) -> Any:
        """Executes the function directly without retries.

        Args:
            func: The asynchronous function to execute.
            on_error: The error handler function (unused in mock).

        Returns:
            The result of the function execution.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if func is not callable.
        """
        if not callable(func):
            msg = "Target function for MockRetry.call_with_retry must be callable."
            logger.error(
                "[RedisPatcher] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return await func()


class ArqCompatibleFakeRedis(FakeRedis):
    """Strongly typed FakeRedis subclass providing Arq connection pool compatibility.

    Attributes:
        retry: Mock retry handler for Arq execution.
        connection_kwargs: Connection parameters dictionary resolved from Settings SSOT.
    """

    connection_kwargs: dict[str, str | int]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes the fake redis instance with Arq compatibility attributes.

        Args:
            *args: Positional arguments for FakeRedis.
            **kwargs: Keyword arguments for FakeRedis.
        """
        super().__init__(*args, **kwargs)
        settings = get_settings()
        self.retry = MockRetry()
        self.connection_kwargs = {"host": settings.redis_host, "port": settings.redis_port}

    async def get_connection(self) -> Any:
        """Returns self as the active connection.

        Returns:
            Self instance.
        """
        return self

    async def release(self, conn: Any) -> None:
        """Releases the connection (no-op for fake redis).

        Args:
            conn: Connection to release.

        Returns:
            None
        """
        _ = conn
        return None

    def pack_commands(self, cmds: Any) -> Any:
        """Packs commands for pipeline execution.

        Args:
            cmds: Command structure to pack.

        Returns:
            The packed commands.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if cmds is empty or None.
        """
        if not cmds:
            msg = "Commands payload for pack_commands cannot be empty."
            logger.error(
                "[RedisPatcher] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return cmds

    async def send_packed_command(self, cmds: Any) -> None:
        """Sends packed commands (no-op for fake redis).

        Args:
            cmds: Packed commands to send.

        Returns:
            None
        """
        _ = cmds
        return None

    async def send_command(self, *args: Any, **kwargs: Any) -> Any:
        """Executes a command and stores the response in context variable.

        Args:
            *args: Positional command arguments.
            **kwargs: Keyword command arguments.

        Returns:
            None

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if no command arguments are provided.
        """
        if not args:
            msg = "Redis command arguments for send_command cannot be empty."
            logger.error(
                "[RedisPatcher] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                exc_info=True,
            )
            raise AppException(
                message=msg,
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        cmd: Any = self.execute_command
        res = await cmd(*args, **kwargs)
        _last_response_var.set(res)

    async def read_response(self) -> Any:
        """Reads the last execution response from context variable.

        Returns:
            The last command response.
        """
        return _last_response_var.get()


def _patch_arq_logging() -> None:
    """Patches Arq logging to prevent crashes with FakeRedis."""

    async def _no_op_log(*args: Any, **kwargs: Any) -> None:
        _ = (args, kwargs)
        return None

    arq.connections.log_redis_info = _no_op_log
    worker_module: Any = arq.worker
    worker_module.log_redis_info = _no_op_log


def get_patched_fakeredis_pool() -> ArqRedis:
    """Creates an ArqCompatibleFakeRedis instance compatible with Arq.

    Arq (0.26+) expects specific methods on the connection pool that FakeRedis
    doesn't natively provide or behaves differently with. This function provides
    a strongly typed subclass instance to ensure Arq runs smoothly in in-memory mode.

    Returns:
        An Arq-compatible wrapper around an ArqCompatibleFakeRedis instance.
    """
    fake_redis = ArqCompatibleFakeRedis(server=FakeServer())

    _patch_arq_logging()

    arq_redis = ArqRedis(cast(ConnectionPool, fake_redis))
    logger.info("In-Memory Redis pool (Patched) initialized.")

    return arq_redis
