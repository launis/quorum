
import pytest
from unittest.mock import AsyncMock, MagicMock, create_autospec, patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.dependencies import get_current_user_from_header, get_repository, get_auth_service, get_audit_service
from backend.models.auth import TokenData, UserRole, Organization, SubscriptionStatus
from backend.services.auth import AuthService
from backend.database.repository import AbstractWorkflowRepository

client = TestClient(app)

# --- Mocks ---
# Repo
mock_repo = AsyncMock()
# Auth Service
mock_auth_service = MagicMock(spec=AuthService)
mock_auth_service.create_user = AsyncMock()
mock_auth_service.delete_user = AsyncMock()
mock_auth_service.repo = MagicMock() # Needs internal repo access for some utilities? usage mostly does not.

# Users
root_user = TokenData(uid="root-1", role=UserRole.ROOT, organization_id="system")
admin_user = TokenData(uid="admin-1", role=UserRole.ADMIN, organization_id="org-1")
member_user = TokenData(uid="member-1", role=UserRole.MEMBER, organization_id="org-1")

# Orgs
org_1 = {
    "id": "org-1",
    "name": "Acme Corp",
    "tier": "standard",
    "quota_limit": 100.0,
    "tpm_limit": 100000,
    "rpm_limit": 60,
    "is_active": True
}

@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides = {}
    app.dependency_overrides[get_repository] = lambda: mock_repo
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    app.dependency_overrides[get_audit_service] = lambda: mock_repo # Reuse mock_repo as it has log_audit_event? 
    # Or better, create separate mock for audit service
    mock_audit = AsyncMock()
    app.dependency_overrides[get_audit_service] = lambda: mock_audit
    
    mock_repo.reset_mock()
    mock_auth_service.reset_mock()
    mock_repo.log_audit_event = AsyncMock() # Still needed? No, audit service uses repo. 
    # Wait, the injected AuditService calls repo. But here we override AuditService itself.
    # So we just need mock_audit.log_event = AsyncMock()
    mock_audit.log_event = AsyncMock()

    yield
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_create_organization_root_only():
    """Only ROOT can create organizations."""
    # 1. ROOT -> Success
    app.dependency_overrides[get_current_user_from_header] = lambda: root_user
    mock_repo.get_organization.return_value = None # No conflict
    mock_repo.create_organization.return_value = None
    
    payload = {"name": "New Corp", "tier": "premium"}
    response = client.post("/organizations/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Corp"
    assert data["id"] is not None

    # 2. ADMIN -> Fail (Router checks AuthService.require_role(ROOT))
    app.dependency_overrides[get_current_user_from_header] = lambda: admin_user
    response = client.post("/organizations/", json=payload)
    # The dependency require_role raises PermissionDeniedError (403)
    assert response.status_code == 403
    assert "permission-denied" in response.json()["type"]

@pytest.mark.asyncio
async def test_get_organization_access_control():
    """Verify Organization scoping."""
    mock_repo.get_organization.return_value = org_1

    # 1. ROOT can access any
    app.dependency_overrides[get_current_user_from_header] = lambda: root_user
    response = client.get("/organizations/org-1")
    assert response.status_code == 200

    # 2. ADMIN can access OWN
    app.dependency_overrides[get_current_user_from_header] = lambda: admin_user
    response = client.get("/organizations/org-1")
    assert response.status_code == 200

    # 3. ADMIN cannot access OTHER
    # admin_user has org="org-1". Try "org-2"
    app.dependency_overrides[get_current_user_from_header] = lambda: admin_user
    response = client.get("/organizations/org-2")
    assert response.status_code == 403
    assert "permission-denied" in response.json()["type"]

@pytest.mark.asyncio
async def test_get_organization_usage_not_found():
    """Fail Fast if org not found."""
    app.dependency_overrides[get_current_user_from_header] = lambda: root_user
    mock_repo.get_organization.return_value = None

    response = client.get("/organizations/bad-id/usage")
    assert response.status_code == 404
    assert "organization-not-found" in response.json()["type"]

@pytest.mark.asyncio
async def test_delete_organization_conflict():
    """Cannot delete non-empty org without force."""
    app.dependency_overrides[get_current_user_from_header] = lambda: root_user
    # Mock list_users returning non-empty
    mock_repo.list_users.return_value = [{"uid": "u1"}]

    response = client.delete("/organizations/org-1")
    assert response.status_code == 409
    assert "organization-not-empty" in response.json()["type"]

@pytest.mark.asyncio
async def test_create_organization_user_strict_types():
    """Verify strict user creation payload."""
    app.dependency_overrides[get_current_user_from_header] = lambda: admin_user
    
    # Missing 'role' or 'email' should be 422 (Pydantic), but let's check correct payload
    payload = {
        "email": "new@example.com",
        "display_name": "New User",
        "role": "MEMBER",
        "password": "password123"
    }
    
    # Mock AuthService.create_user return
    from backend.models.auth import User, UserRole
    from datetime import datetime
    new_user_mock = User(
        uid="u-new", email="new@example.com", role=UserRole.MEMBER, organization_id="org-1",
        created_at=datetime.utcnow()
    )
    mock_auth_service.create_user.return_value = new_user_mock

    response = client.post("/organizations/org-1/users", json=payload)
    assert response.status_code == 201
    assert response.json()["uid"] == "u-new"

