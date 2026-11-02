"""Unit tests for organization service and B2B invitation flows."""

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
    InvitationAcceptRequestDTO,
    InvitationBatchCreateDTO,
    InvitationCreateDTO,
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    SystemOrganizations,
    TokenData,
    TokenExchangeRequestDTO,
    User,
    UserRole,
)
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EmailDeliveryStatus, EntityPrefix, InvitationStatus, SystemLocale
from backend_v2.services.auth import (
    AuthService,
    OrganizationRepository,
    OrganizationService,
    UserRepository,
)
from backend_v2.settings import Settings
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

    non_root_token = TokenData(id="usr_0195f3a0000070008000000000000101", role=UserRole.ADMIN, email="admin@test.com")
    with pytest.raises(PermissionDeniedError):
        await auth.create_organization(non_root_token, payload)

    root_token = TokenData(id="usr_0195f3a0000070008000000000000102", role=UserRole.ROOT, email="root@test.com")
    root_user = User(
        id="usr_0195f3a0000070008000000000000102",
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

    root_token = TokenData(id="usr_0195f3a0000070008000000000000102", role=UserRole.ROOT, email="root@test.com")
    non_root_token = TokenData(id="usr_0195f3a0000070008000000000000103", role=UserRole.ADMIN, email="admin@test.com")

    with pytest.raises(PermissionDeniedError):
        await auth.delete_organization(non_root_token, "org_0195f3a0000070008000000000000201")

    with pytest.raises(PermissionDeniedError):
        await auth.delete_organization(root_token, SystemOrganizations.ROOT_SYSTEM)
    with pytest.raises(PermissionDeniedError):
        await auth.delete_organization(root_token, SystemOrganizations.ROOT_SYSTEM)

    member = User(
        id="usr_0195f3a0000070008000000000000101",
        email="m@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000201",
    )
    await mock_repo.create_organization(
        Organization(
            id="org_0195f3a0000070008000000000000201",
            name="Target Org",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=50000,
            rpm_limit=500,
            allowed_email_domains=[],
        )
    )
    await mock_repo.create_user(member)

    with pytest.raises(ConflictError) as exc_not_empty:
        await auth.delete_organization(root_token, "org_0195f3a0000070008000000000000201", force=False)
    assert exc_not_empty.value.error_code == ErrorCodes.CONFLICT_ERROR

    await auth.delete_organization(root_token, "org_0195f3a0000070008000000000000201", force=True)
    assert (await mock_repo.get_user("usr_0195f3a0000070008000000000000101")) is None
    assert (await mock_repo.get_organization("org_0195f3a0000070008000000000000201")) is None
    mock_audit.log_event.assert_called()


@pytest.mark.asyncio
async def test_auth_service_organization_read_and_update(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Test list_organizations, get_organization, update_organization, and get_users_by_organization."""
    auth = AuthService(mock_repo, use_firebase=False)
    test_org = Organization(
        id="org_0195f3a0000070008000000000000202",
        name="Test Organization",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(test_org)

    root_token = TokenData(id="usr_0195f3a0000070008000000000000102", role=UserRole.ROOT, email="root@test.com")
    member_with_org = TokenData(
        id="usr_0195f3a0000070008000000000000101",
        role=UserRole.MEMBER,
        email="m@test.com",
        organization_id="org_0195f3a0000070008000000000000202",
    )
    member_no_org = TokenData(
        id="usr_0195f3a0000070008000000000000104", role=UserRole.MEMBER, email="orphan@test.com", organization_id=None
    )

    assert len(await auth.list_organizations(root_token)) == 1
    assert len(await auth.list_organizations(member_with_org)) == 1
    assert len(await auth.list_organizations(member_no_org)) == 0

    with pytest.raises(ResourceNotFoundError):
        await auth.get_organization(root_token, "org_0195f3a0000070008000000000000203")

    foreign_org = test_org.model_copy(update={"id": "org_0195f3a0000070008000000000000204", "name": "Foreign Org"})
    await mock_repo.create_organization(foreign_org)
    with pytest.raises(PermissionDeniedError):
        await auth.get_organization(member_with_org, "org_0195f3a0000070008000000000000204")

    found_org = await auth.get_organization(member_with_org, "org_0195f3a0000070008000000000000202")
    assert found_org.id == "org_0195f3a0000070008000000000000202"

    with pytest.raises(PermissionDeniedError):
        await auth.update_organization(
            member_with_org, "org_0195f3a0000070008000000000000202", OrganizationUpdateDTO(name="New")
        )

    updated = await auth.update_organization(
        root_token, "org_0195f3a0000070008000000000000202", OrganizationUpdateDTO(name="Updated Name")
    )
    assert updated.id == "org_0195f3a0000070008000000000000202"

    create_dto = OrganizationCreate(
        name="Brand New",
        admin_email="a@b.com",
        admin_password="password123",
        admin_name="Brand New Admin",
        tpm_limit=50000,
        rpm_limit=500,
    )
    updated2 = await auth.update_organization(root_token, "org_0195f3a0000070008000000000000202", create_dto)
    assert updated2.id == "org_0195f3a0000070008000000000000202"

    users = await auth.get_users_by_organization("org_0195f3a0000070008000000000000205")
    assert users == []


@pytest.mark.asyncio
async def test_create_organization_root_initiator_success(mock_repo: InMemoryUnifiedWorkflowRepository) -> None:
    """TC-P3-01: ROOT initiator successfully creates organization and admin user."""
    auth_service = AuthService(mock_repo)
    root_user = User(
        id="usr_0195f3a0000070008000000000000105",
        email="root@test.com",
        name="Root Admin",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root_user)
    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)
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
    admin_initiator = TokenData(
        id="usr_0195f3a0000070008000000000000106",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000206",
    )
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
        id="usr_0195f3a0000070008000000000000105",
        email="root@test.com",
        name="Root Admin",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(root_user)
    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)
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
    assert org_created_call.kwargs["actor_id"] == "usr_0195f3a0000070008000000000000105"
    assert org_created_call.kwargs["organization_id"] == org.id
    assert org_created_call.kwargs["target_id"] == org.id


@pytest.mark.asyncio
async def test_get_organization_root_initiator_any_org_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-04: ROOT initiator can get any organization."""
    auth_service = AuthService(mock_repo)
    test_org = Organization(
        id="org_0195f3a0000070008000000000000207",
        name="Target Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(test_org)
    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)

    org = await auth_service.get_organization(root_initiator, "org_0195f3a0000070008000000000000207")
    assert org.id == "org_0195f3a0000070008000000000000207"
    assert org.name == "Target Org"


@pytest.mark.asyncio
async def test_get_organization_same_org_member_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-05: Non-root member can view their own organization."""
    auth_service = AuthService(mock_repo)
    test_org = Organization(
        id="org_0195f3a0000070008000000000000208",
        name="My Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(test_org)
    member_initiator = TokenData(
        id="usr_0195f3a0000070008000000000000107",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000208",
    )

    org = await auth_service.get_organization(member_initiator, "org_0195f3a0000070008000000000000208")
    assert org.id == "org_0195f3a0000070008000000000000208"
    assert org.name == "My Org"


@pytest.mark.asyncio
async def test_get_organization_foreign_org_member_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-06: Foreign org member cannot view another organization."""
    auth_service = AuthService(mock_repo)
    test_org = Organization(
        id="org_0195f3a0000070008000000000000209",
        name="Foreign Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(test_org)
    foreign_member = TokenData(
        id="usr_0195f3a0000070008000000000000108",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000210",
    )

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.get_organization(foreign_member, "org_0195f3a0000070008000000000000209")
    assert "You do not have permission to view this organization." in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_organization_non_existent_org_raises_resource_not_found(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-07: Fetching non-existent organization raises ResourceNotFoundError."""
    auth_service = AuthService(mock_repo)
    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await auth_service.get_organization(root_initiator, "org_0195f3a0000070008000000000000211")
    assert exc_info.value.status_code == 404
    assert exc_info.value.details is not None
    assert exc_info.value.details["resource_type"] == "organization"
    assert exc_info.value.details["resource_id"] == "org_0195f3a0000070008000000000000211"


@pytest.mark.asyncio
async def test_list_organizations_root_initiator_returns_all_orgs(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-08: ROOT initiator lists all organizations in the repository."""
    auth_service = AuthService(mock_repo)
    org1 = Organization(
        id="org_0195f3a0000070008000000000000212",
        name="Org 1",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    org2 = Organization(
        id="org_0195f3a0000070008000000000000213",
        name="Org 2",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org1)
    await mock_repo.create_organization(org2)
    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)

    orgs = await auth_service.list_organizations(root_initiator)
    assert len(orgs) == 2
    assert {o.id for o in orgs} == {"org_0195f3a0000070008000000000000212", "org_0195f3a0000070008000000000000213"}


@pytest.mark.asyncio
async def test_list_organizations_tenant_initiator_returns_own_org_only(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-09: Tenant initiator lists only their own organization."""
    auth_service = AuthService(mock_repo)
    org1 = Organization(
        id="org_0195f3a0000070008000000000000214",
        name="My Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    org2 = Organization(
        id="org_0195f3a0000070008000000000000210",
        name="Other Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org1)
    await mock_repo.create_organization(org2)
    admin_initiator = TokenData(
        id="usr_0195f3a0000070008000000000000109",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000214",
    )

    orgs = await auth_service.list_organizations(admin_initiator)
    assert len(orgs) == 1
    assert orgs[0].id == "org_0195f3a0000070008000000000000214"


@pytest.mark.asyncio
async def test_list_organizations_tenant_initiator_no_org_id_returns_empty_list(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-10: Tenant initiator with no organization_id returns empty list."""
    auth_service = AuthService(mock_repo)
    org1 = Organization(
        id="org_0195f3a0000070008000000000000215",
        name="Some Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org1)
    member_no_org = TokenData(id="usr_0195f3a0000070008000000000000110", role=UserRole.MEMBER, organization_id=None)

    orgs = await auth_service.list_organizations(member_no_org)
    assert orgs == []


@pytest.mark.asyncio
async def test_update_organization_root_initiator_with_update_dto_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-11: ROOT initiator updates organization with OrganizationUpdateDTO."""
    auth_service = AuthService(mock_repo)
    org = Organization(
        id="org_0195f3a0000070008000000000000216",
        name="Old Name",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org)
    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)
    dto = OrganizationUpdateDTO(name="New Name", tpm_limit=60000)

    updated = await auth_service.update_organization(root_initiator, "org_0195f3a0000070008000000000000216", dto)
    assert updated.id == "org_0195f3a0000070008000000000000216"
    assert updated.name == "New Name"
    assert updated.tpm_limit == 60000


@pytest.mark.asyncio
async def test_update_organization_root_initiator_with_create_dto_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-12: ROOT initiator updates organization using OrganizationCreate payload."""
    auth_service = AuthService(mock_repo)
    org = Organization(
        id="org_0195f3a0000070008000000000000217",
        name="Old Name",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org)
    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)
    create_dto = OrganizationCreate(
        name="Converted Name",
        admin_email="a@b.com",
        admin_name="Admin",
        admin_password="password",
        tpm_limit=70000,
        rpm_limit=700,
    )

    updated = await auth_service.update_organization(root_initiator, "org_0195f3a0000070008000000000000217", create_dto)
    assert updated.id == "org_0195f3a0000070008000000000000217"
    assert updated.name == "Converted Name"
    assert updated.tpm_limit == 70000


@pytest.mark.asyncio
async def test_update_organization_non_root_initiator_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-13: Non-ROOT initiator raises PermissionDeniedError on update."""
    auth_service = AuthService(mock_repo)
    admin_initiator = TokenData(
        id="usr_0195f3a0000070008000000000000109",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000206",
    )
    dto = OrganizationUpdateDTO(name="New Name")

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_organization(admin_initiator, "org_0195f3a0000070008000000000000206", dto)
    assert "Only ROOT can update organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_update_organization_non_existent_org_raises_resource_not_found(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-14: Updating non-existent organization raises ResourceNotFoundError."""
    auth_service = AuthService(mock_repo)
    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)
    dto = OrganizationUpdateDTO(name="New Name")

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await auth_service.update_organization(root_initiator, "org_0195f3a0000070008000000000000211", dto)
    assert exc_info.value.status_code == 404
    assert exc_info.value.details is not None
    assert exc_info.value.details["resource_type"] == "organization"
    assert exc_info.value.details["resource_id"] == "org_0195f3a0000070008000000000000211"


@pytest.mark.asyncio
async def test_delete_organization_root_empty_org_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-15: ROOT deletes empty organization successfully."""
    mock_audit = AsyncMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit)
    org = Organization(
        id="org_0195f3a0000070008000000000000218",
        name="Delete Me",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org)
    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)

    await auth_service.delete_organization(root_initiator, "org_0195f3a0000070008000000000000218")

    persisted = await mock_repo.get_organization("org_0195f3a0000070008000000000000218")
    assert persisted is None
    assert mock_audit.log_event.call_count == 1
    call_kwargs = mock_audit.log_event.call_args.kwargs
    assert call_kwargs["action"] == "ORG_DELETED"
    assert call_kwargs["organization_id"] == "org_0195f3a0000070008000000000000218"


@pytest.mark.asyncio
async def test_delete_organization_non_root_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-16: Non-ROOT user raises PermissionDeniedError on delete organization."""
    auth_service = AuthService(mock_repo)
    admin_initiator = TokenData(
        id="usr_0195f3a0000070008000000000000109",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000206",
    )

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.delete_organization(admin_initiator, "org_0195f3a0000070008000000000000206")
    assert "Only ROOT can delete organizations." in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_organization_system_org_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-17: Deleting system organization raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.delete_organization(root_initiator, "system")
    assert "protected and CANNOT be deleted" in str(exc_info.value)

    with pytest.raises(PermissionDeniedError) as exc_info_legacy:
        await auth_service.delete_organization(root_initiator, SystemOrganizations.ROOT_SYSTEM)
    assert "protected and CANNOT be deleted" in str(exc_info_legacy.value)


@pytest.mark.asyncio
async def test_delete_organization_non_empty_without_force_raises_conflict_error(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-18: Non-empty organization deletion without force raises ConflictError."""
    auth_service = AuthService(mock_repo)
    org = Organization(
        id="org_0195f3a0000070008000000000000219",
        name="Busy Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org)
    user1 = User(
        id="usr_0195f3a0000070008000000000000111",
        email="busy1@test.com",
        name="Busy 1",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000219",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    user2 = User(
        id="usr_0195f3a0000070008000000000000112",
        email="busy2@test.com",
        name="Busy 2",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000219",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(user1)
    await mock_repo.create_user(user2)
    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)

    with pytest.raises(ConflictError) as exc_info:
        await auth_service.delete_organization(root_initiator, "org_0195f3a0000070008000000000000219", force=False)
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
        id="org_0195f3a0000070008000000000000220",
        name="Force Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org)
    user1 = User(
        id="usr_0195f3a0000070008000000000000113",
        email="cascade1@test.com",
        name="Cascade 1",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000220",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    user2 = User(
        id="usr_0195f3a0000070008000000000000114",
        email="cascade2@test.com",
        name="Cascade 2",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000220",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(user1)
    await mock_repo.create_user(user2)
    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)

    await auth_service.delete_organization(root_initiator, "org_0195f3a0000070008000000000000220", force=True)

    assert await mock_repo.get_organization("org_0195f3a0000070008000000000000220") is None
    assert await mock_repo.get_user("usr_0195f3a0000070008000000000000113") is None
    assert await mock_repo.get_user("usr_0195f3a0000070008000000000000114") is None
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

    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)
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
    root_initiator = TokenData(id="usr_0195f3a0000070008000000000000105", role=UserRole.ROOT)
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


@pytest.mark.asyncio
async def test_delete_organization_force_firebase_delete_error_raises_app_exception(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verifies that force deletion raises AppException when Firebase user deletion fails."""
    mock_fb = MagicMock()
    mock_fb.delete_user.side_effect = RuntimeError("Firebase transport error")
    auth_service = AuthService(mock_repo, use_firebase=True, firebase_auth=mock_fb)

    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    user_id = generate_opaque_id(EntityPrefix.USER)
    root_id = generate_opaque_id(EntityPrefix.USER)

    org = Organization(
        id=org_id,
        name="Firebase Fault Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org)
    user = User(
        id=user_id,
        email="fb_fault@test.com",
        name="FB Fault User",
        role=UserRole.MEMBER,
        organization_id=org_id,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    await mock_repo.create_user(user)
    root_initiator = TokenData(id=root_id, role=UserRole.ROOT)

    with pytest.raises(AppException) as exc_info:
        await auth_service.delete_organization(root_initiator, org_id, force=True)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR.value
    mock_fb.delete_user.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_organization_service_with_exchanged_quorum_jwt_token_data(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify OrganizationService accepts stateless TokenData decoded from an exchanged Quorum Local JWT."""
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        require_mfa=True,
    )
    monkeypatch.setattr("backend_v2.services.auth.token_service.get_settings", lambda: mock_settings)
    monkeypatch.setattr("backend_v2.services.auth.get_settings", lambda: mock_settings)

    root_id = generate_opaque_id(EntityPrefix.USER)
    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    root_user = User(
        id=root_id,
        email="jwt_root@test.com",
        name="JWT Root",
        role=UserRole.ROOT,
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    org = Organization(
        id=org_id,
        name="JWT Verified Org",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_user(root_user)
    await mock_repo.create_organization(org)

    auth_service = AuthService(mock_repo, use_firebase=False)
    exchanged = await auth_service.token_service.exchange_firebase_token(
        TokenExchangeRequestDTO(target_user_id=root_id)
    )
    verified_token_data = await auth_service.verify_token(exchanged.access_token)
    assert verified_token_data.mfa_verified is True
    assert verified_token_data.jti is not None

    fetched_org = await auth_service.get_organization(verified_token_data, org_id)
    assert fetched_org.id == org_id


@pytest.mark.asyncio
async def test_invitation_create_batch_revoke_and_accept_flow_positive(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify create_invitation, create_invitation_batch, list_invitations, revoke_invitation, and accept_invitation."""
    mock_audit = MagicMock(log_event=AsyncMock())
    auth = AuthService(mock_repo, use_firebase=False, audit_service=mock_audit)

    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    admin_id = generate_opaque_id(EntityPrefix.USER)
    org = Organization(
        id=org_id,
        name="Acme Invitation Corp",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=["acme.com"],
    )
    await mock_repo.create_organization(org)

    admin_token = TokenData(id=admin_id, role=UserRole.ADMIN, organization_id=org_id, email="admin@acme.com")
    inv_dto = await auth.org_service.create_invitation(
        admin_token,
        org_id,
        InvitationCreateDTO(email="alice@acme.com", role=UserRole.MANAGER, expires_in_hours=48),
    )
    assert inv_dto.organization_id == org_id
    assert inv_dto.email == "alice@acme.com"
    assert inv_dto.role == UserRole.MANAGER
    assert inv_dto.status == InvitationStatus.PENDING
    assert inv_dto.email_delivery_status == EmailDeliveryStatus.SENT

    raw_token = auth.org_service.get_last_generated_token(inv_dto.id)
    assert raw_token is not None

    batch_res = await auth.org_service.create_invitation_batch(
        admin_token,
        org_id,
        InvitationBatchCreateDTO(
            recipients=[
                InvitationCreateDTO(email="bob@acme.com", role=UserRole.MEMBER),
                InvitationCreateDTO(email="BOB@acme.com", role=UserRole.MEMBER),
                InvitationCreateDTO(email="carol@acme.com", role=UserRole.VIEWER),
            ]
        ),
    )
    assert batch_res.created_count == 2
    assert len(batch_res.invitations) == 2

    listed = await auth.org_service.list_invitations(admin_token, org_id)
    assert len(listed) == 3

    revoked_dto = await auth.org_service.revoke_invitation(admin_token, org_id, batch_res.invitations[1].id)
    assert revoked_dto.status == InvitationStatus.REVOKED

    alice_id = generate_opaque_id(EntityPrefix.USER)
    alice_token = TokenData(
        id=alice_id,
        role=UserRole.MEMBER,
        organization_id=None,
        email="alice@acme.com",
    )
    accepted_user = await auth.org_service.accept_invitation(
        alice_token,
        InvitationAcceptRequestDTO(raw_token=raw_token, name="Alice Manager"),
    )
    assert accepted_user.id == alice_id
    assert accepted_user.organization_id == org_id
    assert accepted_user.role == UserRole.MANAGER
    assert accepted_user.name == "Alice Manager"

    # Re-accepting an already-accepted invitation raises ConflictError
    with pytest.raises(ConflictError):
        await auth.org_service.accept_invitation(
            alice_token,
            InvitationAcceptRequestDTO(raw_token=raw_token),
        )

    # Accepting for an existing unassigned User record updates in-place
    bob_id = generate_opaque_id(EntityPrefix.USER)
    await mock_repo.create_user(
        User(
            id=bob_id,
            email="bob@acme.com",
            name="Bob Existing",
            role=UserRole.VIEWER,
            organization_id=None,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    bob_raw_token = auth.org_service.get_last_generated_token(batch_res.invitations[0].id)
    assert bob_raw_token is not None
    bob_accepted = await auth.org_service.accept_invitation(
        InvitationAcceptRequestDTO(raw_token=bob_raw_token, name="Bob Promoted"),
    )
    assert bob_accepted.id == bob_id
    assert bob_accepted.organization_id == org_id
    assert bob_accepted.role == UserRole.MEMBER
    assert bob_accepted.name == "Bob Promoted"

    # Revoking or accepting nonexistent invitation raises ResourceNotFoundError
    with pytest.raises(ResourceNotFoundError):
        await auth.org_service.revoke_invitation(admin_token, org_id, generate_opaque_id(EntityPrefix.INVITATION))

    with pytest.raises(ResourceNotFoundError):
        await auth.org_service.accept_invitation(
            alice_token,
            InvitationAcceptRequestDTO(raw_token="nonexistent_token_value_1234567890"),
        )


@pytest.mark.asyncio
async def test_invitation_accept_collision_already_assigned_negative(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify 1:1 Flat Identity Collision Guard raises ConflictError with USER_ALREADY_ASSIGNED."""
    auth = AuthService(mock_repo, use_firebase=False)
    org_a_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    org_b_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    admin_b_id = generate_opaque_id(EntityPrefix.USER)
    existing_user_id = generate_opaque_id(EntityPrefix.USER)

    for oid, name in ((org_a_id, "Org A"), (org_b_id, "Org B")):
        await mock_repo.create_organization(
            Organization(
                id=oid,
                name=name,
                is_active=True,
                created_at=datetime.now(timezone.utc),
                tier="enterprise",
                subscription_status=SubscriptionStatus.ACTIVE,
                quota_limit=500.0,
                tpm_limit=50000,
                rpm_limit=500,
                allowed_email_domains=[],
            )
        )

    await mock_repo.create_user(
        User(
            id=existing_user_id,
            email="assigned@corp.com",
            name="Already Assigned",
            role=UserRole.MEMBER,
            organization_id=org_a_id,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )

    admin_b_token = TokenData(id=admin_b_id, role=UserRole.ADMIN, organization_id=org_b_id, email="admin@orgb.com")
    inv_dto = await auth.org_service.create_invitation(
        admin_b_token,
        org_b_id,
        InvitationCreateDTO(email="assigned@corp.com", role=UserRole.MEMBER),
    )
    raw_token = auth.org_service.get_last_generated_token(inv_dto.id)
    assert raw_token is not None

    caller_token = TokenData(
        id=existing_user_id,
        role=UserRole.MEMBER,
        organization_id=org_a_id,
        email="assigned@corp.com",
    )
    with pytest.raises(ConflictError) as exc_info:
        await auth.org_service.accept_invitation(
            caller_token,
            InvitationAcceptRequestDTO(raw_token=raw_token),
        )
    assert exc_info.value.error_code == ErrorCodes.USER_ALREADY_ASSIGNED.value


@pytest.mark.asyncio
async def test_invitation_domain_allowlist_and_role_hierarchy_negative(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify domain allowlist, role hierarchy, duplicate pending, and expired/mismatched token rejections."""
    auth = AuthService(mock_repo, use_firebase=False)
    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    admin_id = generate_opaque_id(EntityPrefix.USER)
    manager_id = generate_opaque_id(EntityPrefix.USER)

    await mock_repo.create_organization(
        Organization(
            id=org_id,
            name="Restricted Domain Org",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=50000,
            rpm_limit=500,
            allowed_email_domains=["allowed.fi"],
        )
    )

    manager_token = TokenData(id=manager_id, role=UserRole.MANAGER, organization_id=org_id, email="mgr@allowed.fi")
    with pytest.raises(PermissionDeniedError):
        await auth.org_service.create_invitation(
            manager_token,
            org_id,
            InvitationCreateDTO(email="user@allowed.fi", role=UserRole.MEMBER),
        )

    admin_token = TokenData(id=admin_id, role=UserRole.ADMIN, organization_id=org_id, email="admin@allowed.fi")
    with pytest.raises(PermissionDeniedError):
        await auth.org_service.create_invitation(
            admin_token,
            org_id,
            InvitationCreateDTO(email="root@allowed.fi", role=UserRole.ROOT),
        )

    with pytest.raises(PermissionDeniedError):
        await auth.org_service.create_invitation(
            admin_token,
            org_id,
            InvitationCreateDTO(email="outsider@external.com", role=UserRole.MEMBER),
        )

    inv_dto = await auth.org_service.create_invitation(
        admin_token,
        org_id,
        InvitationCreateDTO(email="valid@allowed.fi", role=UserRole.MEMBER),
    )
    with pytest.raises(ConflictError):
        await auth.org_service.create_invitation(
            admin_token,
            org_id,
            InvitationCreateDTO(email="valid@allowed.fi", role=UserRole.MEMBER),
        )

    raw_token = auth.org_service.get_last_generated_token(inv_dto.id)
    assert raw_token is not None

    wrong_email_token = TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.MEMBER,
        organization_id=None,
        email="impostor@allowed.fi",
    )
    with pytest.raises(PermissionDeniedError) as mismatch_exc:
        await auth.org_service.accept_invitation(
            wrong_email_token,
            InvitationAcceptRequestDTO(raw_token=raw_token),
        )
    assert mismatch_exc.value.error_code == ErrorCodes.IDENTITY_MISMATCH.value

    await auth.org_service.revoke_invitation(admin_token, org_id, inv_dto.id)
    valid_user_token = TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        role=UserRole.MEMBER,
        organization_id=None,
        email="valid@allowed.fi",
    )
    with pytest.raises(AppException) as exp_exc:
        await auth.org_service.accept_invitation(
            valid_user_token,
            InvitationAcceptRequestDTO(raw_token=raw_token),
        )
    assert exp_exc.value.error_code == ErrorCodes.INVITATION_EXPIRED.value
    assert auth.org_service._local_invitations[inv_dto.id].status == InvitationStatus.REVOKED
