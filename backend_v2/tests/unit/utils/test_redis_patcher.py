"""Unit tests for ArqCompatibleFakeRedis and get_patched_fakeredis_pool."""

import pytest
from fakeredis import FakeServer

from backend_v2.utils.redis_patcher import (
    ArqCompatibleFakeRedis,
    MockRetry,
    get_patched_fakeredis_pool,
)


@pytest.mark.asyncio
async def test_mock_retry() -> None:
    """Tests MockRetry directly calling provided async function."""
    retry = MockRetry()
    called = False

    async def sample_func() -> str:
        nonlocal called
        called = True
        return "result"

    res = await retry.call_with_retry(sample_func, None)
    assert called is True
    assert res == "result"


@pytest.mark.asyncio
async def test_arq_compatible_fake_redis_lifecycle() -> None:
    """Tests ArqCompatibleFakeRedis connection methods and command dispatch."""
    fake_redis = ArqCompatibleFakeRedis(server=FakeServer())

    conn = await fake_redis.get_connection()
    assert conn is fake_redis

    await fake_redis.release(conn)

    packed = fake_redis.pack_commands(["CMD1", "CMD2"])
    assert packed == ["CMD1", "CMD2"]

    await fake_redis.send_packed_command(packed)

    await fake_redis.send_command("PING")
    res = await fake_redis.read_response()
    assert res == b"PONG" or res == "PONG" or res is True


def test_get_patched_fakeredis_pool() -> None:
    """Tests pool factory returns ArqRedis wrapper."""
    pool = get_patched_fakeredis_pool()
    assert pool is not None
