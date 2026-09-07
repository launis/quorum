"""Studio Authorization Validator.

Provides pure functions to enforce tenant isolation and modification rights.
"""

import logging

from backend_v2.exceptions import ErrorCodes, PermissionDeniedError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole

logger = logging.getLogger(__name__)


def is_resource_accessible(
    initiator: TokenData,
    data_org_id: str | None,
    *,
    allow_system: bool = True,
    is_public: bool = False,
) -> bool:
    """Check if a resource is accessible by initiator.

    Args:
        initiator: The user token data.
        data_org_id: The organization ID of the resource.
        allow_system: Whether system resources are accessible.
        is_public: Whether the resource is public.

    Returns:
        True if accessible, False otherwise.
    """
    if initiator.role == UserRole.ROOT or is_public:
        return True

    if allow_system and SystemOrganizations.is_system(data_org_id):
        return True

    return data_org_id == initiator.organization_id


def enforce_tenant_isolation(
    initiator: TokenData,
    data_org_id: str | None,
    resource_type: str,
    resource_id: str,
    allow_system: bool = True,
    is_public: bool = False,
) -> None:
    """Enforce tenant isolation for a resource.

    Args:
        initiator: The user token data.
        data_org_id: The organization ID of the resource.
        resource_type: The type of resource being accessed.
        resource_id: The ID of the resource being accessed.
        allow_system: Whether ROOT_SYSTEM is allowed access.
        is_public: Whether the resource is globally public.

    Raises:
        PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If the user does not have permission.
    """
    if is_resource_accessible(initiator, data_org_id, allow_system=allow_system, is_public=is_public):
        return

    logger.error(
        "[StudioService] %s: User %s attempted to access isolated %s %s.",
        ErrorCodes.PERMISSION_DENIED.name,
        initiator.id,
        resource_type,
        resource_id,
    )
    raise PermissionDeniedError(f"You do not have permission to view this {resource_type}.")


def enforce_modification_rights(
    initiator: TokenData,
    data_org_id: str | None,
    allow_system: bool = False,
) -> None:
    """Enforce modification rights for a resource.

    Args:
        initiator: The user token data.
        data_org_id: The organization ID of the resource.
        allow_system: Whether ROOT_SYSTEM is allowed to be modified by non-root users.

    Raises:
        PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If the user does not have permission.
    """
    if initiator.role not in [UserRole.ROOT, UserRole.ADMIN, UserRole.MANAGER]:
        logger.error(
            "[StudioService] %s: User %s (Role: %s) denied. Only ADMIN or MANAGER can modify resources.",
            ErrorCodes.PERMISSION_DENIED.name,
            initiator.id,
            initiator.role.name,
        )
        raise PermissionDeniedError("Only ADMIN or MANAGER can modify resources.")

    org_id = initiator.organization_id
    if initiator.role != UserRole.ROOT:
        is_system = SystemOrganizations.is_system(data_org_id)
        if is_system and not allow_system:
            logger.error(
                "[StudioService] %s: User %s denied. Only ROOT can modify system resources.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
            )
            raise PermissionDeniedError("Only ROOT can modify system resources.")
        if data_org_id != org_id and not (is_system and allow_system):
            msg = "Cannot modify resources outside your organization."
            logger.error(
                "[StudioService] %s: %s User %s org_id=%s data_org_id=%s",
                ErrorCodes.PERMISSION_DENIED.name,
                msg,
                initiator.id,
                org_id,
                data_org_id,
            )
            raise PermissionDeniedError(msg)
