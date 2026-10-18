"""Unit tests for unified AuthService facade, IAM router endpoints, and Auth models."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import ValidationError

from backend_v2.api.routers.iam.auth import get_my_profile, list_available_roles, list_users
from backend_v2.exceptions import (
    PermissionDeniedError,
)
from backend_v2.models.auth import (
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
from backend_v2.services.auth import (
    AuthService,
)
from backend_v2.services.auth.organization_service import OrganizationUpdateDTO
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide an in-memory unified repository for testing."""
    return InMemoryUnifiedWorkflowRepository()


@pytest.mark.asyncio
async def test_auth_service_init(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    service = AuthService(mock_repo, use_firebase=False)
    assert service.use_firebase is False


@pytest.mark.asyncio
async def test_auth_service_list_users(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    u1 = User(
        id="usr_1234abcd",
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id="org_1234abcd",
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    u2 = User(
        id="usr_2345bcde",
        email="test2@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id="org_2345bcde",
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
    )

    await mock_repo.create_user(u1)
    await mock_repo.create_user(u2)

    initiator = TokenData(id="admin_1234abcd", role=UserRole.ROOT, email="root@test.com")
    users = await service.list_users(initiator)
    assert len(users) == 2


@pytest.mark.asyncio
async def test_auth_service_get_user(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    test_user = User(
        id="usr_1234abcd",
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id="org_1234abcd",
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(test_user)

    initiator = TokenData(id="root_1234abcd", role=UserRole.ROOT, email="root@test.com")
    user = await service.get_user(initiator, "usr_1234abcd")
    assert user.id == "usr_1234abcd"


@pytest.mark.asyncio
async def test_auth_service_tenant_isolation(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    test_user = User(
        id="usr_target12",
        email="target@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id="org_target12",
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(test_user)

    initiator_admin = TokenData(
        id="usr_admin123", role=UserRole.ADMIN, organization_id="org_target12", email="admin@test.com"
    )

    user = await service.get_user(initiator_admin, "usr_target12")
    assert user.id == "usr_target12"

    initiator_wrong_org = TokenData(
        id="usr_admin456", role=UserRole.ADMIN, organization_id="org_wrong123", email="admin2@test.com"
    )

    with pytest.raises(PermissionDeniedError):
        await service.get_user(initiator_wrong_org, "usr_target12")


@pytest.mark.asyncio
async def test_auth_router_list_roles() -> None:
    roles = await list_available_roles()
    assert "ROOT" in roles


@pytest.mark.asyncio
async def test_auth_router_get_my_profile(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    service = AuthService(mock_repo, use_firebase=False)
    mock_user = User(
        id="usr_12345678",
        email="me@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
    )
    await mock_repo.create_user(mock_user)
    user = await get_my_profile(current_user=TokenData(id="usr_12345678", role=UserRole.MEMBER), auth_service=service)
    assert user == mock_user


@pytest.mark.asyncio
async def test_auth_router_list_users() -> None:
    mock_service = AsyncMock()
    mock_service.list_users.return_value = []
    users = await list_users(current_user=TokenData(id="usr_123", role=UserRole.MEMBER), auth_service=mock_service)
    assert users == []


def test_system_organizations_is_system() -> None:
    assert SystemOrganizations.is_system("org_system000000") is True
    assert SystemOrganizations.is_system("SYSTEM") is True
    assert SystemOrganizations.is_system(None) is True
    assert SystemOrganizations.is_system("") is True
    assert SystemOrganizations.is_system("org_e531d2ed8a6641f6") is False


def test_auth_models_validation_coverage() -> None:
    now = datetime.now(timezone.utc)
    # Organization with datetime object and valid fields
    org = Organization(
        id="org_test12345",
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
    )
    assert org.created_at == now

    # Organization validation failures
    with pytest.raises(ValidationError):
        Organization(
            id="org_test12345",
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
            id="org_test12345",
            name="Valid Name",
            is_active=True,
            tier="standard",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=10.0,
            tpm_limit=5000,
            rpm_limit=10,
            contact_email="   ",
        )

    # User with datetime and valid created_by
    user = User(
        id="usr_test12345",
        email="user@test.com",
        role=UserRole.ADMIN,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="dark",
        created_at=now,
        created_by="usr_admin1234",
        name="Valid User",
        organization_id="org_test12345",
    )
    assert user.created_at == now

    with pytest.raises(ValidationError):
        User(
            id="usr_test12345",
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
            id="usr_test12345",
            email="user@test.com",
            role=UserRole.ADMIN,
            is_active=True,
            language=SystemLocale.EN,
            theme_mode="dark",
            created_at=now,
            created_by="   ",
        )

    # OrganizationCreate validation
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

    # TokenData validation
    token = TokenData(id="usr_1234", role=UserRole.ADMIN, organization_id="org_1234", email="a@b.com")
    assert token.id == "usr_1234"

    with pytest.raises(ValidationError):
        TokenData(id="   ", role=UserRole.ADMIN)

    with pytest.raises(ValidationError):
        TokenData(id="usr_1234", role=UserRole.ADMIN, organization_id="   ")


@pytest.mark.asyncio
async def test_auth_service_facade_delegates_all_operations(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P4-39: AuthService facade delegates token, org, and user operations cleanly."""
    auth_service = AuthService(mock_repo)
    assert auth_service.token_service is not None
    assert auth_service.org_service is not None
    assert auth_service.user_service is not None

    # Test property setters synchronize across subservices
    auth_service.use_firebase = True
    assert auth_service.token_service.use_firebase is True
    assert auth_service.org_service.use_firebase is True
    assert auth_service.user_service.use_firebase is True

    mock_fb = MagicMock()
    auth_service.firebase_auth = mock_fb
    assert auth_service.firebase_auth is mock_fb
    assert auth_service.token_service.firebase_auth is mock_fb
    assert auth_service.org_service.firebase_auth is mock_fb
    assert auth_service.user_service.firebase_auth is mock_fb

    auth_service._initialized_firebase = True
    assert auth_service._initialized_firebase is True
    assert auth_service.token_service._initialized_firebase is True

    # Test private and public helper delegations
    auth_service.token_service._init_firebase = MagicMock()
    auth_service._init_firebase()
    auth_service.token_service._init_firebase.assert_called_once()

    auth_service.token_service.create_impersonation_token = MagicMock(return_value="mock_jwt_impersonate")
    token_str = auth_service.create_impersonation_token("usr_target01", 1800)
    assert token_str == "mock_jwt_impersonate"
    auth_service.token_service.create_impersonation_token.assert_called_once_with(
        target_id="usr_target01", duration_seconds=1800
    )

    auth_service.token_service.verify_token = AsyncMock(
        return_value=TokenData(id="usr_verified01", role=UserRole.ADMIN, organization_id="org_test1")
    )
    tok = await auth_service.verify_token("bearer_xyz")
    assert tok.id == "usr_verified01"
    auth_service.token_service.verify_token.assert_awaited_once_with("bearer_xyz")

    # Test organization delegations
    now = datetime.now(timezone.utc)
    dummy_org = Organization(
        id="org_delegate01",
        name="Delegate Org",
        is_active=True,
        tier="standard",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=100.0,
        tpm_limit=5000,
        rpm_limit=10,
        created_at=now,
    )
    root_token = TokenData(id="usr_root000001", role=UserRole.ROOT, organization_id="org_system000000")
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
    assert created_org.id == "org_delegate01"

    auth_service.org_service.delete_organization = AsyncMock()
    await auth_service.delete_organization(root_token, "org_delegate01", force=True)
    auth_service.org_service.delete_organization.assert_awaited_once_with(
        initiator=root_token, target_org_id="org_delegate01", force=True
    )

    auth_service.org_service.list_organizations = AsyncMock(return_value=[dummy_org])
    orgs = await auth_service.list_organizations(root_token)
    assert len(orgs) == 1

    auth_service.org_service.get_organization = AsyncMock(return_value=dummy_org)
    fetched_org = await auth_service.get_organization(root_token, "org_delegate01")
    assert fetched_org.id == "org_delegate01"

    dummy_org_update = OrganizationUpdateDTO(name="Updated Delegate Org")
    auth_service.org_service.update_organization = AsyncMock(return_value=dummy_org)
    updated_org = await auth_service.update_organization(root_token, "org_delegate01", dummy_org_update)
    assert updated_org.id == "org_delegate01"

    # Test user delegations
    dummy_user = User(
        id="usr_delegate01",
        email="user@delegate.com",
        role=UserRole.MEMBER,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
        created_at=now,
        organization_id="org_delegate01",
    )
    dummy_user_create = UserCreate(
        email="user@delegate.com",
        role=UserRole.MEMBER,
        password="secretpassword",
        organization_id="org_delegate01",
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
    )
    dummy_user_update = UserUpdate(name="Updated User")

    auth_service.user_service.create_user = AsyncMock(return_value=dummy_user)
    created_user = await auth_service.create_user("usr_root000001", dummy_user_create)
    assert created_user.id == "usr_delegate01"

    auth_service.user_service._create_user_internal = AsyncMock(return_value=dummy_user)
    internal_user = await auth_service._create_user_internal("usr_root000001", dummy_user_create, "org_delegate01")
    assert internal_user.id == "usr_delegate01"

    auth_service.user_service._enforce_hierarchy = MagicMock()
    auth_service._enforce_hierarchy(dummy_user, UserRole.MEMBER)
    auth_service.user_service._enforce_hierarchy.assert_called_once_with(
        creator=dummy_user, target_role=UserRole.MEMBER
    )

    auth_service.user_service._count_org_admins = AsyncMock(return_value=2)
    assert await auth_service._count_org_admins("org_delegate01") == 2

    auth_service.user_service.get_users_by_organization = AsyncMock(return_value=[dummy_user])
    assert len(await auth_service.get_users_by_organization("org_delegate01")) == 1

    auth_service.user_service.delete_user = AsyncMock(return_value=True)
    assert await auth_service.delete_user("usr_root000001", "usr_delegate01") is True

    auth_service.user_service.update_user = AsyncMock(return_value=dummy_user)
    assert (
        await auth_service.update_user("usr_root000001", "usr_delegate01", dummy_user_update)
    ).id == "usr_delegate01"

    auth_service.user_service.update_user_role = AsyncMock(return_value=dummy_user)
    assert (
        await auth_service.update_user_role("usr_root000001", "usr_delegate01", UserRole.ADMIN)
    ).id == "usr_delegate01"

    auth_service.user_service.list_users = AsyncMock(return_value=[dummy_user])
    assert len(await auth_service.list_users(root_token)) == 1

    auth_service.user_service.get_user = AsyncMock(return_value=dummy_user)
    assert (await auth_service.get_user(root_token, "usr_delegate01")).id == "usr_delegate01"

    auth_service.user_service.ensure_root_user = AsyncMock(return_value=dummy_user)
    assert (await auth_service.ensure_root_user()).id == "usr_delegate01"
