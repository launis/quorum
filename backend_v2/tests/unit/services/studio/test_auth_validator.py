"""Unit tests for Studio Authorization Validator."""

from __future__ import annotations

import pytest

from backend_v2.exceptions import PermissionDeniedError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.enums import EntityPrefix
from backend_v2.services.studio.auth_validator import (
    enforce_modification_rights,
    enforce_tenant_isolation,
    is_resource_accessible,
)

ORG_ALPHA_ID = generate_opaque_id(EntityPrefix.ORGANIZATION)
ORG_BETA_ID = generate_opaque_id(EntityPrefix.ORGANIZATION)
WORKFLOW_ID = generate_opaque_id(EntityPrefix.WORKFLOW)


@pytest.fixture
def root_token() -> TokenData:
    """Create a ROOT user token fixture.

    Returns:
        TokenData for a ROOT user.
    """
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        organization_id=SystemOrganizations.ROOT_SYSTEM,
        email="root@example.com",
        role=UserRole.ROOT,
    )


@pytest.fixture
def admin_token() -> TokenData:
    """Create an ADMIN user token fixture.

    Returns:
        TokenData for an ADMIN user in ORG_ALPHA_ID.
    """
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        organization_id=ORG_ALPHA_ID,
        email="admin@example.com",
        role=UserRole.ADMIN,
    )


@pytest.fixture
def manager_token() -> TokenData:
    """Create a MANAGER user token fixture.

    Returns:
        TokenData for a MANAGER user in ORG_ALPHA_ID.
    """
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        organization_id=ORG_ALPHA_ID,
        email="manager@example.com",
        role=UserRole.MANAGER,
    )


@pytest.fixture
def member_token() -> TokenData:
    """Create a MEMBER user token fixture.

    Returns:
        TokenData for a MEMBER user in ORG_ALPHA_ID.
    """
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        organization_id=ORG_ALPHA_ID,
        email="member@example.com",
        role=UserRole.MEMBER,
    )


@pytest.fixture
def user_token() -> TokenData:
    """Create a VIEWER user token fixture.

    Returns:
        TokenData for a VIEWER user in ORG_ALPHA_ID.
    """
    return TokenData(
        id=generate_opaque_id(EntityPrefix.USER),
        organization_id=ORG_ALPHA_ID,
        email="viewer@example.com",
        role=UserRole.VIEWER,
    )


def test_enforce_tenant_isolation_root_allowed(root_token: TokenData) -> None:
    """Verify ROOT user can access resources across any organization."""
    enforce_tenant_isolation(root_token, ORG_BETA_ID, "workflow", WORKFLOW_ID)


def test_enforce_tenant_isolation_same_org_allowed(admin_token: TokenData) -> None:
    """Verify user can access resources within their own organization."""
    enforce_tenant_isolation(admin_token, ORG_ALPHA_ID, "workflow", WORKFLOW_ID)


def test_enforce_tenant_isolation_system_allowed_by_default(admin_token: TokenData) -> None:
    """Verify system organization resources are accessible by default."""
    enforce_tenant_isolation(admin_token, SystemOrganizations.ROOT_SYSTEM, "workflow", WORKFLOW_ID)
    enforce_tenant_isolation(admin_token, SystemOrganizations.LEGACY_SYSTEM, "workflow", WORKFLOW_ID)
    enforce_tenant_isolation(admin_token, None, "workflow", WORKFLOW_ID)


def test_enforce_tenant_isolation_system_denied_when_disabled(admin_token: TokenData) -> None:
    """Verify system organization resources are denied when allow_system is False."""
    with pytest.raises(PermissionDeniedError):
        enforce_tenant_isolation(
            admin_token,
            SystemOrganizations.ROOT_SYSTEM,
            "workflow",
            WORKFLOW_ID,
            allow_system=False,
        )


def test_enforce_tenant_isolation_public_allowed(admin_token: TokenData) -> None:
    """Verify public resources are accessible across organizations."""
    enforce_tenant_isolation(admin_token, ORG_BETA_ID, "workflow", WORKFLOW_ID, is_public=True)


