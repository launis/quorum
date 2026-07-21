from unittest.mock import AsyncMock
import pytest
from pydantic import ValidationError

from backend_v2.models.auth import Organization, User


def test_organization_fail_fast_on_corrupt_datetime() -> None:
    data = {"id": "org_1", "name": "Test", "created_at": "invalid_date_string"}
    with pytest.raises(ValidationError) as exc_info:
        Organization.model_validate(data)
    assert "invalid_date_string" in str(exc_info.value)


def test_organization_fail_fast_on_corrupt_subscription() -> None:
    data = {"id": "org_1", "name": "Test", "subscription_status": "LIFETIME_HACKER"}
    with pytest.raises(ValidationError) as exc_info:
        Organization.model_validate(data)
    assert "LIFETIME_HACKER" in str(exc_info.value)


def test_user_fail_fast_on_corrupt_datetime() -> None:
    data = {"id": "usr_1", "email": "a@b.com", "created_at": "30.02.2025"}
    with pytest.raises(ValidationError) as exc_info:
        User.model_validate(data)
    assert "30.02.2025" in str(exc_info.value)


def test_user_fail_fast_on_corrupt_role() -> None:
    data = {"id": "usr_1", "email": "a@b.com", "role": "SUPER_ADMIN_GOD"}
    with pytest.raises(ValidationError) as exc_info:
        User.model_validate(data)
    assert "SUPER_ADMIN_GOD" in str(exc_info.value)
