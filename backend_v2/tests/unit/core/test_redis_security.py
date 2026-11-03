"""Unit and ISTQB boundary tests for RevocationCache and TenantRateLimitService."""

from __future__ import annotations

import logging
import time

import pytest

from backend_v2.core.redis_security import (
    PUBLIC_AUTH_EDGE_SCOPES,
    RevocationCache,
    TenantRateLimitService,
    TenantRateLimitStatusDTO,
)
from backend_v2.exceptions import (
    AppException,
    AuthenticationError,
    ErrorCodes,
    ServiceUnavailableError,
    TokenLimitExceededError,
)
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import generate_opaque_id, generate_uuid7
from backend_v2.models.enums import EntityPrefix
from backend_v2.settings import get_settings


class InMemoryAsyncRedisFake:
    """Deterministic in-memory async Redis fake supporting atomic MGET, SET EX, INCR, INCRBY, and EXPIRE.

    Attributes:
        store: Mapping of Redis keys to string values.
        ttls: Mapping of Redis keys to configured TTL seconds.
        mget_calls: Recorded list of key tuples passed to mget.
        fault: Optional exception to raise on the next Redis command.
    """

    def __init__(self) -> None:
        """Initialize the in-memory Redis store and telemetry counters."""
        self.store: dict[str, str] = {}
        self.ttls: dict[str, int] = {}
        self.mget_calls: list[tuple[str, ...]] = []
        self.fault: Exception | None = None
        self.fault_remaining: int | None = None

    def inject_fault(self, exc: Exception, fault_count: int | None = None) -> None:
        """Configure a transport/timeout fault to be raised on subsequent Redis operations.

        Args:
            exc: Exception instance to raise.
            fault_count: Optional number of operations that should raise before auto-clearing.
        """
        self.fault = exc
        self.fault_remaining = fault_count

    def clear_faults(self) -> None:
        """Clear any injected fault state."""
        self.fault = None
        self.fault_remaining = None

    def _check_fault(self) -> None:
        """Raise the configured fault if present."""
        if self.fault is not None:
            exc_to_raise = self.fault
            if self.fault_remaining is not None:
                self.fault_remaining -= 1
                if self.fault_remaining <= 0:
                    self.fault = None
                    self.fault_remaining = None
            raise exc_to_raise

    async def set(self, key: str, value: str, ex: int | None = None) -> bool:
        """Set a string value in the in-memory store with an optional expiration TTL.

        Args:
            key: Redis key string.
            value: String payload to store.
            ex: Optional expiration time in seconds.

        Returns:
            True upon completion.
        """
        self._check_fault()
        self.store[key] = str(value)
        if ex is not None:
            self.ttls[key] = int(ex)
        return True

    async def mget(self, *keys: str) -> list[str | None]:
        """Atomically fetch multiple keys in O(1) roundtrip order.

        Args:
            *keys: Sequence of Redis key strings to query.

        Returns:
            List of string values or None for missing keys.
        """
        normalized_keys: list[str] = []
        for item in keys:
            if isinstance(item, (list, tuple)):
                normalized_keys.extend(str(k) for k in item)
            else:
                normalized_keys.append(str(item))
        key_tuple = tuple(normalized_keys)
        self.mget_calls.append(key_tuple)
        self._check_fault()
        return [self.store[k] if k in self.store else None for k in key_tuple]

    async def incr(self, key: str) -> int:
        """Atomically increment an integer counter by 1.

        Args:
            key: Redis counter key.

        Returns:
            Updated integer counter value.
        """
        return await self.incrby(key, 1)

    async def incrby(self, key: str, amount: int) -> int:
        """Atomically increment an integer counter by the specified amount.

        Args:
            key: Redis counter key.
            amount: Increment delta.

        Returns:
            Updated integer counter value.
        """
        self._check_fault()
        current = int(self.store[key]) if key in self.store else 0
        updated = current + int(amount)
        self.store[key] = str(updated)
        return updated

    async def expire(self, key: str, seconds: int) -> bool:
        """Set a TTL expiration window in seconds on an existing Redis key.

        Args:
            key: Redis key string.
            seconds: Expiration window in seconds.

        Returns:
            True if the key exists and TTL was set, False otherwise.
        """
        self._check_fault()
        self.ttls[key] = int(seconds)
        return True


@pytest.fixture
def fake_redis() -> InMemoryAsyncRedisFake:
    """Provide an isolated in-memory async Redis fake."""
    return InMemoryAsyncRedisFake()


