"""Tests for Admin Router User Management."""
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from backend.api.admin_router import list_organization_users
from backend.models.auth import TokenData, UserRole


@pytest.mark.asyncio
async def test_list_organization_users_root():
    """Test ROOT user accessing users of ANY organization."""
    auth_service = AsyncMock()
    auth_service.get_users_by_organization.return_value = [] # Return empty list

    root_user = TokenData(uid="root", role=UserRole.ROOT, organization_id="system", email="root@sys")

    # Call
    await list_organization_users(organization_id="target_org", user=root_user, auth_service=auth_service)

    # Verify
    auth_service.get_users_by_organization.assert_called_with("target_org")

@pytest.mark.asyncio
async def test_list_organization_users_admin_own_org():
    """Test ADMIN user accessing users of OWN organization."""
    auth_service = AsyncMock()
    auth_service.get_users_by_organization.return_value = []

    admin_user = TokenData(uid="admin", role=UserRole.ADMIN, organization_id="my_org", email="admin@org")

    # Call
    await list_organization_users(organization_id="my_org", user=admin_user, auth_service=auth_service)

    # Verify
    auth_service.get_users_by_organization.assert_called_with("my_org")

@pytest.mark.asyncio
async def test_list_organization_users_admin_other_org():
    """Test ADMIN user accessing users of OTHER organization (Forbidden)."""
    auth_service = AsyncMock()

    admin_user = TokenData(uid="admin", role=UserRole.ADMIN, organization_id="my_org", email="admin@org")

    # Call & Assert
    with pytest.raises(HTTPException) as exc:
        await list_organization_users(organization_id="other_org", user=admin_user, auth_service=auth_service)

    assert exc.value.status_code == 403
    assert "Access denied" in exc.value.detail

@pytest.mark.asyncio
async def test_list_organization_users_member():
    """Test MEMBER user accessing users (Forbidden)."""
    auth_service = AsyncMock()

    member_user = TokenData(uid="mem", role=UserRole.MEMBER, organization_id="my_org", email="mem@org")

    # Call & Assert - even for own org
    with pytest.raises(HTTPException) as exc:
        await list_organization_users(organization_id="my_org", user=member_user, auth_service=auth_service)

    assert exc.value.status_code == 403
    assert "Insufficient privileges" in exc.value.detail
