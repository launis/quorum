"""Typed Redis cache service for high-throughput Pydantic V2 model storage and retrieval.

Enforces strict Rust-level model_validate_json() deserialization, zero unvalidated dict caching,
and auto-eviction firewall on ValidationError as mandated by Phase 6.
"""

import logging
from typing import Any

from pydantic import BaseModel, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.system_config import SystemConfigMCPGateways

logger = logging.getLogger(__name__)

__all__ = ["MCPGatewayCache", "TypedCacheService"]


class TypedCacheService:
    """Generic typed cache service wrapping Redis with Pydantic V2 serialization."""

    def __init__(self, redis: Any | None = None) -> None:
        """Initialize TypedCacheService with an optional Redis client.

        Args:
            redis: Asynchronous Redis client instance or connection pool.
        """
        self.redis = redis

    async def get_cached[T: BaseModel](self, key: str, model_cls: type[T]) -> T | None:
        """Retrieve and validate a cached Pydantic model from Redis.

        Args:
            key: Cache storage key.
            model_cls: Target Pydantic model class for Rust-level deserialization.

        Returns:
            Validated model instance, or None if key is absent or Redis is unavailable.

        Raises:
            AppException: VALIDATION_FAILED if cached data is corrupted or auto-eviction fails.
        """
        if self.redis is None:
            return None

        redis = self.redis
        raw_val = await redis.get(key)
        if raw_val is None:
            return None

        try:
            return model_cls.model_validate_json(raw_val)
        except ValidationError as val_err:
            logger.error(
                "Corrupted cache payload encountered for key %s, auto-evicting",
                key,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            )
            try:
                await self.redis.delete(key)
            except (ConnectionError, TimeoutError, OSError) as e:
                logger.error(
                    "Failed to auto-evict corrupted cache key %s: %s",
                    key,
                    e,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
                )
                raise AppException(
                    message=f"Failed to auto-evict corrupted cache key '{key}': {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "key": key},
                ) from e
            raise AppException(
                message=f"Corrupted cache payload encountered for key '{key}': {val_err}",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "key": key},
            ) from val_err

    async def set_cached(self, key: str, model: BaseModel, expire_seconds: int | None = None) -> None:
        """Serialize and store a Pydantic model in Redis cache.

        Args:
            key: Cache storage key.
            model: Pydantic model instance to serialize.
            expire_seconds: Optional TTL in seconds for key expiration.
        """
        if self.redis is None:
            return

        payload = model.model_dump_json()
        if expire_seconds is not None:
            await self.redis.set(key, payload, ex=expire_seconds)
        else:
            await self.redis.set(key, payload)

    async def delete(self, key: str) -> None:
        """Purge a specific key from Redis cache.

        Args:
            key: Cache storage key to delete.
        """
        if self.redis is None:
            return

        await self.redis.delete(key)


class MCPGatewayCache:
    """Typed cache namespace for discovered SystemConfigMCPGateways tool manifests.

    # Phase 2, Step 2.3: Register MCPGatewayCache with deterministic invalidation
    """

    KEY_PREFIX: str = "mcp_gateway:"

    def __init__(self, cache_service: TypedCacheService | None = None) -> None:
        """Initialize MCPGatewayCache with an underlying TypedCacheService.

        Args:
            cache_service: Optional TypedCacheService instance wrapping Redis.
        """
        self.cache_service = cache_service if cache_service is not None else TypedCacheService()
        self._memory_entries: dict[str, str] = {}

    @classmethod
    def build_key(cls, gateway_id: str) -> str:
        """Construct the canonical cache key for an MCP gateway ID.

        Args:
            gateway_id: Canonical Opaque Stripe ID of the gateway.

        Returns:
            Namespaced cache key string.
        """
        return f"{cls.KEY_PREFIX}{gateway_id}"

    async def get_gateway(self, gateway_id: str) -> SystemConfigMCPGateways | None:
        """Retrieve a cached SystemConfigMCPGateways record by ID.

        Args:
            gateway_id: Canonical Opaque Stripe ID of the gateway.

        Returns:
            Validated SystemConfigMCPGateways instance or None on cache miss.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if cached payload is corrupted.
        """
        key = self.build_key(gateway_id)
        redis_hit = await self.cache_service.get_cached(key, SystemConfigMCPGateways)
        if redis_hit is not None:
            self._memory_entries[key] = redis_hit.model_dump_json()
            return redis_hit

        if key in self._memory_entries:
            return SystemConfigMCPGateways.model_validate_json(self._memory_entries[key])

        return None

    async def set_gateway(
        self,
        gateway: SystemConfigMCPGateways,
        expire_seconds: int | None = None,
    ) -> None:
        """Store a SystemConfigMCPGateways record in cache.

        Args:
            gateway: Validated SystemConfigMCPGateways domain object.
            expire_seconds: Optional expiration TTL in seconds.
        """
        key = self.build_key(gateway.id)
        self._memory_entries[key] = gateway.model_dump_json()
        await self.cache_service.set_cached(key, gateway, expire_seconds=expire_seconds)

    async def invalidate(self, gateway_id: str) -> None:
        """Deterministically evict a specific gateway manifest from cache.

        Args:
            gateway_id: Canonical Opaque Stripe ID of the gateway to evict.
        """
        key = self.build_key(gateway_id)
        if key in self._memory_entries:
            del self._memory_entries[key]
        await self.cache_service.delete(key)
