"""Unit tests for organization service and B2B invitation flows."""

from __future__ import annotations

import hashlib
import logging
import secrets
import time
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.database.interfaces import (
    get_registered_uow_factory,
    register_default_uow_factory,
)
from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ConflictError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import (
    ExecutionAssignmentCreateDTO,
    Invitation,
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
    UserUpdate,
)
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.step import ExpectedInput, Step, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import (
    EmailDeliveryStatus,
    EntityPrefix,
    ExecutionStatus,
    HistoricalContextMode,
    InvitationStatus,
    StepType,
    SystemLocale,
)
from backend_v2.services.auth import (
    AuthService,
    OrganizationRepository,
    OrganizationService,
    UserRepository,
)
from backend_v2.services.execution import (
    ExecutionAssignmentService,
    ExecutionIngressService,
)
from backend_v2.services.execution.lifecycle_service import ExecutionLifecycleService
from backend_v2.settings import Settings
from backend_v2.tests.factories.model_factories import ExecutionRecordFactory
from backend_v2.tests.fakes.in_memory_repositories import (
    InMemoryExecutionRepository,
    InMemoryUnifiedWorkflowRepository,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork


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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
        organization_id="org_0195f3a0000070008000000000000201",
    )
    await mock_repo.create_organization(
        Organization(
            id="org_0195f3a0000070008000000000000201",
            name="Target Org",
            is_active=True,
            created_at=datetime.now(UTC),
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
    mock_audit = MagicMock(log_event=AsyncMock())
    auth = AuthService(mock_repo, use_firebase=False, audit_service=mock_audit)
    test_org = Organization(
        id="org_0195f3a0000070008000000000000202",
        name="Test Organization",
        is_active=True,
        created_at=datetime.now(UTC),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(test_org)

    root_token = TokenData(id="usr_0195f3a0000070008000000000000102", role=UserRole.ROOT, email="root@test.com")
    manager_with_org = TokenData(
        id="usr_0195f3a0000070008000000000000101",
        role=UserRole.MANAGER,
        email="m@test.com",
        organization_id="org_0195f3a0000070008000000000000202",
    )
    manager_no_org = TokenData(
        id="usr_0195f3a0000070008000000000000104",
        role=UserRole.MANAGER,
        email="orphan@test.com",
        organization_id=None,
    )
    member_with_org = TokenData(
        id="usr_0195f3a0000070008000000000000199",
        role=UserRole.MEMBER,
        email="member@test.com",
        organization_id="org_0195f3a0000070008000000000000202",
    )

    assert len(await auth.list_organizations(root_token)) == 1
    assert len(await auth.list_organizations(manager_with_org)) == 1
    assert len(await auth.list_organizations(manager_no_org)) == 0

    with pytest.raises(PermissionDeniedError):
        await auth.list_organizations(member_with_org)

    with pytest.raises(ResourceNotFoundError):
        await auth.get_organization(root_token, "org_0195f3a0000070008000000000000203")

    foreign_org = test_org.model_copy(update={"id": "org_0195f3a0000070008000000000000204", "name": "Foreign Org"})
    await mock_repo.create_organization(foreign_org)
    with pytest.raises(PermissionDeniedError):
        await auth.get_organization(manager_with_org, "org_0195f3a0000070008000000000000204")

    found_org = await auth.get_organization(manager_with_org, "org_0195f3a0000070008000000000000202")
    assert found_org.id == "org_0195f3a0000070008000000000000202"

    with pytest.raises(PermissionDeniedError):
        await auth.update_organization(
            member_with_org, "org_0195f3a0000070008000000000000202", OrganizationUpdateDTO(name="New")
        )

    updated_by_manager = await auth.update_organization(
        manager_with_org,
        "org_0195f3a0000070008000000000000202",
        OrganizationUpdateDTO(name="Manager Updated Name", contact_email="lead@acme.com"),
    )
    assert updated_by_manager.name == "Manager Updated Name"
    mock_audit.log_event.assert_awaited()

    updated = await auth.update_organization(
        root_token, "org_0195f3a0000070008000000000000202", OrganizationUpdateDTO(name="Updated Name", tpm_limit=60000)
    )
    assert updated.id == "org_0195f3a0000070008000000000000202"

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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
    """TC-P3-05: MANAGER and ADMIN can view their own organization; MEMBER and VIEWER raise PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    test_org = Organization(
        id="org_0195f3a0000070008000000000000208",
        name="My Org",
        is_active=True,
        created_at=datetime.now(UTC),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(test_org)
    manager_initiator = TokenData(
        id="usr_0195f3a0000070008000000000000107",
        role=UserRole.MANAGER,
        organization_id="org_0195f3a0000070008000000000000208",
    )

    org = await auth_service.get_organization(manager_initiator, "org_0195f3a0000070008000000000000208")
    assert org.id == "org_0195f3a0000070008000000000000208"
    assert org.name == "My Org"

    member_initiator = TokenData(
        id="usr_0195f3a0000070008000000000000107",
        role=UserRole.MEMBER,
        organization_id="org_0195f3a0000070008000000000000208",
    )
    with pytest.raises(PermissionDeniedError):
        await auth_service.get_organization(member_initiator, "org_0195f3a0000070008000000000000208")


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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
    """TC-P3-10: MANAGER/ADMIN initiator with no organization_id returns empty list; MEMBER raises PermissionDeniedError."""
    auth_service = AuthService(mock_repo)
    org1 = Organization(
        id="org_0195f3a0000070008000000000000215",
        name="Some Org",
        is_active=True,
        created_at=datetime.now(UTC),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org1)
    manager_no_org = TokenData(id="usr_0195f3a0000070008000000000000110", role=UserRole.MANAGER, organization_id=None)

    orgs = await auth_service.list_organizations(manager_no_org)
    assert orgs == []

    member_no_org = TokenData(id="usr_0195f3a0000070008000000000000110", role=UserRole.MEMBER, organization_id=None)
    with pytest.raises(PermissionDeniedError):
        await auth_service.list_organizations(member_no_org)


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
        created_at=datetime.now(UTC),
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
async def test_update_organization_manager_and_admin_profile_fields_success(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-12: MANAGER and ADMIN can update profile fields (name, contact_email); ADMIN can update allowed_email_domains."""
    mock_audit = MagicMock(log_event=AsyncMock())
    auth_service = AuthService(mock_repo, audit_service=mock_audit)
    org = Organization(
        id="org_0195f3a0000070008000000000000217",
        name="Old Name",
        is_active=True,
        created_at=datetime.now(UTC),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org)
    manager_initiator = TokenData(
        id="usr_0195f3a0000070008000000000000105",
        role=UserRole.MANAGER,
        organization_id="org_0195f3a0000070008000000000000217",
    )
    updated_mgr = await auth_service.update_organization(
        manager_initiator,
        "org_0195f3a0000070008000000000000217",
        OrganizationUpdateDTO(name="Manager Name", contact_email="mgr@org.com"),
    )
    assert updated_mgr.name == "Manager Name"
    assert updated_mgr.contact_email == "mgr@org.com"

    # MANAGER cannot update allowed_email_domains
    with pytest.raises(PermissionDeniedError):
        await auth_service.update_organization(
            manager_initiator,
            "org_0195f3a0000070008000000000000217",
            OrganizationUpdateDTO(allowed_email_domains=["org.com"]),
        )

    admin_initiator = TokenData(
        id="usr_0195f3a0000070008000000000000106",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000217",
    )
    updated_adm = await auth_service.update_organization(
        admin_initiator,
        "org_0195f3a0000070008000000000000217",
        OrganizationUpdateDTO(name="Admin Name", allowed_email_domains=["org.com"]),
    )
    assert updated_adm.name == "Admin Name"
    assert updated_adm.allowed_email_domains == ["org.com"]


@pytest.mark.asyncio
async def test_update_organization_non_root_initiator_raises_permission_denied(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """TC-P3-13: Non-ROOT initiator raises PermissionDeniedError on FinOps fields, foreign org, or MEMBER/VIEWER roles."""
    auth_service = AuthService(mock_repo)
    org = Organization(
        id="org_0195f3a0000070008000000000000206",
        name="Target Org",
        is_active=True,
        created_at=datetime.now(UTC),
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=500.0,
        tpm_limit=50000,
        rpm_limit=500,
        allowed_email_domains=[],
    )
    await mock_repo.create_organization(org)
    admin_initiator = TokenData(
        id="usr_0195f3a0000070008000000000000109",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000206",
    )
    dto = OrganizationUpdateDTO(tpm_limit=999999)

    with pytest.raises(PermissionDeniedError) as exc_info:
        await auth_service.update_organization(admin_initiator, "org_0195f3a0000070008000000000000206", dto)
    assert "Only ROOT can modify platform FinOps limits" in str(exc_info.value)

    foreign_admin = TokenData(
        id="usr_0195f3a0000070008000000000000109",
        role=UserRole.ADMIN,
        organization_id="org_0195f3a0000070008000000000000999",
    )
    with pytest.raises(PermissionDeniedError):
        await auth_service.update_organization(
            foreign_admin, "org_0195f3a0000070008000000000000206", OrganizationUpdateDTO(name="Foreign")
        )


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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
        created_at=datetime.now(UTC),
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
    from pydantic import SecretStr

    cli_secret = SecretStr("test_org_service_cli_secret_2026")
    mock_settings = Settings(
        use_mock_llm=True,
        environment="development",
        use_firebase_auth=False,
        require_mfa=True,
        service_auth_secret=cli_secret,
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
        created_at=datetime.now(UTC),
        language=SystemLocale.EN,
        theme_mode="system",
    )
    org = Organization(
        id=org_id,
        name="JWT Verified Org",
        is_active=True,
        created_at=datetime.now(UTC),
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
        TokenExchangeRequestDTO(target_user_id=root_id, service_auth_secret=cli_secret)
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
        created_at=datetime.now(UTC),
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
            created_at=datetime.now(UTC),
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
                created_at=datetime.now(UTC),
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
            created_at=datetime.now(UTC),
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
            created_at=datetime.now(UTC),
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
    revoked_inv = await auth.org_service._get_invitation_by_id(inv_dto.id)
    assert revoked_inv is not None
    assert revoked_inv.status == InvitationStatus.REVOKED


@pytest.mark.asyncio
async def test_rbac_four_tier_matrix_boundaries_boundary(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Verify 4-Tier RBAC Matrix (VIEWER/MEMBER, MANAGER, ADMIN, ROOT) across users, orgs, invitations, and executions."""
    auth = AuthService(mock_repo, use_firebase=False)
    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    root_id = generate_opaque_id(EntityPrefix.USER)
    admin_id = generate_opaque_id(EntityPrefix.USER)
    manager_id = generate_opaque_id(EntityPrefix.USER)
    member_id = generate_opaque_id(EntityPrefix.USER)
    viewer_id = generate_opaque_id(EntityPrefix.USER)

    await mock_repo.create_organization(
        Organization(
            id=org_id,
            name="Matrix Org",
            is_active=True,
            created_at=datetime.now(UTC),
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=50000,
            rpm_limit=500,
            allowed_email_domains=[],
        )
    )
    for uid, email, role, oid in (
        (root_id, "root@matrix.com", UserRole.ROOT, SystemOrganizations.ROOT_SYSTEM),
        (admin_id, "admin@matrix.com", UserRole.ADMIN, org_id),
        (manager_id, "manager@matrix.com", UserRole.MANAGER, org_id),
        (member_id, "member@matrix.com", UserRole.MEMBER, org_id),
        (viewer_id, "viewer@matrix.com", UserRole.VIEWER, org_id),
    ):
        await mock_repo.create_user(
            User(
                id=uid,
                email=email,
                name=role.value,
                role=role,
                organization_id=oid,
                is_active=True,
                created_at=datetime.now(UTC),
                language=SystemLocale.EN,
                theme_mode="system",
            )
        )

    root_tok = TokenData(id=root_id, role=UserRole.ROOT, organization_id=SystemOrganizations.ROOT_SYSTEM)
    admin_tok = TokenData(id=admin_id, role=UserRole.ADMIN, organization_id=org_id)
    manager_tok = TokenData(id=manager_id, role=UserRole.MANAGER, organization_id=org_id)
    member_tok = TokenData(id=member_id, role=UserRole.MEMBER, organization_id=org_id)
    viewer_tok = TokenData(id=viewer_id, role=UserRole.VIEWER, organization_id=org_id)

    # 1. list_users: VIEWER/MEMBER see only self; MANAGER/ADMIN see org users; ROOT sees all
    assert [u.id for u in await auth.list_users(member_tok)] == [member_id]
    assert [u.id for u in await auth.list_users(viewer_tok)] == [viewer_id]
    assert len(await auth.list_users(manager_tok)) == 4
    assert len(await auth.list_users(admin_tok)) == 4
    assert len(await auth.list_users(root_tok)) == 5

    # 2. update_user: VIEWER/MEMBER/MANAGER can self-update profile, but MANAGER cannot update another user
    updated_self = await auth.update_user(
        member_id, member_id, UserUpdate(name="Member Self", language=SystemLocale.FI, theme_mode="dark")
    )
    assert updated_self.name == "Member Self"
    assert updated_self.language == SystemLocale.FI
    assert updated_self.theme_mode == "dark"

    with pytest.raises(PermissionDeniedError):
        await auth.update_user(manager_id, member_id, UserUpdate(name="Manager Edit Peer"))

    # ADMIN can update org users, but cannot promote to ROOT
    with pytest.raises(PermissionDeniedError):
        await auth.update_user(admin_id, member_id, UserUpdate(role=UserRole.ROOT))

    # 3. update_organization & create_invitation
    with pytest.raises(PermissionDeniedError):
        await auth.update_organization(member_tok, org_id, OrganizationUpdateDTO(name="Denied"))
    with pytest.raises(PermissionDeniedError):
        await auth.update_organization(viewer_tok, org_id, OrganizationUpdateDTO(name="Denied"))

    mgr_org = await auth.update_organization(
        manager_tok, org_id, OrganizationUpdateDTO(name="Mgr Org", contact_email="lead@matrix.com")
    )
    assert mgr_org.name == "Mgr Org"
    assert mgr_org.contact_email == "lead@matrix.com"

    with pytest.raises(PermissionDeniedError):
        await auth.update_organization(manager_tok, org_id, OrganizationUpdateDTO(quota_limit=9999.0))
    with pytest.raises(PermissionDeniedError):
        await auth.update_organization(admin_tok, org_id, OrganizationUpdateDTO(quota_limit=9999.0))

    with pytest.raises(PermissionDeniedError):
        await auth.org_service.create_invitation(
            manager_tok, org_id, InvitationCreateDTO(email="invitee@matrix.com", role=UserRole.MEMBER)
        )
    inv = await auth.org_service.create_invitation(
        admin_tok, org_id, InvitationCreateDTO(email="invitee@matrix.com", role=UserRole.MEMBER)
    )
    assert inv.status == InvitationStatus.PENDING

    # 4. list_executions: MEMBER/VIEWER see only own executions; MANAGER/ADMIN see all org executions
    exec_repo = InMemoryExecutionRepository()
    exe_member_id = generate_opaque_id(EntityPrefix.EXECUTION)
    exe_peer_id = generate_opaque_id(EntityPrefix.EXECUTION)
    await exec_repo.save_execution(
        ExecutionRecordFactory.build(
            id=exe_member_id,
            organization_id=org_id,
            created_by=member_id,
            status=ExecutionStatus.PENDING,
        )
    )
    await exec_repo.save_execution(
        ExecutionRecordFactory.build(
            id=exe_peer_id,
            organization_id=org_id,
            created_by=viewer_id,
            status=ExecutionStatus.PENDING,
        )
    )
    lifecycle = ExecutionLifecycleService(exec_repo=exec_repo)
    assert [e.id for e in await lifecycle.list_executions(member_tok)] == [exe_member_id]
    assert [e.id for e in await lifecycle.list_executions(viewer_tok)] == [exe_peer_id]
    assert {e.id for e in await lifecycle.list_executions(manager_tok)} == {exe_member_id, exe_peer_id}
    assert {e.id for e in await lifecycle.list_executions(admin_tok)} == {exe_member_id, exe_peer_id}


@pytest.mark.asyncio
async def test_organization_and_assignment_services_persist_roundtrip_via_uow(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Positive: Verify OrganizationService and ExecutionAssignmentService persist and retrieve via InMemoryUnitOfWork with zero _local_* attributes."""
    uow = InMemoryUnitOfWork()
    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    admin_id = generate_opaque_id(EntityPrefix.USER)
    wf_id = generate_opaque_id(EntityPrefix.WORKFLOW)
    prf_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    stp_id = generate_opaque_id(EntityPrefix.STEP)

    await mock_repo.create_organization(
        Organization(
            id=org_id,
            name="UoW Roundtrip Org",
            is_active=True,
            created_at=datetime.now(UTC),
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
            id=admin_id,
            email="admin@uow-roundtrip.fi",
            name="Admin",
            role=UserRole.ADMIN,
            organization_id=org_id,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    await mock_repo.save_step(
        Step(
            organization_id="org_0195f3a0000070008000000000000001",
            id=stp_id,
            slug="uow-step",
            name=I18nText(translations={"en": "Step", "fi": "Vaihe"}),
            type=StepType.LOGIC,
            hook="my_hook",
            mcp_tool_params={},
            criteria_block_ids=[],
            pre_hooks=[],
            post_hooks=[],
            allowed_mcp_tools=[],
            expected_inputs=[],
        )
    )
    await mock_repo.save_workflow(
        Workflow(
            organization_id="org_0195f3a0000070008000000000000001",
            id=wf_id,
            slug="uow-wf",
            name="UoW Workflow",
            description="Workflow for UoW assignment roundtrip",
            status="active",
            version=1,
            default_strictness_level=50,
            model_registry_id="mrg_0195f3a00000700e826807f3bfa3454d",
            historical_context_mode=HistoricalContextMode.DISABLED,
            expected_inputs=[
                ExpectedInput(
                    input_key="manager_context",
                    label=I18nText(translations={"en": "Context", "fi": "Konteksti"}),
                    required=True,
                    is_chat_history=False,
                    input_modes=["paste"],
                    description=I18nText(translations={"en": "Context", "fi": "Konteksti"}),
                    questionnaire_definition=[],
                ),
                ExpectedInput(
                    input_key="candidate_answer",
                    label=I18nText(translations={"en": "Answer", "fi": "Vastaus"}),
                    required=True,
                    is_chat_history=False,
                    input_modes=["paste"],
                    description=I18nText(translations={"en": "Answer", "fi": "Vastaus"}),
                    questionnaire_definition=[],
                ),
            ],
            steps=[
                StepRule(
                    id=stp_id,
                    task_blueprint=stp_id,
                    depends_on=[],
                    input_mappings={},
                )
            ],
            default_profile_id=prf_id,
        )
    )
    await mock_repo.save_output_profile(
        OutputProfile(
            organization_id="org_0195f3a0000070008000000000000001",
            id=prf_id,
            slug="uow-prf",
            name=I18nText(translations={"en": "Profile", "fi": "Profiili"}),
            workflow_id=wf_id,
            target_block_order=[],
            visible_block_extensions=[],
            visible_workflow_extensions=[],
            visible_metadata=[],
            matrix_visible_columns=[],
            matrix_synthesis_groups=[],
            content_blocks=[],
        )
    )

    org_repo = OrganizationRepository(mock_repo)
    user_repo = UserRepository(mock_repo)
    org_service = OrganizationService(
        org_repo=org_repo,
        user_repo=user_repo,
        entity_adapter=None,
        uow_factory=lambda: uow,
    )
    ingress_service = ExecutionIngressService(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        system_repo=mock_repo,
    )
    assignment_service = ExecutionAssignmentService(
        ingress_service=ingress_service,
        org_repo=org_repo,
        user_repo=user_repo,
        workflow_repo=mock_repo,
        entity_adapter=None,
        uow_factory=lambda: uow,
    )

    assert not any(attr.startswith("_local_") for attr in dir(org_service))
    assert not any(attr.startswith("_local_") for attr in dir(assignment_service))

    admin_tok = TokenData(id=admin_id, role=UserRole.ADMIN, organization_id=org_id, email="admin@uow-roundtrip.fi")
    inv_dto = await org_service.create_invitation(
        admin_tok,
        org_id,
        InvitationCreateDTO(email="invitee@uow-roundtrip.fi", role=UserRole.MEMBER),
    )
    inv_raw_token = org_service.get_last_generated_token(inv_dto.id)
    assert inv_raw_token is not None

    persisted_inv = await uow.entities.get_invitation(inv_dto.id)
    assert persisted_inv is not None
    assert persisted_inv.email == "invitee@uow-roundtrip.fi"

    listed_invs = await org_service.list_invitations(admin_tok, org_id)
    assert [item.id for item in listed_invs] == [inv_dto.id]

    fetched_inv = await org_service._get_invitation_by_id(inv_dto.id)
    assert fetched_inv is not None
    assert fetched_inv.id == inv_dto.id

    asg_dto = await assignment_service.create_assignment(
        initiator=admin_tok,
        payload=ExecutionAssignmentCreateDTO(
            assigned_email="assignee@uow-roundtrip.fi",
            workflow_id=wf_id,
            output_profile_id=prf_id,
            locked_inputs=WorkflowInputs(dynamic_inputs={"manager_context": "Context"}),
            assignee_input_keys=["candidate_answer"],
            hard_deadline_at=datetime.now(UTC) + timedelta(hours=4),
        ),
    )
    asg_raw_token = assignment_service.get_last_generated_token(asg_dto.id)
    assert asg_raw_token is not None

    persisted_asg = await uow.entities.get_execution_assignment(asg_dto.id)
    assert persisted_asg is not None
    assert persisted_asg.id == asg_dto.id

    preview_asg = await assignment_service.preview_assignment(asg_raw_token)
    assert preview_asg.id == asg_dto.id

    fetched_asg = await assignment_service._get_assignment_or_raise(asg_dto.id)
    assert fetched_asg.id == asg_dto.id

    listed_asgs = await assignment_service.list_assignments(admin_tok)
    assert [item.id for item in listed_asgs] == [asg_dto.id]


@pytest.mark.asyncio
async def test_organization_and_assignment_services_fail_fast_when_uow_unconfigured(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Negative: Verify OrganizationService and ExecutionAssignmentService log CONFIGURATION_ERROR and raise ConfigurationError when persistence is unconfigured."""
    org_repo = OrganizationRepository(mock_repo)
    user_repo = UserRepository(mock_repo)
    org_service = OrganizationService(
        org_repo=org_repo,
        user_repo=user_repo,
        entity_adapter=None,
        uow_factory=None,
    )
    ingress_service = ExecutionIngressService(
        exec_repo=mock_repo,
        workflow_repo=mock_repo,
        prompt_block_repo=mock_repo,
        output_profile_repo=mock_repo,
        system_repo=mock_repo,
    )
    assignment_service = ExecutionAssignmentService(
        ingress_service=ingress_service,
        org_repo=org_repo,
        user_repo=user_repo,
        workflow_repo=mock_repo,
        entity_adapter=None,
        uow_factory=None,
    )

    previous_factory = get_registered_uow_factory()
    register_default_uow_factory(None)
    try:
        with (
            caplog.at_level(logging.ERROR),
            pytest.raises(ConfigurationError) as org_exc,
        ):
            await org_service._get_invitation_by_id("inv_0195f3a0000070008000000000000001")
        assert org_exc.value.error_code == ErrorCodes.CONFIGURATION_ERROR.value
        assert any(ErrorCodes.CONFIGURATION_ERROR.name in rec.getMessage() for rec in caplog.records)

        with pytest.raises(ConfigurationError):
            await org_service._list_org_invitations("org_0195f3a0000070008000000000000001")

        with pytest.raises(ConfigurationError):
            await org_service._find_invitation_by_token_hash("a" * 64)

        caplog.clear()
        with (
            caplog.at_level(logging.ERROR),
            pytest.raises(ConfigurationError) as asg_exc,
        ):
            await assignment_service._get_assignment_or_raise("tsk_0195f3a0000070008000000000000001")
        assert asg_exc.value.error_code == ErrorCodes.CONFIGURATION_ERROR.value
        assert any(ErrorCodes.CONFIGURATION_ERROR.name in rec.getMessage() for rec in caplog.records)

        with pytest.raises(ConfigurationError):
            await assignment_service._list_all_assignments()
    finally:
        register_default_uow_factory(previous_factory)


@pytest.mark.asyncio
async def test_delete_organization_non_existent_org_raises_resource_not_found_negative(
    mock_repo: InMemoryUnifiedWorkflowRepository,
) -> None:
    """Negative: Deleting a non-existent organization as ROOT raises ResourceNotFoundError without audit side-effects."""
    mock_audit = AsyncMock()
    auth_service = AuthService(mock_repo, audit_service=mock_audit)
    root_initiator = TokenData(id=generate_opaque_id(EntityPrefix.USER), role=UserRole.ROOT)
    missing_org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)

    with pytest.raises(ResourceNotFoundError) as exc_info:
        await auth_service.delete_organization(root_initiator, missing_org_id)

    assert exc_info.value.status_code == 404
    assert exc_info.value.error_code == ErrorCodes.RESOURCE_NOT_FOUND.value
    mock_audit.log_event.assert_not_called()


@pytest.mark.asyncio
async def test_invitation_accept_missing_payload_expired_and_timeout_negative(
    mock_repo: InMemoryUnifiedWorkflowRepository,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Negative & Boundary: Verify missing accept payload, expired pending auto-transition, persisted email mismatch, and Firebase delete timeout."""
    uow = InMemoryUnitOfWork()
    auth = AuthService(mock_repo, use_firebase=False, entity_adapter=uow.entities)

    org_id = generate_opaque_id(EntityPrefix.ORGANIZATION)
    root_id = generate_opaque_id(EntityPrefix.USER)
    await mock_repo.create_organization(
        Organization(
            id=org_id,
            name="Boundary Invitation Org",
            is_active=True,
            created_at=datetime.now(UTC),
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=500.0,
            tpm_limit=50000,
            rpm_limit=500,
            allowed_email_domains=[],
        )
    )
    root_token = TokenData(id=root_id, role=UserRole.ROOT, organization_id=SystemOrganizations.ROOT_SYSTEM)

    # 1. Unknown invitation_id returns None; ROOT can manage tenant invitations
    assert auth.org_service.get_last_generated_token(generate_opaque_id(EntityPrefix.INVITATION)) is None
    root_created_inv = await auth.org_service.create_invitation(
        root_token,
        org_id,
        InvitationCreateDTO(email="target@boundary.org", role=UserRole.MEMBER),
    )
    assert root_created_inv.organization_id == org_id

    # 2. Missing payload when first argument is TokenData raises VALIDATION_FAILED
    with pytest.raises(AppException) as missing_payload_exc:
        await auth.org_service.accept_invitation(root_token, None)
    assert missing_payload_exc.value.status_code == 400
    assert missing_payload_exc.value.error_code == ErrorCodes.VALIDATION_FAILED.value

    # 3. TokenData with email=None resolves persisted User by ID and rejects mismatched email
    mismatched_user_id = generate_opaque_id(EntityPrefix.USER)
    await mock_repo.create_user(
        User(
            id=mismatched_user_id,
            email="different@boundary.org",
            name="Different User",
            role=UserRole.MEMBER,
            organization_id=None,
            is_active=True,
            created_at=datetime.now(UTC),
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    raw_valid_token = auth.org_service.get_last_generated_token(root_created_inv.id)
    assert raw_valid_token is not None
    token_without_email = TokenData(id=mismatched_user_id, role=UserRole.MEMBER, organization_id=None, email=None)
    with pytest.raises(PermissionDeniedError) as mismatch_by_id_exc:
        await auth.org_service.accept_invitation(
            token_without_email,
            InvitationAcceptRequestDTO(raw_token=raw_valid_token),
        )
    assert mismatch_by_id_exc.value.error_code == ErrorCodes.IDENTITY_MISMATCH.value

    # 4. Expired PENDING invitation (expires_at <= now) auto-transitions to EXPIRED and raises INVITATION_EXPIRED
    expired_raw_token = secrets.token_urlsafe(32)
    expired_inv_id = generate_opaque_id(EntityPrefix.INVITATION)
    now = datetime.now(UTC)
    expired_inv = Invitation(
        id=expired_inv_id,
        organization_id=org_id,
        email="expired@boundary.org",
        role=UserRole.MEMBER,
        token_hash=hashlib.sha256(expired_raw_token.encode("utf-8")).hexdigest(),
        status=InvitationStatus.PENDING,
        email_delivery_status=EmailDeliveryStatus.SENT,
        invited_by=root_id,
        expires_at=now - timedelta(seconds=1),
        created_at=now - timedelta(hours=2),
    )
    await uow.entities.upsert_invitation(expired_inv)
    with pytest.raises(AppException) as expired_exc:
        await auth.org_service.accept_invitation(InvitationAcceptRequestDTO(raw_token=expired_raw_token))
    assert expired_exc.value.status_code == 410
    assert expired_exc.value.error_code == ErrorCodes.INVITATION_EXPIRED.value
    persisted_expired = await uow.entities.get_invitation(expired_inv_id)
    assert persisted_expired is not None
    assert persisted_expired.status == InvitationStatus.EXPIRED

    # 5. Firebase cascade delete exceeding http_client_timeout_seconds raises INTERNAL_SERVER_ERROR
    slow_fb = MagicMock()

    def _slow_delete(_uid: str) -> None:
        time.sleep(0.2)

    slow_fb.delete_user.side_effect = _slow_delete
    fast_timeout_settings = MagicMock(http_client_timeout_seconds=0.01)
    monkeypatch.setattr("backend_v2.services.auth.organization_service.get_settings", lambda: fast_timeout_settings)
    fb_org_service = OrganizationService(
        org_repo=OrganizationRepository(mock_repo),
        user_repo=UserRepository(mock_repo),
        use_firebase=True,
        firebase_auth=slow_fb,
        entity_adapter=uow.entities,
    )
    await mock_repo.create_user(
        User(
            id=generate_opaque_id(EntityPrefix.USER),
            email="cascade@boundary.org",
            name="Cascade Member",
            role=UserRole.MEMBER,
            organization_id=org_id,
            is_active=True,
            created_at=now,
            language=SystemLocale.EN,
            theme_mode="system",
        )
    )
    with pytest.raises(AppException) as timeout_exc:
        await fb_org_service.delete_organization(root_token, org_id, force=True)
    assert timeout_exc.value.status_code == 500
    assert timeout_exc.value.error_code == ErrorCodes.INTERNAL_SERVER_ERROR.value
