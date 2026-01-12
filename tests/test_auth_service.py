"""Tests for AuthService."""

import os
import shutil
import tempfile

import pytest

from backend.database.wrapper import TinyDBClient
from backend.models.auth import User, UserRole
from backend.services.auth import AuthService


@pytest.fixture
def auth_service():
    """Create a fresh AuthService with a temporary DB file."""
    # Create temp dir
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, "test_db.json")

    db = TinyDBClient(path=temp_db_path)
    service = AuthService(db_client=db)

    yield service

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.asyncio
async def test_get_users_by_organization(auth_service):
    """Test retrieving users by organization ID."""
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
    uids_1 = [u.uid for u in users_org_1]
    assert "u1" in uids_1
    assert "u2" in uids_1

    # Test Org 2
    users_org_2 = await auth_service.get_users_by_organization(org_id_2)
    assert len(users_org_2) == 1
    assert users_org_2[0].uid == "u3"

    # Test Non-existent Org
    users_none = await auth_service.get_users_by_organization("non_existent")
    assert users_none == []