@pytest.mark.asyncio
async def test_revocation_cache_dual_key_mget_unrevoked_positive(
    fake_redis: InMemoryAsyncRedisFake,
) -> None:
    """Contract: Dual-key MGET completes in < 1 ms when unrevoked and isolates single-session jti logout."""
    cache = RevocationCache(redis=fake_redis)
    user_id = generate_opaque_id(EntityPrefix.USER)
    org_id = generate_opaque_id(EntityPrefix.ORG)
    jti_1 = str(generate_uuid7())
    jti_2 = str(generate_uuid7())

    token_1 = TokenData(
        id=user_id,
        role=UserRole.MEMBER,
        organization_id=org_id,
        email="user@acme.com",
        mfa_verified=True,
        jti=jti_1,
    )
    token_2 = TokenData(
        id=user_id,
        role=UserRole.MEMBER,
        organization_id=org_id,
        email="user@acme.com",
        mfa_verified=True,
        jti=jti_2,
    )

    # Warm up settings singleton cache prior to sub-millisecond MGET latency benchmark
    _ = get_settings()

    start_ns = time.perf_counter_ns()
    await cache.assert_not_revoked(token_1)
    elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000.0

    assert elapsed_ms < 1.0
    assert fake_redis.mget_calls[-1] == (f"revoked:usr:{user_id}", f"revoked:jti:{jti_1}")

    # Revoke jti #1 on single-session logout; jti #1 fails while newly minted jti #2 for same user passes
    await cache.revoke_token_jti(jti_1, ttl_seconds=420)
    assert fake_redis.store[f"revoked:jti:{jti_1}"] == "1"
    assert fake_redis.ttls[f"revoked:jti:{jti_1}"] == 420

    with pytest.raises(AuthenticationError) as exc_info:
        await cache.assert_not_revoked(token_1)
    assert exc_info.value.status_code == 401
    assert exc_info.value.details["error_code"] == ErrorCodes.AUTH_TOKEN_EXPIRED.value

    # Second session jti #2 for the exact same user continues to succeed
    await cache.assert_not_revoked(token_2)


