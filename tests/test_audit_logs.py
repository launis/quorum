import pytest
from httpx import AsyncClient

from backend.dependencies import get_current_user_from_header
from backend.main import app


@pytest.mark.asyncio
async def test_audit_access_control(client: AsyncClient):
    """Verify RBAC for Audit Logs:
    1. Setup: Create Org, Admin, Member using Root (via mock token).
    2. MEMBER Access -> 403 Forbidden.
    3. ADMIN Access -> 200 OK (Own Org), 200 OK (Own Actions).
    4. ROOT Access -> 200 OK (Everything).
    """
    # 1. Disable Force-Root for this test to allow multi-user testing
    app.dependency_overrides.pop(get_current_user_from_header, None)

    # Use Root Token for Setup (AuthService supports 'mock-token:<uid>' in dev mode)
    root_header = {"Authorization": "Bearer mock-token:root_master"}

    # Create Org
    org_res = await client.post("/organizations/", json={"name": "RBAC Corp", "tier": "standard"}, headers=root_header)
    with open("test_progress.log", "a") as f:
        f.write(f"RBAC Setup Org: {org_res.status_code}\n")
    assert org_res.status_code == 201
    org_id = org_res.json()["id"]

    # Create Member
    try:
        member_payload = {"email": "mem@rbac.com", "display_name": "Mem", "role": "MEMBER", "password": "password123"}
        mem_res = await client.post(f"/organizations/{org_id}/users", json=member_payload, headers=root_header)
        with open("test_progress.log", "a") as f:
            f.write(f"RBAC Setup Member: {mem_res.status_code}\n")
        if mem_res.status_code != 201:
            with open("test_progress.log", "a") as f:
                f.write(f"RBAC Setup Member Error Body: {mem_res.text}\n")
        assert mem_res.status_code == 201
        mem_uid = mem_res.json()["uid"]
    except Exception as e:
        with open("test_progress.log", "a") as f:
            f.write(f"RBAC Setup Member EXCEPTION: {e}\n")
        raise e

    # Create Admin
    admin_payload = {"email": "adm@rbac.com", "display_name": "Adm", "role": "ADMIN", "password": "password123"}
    adm_res = await client.post(f"/organizations/{org_id}/users", json=admin_payload, headers=root_header)
    with open("test_progress.log", "a") as f:
        f.write(f"RBAC Setup Admin: {adm_res.status_code}\n")
    assert adm_res.status_code == 201
    adm_uid = adm_res.json()["uid"]

    member_header = {"Authorization": f"Bearer mock-token:{mem_uid}"}
    admin_header = {"Authorization": f"Bearer mock-token:{adm_uid}"}

    # 2. MEMBER Access -> 403 (Assuming Members cannot read audit logs)
    res = await client.get(f"/audit/logs?organization_id={org_id}", headers=member_header)
    with open("test_progress.log", "a") as f:
        f.write(f"RBAC Step 2 Member Status: {res.status_code}\n")
    assert res.status_code == 403, f"Member should be forbidden. Got {res.status_code}"

    # 3. ADMIN Access -> 200
    res = await client.get(f"/audit/logs?organization_id={org_id}", headers=admin_header)
    with open("test_progress.log", "a") as f:
        f.write(f"RBAC Step 3 Admin Status: {res.status_code}\n")
    assert res.status_code == 200
    assert len(res.json()) >= 2  # Member creation, Admin creation logs

    # 4. ROOT Access -> 200
    res = await client.get("/audit/logs", headers=root_header)
    with open("test_progress.log", "a") as f:
        f.write(f"RBAC Step 4 Root Status: {res.status_code}\n")
    assert res.status_code == 200

    with open("test_progress.log", "a") as f:
        f.write("RBAC TEST SUCCESS\n")


# --- Fixtures & Helpers ---


@pytest.fixture
def member_token_headers():
    """Headers for a standard MEMBER user."""
    return {"Authorization": "Bearer mock_token_member"}


