"""IAM Tests (Clean & Simplified).

Verifies Organization Router RBAC and Conflicts.
Uses strict dependency injection overrides for isolation.
"""

from unittest.mock import MagicMock, AsyncMock
import pytest
from httpx import ASGITransport, AsyncClient

from backend.dependencies import get_async_repository, get_current_user_from_header, get_db_client_dep
from backend.main import app
from backend.models.auth import TokenData, UserRole
import backend.dependencies

# --- FIXTURES ---

@pytest.fixture
async def async_client():
    """Returns an AsyncClient bound to the app."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_repo():
    """Returns a MagicMock for the Repository with Async methods."""
    mock = MagicMock()
    mock.get_organization = AsyncMock(return_value=None)
    mock.create_organization = AsyncMock()
    mock.list_organizations = AsyncMock(return_value=[])
    return mock

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def setup_overrides(mock_repo, mock_db):
    """Setup and Teardown Dependency Overrides & Singleton Injection."""
    # 1. Override dependencies
    async def _get_mock_repo():
        return mock_repo

    app.dependency_overrides[get_async_repository] = _get_mock_repo
    app.dependency_overrides[get_db_client_dep] = lambda: mock_db

    # 2. Workaround: Inject into singleton to ensure recursive deps use it
    original_repo = backend.dependencies._repository_instance
    backend.dependencies._repository_instance = mock_repo

    yield

    # Cleanup
    app.dependency_overrides = {}
    backend.dependencies._repository_instance = original_repo

def override_auth(role: UserRole, uid: str = "user", org_id: str = "org1"):
    """Helper to set the current user."""
    app.dependency_overrides[get_current_user_from_header] = lambda: TokenData(
        uid=uid, email=f"{uid}@test.com", role=role, organization_id=org_id
    )

# --- TESTS ---

@pytest.mark.asyncio
async def test_root_list_organizations_success(async_client, mock_repo, setup_overrides):
    """Verify ROOT can list organizations."""
    override_auth(UserRole.ROOT, uid="root", org_id="system")
    
    mock_repo.list_organizations.return_value = [
        {"id": "system", "name": "System", "tier": "root"},
        {"id": "org-1", "name": "Test Org", "tier": "standard"},
    ]

    response = await async_client.get("/organizations/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["id"] == "system"

@pytest.mark.asyncio
async def test_admin_list_organizations_forbidden(async_client, setup_overrides):
    """Verify ADMIN cannot list all organizations."""
    override_auth(UserRole.ADMIN, uid="admin", org_id="org-1")

    response = await async_client.get("/organizations/")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_organization_root_success(async_client, mock_repo, setup_overrides):
    """Verify ROOT can create organization."""
    override_auth(UserRole.ROOT, uid="root", org_id="system")
    
    mock_repo.get_organization.return_value = None  # No conflict

    payload = {"id": "new-org", "name": "New Org", "tier": "starter", "contact_email": "new@org.com"}

    response = await async_client.post("/organizations/", json=payload)

    # Verify repo calls
    assert response.status_code == 201, f"Response: {response.text}"
    data = response.json()
    assert data["id"] == "new-org"
    mock_repo.create_organization.assert_called_once()

@pytest.mark.asyncio
async def test_create_organization_duplicate_conflict(async_client, mock_repo, setup_overrides):
    """Verify duplicate ID returns 409."""
    override_auth(UserRole.ROOT, uid="root", org_id="system")
    
    mock_repo.get_organization.return_value = {"id": "existing-org", "name": "Existing"}

    payload = {"id": "existing-org", "name": "Fail", "tier": "standard"}

    response = await async_client.post("/organizations/", json=payload)
    assert response.status_code == 409
    assert response.json()["error_code"] == "ORGANIZATION_ALREADY_EXISTS"
