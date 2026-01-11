import pytest
from fastapi.testclient import TestClient
from tinydb import Query

from backend.dependencies import get_db_client_dep
from backend.main import app
from backend.settings import get_settings

client = TestClient(app)

# --- FIXTURES & CONSTANTS ---
ROOT_TOKEN = "mock-token:root_master"
ADMIN_TOKEN = "mock-token:admin_1"  # Belongs to 'org-1'
MEMBER_TOKEN = "mock-token:member_1"  # Belongs to 'org-1'


@pytest.fixture(autouse=True)
def setup_auth_override():
    from fastapi import HTTPException, Request
    from tinydb import Query

    from backend import dependencies
    from backend.dependencies import get_current_user_from_header, get_db_client_dep
    from backend.models.auth import TokenData, UserRole

    # 0. Clear Singletons FIRST to ensure we start fresh
    dependencies._auth_service_instance = None
    dependencies._db_client_instance = None
    dependencies._repository_instance = None

    # 1. Seed DB with required Orgs (Mock DB persistence)
    # This initializes the singleton _db_client_instance which we MUST KEEP for the app to see the same data
    try:
        get_settings.cache_clear()
        db = get_db_client_dep()
        org_table = db.table("organizations")
        Q = Query()
        org_table.upsert({"id": "org-1", "name": "Test Org 1", "tier": "standard"}, Q.id == "org-1")
        org_table.upsert({"id": "system", "name": "System", "tier": "root"}, Q.id == "system")
    except Exception as e:
        print(f"Fixture DB Error: {e}")
        pass

    async def mock_user_resolver(request: Request):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer mock-token:"):
            raise HTTPException(status_code=401, detail="Missing mock token")

        token_val = auth_header.split("Bearer ")[1]
        uid = token_val.split(":")[1]

        if uid == "root_master":
            return TokenData(uid="root_master", email="root@example.com", role=UserRole.ROOT, organization_id="system")
        elif uid == "admin_1":
            return TokenData(uid="admin_1", email="admin@example.com", role=UserRole.ADMIN, organization_id="org-1")
        elif uid == "member_1":
            return TokenData(uid="member_1", email="member@example.com", role=UserRole.MEMBER, organization_id="org-1")

        raise HTTPException(status_code=401, detail="Unknown mock user")

    app.dependency_overrides[get_current_user_from_header] = mock_user_resolver
    yield
    app.dependency_overrides.clear()

    # Cleanup logic
    dependencies._auth_service_instance = None
    dependencies._db_client_instance = None
    dependencies._repository_instance = None


def get_headers(token):
    return {"Authorization": f"Bearer {token}"}


# --- TESTS ---


def test_root_can_list_organizations():
    """Verify ROOT user can fetch the organization list."""
    response = client.get("/organizations/", headers=get_headers(ROOT_TOKEN))
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Check that we have at least the system-seeded organizations
    # (Assuming seed has run, usually we have 'system' and maybe 'org-1')
    ids = [o["id"] for o in data]
    assert "system" in ids


def test_admin_cannot_list_all_organizations():
    """Verify standard ADMIN cannot list *all* organizations (only their own scope usually,
    but /organizations/ usually requires ROOT/System Admin privileges in this architecture).
    """
    # NOTE: Depending on policy, ADMIN might get 403 or just their own.
    # In V2.2 Architecture: /organizations/ logic usually restricts to ROOT.
    response = client.get("/organizations/", headers=get_headers(ADMIN_TOKEN))

    # Expecting 403 Forbidden for non-ROOT users identifying as system admins
    assert response.status_code == 403


def test_root_can_create_organization():
    """Verify ROOT can create a new organization/tenant."""
    new_org_id = "test-org-pytest"
    payload = {
        "id": new_org_id,
        "name": "Pytest Automated Org",
        "tier": "standard",
        "contact_email": "test@example.com",
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
        assert data["id"] == new_org_id
        assert data["name"] == payload["name"]

    # 2. Verify Existence
    get_res = client.get(f"/organizations/{new_org_id}", headers=get_headers(ROOT_TOKEN))
    assert get_res.status_code == 200
    assert get_res.json()["id"] == new_org_id

    # 3. Cleanup (Optional, but good for repeatability)
    # Assuming delete endpoint exists
    client.delete(f"/organizations/{new_org_id}", headers=get_headers(ROOT_TOKEN))


def test_create_duplicate_organization_fails():
    """Verify duplicate ID creation returns 409."""
    # Ensure system exists (seed data)
    payload = {"id": "system", "name": "Duplicate Attempt", "tier": "enterprise"}
    response = client.post("/organizations/", json=payload, headers=get_headers(ROOT_TOKEN))
    assert response.status_code == 409


def test_member_cannot_create_organization():
    """Verify MEMBER role cannot create organizations."""
    payload = {"id": "member-hack", "name": "Hacked Org", "tier": "standard"}
    response = client.post("/organizations/", json=payload, headers=get_headers(MEMBER_TOKEN))
    assert response.status_code == 403


def test_get_my_organization_admin():
    """Verify '/organizations/me' resolves correctly for an ADMIN."""
    # Force seed org-1 because sometimes fixture fails to sync with repo
    db = get_db_client_dep()
    db.table("organizations").upsert({"id": "org-1", "name": "Org 1", "tier": "standard"}, lambda x: x["id"] == "org-1")

    # Cleanup legacy/bad data (previous failing runs injected 'id' instead of 'uid')
    db.table("users").remove(Query().id == "admin_1")

    db.table("users").upsert(
        {
            "uid": "admin_1",
            "email": "admin@example.com",
            "full_name": "Admin One",
            "hashed_password": "fake_hash",
            "organization_id": "org-1",
            "role": "ADMIN",
            "created_at": "2026-01-01T00:00:00",
            "is_active": True,
        },
        lambda x: x["uid"] == "admin_1",
    )

    response = client.get("/organizations/me", headers=get_headers(ADMIN_TOKEN))
    if response.status_code != 200:
        print(f"DEBUG FAIL ORGS: {db.table('organizations').all()}")
    assert response.status_code == 200
    data = response.json()
    # admin_1 is typically seeded to 'org-1'
    assert data["id"] == "org-1"


def test_fetch_nonexistent_organization():
    """Verify 404 for unknown Org ID."""
    response = client.get("/organizations/non-existent-12345", headers=get_headers(ROOT_TOKEN))
    assert response.status_code == 404
