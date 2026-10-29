"""Router for Output Profiles (V2 BFF Architecture).

This router exposes CRUD and clone operations for Output Profiles,
enforcing strict Pydantic V2 domain and DTO validation at the HTTP boundary.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Path, status

from backend_v2.api.dependencies import CurrentUserDep, StudioOutputProfileServiceDep
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.output_profile import (
    OutputProfileResponseDTO,
)

logger = logging.getLogger(__name__)

__all__ = ["router"]

router = APIRouter(prefix="/output-profiles", tags=["Output Profiles"])


@router.get("/", response_model=list[OutputProfileResponseDTO])
async def list_output_profiles(
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
) -> list[OutputProfile]:
    """List all available Output Profiles accessible to the authenticated tenant.

    Args:
        initiator: The current verified user executing the request.
        service: Injected StudioOutputProfileService for domain operations.

    Returns:
        A list of OutputProfile domain models.

    Raises:
        AppException: With ErrorCodes.STATE_INTEGRITY_ERROR if persisted profile data fails validation.
    """
    profiles = await service.list_output_profiles(initiator=initiator)
    return list(profiles)


@router.post("/", response_model=OutputProfileResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_output_profile(
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
) -> OutputProfile:
    """Create a new Output Profile draft securely via the SSOT Service Layer.

    Args:
        initiator: The current verified user executing the request.
        service: Injected StudioOutputProfileService for domain operations.

    Returns:
        The newly created OutputProfile domain model.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if no workflow exists to bind the draft.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant modification rights are violated.
        AppException: With ErrorCodes.VALIDATION_FAILED if draft layout target validation fails.
    """
    return await service.create_output_profile_draft(initiator=initiator)


@router.get("/{profile_id}", response_model=OutputProfileResponseDTO)
async def get_output_profile(
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
    profile_id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
) -> OutputProfile:
    """Get a specific Output Profile by its unique Opaque Stripe ID.

    Args:
        initiator: The current verified user executing the request.
        service: Injected StudioOutputProfileService for domain operations.
        profile_id: Unique Opaque Stripe ID of the profile.

    Returns:
        The requested OutputProfile domain model.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the profile does not exist.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant isolation is violated.
    """
    profile = await service.get_output_profile(initiator=initiator, id=profile_id)
    return profile


@router.put("/{profile_id}", response_model=OutputProfileResponseDTO)
async def upsert_output_profile(
    data: OutputProfile,
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
    profile_id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
) -> OutputProfile:
    """Create or update an Output Profile in-place under its authoritative ID.

    Validates that the URL path ID matches the payload ID before delegating to
    the service layer.

    Args:
        data: The OutputProfile domain model containing the full profile payload.
        initiator: The current verified user executing the request.
        service: Injected StudioOutputProfileService for domain operations.
        profile_id: Unique Opaque Stripe ID of the profile from the URL path.

    Returns:
        The saved OutputProfile domain model.

    Raises:
        AppException: With ErrorCodes.ID_MISMATCH if the URL path ID does not match the payload ID,
            or ErrorCodes.VALIDATION_FAILED if layout target validation fails.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the associated workflow or saved profile is missing.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant modification rights are violated.
    """
    if data.id != profile_id:
        logger.error(
            "[OutputProfilesRouter] %s: Path profile_id '%s' does not match payload id '%s' (Initiator: %s).",
            ErrorCodes.ID_MISMATCH.name,
            profile_id,
            data.id,
            initiator.id,
            exc_info=True,
            extra={"error_code": ErrorCodes.ID_MISMATCH.value, "profile_id": profile_id},
        )
        raise AppException(
            message=f"Path profile_id '{profile_id}' does not match payload id '{data.id}'",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.ID_MISMATCH.value},
        )

    saved_profile = await service.save_output_profile(initiator=initiator, id=profile_id, data=data)
    return saved_profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_output_profile(
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
    profile_id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
) -> None:
    """Delete an Output Profile by its unique Opaque Stripe ID.

    Args:
        initiator: The current verified user executing the request.
        service: Injected StudioOutputProfileService for domain operations.
        profile_id: Unique Opaque Stripe ID of the profile to delete.

    Returns:
        None.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the profile does not exist.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant modification rights are violated.
    """
    await service.delete_output_profile(initiator=initiator, id=profile_id)


@router.post(
    "/{profile_id}/clone",
    response_model=OutputProfileResponseDTO,
    status_code=status.HTTP_201_CREATED,
)
async def clone_output_profile(
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
    profile_id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
) -> OutputProfile:
    """Deep clone an existing Output Profile under a newly generated Opaque Stripe ID.

    Args:
        initiator: The current verified user executing the request.
        service: Injected StudioOutputProfileService for domain operations.
        profile_id: Unique Opaque Stripe ID of the source profile to clone.

    Returns:
        The newly cloned OutputProfile domain model.

    Raises:
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the source profile does not exist.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if tenant isolation is violated.
        AppException: With ErrorCodes.VALIDATION_FAILED if cloned layout target validation fails.
    """
    return await service.clone_output_profile(initiator=initiator, id=profile_id)
