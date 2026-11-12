"""Unit tests for IdentityRepositoryImpl over EntityPersistencePort."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from backend_v2.database.postgres.pool import PostgresPoolManager
from backend_v2.database.postgres.uow import PostgresUnitOfWork
from backend_v2.database.repositories.identity import IdentityRepositoryImpl
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    SystemOrganizations,
    User,
    UserCreate,
    UserRole,
    UserUpdate,
)
from backend_v2.models.enums import StorageBackend
from backend_v2.settings import Settings
from backend_v2.tests.factories.model_factories import UsageRecordFactory
from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool, InMemoryUnitOfWork

ORG_ID = "org_0195f3a0000070018234567890abcdef"
ORG_MISSING = "org_0195f3a0000070008000000000000099"
USER_ID = "usr_0195f3a0000070018234567890abcdef"
USER_MISSING = "usr_0195f3a0000070008000000000000099"


@pytest.fixture
def base_uow() -> InMemoryUnitOfWork:
    """Provide a shared InMemoryUnitOfWork store for stateful repository tests."""
    return InMemoryUnitOfWork()


@pytest.fixture
def repo(base_uow: InMemoryUnitOfWork) -> IdentityRepositoryImpl:
    """Provide an IdentityRepositoryImpl backed by the stateful InMemoryUnitOfWork store."""
    return IdentityRepositoryImpl(uow_factory=lambda: InMemoryUnitOfWork(base_uow.store))


@pytest.fixture
def sample_organization() -> Organization:
    """Valid Organization domain model fixture."""
    return Organization(
        id=ORG_ID,
        name="Test Org",
        created_at=datetime(2026, 8, 30, 12, 0, 0, tzinfo=UTC),
        is_active=True,
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=1000.0,
        tpm_limit=10000,
        rpm_limit=100,
        allowed_email_domains=["example.com"],
    )


@pytest.fixture
def sample_user() -> User:
    """Valid User domain model fixture."""
    return User(
        id=USER_ID,
        email="user@example.com",
        name="Example Admin",
        role=UserRole.ADMIN,
        is_active=True,
        language="fi",
        theme_mode="system",
        organization_id=ORG_ID,
        created_at=datetime(2026, 8, 30, 12, 0, 0, tzinfo=UTC),
    )


@pytest.mark.asyncio
async def test_organization_crud_and_updates(
    repo: IdentityRepositoryImpl,
    sample_organization: Organization,
) -> None:
    """Positive & Boundary: verify organization CRUD, DTO creation, partial updates, empty update, and missing returns."""
    assert await repo.get_organization(ORG_MISSING) is None
    assert await repo.update_organization(ORG_MISSING, OrganizationUpdateDTO(name="Missing")) is False
    assert await repo.delete_organization(ORG_MISSING) is False

    assert await repo.create_organization(sample_organization) == ORG_ID

    org = await repo.get_organization(ORG_ID)
    assert org is not None
    assert org.id == ORG_ID
    assert org.name == "Test Org"

    org_model = await repo.get_organization_model(ORG_ID)
    assert org_model == org

    orgs = await repo.list_organizations()
    assert len(orgs) == 1

    # Empty update returns True without mutating
    assert await repo.update_organization(ORG_ID, OrganizationUpdateDTO()) is True

    # Full field update
    assert (
        await repo.update_organization(
            ORG_ID,
            OrganizationUpdateDTO(
                name="Updated Org",
                tier="standard",
                is_active=False,
                contact_email="billing@example.com",
                billing_id="cus_12345",
                subscription_status=SubscriptionStatus.PAST_DUE,
                quota_limit=500.0,
                tpm_limit=20000,
                rpm_limit=200,
                allowed_email_domains=["corp.example.com"],
            ),
        )
        is True
    )
    updated_org = await repo.get_organization(ORG_ID)
    assert updated_org is not None
    assert updated_org.name == "Updated Org"
    assert updated_org.tier == "standard"
    assert updated_org.is_active is False
    assert updated_org.contact_email == "billing@example.com"
    assert updated_org.billing_id == "cus_12345"
    assert updated_org.subscription_status == SubscriptionStatus.PAST_DUE
    assert updated_org.quota_limit == 500.0
    assert updated_org.allowed_email_domains == ["corp.example.com"]

    org_create = OrganizationCreate(
        name="Acme Corp",
        admin_email="admin@acme.com",
        admin_password="securepassword123",
        admin_name="Acme Admin",
        tpm_limit=5000,
        rpm_limit=50,
    )
    created_dto_id = await repo.create_organization(org_create)
    assert created_dto_id.startswith("org_")
    assert len(created_dto_id) == 36

    assert await repo.delete_organization(ORG_ID) is True
    assert await repo.get_organization(ORG_ID) is None


@pytest.mark.asyncio
async def test_user_crud_and_case_insensitive_email(
    repo: IdentityRepositoryImpl,
    sample_organization: Organization,
    sample_user: User,
) -> None:
    """Positive & Boundary: verify user CRUD, UserCreate DTO, password-only short-circuit, and email lookup."""
    await repo.create_organization(sample_organization)
    assert await repo.get_user(USER_MISSING) is None
    assert await repo.get_user_by_email("missing@example.com") is None
    assert await repo.update_user(USER_MISSING, UserUpdate(language="en")) is False
    assert await repo.delete_user(USER_MISSING) is False

    assert await repo.create_user(sample_user) == USER_ID
    fetched = await repo.get_user(USER_ID)
    assert fetched == sample_user

    by_email = await repo.get_user_by_email("USER@EXAMPLE.COM")
    assert by_email == sample_user

    assert len(await repo.list_users(org_id=ORG_ID)) == 1
    assert len(await repo.list_users()) == 1

    # Password-only or empty UserUpdate returns True without persistence mutation
    assert await repo.update_user(USER_ID, UserUpdate()) is True

    assert (
        await repo.update_user(
            USER_ID,
            UserUpdate(
                name="Updated Name",
                role=UserRole.MANAGER,
                is_active=False,
                language="en",
                theme_mode="dark",
                organization_id=ORG_ID,
            ),
        )
        is True
    )
    updated_user = await repo.get_user(USER_ID)
    assert updated_user is not None
    assert updated_user.name == "Updated Name"
    assert updated_user.role == UserRole.MANAGER
    assert updated_user.is_active is False
    assert updated_user.language == "en"
    assert updated_user.theme_mode == "dark"

    created_from_dto = await repo.create_user(
        UserCreate(
            email="member@example.com",
            password="securepassword123",
            name="Member User",
            role=UserRole.MEMBER,
            organization_id=ORG_ID,
            is_active=True,
            language="fi",
            theme_mode="light",
            created_by=USER_ID,
        )
    )
    assert created_from_dto.startswith("usr_")

    assert await repo.delete_user(USER_ID) is True
    assert await repo.get_user(USER_ID) is None


@pytest.mark.asyncio
async def test_delete_org_data_cascade_and_system_org_protection_failure(
    repo: IdentityRepositoryImpl,
    sample_organization: Organization,
    sample_user: User,
) -> None:
    """Verify delete_org_data purges tenant organization atomically and blocks ROOT_SYSTEM deletion with 403."""
    with pytest.raises(AppException) as sys_exc:
        await repo.delete_org_data(SystemOrganizations.ROOT_SYSTEM.value)
    assert sys_exc.value.status_code == 403
    assert sys_exc.value.details["error_code"] == ErrorCodes.PERMISSION_DENIED.value

    await repo.create_organization(sample_organization)
    await repo.create_user(sample_user)
    await repo.delete_org_data(ORG_ID)
    assert await repo.get_organization(ORG_ID) is None
    assert await repo.get_user(USER_ID) is None


@pytest.mark.asyncio
async def test_get_org_usage_total_rollup_and_invalid_date_failure(
    repo: IdentityRepositoryImpl,
    base_uow: InMemoryUnitOfWork,
) -> None:
    """Verify get_org_usage_total aggregates append-only usage_records and rejects malformed ISO timestamps."""
    rec_1 = UsageRecordFactory.build(
        id="usg_0195f3a0000070018234567890abcdef",
        org_id=ORG_ID,
        user_id=USER_ID,
        cost_usd=0.05,
        timestamp=datetime(2025, 4, 1, 23, 18, 17, tzinfo=UTC),
    )
    rec_2 = UsageRecordFactory.build(
        id="usg_0199f3a0000070028234567890abcdef",
        org_id=ORG_ID,
        user_id=USER_ID,
        cost_usd=0.03,
        timestamp=datetime(2025, 10, 17, 19, 23, 58, tzinfo=UTC),
    )
    async with InMemoryUnitOfWork(base_uow.store) as uow:
        await uow.entities.insert_usage_record(rec_1)
        await uow.entities.insert_usage_record(rec_2)

    total = await repo.get_org_usage_total(ORG_ID, since="2025-01-01T00:00:00Z")
    assert total == pytest.approx(0.08)

    total_naive = await repo.get_org_usage_total(ORG_ID, since="2025-06-01T00:00:00")
    assert total_naive == pytest.approx(0.03)

    with pytest.raises(AppException) as bad_date_exc:
        await repo.get_org_usage_total(ORG_ID, since="not-an-iso-timestamp")
    assert bad_date_exc.value.status_code == 400
    assert bad_date_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_entity_adapter_direct_injection_and_postgres_fault_failure(
    sample_organization: Organization,
    sample_user: User,
) -> None:
    """Verify direct entity_adapter injection and PostgreSQL invalid prefix / SQL fault translation."""
    async with InMemoryUnitOfWork() as uow:
        repo_bound = IdentityRepositoryImpl(entity_adapter=uow.entities)
        assert await repo_bound.create_organization(sample_organization) == ORG_ID
        assert await repo_bound.get_organization(ORG_ID) == sample_organization
        assert await repo_bound.create_user(sample_user) == USER_ID
        assert await repo_bound.get_user(USER_ID) == sample_user

    pool = InMemoryAsyncPgPool()
    settings = Settings(
        storage_backend=StorageBackend.POSTGRES,
        postgres_host="db.internal",
        postgres_port=5432,
        postgres_user="quorum",
        postgres_db="quorum",
        postgres_command_timeout_seconds=5.0,
    )
    pool_mgr = PostgresPoolManager(settings=settings, pool=pool)
    pg_repo = IdentityRepositoryImpl(uow_factory=lambda: PostgresUnitOfWork(pool_mgr))

    with pytest.raises(AppException) as invalid_exc:
        await pg_repo.get_organization(USER_ID)
    assert invalid_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    try:
        pool.inject_fault("fetch", RuntimeError("simulated list failure"))
        with pytest.raises(AppException) as fault_exc:
            await pg_repo.list_organizations()
        assert fault_exc.value.status_code == 500
        assert fault_exc.value.details["error_code"] == ErrorCodes.STORAGE_ACCESS_FAILED.value
    finally:
        pool.clear_faults()
