"""Unit tests for canonical Organizations IAM API Router (backend_v2/api/routers/iam/organizations.py)."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from pydantic import SecretStr

from backend_v2.api.routers.iam.organizations import (
    create_organization,
    create_organization_invitation,
    create_organization_invitation_batch,
    delete_organization,
    delete_organization_secret,
    get_all_organizations,
    get_organization,
    list_organization_invitations,
    list_organization_secrets,
    revoke_organization_invitation,
    save_organization,
    upsert_organization_secret,
)
from backend_v2.exceptions import (
    ConflictError,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import (
    SYSTEM_ROOT_USER_ID,
    InvitationBatchCreateDTO,
    InvitationCreateDTO,
    Organization,
    OrganizationCreate,
    OrganizationUpdateDTO,
    SubscriptionStatus,
    SystemOrganizations,
    TenantSecretCreateDTO,
    TokenData,
    User,
    UserRole,
)
from backend_v2.models.enums import InvitationStatus, LLMProvider, SecretScope, SystemLocale
from backend_v2.services.auth import AuthService
from backend_v2.services.auth.secret_service import SecretService
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork

ORG_ID = "org_0195f3a0000070008000000000000010"


@pytest.fixture
def mock_current_user() -> TokenData:
    """Provide an authenticated ROOT TokenData fixture."""
    return TokenData(id=SYSTEM_ROOT_USER_ID, role=UserRole.ROOT)


@pytest.fixture
def mock_auth_service() -> AsyncMock:
    """Provide an AsyncMock AuthService fixture."""
    return AsyncMock()


@pytest.fixture
def sample_org() -> Organization:
    """Provide a canonical Organization model fixture."""
    return Organization(
        id=ORG_ID,
        name="Tenant Org",
        is_active=True,
        tier="standard",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=100.0,
        tpm_limit=50000,
        rpm_limit=100,
        created_at=datetime.now(timezone.utc),
        allowed_email_domains=[],
    )


@pytest.mark.asyncio
async def test_organizations_router_crud_positive(
    mock_current_user: TokenData,
    mock_auth_service: AsyncMock,
    sample_org: Organization,
) -> None:
    """Positive: Verify get_all_organizations, get_organization, save_organization, and delete_organization."""
    mock_auth_service.list_organizations.return_value = [sample_org]
    orgs = await get_all_organizations(current_user=mock_current_user, auth_service=mock_auth_service)
    assert orgs == [sample_org]

    mock_auth_service.get_organization.return_value = sample_org
    fetched = await get_organization(id=ORG_ID, current_user=mock_current_user, auth_service=mock_auth_service)
    assert fetched == sample_org

    org_create = OrganizationCreate(
        name="Tenant Org",
        admin_email="admin@tenant.com",
        admin_password="secretpassword123",
        admin_name="Admin User",
        tpm_limit=50000,
        rpm_limit=100,
    )
    mock_auth_service.create_organization.return_value = sample_org
    created = await create_organization(
        data=org_create,
        current_user=mock_current_user,
        auth_service=mock_auth_service,
    )
    assert created == sample_org

    org_update = OrganizationUpdateDTO(name="Tenant Org")
    mock_auth_service.update_organization.return_value = sample_org
    saved = await save_organization(
        id=ORG_ID,
        data=org_update,
        current_user=mock_current_user,
        auth_service=mock_auth_service,
    )
    assert saved == sample_org

    mock_auth_service.delete_organization.return_value = None
    deleted = await delete_organization(id=ORG_ID, current_user=mock_current_user, auth_service=mock_auth_service)
    assert deleted.status == "success"
    assert deleted.deleted_id == ORG_ID


@pytest.mark.asyncio
async def test_organizations_router_propagates_permission_denied_and_not_found_negative(
    mock_current_user: TokenData,
    mock_auth_service: AsyncMock,
) -> None:
    """Negative: Verify get_all_organizations and get_organization propagate PermissionDeniedError and ResourceNotFoundError."""
    mock_auth_service.list_organizations.side_effect = PermissionDeniedError("Forbidden")
    with pytest.raises(PermissionDeniedError):
        await get_all_organizations(current_user=mock_current_user, auth_service=mock_auth_service)

    mock_auth_service.get_organization.side_effect = ResourceNotFoundError("Organization", ORG_ID)
    with pytest.raises(ResourceNotFoundError):
        await get_organization(id=ORG_ID, current_user=mock_current_user, auth_service=mock_auth_service)


@pytest.mark.asyncio
async def test_organizations_router_delete_error_branches_negative(
    mock_current_user: TokenData,
    mock_auth_service: AsyncMock,
) -> None:
    """Negative: Verify delete_organization propagates PermissionDeniedError and ResourceNotFoundError directly."""
    mock_auth_service.delete_organization.side_effect = PermissionDeniedError("Cannot delete system org")
    with pytest.raises(PermissionDeniedError):
        await delete_organization(id=ORG_ID, current_user=mock_current_user, auth_service=mock_auth_service)

    mock_auth_service.delete_organization.side_effect = ResourceNotFoundError("Organization", ORG_ID)
    with pytest.raises(ResourceNotFoundError):
        await delete_organization(id=ORG_ID, current_user=mock_current_user, auth_service=mock_auth_service)


@pytest.mark.asyncio
async def test_organizations_router_byok_secrets_endpoints_positive_and_negative(
    mock_current_user: TokenData,
) -> None:
    """Positive & Negative: Verify list_organization_secrets, upsert_organization_secret, and delete_organization_secret."""
    uow = InMemoryUnitOfWork()
    secret_service = SecretService(entity_adapter=uow.entities)

    created = await upsert_organization_secret(
        org_id=ORG_ID,
        payload=TenantSecretCreateDTO(
            scope=SecretScope.LLM_PROVIDER,
            target_identifier=LLMProvider.OPENAI.value,
            plaintext_secret=SecretStr("sk-org-router-unit-9876"),
        ),
        current_user=mock_current_user,
        secret_service=secret_service,
    )
    assert created.organization_id == ORG_ID
    assert created.masked_hint == "****9876"

    secrets_list = await list_organization_secrets(
        org_id=ORG_ID,
        current_user=mock_current_user,
        secret_service=secret_service,
    )
    assert len(secrets_list) == 1
    assert secrets_list[0].id == created.id

    deleted = await delete_organization_secret(
        org_id=ORG_ID,
        secret_id=created.id,
        current_user=mock_current_user,
        secret_service=secret_service,
    )
    assert deleted.status == "success"
    assert deleted.deleted_id == created.id

    with pytest.raises(ResourceNotFoundError):
        await delete_organization_secret(
            org_id=ORG_ID,
            secret_id=created.id,
            current_user=mock_current_user,
            secret_service=secret_service,
        )


@pytest.mark.asyncio
async def test_organizations_router_invitations_endpoints_positive_and_negative(
    mock_current_user: TokenData,
) -> None:
    """Positive & Negative: Verify invitation endpoints via real AuthService and InMemoryUnitOfWork."""
    uow = InMemoryUnitOfWork()
    repo = InMemoryUnifiedWorkflowRepository()
    await repo.create_user(
        User(
            id=mock_current_user.id,
            email="root@quorum.org",
            role=UserRole.ROOT,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            language=SystemLocale.EN,
            theme_mode="system",
            organization_id=SystemOrganizations.ROOT_SYSTEM,
        )
    )
    auth_service = AuthService(repo=repo, entity_adapter=uow.entities)

    created_org = await create_organization(
        data=OrganizationCreate(
            name="B2B Invite Org",
            admin_email="owner@b2b.org",
            admin_password="Password123!@#",
            admin_name="Org Owner",
            tpm_limit=50000,
            rpm_limit=100,
        ),
        current_user=mock_current_user,
        auth_service=auth_service,
    )

    single_inv = await create_organization_invitation(
        org_id=created_org.id,
        payload=InvitationCreateDTO(email="alice@b2b.org", role=UserRole.MEMBER),
        current_user=mock_current_user,
        auth_service=auth_service,
    )
    assert single_inv.email == "alice@b2b.org"
    assert single_inv.status == InvitationStatus.PENDING

    with pytest.raises(ConflictError):
        await create_organization_invitation(
            org_id=created_org.id,
            payload=InvitationCreateDTO(email="alice@b2b.org", role=UserRole.MEMBER),
            current_user=mock_current_user,
            auth_service=auth_service,
        )

    batch_resp = await create_organization_invitation_batch(
        org_id=created_org.id,
        payload=InvitationBatchCreateDTO(
            recipients=[
                InvitationCreateDTO(email="bob@b2b.org", role=UserRole.MEMBER),
                InvitationCreateDTO(email="carol@b2b.org", role=UserRole.ADMIN),
            ]
        ),
        current_user=mock_current_user,
        auth_service=auth_service,
    )
    assert batch_resp.created_count == 2

    all_invs = await list_organization_invitations(
        org_id=created_org.id,
        current_user=mock_current_user,
        auth_service=auth_service,
    )
    assert len(all_invs) == 3

    revoked = await revoke_organization_invitation(
        org_id=created_org.id,
        invitation_id=single_inv.id,
        current_user=mock_current_user,
        auth_service=auth_service,
    )
    assert revoked.status == InvitationStatus.REVOKED

    non_admin_user = TokenData(
        id="usr_0195f3a0000070008000000000000099",
        role=UserRole.MEMBER,
        organization_id=created_org.id,
    )
    with pytest.raises(PermissionDeniedError):
        await list_organization_invitations(
            org_id=created_org.id,
            current_user=non_admin_user,
            auth_service=auth_service,
        )

