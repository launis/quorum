"""Unit tests for backend_v2.services.cache package facade exports and fail-fast invariants."""

from __future__ import annotations

from typing import override

import pytest

import backend_v2.services.cache as cache_pkg
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import EntityPrefix
from backend_v2.services.cache import (
    InMemoryRedisClient,
    MCPGatewayCache,
    RedisClientProtocol,
    TypedCacheService,
)
from backend_v2.tests.factories.model_factories import WorkflowFactory


class FaultyEvictionRedisClient(InMemoryRedisClient):
    """Stateful in-memory Redis client double supporting deterministic delete fault injection.

    Attributes:
        fail_on_delete: Whether delete operations raise a ConnectionError.
    """

    @override
    def __init__(self) -> None:
        """Initialize the in-memory Redis client with fault injection disabled."""
        super().__init__()
        self.fail_on_delete: bool = False

    def inject_delete_fault(self) -> None:
        """Enable deterministic ConnectionError injection on delete calls."""
        self.fail_on_delete = True

    def clear_faults(self) -> None:
        """Clear any active fault injection flags."""
        self.fail_on_delete = False

    @override
    async def delete(self, key: str) -> None:
        """Delete a key or raise ConnectionError when delete fault injection is active.

        Args:
            key: Cache storage key to delete.

        Raises:
            ConnectionError: If delete fault injection is enabled.
        """
        if self.fail_on_delete:
            raise ConnectionError("Simulated Redis transport disconnect during eviction")
        await super().delete(key)


@pytest.mark.asyncio
async def test_cache_package_facade_stateful_roundtrip() -> None:
    """Verify cache package facade exports and stateful roundtrip behavior."""
    assert sorted(cache_pkg.__all__) == [
        "InMemoryRedisClient",
        "MCPGatewayCache",
        "RedisClientProtocol",
        "TypedCacheService",
    ]

    redis_client: RedisClientProtocol = InMemoryRedisClient()
    cache_service = TypedCacheService(redis=redis_client)
    workflow = WorkflowFactory.build()
    cache_key = f"workflow:{workflow.id}"

    assert await cache_service.get_cached(cache_key, Workflow) is None

    await cache_service.set_cached(cache_key, workflow, expire_seconds=300)
    hydrated = await cache_service.get_cached(cache_key, Workflow)
    assert hydrated is not None
    assert hydrated.id == workflow.id
    assert hydrated.name == workflow.name

    await cache_service.delete(cache_key)
    assert await cache_service.get_cached(cache_key, Workflow) is None

    gateway_id = generate_opaque_id(EntityPrefix.MCP_GATEWAY)
    gateway_cache = MCPGatewayCache(cache_service=cache_service)
    assert MCPGatewayCache.build_key(gateway_id) == f"mcp_gateway:{gateway_id}"
    assert await gateway_cache.get_gateway(gateway_id) is None


@pytest.mark.asyncio
async def test_cache_package_corrupted_payload_validation_error() -> None:
    """Negative test (ISTQB): corrupted cached JSON auto-evicts key and raises AppException."""
    redis_client = InMemoryRedisClient()
    cache_service = TypedCacheService(redis=redis_client)
    corrupted_key = f"workflow:{generate_opaque_id(EntityPrefix.WORKFLOW)}"
    await redis_client.set(corrupted_key, '{"unexpected_field": "corrupted_payload"}')

    with pytest.raises(AppException) as exc_info:
        await cache_service.get_cached(corrupted_key, Workflow)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert await redis_client.get(corrupted_key) is None


@pytest.mark.asyncio
async def test_cache_package_auto_eviction_transport_failure() -> None:
    """Negative test (ISTQB): transport failure during auto-eviction raises AppException."""
    faulty_redis = FaultyEvictionRedisClient()
    cache_service = TypedCacheService(redis=faulty_redis)
    corrupted_key = f"workflow:{generate_opaque_id(EntityPrefix.WORKFLOW)}"
    await faulty_redis.set(corrupted_key, "{malformed_json")

    faulty_redis.inject_delete_fault()
    try:
        with pytest.raises(AppException) as exc_info:
            await cache_service.get_cached(corrupted_key, Workflow)

        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        faulty_redis.clear_faults()
