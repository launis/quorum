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

_last_response_var = contextvars.ContextVar("fake_redis_last_response", default=None)


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


def _patch_arq_connection_handling(fake_redis: Any) -> None:
    """Patches connection lifecycle methods on FakeRedis for Arq.

    Args:
        fake_redis: The FakeRedis instance to patch.
    """
    if not hasattr(fake_redis, "get_connection"):

        async def _get_conn() -> Any:
            return fake_redis

        fake_redis.get_connection = _get_conn

    if not hasattr(fake_redis, "release"):

        async def _release(conn: Any) -> None:
            pass

        fake_redis.release = _release

    if not hasattr(fake_redis, "retry"):
        fake_redis.retry = MockRetry()


def _patch_arq_logging() -> None:
    """Patches Arq logging to prevent crashes with FakeRedis."""

    async def _no_op_log(*args: Any, **kwargs: Any) -> None:
        pass

    arq.connections.log_redis_info = _no_op_log
    arq.worker.log_redis_info = _no_op_log  # type: ignore[attr-defined]


def _patch_arq_pipelining(fake_redis: Any) -> None:
    """Patches pipeline and command packing methods on FakeRedis.

    Args:
        fake_redis: The FakeRedis instance to patch.
    """
    if not hasattr(fake_redis, "pack_commands"):

        def _pack(cmds: Any) -> Any:
            return cmds

        fake_redis.pack_commands = _pack

    if not hasattr(fake_redis, "send_packed_command"):

        async def _send_packed(cmds: Any) -> None:
            pass

        fake_redis.send_packed_command = _send_packed


def _patch_arq_command_execution(fake_redis: Any) -> None:
    """Patches direct command execution for Arq compatibility.

    Args:
        fake_redis: The FakeRedis instance to patch.
    """
    if not hasattr(fake_redis, "send_command"):

        async def _send_command(*args: Any, **kwargs: Any) -> Any:
            res = await fake_redis.execute_command(*args, **kwargs)
            _last_response_var.set(res)

        fake_redis.send_command = _send_command

    if not hasattr(fake_redis, "read_response"):

        async def _read_response() -> Any:
            return _last_response_var.get()

        fake_redis.read_response = _read_response


def get_patched_fakeredis_pool() -> ArqRedis:
    """Creates and patches a FakeRedis instance to be compatible with Arq.

    Arq (0.26+) expects specific methods on the connection pool that FakeRedis
    doesn't natively provide or behaves differently with. This function applies
    all necessary monkey-patches to ensure Arq runs smoothly in in-memory mode.

    Returns:
        An Arq-compatible wrapper around a patched FakeRedis instance.
    """
    fake_redis = FakeRedis()
    fake_redis.connection_kwargs = {"host": "localhost", "port": 6379}  # type: ignore[attr-defined]

    _patch_arq_connection_handling(fake_redis)
    _patch_arq_logging()
    _patch_arq_pipelining(fake_redis)
    _patch_arq_command_execution(fake_redis)

    arq_redis = ArqRedis(fake_redis)  # type: ignore[arg-type]
    logger.info("In-Memory Redis pool (Patched) initialized.")

    return arq_redis