@pytest.mark.asyncio
async def test_revocation_cache_revoked_user_or_jti_negative(
    fake_redis: InMemoryAsyncRedisFake,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Contract: Revoked user kill-switch or revoked token jti logs AUTH_TOKEN_EXPIRED and raises 401 AuthenticationError."""
    cache = RevocationCache(redis=fake_redis)
    user_id = generate_opaque_id(EntityPrefix.USER)
    org_id = generate_opaque_id(EntityPrefix.ORG)
    jti_a = str(generate_uuid7())
    jti_b = str(generate_uuid7())

    token_a = TokenData(
        id=user_id,
        role=UserRole.ADMIN,
        organization_id=org_id,
        email="admin@acme.com",
        mfa_verified=True,
        jti=jti_a,
    )
    token_b = TokenData(
        id=user_id,
        role=UserRole.ADMIN,
        organization_id=org_id,
        email="admin@acme.com",
        mfa_verified=True,
        jti=jti_b,
    )

    # Case 1: Revoked jti
    await cache.revoke_token_jti(jti_a, ttl_seconds=1200)
    # Clamped to iam_revocation_ttl_seconds (900s)
    assert fake_redis.ttls[f"revoked:jti:{jti_a}"] == 900

    with caplog.at_level(logging.ERROR), pytest.raises(AuthenticationError) as exc_jti:
        await cache.assert_not_revoked(token_a)
    assert exc_jti.value.status_code == 401
    assert exc_jti.value.details["error_code"] == ErrorCodes.AUTH_TOKEN_EXPIRED.value
    assert ErrorCodes.AUTH_TOKEN_EXPIRED.name in caplog.text

    # Case 2: Global user kill-switch (revoked:usr:{id}) blocks even unrevoked jti_b
    caplog.clear()
    await cache.revoke_user_sessions(user_id, ttl_seconds=900)
    assert fake_redis.store[f"revoked:usr:{user_id}"] == "1"
    assert fake_redis.ttls[f"revoked:usr:{user_id}"] == 900

    with caplog.at_level(logging.ERROR), pytest.raises(AuthenticationError) as exc_usr:
        await cache.assert_not_revoked(token_b)
    assert exc_usr.value.status_code == 401
    assert exc_usr.value.details["error_code"] == ErrorCodes.AUTH_TOKEN_EXPIRED.value
    assert ErrorCodes.AUTH_TOKEN_EXPIRED.name in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "injected_error",
    [
        ConnectionError("Redis connection refused"),
        TimeoutError("Redis MGET timed out"),
        OSError("Socket closed unexpectedly"),
    ],
)
async def test_revocation_cache_redis_down_fail_closed_error_path(
    fake_redis: InMemoryAsyncRedisFake,
    caplog: pytest.LogCaptureFixture,
    injected_error: Exception,
) -> None:
    """Contract: Redis connection or timeout error during revocation check enforces Fail-Closed 503 ServiceUnavailableError."""
    cache = RevocationCache(redis=fake_redis)
    token_data = TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.MEMBER,
        organization_id=generate_opaque_id(EntityPrefix.ORG),
        email="member@acme.com",
        mfa_verified=True,
        jti=str(generate_uuid7()),
    )

    try:
        fake_redis.inject_fault(injected_error)
        with caplog.at_level(logging.ERROR), pytest.raises(ServiceUnavailableError) as exc_info:
            await cache.assert_not_revoked(token_data)
        assert exc_info.value.status_code == 503
        assert exc_info.value.details["error_code"] == ErrorCodes.SERVICE_UNAVAILABLE.value
        assert ErrorCodes.SERVICE_UNAVAILABLE.name in caplog.text

        caplog.clear()
        with caplog.at_level(logging.ERROR), pytest.raises(ServiceUnavailableError):
            await cache.revoke_token_jti(str(generate_uuid7()), ttl_seconds=300)
        assert ErrorCodes.SERVICE_UNAVAILABLE.name in caplog.text

        caplog.clear()
        with caplog.at_level(logging.ERROR), pytest.raises(ServiceUnavailableError):
            await cache.revoke_user_sessions(token_data.id, ttl_seconds=900)
        assert ErrorCodes.SERVICE_UNAVAILABLE.name in caplog.text
    finally:
        fake_redis.clear_faults()


@pytest.mark.asyncio
async def test_revocation_cache_missing_redis_client_And_empty_inputs_fail_fast(
    fake_redis: InMemoryAsyncRedisFake,
) -> None:
    """Verify None Redis client fails closed with 503 and empty jti/user_id inputs fail fast with 400."""
    unconfigured_cache = RevocationCache(redis=None)
    token_data = TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.MEMBER,
        jti=str(generate_uuid7()),
    )
    with pytest.raises(ServiceUnavailableError) as exc_none:
        await unconfigured_cache.assert_not_revoked(token_data)
    assert exc_none.value.status_code == 503

    cache = RevocationCache(redis=fake_redis)
    with pytest.raises(AppException) as exc_empty_jti:
        await cache.revoke_token_jti("   ", ttl_seconds=60)
    assert exc_empty_jti.value.status_code == 400
    assert exc_empty_jti.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as exc_empty_usr:
        await cache.revoke_user_sessions("", ttl_seconds=60)
    assert exc_empty_usr.value.status_code == 400
    assert exc_empty_usr.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_tenant_rate_limit_service_bva_boundary(
    fake_redis: InMemoryAsyncRedisFake,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Contract: ISTQB BVA at rpm_limit - 1, rpm_limit, rpm_limit + 1 and tpm_limit - 1, tpm_limit, tpm_limit + 1."""
    limiter = TenantRateLimitService(redis=fake_redis)
    org_id = generate_opaque_id(EntityPrefix.ORG)
    rpm_limit = 5
    tpm_limit = 1000

    # 1. RPM BVA: requests 1..4 (up to rpm_limit - 1) and request 5 (rpm_limit) succeed
    for expected_rpm in range(1, rpm_limit):
        status_dto = await limiter.check_and_increment_tenant_limits(
            organization_id=org_id,
            rpm_limit=rpm_limit,
            tpm_limit=tpm_limit,
            requested_tokens=100,
        )
        assert isinstance(status_dto, TenantRateLimitStatusDTO)
        assert status_dto.rpm_current == expected_rpm

    # Boundary: exact rpm_limit (5th request, 500 total tokens) succeeds
    at_limit_dto = await limiter.check_and_increment_tenant_limits(
        organization_id=org_id,
        rpm_limit=rpm_limit,
        tpm_limit=tpm_limit,
        requested_tokens=100,
    )
    assert at_limit_dto.rpm_current == rpm_limit
    assert at_limit_dto.tpm_current == 500

    # Boundary + 1: rpm_limit + 1 (6th request) logs RATE_LIMIT_EXCEEDED and raises 429 TokenLimitExceededError
    caplog.clear()
    with caplog.at_level(logging.ERROR), pytest.raises(TokenLimitExceededError) as rpm_exc:
        await limiter.check_and_increment_tenant_limits(
            organization_id=org_id,
            rpm_limit=rpm_limit,
            tpm_limit=tpm_limit,
            requested_tokens=10,
        )
    assert rpm_exc.value.status_code == 429
    assert rpm_exc.value.details["error_code"] == ErrorCodes.RATE_LIMIT_EXCEEDED.value
    assert ErrorCodes.RATE_LIMIT_EXCEEDED.name in caplog.text

    # 2. TPM BVA on a second organization: tpm_limit - 1 (999), tpm_limit (1000), and tpm_limit + 1 (1001)
    org_id_tpm = generate_opaque_id(EntityPrefix.ORG)
    high_rpm_limit = 100

    # tpm_limit - 1 (999 tokens) succeeds
    dto_tpm_minus_one = await limiter.check_and_increment_tenant_limits(
        organization_id=org_id_tpm,
        rpm_limit=high_rpm_limit,
        tpm_limit=tpm_limit,
        requested_tokens=tpm_limit - 1,
    )
    assert dto_tpm_minus_one.tpm_current == tpm_limit - 1

    # tpm_limit (999 + 1 = 1000 tokens) succeeds
    dto_tpm_exact = await limiter.check_and_increment_tenant_limits(
        organization_id=org_id_tpm,
        rpm_limit=high_rpm_limit,
        tpm_limit=tpm_limit,
        requested_tokens=1,
    )
    assert dto_tpm_exact.tpm_current == tpm_limit

    # tpm_limit + 1 (1000 + 1 = 1001 tokens) raises 429 TokenLimitExceededError with RATE_LIMIT_EXCEEDED
    caplog.clear()
    with caplog.at_level(logging.ERROR), pytest.raises(TokenLimitExceededError) as tpm_exc:
        await limiter.check_and_increment_tenant_limits(
            organization_id=org_id_tpm,
            rpm_limit=high_rpm_limit,
            tpm_limit=tpm_limit,
            requested_tokens=1,
        )
    assert tpm_exc.value.status_code == 429
    assert tpm_exc.value.details["error_code"] == ErrorCodes.RATE_LIMIT_EXCEEDED.value
    assert ErrorCodes.RATE_LIMIT_EXCEEDED.name in caplog.text


@pytest.mark.asyncio
async def test_tenant_rate_limit_service_auth_edge_ip_bva_and_fail_closed(
    fake_redis: InMemoryAsyncRedisFake,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify enforce_auth_edge_rate_limit across public auth/assignment scopes at limit - 1, limit, and limit + 1."""
    limiter = TenantRateLimitService(redis=fake_redis)
    edge_limit = get_settings().auth_edge_rpm_limit
    client_ip = "203.0.113.42"
    scope = "POST /api/v2/iam/auth/exchange"
    assert scope in PUBLIC_AUTH_EDGE_SCOPES

    for count in range(1, edge_limit):
        current = await limiter.enforce_auth_edge_rate_limit(client_ip=client_ip, endpoint_scope=scope)
        assert current == count

    # Exact edge_limit succeeds
    at_limit = await limiter.enforce_auth_edge_rate_limit(client_ip=client_ip, endpoint_scope=scope)
    assert at_limit == edge_limit
    assert fake_redis.ttls[f"ratelimit:auth_edge:{scope}:{client_ip}"] == 60

    # edge_limit + 1 logs RATE_LIMIT_EXCEEDED and raises 429 TokenLimitExceededError
    caplog.clear()
    with caplog.at_level(logging.ERROR), pytest.raises(TokenLimitExceededError) as edge_exc:
        await limiter.enforce_auth_edge_rate_limit(client_ip=client_ip, endpoint_scope=scope)
    assert edge_exc.value.status_code == 429
    assert edge_exc.value.details["error_code"] == ErrorCodes.RATE_LIMIT_EXCEEDED.value
    assert ErrorCodes.RATE_LIMIT_EXCEEDED.name in caplog.text

    # Negative validation on empty client_ip or endpoint_scope
    with pytest.raises(AppException) as empty_ip_exc:
        await limiter.enforce_auth_edge_rate_limit(client_ip=" ", endpoint_scope=scope)
    assert empty_ip_exc.value.status_code == 400

    # Fail-Closed 503 when Redis fails during rate limit evaluation
    try:
        fake_redis.inject_fault(ConnectionError("Redis unreachable"))
        with pytest.raises(ServiceUnavailableError) as redis_exc:
            await limiter.enforce_auth_edge_rate_limit(client_ip="198.51.100.7", endpoint_scope=scope)
        assert redis_exc.value.status_code == 503
    finally:
        fake_redis.clear_faults()


@pytest.mark.asyncio
async def test_tenant_rate_limit_service_validation_and_redis_failure_branches(
    fake_redis: InMemoryAsyncRedisFake,
) -> None:
    """Verify TenantRateLimitService validation, delegation, custom settings/timeouts, and Redis failure branches."""
    org_id = generate_opaque_id(EntityPrefix.ORG)

    # 1. Unconfigured Redis client fails closed with 503
    unconfigured = TenantRateLimitService(redis=None)
    with pytest.raises(ServiceUnavailableError) as none_exc:
        await unconfigured.enforce_tenant_rate_limit(
            organization_id=org_id,
            rpm_limit=10,
            tpm_limit=1000,
        )
    assert none_exc.value.status_code == 503

    # 2. Custom get_settings_fn and timeout_seconds + enforce_tenant_rate_limit delegation
    limiter = TenantRateLimitService(
        redis=fake_redis,
        get_settings_fn=get_settings,
        timeout_seconds=1.5,
        window_seconds=60,
    )
    dto = await limiter.enforce_tenant_rate_limit(
        organization_id=org_id,
        rpm_limit=10,
        tpm_limit=1000,
        requested_tokens=50,
    )
    assert dto.rpm_current == 1
    assert dto.tpm_current == 50

    # 3. Invalid parameters fail fast with 400 VALIDATION_FAILED
    with pytest.raises(AppException) as invalid_exc:
        await limiter.check_and_increment_tenant_limits(
            organization_id=org_id,
            rpm_limit=0,
            tpm_limit=1000,
        )
    assert invalid_exc.value.status_code == 400
    assert invalid_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    # 4. Redis failure during check_and_increment_tenant_limits fails closed with 503
    try:
        fake_redis.inject_fault(ConnectionError("Redis cluster down"))
        with pytest.raises(ServiceUnavailableError) as err_503:
            await limiter.check_and_increment_tenant_limits(
                organization_id=org_id,
                rpm_limit=10,
                tpm_limit=1000,
                requested_tokens=10,
            )
        assert err_503.value.status_code == 503
        assert err_503.value.details["error_code"] == ErrorCodes.SERVICE_UNAVAILABLE.value
    finally:
        fake_redis.clear_faults()


@pytest.mark.asyncio
async def test_revocation_cache_custom_settings_and_missing_jti_fallback(
    fake_redis: InMemoryAsyncRedisFake,
) -> None:
    """Verify RevocationCache custom settings/timeout injection and token_data with jti=None."""
    cache = RevocationCache(
        redis=fake_redis,
        get_settings_fn=get_settings,
        timeout_seconds=1.0,
    )
    user_id = generate_opaque_id(EntityPrefix.USER)
    token_without_jti = TokenData(
        id=user_id,
        role=UserRole.MEMBER,
        jti=None,
    )
    await cache.assert_not_revoked(token_without_jti)
    assert fake_redis.mget_calls[-1] == (f"revoked:usr:{user_id}", "revoked:jti:none")


@pytest.mark.asyncio
async def test_revocation_cache_transient_timeout_single_retry_recovery_and_exhaustion(
    fake_redis: InMemoryAsyncRedisFake,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify single transient MGET TimeoutError recovers on retry while 2 consecutive timeouts fail closed with 503."""
    cache = RevocationCache(redis=fake_redis)
    assert cache._resolve_timeout_seconds() == 3.0

    token_data = TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.MEMBER,
        organization_id=generate_opaque_id(EntityPrefix.ORG),
        email="member@acme.com",
        mfa_verified=True,
        jti=str(generate_uuid7()),
    )

    try:
        # 1. Single transient TimeoutError recovers on immediate retry (attempt 2/2)
        fake_redis.mget_calls.clear()
        fake_redis.inject_fault(TimeoutError("Transient loopback stall"), fault_count=1)
        with caplog.at_level(logging.WARNING):
            await cache.assert_not_revoked(token_data)
        assert len(fake_redis.mget_calls) == 2
        assert "Transient Redis MGET TimeoutError on attempt 1/2" in caplog.text

        # 2. Persistent TimeoutError across both attempts fails closed with 503 ServiceUnavailableError
        caplog.clear()
        fake_redis.mget_calls.clear()
        fake_redis.inject_fault(TimeoutError("Persistent Redis stall"), fault_count=2)
        with caplog.at_level(logging.ERROR), pytest.raises(ServiceUnavailableError) as exc_info:
            await cache.assert_not_revoked(token_data)
        assert len(fake_redis.mget_calls) == 2
        assert exc_info.value.status_code == 503
        assert exc_info.value.details["error_code"] == ErrorCodes.SERVICE_UNAVAILABLE.value
        assert ErrorCodes.SERVICE_UNAVAILABLE.name in caplog.text
    finally:
        fake_redis.clear_faults()
