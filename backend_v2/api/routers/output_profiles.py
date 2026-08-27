"""Router for Output Profiles (V2 BFF Architecture).

This router exposes CRUD operations for Output Profiles.
It strictly translates API dicts into OutputProfile models prior to service/repo engagement.
"""

import logging

from fastapi import APIRouter, status

from backend_v2.api.dependencies import CurrentUserDep, StudioOutputProfileServiceDep
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.output_profile import (
    OutputProfileCreateDTO,
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


@router.post("/", response_model=OutputProfileResponseDTO)
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
    profile_id: str,
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
) -> OutputProfile:
    """Get a specific Output Profile by its unique identifier.

    Args:
        profile_id: Unique Opaque Stripe ID of the profile.
        initiator: The current verified user executing the request.
        service: Injected StudioService for domain operations.

    Returns:
        The requested OutputProfile domain model.
    """
    profile = await service.get_output_profile(initiator=initiator, id=profile_id)
    return profile


@router.put("/{profile_id}", response_model=OutputProfileResponseDTO)
async def upsert_output_profile(
    profile_id: str,
    dto: OutputProfileCreateDTO,
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
) -> OutputProfile:
    """Create or Update an Output Profile.

    Validation automatically enforced by Pydantic. Validates that the path ID
    matches the payload ID before executing the save operation.

    Args:
        profile_id: Unique Opaque Stripe ID of the profile from the URL path.
        dto: The data transfer object containing the profile data.
        initiator: The current verified user executing the request.
        service: Injected StudioService for domain operations.

    Returns:
        The saved OutputProfile domain model.

    Raises:
        AppException: With error code ID_MISMATCH if the URL path ID does not match the payload ID.
    """
    # Domain conversion (hydrates DTO -> Domain with server-validated path ID)
    profile_dict = dto.model_dump()
    profile_dict["id"] = profile_id
    profile_data = OutputProfile.model_validate(profile_dict)

    # StudioService enforces Tenant boundaries and Repo interaction
    saved_profile = await service.save_output_profile(initiator=initiator, id=profile_id, data=profile_data)
    return saved_profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_output_profile(
    profile_id: str,
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
) -> None:
    """Delete an Output Profile.

    Args:
        profile_id: Unique Opaque Stripe ID of the profile to delete.
        initiator: The current verified user executing the request.
        service: Injected StudioService for domain operations.
    """
    await service.delete_output_profile(initiator=initiator, id=profile_id)


@router.post("/{profile_id}/clone", response_model=OutputProfileResponseDTO)
async def clone_output_profile(
    profile_id: str,
    initiator: CurrentUserDep,
    service: StudioOutputProfileServiceDep,
) -> OutputProfile:
    """Deep clone an Output Profile.

    Args:
        profile_id: Unique Opaque Stripe ID of the profile to clone.
        initiator: The current verified user executing the request.
        service: Injected StudioService for domain operations.

    Returns:
        The newly cloned OutputProfile domain model.
    """
    profile = await service.clone_output_profile(initiator=initiator, id=profile_id)
    return profile
