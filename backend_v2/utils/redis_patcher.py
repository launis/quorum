"""Redis patching utilities."""

import contextvars
import logging
from typing import Any

import arq.connections
import arq.worker
from arq.connections import ArqRedis
from fakeredis.aioredis import FakeRedis

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
        """
        return await func()


class ArqCompatibleFakeRedis(FakeRedis):
    """Strongly typed FakeRedis subclass providing Arq connection pool compatibility.

    Attributes:
        retry: Mock retry handler for Arq execution.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initializes the fake redis instance with Arq compatibility attributes.

        Args:
            *args: Positional arguments for FakeRedis.
            **kwargs: Keyword arguments for FakeRedis.
        """
        super().__init__(*args, **kwargs)
        self.retry = MockRetry()

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
        pass

    def pack_commands(self, cmds: Any) -> Any:
        """Packs commands for pipeline execution.

        Args:
            cmds: Command structure to pack.

        Returns:
            The packed commands.
        """
        return cmds

    async def send_packed_command(self, cmds: Any) -> None:
        """Sends packed commands (no-op for fake redis).

        Args:
            cmds: Packed commands to send.

        Returns:
            None
        """
        pass

    async def send_command(self, *args: Any, **kwargs: Any) -> Any:
        """Executes a command and stores the response in context variable.

        Args:
            *args: Positional command arguments.
            **kwargs: Keyword command arguments.

        Returns:
            None
        """
        res = await self.execute_command(*args, **kwargs)  # type: ignore[no-untyped-call]
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
        pass

    arq.connections.log_redis_info = _no_op_log
    arq.worker.log_redis_info = _no_op_log  # type: ignore[attr-defined]


def get_patched_fakeredis_pool() -> ArqRedis:
    """Creates an ArqCompatibleFakeRedis instance compatible with Arq.

    Arq (0.26+) expects specific methods on the connection pool that FakeRedis
    doesn't natively provide or behaves differently with. This function provides
    a strongly typed subclass instance to ensure Arq runs smoothly in in-memory mode.

    Returns:
        An Arq-compatible wrapper around an ArqCompatibleFakeRedis instance.
    """
    from fakeredis import FakeServer

    fake_redis = ArqCompatibleFakeRedis(server=FakeServer())
    fake_redis.connection_kwargs = {"host": "localhost", "port": 6379}  # type: ignore[attr-defined]

    _patch_arq_logging()

    arq_redis = ArqRedis(fake_redis)  # type: ignore[arg-type]
    logger.info("In-Memory Redis pool (Patched) initialized.")

    return arq_redis
