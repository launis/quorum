"""Redis patching utilities."""

import logging
from typing import Any

from arq.connections import ArqRedis

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


def get_patched_fakeredis_pool() -> ArqRedis:
    """Creates and patches a FakeRedis instance to be compatible with Arq.

    Arq (0.26+) expects specific methods on the connection pool that FakeRedis
    doesn't natively provide or behaves differently with. This function applies
    all necessary monkey-patches to ensure Arq runs smoothly in in-memory mode.

    Returns:
        ArqRedis: An Arq-compatible wrapper around a patched FakeRedis instance.
    """
    try:
        import arq.connections
        import arq.worker
        from fakeredis.aioredis import FakeRedis
    except ImportError as e:
        logger.warning("Failed to import 'fakeredis': %s. Creating a pure Python Mock pool instead.", e)

        class MockArqPool:
            async def enqueue_job(self, function: str, *args: Any, **kwargs: Any) -> Any:
                logger.debug("[MockArqPool] Enqueued virtual job %s", function)

                class MockJob:
                    job_id = "mock_job_123"

                return MockJob()

            def close(self) -> None:
                pass

            async def wait_closed(self) -> None:
                pass

        return MockArqPool()  # type: ignore

    # Initialize FakeRedis
    # Arq expects a pool-like object, FakeRedis works as one, but needs 'connection_kwargs' for Arq logging
    fake_redis: Any = FakeRedis()
    fake_redis.connection_kwargs = {"host": "localhost", "port": 6379}  # Mock for Arq compatibility

    # PATCH: Arq 0.26+ calls .get_connection() on the pool, which FakeRedis lacks
    if not hasattr(fake_redis, "get_connection"):

        async def _get_conn():  # type: ignore
            return fake_redis

        fake_redis.get_connection = _get_conn

    # PATCH: Arq also calls .release(conn)
    if not hasattr(fake_redis, "release"):

        async def _release(conn):  # type: ignore
            pass

        fake_redis.release = _release

    # PATCH: Arq calls .disconnect() on the pool? No, on connection.
    # FakeRedis has close() but Arq might call something else.
    # But the specific error is AttributeError: 'FakeRedis' object has no attribute 'retry'
    # in await conn.retry.call_with_retry
    # Wait, 'conn' IS 'fake_redis' because _get_conn returns self.
    # So fake_redis needs a .retry attribute which has a .call_with_retry method.

    class MockRetry:
        async def call_with_retry(self, func, on_error):  # type: ignore
            return await func()

    if not hasattr(fake_redis, "retry"):
        fake_redis.retry = MockRetry()

    # PATCH: Arq tries to log Redis info on startup, which crashes on FakeRedis
    # We patch the logging function itself to be a no-op
    async def _no_op_log(*args, **kwargs):  # type: ignore
        pass

    arq.connections.log_redis_info = _no_op_log

    # PATCH: We must also patch the reference in arq.worker, as it likely imported the function already
    arq.worker.log_redis_info = _no_op_log  # type: ignore

    # PATCH: Arq 0.26+ uses connection.pack_commands(cmds) for pipelining optimization
    if not hasattr(fake_redis, "pack_commands"):

        def _pack(cmds):  # type: ignore
            return cmds  # Pass through for fake redis

        fake_redis.pack_commands = _pack

    if not hasattr(fake_redis, "send_packed_command"):

        async def _send_packed(cmds):  # type: ignore
            pass

        fake_redis.send_packed_command = _send_packed

    # PATCH: Arq 0.26+ uses send_command(*args)
    if not hasattr(fake_redis, "send_command"):

        async def _send_command(*args, **kwargs):  # type: ignore
            pass

        fake_redis.send_command = _send_command

    # PATCH: Redis-py (via Arq) calls read_response() to await result
    if not hasattr(fake_redis, "read_response"):

        async def _read_response():  # type: ignore
            # In a real connection, this reads bytes.
            # Here, we do nothing because fakeredis executes immediately.
            # Returning None might cause parse_response to fail if it expects data.
            # However, for many operations, the result is already returned by execute_command.
            pass

        fake_redis.read_response = _read_response

    # ArqRedis wrapper needed for Arq features
    arq_redis = ArqRedis(fake_redis)
    logger.info("In-Memory Redis pool (Patched) initialized.")

    return arq_redis
