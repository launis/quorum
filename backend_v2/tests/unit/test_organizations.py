"""Unit tests for canonical Organizations IAM API Router (backend_v2/api/routers/iam/organizations.py)."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from backend_v2.api.routers.iam.organizations import (
    delete_organization,
    get_all_organizations,
    get_organization,
    save_organization,
)
from backend_v2.exceptions import (
    AppException,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import (
    SYSTEM_ROOT_USER_ID,
    Organization,
    OrganizationCreate,
    SubscriptionStatus,
    TokenData,
    UserRole,
)

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
    mock_auth_service.update_organization.return_value = sample_org
    saved = await save_organization(
        id=ORG_ID,
        data=org_create,
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
    """Negative: Verify delete_organization propagates AppException and wraps unexpected errors in 500 AppException."""
    mock_auth_service.delete_organization.side_effect = PermissionDeniedError("Cannot delete system org")
    with pytest.raises(PermissionDeniedError):
        await delete_organization(id=ORG_ID, current_user=mock_current_user, auth_service=mock_auth_service)

    mock_auth_service.delete_organization.side_effect = RuntimeError("Database connection lost")
    with pytest.raises(AppException) as exc:
        await delete_organization(id=ORG_ID, current_user=mock_current_user, auth_service=mock_auth_service)
    assert exc.value.status_code == 500
