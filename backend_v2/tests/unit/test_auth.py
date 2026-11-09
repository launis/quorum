"""Unit tests for unified AuthService facade, IAM router endpoints, and Auth models."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from fakeredis.aioredis import FakeRedis
from fastapi import Request
from pydantic import ValidationError
from starlette.datastructures import Address

from backend_v2.api.routers.iam.auth import (
    accept_invitation,
    exchange_firebase_token,
    firebase_user_deleted_webhook,
    get_my_profile,
    impersonate_user,
    list_available_roles,
    logout_user,
)
from backend_v2.core.redis_security import TenantRateLimitService
from backend_v2.exceptions import (
    AppException,
    AuthenticationError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
    ServiceUnavailableError,
    TokenLimitExceededError,
)
from backend_v2.models.auth import (
    SYSTEM_ROOT_USER_ID,
    ImpersonationRequest,
    LogoutRequestDTO,
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    SystemOrganizations,
    TokenData,
    TokenExchangeRequestDTO,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)
from backend_v2.models.enums import SystemLocale
from backend_v2.services.auth import AuthService
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository

USER_1_ID = "usr_0195f3a0000070008000000000000001"
USER_2_ID = "usr_0195f3a0000070008000000000000002"
ADMIN_1_ID = "usr_0195f3a0000070008000000000000003"
ADMIN_2_ID = "usr_0195f3a0000070008000000000000004"
ORG_1_ID = "org_0195f3a0000070008000000000000011"
ORG_2_ID = "org_0195f3a0000070008000000000000012"


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide an in-memory unified repository for testing."""
    return InMemoryUnifiedWorkflowRepository()


