"""Router for Output Profiles (V2 BFF Architecture).

This router exposes CRUD operations for Output Profiles.
It strictly translates API dicts into OutputProfile models prior to service/repo engagement.
"""

import logging

from fastapi import APIRouter, Path, status

from backend_v2.api.dependencies import CurrentUserDep, StudioOutputProfileServiceDep
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.output_profile import (
    OutputProfileResponseDTO,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/output-profiles", tags=["Output Profiles"])


@router.get("/", response_model=list[OutputProfileResponseDTO])
async def list_output_profiles(
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
) -> list[OutputProfile]:
    """List all available Output Profiles.

    Tenant isolation handled safely by StudioService.

    Args:
        initiator: The current verified user executing the request.
        service: Injected StudioService for domain operations.

    Returns:
        A list of OutputProfile domain models.
    """
    profiles = await service.list_output_profiles(initiator=initiator)
    return list(profiles)


@router.post("/", response_model=OutputProfileResponseDTO, status_code=status.HTTP_201_CREATED)
async def create_output_profile(
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
) -> OutputProfile:
    """Create a new Output Profile draft securely via SSOT Service Layer.

    Args:
        initiator: The current verified user executing the request.
        service: Injected StudioService for domain operations.

    Returns:
        The newly created OutputProfile domain model.
    """
    return await service.create_output_profile_draft(initiator=initiator)


@router.get("/{profile_id}", response_model=OutputProfileResponseDTO)
async def get_output_profile(
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
    profile_id: str = Path(..., pattern=OPAQUE_STRIPE_ID_REGEX),
) -> OutputProfile:
    """Get a specific Output Profile by its unique identifier.

    Args:
        initiator: The current verified user executing the request.
        service: Injected StudioService for domain operations.
        profile_id: Unique Opaque Stripe ID of the profile.

    Returns:
        The requested OutputProfile domain model.

    Raises:
        AppException: If the profile is not found or tenant unauthorized.
    """
    profile = await service.get_output_profile(initiator=initiator, id=profile_id)
    return profile


@router.put("/{profile_id}", response_model=OutputProfileResponseDTO)
async def upsert_output_profile(
    data: OutputProfile,
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
    profile_id: str = Path(..., pattern=OPAQUE_STRIPE_ID_REGEX),
) -> OutputProfile:
    """Create or Update an Output Profile.

    Validation automatically enforced by Pydantic. Validates that the path ID
    matches the payload ID before executing the save operation.

    Args:
        data: The output profile domain model containing the full profile data.
        initiator: The current verified user executing the request.
        service: Injected StudioService for domain operations.
        profile_id: Unique Opaque Stripe ID of the profile from the URL path.

    Returns:
        The saved OutputProfile domain model.

    Raises:
        AppException: With error code ID_MISMATCH if the URL path ID does not match the payload ID.
    """
    if data.id != profile_id:
        logger.error(
            "[OutputProfilesRouter] %s: Path profile_id '%s' does not match payload id '%s' (Initiator: %s).",
            ErrorCodes.ID_MISMATCH.name,
            profile_id,
            data.id,
            initiator.id,
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
    profile_id: str = Path(..., pattern=OPAQUE_STRIPE_ID_REGEX),
) -> None:
    """Delete an Output Profile.

    Args:
        initiator: The current verified user executing the request.
        service: Injected StudioService for domain operations.
        profile_id: Unique Opaque Stripe ID of the profile to delete.
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
    profile_id: str = Path(..., pattern=OPAQUE_STRIPE_ID_REGEX),
) -> OutputProfile:
    """Deep clone an Output Profile.

    Args:
        initiator: The current verified user executing the request.
        service: Injected StudioService for domain operations.
        profile_id: Unique Opaque Stripe ID of the profile to clone.

    Returns:
        The newly cloned OutputProfile domain model.
    """
    return await service.clone_output_profile(initiator=initiator, id=profile_id)
