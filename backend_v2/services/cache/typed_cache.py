"""Typed Redis cache service for high-throughput Pydantic V2 model storage and retrieval.

Enforces strict Rust-level model_validate_json() deserialization, zero unvalidated dictionary caching,
bounded Redis I/O timeouts from Settings, and deterministic auto-eviction on ValidationError.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Final, Protocol

from pydantic import BaseModel, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import parse_prefixed_uuid7
from backend_v2.models.domain.system_config import SystemConfigMCPGateways
from backend_v2.models.enums import EntityPrefix
from backend_v2.settings import Settings, get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "InMemoryRedisClient",
    "MCPGatewayCache",
    "RedisClientProtocol",
    "TypedCacheService",
]


class RedisClientProtocol(Protocol):
    """Protocol defining the asynchronous Redis key-value operations required by TypedCacheService."""

    async def get(self, key: str) -> str | bytes | None:
        """Retrieve a raw string or bytes value for a cache key.

        Args:
            key: Cache storage key.

        Returns:
            Cached serialized payload or None on cache miss.
        """
        ...

    async def set(self, key: str, value: str, *, ex: int | None = None) -> object:
        """Persist a serialized JSON payload under a cache key with an optional TTL.

        Args:
            key: Cache storage key.
            value: Serialized JSON string.
            ex: Optional expiration TTL in seconds.

        Returns:
            Driver acknowledgment result.
        """
        ...

    async def delete(self, key: str) -> object:
        """Delete a cache key.

        Args:
            key: Cache storage key to evict.

        Returns:
            Driver deletion result.
        """
        ...


class InMemoryRedisClient:
    """In-memory implementation of RedisClientProtocol for local and test TypedCacheService instances.

    Attributes:
        entries: Mapping of cache keys to serialized JSON payloads.
    """

    def __init__(self) -> None:
        """Initialize an empty in-memory Redis store."""
        self.entries: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        """Retrieve a serialized JSON string for a cache key.

        Args:
            key: Cache storage key.

        Returns:
            Serialized JSON string if present, else None.
        """
        if key in self.entries:
            return self.entries[key]
        return None

    async def set(self, key: str, value: str, *, ex: int | None = None) -> None:
        """Store a serialized JSON string under a cache key.

        Args:
            key: Cache storage key.
            value: Serialized JSON string.
            ex: Optional expiration TTL in seconds.
        """
        _ = ex
        self.entries[key] = value

    async def delete(self, key: str) -> None:
        """Delete a key from the in-memory store if present.

        Args:
            key: Cache storage key to delete.
        """
        if key in self.entries:
            del self.entries[key]


class TypedCacheService:
    """Generic typed cache service wrapping Redis with Pydantic V2 serialization and bounded I/O.

    Attributes:
        redis: Optional RedisClientProtocol client instance.
    """

    def __init__(
        self,
        redis: RedisClientProtocol | None = None,
        get_settings_fn: Callable[[], Settings] | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        """Initialize TypedCacheService with an optional Redis client and Settings timeout binding.

        Args:
            redis: Asynchronous Redis client instance implementing RedisClientProtocol.
            get_settings_fn: Optional callable resolving the active Settings configuration.
            timeout_seconds: Optional positive Redis I/O timeout override in seconds.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if timeout_seconds is non-positive.
        """
        if timeout_seconds is not None and timeout_seconds <= 0.0:
            msg = f"TypedCacheService timeout_seconds must be positive, got {timeout_seconds}."
            logger.error(
                "[TypedCacheService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        self.redis: RedisClientProtocol | None = redis
        self._get_settings_fn: Callable[[], Settings] | None = get_settings_fn
        self._timeout_seconds: float | None = timeout_seconds

    def _resolve_timeout_seconds(self) -> float:
        """Resolve bounded Redis I/O timeout in seconds from explicit override or Settings SSOT.

        Returns:
            Positive timeout duration in seconds.
        """
        if self._timeout_seconds is not None:
            return self._timeout_seconds
        settings = self._get_settings_fn() if self._get_settings_fn is not None else get_settings()
        return float(settings.redis_connection_timeout_seconds)

    def _validate_cache_key(self, key: str) -> None:
        """Verify that a cache storage key is non-empty and contains non-whitespace characters.

        Args:
            key: Cache storage key to validate.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if key is empty or whitespace-only.
        """
        if not key or not key.strip():
            msg = "Cache key cannot be empty or whitespace-only."
            logger.error(
                "[TypedCacheService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "key": key},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "key": key},
            )

    async def _execute_redis_op[R](
        self,
        key: str,
        operation: str,
        op_factory: Callable[[], Awaitable[R]],
        *,
        error_code: ErrorCodes = ErrorCodes.STORAGE_ACCESS_FAILED,
    ) -> R:
        """Execute a Redis I/O operation inside a bounded asyncio.timeout context.

        Args:
            key: Target cache storage key for diagnostic context.
            operation: Redis command identifier for diagnostic logging.
            op_factory: Zero-argument callable creating the Redis coroutine to await.
            error_code: Standardized ErrorCodes value attached on transport or timeout failure.

        Returns:
            Result produced by the awaited Redis operation.

        Raises:
            AppException: With the specified error_code (default STORAGE_ACCESS_FAILED) on transport or timeout failure.
        """
        timeout = self._resolve_timeout_seconds()
        try:
            async with asyncio.timeout(timeout):
                return await op_factory()
        except (ConnectionError, TimeoutError, OSError) as exc:
            msg = f"Redis '{operation}' failed for cache key '{key}': {exc}"
            logger.error(
                "[TypedCacheService] %s: %s",
                error_code.name,
                msg,
                exc_info=True,
                extra={"error_code": error_code.value, "key": key, "operation": operation},
            )
            if error_code is ErrorCodes.VALIDATION_FAILED:
                raise AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "key": key, "operation": operation},
                ) from exc
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value, "key": key, "operation": operation},
            ) from exc

    async def get_cached[T: BaseModel](self, key: str, model_cls: type[T]) -> T | None:
        """Retrieve and validate a cached Pydantic model from Redis.

        Args:
            key: Cache storage key.
            model_cls: Target Pydantic model class for Rust-level deserialization.

        Returns:
            Validated model instance, or None if key is absent or Redis is unavailable.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if key is invalid, cached data is corrupted, or auto-eviction fails; or ErrorCodes.STORAGE_ACCESS_FAILED on Redis transport/timeout failure.
        """
        self._validate_cache_key(key)
        if self.redis is None:
            return None

        redis = self.redis
        raw_val = await self._execute_redis_op(key, "get", lambda: redis.get(key))
        if raw_val is None:
            return None

        try:
            return model_cls.model_validate_json(raw_val)
        except ValidationError as val_err:
            logger.error(
                "[TypedCacheService] %s: Corrupted cache payload encountered for key %s, auto-evicting.",
                ErrorCodes.VALIDATION_FAILED.name,
                key,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "key": key},
            )
            await self._execute_redis_op(
                key,
                "auto_evict_delete",
                lambda: redis.delete(key),
                error_code=ErrorCodes.VALIDATION_FAILED,
            )
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
            expire_seconds: Optional positive TTL in seconds for key expiration.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if key is empty or expire_seconds <= 0; or ErrorCodes.STORAGE_ACCESS_FAILED on Redis transport/timeout failure.
        """
        self._validate_cache_key(key)
        if expire_seconds is not None and expire_seconds <= 0:
            msg = f"Cache expire_seconds must be positive for key '{key}', got {expire_seconds}."
            logger.error(
                "[TypedCacheService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
                extra={
                    "error_code": ErrorCodes.VALIDATION_FAILED.value,
                    "key": key,
                    "expire_seconds": expire_seconds,
                },
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "key": key},
            )
        if self.redis is None:
            return

        redis = self.redis
        payload = model.model_dump_json()
        if expire_seconds is not None:
            await self._execute_redis_op(key, "set", lambda: redis.set(key, payload, ex=expire_seconds))
        else:
            await self._execute_redis_op(key, "set", lambda: redis.set(key, payload))

    async def delete(self, key: str) -> None:
        """Purge a specific key from Redis cache.

        Args:
            key: Cache storage key to delete.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if key is empty; or ErrorCodes.STORAGE_ACCESS_FAILED on Redis transport/timeout failure.
        """
        self._validate_cache_key(key)
        if self.redis is None:
            return

        redis = self.redis
        await self._execute_redis_op(key, "delete", lambda: redis.delete(key))


