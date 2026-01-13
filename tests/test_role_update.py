"""Tests for User Role Update logic."""

import pytest
from unittest.mock import AsyncMock
from backend.api.auth_router import update_user
from backend.models.auth import TokenData, UserAdminView, UserRole, UserUpdate, User
from backend.exceptions import ConflictError, PermissionDeniedError, ResourceNotFoundError

@pytest.mark.asyncio
async def test_update_role_success():
    """Test successful role update."""
    auth_service = AsyncMock()
    # Mock return value
    expected_user = User(
        uid="target",
        email="t@t.com",
        role=UserRole.ADMIN,
        organization_id="org1",
        created_at="2024-01-01T00:00:00",
        last_login_at=None,
        execution_count=0,
    )
    auth_service.update_user.return_value = expected_user

    root_user = TokenData(uid="root", role=UserRole.ROOT, organization_id="system", email="root@sys")
    req = UserUpdate(role=UserRole.ADMIN)

    # Call
    result = await update_user(uid="target", user_update=req, current_user=root_user, auth_service=auth_service)

    # Verify
    auth_service.update_user.assert_called_with("root", "target", req)
    assert result == expected_user


@pytest.mark.asyncio
async def test_update_role_permission_error():
    """Test permission denial (mapped to 403)."""
    auth_service = AsyncMock()
    auth_service.update_user.side_effect = PermissionDeniedError("Hierarchy violation")

    user = TokenData(uid="mem", role=UserRole.MEMBER, organization_id="org1", email="m@m")
    req = UserUpdate(role=UserRole.ADMIN)

    with pytest.raises(PermissionDeniedError) as exc:
        await update_user(uid="target", user_update=req, current_user=user, auth_service=auth_service)

    assert exc.value.status_code == 403
    assert "Hierarchy violation" in exc.value.message


@pytest.mark.asyncio
async def test_update_role_not_found():
    """Test user not found (mapped to 404)."""
    auth_service = AsyncMock()
    auth_service.update_user.side_effect = ResourceNotFoundError("User", "unknown")

    user = TokenData(uid="root", role=UserRole.ROOT, organization_id="sys", email="r@s")
    req = UserUpdate(role=UserRole.ADMIN)

    with pytest.raises(ResourceNotFoundError) as exc:
        await update_user(uid="unknown", user_update=req, current_user=user, auth_service=auth_service)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_role_last_admin_conflict():
    """Test Last Admin Protection (mapped to 409)."""
    auth_service = AsyncMock()
    # ConflictError takes (message, details)
    # Raising with specific message
    auth_service.update_user.side_effect = ConflictError("LAST_ADMIN_PROTECTION: Cannot demote", details={"reason": "last_admin"})

    user = TokenData(uid="admin", role=UserRole.ADMIN, organization_id="org1", email="a@a")
    req = UserUpdate(role=UserRole.MEMBER)

    with pytest.raises(ConflictError) as exc:
        await update_user(uid="self", user_update=req, current_user=user, auth_service=auth_service)

    assert exc.value.status_code == 409
    assert "LAST_ADMIN_PROTECTION" in exc.value.message
