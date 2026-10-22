"""Unit tests for organization service."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.exceptions import (
    AppException,
    ConflictError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import (
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    SystemOrganizations,
    TokenData,
    User,
    UserRole,
)
from backend_v2.models.enums import SystemLocale
from backend_v2.services.auth import (
    LEGACY_SYSTEM_ORG_ID,
    AuthService,
    OrganizationRepository,
    OrganizationService,
    UserRepository,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide an in-memory unified repository for testing."""
    return InMemoryUnifiedWorkflowRepository()


@pytest.mark.asyncio
async def test_auth_service_create_organization_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test create_organization permissions and success flow."""
    mock_audit = MagicMock(log_event=AsyncMock())
    auth = AuthService(mock_repo, use_firebase=False, audit_service=mock_audit)

    payload = OrganizationCreate(
        name="New Acme",
        admin_email="admin@acme.com",
        admin_password="password123",
        admin_name="Acme Admin",
        tpm_limit=50000,
        rpm_limit=500,
    )

    # Non-root initiator raises PermissionDeniedError
    non_root_token = TokenData(id="usr_member000001", role=UserRole.ADMIN, email="admin@test.com")
    with pytest.raises(PermissionDeniedError):
        await auth.create_organization(non_root_token, payload)

    # ROOT initiator succeeds
    root_token = TokenData(id="usr_root00000001", role=UserRole.ROOT, email="root@test.com")
    root_user = User(
        id="usr_root00000001",
        email="root@test.com",
        role=UserRole.ROOT,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id=SystemOrganizations.ROOT_SYSTEM,
    )
    await mock_repo.create_user(root_user)

    created_org = await auth.create_organization(root_token, payload)
    assert created_org.name == "New Acme"
    assert (await mock_repo.get_organization(created_org.id)) is not None
    mock_audit.log_event.assert_called()


@pytest.mark.asyncio
async def test_auth_service_delete_organization_branches(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test delete_organization permissions, protection, empty vs non-empty force delete."""
    mock_audit = MagicMock(log_event=AsyncMock())
    auth = AuthService(mock_repo, use_firebase=False, audit_service=mock_audit)

    root_token = TokenData(id="usr_root00000001", role=UserRole.ROOT, email="root@test.com")
    non_root_token = TokenData(id="usr_admin000001", role=UserRole.ADMIN, email="admin@test.com")

    # 1. Non-root cannot delete organization
    with pytest.raises(PermissionDeniedError):
        await auth.delete_organization(non_root_token, "org_target000001")

    # 2. Cannot delete system organizations
    with pytest.raises(PermissionDeniedError):
        await auth.delete_organization(root_token, SystemOrganizations.ROOT_SYSTEM)
    with pytest.raises(PermissionDeniedError):
        await auth.delete_organization(root_token, LEGACY_SYSTEM_ORG_ID)

    # 3. Non-empty organization without force raises ConflictError
    member = User(
        id="usr_member000001",
        email="m@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_target000001",
    )
    await mock_repo.create_organization(
        Organization(
            id="org_target000001",
            name="Target Org",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=50000,
            rpm_limit=500,
        )
    )
    await mock_repo.create_user(member)

    with pytest.raises(ConflictError) as exc_not_empty:
        await auth.delete_organization(root_token, "org_target000001", force=False)
    assert exc_not_empty.value.error_code == ErrorCodes.CONFLICT_ERROR

    # 4. Non-empty organization with force=True cascades user deletion and deletes org
    await auth.delete_organization(root_token, "org_target000001", force=True)
    assert (await mock_repo.get_user("usr_member000001")) is None
    assert (await mock_repo.get_organization("org_target000001")) is None
    mock_audit.log_event.assert_called()


