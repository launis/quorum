import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.settings import get_settings

client = TestClient(app)

# --- FIXTURES & CONSTANTS ---
ROOT_TOKEN = "mock-token:root_master"
ADMIN_TOKEN = "mock-token:admin_1"  # Belongs to 'org-1'
MEMBER_TOKEN = "mock-token:member_1" # Belongs to 'org-1'

@pytest.fixture(autouse=True)
def setup_auth():
    from backend.dependencies import get_db_client_dep, get_settings_dep
    from backend.services.auth import AuthService
    
    # Bootstrap DB with users
    db = get_db_client_dep()
    svc = AuthService(db, use_firebase=False)
    svc.ensure_root_user()

def get_headers(token):
    return {"Authorization": f"Bearer {token}"}

# --- TESTS ---

def test_root_can_list_organizations():
    """
    Verify ROOT user can fetch the organization list.
    """
    response = client.get("/organizations/", headers=get_headers(ROOT_TOKEN))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check that we have at least the system-seeded organizations
    # (Assuming seed has run, usually we have 'system' and maybe 'org-1')
    ids = [o['id'] for o in data]
    assert "system" in ids

def test_admin_cannot_list_all_organizations():
    """
    Verify standard ADMIN cannot list *all* organizations (only their own scope usually, 
    but /organizations/ usually requires ROOT/System Admin privileges in this architecture).
    """
    # NOTE: Depending on policy, ADMIN might get 403 or just their own.
    # In V2.2 Architecture: /organizations/ logic usually restricts to ROOT.
    response = client.get("/organizations/", headers=get_headers(ADMIN_TOKEN))
    
    # Expecting 403 Forbidden for non-ROOT users identifying as system admins
    assert response.status_code == 403

def test_root_can_create_organization():
    """
    Verify ROOT can create a new organization/tenant.
    """
    new_org_id = "test-org-pytest"
    payload = {
        "id": new_org_id,
        "name": "Pytest Automated Org",
        "tier": "standard",
        "contact_email": "test@example.com"
    }
    
    # 1. Create
    response = client.post("/organizations/", json=payload, headers=get_headers(ROOT_TOKEN))
    # It might already exist from previous runs if DB persists
    if response.status_code == 409:
        # Cleanup (Delete) then Retry logic would be ideal, but for now we accept 409 or 201
        assert response.status_code == 409
    else:
        assert response.status_code == 201
        data = response.json()
        assert data['id'] == new_org_id
        assert data['name'] == payload['name']

    # 2. Verify Existence
    get_res = client.get(f"/organizations/{new_org_id}", headers=get_headers(ROOT_TOKEN))
    assert get_res.status_code == 200
    assert get_res.json()['id'] == new_org_id

    # 3. Cleanup (Optional, but good for repeatability)
    # Assuming delete endpoint exists
    client.delete(f"/organizations/{new_org_id}", headers=get_headers(ROOT_TOKEN))

def test_create_duplicate_organization_fails():
    """
    Verify duplicate ID creation returns 409.
    """
    # Ensure system exists (seed data)
    payload = {
        "id": "system",
        "name": "Duplicate Attempt",
        "tier": "enterprise"
    }
    response = client.post("/organizations/", json=payload, headers=get_headers(ROOT_TOKEN))
    assert response.status_code == 409 

def test_member_cannot_create_organization():
    """
    Verify MEMBER role cannot create organizations.
    """
    payload = {
        "id": "member-hack",
        "name": "Hacked Org",
        "tier": "standard"
    }
    response = client.post("/organizations/", json=payload, headers=get_headers(MEMBER_TOKEN))
    assert response.status_code == 403

def test_get_my_organization_admin():
    """
    Verify '/organizations/me' resolves correctly for an ADMIN.
    """
    response = client.get("/organizations/me", headers=get_headers(ADMIN_TOKEN))
    assert response.status_code == 200
    data = response.json()
    # admin_1 is typically seeded to 'org-1'
    assert data['id'] == 'org-1' 

def test_fetch_nonexistent_organization():
    """
    Verify 404 for unknown Org ID.
    """
    response = client.get("/organizations/non-existent-12345", headers=get_headers(ROOT_TOKEN))
    assert response.status_code == 404

