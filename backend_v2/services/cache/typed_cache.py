"""Typed Redis cache service for high-throughput Pydantic V2 model storage and retrieval.

Enforces strict Rust-level model_validate_json() deserialization, zero unvalidated dict caching,
and auto-eviction firewall on ValidationError as mandated by Phase 6.
"""

import logging
from typing import Any

from pydantic import BaseModel, ValidationError

from backend_v2.exceptions import ErrorCodes

logger = logging.getLogger(__name__)

__all__ = ["TypedCacheService"]


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
            Validated model instance, or None if key is absent, Redis unavailable, or corrupted.
        """
        if self.redis is None:
            return None

        raw_val = await self.redis.get(key)
        if raw_val is None:
            return None

        try:
            return model_cls.model_validate_json(raw_val)
        except ValidationError:
            logger.warning(
                "Corrupted cache payload encountered for key %s, auto-evicting",
                key,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            )
            try:
                await self.redis.delete(key)
            except Exception as e:  # noqa: QGR003 [REASON: Best-effort cache auto-eviction cleanup]
                logger.error("Failed to auto-evict corrupted cache key %s: %s", key, e)
            return None

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
