from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.api.routers.iam.auth import get_my_profile, list_available_roles, list_users
from backend_v2.exceptions import PermissionDeniedError
from backend_v2.models.auth import (
    Organization,
    SubscriptionStatus,
    TokenData,
    User,
    UserRole,
    UserUpdate,
)
from backend_v2.services.auth import AuthService, OrganizationRepository, UserRepository


@pytest.fixture
def mock_repo() -> Any:
    repo = AsyncMock()
    return repo


@pytest.mark.asyncio
async def test_organization_repository(mock_repo: Any) -> None:
    org_repo = OrganizationRepository(mock_repo)

    test_org = Organization(
        id="org_1234abcd",
        name="Test Org",
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )

    # Test get_by_id
    mock_repo.get_organization.return_value = test_org
    org = await org_repo.get_by_id("org_1234abcd")
    assert org is not None
    assert org.id == "org_1234abcd"

    # Test create
    org_obj = Organization(
        id="org_2345bcde",
        name="New Org",
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await org_repo.create(org_obj)
    mock_repo.create_organization.assert_called_once()

    # Test list_all
    mock_repo.list_organizations.return_value = [test_org]
    orgs = await org_repo.list_all()
    assert len(orgs) == 1


@pytest.mark.asyncio
async def test_user_repository(mock_repo: Any) -> None:
    user_repo = UserRepository(mock_repo)

    test_user = User(
        id="usr_1234abcd",
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_1234abcd",
    )

    # Test get_by_id
    mock_repo.get_user.return_value = test_user
    user = await user_repo.get_by_id("usr_1234abcd")
    assert user is not None
    assert user.id == "usr_1234abcd"


@pytest.mark.asyncio
async def test_user_repository_create_update_delete(mock_repo: Any) -> None:
    user_repo = UserRepository(mock_repo)

    # create
    new_user = User(
        id="usr_2345bcde",
        email="new@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_2345bcde",
    )
    mock_repo.get_user.side_effect = [None]  # For the exist check
    await user_repo.create(new_user)
    mock_repo.create_user.assert_called_once()

    # update
    updated_user = User(
        id="usr_2345bcde",
        email="new@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_2345bcde",
        name="Updated Name",
    )
    mock_repo.get_user.side_effect = [new_user, updated_user]
    updated = await user_repo.update("usr_2345bcde", UserUpdate(name="Updated Name"))
    mock_repo.update_user.assert_called_once()
    assert updated.name == "Updated Name"

    # delete
    mock_repo.delete_user.return_value = True
    result = await user_repo.delete("usr_2345bcde")
    assert result is True


@pytest.mark.asyncio
async def test_auth_service_init(mock_repo: Any) -> None:
    service = AuthService(mock_repo, use_firebase=False)
    assert service.use_firebase is False


@pytest.mark.asyncio
async def test_auth_service_verify_token_mock(mock_repo: Any) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    # Test mock token
    test_user = User(
        id="usr_1234abcd",
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
        organization_id="org_1234abcd",
    )
    mock_repo.get_user.return_value = test_user
    token_data = await service.verify_token("mock-token:usr_1234abcd")

    assert token_data.id == "usr_1234abcd"
    assert token_data.role == UserRole.MEMBER


@pytest.mark.asyncio
async def test_auth_service_create_impersonation_token(mock_repo: Any) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    token = service.create_impersonation_token("target_usr_123")
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_auth_service_list_users(mock_repo: Any) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    u1 = User(
        id="usr_1234abcd",
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id="org_1234abcd",
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
    )
    u2 = User(
        id="usr_2345bcde",
        email="test2@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id="org_2345bcde",
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
    )

    mock_repo.list_users.return_value = [u1, u2]

    initiator = TokenData(id="admin_1234abcd", role=UserRole.ROOT, email="root@test.com")
    users = await service.list_users(initiator)
    assert len(users) == 2


@pytest.mark.asyncio
async def test_auth_service_get_user(mock_repo: Any) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    test_user = User(
        id="usr_1234abcd",
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id="org_1234abcd",
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
    )
    mock_repo.get_user.return_value = test_user

    initiator = TokenData(id="root_1234abcd", role=UserRole.ROOT, email="root@test.com")
    user = await service.get_user(initiator, "usr_1234abcd")
    assert user.id == "usr_1234abcd"


@pytest.mark.asyncio
async def test_auth_service_tenant_isolation(mock_repo: Any) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    test_user = User(
        id="usr_target12",
        email="target@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id="org_target12",
        created_at="2026-01-01T00:00:00Z",
        language="en",
        theme_mode="system",
    )
    mock_repo.get_user.return_value = test_user

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


# --- Auth Router Tests ---


@pytest.mark.asyncio
async def test_auth_router_list_roles() -> None:
    roles = await list_available_roles()
    assert "ROOT" in roles


@pytest.mark.asyncio
async def test_auth_router_get_my_profile() -> None:
    mock_service = AsyncMock()
    mock_user = User(
        id="usr_12345678",
        email="me@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        language="en",
        theme_mode="system",
        created_at="2026-01-01T00:00:00Z",
    )
    mock_service.repo.get_by_id.return_value = mock_user
    user = await get_my_profile(
        current_user=TokenData(id="usr_12345678", role=UserRole.MEMBER), auth_service=mock_service
    )
    assert user == mock_user


@pytest.mark.asyncio
async def test_auth_router_list_users() -> None:
    mock_service = AsyncMock()
    mock_service.list_users.return_value = []
    users = await list_users(current_user=TokenData(id="usr_123", role=UserRole.MEMBER), auth_service=mock_service)
    assert users == []