class MCPGatewayCache:
    """Typed cache namespace for discovered SystemConfigMCPGateways tool manifests.

    Attributes:
        cache_service: Underlying TypedCacheService instance.
    """

    KEY_PREFIX: Final[str] = "mcp_gateway:"

    def __init__(self, cache_service: TypedCacheService | None = None) -> None:
        """Initialize MCPGatewayCache with an underlying TypedCacheService.

        Args:
            cache_service: Optional TypedCacheService instance wrapping RedisClientProtocol.
        """
        self.cache_service: TypedCacheService = (
            cache_service if cache_service is not None else TypedCacheService(redis=InMemoryRedisClient())
        )

    @classmethod
    def build_key(cls, gateway_id: str) -> str:
        """Validate and construct the canonical cache key for an MCP gateway ID.

        Args:
            gateway_id: Canonical Opaque Stripe ID (mcp_<hex32>) of the gateway.

        Returns:
            Namespaced cache key string.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if gateway_id is not a canonical mcp_<hex32> identifier.
        """
        parse_prefixed_uuid7(gateway_id, expected_prefix=EntityPrefix.MCP_GATEWAY, enforce_v7=False)
        cleaned_id = gateway_id.strip()
        return f"{cls.KEY_PREFIX}{cleaned_id}"

    async def get_gateway(self, gateway_id: str) -> SystemConfigMCPGateways | None:
        """Retrieve a cached SystemConfigMCPGateways record by ID.

        Args:
            gateway_id: Canonical Opaque Stripe ID (mcp_<hex32>) of the gateway.

        Returns:
            Validated SystemConfigMCPGateways instance or None on cache miss.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if gateway_id or cached payload is invalid, or ErrorCodes.STORAGE_ACCESS_FAILED on Redis transport/timeout failure.
        """
        key = self.build_key(gateway_id)
        return await self.cache_service.get_cached(key, SystemConfigMCPGateways)

    async def set_gateway(
        self,
        gateway: SystemConfigMCPGateways,
        expire_seconds: int | None = None,
    ) -> None:
        """Store a SystemConfigMCPGateways record in cache.

        Args:
            gateway: Validated SystemConfigMCPGateways domain object.
            expire_seconds: Optional positive expiration TTL in seconds.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if gateway.id or expire_seconds is invalid, or ErrorCodes.STORAGE_ACCESS_FAILED on Redis transport/timeout failure.
        """
        key = self.build_key(gateway.id)
        await self.cache_service.set_cached(key, gateway, expire_seconds=expire_seconds)

    async def invalidate(self, gateway_id: str) -> None:
        """Deterministically evict a specific gateway manifest from cache.

        Args:
            gateway_id: Canonical Opaque Stripe ID (mcp_<hex32>) of the gateway to evict.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if gateway_id is invalid, or ErrorCodes.STORAGE_ACCESS_FAILED on Redis transport/timeout failure.
        """
        key = self.build_key(gateway_id)
        await self.cache_service.delete(key)
