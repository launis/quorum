"""Real-Time Dual-Key Redis Kill-Switch and Per-Tenant Sliding-Window Rate Limiter.

Provides atomic O(1) Dual-Key Redis MGET session revocation checks (`RevocationCache`)
with strict Fail-Closed `503 Service Unavailable` semantics and per-organization /
public auth-edge sliding-window rate limiting (`TenantRateLimitService`).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Annotated, Any, Final

from pydantic import ConfigDict, Field

from backend_v2.exceptions import (
    AppException,
    AuthenticationError,
    ErrorCodes,
    ServiceUnavailableError,
    TokenLimitExceededError,
)
from backend_v2.models.auth import TokenData
from backend_v2.models.core_base import PrefixedUUID7
from backend_v2.models.dtos.base import BaseDTO
from backend_v2.settings import Settings, get_settings

logger = logging.getLogger(__name__)

PUBLIC_AUTH_EDGE_SCOPES: frozenset[str] = frozenset(
    {
        "POST /api/v2/iam/auth/exchange",
        "POST /api/v2/iam/auth/invitations/accept",
        "GET /api/v2/execution/executions/assignments/preview",
        "POST /api/v2/execution/executions/assignments/onboard",
    }
)

__all__ = [
    "PUBLIC_AUTH_EDGE_SCOPES",
    "RevocationCache",
    "TenantRateLimitService",
    "TenantRateLimitStatusDTO",
]

# Phase 1, Step 1: Bounded Redis timeout divisor (3.0s at 900s TTL) and MGET retry ceiling
_REDIS_TIMEOUT_TTL_DIVISOR: Final[float] = 300.0
_REVOCATION_MGET_MAX_ATTEMPTS: Final[int] = 2


class TenantRateLimitStatusDTO(BaseDTO):
    """Immutable snapshot of a tenant organization's sliding-window rate limit consumption.

    Attributes:
        organization_id: Target tenant organization identifier (org_<hex32>).
        rpm_current: Current sliding-window request count in the active window.
        rpm_limit: Configured tenant requests-per-minute ceiling.
        tpm_current: Current sliding-window token count in the active window.
        tpm_limit: Configured tenant tokens-per-minute ceiling.
        window_seconds: Sliding rate-limit window duration in seconds.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    organization_id: Annotated[
        PrefixedUUID7,
        Field(description="Target tenant organization identifier (org_<hex32>)"),
    ]
    rpm_current: Annotated[
        int,
        Field(ge=0, description="Current sliding-window request count in the active window"),
    ]
    rpm_limit: Annotated[
        int,
        Field(ge=1, description="Configured tenant requests-per-minute ceiling"),
    ]
    tpm_current: Annotated[
        int,
        Field(ge=0, description="Current sliding-window token count in the active window"),
    ]
    tpm_limit: Annotated[
        int,
        Field(ge=1, description="Configured tenant tokens-per-minute ceiling"),
    ]
    window_seconds: Annotated[
        int,
        Field(default=60, ge=1, description="Sliding rate-limit window duration in seconds"),
    ] = 60