@pytest.mark.asyncio
async def test_auth_service_organization_read_and_update(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test list_organizations, get_organization, update_organization, and get_users_by_organization."""
    auth = AuthService(mock_repo, use_firebase=False)
    test_org = Organization(
        id="org_test00000001",
        name="Test Organization",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(test_org)

    # 1. list_organizations
    root_token = TokenData(id="usr_root00000001", role=UserRole.ROOT, email="root@test.com")
    member_with_org = TokenData(
        id="usr_member000001", role=UserRole.MEMBER, email="m@test.com", organization_id="org_test00000001"
    )
    member_no_org = TokenData(
        id="usr_orphan000001", role=UserRole.MEMBER, email="orphan@test.com", organization_id=None
    )

    assert len(await auth.list_organizations(root_token)) == 1
    assert len(await auth.list_organizations(member_with_org)) == 1
    assert len(await auth.list_organizations(member_no_org)) == 0

    # 2. get_organization
    # Not found
    with pytest.raises(ResourceNotFoundError):
        await auth.get_organization(root_token, "org_missing00001")

    # Member accessing foreign organization
    foreign_org = test_org.model_copy(update={"id": "org_foreign00001", "name": "Foreign Org"})
    await mock_repo.create_organization(foreign_org)
    with pytest.raises(PermissionDeniedError):
        await auth.get_organization(member_with_org, "org_foreign00001")

    # Success
    found_org = await auth.get_organization(member_with_org, "org_test00000001")
    assert found_org.id == "org_test00000001"

    # 3. update_organization
    with pytest.raises(PermissionDeniedError):
        await auth.update_organization(member_with_org, "org_test00000001", OrganizationUpdateDTO(name="New"))

    # Root update with OrganizationUpdateDTO
    updated = await auth.update_organization(root_token, "org_test00000001", OrganizationUpdateDTO(name="Updated Name"))
    assert updated.id == "org_test00000001"

    # Root update with OrganizationCreate
    create_dto = OrganizationCreate(
        name="Brand New",
        admin_email="a@b.com",
        admin_password="password123",
        admin_name="Brand New Admin",
        tpm_limit=50000,
        rpm_limit=500,
    )
    updated2 = await auth.update_organization(root_token, "org_test00000001", create_dto)
    assert updated2.id == "org_test00000001"

    # 4. get_users_by_organization
    users = await auth.get_users_by_organization("org_empty0000001")
    assert users == []


@pytest.mark.asyncio
async def test_create_organization_root_initiator_success(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """TC-P3-01: ROOT initiator successfully creates organization and admin user."""
    auth_service = AuthService(mock_repo)
    root_user = User(
        id="usr_root0000000001",
        email="root@test.com",
        name="Root Admin",
        role=UserRole.ROOT,
        organization_id="org_system000000",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root_user)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)
    payload = OrganizationCreate(
        name="Acme Corp",
        admin_email="admin@acme.com",
        admin_name="Acme Admin",
        admin_password="password123",
        tpm_limit=50000,
        rpm_limit=500,
    )

    org = await auth_service.create_organization(root_initiator, payload)

    assert org.name == "Acme Corp"
    assert org.id.startswith("org_")
    assert org.is_active is True
    persisted_org = await mock_repo.get_organization(org.id)
    assert persisted_org is not None
    assert persisted_org.name == "Acme Corp"

    admin_user = await mock_repo.get_user_by_email("admin@acme.com")
    assert admin_user is not None
    assert admin_user.role == UserRole.ADMIN
    assert admin_user.organization_id == org.id


@pytest.mark.asyncio
async def test_create_organization_non_root_initiator_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-02: Non-ROOT initiator raises PermissionDeniedError when creating organization."""
    auth_service = AuthService(mock_repo)
    admin_initiator = TokenData(id="usr_admin000000001", role=UserRole.ADMIN, organization_id="org_test000000001")
    payload = OrganizationCreate(
        name="Acme Corp",
        admin_email="admin@acme.com",
        admin_name="Acme Admin",
        admin_password="password123",
        tpm_limit=50000,
        rpm_limit=500,
    )

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.create_organization(admin_initiator, payload)
    assert "Only ROOT can create organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_organization_logs_audit_event_when_audit_service_configured(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-03: create_organization logs ORG_CREATED audit event when audit_service is present."""
    mock_audit = AsyncMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit)
    root_user = User(
        id="usr_root0000000001",
        email="root@test.com",
        name="Root Admin",
        role=UserRole.ROOT,
        organization_id="org_system000000",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root_user)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)
    payload = OrganizationCreate(
        name="Audit Org",
        admin_email="admin@audit.com",
        admin_name="Audit Admin",
        admin_password="password123",
        tpm_limit=50000,
        rpm_limit=500,
    )

    org = await auth_service.create_organization(root_initiator, payload)

    assert mock_audit.log_event.call_count == 2
    actions = [call.kwargs["action"] for call in mock_audit.log_event.call_args_list]
    assert "ORG_CREATED" in actions
    assert "USER_CREATED" in actions

    org_created_call = next(c for c in mock_audit.log_event.call_args_list if c.kwargs["action"] == "ORG_CREATED")
    assert org_created_call.kwargs["actor_id"] == "usr_root0000000001"
    assert org_created_call.kwargs["organization_id"] == org.id
    assert org_created_call.kwargs["target_id"] == org.id


