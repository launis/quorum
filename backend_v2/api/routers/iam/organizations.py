"""Organizations API Router.

Provides canonical SSOT endpoints for managing organizations, B2B invitations,
and tenant BYOK secrets securely under `/api/v2/iam/organizations`.
"""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from backend_v2.api.dependencies import AuthServiceDep, CurrentUserDep, require_role
from backend_v2.models.auth import (
    InvitationBatchCreateDTO,
    InvitationBatchResponseDTO,
    InvitationCreateDTO,
    InvitationResponseDTO,
    Organization,
    OrganizationCreate,
    OrganizationDeleteResponse,
    OrganizationUpdateDTO,
    TenantSecretCreateDTO,
    TenantSecretResponseDTO,
    TokenData,
)
from backend_v2.models.enums import UserRole
from backend_v2.services.auth.secret_service import SecretService, get_secret_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/organizations", tags=["Admin IAM V2 - Organizations"])

SecretServiceDep = Annotated[SecretService, Depends(get_secret_service)]
TenantAdminDep = Annotated[TokenData, Depends(require_role([UserRole.ROOT, UserRole.ADMIN]))]


@router.get("/", response_model=list[Organization])
async def get_all_organizations(current_user: CurrentUserDep, auth_service: AuthServiceDep) -> list[Organization]:
    """Retrieve all organizations securely evaluated by SSOT Service Layer.

    Args:
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        A list of organizations accessible by the user.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks privileges.
        AppException: If fetching organizations fails.
    """
    return await auth_service.list_organizations(current_user)