@pytest.fixture
def admin_token_headers_custom(client):
    """Headers for an ADMIN of a specific org (not ROOT)."""
    return {"Authorization": "Bearer mock_token_admin_custom"}


# --- Tests ---


@pytest.mark.asyncio
async def test_audit_lifecycle_root(client: AsyncClient, admin_token_headers):
    """Verify the full audit lifecycle as ROOT:
    1. Create Organization -> Expect ORG_CREATED log.
    2. Create User in that Org -> Expect USER_CREATED log.
    3. Delete User -> Expect USER_DELETED log.
    4. Delete Organization -> Expect ORG_DELETED log.
    """
    # 1. Create Organization
    org_payload = {"name": "Audit Test Corp", "tier": "standard", "quota_limit": 50.0}
    res = await client.post("/organizations/", json=org_payload, headers=admin_token_headers)
    assert res.status_code == 201
    org_id = res.json()["id"]

    # Verify Log: ORG_CREATED
    res_logs = await client.get(f"/audit/logs?organization_id={org_id}&action=ORG_CREATED", headers=admin_token_headers)
    assert res_logs.status_code == 200
    logs = res_logs.json()
    assert len(logs) >= 1
    assert logs[0]["action"] == "ORG_CREATED"
    assert logs[0]["organization_id"] == org_id

    # 2. Create User
    user_payload = {
        "email": "audited_user@test.com",
        "display_name": "Audited User",
        "role": "MEMBER",
        "password": "password123",
    }
    res = await client.post(f"/organizations/{org_id}/users", json=user_payload, headers=admin_token_headers)
    assert res.status_code == 201
    user_uid = res.json()["uid"]

    # Verify Log: USER_CREATED
    res_logs = await client.get(
        f"/audit/logs?organization_id={org_id}&action=USER_CREATED", headers=admin_token_headers
    )
    assert res_logs.status_code == 200
    logs = res_logs.json()
    found = any(l["target_uid"] == user_uid for l in logs)
    assert found, "USER_CREATED log not found for new user"

    # 3. Delete User
    res = await client.delete(f"/organizations/{org_id}/users/{user_uid}", headers=admin_token_headers)
    with open("test_progress.log", "a") as f:
        f.write(f"Step 3 User Delete Status: {res.status_code}\n")
    assert res.status_code == 204, f"Delete failed: {res.status_code}"

    # Verify Log: USER_DELETED
    res_logs = await client.get(
        f"/audit/logs?organization_id={org_id}&action=USER_DELETED", headers=admin_token_headers
    )
    with open("test_progress.log", "a") as f:
        f.write(f"Step 3 Audit Log Status: {res_logs.status_code}\n")
    assert res_logs.status_code == 200
    logs = res_logs.json()
    found = any(l["target_uid"] == user_uid for l in logs)
    assert found, "USER_DELETED log not found"

    # 4. Delete Organization
    res = await client.delete(f"/organizations/{org_id}", headers=admin_token_headers)
    with open("test_progress.log", "a") as f:
        f.write(f"Step 4 Org Delete Status: {res.status_code}\n")
    assert res.status_code == 204

    # Verify Log: ORG_DELETED
    res_logs = await client.get(f"/audit/logs?organization_id={org_id}&action=ORG_DELETED", headers=admin_token_headers)
    with open("test_progress.log", "a") as f:
        f.write(f"Step 4 Audit Log Status: {res_logs.status_code}\n")
    assert res_logs.status_code == 200
    logs = res_logs.json()
    assert len(logs) >= 1
    assert logs[0]["action"] == "ORG_DELETED"

    with open("test_progress.log", "a") as f:
        f.write("TEST COMPLETE SUCCESS\n")


# @pytest.mark.asyncio
# async def test_audit_access_control(client: AsyncClient, admin_token_headers):
#     pass
