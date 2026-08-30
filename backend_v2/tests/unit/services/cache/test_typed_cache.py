"""Unit tests for TypedCacheService and auto-eviction firewall."""

from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel, ConfigDict

from backend_v2.services.cache.typed_cache import TypedCacheService


class SampleModel(BaseModel):
    """Sample Pydantic model for cache testing."""

    model_config = ConfigDict(strict=True, extra="forbid")

    id: str
    name: str
    count: int


@pytest.mark.asyncio
async def test_typed_cache_get_cached_none_when_no_redis() -> None:
    """Verify get_cached returns None when Redis is unconfigured."""
    cache_service = TypedCacheService(redis=None)
    result = await cache_service.get_cached("some_key", SampleModel)
    assert result is None


@pytest.mark.asyncio
async def test_typed_cache_get_cached_miss() -> None:
    """Verify get_cached returns None on cache miss."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None

    cache_service = TypedCacheService(redis=mock_redis)
    result = await cache_service.get_cached("missing_key", SampleModel)

    assert result is None
    mock_redis.get.assert_called_once_with("missing_key")


@pytest.mark.asyncio
async def test_typed_cache_get_cached_hit() -> None:
    """Verify get_cached successfully deserializes valid JSON."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = '{"id": "s1", "name": "Test", "count": 42}'

    cache_service = TypedCacheService(redis=mock_redis)
    result = await cache_service.get_cached("sample_key", SampleModel)

    assert result is not None
    assert isinstance(result, SampleModel)
    assert result.id == "s1"
    assert result.name == "Test"
    assert result.count == 42


@pytest.mark.asyncio
async def test_typed_cache_get_cached_auto_eviction_on_validation_error() -> None:
    """Verify get_cached auto-evicts corrupted payload on ValidationError and returns None."""
    mock_redis = AsyncMock()
    # Malformed payload missing required field 'count' and having unexpected field 'extra'
    mock_redis.get.return_value = '{"id": "s1", "name": "Test", "extra": "invalid"}'

    cache_service = TypedCacheService(redis=mock_redis)
    result = await cache_service.get_cached("corrupted_key", SampleModel)

    assert result is None
    mock_redis.delete.assert_called_once_with("corrupted_key")


@pytest.mark.asyncio
async def test_typed_cache_set_cached_with_ttl() -> None:
    """Verify set_cached stores serialized JSON with expiration."""
    mock_redis = AsyncMock()
    model = SampleModel(id="s1", name="Test", count=10)

    cache_service = TypedCacheService(redis=mock_redis)
    await cache_service.set_cached("sample_key", model, expire_seconds=3600)

    mock_redis.set.assert_called_once_with(
        "sample_key",
        '{"id":"s1","name":"Test","count":10}',
        ex=3600,
    )


@pytest.mark.asyncio
async def test_typed_cache_set_cached_without_ttl() -> None:
    """Verify set_cached stores serialized JSON without expiration."""
    mock_redis = AsyncMock()
    model = SampleModel(id="s1", name="Test", count=10)

    cache_service = TypedCacheService(redis=mock_redis)
    await cache_service.set_cached("sample_key", model)

    mock_redis.set.assert_called_once_with(
        "sample_key",
        '{"id":"s1","name":"Test","count":10}',
    )


@pytest.mark.asyncio
async def test_typed_cache_set_cached_no_redis() -> None:
    """Verify set_cached does not fail when Redis is None."""
    model = SampleModel(id="s1", name="Test", count=10)
    cache_service = TypedCacheService(redis=None)
    await cache_service.set_cached("sample_key", model)


@pytest.mark.asyncio
async def test_typed_cache_delete() -> None:
    """Verify delete calls redis.delete."""
    mock_redis = AsyncMock()
    cache_service = TypedCacheService(redis=mock_redis)
    await cache_service.delete("sample_key")

    mock_redis.delete.assert_called_once_with("sample_key")


@pytest.mark.asyncio
async def test_typed_cache_delete_no_redis() -> None:
    """Verify delete does not fail when Redis is None."""
    cache_service = TypedCacheService(redis=None)
    await cache_service.delete("sample_key")
