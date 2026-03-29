"""Router for Output Profiles (V2 BFF Architecture).

This router exposes CRUD operations for Output Profiles.
It strictly translates API dicts into OutputProfile models prior to service/repo engagement.
"""

import logging

from fastapi import APIRouter, status

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep
from backend_v2.exceptions import AppException
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
    service: StudioServiceDep,
) -> list[OutputProfile]:
    """List all available Output Profiles. Tenant isolation handled safely by StudioService."""
    profiles = await service.list_output_profiles(initiator=initiator)
    return list(profiles)


@router.get("/{profile_id}", response_model=OutputProfileResponseDTO)
async def get_output_profile(
    profile_id: str,
    initiator: CurrentUserDep,
    service: StudioServiceDep,
) -> OutputProfile:
    """Get a specific Output Profile."""
    profile = await service.get_output_profile(initiator=initiator, id=profile_id)
    return profile


@router.put("/{profile_id}", response_model=OutputProfileResponseDTO)
async def upsert_output_profile(
    profile_id: str,
    dto: OutputProfileCreateDTO,
    initiator: CurrentUserDep,
    service: StudioServiceDep,
) -> OutputProfile:
    """Create or Update an Output Profile. Validation automatically enforced by Pydantic."""
    # Ensure ID match
    if dto.id != profile_id:
        msg = "Path ID does not match Payload ID"
        logger.error(
            "[OutputProfilesRouter] %s",
            msg,
            extra={
                "error_code": "ID_MISMATCH",
                "path_id": profile_id,
                "payload_id": dto.id,
            },
        )
        raise AppException(message=msg, status_code=400, details={"error_code": "ID_MISMATCH"})

    # Domain conversion (hydrates DTO -> Domain)
    profile_data = OutputProfile.model_validate(dto.model_dump())

    # StudioService enforces Tenant boundaries and Repo interaction
    saved_profile = await service.save_output_profile(initiator=initiator, id=profile_id, data=profile_data)
    return saved_profile


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_output_profile(
    profile_id: str,
    initiator: CurrentUserDep,
    service: StudioServiceDep,
) -> None:
    """Delete an Output Profile."""
    await service.delete_output_profile(initiator=initiator, id=profile_id)


@router.post("/{profile_id}/clone", response_model=OutputProfileResponseDTO)
async def clone_output_profile(
    profile_id: str,
    initiator: CurrentUserDep,
    service: StudioServiceDep,
) -> OutputProfile:
    """Deep clone an Output Profile."""
    profile = await service.clone_output_profile(initiator=initiator, id=profile_id)
    return profile
