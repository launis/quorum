import pytest
from datetime import datetime, timezone
from backend.models.auth import UserAdminView, UserRole

def test_user_admin_view_instantiation_dict_datetime():
    """Test creating UserAdminView from dict with datetime objects."""
    now = datetime.now(timezone.utc)
    data = {
        "uid": "test_uid",
        "email": "test@example.com",
        "role": UserRole.ADMIN,
        "created_at": now,
        "last_login_at": now,
        "execution_count": 5
    }
    user = UserAdminView(**data)
    assert user.uid == "test_uid"
    assert user.created_at == now
    assert user.last_login_at == now
    assert user.execution_count == 5
    assert user.role == UserRole.ADMIN

def test_user_admin_view_instantiation_dict_string():
    """Test creating UserAdminView from dict with ISO strings (auto-parsing)."""
    now = datetime.now(timezone.utc)
    iso_now = now.isoformat()
    data = {
        "uid": "test_uid",
        "email": "test@example.com",
        "role": UserRole.MEMBER,
        "created_at": iso_now,
        "last_login_at": iso_now,
        "execution_count": 10
    }
    user = UserAdminView(**data)
    assert user.uid == "test_uid"
    assert isinstance(user.created_at, datetime)
    assert user.created_at == now
    assert isinstance(user.last_login_at, datetime)
    assert user.execution_count == 10

def test_user_admin_view_from_attributes():
    """Test creating UserAdminView from an object (ORM-like behavior)."""
    class MockORMUser:
        def __init__(self):
            self.uid = "orm_uid"
            self.email = "orm@example.com"
            self.role = "MANAGER"
            self.created_at = datetime.now(timezone.utc)
            self.last_login_at = datetime.now(timezone.utc)
            self.execution_count = 42
            self.is_active = True
            self.language = "en"
            self.theme_mode = "dark"
            self.display_name = "ORM User"
            self.organization_id = "org_1"
            self.created_by = "admin_1"

    mock_obj = MockORMUser()
    user = UserAdminView.model_validate(mock_obj)
    
    assert user.uid == "orm_uid"
    assert user.email == "orm@example.com"
    assert user.role == UserRole.MANAGER
    assert isinstance(user.created_at, datetime)
    assert user.created_at == mock_obj.created_at
    assert user.execution_count == 42
