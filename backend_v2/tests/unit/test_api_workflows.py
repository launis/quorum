import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from backend_v2.api.dependencies import get_current_user_from_header, get_studio_service
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.services.studio import StudioService
from backend_v2.exceptions import PermissionDeniedError
from backend_v2.main import app

def mock_get_current_user_member():
    return TokenData(email="member@test.com", id="user456", role=UserRole.MEMBER, organization_id="test_org")

def mock_get_current_user_root():
    return TokenData(email="root@test.com", id="user999", role=UserRole.ROOT, organization_id="test_org")

@pytest.fixture
def mock_studio_service_manager():
    service = AsyncMock(spec=StudioService)
    # Configure mock responses for failing non-root mutations
    service.save_workflow.side_effect = PermissionDeniedError("Only ROOT can modify workflows.")
    service.delete_workflow.side_effect = PermissionDeniedError("Only ROOT can delete workflows.")
    return service

@pytest.fixture
def client_member(mock_studio_service_manager):
    app.dependency_overrides[get_current_user_from_header] = mock_get_current_user_member
    app.dependency_overrides[get_studio_service] = lambda: mock_studio_service_manager
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_workflow_rbac_save_member_forbidden(client_member):
    payload = {
        "id": "new_wf",
        "name": {"default_locale": "en", "translations": {"en": "new"}},
        "description": {"default_locale": "en", "translations": {"en": "desc"}},
        "organization_id": "test_org"
    }
    response = client_member.put("/api/v2/studio/workflows/new_wf", json=payload)
    if response.status_code == 404:
        response = client_member.put("/studio/workflows/new_wf", json=payload)
    
    assert response.status_code == 403
    assert "Permission" in response.json()["detail"] or "ROOT" in response.json()["detail"]

def test_workflow_rbac_delete_member_forbidden(client_member):
    response = client_member.delete("/api/v2/studio/workflows/some_id")
    if response.status_code == 404:
        response = client_member.delete("/studio/workflows/some_id")

    assert response.status_code == 403
