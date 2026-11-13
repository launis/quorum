"""Unit tests for TypedCacheService, MCPGatewayCache, and auto-eviction firewall."""

from __future__ import annotations

import asyncio

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.system_config import AllowedMCPTool, SystemConfigMCPGateways
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.mcp import MCPToolInputSchemaDTO
from backend_v2.models.enums import EntityPrefix
from backend_v2.services.cache.typed_cache import (
    InMemoryRedisClient,
    MCPGatewayCache,
    RedisClientProtocol,
    TypedCacheService,
)
from backend_v2.settings import get_settings
from backend_v2.tests.factories.model_factories import I18nTextFactory, WorkflowFactory


class FaultyRedisClient:
    """Stateful RedisClientProtocol test double delegating to InMemoryRedisClient with fault injection.

    Attributes:
        backing: Underlying stateful InMemoryRedisClient store.
        fail_on_get: Whether get operations raise ConnectionError.
        fail_on_set: Whether set operations raise OSError.
        fail_on_delete: Whether delete operations raise ConnectionError.
        delay_seconds: Artificial async delay in seconds before completing operations.
        last_ex: Last expiration TTL passed to set, or None.
        bytes_mode: Whether get returns UTF-8 bytes instead of str on cache hit.
    """

    def __init__(self) -> None:
        """Initialize the stateful Redis client double with all faults cleared."""
        self.backing: InMemoryRedisClient = InMemoryRedisClient()
        self.fail_on_get: bool = False
        self.fail_on_set: bool = False
        self.fail_on_delete: bool = False
        self.delay_seconds: float = 0.0
        self.last_ex: int | None = None
        self.bytes_mode: bool = False

    def clear_faults(self) -> None:
        """Reset all fault and latency injection flags to clean defaults."""
        self.fail_on_get = False
        self.fail_on_set = False
        self.fail_on_delete = False
        self.delay_seconds = 0.0
        self.bytes_mode = False

    async def get(self, key: str) -> str | bytes | None:
        """Retrieve a value or simulate latency/transport failure when configured.

        Args:
            key: Cache storage key.

        Returns:
            Serialized JSON str or UTF-8 bytes on hit, or None on miss.

        Raises:
            ConnectionError: If fail_on_get fault injection is active.
        """
        if self.delay_seconds > 0.0:
            await asyncio.sleep(self.delay_seconds)
        if self.fail_on_get:
            raise ConnectionError("Simulated Redis disconnect on get")
        val = await self.backing.get(key)
        if val is not None and self.bytes_mode:
            return val.encode("utf-8")
        return val

    async def set(self, key: str, value: str, *, ex: int | None = None) -> None:
        """Store a value with optional TTL tracking or simulate transport failure.

        Args:
            key: Cache storage key.
            value: Serialized JSON string.
            ex: Optional expiration TTL in seconds.

        Raises:
            OSError: If fail_on_set fault injection is active.
        """
        if self.delay_seconds > 0.0:
            await asyncio.sleep(self.delay_seconds)
        if self.fail_on_set:
            raise OSError("Simulated Redis socket error on set")
        self.last_ex = ex
        await self.backing.set(key, value, ex=ex)

    async def delete(self, key: str) -> None:
        """Delete a key or simulate transport failure when configured.

        Args:
            key: Cache storage key to delete.

        Raises:
            ConnectionError: If fail_on_delete fault injection is active.
        """
        if self.delay_seconds > 0.0:
            await asyncio.sleep(self.delay_seconds)
        if self.fail_on_delete:
            raise ConnectionError("Simulated Redis disconnect on delete")
        await self.backing.delete(key)


def _build_gateway(gateway_id: str | None = None) -> SystemConfigMCPGateways:
    """Construct a canonical SystemConfigMCPGateways instance with typed tool schemas."""
    resolved_id = gateway_id if gateway_id is not None else generate_opaque_id(EntityPrefix.MCP_GATEWAY)
    return SystemConfigMCPGateways(
        id=resolved_id,
        organization_id="org_0195f3a0000070008000000000000001",
        name="Tavily MCP Gateway",
        slug="tavily_gateway",
        tools=[
            AllowedMCPTool(
                tool_id="tavily_search",
                name=I18nTextFactory.build(),
                description="Search web",
                input_schema=MCPToolInputSchemaDTO(properties={}, required=[]),
            )
        ],
    )