def test_enforce_tenant_isolation_other_org_denied(admin_token: TokenData) -> None:
    """Verify non-ROOT user cannot access private resources of another organization."""
    with pytest.raises(PermissionDeniedError):
        enforce_tenant_isolation(admin_token, ORG_BETA_ID, "workflow", WORKFLOW_ID)


def test_enforce_modification_rights_user_role_denied(user_token: TokenData, member_token: TokenData) -> None:
    """Verify VIEWER and MEMBER roles are denied modification rights."""
    with pytest.raises(PermissionDeniedError) as exc_info:
        enforce_modification_rights(user_token, ORG_ALPHA_ID)
    assert "Only ADMIN or MANAGER" in str(exc_info.value)

    with pytest.raises(PermissionDeniedError) as member_exc:
        enforce_modification_rights(member_token, ORG_ALPHA_ID)
    assert "Only ADMIN or MANAGER" in str(member_exc.value)


def test_enforce_modification_rights_root_can_modify_system(root_token: TokenData) -> None:
    """Verify ROOT role can modify system resources."""
    enforce_modification_rights(root_token, SystemOrganizations.ROOT_SYSTEM)


def test_enforce_modification_rights_manager_same_org_and_foreign_org(manager_token: TokenData) -> None:
    """Verify MANAGER can modify own organization resources but not foreign organization resources."""
    enforce_modification_rights(manager_token, ORG_ALPHA_ID)
    with pytest.raises(PermissionDeniedError) as exc_info:
        enforce_modification_rights(manager_token, ORG_BETA_ID)
    assert "Cannot modify resources outside your organization" in str(exc_info.value)


def test_enforce_modification_rights_admin_cannot_modify_system_without_allow_system(admin_token: TokenData) -> None:
    """Verify ADMIN cannot modify system resources when allow_system is False."""
    with pytest.raises(PermissionDeniedError) as exc_info:
        enforce_modification_rights(admin_token, SystemOrganizations.ROOT_SYSTEM, allow_system=False)
    assert "Only ROOT can modify system resources" in str(exc_info.value)


def test_enforce_modification_rights_admin_can_modify_system_with_allow_system(admin_token: TokenData) -> None:
    """Verify ADMIN can modify system resources when allow_system is True."""
    enforce_modification_rights(admin_token, SystemOrganizations.ROOT_SYSTEM, allow_system=True)


def test_enforce_modification_rights_admin_cannot_modify_other_org(admin_token: TokenData) -> None:
    """Verify ADMIN cannot modify resources belonging to another organization."""
    with pytest.raises(PermissionDeniedError) as exc_info:
        enforce_modification_rights(admin_token, ORG_BETA_ID)
    assert "Cannot modify resources outside your organization" in str(exc_info.value)


def test_is_resource_accessible_scenarios(root_token: TokenData, admin_token: TokenData, user_token: TokenData) -> None:
    """Verify boolean accessibility checks across role, system, public, and org boundaries."""
    # Root can access everything
    assert is_resource_accessible(root_token, ORG_BETA_ID) is True
    assert is_resource_accessible(root_token, None) is True

    # Public resources accessible to anyone
    assert is_resource_accessible(user_token, ORG_BETA_ID, is_public=True) is True

    # Same organization accessible
    assert is_resource_accessible(admin_token, ORG_ALPHA_ID) is True

    # System resources accessible by default
    assert is_resource_accessible(admin_token, SystemOrganizations.ROOT_SYSTEM) is True
    assert is_resource_accessible(admin_token, SystemOrganizations.LEGACY_SYSTEM) is True
    assert is_resource_accessible(admin_token, None) is True

    # System resources denied if allow_system=False
    assert is_resource_accessible(admin_token, None, allow_system=False) is False

    # Foreign organization denied
    assert is_resource_accessible(admin_token, ORG_BETA_ID) is False
