
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from backend.main import app
from backend.dependencies import get_async_repository, get_auth_service, get_audit_service
from backend.models.auth import TokenData, UserRole
from backend.models.settings import SystemSettings

client = TestClient(app)

# Mocks
mock_repo = AsyncMock()
mock_auth_service = MagicMock()
mock_audit_service = AsyncMock()

@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides = {}
    app.dependency_overrides[get_async_repository] = lambda: mock_repo
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    app.dependency_overrides[get_audit_service] = lambda: mock_audit_service
    
    mock_repo.reset_mock()
    mock_auth_service.reset_mock()
    mock_audit_service.reset_mock()
    mock_audit_service.log_event = AsyncMock()
    
    yield
    app.dependency_overrides = {}

def get_token_header(role: UserRole = UserRole.ROOT, uid: str = "test_user"):
    # Mock verify_token to return this user
    token = f"Bearer {role.value}_token"
    mock_auth_service.verify_token.return_value = TokenData(
        uid=uid,
        role=role,
        organization_id="system"
    )
    return {"Authorization": token}

@pytest.mark.asyncio
async def test_get_settings_success():
    # Setup
    mock_settings = {"maintenance_mode": True, "global_banner": "Test Banner"}
    mock_repo.get_system_settings.return_value = mock_settings
    
    # Execute
    response = client.get("/settings")
    
    # Verify
    assert response.status_code == 200
    data = response.json()
    assert data["maintenance_mode"] is True
    assert data["global_banner"] == "Test Banner"
    assert data["default_model_strategy"] == "fast" # Default

@pytest.mark.asyncio
async def test_get_settings_empty_db():
    # Setup: DB returns None (first run)
    mock_repo.get_system_settings.return_value = None
    
    # Execute
    response = client.get("/settings")
    
    # Verify
    assert response.status_code == 200
    data = response.json()
    assert data["maintenance_mode"] is False # Default

@pytest.mark.asyncio
async def test_update_settings_success():
    # Setup
    mock_auth_service.verify_token.return_value = TokenData(uid="root", role=UserRole.ROOT, organization_id="system")
    update_payload = {"global_banner": "New Banner", "maintenance_mode": True}
    
    # Execute
    response = client.patch("/settings", json=update_payload, headers={"Authorization": "Bearer root_token"})
    
    # Verify
    assert response.status_code == 200
    assert response.json()["global_banner"] == "New Banner"
    
    # Verify Repo call
    mock_repo.update_system_settings.assert_called_once()
    call_args = mock_repo.update_system_settings.call_args[0][0]
    assert call_args["global_banner"] == "New Banner"
    
    # Verify Audit
    mock_audit_service.log_event.assert_called_once()
    assert mock_audit_service.log_event.call_args[1]["action"] == "SETTINGS_UPDATED"

@pytest.mark.asyncio
async def test_update_settings_permission_denied():
    # Setup: ADMIN (not ROOT)
    mock_auth_service.verify_token.return_value = TokenData(uid="admin", role=UserRole.ADMIN, organization_id="org1")
    
    # Execute
    response = client.patch("/settings", json={}, headers={"Authorization": "Bearer admin_token"})
    
    # Verify
    assert response.status_code == 403
    # Verify RFC 7807 Structure
    data = response.json()
    assert data["status"] == 403
    assert data["title"] == "Permission Denied Root Only"
    assert "permission-denied-root-only" in data["type"]
