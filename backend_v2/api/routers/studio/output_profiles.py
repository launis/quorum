"""Output Profiles Studio Router."""

import logging

from fastapi import APIRouter, Path, status

from backend_v2.api.dependencies import CurrentUserDep, StudioOutputProfileServiceDep
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.studio import OutputProfileListResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/profiles",
    tags=["Studio - Output Profiles"],
)


@router.get("", response_model=OutputProfileListResponse, status_code=status.HTTP_200_OK)
async def list_output_profiles(
    current_user: CurrentUserDep,
    studio_service: StudioOutputProfileServiceDep,
) -> OutputProfileListResponse:
    """List all OutputProfiles.

    Args:
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        A list of OutputProfiles.

    Raises:
        AppException: If listing the output profiles fails.
    """
    profiles = await studio_service.list_output_profiles(current_user)
    return OutputProfileListResponse(items=profiles)


@router.post("/draft", response_model=OutputProfile, status_code=status.HTTP_201_CREATED)
async def create_output_profile_draft(
    current_user: CurrentUserDep,
    studio_service: StudioOutputProfileServiceDep,
) -> OutputProfile:
    """Create a new OutputProfile draft.

    Args:
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The newly created OutputProfile draft.

    Raises:
        AppException: If creating the draft fails.
    """
    return await studio_service.create_output_profile_draft(current_user)


@router.get("/{profile_id}", response_model=OutputProfile, status_code=status.HTTP_200_OK)
async def get_output_profile(
    current_user: CurrentUserDep,
    studio_service: StudioOutputProfileServiceDep,
    profile_id: str = Path(..., pattern=r"^prof_[a-fA-F0-9]{16,32}$"),
) -> OutputProfile:
    """Get a specific OutputProfile.

    Args:
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.
        profile_id: The unique identifier of the output profile.

    Returns:
        The requested OutputProfile.

    Raises:
        ResourceNotFoundError: If the output profile is not found.
        AppException: If fetching the output profile fails.
    """
    return await studio_service.get_output_profile(current_user, profile_id)


@router.put("/{profile_id}", response_model=OutputProfile, status_code=status.HTTP_200_OK)
async def save_output_profile(
    data: OutputProfile,
    current_user: CurrentUserDep,
    studio_service: StudioOutputProfileServiceDep,
    profile_id: str = Path(..., pattern=r"^prof_[a-fA-F0-9]{16,32}$"),
) -> OutputProfile:
    """Update a specific OutputProfile.

    Args:
        data: The new output profile data.
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.
        profile_id: The unique identifier of the output profile.

    Returns:
        The updated OutputProfile.

    Raises:
        ResourceNotFoundError: If the output profile is not found.
        AppException: If updating the output profile fails.
    """
    return await studio_service.save_output_profile(current_user, profile_id, data)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_output_profile(
    current_user: CurrentUserDep,
    studio_service: StudioOutputProfileServiceDep,
    profile_id: str = Path(..., pattern=r"^prof_[a-fA-F0-9]{16,32}$"),
) -> None:
    """Delete a specific OutputProfile.

    Args:
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.
        profile_id: The unique identifier of the output profile.

    Raises:
        ResourceNotFoundError: If the output profile is not found.
        AppException: If deleting the output profile fails.
    """
    await studio_service.delete_output_profile(current_user, profile_id)


@router.post("/{profile_id}/clone", response_model=OutputProfile, status_code=status.HTTP_201_CREATED)
async def clone_output_profile(
    current_user: CurrentUserDep,
    studio_service: StudioOutputProfileServiceDep,
    profile_id: str = Path(..., pattern=r"^prof_[a-fA-F0-9]{16,32}$"),
) -> OutputProfile:
    """Clone an existing OutputProfile.

    Args:
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.
        profile_id: The unique identifier of the output profile to clone.

    Returns:
        The cloned OutputProfile.

    Raises:
        ResourceNotFoundError: If the source output profile is not found.
        AppException: If cloning the output profile fails.
    """
    return await studio_service.clone_output_profile(current_user, profile_id)