@pytest.mark.asyncio
async def test_get_organization_root_initiator_any_org_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-04: ROOT initiator can get any organization."""
    auth_service = AuthService(mock_repo)
    test_org = Organization(
        id="org_target0000001",
        name="Target Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(test_org)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    org = await auth_service.get_organization(root_initiator, "org_target0000001")
    assert org.id == "org_target0000001"
    assert org.name == "Target Org"


@pytest.mark.asyncio
async def test_get_organization_same_org_member_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-05: Non-root member can view their own organization."""
    auth_service = AuthService(mock_repo)
    test_org = Organization(
        id="org_member0000001",
        name="My Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(test_org)
    member_initiator = TokenData(id="usr_member0000001", role=UserRole.MEMBER, organization_id="org_member0000001")

    org = await auth_service.get_organization(member_initiator, "org_member0000001")
    assert org.id == "org_member0000001"
    assert org.name == "My Org"


@pytest.mark.asyncio
async def test_get_organization_foreign_org_member_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-06: Foreign org member cannot view another organization."""
    auth_service = AuthService(mock_repo)
    test_org = Organization(
        id="org_foreign000001",
        name="Foreign Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(test_org)
    foreign_member = TokenData(id="usr_member0000002", role=UserRole.MEMBER, organization_id="org_other00000001")

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.get_organization(foreign_member, "org_foreign000001")
    assert "You do not have permission to view this organization." in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_organization_non_existent_org_raises_resource_not_found(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-07: Fetching non-existent organization raises ResourceNotFoundError."""
    auth_service = AuthService(mock_repo)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await auth_service.get_organization(root_initiator, "org_missing000001")
    assert exc_info.value.status_code == 404
    assert exc_info.value.details is not None
    assert exc_info.value.details["resource_type"] == "organization"
    assert exc_info.value.details["resource_id"] == "org_missing000001"


@pytest.mark.asyncio
async def test_list_organizations_root_initiator_returns_all_orgs(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-08: ROOT initiator lists all organizations in the repository."""
    auth_service = AuthService(mock_repo)
    org1 = Organization(
        id="org_all0000000001",
        name="Org 1",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    org2 = Organization(
        id="org_all0000000002",
        name="Org 2",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org1)
    await mock_repo.create_organization(org2)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    orgs = await auth_service.list_organizations(root_initiator)
    assert len(orgs) == 2
    assert {o.id for o in orgs} == {"org_all0000000001", "org_all0000000002"}


@pytest.mark.asyncio
async def test_list_organizations_tenant_initiator_returns_own_org_only(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-09: Tenant initiator lists only their own organization."""
    auth_service = AuthService(mock_repo)
    org1 = Organization(
        id="org_mine00000001",
        name="My Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    org2 = Organization(
        id="org_other00000001",
        name="Other Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org1)
    await mock_repo.create_organization(org2)
    admin_initiator = TokenData(id="usr_admin00000001", role=UserRole.ADMIN, organization_id="org_mine00000001")

    orgs = await auth_service.list_organizations(admin_initiator)
    assert len(orgs) == 1
    assert orgs[0].id == "org_mine00000001"


@pytest.mark.asyncio
async def test_list_organizations_tenant_initiator_no_org_id_returns_empty_list(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-10: Tenant initiator with no organization_id returns empty list."""
    auth_service = AuthService(mock_repo)
    org1 = Organization(
        id="org_some00000001",
        name="Some Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org1)
    member_no_org = TokenData(id="usr_noorg00000001", role=UserRole.MEMBER, organization_id=None)

    orgs = await auth_service.list_organizations(member_no_org)
    assert orgs == []


@pytest.mark.asyncio
async def test_update_organization_root_initiator_with_update_dto_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-11: ROOT initiator updates organization with OrganizationUpdateDTO."""
    auth_service = AuthService(mock_repo)
    org = Organization(
        id="org_update0000001",
        name="Old Name",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)
    dto = OrganizationUpdateDTO(name="New Name", tpm_limit=60000)

    updated = await auth_service.update_organization(root_initiator, "org_update0000001", dto)
    assert updated.id == "org_update0000001"
    assert updated.name == "New Name"
    assert updated.tpm_limit == 60000


@pytest.mark.asyncio
async def test_update_organization_root_initiator_with_create_dto_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-12: ROOT initiator updates organization using OrganizationCreate payload."""
    auth_service = AuthService(mock_repo)
    org = Organization(
        id="org_update0000002",
        name="Old Name",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)
    create_dto = OrganizationCreate(
        name="Converted Name",
        admin_email="a@b.com",
        admin_name="Admin",
        admin_password="password",
        tpm_limit=70000,
        rpm_limit=700,
    )

    updated = await auth_service.update_organization(root_initiator, "org_update0000002", create_dto)
    assert updated.id == "org_update0000002"
    assert updated.name == "Converted Name"
    assert updated.tpm_limit == 70000


@pytest.mark.asyncio
async def test_update_organization_non_root_initiator_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-13: Non-ROOT initiator raises PermissionDeniedError on update."""
    auth_service = AuthService(mock_repo)
    admin_initiator = TokenData(id="usr_admin00000001", role=UserRole.ADMIN, organization_id="org_test000000001")
    dto = OrganizationUpdateDTO(name="New Name")

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_organization(admin_initiator, "org_test000000001", dto)
    assert "Only ROOT can update organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_organization_non_existent_org_raises_resource_not_found(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-14: Updating non-existent organization raises ResourceNotFoundError."""
    auth_service = AuthService(mock_repo)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)
    dto = OrganizationUpdateDTO(name="New Name")

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await auth_service.update_organization(root_initiator, "org_missing000001", dto)
    assert exc_info.value.status_code == 404
    assert exc_info.value.details is not None
    assert exc_info.value.details["resource_type"] == "organization"
    assert exc_info.value.details["resource_id"] == "org_missing000001"


@pytest.mark.asyncio
async def test_delete_organization_root_empty_org_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-15: ROOT deletes empty organization successfully."""
    mock_audit = AsyncMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit)
    org = Organization(
        id="org_delete0000001",
        name="Delete Me",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    await auth_service.delete_organization(root_initiator, "org_delete0000001")

    persisted = await mock_repo.get_organization("org_delete0000001")
    assert persisted is None
    assert mock_audit.log_event.call_count == 1
    call_kwargs = mock_audit.log_event.call_args.kwargs
    assert call_kwargs["action"] == "ORG_DELETED"
    assert call_kwargs["organization_id"] == "org_delete0000001"


@pytest.mark.asyncio
async def test_delete_organization_non_root_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-16: Non-ROOT user raises PermissionDeniedError on delete organization."""
    auth_service = AuthService(mock_repo)
    admin_initiator = TokenData(id="usr_admin00000001", role=UserRole.ADMIN, organization_id="org_test000000001")

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.delete_organization(admin_initiator, "org_test000000001")
    assert "Only ROOT can delete organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_organization_system_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-17: Deleting system organization raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.delete_organization(root_initiator, "system")
    assert "protected and CANNOT be deleted" in str(exc_info.value)

    with pytest.raises(PermissionDeniedError) as exc_info_legacy:
        await auth_service.delete_organization(root_initiator, LEGACY_SYSTEM_ORG_ID)
    assert "protected and CANNOT be deleted" in str(exc_info_legacy.value)


@pytest.mark.asyncio
async def test_delete_organization_non_empty_without_force_raises_conflict_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-18: Non-empty organization deletion without force raises ConflictError."""
    auth_service = AuthService(mock_repo)
    org = Organization(
        id="org_busy000000001",
        name="Busy Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org)
    user1 = User(
        id="usr_busy000000001",
        email="busy1@test.com",
        name="Busy 1",
        role=UserRole.MEMBER,
        organization_id="org_busy000000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    user2 = User(
        id="usr_busy000000002",
        email="busy2@test.com",
        name="Busy 2",
        role=UserRole.MEMBER,
        organization_id="org_busy000000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(user1)
    await mock_repo.create_user(user2)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    with pytest.raises(ConflictError) as exc_info:
        await auth_service.delete_organization(root_initiator, "org_busy000000001", force=False)
    assert "Organization is not empty" in exc_info.value.message
    assert exc_info.value.details is not None
    assert exc_info.value.details["reason"] == "ORG_NOT_EMPTY"


@pytest.mark.asyncio
async def test_delete_organization_non_empty_with_force_cascades_deletion_and_logs_audit(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-19: Force deletion cascades delete to users in org and Firebase."""
    mock_audit = AsyncMock()
    mock_fb = MagicMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit, use_firebase=True, firebase_auth=mock_fb)

    org = Organization(
        id="org_force00000001",
        name="Force Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
    )
    await mock_repo.create_organization(org)
    user1 = User(
        id="usr_cascade000001",
        email="cascade1@test.com",
        name="Cascade 1",
        role=UserRole.MEMBER,
        organization_id="org_force00000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    user2 = User(
        id="usr_cascade000002",
        email="cascade2@test.com",
        name="Cascade 2",
        role=UserRole.MEMBER,
        organization_id="org_force00000001",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(user1)
    await mock_repo.create_user(user2)
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)

    await auth_service.delete_organization(root_initiator, "org_force00000001", force=True)

    assert await mock_repo.get_organization("org_force00000001") is None
    assert await mock_repo.get_user("usr_cascade000001") is None
    assert await mock_repo.get_user("usr_cascade000002") is None
    assert mock_fb.delete_user.call_count == 2
    assert mock_audit.log_event.call_count == 1
    call_kwargs = mock_audit.log_event.call_args.kwargs
    assert call_kwargs["action"] == "ORG_DELETED"
    assert call_kwargs["details"]["users_deleted"] == 2
    assert call_kwargs["details"]["force_used"] is True


@pytest.mark.asyncio
async def test_direct_organization_service_execution(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verifies direct instantiation and execution of OrganizationService."""
    org_repo = OrganizationRepository(mock_repo)
    user_repo = UserRepository(mock_repo)
    mock_audit = AsyncMock()
    mock_create_user = AsyncMock()

    service = OrganizationService(
        org_repo=org_repo,
        user_repo=user_repo,
        audit_service=mock_audit,
        user_creator=mock_create_user,
    )

    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)
    payload = OrganizationCreate(
        name="Direct Org",
        admin_email="direct@org.com",
        admin_name="Direct Admin",
        admin_password="password123",
        tpm_limit=50000,
        rpm_limit=500,
    )

    created = await service.create_organization(root_initiator, payload)
    assert created.name == "Direct Org"
    assert mock_create_user.call_count == 1

    fetched = await service.get_organization(root_initiator, created.id)
    assert fetched.id == created.id

    listed = await service.list_organizations(root_initiator)
    assert any(o.id == created.id for o in listed)

    updated = await service.update_organization(
        root_initiator, created.id, OrganizationUpdateDTO(name="Updated Direct")
    )
    assert updated.name == "Updated Direct"

    await service.delete_organization(root_initiator, created.id)
    assert await org_repo.get_by_id(created.id) is None


@pytest.mark.asyncio
async def test_direct_organization_service_execution_missing_user_creator_fails_fast(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verifies that create_organization raises AppException if user_creator protocol is missing."""
    org_repo = OrganizationRepository(mock_repo)
    user_repo = UserRepository(mock_repo)
    service = OrganizationService(
        org_repo=org_repo,
        user_repo=user_repo,
        user_creator=None,
    )
    root_initiator = TokenData(id="usr_root0000000001", role=UserRole.ROOT)
    payload = OrganizationCreate(
        name="Missing Creator Org",
        admin_email="direct@org.com",
        admin_name="Direct Admin",
        admin_password="password123",
        tpm_limit=50000,
        rpm_limit=500,
    )
    with pytest.raises(AppException) as exc_info:
        await service.create_organization(root_initiator, payload)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
