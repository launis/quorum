"""IAM Tests (Clean Slate).

Verifies Role-Based Access Control (RBAC) and Organization boundaries.
Uses strictly isolated dependency overrides with NO shared fixtures unless explicit.
"""

import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.models.auth import TokenData, UserRole
from backend.dependencies import get_current_user_from_header
from backend.exceptions import AuthenticationError

# --- CONSTANTS ---
ROOT_TOKEN = "mock-token:root_master"
ADMIN_TOKEN = "mock-token:admin_1"
MEMBER_TOKEN = "mock-token:member_1"


@pytest.fixture
def mock_auth_dep_factory():
    """Factory to create dynamic auth overrides per test."""
    
    def _create_override(role: UserRole, uid: str, org_id: str):
        async def _mock_auth():
            return TokenData(
                uid=uid,
                email=f"{uid}@example.com",
                role=role,
                organization_id=org_id
            )
        return _mock_auth
    
    return _create_override


@pytest.fixture
async def async_client():
    """Async client with NO default auth. Tests must install overrides."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c





# --- ACTUAL IMPLEMENTATION ---
# To avoid singleton hell, we will mock the `OrganizationService` dependency 
# if possible, or just seed a fresh temporary DB.
# For simplicity and strictness: MOCK THE REPO.

from unittest.mock import AsyncMock, MagicMock
from backend.api.organization_router import get_db_client_dep, get_settings


@pytest.mark.asyncio
async def test_root_list_organizations_success(async_client):
    """Verify ROOT can list organizations."""
    
    # 1. Mock Auth
    app.dependency_overrides[get_current_user_from_header] = lambda: TokenData(
        uid="root", email="root@e.com", role=UserRole.ROOT, organization_id="system"
    )
    
    # 2. Mock REPO directly
    mock_repo = MagicMock()
    mock_repo.list_organizations.return_value = [
        {"id": "system", "name": "System", "tier": "root"},
        {"id": "org-1", "name": "Test Org", "tier": "standard"}
    ]
    
    from backend.dependencies import get_async_repository
    async def _get_mock_repo():
        return mock_repo
    app.dependency_overrides[get_async_repository] = _get_mock_repo
    
    try:
        response = await async_client.get("/organizations/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["id"] == "system"
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_admin_list_organizations_forbidden(async_client):
    """Verify ADMIN cannot list all organizations."""
    
    # 1. Mock Auth as ADMIN
    app.dependency_overrides[get_current_user_from_header] = lambda: TokenData(
        uid="admin", email="admin@e.com", role=UserRole.ADMIN, organization_id="org-1"
    )
    
    try:
        response = await async_client.get("/organizations/")
        assert response.status_code == 403
        assert response.json()["error_code"] == "PERMISSION_DENIED_ERROR"
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_create_organization_root_success(async_client):
    """Verify ROOT can create organization."""
    
    app.dependency_overrides[get_current_user_from_header] = lambda: TokenData(
        uid="root", email="root@e.com", role=UserRole.ROOT, organization_id="system"
    )
    
    # Mock Repository directly (bypassing the get_db_client_dep issue)
    mock_repo = MagicMock()
    mock_repo.get_organization.return_value = None # No conflict
    
    from backend.dependencies import get_async_repository
    async def _get_mock_repo():
        return mock_repo
    app.dependency_overrides[get_async_repository] = _get_mock_repo

    # We also need to mock AuthService because the endpoint uses it for 'require_role' (which we mocked via user override)
    # BUT the endpoint also accepts 'auth: AuthServiceDep'.
    # get_auth_service depends on get_db_client_dep. 
    # Let's override get_db_client_dep too, just to be safe for AuthService.
    mock_db = MagicMock()
    app.dependency_overrides[get_db_client_dep] = lambda: mock_db

    payload = {
        "id": "new-org",
        "name": "New Org",
        "tier": "starter",
        "contact_email": "new@org.com"
    }

    try:
        response = await async_client.post("/organizations/", json=payload)
        
        # Verify repo calls
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "new-org"
        mock_repo.create_organization.assert_called_once()
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_create_organization_duplicate_conflict(async_client):
    """Verify duplicate ID returns 409."""
    
    app.dependency_overrides[get_current_user_from_header] = lambda: TokenData(
        uid="root", email="root@e.com", role=UserRole.ROOT, organization_id="system"
    )
    
    mock_repo = MagicMock()
    # Simulator existing org
    mock_repo.get_organization.return_value = {"id": "existing-org", "name": "Existing"} 
    
    from backend.dependencies import get_async_repository
    async def _get_mock_repo():
        return mock_repo
    app.dependency_overrides[get_async_repository] = _get_mock_repo
    
    # Mock DB for AuthService safety
    mock_db = MagicMock()
    app.dependency_overrides[get_db_client_dep] = lambda: mock_db

    payload = {"id": "existing-org", "name": "Fail", "tier": "standard"}

    try:
        response = await async_client.post("/organizations/", json=payload)
        assert response.status_code == 409
        assert response.json()["error_code"] == "CONFLICT_ERROR"
    finally:
        app.dependency_overrides = {}
