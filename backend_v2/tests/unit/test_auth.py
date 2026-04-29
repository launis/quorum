from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.models.auth import Organization, SubscriptionStatus, TokenData, User, UserRole, UserUpdate
from backend_v2.services.auth import AuthService, OrganizationRepository, UserRepository


@pytest.fixture
def mock_repo() -> Any:
    repo = AsyncMock()
    return repo


@pytest.mark.asyncio
async def test_organization_repository(mock_repo: Any) -> None:
    org_repo = OrganizationRepository(mock_repo)

    # Test get_by_id
    mock_repo.get_organization.return_value = {
        "id": "org_1234abcd",
        "name": "Test Org",
        "is_active": True,
        "created_at": "2026-01-01T00:00:00Z",
        "tier": "enterprise",
        "subscription_status": "active",
        "quota_limit": 500.0,
        "tpm_limit": 50000,
        "rpm_limit": 500,
    }
    org = await org_repo.get_by_id("org_1234abcd")
    assert org is not None
    assert org.id == "org_1234abcd"

    # Test create
    org_obj = Organization(
        id="org_2345bcde",
        name="New Org",
        is_active=True,
        created_at="2026-01-01T00:00:00Z",  # type: ignore  # type: ignore
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await org_repo.create(org_obj)
    mock_repo.create_organization.assert_called_once()

    # Test list_all
    mock_repo.list_organizations.return_value = [
        {
            "id": "org_1234abcd",
            "name": "Test Org",
            "is_active": True,
            "created_at": "2026-01-01T00:00:00Z",
            "tier": "enterprise",
            "subscription_status": "active",
            "quota_limit": 500.0,
            "tpm_limit": 50000,
            "rpm_limit": 500,
        }
    ]
    orgs = await org_repo.list_all()
    assert len(orgs) == 1


@pytest.mark.asyncio
async def test_user_repository(mock_repo: Any) -> None:
    user_repo = UserRepository(mock_repo)

    # Test get_by_id
    mock_repo.get_user.return_value = {
        "id": "usr_1234abcd",
        "email": "test@test.com",
        "role": "MEMBER",
        "is_active": True,
        "created_at": "2026-01-01T00:00:00Z",
        "language": "en",
        "theme_mode": "system",
    }
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
        created_at="2026-01-01T00:00:00Z",  # type: ignore  # type: ignore
        language="en",
        theme_mode="system",
    )
    mock_repo.get_user.side_effect = [None]  # For the exist check
    await user_repo.create(new_user)
    mock_repo.create_user.assert_called_once()

    # update
    mock_repo.get_user.side_effect = [
        {
            "id": "usr_2345bcde",
            "email": "new@test.com",
            "role": "MEMBER",
            "is_active": True,
            "created_at": "2026-01-01T00:00:00Z",
            "language": "en",
            "theme_mode": "system",
        },  # noqa: E501
        {
            "id": "usr_2345bcde",
            "email": "new@test.com",
            "role": "MEMBER",
            "is_active": True,
            "created_at": "2026-01-01T00:00:00Z",
            "language": "en",
            "theme_mode": "system",
            "display_name": "Updated Name",
        },  # noqa: E501
    ]
    updated = await user_repo.update("usr_2345bcde", UserUpdate(display_name="Updated Name"))
    mock_repo.update_user.assert_called_once()
    assert updated.display_name == "Updated Name"  # type: ignore  # type: ignore

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
    mock_repo.get_user.return_value = {
        "id": "usr_1234abcd",
        "email": "test@test.com",
        "role": "MEMBER",
        "is_active": True,
        "created_at": "2026-01-01T00:00:00Z",
        "language": "en",
        "theme_mode": "system",
    }
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

    mock_repo.list_users.return_value = [
        {
            "id": "usr_1234abcd",
            "email": "test@test.com",
            "role": "MEMBER",
            "is_active": True,
            "organization_id": "org_1234abcd",
            "created_at": "2026-01-01T00:00:00Z",
            "language": "en",
            "theme_mode": "system",
        },
        {
            "id": "usr_2345bcde",
            "email": "test2@test.com",
            "role": "MEMBER",
            "is_active": True,
            "organization_id": "org_2345bcde",
            "created_at": "2026-01-01T00:00:00Z",
            "language": "en",
            "theme_mode": "system",
        },
    ]

    initiator = TokenData(id="admin_1234abcd", role=UserRole.ROOT, email="root@test.com")
    users = await service.list_users(initiator)
    assert len(users) == 2


@pytest.mark.asyncio
async def test_auth_service_get_user(mock_repo: Any) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    mock_repo.get_user.return_value = {
        "id": "usr_1234abcd",
        "email": "test@test.com",
        "role": "MEMBER",
        "is_active": True,
        "organization_id": "org_1234abcd",
        "created_at": "2026-01-01T00:00:00Z",
        "language": "en",
        "theme_mode": "system",
    }

    initiator = TokenData(id="root_1234abcd", role=UserRole.ROOT, email="root@test.com")
    user = await service.get_user(initiator, "usr_1234abcd")
    assert user.id == "usr_1234abcd"


@pytest.mark.asyncio
async def test_auth_service_tenant_isolation(mock_repo: Any) -> None:
    service = AuthService(mock_repo, use_firebase=False)

    mock_repo.get_user.return_value = {
        "id": "usr_target12",
        "email": "target@test.com",
        "role": "MEMBER",
        "is_active": True,
        "organization_id": "org_target12",
        "created_at": "2026-01-01T00:00:00Z",
        "language": "en",
        "theme_mode": "system",
    }

    initiator_admin = TokenData(
        id="usr_admin123", role=UserRole.ADMIN, organization_id="org_target12", email="admin@test.com"
    )  # noqa: E501

    user = await service.get_user(initiator_admin, "usr_target12")
    assert user.id == "usr_target12"

    initiator_wrong_org = TokenData(
        id="usr_admin456", role=UserRole.ADMIN, organization_id="org_wrong123", email="admin2@test.com"
    )  # noqa: E501
    from backend_v2.exceptions import PermissionDeniedError

    with pytest.raises(PermissionDeniedError):
        await service.get_user(initiator_wrong_org, "usr_target12")
