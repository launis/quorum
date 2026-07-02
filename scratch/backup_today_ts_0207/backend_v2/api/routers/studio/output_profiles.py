"""Output Profiles Studio Router."""

import logging

from fastapi import APIRouter, Path, status
from pydantic import BaseModel, ConfigDict

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep
from backend_v2.models.domain.output_profile import OutputProfile

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/profiles",
    tags=["Studio - Output Profiles"],
)


class OutputProfileListResponse(BaseModel):
    """Response model for a list of OutputProfiles."""

    model_config = ConfigDict(extra="forbid")

    items: list[OutputProfile]


@router.get("", response_model=OutputProfileListResponse, status_code=status.HTTP_200_OK)
async def list_output_profiles(
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> OutputProfileListResponse:
    """List all OutputProfiles."""
    profiles = await studio_service.list_output_profiles(current_user)
    return OutputProfileListResponse(items=profiles)


@router.post("/draft", response_model=OutputProfile, status_code=status.HTTP_201_CREATED)
async def create_output_profile_draft(
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> OutputProfile:
    """Create a new OutputProfile draft."""
    return await studio_service.create_output_profile_draft(current_user)


@router.get("/{profile_id}", response_model=OutputProfile, status_code=status.HTTP_200_OK)
async def get_output_profile(
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
    profile_id: str = Path(..., pattern=r"^prof_[a-fA-F0-9]{16,32}$"),
) -> OutputProfile:
    """Get a specific OutputProfile."""
    return await studio_service.get_output_profile(current_user, profile_id)


@router.put("/{profile_id}", response_model=OutputProfile, status_code=status.HTTP_200_OK)
async def save_output_profile(
    data: OutputProfile,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
    profile_id: str = Path(..., pattern=r"^prof_[a-fA-F0-9]{16,32}$"),
) -> OutputProfile:
    """Update a specific OutputProfile."""
    return await studio_service.save_output_profile(current_user, profile_id, data)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_output_profile(
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
    profile_id: str = Path(..., pattern=r"^prof_[a-fA-F0-9]{16,32}$"),
) -> None:
    """Delete a specific OutputProfile."""
    await studio_service.delete_output_profile(current_user, profile_id)


@router.post("/{profile_id}/clone", response_model=OutputProfile, status_code=status.HTTP_201_CREATED)
async def clone_output_profile(
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
    profile_id: str = Path(..., pattern=r"^prof_[a-fA-F0-9]{16,32}$"),
) -> OutputProfile:
    """Clone an existing OutputProfile."""
    return await studio_service.clone_output_profile(current_user, profile_id)