@pytest.mark.asyncio
async def test_auth_service_init(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Verify AuthService initializes with firebase flag."""
    service = AuthService(mock_repo, use_firebase=False)
    assert service.use_firebase is False


@pytest.mark.asyncio
async def test_auth_service_list_users(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Verify ROOT user lists all users across organizations."""
    service = AuthService(mock_repo, use_firebase=False)

    u1 = User(
        id=USER_1_ID,
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id=ORG_1_ID,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    u2 = User(
        id=USER_2_ID,
        email="test2@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id=ORG_2_ID,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
    )

    await mock_repo.create_user(u1)
    await mock_repo.create_user(u2)

    initiator = TokenData(id=SYSTEM_ROOT_USER_ID, role=UserRole.ROOT, email="root@test.com")
    users = await service.list_users(initiator)
    assert len(users) == 2


@pytest.mark.asyncio
async def test_auth_service_get_user(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Verify ROOT user retrieves user by canonical ID."""
    service = AuthService(mock_repo, use_firebase=False)

    test_user = User(
        id=USER_1_ID,
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id=ORG_1_ID,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(test_user)

    initiator = TokenData(id=SYSTEM_ROOT_USER_ID, role=UserRole.ROOT, email="root@test.com")
    user = await service.get_user(initiator, USER_1_ID)
    assert user.id == USER_1_ID


@pytest.mark.asyncio
async def test_auth_service_tenant_isolation_and_permission_denied_failure(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify tenant isolation allows same-org ADMIN and raises PermissionDeniedError on cross-org access."""
    service = AuthService(mock_repo, use_firebase=False)

    test_user = User(
        id=USER_1_ID,
        email="target@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id=ORG_1_ID,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(test_user)

    initiator_admin = TokenData(
        id=ADMIN_1_ID,
        role=UserRole.ADMIN,
        organization_id=ORG_1_ID,
        email="admin@test.com",
    )

    user = await service.get_user(initiator_admin, USER_1_ID)
    assert user.id == USER_1_ID

    initiator_wrong_org = TokenData(
        id=ADMIN_2_ID,
        role=UserRole.ADMIN,
        organization_id=ORG_2_ID,
        email="admin2@test.com",
    )

    with pytest.raises(PermissionDeniedError):
        await service.get_user(initiator_wrong_org, USER_1_ID)


@pytest.mark.asyncio
async def test_auth_router_list_roles() -> None:
    """Verify list_available_roles returns all canonical role names."""
    roles = await list_available_roles()
    assert "ROOT" in roles


@pytest.mark.asyncio
async def test_auth_router_get_my_profile(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Verify get_my_profile returns the authenticated user's profile."""
    service = AuthService(mock_repo, use_firebase=False)
    mock_user = User(
        id=USER_1_ID,
        email="me@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id=ORG_1_ID,
        language=SystemLocale.EN,
        theme_mode="system",
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
    )
    await mock_repo.create_user(mock_user)
    user = await get_my_profile(
        current_user=TokenData(id=USER_1_ID, role=UserRole.MEMBER, organization_id=ORG_1_ID),
        auth_service=service,
    )
    assert user == mock_user


@pytest.mark.asyncio
async def test_auth_router_exchange_logout_and_impersonate_flow(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify exchange_firebase_token, logout_user, and impersonate_user router endpoints and AuthService methods."""
    from backend_v2.settings import Settings

    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        require_mfa=True,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.services.auth.get_settings", lambda: mock_settings)

    mock_audit = MagicMock()
    mock_audit.log_event = AsyncMock()
    mock_revocation = MagicMock()
    mock_revocation.assert_not_revoked = AsyncMock()
    mock_revocation.revoke_token_jti = AsyncMock()
    mock_revocation.revoke_user_sessions = AsyncMock()
    mock_fb = MagicMock()

    service = AuthService(
        mock_repo,
        use_firebase=True,
        audit_service=mock_audit,
        firebase_auth=mock_fb,
        revocation_cache=mock_revocation,
    )

    target_user = User(
        id=USER_1_ID,
        email="target@test.com",
        firebase_uid="fb_uid_logout_1",
        role=UserRole.ADMIN,
        is_active=True,
        organization_id=ORG_1_ID,
        language=SystemLocale.EN,
        theme_mode="system",
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
    )
    await mock_repo.create_user(target_user)

    mock_req = MagicMock(spec=Request)
    mock_req.client = Address("203.0.113.10", 50000)
    rate_limiter = TenantRateLimitService(redis=FakeRedis(), get_settings_fn=lambda: mock_settings)
    exchange_res = await exchange_firebase_token(
        request=mock_req,
        payload=TokenExchangeRequestDTO(target_user_id=USER_1_ID),
        auth_service=service,
        rate_limit_service=rate_limiter,
    )
    assert exchange_res.user.id == USER_1_ID
    assert exchange_res.expires_in_seconds == 900

    verified_token = await service.verify_token(exchange_res.access_token)
    logout_res = await logout_user(
        payload=LogoutRequestDTO(revoke_all_sessions=True),
        current_user=verified_token,
        auth_service=service,
    )
    assert logout_res.status == "logged_out"
    assert logout_res.revoked_jti == verified_token.jti
    assert logout_res.all_sessions_revoked is True
    mock_revocation.revoke_token_jti.assert_awaited_once()
    mock_revocation.revoke_user_sessions.assert_awaited_once_with(USER_1_ID, ttl_seconds=900)
    mock_fb.revoke_refresh_tokens.assert_called_once_with("fb_uid_logout_1")
    mock_audit.log_event.assert_awaited()

    root_token = TokenData(
        id=SYSTEM_ROOT_USER_ID,
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        email="root@test.com",
    )
    imp_res = await impersonate_user(
        payload=ImpersonationRequest(target_id=USER_1_ID, reason="Forensic audit debugging"),
        current_user=root_token,
        auth_service=service,
    )
    assert imp_res.target_id == USER_1_ID
    assert imp_res.reason == "Forensic audit debugging"
    decoded_imp = await service.verify_token(imp_res.access_token)
    assert decoded_imp.id == USER_1_ID
    assert decoded_imp.actor_id == SYSTEM_ROOT_USER_ID
    assert decoded_imp.mfa_verified is True


@pytest.mark.asyncio
async def test_auth_router_impersonate_and_profile_negative(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Negative: Verify non-ROOT impersonation, missing target user, and missing profile raise typed AppExceptions."""
    service = AuthService(mock_repo, use_firebase=False)

    non_root = TokenData(id=ADMIN_1_ID, role=UserRole.ADMIN, organization_id=ORG_1_ID)
    with pytest.raises(PermissionDeniedError) as exc_perm:
        await impersonate_user(
            payload=ImpersonationRequest(target_id=USER_1_ID, reason="Unauthorized attempt"),
            current_user=non_root,
            auth_service=service,
        )
    assert exc_perm.value.error_code == ErrorCodes.PERMISSION_DENIED

    root_token = TokenData(
        id=SYSTEM_ROOT_USER_ID,
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
    )
    with pytest.raises(ResourceNotFoundError):
        await impersonate_user(
            payload=ImpersonationRequest(target_id=USER_2_ID, reason="Missing user test"),
            current_user=root_token,
            auth_service=service,
        )

    with pytest.raises(AuthenticationError) as exc_me:
        await get_my_profile(
            current_user=TokenData(id=USER_2_ID, role=UserRole.MEMBER, organization_id=ORG_1_ID),
            auth_service=service,
        )
    assert exc_me.value.error_code == ErrorCodes.AUTHENTICATION_FAILED


def test_system_organizations_is_system() -> None:
    """Verify SystemOrganizations.is_system recognizes canonical ROOT_SYSTEM and SYSTEM sentinel."""
    assert SystemOrganizations.is_system(SystemOrganizations.ROOT_SYSTEM) is True
    assert SystemOrganizations.is_system("SYSTEM") is True
    assert SystemOrganizations.is_system(None) is True
    assert SystemOrganizations.is_system("") is True
    assert SystemOrganizations.is_system("org_0195f3a00000700e8531d2ed8a6641f6") is False


def test_auth_models_validation_coverage_and_invalid_inputs_error() -> None:
    """Verify Organization, User, OrganizationCreate, and TokenData validation and negative error cases."""
    now = datetime.now(UTC)
    org = Organization(
        id=ORG_1_ID,
        name="Valid Name",
        is_active=True,
        tier="standard",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=100.0,
        tpm_limit=5000,
        rpm_limit=10,
        created_at=now,
        contact_email="test@org.com",
        billing_id="bill_12345",
        allowed_email_domains=["org.com"],
    )
    assert org.created_at == now
    assert org.allowed_email_domains == ["org.com"]

    with pytest.raises(ValidationError):
        Organization(
            id=ORG_1_ID,
            name="Valid Name",
            is_active=True,
            tier="standard",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=-5.0,
            tpm_limit=5000,
            rpm_limit=10,
            allowed_email_domains=[],
        )

    with pytest.raises(ValidationError):
        Organization(
            id="   ",
            name="Valid Name",
            is_active=True,
            tier="standard",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=10.0,
            tpm_limit=5000,
            rpm_limit=10,
            allowed_email_domains=[],
        )

    with pytest.raises(ValidationError):
        Organization(
            id=ORG_1_ID,
            name="Valid Name",
            is_active=True,
            tier="standard",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=10.0,
            tpm_limit=5000,
            rpm_limit=10,
            contact_email="   ",
            allowed_email_domains=[],
        )

    user = User(
        id=USER_1_ID,
        email="user@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="dark",
        created_at=now,
        created_by=ADMIN_1_ID,
        name="Valid User",
        organization_id=ORG_1_ID,
        firebase_uid="fb_uid_12345",
    )
    assert user.created_at == now
    assert user.firebase_uid == "fb_uid_12345"

    with pytest.raises(ValidationError):
        User(
            id=USER_1_ID,
            email="user@test.com",
            role=UserRole.ADMIN,
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="dark",
            created_at=now,
            name="   ",
        )

    with pytest.raises(ValidationError):
        User(
            id="   ",
            email="user@test.com",
            role=UserRole.ADMIN,
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="dark",
            created_at=now,
        )

    with pytest.raises(ValidationError):
        User(
            id=USER_1_ID,
            email="user@test.com",
            role=UserRole.ADMIN,
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="dark",
            created_at=now,
            created_by="   ",
        )

    org_create = OrganizationCreate(
        name="Valid Name",
        admin_email="admin@test.com",
        admin_password="secretpassword",
        admin_name="Admin Name",
        tpm_limit=5000,
        rpm_limit=10,
    )
    assert org_create.name == "Valid Name"

    with pytest.raises(ValidationError):
        OrganizationCreate(
            name="   ",
            admin_email="admin@test.com",
            admin_password="secretpassword",
            admin_name="Admin Name",
            tpm_limit=5000,
            rpm_limit=10,
        )

    token = TokenData(id=USER_1_ID, role=UserRole.ADMIN, organization_id=ORG_1_ID, email="a@b.com")
    assert token.id == USER_1_ID

    with pytest.raises(ValidationError):
        TokenData(id="   ", role=UserRole.ADMIN)

    with pytest.raises(ValidationError):
        TokenData(id=USER_1_ID, role=UserRole.ADMIN, organization_id="   ")


@pytest.mark.asyncio
async def test_auth_service_facade_delegates_all_operations(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """TC-P4-39: AuthService facade delegates token, org, and user operations cleanly."""
    mock_fb = MagicMock()
    auth_service = AuthService(mock_repo, use_firebase=True, firebase_auth=mock_fb)
    assert auth_service.token_service is not None
    assert auth_service.org_service is not None
    assert auth_service.user_service is not None

    assert auth_service.use_firebase is True
    assert auth_service.token_service.use_firebase is True
    assert auth_service.org_service.use_firebase is True
    assert auth_service.user_service.use_firebase is True

    assert auth_service.firebase_auth is mock_fb
    assert auth_service.token_service.firebase_auth is mock_fb
    assert auth_service.org_service.firebase_auth is mock_fb
    assert auth_service.user_service.firebase_auth is mock_fb

    with pytest.raises(AttributeError):
        del auth_service.use_firebase

    with pytest.raises(AttributeError):
        del auth_service.firebase_auth

    init_file = Path(__file__).parents[2] / "services" / "auth" / "__init__.py"
    line_count = len(init_file.read_text(encoding="utf-8").splitlines())
    assert line_count < 300, f"AuthService facade line count ({line_count}) exceeds 300 lines cap"

    mock_init_fb = MagicMock()
    monkeypatch.setattr(auth_service.token_service, "_init_firebase", mock_init_fb)
    auth_service._init_firebase()
    mock_init_fb.assert_called_once()

    mock_create_imp = MagicMock(return_value="mock_jwt_impersonate")
    monkeypatch.setattr(auth_service.token_service, "create_impersonation_token", mock_create_imp)
    token_str = auth_service.create_impersonation_token(USER_1_ID, 1800)
    assert token_str == "mock_jwt_impersonate"
    mock_create_imp.assert_called_once_with(target_id=USER_1_ID, duration_seconds=1800)

    mock_verify_tok = AsyncMock(return_value=TokenData(id=USER_1_ID, role=UserRole.ADMIN, organization_id=ORG_1_ID))
    monkeypatch.setattr(auth_service.token_service, "verify_token", mock_verify_tok)
    tok = await auth_service.verify_token("bearer_xyz")
    assert tok.id == USER_1_ID
    mock_verify_tok.assert_awaited_once_with("bearer_xyz")

    now = datetime.now(UTC)
    dummy_org = Organization(
        id=ORG_1_ID,
        name="Delegate Org",
        is_active=True,
        tier="standard",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=100.0,
        tpm_limit=5000,
        rpm_limit=10,
        created_at=now,
        allowed_email_domains=[],
    )
    root_token = TokenData(
        id=SYSTEM_ROOT_USER_ID,
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
    )
    dummy_org_create = OrganizationCreate(
        name="New Org",
        admin_email="admin@delegate.com",
        admin_password="delegatepassword",
        admin_name="Delegate Admin",
        tpm_limit=5000,
        rpm_limit=10,
    )
    monkeypatch.setattr(auth_service.org_service, "create_organization", AsyncMock(return_value=dummy_org))
    created_org = await auth_service.create_organization(root_token, dummy_org_create)
    assert created_org.id == ORG_1_ID

    mock_del_org = AsyncMock()
    monkeypatch.setattr(auth_service.org_service, "delete_organization", mock_del_org)
    await auth_service.delete_organization(root_token, ORG_1_ID, force=True)
    mock_del_org.assert_awaited_once_with(initiator=root_token, target_org_id=ORG_1_ID, force=True)

    monkeypatch.setattr(auth_service.org_service, "list_organizations", AsyncMock(return_value=[dummy_org]))
    orgs = await auth_service.list_organizations(root_token)
    assert len(orgs) == 1

    monkeypatch.setattr(auth_service.org_service, "get_organization", AsyncMock(return_value=dummy_org))
    fetched_org = await auth_service.get_organization(root_token, ORG_1_ID)
    assert fetched_org.id == ORG_1_ID

    dummy_org_update = OrganizationUpdateDTO(name="Updated Delegate Org")
    monkeypatch.setattr(auth_service.org_service, "update_organization", AsyncMock(return_value=dummy_org))
    updated_org = await auth_service.update_organization(root_token, ORG_1_ID, dummy_org_update)
    assert updated_org.id == ORG_1_ID

    dummy_user = User(
        id=USER_1_ID,
        email="user@delegate.com",
        role=UserRole.MEMBER,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
        created_at=now,
        organization_id=ORG_1_ID,
    )
    dummy_user_create = UserCreate(
        email="user@delegate.com",
        role=UserRole.MEMBER,
        password="secretpassword",
        organization_id=ORG_1_ID,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
    )
    dummy_user_update = UserUpdate(name="Updated User")

    monkeypatch.setattr(auth_service.user_service, "create_user", AsyncMock(return_value=dummy_user))
    created_user = await auth_service.create_user(SYSTEM_ROOT_USER_ID, dummy_user_create)
    assert created_user.id == USER_1_ID

    monkeypatch.setattr(auth_service.user_service, "_create_user_internal", AsyncMock(return_value=dummy_user))
    internal_user = await auth_service._create_user_internal(SYSTEM_ROOT_USER_ID, dummy_user_create, ORG_1_ID)
    assert internal_user.id == USER_1_ID

    mock_enf_hier = MagicMock()
    monkeypatch.setattr(auth_service.user_service, "_enforce_hierarchy", mock_enf_hier)
    auth_service._enforce_hierarchy(dummy_user, UserRole.MEMBER)
    mock_enf_hier.assert_called_once_with(creator=dummy_user, target_role=UserRole.MEMBER)

    monkeypatch.setattr(auth_service.user_service, "_count_org_admins", AsyncMock(return_value=2))
    assert await auth_service._count_org_admins(ORG_1_ID) == 2

    monkeypatch.setattr(auth_service.user_service, "get_users_by_organization", AsyncMock(return_value=[dummy_user]))
    assert len(await auth_service.get_users_by_organization(ORG_1_ID)) == 1

    monkeypatch.setattr(auth_service.user_service, "delete_user", AsyncMock(return_value=True))
    assert await auth_service.delete_user(SYSTEM_ROOT_USER_ID, USER_1_ID) is True

    monkeypatch.setattr(auth_service.user_service, "update_user", AsyncMock(return_value=dummy_user))
    assert (await auth_service.update_user(SYSTEM_ROOT_USER_ID, USER_1_ID, dummy_user_update)).id == USER_1_ID

    monkeypatch.setattr(auth_service.user_service, "update_user_role", AsyncMock(return_value=dummy_user))
    assert (await auth_service.update_user_role(SYSTEM_ROOT_USER_ID, USER_1_ID, UserRole.ADMIN)).id == USER_1_ID

    monkeypatch.setattr(auth_service.user_service, "list_users", AsyncMock(return_value=[dummy_user]))
    assert len(await auth_service.list_users(root_token)) == 1

    monkeypatch.setattr(auth_service.user_service, "get_user", AsyncMock(return_value=dummy_user))
    assert (await auth_service.get_user(root_token, USER_1_ID)).id == USER_1_ID

    monkeypatch.setattr(auth_service.user_service, "ensure_root_user", AsyncMock(return_value=dummy_user))
    assert (await auth_service.ensure_root_user()).id == USER_1_ID


@pytest.mark.asyncio
async def test_auth_router_accept_invitation_and_firebase_webhook(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify accept_invitation and firebase_user_deleted_webhook router endpoints delegate to AuthService."""
    import hashlib
    import hmac

    from pydantic import SecretStr

    from backend_v2.models.auth import InvitationAcceptRequestDTO
    from backend_v2.settings import Settings

    secret_val = "whsec_router_test_2026"
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        firebase_webhook_secret=SecretStr(secret_val),
    )
    monkeypatch.setattr("backend_v2.services.auth.user_service.get_settings", lambda: mock_settings)

    service = AuthService(mock_repo, use_firebase=False)
    now = datetime.now(UTC)
    member = User(
        id=USER_1_ID,
        email="webhook_user@test.com",
        firebase_uid="fb_uid_router_wh",
        role=UserRole.MEMBER,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
        created_at=now,
        organization_id=ORG_1_ID,
    )
    await mock_repo.create_user(member)

    monkeypatch.setattr(service.org_service, "accept_invitation", AsyncMock(return_value=member))
    accepted = await accept_invitation(
        payload=InvitationAcceptRequestDTO(raw_token="raw_invitation_token_1234567890"),
        current_user=TokenData(id=USER_1_ID, role=UserRole.MEMBER, email="webhook_user@test.com"),
        auth_service=service,
    )
    assert accepted.id == USER_1_ID

    mock_req = MagicMock(spec=Request)
    mock_req.client = Address("203.0.113.10", 50000)
    mock_req.body = AsyncMock(return_value=b"")
    sig = hmac.new(secret_val.encode("utf-8"), b"fb_uid_router_wh", hashlib.sha256).hexdigest()
    del_res = await firebase_user_deleted_webhook(
        request=mock_req,
        auth_service=service,
        firebase_uid="fb_uid_router_wh",
        x_quorum_webhook_signature=f"sha256={sig}",
    )
    assert del_res.status == "success"
    assert del_res.id == "fb_uid_router_wh"

    with pytest.raises(AuthenticationError) as exc_wh:
        await firebase_user_deleted_webhook(
            request=mock_req,
            auth_service=service,
            firebase_uid="fb_uid_router_wh",
            x_quorum_webhook_signature="sha256=invalid_signature",
        )
    assert exc_wh.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    rate_limiter = TenantRateLimitService(redis=FakeRedis(), get_settings_fn=lambda: mock_settings)
    with pytest.raises(AuthenticationError) as exc_ex:
        await exchange_firebase_token(
            request=mock_req,
            payload=TokenExchangeRequestDTO(target_user_id=USER_2_ID),
            auth_service=service,
            rate_limit_service=rate_limiter,
        )
    assert exc_ex.value.error_code == ErrorCodes.AUTHENTICATION_FAILED

    bva_settings = mock_settings.model_copy(update={"auth_edge_rpm_limit": 2})
    bva_limiter = TenantRateLimitService(redis=FakeRedis(), get_settings_fn=lambda: bva_settings)
    active_member = member.model_copy(update={"is_active": True, "deleted_at": None})
    await mock_repo.create_user(active_member)
    valid_payload = TokenExchangeRequestDTO(target_user_id=USER_1_ID)

    res_1 = await exchange_firebase_token(
        request=mock_req,
        payload=valid_payload,
        auth_service=service,
        rate_limit_service=bva_limiter,
    )
    assert res_1.user.id == USER_1_ID

    res_2 = await exchange_firebase_token(
        request=mock_req,
        payload=valid_payload,
        auth_service=service,
        rate_limit_service=bva_limiter,
    )
    assert res_2.user.id == USER_1_ID

    # Boundary limit + 1 raises HTTP 429 TokenLimitExceededError with RATE_LIMIT_EXCEEDED
    with pytest.raises(TokenLimitExceededError) as exc_429:
        await exchange_firebase_token(
            request=mock_req,
            payload=valid_payload,
            auth_service=service,
            rate_limit_service=bva_limiter,
        )
    assert exc_429.value.status_code == 429
    assert exc_429.value.details["error_code"] == ErrorCodes.RATE_LIMIT_EXCEEDED.value

    # Missing client IP (request.client is None) raises HTTP 400 VALIDATION_FAILED
    no_client_req = MagicMock(spec=Request)
    no_client_req.client = None
    with pytest.raises(AppException) as exc_400:
        await exchange_firebase_token(
            request=no_client_req,
            payload=valid_payload,
            auth_service=service,
            rate_limit_service=bva_limiter,
        )
    assert exc_400.value.status_code == 400
    assert exc_400.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    # Fail-Closed Redis unavailability (redis=None) raises HTTP 503 SERVICE_UNAVAILABLE
    with pytest.raises(ServiceUnavailableError) as exc_503:
        await exchange_firebase_token(
            request=mock_req,
            payload=valid_payload,
            auth_service=service,
            rate_limit_service=TenantRateLimitService(redis=None),
        )
    assert exc_503.value.status_code == 503
    assert exc_503.value.details["error_code"] == ErrorCodes.SERVICE_UNAVAILABLE.value