class RevocationCache:
    """Fail-Closed Dual-Key Redis Kill-Switch for JWT jti and user-wide session revocation.

    Attributes:
        redis: Async Redis connection pool or client supporting `mget` and `set`.
    """

    def __init__(
        self,
        redis: Any | None = None,
        get_settings_fn: Callable[[], Settings] | None = None,
        timeout_seconds: float | None = None,
    ) -> None:
        """Initialize the RevocationCache.

        Args:
            redis: Async Redis client or ArqRedis connection pool.
            get_settings_fn: Optional callable returning application Settings.
            timeout_seconds: Optional explicit Redis I/O timeout override in seconds.
        """
        self.redis = redis
        self._get_settings_fn = get_settings_fn
        self._timeout_seconds = timeout_seconds

    def _resolve_settings(self) -> Settings:
        """Resolve active application Settings instance.

        Returns:
            Active Settings configuration object.
        """
        if self._get_settings_fn is not None:
            return self._get_settings_fn()
        return get_settings()

    def _resolve_timeout_seconds(self) -> float:
        """Resolve bounded Redis I/O timeout in seconds from Settings.

        Returns:
            Positive timeout duration in seconds.
        """
        if self._timeout_seconds is not None:
            return self._timeout_seconds
        settings = self._resolve_settings()
        return max(0.5, float(settings.iam_revocation_ttl_seconds) / _REDIS_TIMEOUT_TTL_DIVISOR)

    def _require_redis(self) -> Any:
        """Verify that an active Redis client is bound or fail closed with 503.

        Returns:
            Bound async Redis client.

        Raises:
            ServiceUnavailableError: With ErrorCodes.SERVICE_UNAVAILABLE if Redis is unconfigured.
        """
        if self.redis is None:
            msg = "Redis revocation cache client is not configured (Fail-Closed)."
            logger.error(
                "[RevocationCache] %s: %s",
                ErrorCodes.SERVICE_UNAVAILABLE.name,
                msg,
                extra={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
            )
            raise ServiceUnavailableError(
                message=msg,
                details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
            )
        return self.redis

    async def revoke_token_jti(self, jti: str, ttl_seconds: int) -> None:
        """Revoke an individual JWT session identifier (`jti`) for its remaining lifetime.

        Args:
            jti: RFC 7519 unique JWT identifier to revoke.
            ttl_seconds: Remaining token validity duration in seconds (bounded up to 900s).

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if jti is empty.
            ServiceUnavailableError: With ErrorCodes.SERVICE_UNAVAILABLE if Redis fails or times out.
        """
        # Phase 4, Step 4.1: Set revoked:jti:{jti} = "1" with bounded EX ttl_seconds
        if not jti or not jti.strip():
            msg = "Token jti cannot be empty for revocation."
            logger.error(
                "[RevocationCache] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        redis_client = self._require_redis()
        settings = self._resolve_settings()
        effective_ttl = max(1, min(settings.iam_revocation_ttl_seconds, int(ttl_seconds)))
        timeout_sec = self._resolve_timeout_seconds()
        key = f"revoked:jti:{jti.strip()}"

        try:
            async with asyncio.timeout(timeout_sec):
                await redis_client.set(key, "1", ex=effective_ttl)
        except AppException:
            raise
        except Exception as exc:
            msg = "Redis revocation store unavailable during token jti revocation (Fail-Closed)."
            logger.error(
                "[RevocationCache] %s: %s (%s)",
                ErrorCodes.SERVICE_UNAVAILABLE.name,
                msg,
                type(exc).__name__,
                exc_info=True,
                extra={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
            )
            raise ServiceUnavailableError(
                message=msg,
                details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
            ) from exc

    async def revoke_user_sessions(self, user_id: str, ttl_seconds: int = 900) -> None:
        """Activate the user-wide Redis kill-switch for administrative or global sign-out events.

        Args:
            user_id: Target user Opaque Stripe ID (`usr_<hex32>`).
            ttl_seconds: Kill-switch retention window in seconds (defaults to 900).

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if user_id is empty.
            ServiceUnavailableError: With ErrorCodes.SERVICE_UNAVAILABLE if Redis fails or times out.
        """
        # Phase 4, Step 4.1: Set revoked:usr:{user_id} = "1" with EX ttl_seconds
        if not user_id or not user_id.strip():
            msg = "User ID cannot be empty for session revocation."
            logger.error(
                "[RevocationCache] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        redis_client = self._require_redis()
        effective_ttl = max(1, int(ttl_seconds))
        timeout_sec = self._resolve_timeout_seconds()
        key = f"revoked:usr:{user_id.strip()}"

        try:
            async with asyncio.timeout(timeout_sec):
                await redis_client.set(key, "1", ex=effective_ttl)
        except AppException:
            raise
        except Exception as exc:
            msg = "Redis revocation store unavailable during user session revocation (Fail-Closed)."
            logger.error(
                "[RevocationCache] %s: %s (%s)",
                ErrorCodes.SERVICE_UNAVAILABLE.name,
                msg,
                type(exc).__name__,
                exc_info=True,
                extra={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value, "user_id": user_id.strip()},
            )
            raise ServiceUnavailableError(
                message=msg,
                details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
            ) from exc

    async def assert_not_revoked(self, token_data: TokenData) -> None:
        """Execute an atomic O(1) Dual-Key Redis MGET check to verify neither user nor jti is revoked.

        Args:
            token_data: Verified Quorum Local JWT claim payload.

        Raises:
            AuthenticationError: With ErrorCodes.AUTH_TOKEN_EXPIRED (401) if either key exists in Redis.
            ServiceUnavailableError: With ErrorCodes.SERVICE_UNAVAILABLE (503) if Redis is unreachable or times out.
        """
        # Phase 4, Step 4.1: Atomic O(1) Dual-Key MGET revoked:usr:{id} revoked:jti:{jti}
        redis_client = self._require_redis()
        user_key = f"revoked:usr:{token_data.id}"
        if token_data.jti is not None and token_data.jti.strip():
            jti_key = f"revoked:jti:{token_data.jti.strip()}"
        else:
            jti_key = "revoked:jti:none"

        # Phase 1, Step 1: Bounded 2-attempt MGET TimeoutError retry with Fail-Closed 503
        timeout_sec = self._resolve_timeout_seconds()
        results: Any = None
        for attempt in range(1, _REVOCATION_MGET_MAX_ATTEMPTS + 1):
            try:
                async with asyncio.timeout(timeout_sec):
                    results = await redis_client.mget(user_key, jti_key)
                break
            except AppException:
                raise
            except TimeoutError as exc:
                if attempt < _REVOCATION_MGET_MAX_ATTEMPTS:
                    logger.warning(
                        "[RevocationCache] Transient Redis MGET TimeoutError on attempt %d/%d; retrying immediately (user_id=%s).",
                        attempt,
                        _REVOCATION_MGET_MAX_ATTEMPTS,
                        token_data.id,
                        extra={"user_id": token_data.id, "attempt": attempt},
                    )
                    continue
                msg = "Redis revocation check failed; enforcing Fail-Closed security policy."
                logger.error(
                    "[RevocationCache] %s: %s (%s)",
                    ErrorCodes.SERVICE_UNAVAILABLE.name,
                    msg,
                    type(exc).__name__,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value, "user_id": token_data.id},
                )
                raise ServiceUnavailableError(
                    message=msg,
                    details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
                ) from exc
            except Exception as exc:
                msg = "Redis revocation check failed; enforcing Fail-Closed security policy."
                logger.error(
                    "[RevocationCache] %s: %s (%s)",
                    ErrorCodes.SERVICE_UNAVAILABLE.name,
                    msg,
                    type(exc).__name__,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value, "user_id": token_data.id},
                )
                raise ServiceUnavailableError(
                    message=msg,
                    details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
                ) from exc

        is_revoked = False
        if results is not None:
            for item in results:
                if item is not None:
                    normalized = item.decode("utf-8") if isinstance(item, bytes) else str(item)
                    if normalized not in ("", "0"):
                        is_revoked = True
                        break

        if is_revoked:
            msg = "Session token has been revoked or invalidated by security kill-switch."
            logger.error(
                "[RevocationCache] %s: %s (user_id=%s)",
                ErrorCodes.AUTH_TOKEN_EXPIRED.name,
                msg,
                token_data.id,
                extra={"error_code": ErrorCodes.AUTH_TOKEN_EXPIRED.value, "user_id": token_data.id},
            )
            raise AuthenticationError(
                message=msg,
                details={"error_code": ErrorCodes.AUTH_TOKEN_EXPIRED.value},
            )


class TenantRateLimitService:
    """Per-organization RPM/TPM sliding-window rate limiter and public auth-edge brute-force guard.

    Attributes:
        redis: Async Redis client supporting atomic `incr`, `incrby`, and `expire`.
        window_seconds: Sliding rate-limit window duration in seconds (defaults to 60).
    """

    def __init__(
        self,
        redis: Any | None = None,
        get_settings_fn: Callable[[], Settings] | None = None,
        timeout_seconds: float | None = None,
        window_seconds: int = 60,
    ) -> None:
        """Initialize the TenantRateLimitService.

        Args:
            redis: Async Redis client or connection pool.
            get_settings_fn: Optional callable returning application Settings.
            timeout_seconds: Optional explicit Redis I/O timeout override in seconds.
            window_seconds: Rate-limit sliding window duration in seconds.
        """
        self.redis = redis
        self._get_settings_fn = get_settings_fn
        self._timeout_seconds = timeout_seconds
        self.window_seconds = max(1, int(window_seconds))

    def _resolve_settings(self) -> Settings:
        """Resolve active application Settings instance.

        Returns:
            Active Settings configuration object.
        """
        if self._get_settings_fn is not None:
            return self._get_settings_fn()
        return get_settings()

    def _resolve_timeout_seconds(self) -> float:
        """Resolve bounded Redis I/O timeout in seconds from Settings.

        Returns:
            Positive timeout duration in seconds.
        """
        if self._timeout_seconds is not None:
            return self._timeout_seconds
        settings = self._resolve_settings()
        return max(0.5, float(settings.iam_revocation_ttl_seconds) / _REDIS_TIMEOUT_TTL_DIVISOR)

    def _require_redis(self) -> Any:
        """Verify that an active Redis client is bound or fail closed with 503.

        Returns:
            Bound async Redis client.

        Raises:
            ServiceUnavailableError: With ErrorCodes.SERVICE_UNAVAILABLE if Redis is unconfigured.
        """
        if self.redis is None:
            msg = "Redis rate-limit store is not configured (Fail-Closed)."
            logger.error(
                "[TenantRateLimitService] %s: %s",
                ErrorCodes.SERVICE_UNAVAILABLE.name,
                msg,
                extra={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
            )
            raise ServiceUnavailableError(
                message=msg,
                details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
            )
        return self.redis

    def _raise_rate_limit_exceeded(
        self,
        message: str,
        limit_type: str,
        current_value: int,
        limit_value: int,
        scope_id: str,
    ) -> None:
        """Log RFC 7807 error and raise a 429 TokenLimitExceededError with RATE_LIMIT_EXCEEDED.

        Args:
            message: Diagnostic rate-limit violation message.
            limit_type: Rate limit dimension identifier ("rpm", "tpm", or "auth_edge_rpm").
            current_value: Observed sliding-window counter value.
            limit_value: Configured ceiling value.
            scope_id: Organization ID or endpoint scope string.

        Raises:
            TokenLimitExceededError: With HTTP 429 status code and ErrorCodes.RATE_LIMIT_EXCEEDED.
        """
        logger.error(
            "[TenantRateLimitService] %s: %s (scope=%s, type=%s, current=%d, limit=%d)",
            ErrorCodes.RATE_LIMIT_EXCEEDED.name,
            message,
            scope_id,
            limit_type,
            current_value,
            limit_value,
            extra={
                "error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value,
                "limit_type": limit_type,
                "current": current_value,
                "limit": limit_value,
            },
        )
        err = TokenLimitExceededError(
            message=message,
            details={
                "error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value,
                "limit_type": limit_type,
                "current": current_value,
                "limit": limit_value,
            },
        )
        err.status_code = 429
        raise err

    async def check_and_increment_tenant_limits(
        self,
        organization_id: PrefixedUUID7,
        rpm_limit: int,
        tpm_limit: int,
        requested_tokens: int = 0,
        increment_requests: int = 1,
    ) -> TenantRateLimitStatusDTO:
        """Atomically increment and evaluate per-organization RPM and TPM sliding-window counters.

        Args:
            organization_id: Target tenant organization Opaque Stripe ID (`org_<hex32>`).
            rpm_limit: Organization requests-per-minute ceiling (`Organization.rpm_limit`).
            tpm_limit: Organization tokens-per-minute ceiling (`Organization.tpm_limit`).
            requested_tokens: Number of tokens to add to the organization's TPM window.
            increment_requests: Number of requests to add to the organization's RPM window.

        Returns:
            Validated TenantRateLimitStatusDTO reflecting current window counters.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if limits or increments are invalid.
            TokenLimitExceededError: With ErrorCodes.RATE_LIMIT_EXCEEDED (429) if RPM or TPM exceeds limit.
            ServiceUnavailableError: With ErrorCodes.SERVICE_UNAVAILABLE (503) if Redis is unreachable.
        """
        # Phase 4, Step 4.2: Per-organization atomic Redis sliding-window RPM & TPM enforcement
        if rpm_limit < 1 or tpm_limit < 1 or requested_tokens < 0 or increment_requests < 0:
            msg = "Invalid tenant rate-limit parameters."
            logger.error(
                "[TenantRateLimitService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "organization_id": organization_id},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        redis_client = self._require_redis()
        rpm_key = f"ratelimit:org:{organization_id}:rpm"
        tpm_key = f"ratelimit:org:{organization_id}:tpm"
        timeout_sec = self._resolve_timeout_seconds()

        try:
            async with asyncio.timeout(timeout_sec):
                current_rpm = int(await redis_client.incrby(rpm_key, increment_requests))
                if current_rpm == increment_requests and increment_requests > 0:
                    await redis_client.expire(rpm_key, self.window_seconds)

                current_tpm = int(await redis_client.incrby(tpm_key, requested_tokens))
                if current_tpm == requested_tokens and requested_tokens > 0:
                    await redis_client.expire(tpm_key, self.window_seconds)
        except AppException:
            raise
        except Exception as exc:
            msg = "Redis rate-limit store unavailable during tenant quota evaluation (Fail-Closed)."
            logger.error(
                "[TenantRateLimitService] %s: %s (%s)",
                ErrorCodes.SERVICE_UNAVAILABLE.name,
                msg,
                type(exc).__name__,
                exc_info=True,
                extra={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value, "organization_id": organization_id},
            )
            raise ServiceUnavailableError(
                message=msg,
                details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
            ) from exc

        if current_rpm > rpm_limit:
            self._raise_rate_limit_exceeded(
                message=f"Organization '{organization_id}' exceeded RPM rate limit ({current_rpm}/{rpm_limit}).",
                limit_type="rpm",
                current_value=current_rpm,
                limit_value=rpm_limit,
                scope_id=organization_id,
            )

        if current_tpm > tpm_limit:
            self._raise_rate_limit_exceeded(
                message=f"Organization '{organization_id}' exceeded TPM rate limit ({current_tpm}/{tpm_limit}).",
                limit_type="tpm",
                current_value=current_tpm,
                limit_value=tpm_limit,
                scope_id=organization_id,
            )

        return TenantRateLimitStatusDTO(
            organization_id=organization_id,
            rpm_current=current_rpm,
            rpm_limit=rpm_limit,
            tpm_current=current_tpm,
            tpm_limit=tpm_limit,
            window_seconds=self.window_seconds,
        )

    async def enforce_tenant_rate_limit(
        self,
        organization_id: PrefixedUUID7,
        rpm_limit: int,
        tpm_limit: int,
        requested_tokens: int = 0,
        increment_requests: int = 1,
    ) -> TenantRateLimitStatusDTO:
        """Enforce per-organization RPM and TPM limits and return the current window status DTO.

        Args:
            organization_id: Target tenant organization Opaque Stripe ID (`org_<hex32>`).
            rpm_limit: Organization requests-per-minute ceiling.
            tpm_limit: Organization tokens-per-minute ceiling.
            requested_tokens: Number of tokens to add to the organization's TPM window.
            increment_requests: Number of requests to add to the organization's RPM window.

        Returns:
            Validated TenantRateLimitStatusDTO reflecting current window counters.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if parameters are invalid.
            TokenLimitExceededError: With ErrorCodes.RATE_LIMIT_EXCEEDED (429) if limits are exceeded.
            ServiceUnavailableError: With ErrorCodes.SERVICE_UNAVAILABLE (503) if Redis fails.
        """
        return await self.check_and_increment_tenant_limits(
            organization_id=organization_id,
            rpm_limit=rpm_limit,
            tpm_limit=tpm_limit,
            requested_tokens=requested_tokens,
            increment_requests=increment_requests,
        )

    async def enforce_auth_edge_rate_limit(self, client_ip: str, endpoint_scope: str) -> int:
        """Enforce sliding-window IP rate limiting on public authentication, invitation, and assignment endpoints.

        Args:
            client_ip: Normalized caller IP address string.
            endpoint_scope: Canonical endpoint scope identifier (for example `POST /api/v2/iam/auth/exchange`).

        Returns:
            Current request count within the active 60-second window for the caller IP and scope.

        Raises:
            AppException: With ErrorCodes.VALIDATION_FAILED if client_ip or endpoint_scope is empty.
            TokenLimitExceededError: With ErrorCodes.RATE_LIMIT_EXCEEDED (429) when count exceeds auth_edge_rpm_limit.
            ServiceUnavailableError: With ErrorCodes.SERVICE_UNAVAILABLE (503) if Redis is unreachable.
        """
        # Phase 4, Step 4.2: Public auth/assignment edge IP brute-force protection
        if not client_ip or not client_ip.strip() or not endpoint_scope or not endpoint_scope.strip():
            msg = "Client IP and endpoint scope are required for edge rate limiting."
            logger.error(
                "[TenantRateLimitService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        redis_client = self._require_redis()
        settings = self._resolve_settings()
        edge_limit = settings.auth_edge_rpm_limit
        normalized_scope = endpoint_scope.strip()
        normalized_ip = client_ip.strip()
        edge_key = f"ratelimit:auth_edge:{normalized_scope}:{normalized_ip}"
        timeout_sec = self._resolve_timeout_seconds()

        try:
            async with asyncio.timeout(timeout_sec):
                current_count = int(await redis_client.incr(edge_key))
                if current_count == 1:
                    await redis_client.expire(edge_key, self.window_seconds)
        except AppException:
            raise
        except Exception as exc:
            msg = "Redis rate-limit store unavailable during auth edge rate limit check (Fail-Closed)."
            logger.error(
                "[TenantRateLimitService] %s: %s (%s)",
                ErrorCodes.SERVICE_UNAVAILABLE.name,
                msg,
                type(exc).__name__,
                exc_info=True,
                extra={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value, "endpoint_scope": normalized_scope},
            )
            raise ServiceUnavailableError(
                message=msg,
                details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value},
            ) from exc

        if current_count > edge_limit:
            self._raise_rate_limit_exceeded(
                message=f"Auth edge rate limit exceeded for scope '{normalized_scope}' ({current_count}/{edge_limit}).",
                limit_type="auth_edge_rpm",
                current_value=current_count,
                limit_value=edge_limit,
                scope_id=normalized_scope,
            )

        return current_count
