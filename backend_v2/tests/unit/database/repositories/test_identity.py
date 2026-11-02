"""Unit tests for IdentityRepositoryImpl."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from backend_v2.database.driver import StorageDriver
from backend_v2.database.repositories.identity import IdentityRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SystemOrganizations,
    User,
    UserRole,
    UserUpdate,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork

ORG_ID = "org_0195f3a0000070018234567890abcdef"
USER_ID = "usr_0195f3a0000070018234567890abcdef"


@pytest.fixture
def mock_driver() -> AsyncMock:
    """Mock storage driver."""
    driver = AsyncMock(spec=StorageDriver)
    driver.query.return_value = []
    driver.upsert.return_value = ORG_ID
    driver.update.return_value = True
    driver.delete.return_value = True
    return driver


@pytest.fixture
def repo(mock_driver: AsyncMock) -> IdentityRepositoryImpl:
    """Identity repository fixture."""
    return IdentityRepositoryImpl(mock_driver)


@pytest.fixture
def sample_organization() -> Organization:
    """Valid Organization domain model fixture."""
    return Organization(
        id=ORG_ID,
        name="Test Org",
        is_active=True,
        tier="enterprise",
        subscription_status="active",
        quota_limit=1000.0,
        tpm_limit=10000,
        rpm_limit=100,
    )


@pytest.fixture
def sample_user() -> User:
    """Valid User domain model fixture."""
    return User(
        id=USER_ID,
        email="user@example.com",
        role=UserRole.ADMIN,
        is_active=True,
        language="fi",
        theme_mode="system",
        organization_id=ORG_ID,
        created_at="2026-08-30T12:00:00Z",
    )


@pytest.mark.asyncio
async def test_organization_crud(
    repo: IdentityRepositoryImpl, mock_driver: AsyncMock, sample_organization: Organization
) -> None:
    """Positive: tests organization CRUD operations."""
    org_dict = sample_organization.model_dump(mode="json")
    mock_driver.query.return_value = [org_dict]

    org = await repo.get_organization(ORG_ID)
    assert org is not None
    assert org.id == ORG_ID
    assert org.name == "Test Org"

    org_model = await repo.get_organization_model(ORG_ID)
    assert org_model is not None

    orgs = await repo.list_organizations()
    assert len(orgs) == 1
    assert orgs[0].id == ORG_ID

    assert await repo.create_organization(sample_organization) == ORG_ID
    assert await repo.update_organization(ORG_ID, OrganizationUpdateDTO(name="Updated Org")) is True
    assert await repo.delete_organization(ORG_ID) is True


@pytest.mark.asyncio
async def test_organization_corruption_fail_fast(repo: IdentityRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: tests that corrupted organization raises AppException."""
    mock_driver.query.return_value = [{"id": "corrupted_org"}]
    with pytest.raises(AppException) as exc_info:
        await repo.list_organizations()
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED


