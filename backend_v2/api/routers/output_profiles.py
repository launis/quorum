"""Router for Output Profiles (V2 BFF Architecture).

This router exposes CRUD operations for Output Profiles.
It strictly translates API dicts into OutputProfile models prior to service/repo engagement.
"""

import logging
from typing import Any

from fastapi import APIRouter, status

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep
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
) -> list[dict[str, Any]]:
    """List all available Output Profiles. Tenant isolation handled safely by StudioService."""
    profiles = await service.list_output_profiles(initiator=initiator)
    return [p.model_dump() for p in profiles]


@router.get("/{profile_id}", response_model=OutputProfileResponseDTO)
async def get_output_profile(
    profile_id: str,
    initiator: CurrentUserDep,
    service: StudioServiceDep,
) -> dict[str, Any]:
    """Get a specific Output Profile."""
    profile = await service.get_output_profile(initiator=initiator, id=profile_id)
    return profile.model_dump()


@router.put("/{profile_id}", response_model=OutputProfileResponseDTO)
async def upsert_output_profile(
    profile_id: str,
    dto: OutputProfileCreateDTO,
    initiator: CurrentUserDep,
    service: StudioServiceDep,
) -> dict[str, Any]:
    """Create or Update an Output Profile. Validation automatically enforced by Pydantic."""
    # Ensure ID match
    if dto.id != profile_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Path ID does not match Payload ID")

    # Domain conversion (hydrates DTO -> Domain)
    profile_data = OutputProfile(**dto.model_dump())

    # StudioService enforces Tenant boundaries and Repo interaction
    saved_profile = await service.save_output_profile(initiator=initiator, id=profile_id, data=profile_data)
    return saved_profile.model_dump()


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_output_profile(
    profile_id: str,
    initiator: CurrentUserDep,
    service: StudioServiceDep,
) -> None:
    """Delete an Output Profile."""
    await service.delete_output_profile(initiator=initiator, id=profile_id)
