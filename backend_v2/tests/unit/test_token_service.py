"""Unit tests for token service, session token exchange, mandatory 2FA, and RAM JWT verification."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import jwt
import pytest
from pydantic import SecretStr

from backend_v2.exceptions import (
    AuthenticationError,
    ConflictError,
    ErrorCodes,
)
from backend_v2.models.auth import (
    TokenData,
    TokenExchangeRequestDTO,
    TokenExchangeResponseDTO,
    User,
    UserRole,
)
from backend_v2.models.core_base import generate_uuid7
from backend_v2.models.enums import SystemLocale
from backend_v2.services.auth import (
    AuthService,
    TokenService,
    UserRepository,
)
from backend_v2.settings import Settings, get_settings
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _jwt_secret() -> str:
    """Resolve active JWT secret key from Settings."""
    return get_settings().jwt_secret_key.get_secret_value()


def _jwt_algorithm() -> str:
    """Resolve active JWT signing algorithm from Settings."""
    return get_settings().jwt_algorithm


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide an in-memory unified repository for testing."""
    return InMemoryUnifiedWorkflowRepository()


@pytest.mark.asyncio
async def test_exchange_firebase_token_mfa_verified_positive(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Contract: Valid TokenExchangeRequestDTO with firebase.sign_in_second_factor='totp' issues 15-min Quorum Local JWT."""
    mock_settings = Settings(
        use_mock_llm=True,
        environment="production",
        use_firebase_auth=True,
        require_mfa=True,
        jwt_access_token_expire_minutes=15,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    active_user = User(
        id="usr_0195f3a0000070008000000000000501",
        firebase_uid="fb_uid_active_501",
        email="mfa_user@test.com",
        role=UserRole.MANAGER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000001",
    )
    await mock_repo.create_user(active_user)

    mock_fb = MagicMock()
    mock_fb.verify_id_token.return_value = {
        "uid": "fb_uid_active_501",
        "email": "mfa_user@test.com",
        "email_verified": True,
        "firebase": {"sign_in_second_factor": "totp"},
    }

    token_service = TokenService(
        repo=UserRepository(mock_repo),
        use_firebase=True,
        firebase_module=mock_fb,
        get_settings_fn=lambda: mock_settings,
    )

    payload = TokenExchangeRequestDTO(firebase_token="valid_firebase_id_token_mfa_12345")
    response = await token_service.exchange_firebase_token(payload)

    assert isinstance(response, TokenExchangeResponseDTO)
    assert response.token_type == "bearer"
    assert response.expires_in_seconds == 900
    assert response.user.id == active_user.id

    decoded = jwt.decode(
        response.access_token,
        mock_settings.jwt_secret_key.get_secret_value(),
        algorithms=[mock_settings.jwt_algorithm],
    )
    assert decoded["sub"] == active_user.id
    assert decoded["org"] == active_user.organization_id
    assert decoded["role"] == UserRole.MANAGER.value
    assert decoded["mfa"] is True
    assert isinstance(decoded["jti"], str) and len(decoded["jti"]) > 0
    assert isinstance(decoded["iat"], int)
    assert decoded["exp"] - decoded["iat"] == 900
    assert decoded["type"] == "access"


@pytest.mark.asyncio
async def test_exchange_firebase_token_missing_mfa_negative(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Contract: TokenExchangeRequestDTO lacking firebase.sign_in_second_factor when require_mfa=True raises MFA_REQUIRED."""
    mock_settings = Settings(
        use_mock_llm=True,
        environment="production",
        use_firebase_auth=True,
        require_mfa=True,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    mock_fb = MagicMock()
    mock_fb.verify_id_token.return_value = {
        "uid": "fb_uid_single_factor",
        "email": "single@test.com",
        "email_verified": True,
        "firebase": {"sign_in_provider": "password"},
    }

    token_service = TokenService(
        repo=UserRepository(mock_repo),
        use_firebase=True,
        firebase_module=mock_fb,
        get_settings_fn=lambda: mock_settings,
    )

    payload = TokenExchangeRequestDTO(firebase_token="single_factor_firebase_token_123")
    with pytest.raises(AuthenticationError) as exc_info:
        await token_service.exchange_firebase_token(payload)

    assert exc_info.value.error_code == ErrorCodes.MFA_REQUIRED
    assert ErrorCodes.MFA_REQUIRED.name in caplog.text


@pytest.mark.asyncio
async def test_exchange_firebase_token_uid_collision_negative(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Contract: Firebase token whose verified email matches a User bound to a different firebase_uid raises ConflictError."""
    mock_settings = Settings(
        use_mock_llm=True,
        environment="production",
        use_firebase_auth=True,
        require_mfa=True,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    bound_user = User(
        id="usr_0195f3a0000070008000000000000502",
        firebase_uid="existing_bound_firebase_uid_111",
        email="collision@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000001",
    )
    await mock_repo.create_user(bound_user)

    mock_fb = MagicMock()
    mock_fb.verify_id_token.return_value = {
        "uid": "different_attacker_firebase_uid_999",
        "email": "collision@test.com",
        "email_verified": True,
        "firebase": {"sign_in_second_factor": "totp"},
    }

    token_service = TokenService(
        repo=UserRepository(mock_repo),
        use_firebase=True,
        firebase_module=mock_fb,
        get_settings_fn=lambda: mock_settings,
    )

    payload = TokenExchangeRequestDTO(firebase_token="colliding_firebase_token_12345")
    with pytest.raises(ConflictError) as exc_info:
        await token_service.exchange_firebase_token(payload)

    assert exc_info.value.status_code == 409
    assert exc_info.value.details["error_code"] == ErrorCodes.USER_ALREADY_ASSIGNED.value
    assert ErrorCodes.USER_ALREADY_ASSIGNED.name in caplog.text


@pytest.mark.asyncio
async def test_exchange_headless_user_token_unauthorized_negative(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Contract: TokenExchangeRequestDTO(target_user_id=...) when allow_mock_tokens=False and secret mismatched raises 401."""
    mock_settings = Settings(
        use_mock_llm=True,
        environment="production",
        use_firebase_auth=True,
        service_auth_secret=SecretStr("expected_production_service_secret_xyz"),
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    token_service = TokenService(
        repo=UserRepository(mock_repo),
        use_firebase=True,
        get_settings_fn=lambda: mock_settings,
    )

    # Missing service_auth_secret
    payload_missing = TokenExchangeRequestDTO(target_user_id="usr_0195f3a0000070008000000000000503")
    with pytest.raises(AuthenticationError) as exc_missing:
        await token_service.exchange_firebase_token(payload_missing)
    assert exc_missing.value.status_code == 401
    assert exc_missing.value.error_code == ErrorCodes.PERMISSION_DENIED
    assert ErrorCodes.PERMISSION_DENIED.name in caplog.text

    # Mismatched service_auth_secret
    payload_mismatch = TokenExchangeRequestDTO(
        target_user_id="usr_0195f3a0000070008000000000000503",
        service_auth_secret=SecretStr("wrong_secret_value"),
    )
    with pytest.raises(AuthenticationError) as exc_mismatch:
        await token_service.exchange_firebase_token(payload_mismatch)
    assert exc_mismatch.value.status_code == 401
    assert exc_mismatch.value.error_code == ErrorCodes.PERMISSION_DENIED


@pytest.mark.asyncio
async def test_verify_token_ram_decode_zero_db_queries_positive(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Contract: Valid signed Quorum Local JWT passed to TokenService.verify_token decodes in RAM with 0 DB queries."""
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        require_mfa=True,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    user = User(
        id="usr_0195f3a0000070008000000000000401",
        email="ramdecode@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000001",
    )
    await mock_repo.create_user(user)

    user_repo = UserRepository(mock_repo)
    token_service = TokenService(
        repo=user_repo,
        use_firebase=False,
        get_settings_fn=lambda: mock_settings,
    )

    exchange_res = await token_service.exchange_firebase_token(
        TokenExchangeRequestDTO(target_user_id=user.id)
    )
    calls_before_verify = mock_repo.get_call_count("get_user")
    assert calls_before_verify == 1

    token_data = await token_service.verify_token(exchange_res.access_token)
    assert mock_repo.get_call_count("get_user") == calls_before_verify

    assert token_data.id == user.id
    assert token_data.role == UserRole.ADMIN
    assert token_data.organization_id == user.organization_id
    assert token_data.email == user.email
    assert token_data.mfa_verified is True
    assert token_data.jti is not None
    assert token_data.iat is not None
    assert token_data.exp is not None


@pytest.mark.asyncio
async def test_verify_token_expired_or_mock_prefix_negative(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Contract: Expired Quorum Local JWT or legacy 'mock-token:...' string passed to verify_token raises AuthenticationError."""
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        require_mfa=True,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    token_service = TokenService(
        repo=UserRepository(mock_repo),
        use_firebase=False,
        get_settings_fn=lambda: mock_settings,
    )

    expired_token = jwt.encode(
        {
            "sub": "usr_0195f3a0000070008000000000000301",
            "org": "org_0195f3a0000070008000000000000001",
            "role": UserRole.MEMBER.value,
            "mfa": True,
            "jti": str(generate_uuid7()),
            "iat": int(time.time()) - 1800,
            "exp": int(time.time()) - 900,
            "type": "access",
        },
        mock_settings.jwt_secret_key.get_secret_value(),
        algorithm=mock_settings.jwt_algorithm,
    )

    with pytest.raises(AuthenticationError) as exc_exp:
        await token_service.verify_token(expired_token)
    assert exc_exp.value.error_code == ErrorCodes.AUTH_TOKEN_EXPIRED

    with pytest.raises(AuthenticationError) as exc_mock:
        await token_service.verify_token("mock-token:usr_0195f3a0000070008000000000000301")
    assert exc_mock.value.error_code == ErrorCodes.AUTHENTICATION_FAILED


@pytest.mark.asyncio
async def test_exchange_firebase_token_first_time_email_bind_and_headless_secret_positive(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify first-time pre-provisioned account bind by verified email and headless service_auth_secret exchange."""
    secret = SecretStr("shared_ci_secret_token_987654321")
    mock_settings = Settings(
        use_mock_llm=True,
        environment="production",
        use_firebase_auth=True,
        require_mfa=True,
        service_auth_secret=secret,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    preprovisioned_user = User(
        id="usr_0195f3a0000070008000000000000601",
        firebase_uid=None,
        email="preprovisioned@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000001",
    )
    await mock_repo.create_user(preprovisioned_user)

    mock_fb = MagicMock()
    mock_fb.verify_id_token.return_value = {
        "uid": "newly_bound_fb_uid_601",
        "email": "preprovisioned@test.com",
        "email_verified": True,
        "firebase": {"sign_in_second_factor": "phone"},
    }

    token_service = TokenService(
        repo=UserRepository(mock_repo),
        use_firebase=True,
        firebase_module=mock_fb,
        get_settings_fn=lambda: mock_settings,
    )

    res_bind = await token_service.exchange_firebase_token(
        TokenExchangeRequestDTO(firebase_token="first_time_bind_firebase_token")
    )
    assert res_bind.user.id == preprovisioned_user.id
    assert res_bind.user.firebase_uid == "newly_bound_fb_uid_601"
    persisted_user = await mock_repo.get_user(preprovisioned_user.id)
    assert persisted_user is not None
    assert persisted_user.firebase_uid == "newly_bound_fb_uid_601"

    # Headless exchange using valid service_auth_secret in production
    res_headless = await token_service.exchange_firebase_token(
        TokenExchangeRequestDTO(
            target_user_id=preprovisioned_user.id,
            service_auth_secret=secret,
        )
    )
    assert res_headless.user.id == preprovisioned_user.id


@pytest.mark.asyncio
async def test_exchange_firebase_token_inactive_deleted_or_revoked_user_negative(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify exchange_firebase_token rejects missing, inactive, soft-deleted, or Redis-revoked users."""
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        require_mfa=True,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    inactive_user = User(
        id="usr_0195f3a0000070008000000000000701",
        email="inactive@test.com",
        role=UserRole.MEMBER,
        is_active=False,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000001",
    )
    deleted_user = User(
        id="usr_0195f3a0000070008000000000000702",
        email="deleted@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        deleted_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000001",
    )
    revoked_user = User(
        id="usr_0195f3a0000070008000000000000703",
        email="revoked@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000001",
    )
    await mock_repo.create_user(inactive_user)
    await mock_repo.create_user(deleted_user)
    await mock_repo.create_user(revoked_user)

    mock_revocation = MagicMock()
    mock_revocation.assert_not_revoked = AsyncMock(
        side_effect=AuthenticationError(
            message="User session is revoked.",
            details={"error_code": ErrorCodes.AUTH_TOKEN_EXPIRED.value},
        )
    )

    token_service = TokenService(
        repo=UserRepository(mock_repo),
        use_firebase=False,
        get_settings_fn=lambda: mock_settings,
        revocation_cache=mock_revocation,
    )

    # Missing user
    with pytest.raises(AuthenticationError) as exc_missing:
        await token_service.exchange_firebase_token(
            TokenExchangeRequestDTO(target_user_id="usr_0195f3a0000070008000000000000799")
        )
    assert exc_missing.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Inactive user
    with pytest.raises(AuthenticationError) as exc_inactive:
        await token_service.exchange_firebase_token(
            TokenExchangeRequestDTO(target_user_id=inactive_user.id)
        )
    assert exc_inactive.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Soft-deleted user
    with pytest.raises(AuthenticationError) as exc_deleted:
        await token_service.exchange_firebase_token(
            TokenExchangeRequestDTO(target_user_id=deleted_user.id)
        )
    assert exc_deleted.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Revoked user lock in RevocationCache
    with pytest.raises(AuthenticationError) as exc_revoked:
        await token_service.exchange_firebase_token(
            TokenExchangeRequestDTO(target_user_id=revoked_user.id)
        )
    assert exc_revoked.value.error_code == ErrorCodes.AUTH_TOKEN_EXPIRED


@pytest.mark.asyncio
async def test_verify_token_impersonation_and_claim_validation_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify RFC 8693 impersonation actor_id extraction and negative claim validation branches in verify_token."""
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        require_mfa=True,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.services.auth.get_settings", lambda: mock_settings)

    auth = AuthService(mock_repo, use_firebase=False)
    imp_token = auth.token_service.create_impersonation_token(
        target_id="usr_0195f3a0000070008000000000000101",
        duration_seconds=900,
        organization_id="org_0195f3a0000070008000000000000001",
        role=UserRole.ADMIN,
        email="imp@test.com",
        actor_id="usr_0195f3a00000700a83fd6b3d77c748f4",
    )
    token_data: TokenData = await auth.verify_token(imp_token)
    assert token_data.id == "usr_0195f3a0000070008000000000000101"
    assert token_data.role == UserRole.ADMIN
    assert token_data.organization_id == "org_0195f3a0000070008000000000000001"
    assert token_data.email == "imp@test.com"
    assert token_data.actor_id == "usr_0195f3a00000700a83fd6b3d77c748f4"
    assert token_data.mfa_verified is True

    secret = mock_settings.jwt_secret_key.get_secret_value()
    alg = mock_settings.jwt_algorithm

    # Missing sub claim
    no_sub = jwt.encode({"exp": int(time.time()) + 900, "role": "admin", "mfa": True}, secret, algorithm=alg)
    with pytest.raises(AuthenticationError) as exc_sub:
        await auth.verify_token(no_sub)
    assert exc_sub.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Missing mfa claim when require_mfa=True
    no_mfa = jwt.encode(
        {"sub": "usr_0195f3a0000070008000000000000101", "exp": int(time.time()) + 900, "role": "admin", "mfa": False},
        secret,
        algorithm=alg,
    )
    with pytest.raises(AuthenticationError) as exc_mfa:
        await auth.verify_token(no_mfa)
    assert exc_mfa.value.error_code == ErrorCodes.MFA_REQUIRED

    # Missing role claim
    no_role = jwt.encode(
        {"sub": "usr_0195f3a0000070008000000000000101", "exp": int(time.time()) + 900, "mfa": True},
        secret,
        algorithm=alg,
    )
    with pytest.raises(AuthenticationError) as exc_role:
        await auth.verify_token(no_role)
    assert exc_role.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Invalid role claim
    bad_role = jwt.encode(
        {"sub": "usr_0195f3a0000070008000000000000101", "exp": int(time.time()) + 900, "mfa": True, "role": "invalid"},
        secret,
        algorithm=alg,
    )
    with pytest.raises(AuthenticationError) as exc_bad_role:
        await auth.verify_token(bad_role)
    assert exc_bad_role.value.error_code == ErrorCodes.AUTHENTICATION_FAILED


@pytest.mark.asyncio
async def test_auth_service_init_firebase_fallback_and_transport_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test AuthService fallback when firebase is not installed and Firebase SDK verification errors."""
    monkeypatch.setattr("backend_v2.services.auth.firebase_auth_module", None)
    auth = AuthService(mock_repo, use_firebase=True)
    assert auth.use_firebase is False

    mock_settings = Settings(
        use_mock_llm=True,
        environment="production",
        use_firebase_auth=True,
        require_mfa=True,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    mock_fb = MagicMock()
    mock_fb.verify_id_token.side_effect = RuntimeError("Firebase transport error")
    token_service = TokenService(
        repo=UserRepository(mock_repo),
        use_firebase=True,
        firebase_module=mock_fb,
        get_settings_fn=lambda: mock_settings,
    )
    with pytest.raises(AuthenticationError) as exc_fb:
        await token_service.exchange_firebase_token(
            TokenExchangeRequestDTO(firebase_token="broken_firebase_token_12345")
        )
    assert exc_fb.value.error_code == ErrorCodes.AUTHENTICATION_FAILED
