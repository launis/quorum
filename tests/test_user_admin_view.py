"""Tests for UserAdminView."""

from datetime import UTC, datetime

from backend.models.auth import UserAdminView, UserRole


def test_user_admin_view_instantiation_dict_datetime():
    """Test creating UserAdminView from dict with datetime objects."""
    now = datetime.now(UTC)
    data = {
        "uid": "test_uid",
        "email": "test@example.com",
        "role": "ADMIN",
        "organization_id": "test_org",
        "created_at": now,
        "last_login_at": now,
        "execution_count": 5,
    }

    user = UserAdminView(**data)

    assert user.uid == "test_uid"
    assert user.role == UserRole.ADMIN
    assert user.created_at == now
    assert user.last_login_at == now
    assert user.execution_count == 5


def test_user_admin_view_instantiation_dict_string():
    """Test creating UserAdminView from dict with ISO strings (auto-parsing)."""
    now = datetime.now(UTC)
    iso_now = now.isoformat()
    data = {
        "uid": "test_uid_2",
        "email": "test2@example.com",
        "role": "MEMBER",
        "organization_id": "test_org",
        "created_at": iso_now,
        "last_login_at": iso_now,
        "execution_count": 10,
    }

    user = UserAdminView(**data)

    # Pydantic should parse strings to datetime
    assert user.created_at == now
    assert user.last_login_at == now


def test_user_admin_view_from_orm():
    """Test creating UserAdminView using from_attributes (ORM mode)."""

    class MockORMUser:
        def __init__(self):
            self.uid = "orm_uid"
            self.email = "orm@example.com"
            self.role = "MANAGER"
            self.created_at = datetime.now(UTC)
            self.last_login_at = datetime.now(UTC)
            self.execution_count = 42
            self.is_active = True
            self.created_by = "creator"
            self.organization_id = "org_1"

    mock_obj = MockORMUser()
    user = UserAdminView.model_validate(mock_obj)

    assert user.uid == "orm_uid"
    assert user.email == "orm@example.com"
    assert user.role == UserRole.MANAGER
    assert user.execution_count == 42
    assert user.created_by == "creator"
