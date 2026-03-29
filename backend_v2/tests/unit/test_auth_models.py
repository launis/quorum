from typing import Any
import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.auth import Organization, User


def test_organization_fail_fast_on_corrupt_datetime() -> None:
    data = {"id": "org_1", "name": "Test", "created_at": "invalid_date_string"}
    with pytest.raises(AppException) as exc_info:
        Organization.model_validate(data)
    assert "Invalid datetime 'invalid_date_string'" in exc_info.value.message


def test_organization_fail_fast_on_corrupt_subscription() -> None:
    data = {"id": "org_1", "name": "Test", "subscription_status": "LIFETIME_HACKER"}
    with pytest.raises(AppException) as exc_info:
        Organization.model_validate(data)
    assert "Invalid subscription status 'LIFETIME_HACKER'" in exc_info.value.message


def test_user_fail_fast_on_corrupt_datetime() -> None:
    data = {"id": "usr_1", "email": "a@b.com", "created_at": "30.02.2025"}
    with pytest.raises(AppException) as exc_info:
        User.model_validate(data)
    assert "Invalid datetime '30.02.2025'" in exc_info.value.message


def test_user_fail_fast_on_corrupt_role() -> None:
    data = {"id": "usr_1", "email": "a@b.com", "role": "SUPER_ADMIN_GOD"}
    with pytest.raises(AppException) as exc_info:
        User.model_validate(data)
    assert "Invalid role 'SUPER_ADMIN_GOD'" in exc_info.value.message