@pytest.mark.asyncio
async def test_get_organization_not_found(repo: IdentityRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: returns None when organization is not found."""
    mock_driver.query.return_value = []
    assert await repo.get_organization(ORG_ID) is None


@pytest.mark.asyncio
async def test_user_crud(repo: IdentityRepositoryImpl, mock_driver: AsyncMock, sample_user: User) -> None:
    """Positive: tests user CRUD operations."""
    user_dict = sample_user.model_dump(mode="json")
    mock_driver.query.return_value = [user_dict]

    user = await repo.get_user(USER_ID)
    assert user is not None
    assert user.id == USER_ID
    assert user.email == "user@example.com"

    users = await repo.list_users(org_id=ORG_ID)
    assert len(users) == 1
    assert users[0].email == "user@example.com"

    mock_driver.query.return_value = [user_dict]
    by_email = await repo.get_user_by_email("user@example.com")
    assert by_email is not None
    assert by_email.id == USER_ID

    mock_driver.upsert.return_value = USER_ID
    assert await repo.create_user(sample_user) == USER_ID
    assert await repo.update_user(USER_ID, UserUpdate(language="en")) is True
    assert await repo.delete_user(USER_ID) is True


@pytest.mark.asyncio
async def test_user_corruption_fail_fast(repo: IdentityRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: tests that corrupted user raises AppException."""
    mock_driver.query.return_value = [{"id": "corrupted_user"}]
    with pytest.raises(AppException) as exc_info:
        await repo.list_users()
    assert exc_info.value.error_code == ErrorCodes.VALIDATION_FAILED


@pytest.mark.asyncio
async def test_get_user_not_found(repo: IdentityRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: returns None when user is not found."""
    mock_driver.query.return_value = []
    assert await repo.get_user(USER_ID) is None
    assert await repo.get_user_by_email("missing@example.com") is None


@pytest.mark.asyncio
async def test_delete_org_data_cascade(repo: IdentityRepositoryImpl, mock_driver: AsyncMock, sample_user: User) -> None:
    """Positive: tests cascading purge of users, executions, and custom workflows."""
    mock_driver.query.side_effect = [
        [sample_user.model_dump(mode="json")],
        [{"id": "exe_1", "organization_id": ORG_ID}],
        [{"id": "wf_1", "organization_id": ORG_ID}],
    ]
    await repo.delete_org_data(ORG_ID)
    assert mock_driver.delete.call_count >= 3


@pytest.mark.asyncio
async def test_get_org_usage_total(repo: IdentityRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Positive: calculates total cost estimate across organization executions."""
    mock_driver.query.return_value = [
        {"id": "exe_1", "cost_estimate": 0.05},
        {"id": "exe_2", "cost_estimate": 0.03},
        {"id": "exe_3", "cost_estimate": None},
    ]
    total = await repo.get_org_usage_total(ORG_ID, since="2026-08-01T00:00:00Z")
    assert total == pytest.approx(0.08)


@pytest.mark.asyncio
async def test_create_organization_from_dto_generates_prefixed_id(
    repo: IdentityRepositoryImpl, mock_driver: AsyncMock
) -> None:
    """Positive/Edge: tests creating an organization from OrganizationCreate generates an org_<uuid7> ID."""
    org_create = OrganizationCreate(
        name="Acme Corp",
        admin_email="admin@acme.com",
        admin_password="securepassword",
        admin_name="Acme Admin",
        tpm_limit=5000,
        rpm_limit=50,
    )
    mock_driver.upsert.return_value = ORG_ID
    doc_id = await repo.create_organization(org_create)
    assert doc_id == ORG_ID
    mock_driver.upsert.assert_awaited_once()
    call_args = mock_driver.upsert.call_args[0]
    assert call_args[0] == "organizations"
    assert str(call_args[2]).startswith("org_")
    assert len(str(call_args[2])) == 36


@pytest.mark.asyncio
async def test_empty_updates_short_circuit(repo: IdentityRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Boundary: tests that empty updates immediately return True without calling driver."""
    res_org = await repo.update_organization(ORG_ID, OrganizationUpdateDTO())
    assert res_org is True

    res_user = await repo.update_user(USER_ID, UserUpdate())
    assert res_user is True

    mock_driver.update.assert_not_awaited()


@pytest.mark.asyncio
async def test_corruption_without_id_reports_unknown(repo: IdentityRepositoryImpl, mock_driver: AsyncMock) -> None:
    """Negative: tests that corrupted records without an 'id' attribute report item_id='unknown'."""
    mock_driver.query.return_value = [{"invalid_key": "corrupted"}]
    with pytest.raises(AppException) as exc_org:
        await repo.list_organizations()
    assert exc_org.value.error_code == ErrorCodes.VALIDATION_FAILED
    assert exc_org.value.details["item_id"] == "unknown"

    with pytest.raises(AppException) as exc_user:
        await repo.list_users()
    assert exc_user.value.error_code == ErrorCodes.VALIDATION_FAILED
    assert exc_user.value.details["item_id"] == "unknown"


@pytest.mark.asyncio
async def test_delete_org_data_preserves_root_system_workflows(
    repo: IdentityRepositoryImpl, mock_driver: AsyncMock
) -> None:
    """Boundary: tests that workflows belonging to ROOT_SYSTEM are not purged during org data deletion."""
    mock_driver.query.side_effect = [
        [],
        [],
        [
            {"id": "wf_tenant", "organization_id": ORG_ID},
            {"id": "wf_root", "organization_id": SystemOrganizations.ROOT_SYSTEM},
        ],
    ]
    await repo.delete_org_data(ORG_ID)
    mock_driver.delete.assert_awaited_once_with("workflows", "wf_tenant")


@pytest.mark.asyncio
async def test_entity_adapter_delegation(
    mock_driver: AsyncMock,
    sample_organization: Organization,
    sample_user: User,
) -> None:
    """Positive: verifies IdentityRepositoryImpl delegates directly to EntityPersistencePort with stateful roundtrip."""
    async with InMemoryUnitOfWork() as uow:
        repo_with_adapter = IdentityRepositoryImpl(mock_driver, entity_adapter=uow.entities)
        assert await repo_with_adapter.create_organization(sample_organization) == ORG_ID
        assert await repo_with_adapter.get_organization(ORG_ID) == sample_organization
        assert await repo_with_adapter.list_organizations() == [sample_organization]
        assert await repo_with_adapter.create_user(sample_user) == USER_ID
        assert await repo_with_adapter.get_user(USER_ID) == sample_user
        assert await repo_with_adapter.list_users(ORG_ID) == [sample_user]
