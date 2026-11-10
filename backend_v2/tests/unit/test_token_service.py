"""Unit tests for token service, session token exchange, mandatory 2FA, and RAM JWT verification."""

from __future__ import annotations

import time
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import jwt
import pytest
from pydantic import SecretStr

from backend_v2.exceptions import (
    AppException,
    AuthenticationError,
    ConfigurationError,
    ConflictError,
    ErrorCodes,
)
from backend_v2.models.auth import (
    SYSTEM_ROOT_USER_ID,
    SystemOrganizations,
    TenantSecretCreateDTO,
    TokenData,
    TokenExchangeRequestDTO,
    TokenExchangeResponseDTO,
    User,
    UserRole,
)
from backend_v2.models.core_base import generate_uuid7
from backend_v2.models.enums import LLMProvider, SecretScope, SecretStorageMode, SystemLocale
from backend_v2.services.auth import (
    AuthService,
    SecretService,
    TokenService,
    UserRepository,
    initialize_firebase_admin_from_secrets,
)
from backend_v2.settings import Settings
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork


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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
    """Contract: TokenExchangeRequestDTO(target_user_id=...) when service_auth_secret is missing or mismatched raises 401."""
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
async def test_headless_cli_exchange_requires_service_auth_secret_even_in_development(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify headless CLI token exchange requires service_auth_secret unconditionally even in development."""
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        service_auth_secret=SecretStr("dev_cli_shared_secret_123456"),
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    token_service = TokenService(
        repo=UserRepository(mock_repo),
        use_firebase=False,
        get_settings_fn=lambda: mock_settings,
    )

    with pytest.raises(AuthenticationError) as exc_info:
        await token_service.exchange_firebase_token(
            TokenExchangeRequestDTO(
                target_user_id="usr_0195f3a00000700a83fd6b3d77c748f4",
                service_auth_secret=None,
            )
        )
    assert exc_info.value.error_code == ErrorCodes.PERMISSION_DENIED
    assert ErrorCodes.PERMISSION_DENIED.name in caplog.text


@pytest.mark.asyncio
async def test_verify_token_ram_decode_zero_db_queries_positive(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Contract: Valid signed Quorum Local JWT passed to TokenService.verify_token decodes in RAM with 0 DB queries."""
    shared_secret = SecretStr("test_cli_service_secret_ram_decode")
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        require_mfa=True,
        service_auth_secret=shared_secret,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    user = User(
        id="usr_0195f3a0000070008000000000000401",
        email="ramdecode@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(UTC),
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
        TokenExchangeRequestDTO(target_user_id=user.id, service_auth_secret=shared_secret)
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
        created_at=datetime.now(UTC),
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
    shared_secret = SecretStr("test_cli_service_secret_negative_users")
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        require_mfa=True,
        service_auth_secret=shared_secret,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    inactive_user = User(
        id="usr_0195f3a0000070008000000000000701",
        email="inactive@test.com",
        role=UserRole.MEMBER,
        is_active=False,
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000001",
    )
    deleted_user = User(
        id="usr_0195f3a0000070008000000000000702",
        email="deleted@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        deleted_at=datetime.now(UTC),
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000001",
    )
    revoked_user = User(
        id="usr_0195f3a0000070008000000000000703",
        email="revoked@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(UTC),
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
            TokenExchangeRequestDTO(
                target_user_id="usr_0195f3a0000070008000000000000799",
                service_auth_secret=shared_secret,
            )
        )
    assert exc_missing.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Inactive user
    with pytest.raises(AuthenticationError) as exc_inactive:
        await token_service.exchange_firebase_token(
            TokenExchangeRequestDTO(target_user_id=inactive_user.id, service_auth_secret=shared_secret)
        )
    assert exc_inactive.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Soft-deleted user
    with pytest.raises(AuthenticationError) as exc_deleted:
        await token_service.exchange_firebase_token(
            TokenExchangeRequestDTO(target_user_id=deleted_user.id, service_auth_secret=shared_secret)
        )
    assert exc_deleted.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Revoked user lock in RevocationCache
    with pytest.raises(AuthenticationError) as exc_revoked:
        await token_service.exchange_firebase_token(
            TokenExchangeRequestDTO(target_user_id=revoked_user.id, service_auth_secret=shared_secret)
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


@pytest.mark.asyncio
async def test_token_service_boundary_and_negative_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify negative and boundary branches in TokenService for uninitialized Firebase, missing uid, and email binding."""
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        require_mfa=False,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)

    # Default _resolve_settings() without get_settings_fn and firebase_auth=None
    service_no_fb = TokenService(repo=UserRepository(mock_repo), use_firebase=False)
    with pytest.raises(AuthenticationError) as exc_no_fb:
        await service_no_fb.exchange_firebase_token(
            TokenExchangeRequestDTO(firebase_token="valid_length_firebase_token")
        )
    assert exc_no_fb.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Bypassed DTO via model_construct lacking both firebase_token and target_user_id
    empty_payload = TokenExchangeRequestDTO.model_construct(
        firebase_token=None,
        target_user_id=None,
        service_auth_secret=None,
    )
    with pytest.raises(AuthenticationError) as exc_empty:
        await service_no_fb.exchange_firebase_token(empty_payload)
    assert exc_empty.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Missing 'uid' claim when require_mfa=False
    mock_fb = MagicMock()
    mock_fb.verify_id_token.return_value = {"email": "nouid@test.com", "email_verified": True}
    service_fb = TokenService(
        repo=UserRepository(mock_repo),
        use_firebase=True,
        firebase_module=mock_fb,
    )
    with pytest.raises(AuthenticationError) as exc_no_uid:
        await service_fb.exchange_firebase_token(TokenExchangeRequestDTO(firebase_token="token_without_uid_claim"))
    assert exc_no_uid.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Email not verified -> returns None -> raises AUTHENTICATION_FAILED
    mock_fb.verify_id_token.return_value = {
        "uid": "fb_unverified_email_uid",
        "email": "unverified@test.com",
        "email_verified": False,
    }
    with pytest.raises(AuthenticationError) as exc_unverified:
        await service_fb.exchange_firebase_token(TokenExchangeRequestDTO(firebase_token="token_unverified_email"))
    assert exc_unverified.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Verified email not matching any user in repository -> returns None -> raises AUTHENTICATION_FAILED
    mock_fb.verify_id_token.return_value = {
        "uid": "fb_unknown_email_uid",
        "email": "unknown_user@test.com",
        "email_verified": True,
    }
    with pytest.raises(AuthenticationError) as exc_unknown_email:
        await service_fb.exchange_firebase_token(TokenExchangeRequestDTO(firebase_token="token_unknown_email_123"))
    assert exc_unknown_email.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    # Non-actor impersonation token (actor_id=None)
    imp_no_actor = service_no_fb.create_impersonation_token(
        target_id="usr_0195f3a0000070008000000000000101",
        duration_seconds=600,
        organization_id="org_0195f3a0000070008000000000000001",
        role=UserRole.MEMBER,
        email="noactor@test.com",
        actor_id=None,
    )
    verified_no_actor = await service_no_fb.verify_token(imp_no_actor)
    assert verified_no_actor.actor_id is None
    assert verified_no_actor.id == "usr_0195f3a0000070008000000000000101"


@pytest.mark.asyncio
async def test_initialize_firebase_admin_from_secrets_initializes_app_from_vertex_sa(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify initialize_firebase_admin_from_secrets decrypts vertex_ai SA JSON and initializes firebase_admin."""
    uow = InMemoryUnitOfWork()
    secret_service = SecretService(entity_adapter=uow.entities)
    initiator = TokenData(
        id=SYSTEM_ROOT_USER_ID,
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
        email="root@example.com",
        mfa_verified=True,
    )
    sa_json = '{"type": "service_account", "project_id": "quorum-test-proj", "client_email": "sa@test.iam.gserviceaccount.com"}'
    await secret_service.upsert_tenant_secret(
        initiator=initiator,
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=LLMProvider.VERTEX_AI.value,
            plaintext_secret=SecretStr(sa_json),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
    )

    mock_fb_admin = MagicMock()
    mock_fb_admin._apps = {}
    mock_fb_creds = MagicMock()
    mock_cert_obj = MagicMock()
    mock_fb_creds.Certificate.return_value = mock_cert_obj

    monkeypatch.setattr("backend_v2.services.auth.token_service.firebase_admin", mock_fb_admin)
    monkeypatch.setattr("backend_v2.services.auth.token_service.firebase_credentials_module", mock_fb_creds)

    # No-op when use_firebase_auth is False
    disabled_settings = Settings(use_mock_llm=True, use_firebase_auth=False)
    await initialize_firebase_admin_from_secrets(secret_service, disabled_settings)
    mock_fb_creds.Certificate.assert_not_called()

    # Initializes Certificate and default app when use_firebase_auth is True and _apps is empty
    enabled_settings = Settings(use_mock_llm=True, use_firebase_auth=True)
    await initialize_firebase_admin_from_secrets(secret_service, enabled_settings)
    mock_fb_creds.Certificate.assert_called_once_with(
        {
            "type": "service_account",
            "project_id": "quorum-test-proj",
            "client_email": "sa@test.iam.gserviceaccount.com",
        }
    )
    mock_fb_admin.initialize_app.assert_called_once_with(mock_cert_obj)

    # Idempotent no-op when _apps is already populated
    mock_fb_admin._apps = {"[DEFAULT]": MagicMock()}
    await initialize_firebase_admin_from_secrets(secret_service, enabled_settings)
    assert mock_fb_admin.initialize_app.call_count == 1

    # Fails fast when firebase_admin is not installed
    monkeypatch.setattr("backend_v2.services.auth.token_service.firebase_admin", None)
    with pytest.raises(ConfigurationError) as exc_missing_sdk:
        await initialize_firebase_admin_from_secrets(secret_service, enabled_settings)
    assert exc_missing_sdk.value.error_code == ErrorCodes.CONFIGURATION_ERROR


@pytest.mark.asyncio
async def test_initialize_firebase_admin_from_secrets_fails_fast_on_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify initialize_firebase_admin_from_secrets raises ConfigurationError on non-JSON or malformed SA secret."""
    uow = InMemoryUnitOfWork()
    secret_service = SecretService(entity_adapter=uow.entities)
    initiator = TokenData(
        id=SYSTEM_ROOT_USER_ID,
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
        email="root@example.com",
        mfa_verified=True,
    )

    mock_fb_admin = MagicMock()
    mock_fb_admin._apps = {}
    mock_fb_creds = MagicMock()
    monkeypatch.setattr("backend_v2.services.auth.token_service.firebase_admin", mock_fb_admin)
    monkeypatch.setattr("backend_v2.services.auth.token_service.firebase_credentials_module", mock_fb_creds)
    enabled_settings = Settings(use_mock_llm=True, use_firebase_auth=True)

    # Case 1: Non-JSON prefix
    await secret_service.upsert_tenant_secret(
        initiator=initiator,
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=LLMProvider.VERTEX_AI.value,
            plaintext_secret=SecretStr("not-a-json-object"),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
    )
    with pytest.raises(ConfigurationError) as exc_non_json:
        await initialize_firebase_admin_from_secrets(secret_service, enabled_settings)
    assert exc_non_json.value.error_code == ErrorCodes.CONFIGURATION_ERROR

    # Case 2: Starts with '{' but invalid JSON syntax
    await secret_service.upsert_tenant_secret(
        initiator=initiator,
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=LLMProvider.VERTEX_AI.value,
            plaintext_secret=SecretStr("{malformed_json_payload"),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
    )
    with pytest.raises(ConfigurationError) as exc_bad_syntax:
        await initialize_firebase_admin_from_secrets(secret_service, enabled_settings)
    assert exc_bad_syntax.value.error_code == ErrorCodes.CONFIGURATION_ERROR

    # Case 3: Valid JSON object but Certificate() raises ValueError
    await secret_service.upsert_tenant_secret(
        initiator=initiator,
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=LLMProvider.VERTEX_AI.value,
            plaintext_secret=SecretStr('{"type": "invalid_cert"}'),
            storage_mode=SecretStorageMode.ENVELOPE_KMS,
        ),
    )
    mock_fb_creds.Certificate.side_effect = ValueError("Invalid certificate fields")
    with pytest.raises(ConfigurationError) as exc_cert_err:
        await initialize_firebase_admin_from_secrets(secret_service, enabled_settings)
    assert exc_cert_err.value.error_code == ErrorCodes.CONFIGURATION_ERROR


@pytest.mark.asyncio
async def test_create_impersonation_token_ssot_ttl_and_boundary_validation(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verify create_impersonation_token resolves default TTL from Settings SSOT and enforces ISTQB BVA guards."""
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        jwt_access_token_expire_minutes=20,
    )
    token_service = TokenService(
        repo=UserRepository(mock_repo),
        use_firebase=False,
        get_settings_fn=lambda: mock_settings,
    )

    # Positive 1: Omit duration_seconds -> resolves 20 * 60 = 1200 seconds from Settings SSOT
    default_ttl_jwt = token_service.create_impersonation_token(
        target_id="usr_0195f3a0000070008000000000000101",
        organization_id=SystemOrganizations.ROOT_SYSTEM.value,
        role=UserRole.ADMIN,
    )
    decoded_default = jwt.decode(
        default_ttl_jwt,
        mock_settings.jwt_secret_key.get_secret_value(),
        algorithms=[mock_settings.jwt_algorithm],
    )
    assert decoded_default["exp"] - decoded_default["iat"] == 1200

    # Positive 2: Lower valid boundary (min = 1 second)
    min_ttl_jwt = token_service.create_impersonation_token(
        target_id="usr_0195f3a0000070008000000000000101",
        duration_seconds=1,
    )
    decoded_min = jwt.decode(
        min_ttl_jwt,
        mock_settings.jwt_secret_key.get_secret_value(),
        algorithms=[mock_settings.jwt_algorithm],
    )
    assert decoded_min["exp"] - decoded_min["iat"] == 1

    # Negative 1 (BVA min - 1): duration_seconds = 0 and -5 raise AppException(VALIDATION_FAILED)
    for invalid_duration in (0, -5):
        with pytest.raises(AppException) as exc_dur:
            token_service.create_impersonation_token(
                target_id="usr_0195f3a0000070008000000000000101",
                duration_seconds=invalid_duration,
            )
        assert exc_dur.value.status_code == 400
        assert exc_dur.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert ErrorCodes.VALIDATION_FAILED.name in caplog.text

    # Negative 2: Empty or whitespace target_id raises AppException(VALIDATION_FAILED)
    for invalid_target in ("", "   "):
        with pytest.raises(AppException) as exc_target:
            token_service.create_impersonation_token(
                target_id=invalid_target,
                duration_seconds=60,
            )
        assert exc_target.value.status_code == 400
        assert exc_target.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
