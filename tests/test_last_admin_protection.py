"""Last Admin Protection Tests (Async)."""

import os

import pytest
from httpx import AsyncClient

# Force Mock DB to avoid file lock conflicts with running backend
os.environ["USE_MOCK_DB"] = "true"


# Fixture setup similar to test_iam.py
@pytest.fixture
async def setup_auth_scenario(client):
    """Setup auth scenario with Last Admin Corp."""
    from backend.dependencies import get_db_client_dep
    from backend.services.auth import AuthService, OrganizationCreate

    db = get_db_client_dep()
    # Use sync=True if AuthService supports it? No, it's async first.
    svc = AuthService(db, use_firebase=False)

    # 1. Reset/Ensure System State
    svc.ensure_root_user()

    # 2. Setup Test Org "LastAdminCorp"
    root_uid = "root_master"
    org_create = OrganizationCreate(
        name="Last Admin Corp",
        admin_email="admin_last@example.com",
        admin_password="password123",
        admin_name="Last Admin",
    )
    # This creates the org AND the first admin (Last Admin)

    # Cleanup previous run if needed
    existing_users = svc.repo.list_all()
    for u in existing_users:
        if u.email == "admin_last@example.com":
            svc.repo.delete(u.uid)
        if u.email == "admin_second@example.com":
            svc.repo.delete(u.uid)

    # Re-create
    try:
        await svc.create_organization(root_uid, org_create)
    except Exception:
        # Might fail if Org ID collision, but usually we just want the User.
        pass

    # Find the user to get UID
    admin_user = svc.repo.get_by_email("admin_last@example.com")
    return admin_user


def get_headers(uid):
    """Create auth headers."""
    return {"Authorization": f"Bearer mock-token:{uid}"}


@pytest.mark.asyncio
async def test_last_admin_cannot_delete_self(client: AsyncClient, setup_auth_scenario):
    """Verify last admin cannot delete themselves."""
    admin_user = setup_auth_scenario
    assert admin_user is not None

    # Try to delete self
    response = await client.delete(f"/auth/users/{admin_user.uid}", headers=get_headers(admin_user.uid))

    # Should fail with 400 or 403 (Service raises ValueError -> 400)
    assert response.status_code == 400
    # detail could be string or dict? Usually generic handler makes it "detail": str
    # Or "message" in APIError
    assert "Cannot delete the last Administrator" in response.text



@pytest.mark.asyncio
async def test_last_admin_cannot_be_demoted(client: AsyncClient, setup_auth_scenario):
    """Verify last admin cannot be demoted."""
    admin_user = setup_auth_scenario
    assert admin_user is not None

    # Try to update role to MEMBER
    payload = {"role": "MEMBER"}
    response = await client.patch(f"/auth/users/{admin_user.uid}", json=payload, headers=get_headers(admin_user.uid))

    assert response.status_code == 400
    assert response.status_code == 400
    assert "Cannot demote the last Administrator" in response.text


@pytest.mark.asyncio
async def test_second_admin_allows_deletion(client: AsyncClient, setup_auth_scenario):
    """Verify deletion succeeds if another admin exists."""
    last_admin = setup_auth_scenario
    assert last_admin is not None

    # 1. Promote a second user to ADMIN
    # First create a member OR create directly using API if allowed?
    # Create via API as Last Admin
    new_user_payload = {
        "email": "admin_second@example.com",
        "display_name": "Second Admin",
        "role": "ADMIN",  # Direct creation as ADMIN
        "organization_id": last_admin.organization_id,
        "password": "password123"
    }

    # Note: ADMIN creating ADMIN is allowed in our new rules
    create_res = await client.post("/auth/users", json=new_user_payload, headers=get_headers(last_admin.uid))
    assert create_res.status_code == 200, f"Failed to create second admin: {create_res.text}"
    second_admin_uid = create_res.json()["uid"]

    # 2. Now Last Admin deletes themselves (should succeed because there is a second admin)
    # Actually, let's have the Second Admin delete the First Admin to test cross-admin deletion
    delete_res = await client.delete(f"/auth/users/{last_admin.uid}", headers=get_headers(second_admin_uid))

    assert delete_res.status_code == 200
    assert delete_res.json()["status"] == "deleted"


@pytest.mark.asyncio
async def test_root_can_bypass_checks_if_orphan_org_logic_not_strict(client: AsyncClient, setup_auth_scenario):
    """Verify ROOT is also subject to last admin protection."""
    last_admin = setup_auth_scenario
    assert last_admin is not None
    root_token = "root_master"

    response = await client.delete(f"/auth/users/{last_admin.uid}", headers=get_headers(root_token))

    # Based on our implementation:
    # if target.role == ADMIN: admin_count = ... if <=1 raise
    # This check runs AFTER permission check. So Root IS subject to it.
    assert response.status_code == 400
    assert "Cannot delete the last Administrator" in response.text
