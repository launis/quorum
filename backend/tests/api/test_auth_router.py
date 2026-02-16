
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, create_autospec
from fastapi.testclient import TestClient
from backend.main import app
from backend.dependencies import get_current_user_from_header, get_auth_service
from backend.models.auth import TokenData, UserRole, User
from backend.services.auth import AuthService

from unittest.mock import AsyncMock, MagicMock, create_autospec

# ... imports ...

client = TestClient(app)

# Mock Data
mock_auth_service = MagicMock(spec=AuthService)
# Async Methods
mock_auth_service.create_user = AsyncMock()
mock_auth_service.update_user = AsyncMock()
mock_auth_service.delete_user = AsyncMock()
mock_auth_service.create_organization = AsyncMock()
# Sync Methods (Left as MagicMock by default, but verify_token is sync)
# verify_token and create_impersonation_token are sync in AuthService.

# Need to mock the repo attribute access too, or methods
mock_auth_repo = MagicMock()
mock_auth_service.repo = mock_auth_repo

# Users
root_user = TokenData(uid="root-1", role=UserRole.ROOT, organization_id="system")
admin_user = TokenData(uid="admin-1", role=UserRole.ADMIN, organization_id="org-A")
member_user = TokenData(uid="member-1", role=UserRole.MEMBER, organization_id="org-A")

full_user_root = User(
    uid="root-1", email="root@example.com", role=UserRole.ROOT, organization_id="system",
    created_at=datetime.utcnow(), updated_at=datetime.utcnow()
)
full_user_admin = User(
    uid="admin-1", email="admin@example.com", role=UserRole.ADMIN, organization_id="org-A",
    created_at=datetime.utcnow(), updated_at=datetime.utcnow()
)

@pytest.fixture(autouse=True)
def setup_dependencies():
    app.dependency_overrides = {}
    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    yield
    app.dependency_overrides = {}

@pytest.mark.asyncio
async def test_verify_user_token_success():
    """Test successful login."""
    payload = {"token": "valid-token"}
    
    # Mock verify_token returning TokenData
    mock_auth_service.verify_token.return_value = root_user
    # Mock repo.get_by_uid returning User
    mock_auth_repo.get_by_uid.return_value = full_user_root
    mock_auth_service.use_firebase = False

    response = client.post("/auth/verify", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["token_valid"] is True
    assert data["user"]["uid"] == "root-1"


@pytest.mark.asyncio
async def test_impersonate_user_success():
    """ROOT can impersonate."""
    app.dependency_overrides[get_current_user_from_header] = lambda: root_user
    
    def get_by_uid_side_effect(uid):
        if uid == "root-1":
            return full_user_root
        if uid == "admin-1":
            return full_user_admin
        return None

    mock_auth_repo.get_by_uid.side_effect = get_by_uid_side_effect
    mock_auth_service.create_impersonation_token.return_value = "impersonation-token"

    payload = {"target_uid": "admin-1"}
    response = client.post("/auth/impersonate", json=payload)
    
    assert response.status_code == 200
    assert response.json()["access_token"] == "impersonation-token"

@pytest.mark.asyncio
async def test_impersonate_user_denied_non_root():
    """Non-ROOT cannot impersonate."""
    # Requester is ADMIN (not ROOT)
    app.dependency_overrides[get_current_user_from_header] = lambda: admin_user
    mock_auth_repo.get_by_uid.return_value = full_user_admin 

    payload = {"target_uid": "member-1"}
    response = client.post("/auth/impersonate", json=payload)
    
    assert response.status_code == 403
    assert "permission-denied-impersonation" in response.json()["type"]

@pytest.mark.asyncio
async def test_list_users_scoping():
    """Test visibility scoping."""
    # Mock repo returning list
    all_users = [
        full_user_root,
        full_user_admin,
        User(uid="mem-1", email="mem1@example.com", role=UserRole.MEMBER, organization_id="org-A", created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
        User(uid="mem-2", email="mem2@example.com", role=UserRole.MEMBER, organization_id="org-B", created_at=datetime.utcnow(), updated_at=datetime.utcnow()),
    ]
    mock_auth_repo.list_all.return_value = all_users

    # 1. ROOT sees all
    app.dependency_overrides[get_current_user_from_header] = lambda: root_user
    mock_auth_repo.get_by_uid.return_value = full_user_root
    
    response = client.get("/auth/users")
    assert response.status_code == 200
    assert len(response.json()) == 4

    # 2. ADMIN sees Own Org (root, admin, mem-1) -- Wait, root is system.
    # Logic in router: org_users = [u for u in all_users if u.organization_id == requester.organization_id]
    # Org-A has: admin-1, mem-1.
    app.dependency_overrides[get_current_user_from_header] = lambda: admin_user
    mock_auth_repo.get_by_uid.return_value = full_user_admin
    
    response = client.get("/auth/users")
    assert response.status_code == 200
    # Should see admin-1 and mem-1
    uids = [u["uid"] for u in response.json()]
    assert "admin-1" in uids
    assert "mem-1" in uids
    assert "mem-2" not in uids # Org-B

