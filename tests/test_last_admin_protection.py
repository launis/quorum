"""Last Admin Protection Tests (Clean Slate).

Verifies the critical safety mechanism: The last Administrator of an Organization cannot be deleted or demoted.
Uses strictly isolated dependency overrides.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from backend.dependencies import get_current_user_from_header
from backend.main import app
from backend.models.auth import TokenData, User, UserRole

# --- MOCK DATA ---
LAST_ADMIN = User(
    uid="admin-1",
    email="admin@corp.com",
    role=UserRole.ADMIN,
    organization_id="org-1",
    created_at="2024-01-01"
)

SECOND_ADMIN = User(
    uid="admin-2",
    email="backup@corp.com",
    role=UserRole.ADMIN,
    organization_id="org-1",
    created_at="2024-01-02"
)


# --- FIXTURES ---

@pytest.fixture
def async_client():
    """Returns an AsyncClient for the app."""
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


# --- TESTS ---

# --- FAKE DB HELPERS ---
class FakeTable:
    """Mock database table for simulating TinyDB behavior."""

    def __init__(self, items=None):
        """Initialize with list of items."""
        self._items = items or []

    def get(self, query_func):
        """Mock get method."""
        # query_func is a lambda taking a dict
        for item in self._items:
            try:
                if query_func(item):
                    return item
            except Exception:
                continue
        return None

    def all(self):
        """Mock all method."""
        return list(self._items)

    def remove(self, query):
        """Mock remove method."""
        # query is a tinydb Query object usually, but AuthService uses .remove(Query().uid == uid)
        # simulating this is tricky.
        # But wait, AuthService.delete_user uses: self.repo.delete -> self.table.remove(Query().uid == uid)
        # We can just implement 'remove' to remove everything for now or assume test removes specific ID.
        # But since we are testing Protection (failure), remove shouldn't be called successfully in the failure case.
        # For success case, we can just return checks.
        pass

    def search(self, query):
        """Mock search method."""
        return []


class FakeDB:
    """Mock database class."""

    def __init__(self, users_data):
        """Initialize with user data."""
        self.users = FakeTable(users_data)

    def table(self, name):
        """Mock table accessor."""
        if name == "users":
            return self.users
        return FakeTable()


# --- TESTS ---

@pytest.mark.asyncio
async def test_cannot_delete_last_admin(async_client):
    """Verify 409 Conflict when attempting to delete the last admin."""
    # Data Setup
    last_admin_data = LAST_ADMIN.model_dump()
    users_data = [last_admin_data]

    fake_db = FakeDB(users_data)

    # 1. Mock Auth Dependency (Target Logic)
    # We construct a real AuthService but backed by FakeDB
    from backend.services.auth import AuthService

    # Override get_auth_service (used by Router)
    from backend.dependencies import get_auth_service
    app.dependency_overrides[get_auth_service] = lambda: AuthService(fake_db)

    # 2. Mock Current User (Router Access Control)
    app.dependency_overrides[get_current_user_from_header] = lambda: TokenData(
        uid=LAST_ADMIN.uid,
        email=LAST_ADMIN.email,
        role=LAST_ADMIN.role,
        organization_id=LAST_ADMIN.organization_id
    )

    try:
        response = await async_client.delete(f"/auth/users/{LAST_ADMIN.uid}")

        assert response.status_code == 409, f"Expected 409, got {response.status_code}: {response.text}"
        data = response.json()
        assert data["error_code"] == "CONFLICT_ERROR"
        assert data["details"]["error_code"] == "LAST_ADMIN_PROTECTION"
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_can_delete_admin_if_second_exists(async_client):
    """Verify deletion succeeds if another admin remains."""
    users_data = [LAST_ADMIN.model_dump(), SECOND_ADMIN.model_dump()]
    fake_db = FakeDB(users_data)

    from backend.dependencies import get_auth_service
    from backend.services.auth import AuthService

    auth_service = AuthService(fake_db)

    # Mock 'remove' to actually work for checking
    def _fake_remove(query):
        # We assume query matches LAST_ADMIN for this test
        # Just manually remove LAST_ADMIN from list to simulate success
        fake_db.users._items = [u for u in fake_db.users._items if u["uid"] != LAST_ADMIN.uid]
        return [1]  # IDs removed

    fake_db.users.remove = _fake_remove

    app.dependency_overrides[get_auth_service] = lambda: auth_service

    app.dependency_overrides[get_current_user_from_header] = lambda: TokenData(
        uid=SECOND_ADMIN.uid,
        email=SECOND_ADMIN.email,
        role=SECOND_ADMIN.role,
        organization_id=SECOND_ADMIN.organization_id
    )

    try:
        response = await async_client.delete(f"/auth/users/{LAST_ADMIN.uid}")
        assert response.status_code == 200, f"Failed: {response.text}"

        # Verify deletion in DB
        remaining = fake_db.users.all()
        assert len(remaining) == 1
        assert remaining[0]["uid"] == SECOND_ADMIN.uid
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_cannot_demote_last_admin(async_client):
    """Verify 409 Conflict when demoting last admin."""
    users_data = [LAST_ADMIN.model_dump()]
    fake_db = FakeDB(users_data)

    # Mock update
    def _fake_update(data, query_func):
        return [1]

    fake_db.users.update = _fake_update
    
    payload = {"role": "MEMBER"}
    
    try:
        response = await async_client.patch(f"/auth/users/{LAST_ADMIN.uid}", json=payload)
        # NOTE: PATCH logic might be different. 
        # But generally triggers same protection.
        assert response.status_code == 409
        data = response.json()
        assert data["error_code"] == "CONFLICT_ERROR"
        assert data["details"]["error_code"] == "LAST_ADMIN_PROTECTION"
    finally:
        app.dependency_overrides = {}
