"""Unit tests for unified AuthService facade, IAM router endpoints, and Auth models."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from backend_v2.api.routers.iam.auth import get_my_profile, list_available_roles, list_users
from backend_v2.exceptions import PermissionDeniedError
from backend_v2.models.auth import (
    SYSTEM_ROOT_USER_ID,
    Organization,
    OrganizationCreate,
    SubscriptionStatus,
    SystemOrganizations,
    TokenData,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)
from backend_v2.models.enums import SystemLocale
from backend_v2.services.auth import AuthService
from backend_v2.services.auth.organization_service import OrganizationUpdateDTO
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
async def test_auth_router_list_users(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Verify list_users endpoint returns empty list when no users exist in tenant."""
    service = AuthService(mock_repo, use_firebase=False)
    users = await list_users(
        current_user=TokenData(id=ADMIN_1_ID, role=UserRole.ADMIN, organization_id=ORG_1_ID),
        auth_service=service,
    )
    assert users == []


def test_system_organizations_is_system() -> None:
    """Verify SystemOrganizations.is_system recognizes canonical ROOT_SYSTEM and SYSTEM sentinel."""
    assert SystemOrganizations.is_system(SystemOrganizations.ROOT_SYSTEM) is True
    assert SystemOrganizations.is_system("SYSTEM") is True
    assert SystemOrganizations.is_system(None) is True
    assert SystemOrganizations.is_system("") is True
    assert SystemOrganizations.is_system("org_0195f3a00000700e8531d2ed8a6641f6") is False


def test_auth_models_validation_coverage_and_invalid_inputs_error() -> None:
    """Verify Organization, User, OrganizationCreate, and TokenData validation and negative error cases."""
    now = datetime.now(timezone.utc)
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

    assert AuthService.use_firebase.fset is None
    assert AuthService.firebase_auth.fset is None

    with pytest.raises(AttributeError):
        AuthService.use_firebase.__set__(auth_service, False)

    with pytest.raises(AttributeError):
        AuthService.firebase_auth.__set__(auth_service, None)

    init_file = Path(__file__).parents[2] / "services" / "auth" / "__init__.py"
    line_count = len(init_file.read_text(encoding="utf-8").splitlines())
    assert line_count < 300, f"AuthService facade line count ({line_count}) exceeds 300 lines cap"

    auth_service.token_service._init_firebase = MagicMock()
    auth_service._init_firebase()
    auth_service.token_service._init_firebase.assert_called_once()

    auth_service.token_service.create_impersonation_token = MagicMock(return_value="mock_jwt_impersonate")
    token_str = auth_service.create_impersonation_token(USER_1_ID, 1800)
    assert token_str == "mock_jwt_impersonate"
    auth_service.token_service.create_impersonation_token.assert_called_once_with(
        target_id=USER_1_ID, duration_seconds=1800
    )

    auth_service.token_service.verify_token = AsyncMock(
        return_value=TokenData(id=USER_1_ID, role=UserRole.ADMIN, organization_id=ORG_1_ID)
    )
    tok = await auth_service.verify_token("bearer_xyz")
    assert tok.id == USER_1_ID
    auth_service.token_service.verify_token.assert_awaited_once_with("bearer_xyz")

    now = datetime.now(timezone.utc)
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
    auth_service.org_service.create_organization = AsyncMock(return_value=dummy_org)
    created_org = await auth_service.create_organization(root_token, dummy_org_create)
    assert created_org.id == ORG_1_ID

    auth_service.org_service.delete_organization = AsyncMock()
    await auth_service.delete_organization(root_token, ORG_1_ID, force=True)
    auth_service.org_service.delete_organization.assert_awaited_once_with(
        initiator=root_token, target_org_id=ORG_1_ID, force=True
    )

    auth_service.org_service.list_organizations = AsyncMock(return_value=[dummy_org])
    orgs = await auth_service.list_organizations(root_token)
    assert len(orgs) == 1

    auth_service.org_service.get_organization = AsyncMock(return_value=dummy_org)
    fetched_org = await auth_service.get_organization(root_token, ORG_1_ID)
    assert fetched_org.id == ORG_1_ID

    dummy_org_update = OrganizationUpdateDTO(name="Updated Delegate Org")
    auth_service.org_service.update_organization = AsyncMock(return_value=dummy_org)
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

    auth_service.user_service.create_user = AsyncMock(return_value=dummy_user)
    created_user = await auth_service.create_user(SYSTEM_ROOT_USER_ID, dummy_user_create)
    assert created_user.id == USER_1_ID

    auth_service.user_service._create_user_internal = AsyncMock(return_value=dummy_user)
    internal_user = await auth_service._create_user_internal(SYSTEM_ROOT_USER_ID, dummy_user_create, ORG_1_ID)
    assert internal_user.id == USER_1_ID

    auth_service.user_service._enforce_hierarchy = MagicMock()
    auth_service._enforce_hierarchy(dummy_user, UserRole.MEMBER)
    auth_service.user_service._enforce_hierarchy.assert_called_once_with(
        creator=dummy_user, target_role=UserRole.MEMBER
    )

    auth_service.user_service._count_org_admins = AsyncMock(return_value=2)
    assert await auth_service._count_org_admins(ORG_1_ID) == 2

    auth_service.user_service.get_users_by_organization = AsyncMock(return_value=[dummy_user])
    assert len(await auth_service.get_users_by_organization(ORG_1_ID)) == 1

    auth_service.user_service.delete_user = AsyncMock(return_value=True)
    assert await auth_service.delete_user(SYSTEM_ROOT_USER_ID, USER_1_ID) is True

    auth_service.user_service.update_user = AsyncMock(return_value=dummy_user)
    assert (await auth_service.update_user(SYSTEM_ROOT_USER_ID, USER_1_ID, dummy_user_update)).id == USER_1_ID

    auth_service.user_service.update_user_role = AsyncMock(return_value=dummy_user)
    assert (await auth_service.update_user_role(SYSTEM_ROOT_USER_ID, USER_1_ID, UserRole.ADMIN)).id == USER_1_ID

    auth_service.user_service.list_users = AsyncMock(return_value=[dummy_user])
    assert len(await auth_service.list_users(root_token)) == 1

    auth_service.user_service.get_user = AsyncMock(return_value=dummy_user)
    assert (await auth_service.get_user(root_token, USER_1_ID)).id == USER_1_ID

    auth_service.user_service.ensure_root_user = AsyncMock(return_value=dummy_user)
    assert (await auth_service.ensure_root_user()).id == USER_1_ID
