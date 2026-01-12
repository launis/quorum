import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, Mock

from backend.api.admin_router import update_user_role, UpdateRoleRequest
from backend.models.auth import UserRole, TokenData, UserAdminView

@pytest.mark.asyncio
async def test_update_role_success():
    """Test successful role update."""
    auth_service = AsyncMock()
    # Mock return value
    expected_user = UserAdminView(
        uid="target", email="t@t.com", role=UserRole.ADMIN, 
        organization_id="org1", created_at="2024-01-01T00:00:00",
        last_login_at=None, execution_count=0
    )
    auth_service.update_user_role.return_value = expected_user
    
    root_user = TokenData(uid="root", role=UserRole.ROOT, organization_id="system", email="root@sys")
    req = UpdateRoleRequest(role=UserRole.ADMIN)
    
    # Call
    result = await update_user_role(user_id="target", request=req, user=root_user, auth_service=auth_service)
    
    # Verify
    auth_service.update_user_role.assert_called_with(
        initiator_uid="root", target_uid="target", new_role=UserRole.ADMIN
    )
    assert result == expected_user

@pytest.mark.asyncio
async def test_update_role_permission_error():
    """Test permission denial (mapped to 403)."""
    auth_service = AsyncMock()
    auth_service.update_user_role.side_effect = PermissionError("Hierarchy violation")
    
    user = TokenData(uid="mem", role=UserRole.MEMBER, organization_id="org1", email="m@m")
    req = UpdateRoleRequest(role=UserRole.ADMIN)
    
    with pytest.raises(HTTPException) as exc:
        await update_user_role(user_id="target", request=req, user=user, auth_service=auth_service)
    
    assert exc.value.status_code == 403
    assert "Hierarchy violation" in exc.value.detail

@pytest.mark.asyncio
async def test_update_role_not_found():
    """Test user not found (mapped to 404)."""
    auth_service = AsyncMock()
    auth_service.update_user_role.side_effect = ValueError("User not found")
    
    user = TokenData(uid="root", role=UserRole.ROOT, organization_id="sys", email="r@s")
    req = UpdateRoleRequest(role=UserRole.ADMIN)
    
    with pytest.raises(HTTPException) as exc:
        await update_user_role(user_id="unknown", request=req, user=user, auth_service=auth_service)
        
    assert exc.value.status_code == 404

@pytest.mark.asyncio
async def test_update_role_last_admin_conflict():
    """Test Last Admin Protection (mapped to 409)."""
    auth_service = AsyncMock()
    # Simulate the special RuntimeError raised by logic
    auth_service.update_user_role.side_effect = RuntimeError("LAST_ADMIN_PROTECTION: Cannot demote...")
    
    user = TokenData(uid="admin", role=UserRole.ADMIN, organization_id="org1", email="a@a")
    req = UpdateRoleRequest(role=UserRole.MEMBER)
    
    with pytest.raises(HTTPException) as exc:
        await update_user_role(user_id="self", request=req, user=user, auth_service=auth_service)
        
    assert exc.value.status_code == 409
    assert exc.value.detail["error_code"] == "LAST_ADMIN_PROTECTION"
    assert "Cannot demote" in exc.value.detail["message"]
