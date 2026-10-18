"""Unit tests for organization and user repositories."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend_v2.exceptions import (
    AppException,
    ErrorCodes,
)
from backend_v2.models.auth import (
    Organization,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    User,
    UserRole,
    UserUpdate,
)
from backend_v2.models.enums import SystemLocale
from backend_v2.services.auth import (
    OrganizationRepository,
    UserRepository,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide an in-memory unified repository for testing."""
    return InMemoryUnifiedWorkflowRepository()


@pytest.mark.asyncio
async def test_organization_repository(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    org_repo = OrganizationRepository(mock_repo)

    test_org = Organization(
        id="org_1234abcd",
        name="Test Org",
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )

    # Test get_by_id
    await mock_repo.create_organization(test_org)
    org = await org_repo.get_by_id("org_1234abcd")
    assert org is not None
    assert org.id == "org_1234abcd"

    # Test create
    org_obj = Organization(
        id="org_2345bcde",
        name="New Org",
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await org_repo.create(org_obj)
    persisted = await mock_repo.get_organization("org_2345bcde")
    assert persisted is not None

    # Test list_all
    orgs = await org_repo.list_all()
    assert len(orgs) == 2


@pytest.mark.asyncio
async def test_user_repository(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    user_repo = UserRepository(mock_repo)

    test_user = User(
        id="usr_1234abcd",
        email="test@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_1234abcd",
    )

    # Test get_by_id
    await mock_repo.create_user(test_user)
    user = await user_repo.get_by_id("usr_1234abcd")
    assert user is not None
    assert user.id == "usr_1234abcd"


@pytest.mark.asyncio
async def test_user_repository_create_update_delete(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    user_repo = UserRepository(mock_repo)

    # create
    new_user = User(
        id="usr_2345bcde",
        email="new@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_2345bcde",
    )
    await user_repo.create(new_user)
    persisted = await mock_repo.get_user("usr_2345bcde")
    assert persisted is not None

    # update
    updated = await user_repo.update("usr_2345bcde", UserUpdate(name="Updated Name"))
    assert updated is not None
    assert updated.name == "Updated Name"

    # delete
    result = await user_repo.delete("usr_2345bcde")
    assert result is True
    assert await mock_repo.get_user("usr_2345bcde") is None


@pytest.mark.asyncio
async def test_organization_repository_get_by_id_found_returns_organization(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    org_repo = OrganizationRepository(mock_repo)
    test_org = Organization(
        id="org_test1234",
        name="Test Org",
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(test_org)
    res = await org_repo.get_by_id("org_test1234")
    assert res is not None
    assert res.id == "org_test1234"
    assert res.name == "Test Org"


@pytest.mark.asyncio
async def test_organization_repository_get_by_id_not_found_returns_none(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    org_repo = OrganizationRepository(mock_repo)
    res = await org_repo.get_by_id("org_missing")
    assert res is None


@pytest.mark.asyncio
async def test_organization_repository_create_persists_and_returns(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    org_repo = OrganizationRepository(mock_repo)
    test_org = Organization(
        id="org_create123",
        name="Created Org",
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    created = await org_repo.create(test_org)
    assert created.id == "org_create123"
    persisted = await mock_repo.get_organization("org_create123")
    assert persisted is not None


@pytest.mark.asyncio
async def test_organization_repository_list_all_returns_list(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    org_repo = OrganizationRepository(mock_repo)
    test_org = Organization(
        id="org_list1234",
        name="List Org",
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await org_repo.create(test_org)
    orgs = await org_repo.list_all()
    assert isinstance(orgs, list)
    assert any(o.id == "org_list1234" for o in orgs)


@pytest.mark.asyncio
async def test_user_repository_get_by_id_found_returns_user(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    test_user = User(
        id="usr_abc12345",
        email="abc@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test1234",
    )
    await mock_repo.create_user(test_user)
    user = await user_repo.get_by_id("usr_abc12345")
    assert user is not None
    assert user.id == "usr_abc12345"


@pytest.mark.asyncio
async def test_user_repository_get_by_id_not_found_returns_none(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    user = await user_repo.get_by_id("usr_none123")
    assert user is None


@pytest.mark.asyncio
async def test_user_repository_get_by_email_found_returns_user(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    test_user = User(
        id="usr_email123",
        email="admin@example.com",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test1234",
    )
    await mock_repo.create_user(test_user)
    user = await user_repo.get_by_email("admin@example.com")
    assert user is not None
    assert user.id == "usr_email123"


@pytest.mark.asyncio
async def test_user_repository_get_by_email_not_found_returns_none(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    user = await user_repo.get_by_email("unknown@example.com")
    assert user is None


@pytest.mark.asyncio
async def test_user_repository_create_duplicate_id_raises_app_exception(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    test_user = User(
        id="usr_dup12345",
        email="dup1@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test1234",
    )
    await user_repo.create(test_user)
    dup_user = User(
        id="usr_dup12345",
        email="dup2@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test1234",
    )
    with pytest.raises(AppException) as exc_info:
        await user_repo.create(dup_user)
    assert exc_info.value.status_code == 409
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFLICT_ERROR.value


@pytest.mark.asyncio
async def test_user_repository_update_not_found_returns_none(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    res = await user_repo.update("usr_missing", UserUpdate(name="New Name"))
    assert res is None


@pytest.mark.asyncio
async def test_user_repository_update_success_returns_updated_user(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    test_user = User(
        id="usr_upd12345",
        email="upd@test.com",
        name="Original Name",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test1234",
    )
    await user_repo.create(test_user)
    updated = await user_repo.update("usr_upd12345", UserUpdate(name="Updated Name"))
    assert updated is not None
    assert updated.name == "Updated Name"


@pytest.mark.asyncio
async def test_user_repository_delete_calls_underlying_repo(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    test_user = User(
        id="usr_del12345",
        email="del@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_test1234",
    )
    await user_repo.create(test_user)
    res = await user_repo.delete("usr_del12345")
    assert res is True
    assert await user_repo.get_by_id("usr_del12345") is None


@pytest.mark.asyncio
async def test_user_repository_get_by_organization_filters_and_validates(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    user_repo = UserRepository(mock_repo)
    user1 = User(
        id="usr_org12301",
        email="user1@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_target01",
    )
    user2 = User(
        id="usr_org12302",
        email="user2@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_target01",
    )
    user_other = User(
        id="usr_orgother01",
        email="other@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.fromisoformat("2026-01-01T00:00:00Z"),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_other01",
    )
    await user_repo.create(user1)
    await user_repo.create(user2)
    await user_repo.create(user_other)

    users = await user_repo.get_by_organization("org_target01")
    assert len(users) == 2
    assert all(isinstance(u, User) for u in users)
    assert {u.id for u in users} == {"usr_org12301", "usr_org12302"}


@pytest.mark.asyncio
async def test_organization_repository_not_found(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Test get_by_id returns None when organization is not found."""
    org_repo = OrganizationRepository(mock_repo)
    res = await org_repo.get_by_id("org_missing")
    assert res is None


@pytest.mark.asyncio
async def test_user_repository_additional_coverage(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """Test UserRepository get_by_email, create duplicate conflict, update not found, and get_by_organization."""
    user_repo = UserRepository(mock_repo)
    test_user = User(
        id="usr_existing1234",
        email="existing@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_1234abcd",
    )

    # get_by_email
    await mock_repo.create_user(test_user)
    found = await user_repo.get_by_email("existing@test.com")
    assert found is not None
    assert found.id == "usr_existing1234"

    # create duplicate raises conflict
    with pytest.raises(AppException) as excinfo:
        await user_repo.create(test_user)
    assert excinfo.value.status_code == 409

    # update when user not found returns None
    res = await user_repo.update("usr_unknown", UserUpdate(name="New Name"))
    assert res is None

    # get_by_organization
    users = await user_repo.get_by_organization("org_1234abcd")
    assert len(users) == 1
    assert users[0].id == test_user.id


@pytest.mark.asyncio
async def test_organization_repository_update_and_delete(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verifies OrganizationRepository update and delete methods."""
    org_repo = OrganizationRepository(mock_repo)
    test_org = Organization(
        id="org_repocrud00001",
        name="Repo CRUD",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await org_repo.create(test_org)

    update_success = await org_repo.update("org_repocrud00001", OrganizationUpdateDTO(name="New Repo CRUD"))
    assert update_success is True
    refreshed = await org_repo.get_by_id("org_repocrud00001")
    assert refreshed is not None
    assert refreshed.name == "New Repo CRUD"

    del_success = await org_repo.delete("org_repocrud00001")
    assert del_success is True
    assert await org_repo.get_by_id("org_repocrud00001") is None
