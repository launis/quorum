"""Unit tests for authentication and identity models in backend_v2.models.auth."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.auth import Organization, SubscriptionStatus, User, UserRole
from backend_v2.models.enums import SystemLocale


def test_organization_fail_fast_on_corrupt_datetime() -> None:
    """Verify Organization rejects malformed ISO datetime strings."""
    data = {"id": "org_12345678", "name": "Test", "created_at": "invalid_date_string"}
    with pytest.raises(ValidationError) as exc_info:
        Organization.model_validate(data)
    assert "invalid_date_string" in str(exc_info.value)


def test_organization_fail_fast_on_corrupt_subscription() -> None:
    """Verify Organization rejects invalid subscription status values."""
    data = {"id": "org_12345678", "name": "Test", "subscription_status": "LIFETIME_HACKER"}
    with pytest.raises(ValidationError) as exc_info:
        Organization.model_validate(data)
    assert "LIFETIME_HACKER" in str(exc_info.value)


def test_organization_default_id_and_empty_name_validation() -> None:
    """Verify Organization generates an Opaque Stripe ID by default and rejects empty names."""
    org = Organization(
        name="Acme Corp",
        is_active=True,
        tier="enterprise",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=0.0,
        tpm_limit=1000,
        rpm_limit=1,
        created_at="2026-01-01T00:00:00Z",
    )
    assert org.id.startswith("org_")
    assert len(org.id) == 36

    with pytest.raises(ValidationError):
        Organization(
            id="org_12345678",
            name="   ",
            is_active=True,
            tier="enterprise",
            subscription_status=SubscriptionStatus.ACTIVE,
            quota_limit=10.0,
            tpm_limit=1000,
            rpm_limit=1,
        )


def test_user_fail_fast_on_corrupt_datetime() -> None:
    """Verify User rejects malformed ISO datetime strings."""
    data = {"id": "usr_12345678", "email": "a@b.com", "created_at": "30.02.2025"}
    with pytest.raises(ValidationError) as exc_info:
        User.model_validate(data)
    assert "30.02.2025" in str(exc_info.value)


def test_user_fail_fast_on_corrupt_role() -> None:
    """Verify User rejects unrecognized role enum values."""
    data = {"id": "usr_12345678", "email": "a@b.com", "role": "SUPER_ADMIN_GOD"}
    with pytest.raises(ValidationError) as exc_info:
        User.model_validate(data)
    assert "SUPER_ADMIN_GOD" in str(exc_info.value)


def test_user_default_id_and_validate_non_empty() -> None:
    """Verify User generates a default Opaque Stripe ID and enforces non-empty ID validation."""
    user = User(
        email="valid@example.com",
        role=UserRole.MEMBER,
        is_active=True,
        language=SystemLocale.EN,
        theme_mode="system",
        created_at="2026-01-01T00:00:00Z",
    )
    assert user.id.startswith("usr_")
    assert len(user.id) == 36

    with pytest.raises(ValueError, match="Field cannot be empty or whitespace only"):
        User.validate_non_empty("   ")
