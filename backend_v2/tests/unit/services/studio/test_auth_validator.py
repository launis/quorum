"""Unit tests for Studio Authorization Validator."""

import pytest

from backend_v2.exceptions import PermissionDeniedError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.services.studio.auth_validator import (
    enforce_modification_rights,
    enforce_tenant_isolation,
)


@pytest.fixture
def root_token() -> TokenData:
    return TokenData(
        id="usr_root",
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        email="root@example.com",
        role=UserRole.ROOT,
    )


@pytest.fixture
def admin_token() -> TokenData:
    return TokenData(
        id="usr_admin",
        organization_id="org_alpha",
        email="admin@example.com",
        role=UserRole.ADMIN,
    )


@pytest.fixture
def manager_token() -> TokenData:
    return TokenData(
        id="usr_manager",
        organization_id="org_alpha",
        email="manager@example.com",
        role=UserRole.MANAGER,
    )


@pytest.fixture
def user_token() -> TokenData:
    return TokenData(
        id="usr_viewer",
        organization_id="org_alpha",
        email="viewer@example.com",
        role=UserRole.VIEWER,
    )


def test_enforce_tenant_isolation_root_allowed(root_token: TokenData) -> None:
    enforce_tenant_isolation(root_token, "org_beta", "workflow", "wf_1")


def test_enforce_tenant_isolation_same_org_allowed(admin_token: TokenData) -> None:
    enforce_tenant_isolation(admin_token, "org_alpha", "workflow", "wf_1")


def test_enforce_tenant_isolation_system_allowed_by_default(admin_token: TokenData) -> None:
    enforce_tenant_isolation(admin_token, SystemOrganizations.ROOT_SYSTEM, "workflow", "wf_1")


def test_enforce_tenant_isolation_other_org_denied(admin_token: TokenData) -> None:
    with pytest.raises(PermissionDeniedError):
        enforce_tenant_isolation(admin_token, "org_beta", "workflow", "wf_1")


def test_enforce_modification_rights_user_role_denied(user_token: TokenData) -> None:
    with pytest.raises(PermissionDeniedError) as exc_info:
        enforce_modification_rights(user_token, "org_alpha")
    assert "Only ADMIN or MANAGER" in str(exc_info.value)


def test_enforce_modification_rights_root_can_modify_system(root_token: TokenData) -> None:
    enforce_modification_rights(root_token, SystemOrganizations.ROOT_SYSTEM)


def test_enforce_modification_rights_admin_cannot_modify_system_without_allow_system(admin_token: TokenData) -> None:
    with pytest.raises(PermissionDeniedError) as exc_info:
        enforce_modification_rights(admin_token, SystemOrganizations.ROOT_SYSTEM, allow_system=False)
    assert "Only ROOT can modify system resources" in str(exc_info.value)


def test_enforce_modification_rights_admin_can_modify_system_with_allow_system(admin_token: TokenData) -> None:
    enforce_modification_rights(admin_token, SystemOrganizations.ROOT_SYSTEM, allow_system=True)


def test_enforce_modification_rights_admin_cannot_modify_other_org(admin_token: TokenData) -> None:
    with pytest.raises(PermissionDeniedError) as exc_info:
        enforce_modification_rights(admin_token, "org_beta")
    assert "Cannot modify resources outside your organization" in str(exc_info.value)