@pytest.mark.asyncio
async def test_typed_cache_stateful_roundtrip_str_and_bytes() -> None:
    """Positive: Verify stateful set, get (str and bytes), TTL forwarding, and delete roundtrips."""
    redis_client = FaultyRedisClient()
    protocol_client: RedisClientProtocol = redis_client
    cache_service = TypedCacheService(redis=protocol_client)
    workflow = WorkflowFactory.build()
    cache_key = f"workflow:{workflow.id}"

    try:
        assert await cache_service.get_cached(cache_key, Workflow) is None

        # Deleting a non-existent key is a clean no-op
        await cache_service.delete(cache_key)

        await cache_service.set_cached(cache_key, workflow, expire_seconds=3600)
        assert redis_client.last_ex == 3600

        hit_str = await cache_service.get_cached(cache_key, Workflow)
        assert hit_str is not None
        assert hit_str.id == workflow.id
        assert hit_str.name == workflow.name

        # Verify bytes deserialization path supported by RedisClientProtocol
        redis_client.bytes_mode = True
        hit_bytes = await cache_service.get_cached(cache_key, Workflow)
        assert hit_bytes is not None
        assert hit_bytes.id == workflow.id

        # Overwrite without TTL
        await cache_service.set_cached(cache_key, workflow)
        assert redis_client.last_ex is None

        await cache_service.delete(cache_key)
        assert await cache_service.get_cached(cache_key, Workflow) is None
    finally:
        redis_client.clear_faults()


@pytest.mark.asyncio
async def test_typed_cache_noop_when_redis_unconfigured() -> None:
    """Positive: Verify get_cached, set_cached, and delete act as safe no-ops when redis is None."""
    workflow = WorkflowFactory.build()
    cache_key = f"workflow:{workflow.id}"
    cache_service = TypedCacheService(redis=None)

    assert await cache_service.get_cached(cache_key, Workflow) is None
    await cache_service.set_cached(cache_key, workflow, expire_seconds=60)
    await cache_service.delete(cache_key)


@pytest.mark.asyncio
async def test_typed_cache_auto_eviction_on_validation_error() -> None:
    """Negative (ISTQB): Corrupted cached JSON auto-evicts key and raises VALIDATION_FAILED AppException."""
    redis_client = InMemoryRedisClient()
    cache_service = TypedCacheService(redis=redis_client)
    corrupted_key = f"workflow:{generate_opaque_id(EntityPrefix.WORKFLOW)}"
    await redis_client.set(corrupted_key, '{"unexpected_field": "invalid"}')

    with pytest.raises(AppException) as exc_info:
        await cache_service.get_cached(corrupted_key, Workflow)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert await redis_client.get(corrupted_key) is None


@pytest.mark.asyncio
async def test_typed_cache_auto_eviction_delete_failure() -> None:
    """Negative (ISTQB): Transport failure during ValidationError auto-eviction raises VALIDATION_FAILED."""
    faulty_redis = FaultyRedisClient()
    cache_service = TypedCacheService(redis=faulty_redis)
    corrupted_key = f"workflow:{generate_opaque_id(EntityPrefix.WORKFLOW)}"
    await faulty_redis.set(corrupted_key, "{malformed_json")

    faulty_redis.fail_on_delete = True
    try:
        with pytest.raises(AppException) as exc_info:
            await cache_service.get_cached(corrupted_key, Workflow)

        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    finally:
        faulty_redis.clear_faults()


