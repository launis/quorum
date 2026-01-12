import pytest
import asyncio
from backend.services.auth import AuthService, OrganizationRepository, UserRepository
from backend.models.auth import User, UserRole
from backend.database.wrapper import TinyDBClient

@pytest.fixture
def test_db_client(tmp_path):
    """Fixture for temporary TinyDB client."""
    db_path = tmp_path / "test_db.json"
    client = TinyDBClient(str(db_path))
    yield client
    client.close()

@pytest.fixture
def auth_service(test_db_client):
    """Fixture for AuthService."""
    return AuthService(test_db_client, use_firebase=False)

@pytest.mark.asyncio
async def test_get_users_by_organization(auth_service):
    """Test retrieving users for a specific organization."""
    # Setup Data
    org_id_1 = "org_A"
    org_id_2 = "org_B"
    
    user1 = User(uid="u1", email="u1@a.com", role=UserRole.MEMBER, organization_id=org_id_1, created_at="now")
    user2 = User(uid="u2", email="u2@a.com", role=UserRole.ADMIN, organization_id=org_id_1, created_at="now")
    user3 = User(uid="u3", email="u3@b.com", role=UserRole.MEMBER, organization_id=org_id_2, created_at="now")
    
    auth_service.repo.create(user1)
    auth_service.repo.create(user2)
    auth_service.repo.create(user3)
    
    # Test Org 1
    users_org_1 = await auth_service.get_users_by_organization(org_id_1)
    assert len(users_org_1) == 2
    uids_1 = {u.uid for u in users_org_1}
    assert "u1" in uids_1
    assert "u2" in uids_1
    
    # Test Org 2
    users_org_2 = await auth_service.get_users_by_organization(org_id_2)
    assert len(users_org_2) == 1
    assert users_org_2[0].uid == "u3"
    
    # Test Non-existent Org
    users_none = await auth_service.get_users_by_organization("non_existent")
    assert isinstance(users_none, list)
    assert len(users_none) == 0