@router.get("/{org_id}/invitations", response_model=list[InvitationResponseDTO])
async def list_organization_invitations(
    org_id: str,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> list[InvitationResponseDTO]:
    """List B2B invitations for a specific organization.

    Args:
        org_id: Target organization identifier (org_<hex32>).
        current_user: Authenticated caller token data.
        auth_service: Injected AuthService dependency.

    Returns:
        List of redacted InvitationResponseDTO records.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller is not org ADMIN or ROOT.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if organization does not exist.
    """
    return await auth_service.org_service.list_invitations(current_user, org_id)


@router.post("/{org_id}/invitations", response_model=InvitationResponseDTO)
async def create_organization_invitation(
    org_id: str,
    payload: InvitationCreateDTO,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> InvitationResponseDTO:
    """Create a single cryptographic B2B organization invitation.

    Args:
        org_id: Target organization identifier (org_<hex32>).
        payload: Validated InvitationCreateDTO specifying recipient email and role.
        current_user: Authenticated caller token data.
        auth_service: Injected AuthService dependency.

    Returns:
        Redacted InvitationResponseDTO confirming creation and email delivery status.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks privileges or domain is disallowed.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if organization does not exist.
        ConflictError: With ErrorCodes.CONFLICT_ERROR if a pending invitation already exists.
    """
    return await auth_service.org_service.create_invitation(current_user, org_id, payload)


@router.post("/{org_id}/invitations/batch", response_model=InvitationBatchResponseDTO)
async def create_organization_invitation_batch(
    org_id: str,
    payload: InvitationBatchCreateDTO,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> InvitationBatchResponseDTO:
    """Create a batch of 1 to 500 cryptographic B2B organization invitations.

    Args:
        org_id: Target organization identifier (org_<hex32>).
        payload: Validated InvitationBatchCreateDTO specifying batch recipients.
        current_user: Authenticated caller token data.
        auth_service: Injected AuthService dependency.

    Returns:
        InvitationBatchResponseDTO with created count and invitation DTOs.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks privileges or domain is disallowed.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if organization does not exist.
        ConflictError: With ErrorCodes.CONFLICT_ERROR if any recipient has a pending invitation.
    """
    return await auth_service.org_service.create_invitation_batch(current_user, org_id, payload)


@router.delete("/{org_id}/invitations/{invitation_id}", response_model=InvitationResponseDTO)
async def revoke_organization_invitation(
    org_id: str,
    invitation_id: str,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> InvitationResponseDTO:
    """Revoke a pending B2B organization invitation.

    Args:
        org_id: Owning organization identifier (org_<hex32>).
        invitation_id: Target Invitation ID (inv_<hex32>).
        current_user: Authenticated caller token data.
        auth_service: Injected AuthService dependency.

    Returns:
        Updated InvitationResponseDTO with status='revoked'.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller lacks privileges.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if invitation does not exist.
    """
    return await auth_service.org_service.revoke_invitation(current_user, org_id, invitation_id)


@router.get("/{org_id}/secrets", response_model=list[TenantSecretResponseDTO])
async def list_organization_secrets(
    org_id: str,
    current_user: TenantAdminDep,
    secret_service: SecretServiceDep,
) -> list[TenantSecretResponseDTO]:
    """List redacted BYOK secret metadata records configured for an organization.

    Args:
        org_id: Target organization identifier (org_<hex32>).
        current_user: Authenticated ROOT or ADMIN user.
        secret_service: Injected SecretService dependency.

    Returns:
        List of redacted TenantSecretResponseDTO instances with masked_hint only.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller does not own org_id.
    """
    return await secret_service.list_tenant_secrets(initiator=current_user, organization_id=org_id)


@router.put("/{org_id}/secrets", response_model=TenantSecretResponseDTO)
async def upsert_organization_secret(
    org_id: str,
    payload: TenantSecretCreateDTO,
    current_user: TenantAdminDep,
    secret_service: SecretServiceDep,
) -> TenantSecretResponseDTO:
    """Provision or rotate a tenant-scoped BYOK secret for an organization.

    Args:
        org_id: Target organization identifier (org_<hex32>).
        payload: Validated TenantSecretCreateDTO containing the SecretStr credential.
        current_user: Authenticated ROOT or ADMIN user.
        secret_service: Injected SecretService dependency.

    Returns:
        Redacted TenantSecretResponseDTO confirming secret configuration and kek_version.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller does not own org_id.
        AppException: With ErrorCodes.VALIDATION_FAILED if payload is invalid.
        ConfigurationError: With ErrorCodes.SECRET_RESOLUTION_FAILED if KMS wrapping fails.
    """
    return await secret_service.upsert_tenant_secret(
        initiator=current_user,
        organization_id=org_id,
        payload=payload,
    )


@router.delete("/{org_id}/secrets/{secret_id}", response_model=OrganizationDeleteResponse)
async def delete_organization_secret(
    org_id: str,
    secret_id: str,
    current_user: TenantAdminDep,
    secret_service: SecretServiceDep,
) -> OrganizationDeleteResponse:
    """Delete a tenant-scoped BYOK secret from an organization.

    Args:
        org_id: Owning organization identifier (org_<hex32>).
        secret_id: Canonical tenant secret identifier (sec_<hex32>).
        current_user: Authenticated ROOT or ADMIN user.
        secret_service: Injected SecretService dependency.

    Returns:
        OrganizationDeleteResponse confirming deletion of secret_id.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller does not own org_id.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if secret_id does not exist in org_id.
    """
    await secret_service.delete_tenant_secret(
        initiator=current_user,
        organization_id=org_id,
        secret_id=secret_id,
    )
    return OrganizationDeleteResponse(status="success", deleted_id=secret_id)


@router.post("/", response_model=Organization)
async def create_organization(
    data: OrganizationCreate,
    current_user: CurrentUserDep,
    auth_service: AuthServiceDep,
) -> Organization:
    """Provision a new organization and its initial administrator via SSOT Service Layer.

    Args:
        data: Validated OrganizationCreate payload.
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        The newly created Organization.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if caller is not ROOT.
        AppException: If creating the organization fails.
    """
    return await auth_service.create_organization(current_user, data)


@router.get("/{id}", response_model=Organization)
async def get_organization(id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep) -> Organization:
    """Retrieve a specific organization securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the organization.
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        The requested organization.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the organization is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks permission to view it.
        AppException: If fetching the organization fails.
    """
    return await auth_service.get_organization(current_user, id)


@router.put("/{id}", response_model=Organization)
async def save_organization(
    id: str, data: OrganizationUpdateDTO, current_user: CurrentUserDep, auth_service: AuthServiceDep
) -> Organization:
    """Update an existing organization securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the organization.
        data: Validated OrganizationUpdateDTO payload.
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        The updated organization.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks permission.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the organization does not exist.
    """
    return await auth_service.update_organization(current_user, id, data)


@router.delete("/{id}", response_model=OrganizationDeleteResponse)
async def delete_organization(
    id: str, current_user: CurrentUserDep, auth_service: AuthServiceDep
) -> OrganizationDeleteResponse:
    """Delete an organization from the system securely via SSOT Service Layer.

    Args:
        id: The unique identifier of the organization to delete.
        current_user: The authenticated user making the request.
        auth_service: The authentication service dependency.

    Returns:
        An OrganizationDeleteResponse confirming deletion.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the organization is not found.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks permission.
        AppException: If deleting the organization fails.
    """
    await auth_service.delete_organization(current_user, id)
    return OrganizationDeleteResponse(status="success", deleted_id=id)
