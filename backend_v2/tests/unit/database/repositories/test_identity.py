"""Unit tests for IdentityRepositoryImpl."""

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.identity import IdentityRepositoryImpl


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Mock storage driver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.get.return_value = None
    driver.upsert.return_value = "org_1234567890abcdef"
    driver.update.return_value = True
    driver.delete.return_value = True
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> IdentityRepositoryImpl:
    """Identity repository fixture."""
    return IdentityRepositoryImpl(mock_driver)


@pytest.fixture
def valid_org_doc() -> dict:
    """Valid organization document fixture."""
    return {
        "id": "org_1234567890abcdef",
        "name": "Test Org",
        "is_active": True,
        "tier": "enterprise",
        "subscription_status": "active",
        "quota_limit": 1000,
        "tpm_limit": 10000,
        "rpm_limit": 100,
        "created_at": "2026-08-30T12:00:00Z",
    }


@pytest.fixture
def valid_user_doc() -> dict:
    """Valid user document fixture."""
    return {
        "id": "usr_1234567890abcdef",
        "email": "user@example.com",
        "role": "ADMIN",
        "is_active": True,
        "language": "fi",
        "theme_mode": "system",
        "organization_id": "org_1234567890abcdef",
        "created_at": "2026-08-30T12:00:00Z",
    }


@pytest.mark.asyncio
async def test_organization_crud(repo: IdentityRepositoryImpl, mock_driver: AsyncMock, valid_org_doc: dict) -> None:
    """Positive: tests organization CRUD operations and corrupted record skipping."""
    mock_driver.get.return_value = valid_org_doc
    mock_driver.query.return_value = [{"id": "corrupted_org"}, valid_org_doc]

    org = await repo.get_organization("org_1234567890abcdef")
    assert org is not None
    assert org.id == "org_1234567890abcdef"
    assert org.name == "Test Org"

    org_model = await repo.get_organization_model("org_1234567890abcdef")
    assert org_model is not None

    orgs = await repo.list_organizations()
    assert len(orgs) == 1
    assert orgs[0].id == "org_1234567890abcdef"

    assert await repo.create_organization(valid_org_doc) == "org_1234567890abcdef"
    assert await repo.update_organization("org_1234567890abcdef", {"name": "Updated Org"}) is True
    assert await repo.delete_organization("org_1234567890abcdef") is True


@pytest.mark.asyncio
async def test_get_organization_not_found(repo: IdentityRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: returns None when organization is not found."""
    mock_driver.get.return_value = None
    assert await repo.get_organization("org_missing") is None


@pytest.mark.asyncio
async def test_user_crud(repo: IdentityRepositoryImpl, mock_driver: AsyncMock, valid_user_doc: dict) -> None:
    """Positive: tests user CRUD operations and corrupted record skipping."""
    mock_driver.get.return_value = valid_user_doc
    mock_driver.query.return_value = [{"id": "corrupted_user"}, valid_user_doc]

    user = await repo.get_user("usr_1234567890abcdef")
    assert user is not None
    assert user.id == "usr_1234567890abcdef"
    assert user.email == "user@example.com"

    users = await repo.list_users(org_id="org_1234567890abcdef")
    assert len(users) == 1
    assert users[0].email == "user@example.com"

    mock_driver.query.return_value = [valid_user_doc]
    by_email = await repo.get_user_by_email("user@example.com")
    assert by_email is not None
    assert by_email.id == "usr_1234567890abcdef"

    mock_driver.upsert.return_value = "usr_1234567890abcdef"
    assert await repo.create_user(valid_user_doc) == "usr_1234567890abcdef"
    assert await repo.update_user("usr_1234567890abcdef", {"language": "en"}) is True
    assert await repo.delete_user("usr_1234567890abcdef") is True


@pytest.mark.asyncio
async def test_get_user_not_found(repo: IdentityRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: returns None when user is not found."""
    mock_driver.get.return_value = None
    assert await repo.get_user("usr_missing") is None

    mock_driver.query.return_value = []
    assert await repo.get_user_by_email("missing@example.com") is None


@pytest.mark.asyncio
async def test_delete_org_data_cascade(
    repo: IdentityRepositoryImpl, mock_driver: AsyncMock, valid_user_doc: dict
) -> None:
    """Positive: tests cascading purge of users, executions, and custom workflows."""
    mock_driver.query.side_effect = [
        [valid_user_doc],  # users for org
        [{"id": "exe_1", "organization_id": "org_1"}],  # executions
        [{"id": "wf_1", "organization_id": "org_1"}],  # workflows
    ]
    await repo.delete_org_data("org_1")
    assert mock_driver.delete.call_count >= 3


@pytest.mark.asyncio
async def test_get_org_usage_total(repo: IdentityRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: calculates total cost estimate across organization executions."""
    mock_driver.query.return_value = [
        {"id": "exe_1", "cost_estimate": 0.05},
        {"id": "exe_2", "cost_estimate": 0.03},
        {"id": "exe_3", "cost_estimate": None},
    ]
    total = await repo.get_org_usage_total("org_1", since="2026-08-01T00:00:00Z")
    assert total == pytest.approx(0.08)
