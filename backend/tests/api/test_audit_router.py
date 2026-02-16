
import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from backend.main import app
from backend.dependencies import get_current_user_from_header, get_audit_service
from backend.models.auth import TokenData, UserRole
from backend.models.audit import AuditEvent

# Create client once? No, TestClient persists app state.
client = TestClient(app)

# Mock Data
mock_audit_service = AsyncMock()

root_user = TokenData(uid="root-1", role=UserRole.ROOT, organization_id="system")
admin_user = TokenData(uid="admin-1", role=UserRole.ADMIN, organization_id="org-A")
member_user = TokenData(uid="member-1", role=UserRole.MEMBER, organization_id="org-A")

@pytest.fixture(autouse=True)
def cleanup_overrides():
    """Ensure clean start for each test."""
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_audit_root_access():
    """ROOT can access all logs."""
    mock_audit_service.get_logs.return_value = []
    
    app.dependency_overrides[get_audit_service] = lambda: mock_audit_service
    app.dependency_overrides[get_current_user_from_header] = lambda: root_user

    response = client.get("/audit/logs")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    
    mock_audit_service.get_logs.assert_called()


@pytest.mark.asyncio
async def test_audit_admin_access_own_org():
    """ADMIN is forced to their own org."""
    mock_audit_service.get_logs.return_value = []
    mock_audit_service.get_logs.reset_mock()

    app.dependency_overrides[get_audit_service] = lambda: mock_audit_service
    app.dependency_overrides[get_current_user_from_header] = lambda: admin_user

    # No param -> Scoped to user.org
    response = client.get("/audit/logs")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    mock_audit_service.get_logs.assert_called_with(
        organization_id="org-A", actor_uid=None, action=None, limit=100
    )


@pytest.mark.asyncio
async def test_audit_admin_access_other_org_denied():
    """ADMIN cannot access other orgs."""
    app.dependency_overrides[get_audit_service] = lambda: mock_audit_service
    app.dependency_overrides[get_current_user_from_header] = lambda: admin_user

    response = client.get("/audit/logs?organization_id=org-B")
    
    assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
    data = response.json()
    assert "access-denied-organization-mismatch" in data["type"]


@pytest.mark.asyncio
async def test_audit_member_denied():
    """MEMBER cannot access logs."""
    app.dependency_overrides[get_audit_service] = lambda: mock_audit_service
    app.dependency_overrides[get_current_user_from_header] = lambda: member_user

    response = client.get("/audit/logs")
    
    assert response.status_code == 403, f"Expected 403, got {response.status_code}: {response.text}"
    data = response.json()
    assert "permission-denied-audit-view" in data["type"]


@pytest.mark.asyncio
async def test_audit_service_failure():
    """Service failure raises 500."""
    mock_audit_service.get_logs.side_effect = Exception("DB Connection Failed")
    app.dependency_overrides[get_audit_service] = lambda: mock_audit_service
    app.dependency_overrides[get_current_user_from_header] = lambda: root_user

    response = client.get("/audit/logs")
    
    assert response.status_code == 500, f"Expected 500, got {response.status_code}: {response.text}"
    mock_audit_service.get_logs.side_effect = None # Reset
    data = response.json()
    assert "audit-log-retrieval-failed" in data["type"]
