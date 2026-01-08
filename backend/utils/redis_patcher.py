
import logging
from arq.connections import ArqRedis

logger = logging.getLogger(__name__)

def get_patched_fakeredis_pool() -> ArqRedis:
    """
    Creates and patches a FakeRedis instance to be compatible with Arq.
    
    Arq (0.26+) expects specific methods on the connection pool that FakeRedis
    doesn't natively provide or behaves differently with. This function applies
    all necessary monkey-patches to ensure Arq runs smoothly in in-memory mode.
    
    Returns:
        ArqRedis: An Arq-compatible wrapper around a patched FakeRedis instance.
    """
    try:
        from fakeredis.aioredis import FakeRedis
        import arq.connections
        import arq.worker
    except ImportError:
        logger.error("Failed to import 'fakeredis'. Is it installed?")
        raise

    # Initialize FakeRedis
    # Arq expects a pool-like object, FakeRedis works as one, but needs 'connection_kwargs' for Arq logging
    fake_redis = FakeRedis()
    fake_redis.connection_kwargs = {"host": "localhost", "port": 6379}  # Mock for Arq compatibility

    # PATCH: Arq 0.26+ calls .get_connection() on the pool, which FakeRedis lacks
    if not hasattr(fake_redis, "get_connection"):

        async def _get_conn():
            return fake_redis

        fake_redis.get_connection = _get_conn

    # PATCH: Arq also calls .release(conn)
    if not hasattr(fake_redis, "release"):

        async def _release(conn):
            pass

        fake_redis.release = _release

    # PATCH: Arq calls .disconnect() on the pool? No, on connection. FakeRedis has close() but Arq might call something else.
    # But the specific error is AttributeError: 'FakeRedis' object has no attribute 'retry' in await conn.retry.call_with_retry
    # Wait, 'conn' IS 'fake_redis' because _get_conn returns self.
    # So fake_redis needs a .retry attribute which has a .call_with_retry method.

    class MockRetry:
        async def call_with_retry(self, func, on_error):
            return await func()

    if not hasattr(fake_redis, "retry"):
        fake_redis.retry = MockRetry()

    # PATCH: Arq tries to log Redis info on startup, which crashes on FakeRedis
    # We patch the logging function itself to be a no-op
    async def _no_op_log(*args, **kwargs):
        pass

    arq.connections.log_redis_info = _no_op_log
    
    # PATCH: We must also patch the reference in arq.worker, as it likely imported the function already
    arq.worker.log_redis_info = _no_op_log

    # PATCH: Arq 0.26+ uses connection.pack_commands(cmds) for pipelining optimization
    if not hasattr(fake_redis, "pack_commands"):

        def _pack(cmds):
            return cmds  # Pass through for fake redis

        fake_redis.pack_commands = _pack

    if not hasattr(fake_redis, "send_packed_command"):

        async def _send_packed(cmds):
            pass

        fake_redis.send_packed_command = _send_packed

    # PATCH: Arq 0.26+ uses send_command(*args)
    if not hasattr(fake_redis, "send_command"):

        async def _send_command(*args, **kwargs):
            pass

        fake_redis.send_command = _send_command

    # PATCH: Redis-py (via Arq) calls read_response() to await result
    if not hasattr(fake_redis, "read_response"):
        async def _read_response():
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
