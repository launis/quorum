"""Unit tests for ArqCompatibleFakeRedis and get_patched_fakeredis_pool."""

import arq.connections
import pytest
from fakeredis import FakeServer

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.settings import get_settings
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
async def test_mock_retry_invalid_callable_raises_app_exception() -> None:
    """Tests MockRetry raises AppException when func is not callable (ISTQB negative test)."""
    retry = MockRetry()

    with pytest.raises(AppException) as exc_info:
        await retry.call_with_retry(None, None)

    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_arq_compatible_fake_redis_lifecycle() -> None:
    """Tests ArqCompatibleFakeRedis connection methods and command dispatch."""
    settings = get_settings()
    fake_redis = ArqCompatibleFakeRedis(server=FakeServer())

    assert fake_redis.connection_kwargs == {
        "host": settings.redis_host,
        "port": settings.redis_port,
    }

    conn = await fake_redis.get_connection()
    assert conn is fake_redis

    await fake_redis.release(conn)

    packed = fake_redis.pack_commands(["CMD1", "CMD2"])
    assert packed == ["CMD1", "CMD2"]

    await fake_redis.send_packed_command(packed)

    await fake_redis.send_command("PING")
    res = await fake_redis.read_response()
    assert res in (b"PONG", "PONG", True)


def test_arq_compatible_fake_redis_pack_commands_empty_raises_app_exception() -> None:
    """Tests pack_commands raises AppException on empty or None command payload (ISTQB boundary test)."""
    fake_redis = ArqCompatibleFakeRedis(server=FakeServer())

    with pytest.raises(AppException) as exc_info:
        fake_redis.pack_commands([])

    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_arq_compatible_fake_redis_send_command_empty_raises_app_exception() -> None:
    """Tests send_command raises AppException when invoked with no command arguments (ISTQB boundary test)."""
    fake_redis = ArqCompatibleFakeRedis(server=FakeServer())

    with pytest.raises(AppException) as exc_info:
        await fake_redis.send_command()

    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_get_patched_fakeredis_pool() -> None:
    """Tests pool factory returns ArqRedis wrapper and patches Arq logging."""
    pool = get_patched_fakeredis_pool()
    assert pool is not None
    await arq.connections.log_redis_info(pool, print)
