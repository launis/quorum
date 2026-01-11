"""Organization Management Tests."""

from datetime import datetime

import pytest

from backend.models.auth import User, UserRole

# Mock user payloads
ROOT_USER = User(
    uid="root_master",
    role=UserRole.ROOT,
    organization_id="system",
    email="root@test.com",
    display_name="Root",
    created_at=datetime.utcnow().isoformat(),
)

ADMIN_USER = User(
    uid="test_admin",
    role=UserRole.ADMIN,
    organization_id="test_org",
    email="admin@test.com",
    display_name="Admin",
    created_at=datetime.utcnow().isoformat(),
)


@pytest.mark.asyncio
async def test_create_org_as_root(client_authenticated, mock_auth_service):
    """Test that ROOT can create an organization."""
    # Setup Root User
    mock_auth_service.current_user = ROOT_USER

    org_data = {"id": "new_corp_root", "name": "New Corp", "tier": "standard", "contact_email": "admin@newcorp.com"}
    response = await client_authenticated.post("/organizations/", json=org_data)
    assert response.status_code == 201
    assert response.json()["id"] == "new_corp_root"

    # Cleanup
    await client_authenticated.delete("/organizations/new_corp_root?force=true")


@pytest.mark.asyncio
async def test_create_org_as_admin_forbidden(client_authenticated, mock_auth_service):
    """Test that ADMIN cannot create an organization."""
    mock_auth_service.current_user = ADMIN_USER

    org_data = {"id": "fail_corp_admin", "name": "Fail Corp"}
    response = await client_authenticated.post("/organizations/", json=org_data)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_org_as_admin_forbidden(client_authenticated, mock_auth_service):
    """Test that ADMIN cannot delete an organization."""
    mock_auth_service.current_user = ADMIN_USER

    # Needs a real ID to pass generic 404 text if repo mocks don't exist,
    # but 403 authorization check happens BEFORE 404 lookup usually.
    response = await client_authenticated.delete("/organizations/some_org?force=true")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_orgs_as_admin_forbidden(client_authenticated, mock_auth_service):
    """Test that ADMIN cannot list organizations."""
    mock_auth_service.current_user = ADMIN_USER

    response = await client_authenticated.get("/organizations/")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_system_org_forbidden(client_authenticated, mock_auth_service):
    """Test that deleting the 'system' organization is forbidden."""
    mock_auth_service.current_user = ROOT_USER

    response = await client_authenticated.delete("/organizations/system?force=true")
    assert response.status_code == 403
    assert response.status_code == 403
    # Check for error message in text since structure might vary (detail vs message)
    # Check for error message in text since structure might vary (detail vs message)
    assert "Cannot delete System Organization" in response.text


@pytest.mark.asyncio
async def test_delete_org_with_users_conflict(client_authenticated, mock_auth_service):
    """Test that deleting a populated org without force=true fails."""
    mock_auth_service.current_user = ROOT_USER

    # 1. Create Org
    org_id = "populated_org"
    await client_authenticated.post("/organizations/", json={"id": org_id, "name": "Populated"})

    # 2. Add a User to it (Mocking DB state directly or via API if available)
    # Using API to create user if possible, or mocking repo.
    # Let's assume we can create a user.
    user_data = {"uid": "user1", "email": "user@pop.com", "role": "MEMBER", "organization_id": org_id}
    # Create user directly in repo/db for speed if no public API, but let's try API if we have access.
    # Actually, let's just use the fact that the endpoint calls AuthService.delete_organization
    # We should probably mock the repository response for 'count_users' if we want unit test isolation,
    # but for integration text, we need real state.

    # Prerequisite: We need a way to insert a user.
    # If standard API allows creating users: POST /api/v1/users
    # If standard API allows creating users: POST /api/v1/users
    res_create = await client_authenticated.post("/auth/users", json=user_data)
    assert res_create.status_code in [200, 201]

    # 3. Attempt Delete without force
    response = await client_authenticated.delete(f"/organizations/{org_id}")
    assert response.status_code == 409
    assert "ORG_HAS_USERS" in response.text or "not empty" in response.text

    # Cleanup (Clean deletion for next test)
    await client_authenticated.delete(f"/organizations/{org_id}?force=true")


@pytest.mark.asyncio
async def test_force_delete_org_success(client_authenticated, mock_auth_service):
    """Test that force=true successfully deletes an org and its users."""
    mock_auth_service.current_user = ROOT_USER
    org_id = "force_del_org"

    # 1. Setup
    await client_authenticated.post("/organizations/", json={"id": org_id, "name": "To Delete"})
    await client_authenticated.post(
        "/auth/users", json={"uid": "user2", "organization_id": org_id, "role": "MEMBER", "email": "u@d.com"}
    )

    # 2. Force Delete
    response = await client_authenticated.delete(f"/organizations/{org_id}?force=true")
    assert response.status_code == 204

    # 3. Verify Gone
    check = await client_authenticated.get("/organizations/")
    orgs = check.json()
    assert not any(o["id"] == org_id for o in orgs)
