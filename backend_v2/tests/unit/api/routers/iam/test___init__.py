"""Aggregate unit tests for backend_v2/api/routers/iam/ package."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from backend_v2.models.auth import (
    SYSTEM_ROOT_USER_ID,
    Organization,
    SubscriptionStatus,
    TokenData,
    User,
    UserRole,
)
from backend_v2.models.enums import SystemLocale
from backend_v2.tests.unit import test_organizations as org_tests
from backend_v2.tests.unit import test_users as user_tests
from backend_v2.tests.unit.test_auth import (
    mock_repo as mock_repo,
)
from backend_v2.tests.unit.test_auth import (
    test_auth_router_exchange_logout_and_impersonate_flow as test_auth_router_exchange_logout_and_impersonate_flow,
)
from backend_v2.tests.unit.test_auth import (
    test_auth_router_get_my_profile as test_auth_router_get_my_profile,
)
from backend_v2.tests.unit.test_auth import (
    test_auth_router_impersonate_and_profile_negative as test_auth_router_impersonate_and_profile_negative,
)
from backend_v2.tests.unit.test_auth import (
    test_auth_router_list_roles as test_auth_router_list_roles,
)


def test_init_import() -> None:
    """Test that the IAM router package imports successfully."""
    import backend_v2.api.routers.iam

    assert backend_v2.api.routers.iam is not None


@pytest.mark.asyncio
async def test_iam_users_and_organizations_routers_coverage_and_error_branches_negative() -> None:
    """Execute positive and negative unit test partitions for users.py and organizations.py routers."""
    admin_token = TokenData(id=user_tests.ADMIN_ID, role=UserRole.ADMIN, organization_id=user_tests.ORG_ID)
    root_token = TokenData(id=SYSTEM_ROOT_USER_ID, role=UserRole.ROOT)
    sample_user = User(
        id=user_tests.TARGET_ID,
        email="member@test.com",
        role=UserRole.MEMBER,
        is_active=True,
        organization_id=user_tests.ORG_ID,
        language=SystemLocale.EN,
        theme_mode="system",
        created_at=datetime.now(timezone.utc),
    )
    sample_org = Organization(
        id=org_tests.ORG_ID,
        name="Tenant Org",
        is_active=True,
        tier="standard",
        subscription_status=SubscriptionStatus.ACTIVE,
        quota_limit=100.0,
        tpm_limit=50000,
        rpm_limit=100,
        created_at=datetime.now(timezone.utc),
        allowed_email_domains=[],
    )

    await user_tests.test_users_router_crud_positive(admin_token, AsyncMock(), sample_user)
    await user_tests.test_users_router_propagates_permission_denied_and_not_found_negative(admin_token, AsyncMock())
    await user_tests.test_users_router_delete_error_branches_negative(admin_token, AsyncMock())

    await org_tests.test_organizations_router_crud_positive(root_token, AsyncMock(), sample_org)
    await org_tests.test_organizations_router_propagates_permission_denied_and_not_found_negative(
        root_token, AsyncMock()
    )
    await org_tests.test_organizations_router_delete_error_branches_negative(root_token, AsyncMock())