@pytest.mark.asyncio
async def test_typed_cache_rejects_empty_or_whitespace_keys_and_non_positive_ttl() -> None:
    """Negative & BVA (ISTQB min-1): Empty/whitespace keys and expire_seconds <= 0 or timeout <= 0 raise VALIDATION_FAILED."""
    redis_client = InMemoryRedisClient()
    cache_service = TypedCacheService(redis=redis_client)
    workflow = WorkflowFactory.build()
    valid_key = f"workflow:{workflow.id}"

    for invalid_key in ("", "   "):
        with pytest.raises(AppException) as get_exc:
            await cache_service.get_cached(invalid_key, Workflow)
        assert get_exc.value.status_code == 400
        assert get_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as set_exc:
            await cache_service.set_cached(invalid_key, workflow)
        assert set_exc.value.status_code == 400
        assert set_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

        with pytest.raises(AppException) as del_exc:
            await cache_service.delete(invalid_key)
        assert del_exc.value.status_code == 400
        assert del_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    for invalid_ttl in (0, -1):
        with pytest.raises(AppException) as ttl_exc:
            await cache_service.set_cached(valid_key, workflow, expire_seconds=invalid_ttl)
        assert ttl_exc.value.status_code == 400
        assert ttl_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    for invalid_timeout in (0.0, -0.5):
        with pytest.raises(AppException) as timeout_init_exc:
            TypedCacheService(redis=redis_client, timeout_seconds=invalid_timeout)
        assert timeout_init_exc.value.status_code == 400
        assert timeout_init_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_typed_cache_transport_errors_and_settings_timeout_sovereignty() -> None:
    """Negative (ISTQB): Redis transport errors and Settings timeout breaches translate to STORAGE_ACCESS_FAILED."""
    faulty_redis = FaultyRedisClient()
    workflow = WorkflowFactory.build()
    cache_key = f"workflow:{workflow.id}"
    base_settings = get_settings()
    short_timeout_settings = base_settings.model_copy(update={"redis_connection_timeout_seconds": 1})
    cache_service = TypedCacheService(
        redis=faulty_redis,
        get_settings_fn=lambda: short_timeout_settings,
    )

    try:
        faulty_redis.fail_on_get = True
        with pytest.raises(AppException) as get_err:
            await cache_service.get_cached(cache_key, Workflow)
        assert get_err.value.status_code == 500
        assert get_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
        faulty_redis.fail_on_get = False

        faulty_redis.fail_on_set = True
        with pytest.raises(AppException) as set_err:
            await cache_service.set_cached(cache_key, workflow, expire_seconds=60)
        assert set_err.value.status_code == 500
        assert set_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
        faulty_redis.fail_on_set = False

        faulty_redis.fail_on_delete = True
        with pytest.raises(AppException) as del_err:
            await cache_service.delete(cache_key)
        assert del_err.value.status_code == 500
        assert del_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
        faulty_redis.fail_on_delete = False

        # Verify bounded asyncio.timeout cancellation using explicit timeout_seconds override
        fast_timeout_cache = TypedCacheService(redis=faulty_redis, timeout_seconds=0.01)
        faulty_redis.delay_seconds = 0.05
        with pytest.raises(AppException) as timeout_err:
            await fast_timeout_cache.get_cached(cache_key, Workflow)
        assert timeout_err.value.status_code == 500
        assert timeout_err.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        faulty_redis.clear_faults()


@pytest.mark.asyncio
async def test_mcp_gateway_cache_stateful_roundtrip_and_invalid_id_rejection() -> None:
    """Positive & Negative (ISTQB): Verify MCPGatewayCache roundtrip and canonical mcp_<hex32> ID enforcement."""
    gateway = _build_gateway()
    gw_cache = MCPGatewayCache()
    assert MCPGatewayCache.build_key(gateway.id) == f"mcp_gateway:{gateway.id}"
    assert await gw_cache.get_gateway(gateway.id) is None

    await gw_cache.set_gateway(gateway, expire_seconds=300)
    cached = await gw_cache.get_gateway(gateway.id)
    assert cached is not None
    assert cached.id == gateway.id
    assert cached.name == "Tavily MCP Gateway"
    assert len(cached.tools) == 1

    await gw_cache.invalidate(gateway.id)
    assert await gw_cache.get_gateway(gateway.id) is None

    # Negative: non-canonical or wrong-prefix IDs must fail fast with VALIDATION_FAILED
    wrong_prefix_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    for bad_gateway_id in ("", "tavily_gateway", wrong_prefix_id):
        with pytest.raises(AppException) as bad_id_exc:
            await gw_cache.get_gateway(bad_gateway_id)
        assert bad_id_exc.value.status_code == 400
        assert bad_id_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
