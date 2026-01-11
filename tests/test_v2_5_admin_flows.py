"""Admin V2.5 Flow Tests."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.auth import TokenData, UserRole

client = TestClient(app)


@pytest.mark.asyncio
async def test_global_settings_persistence(client_authenticated, mock_auth_service):
    """Verify ROOT can update global settings and audit log is created."""
    mock_auth_service.current_user.role = UserRole.ROOT
    
    # 1. Get initial
    res = await client_authenticated.get("/settings")
    assert res.status_code == 200

    # 2. Update
    payload = {"maintenance_mode": True, "global_banner": "Test Banner"}
    res = await client_authenticated.patch("/settings", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["maintenance_mode"] is True
    assert data["global_banner"] == "Test Banner"

    # 3. Verify Persistence
    res = await client_authenticated.get("/settings")
    assert res.json()["maintenance_mode"] is True

    # 4. Verify Audit Log
    res = await client_authenticated.get("/audit/logs", params={"action": "SETTINGS_UPDATED", "limit": 1})
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0
    assert logs[0]["action"] == "SETTINGS_UPDATED"
    assert logs[0]["details"]["maintenance_mode"] is True


@pytest.mark.asyncio
async def test_organization_lifecycle_saas(client_authenticated, mock_auth_service):
    """Verify Org creation with Billing fields and User management."""
    mock_auth_service.current_user.role = UserRole.ROOT

    # 1. Create Org with SaaS fields
    org_payload = {
        "name": "SaaS Corp",
        "tier": "premium",
        "subscription_status": "active",
        "quota_limit": 5000,
        "billing_id": "cust_123",
        "contact_email": "admin@saas.com",
    }
    res = await client_authenticated.post("/organizations/", json=org_payload)
    assert res.status_code == 201
    org = res.json()
    org_id = org["id"]

    assert org["subscription_status"] == "active"
    assert org["quota_limit"] == 5000
    assert org["billing_id"] == "cust_123"

    # 2. Create User in Org
    user_payload = {"email": "user@saas.com", "display_name": "SaaS User", "role": "MEMBER", "password": "password123"}
    res = await client_authenticated.post(f"/organizations/{org_id}/users", json=user_payload)
    assert res.status_code == 201
    user = res.json()
    user_uid = user["uid"]
    assert user["email"] == "user@saas.com"
    assert user["organization_id"] == org_id

    # 3. Verify Audit Log for Org & User Creation
    res = await client_authenticated.get("/audit/logs", params={"organization_id": org_id, "limit": 10})
    logs = res.json()
    actions = [entry["action"] for entry in logs]
    assert "ORG_CREATED" in actions or "USER_CREATED" in actions  # Depending on order/filter

    # 4. Impersonation
    res = await client_authenticated.post("/auth/impersonate", json={"target_uid": user_uid})
    assert res.status_code == 200
    token_data = res.json()
    assert "access_token" in token_data

    # 5. Delete User
    res = await client_authenticated.delete(f"/organizations/{org_id}/users/{user_uid}")
    assert res.status_code == 204

    # 6. Verify Deletion Audit
    res = await client_authenticated.get("/audit/logs", params={"action": "USER_DELETED", "target_uid": user_uid})
    assert res.status_code == 200
    assert len(res.json()) >= 1
