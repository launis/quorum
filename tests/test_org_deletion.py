
# Tests for Organization Deletion and Root Protection

import pytest
import os
# Force Mock DB
os.environ["USE_MOCK_DB"] = "true"

from fastapi.testclient import TestClient
from backend.main import app
from backend.models.auth import UserRole

client = TestClient(app)

@pytest.fixture
def setup_root_and_org():
    from backend.dependencies import get_db_client_dep
    from backend.services.auth import AuthService, OrganizationCreate
    
    db = get_db_client_dep()
    svc = AuthService(db, use_firebase=False)
    
    # Ensure Root
    root = svc.ensure_root_user()
    
    # Create Target Org
    org_create = OrganizationCreate(
        name="Doomed Corp",
        admin_email="doomed_admin@example.com",
        admin_password="password123",
        admin_name="Doomed Admin"
    )
    
    # Cleanup if exists
    # Cleanup if exists
    svc.org_repo.table.remove(lambda x: x['name'] == "Doomed Corp")
        
    try:
        new_org = svc.create_organization(root.uid, org_create)
    except Exception:
        pass
        
    # Get ID
    target_org = svc.org_repo.table.search(lambda x: x['name'] == "Doomed Corp")[0]
    return root, target_org['id']

def get_headers(uid):
    return {"Authorization": f"Bearer mock-token:{uid}"}

def test_root_cannot_be_deleted(setup_root_and_org):
    root_user, _ = setup_root_and_org
    
    # Root tries to delete themselves? Or another root?
    # Based on logic: delete_user(initiator, target)
    
    # Try deleting Root Master
    response = client.delete(f"/auth/users/root_master", headers=get_headers(root_user.uid))
    assert response.status_code == 403
    assert "Root account cannot be deleted" in response.json()['detail']

def test_org_deletion_cascades(setup_root_and_org):
    root_user, org_id = setup_root_and_org
    
    # Verify users exist
    # (We assume verify_token works so we can list them or just trust create_organization made them)
    
    # Execute Delete Org
    response = client.delete(f"/organizations/{org_id}", headers=get_headers(root_user.uid))
    assert response.status_code == 204
    
    # Verify Org is gone
    get_res = client.get(f"/organizations/{org_id}", headers=get_headers(root_user.uid))
    assert get_res.status_code == 404
    
    # Verify Users are gone (Doomed Admin) with clean DB check
    # We can use the service directly or API
    # Let's use internal check via fixture logic imports would be cleaner but client is easier
    # The Admin was "doomed_admin@example.com". 
    # Let's try to login as them (should fail) or list all users
    
    from backend.dependencies import get_db_client_dep
    db = get_db_client_dep()
    users_table = db.table("users")
    remaining = users_table.search(lambda x: x['organization_id'] == org_id)
    assert len(remaining) == 0

