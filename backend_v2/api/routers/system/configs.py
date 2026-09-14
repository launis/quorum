"""System router for exposing global configurations and enums."""

import logging

from fastapi import APIRouter

from backend_v2.models.dtos.system import StrictnessConfigDTO, StrictnessConfigListResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/configs", tags=["System Configs"])


@router.get("/strictness", response_model=StrictnessConfigListResponse)
async def get_strictness_configurations() -> StrictnessConfigListResponse:
    """Get the available strictness configurations and their localization keys.

    Returns:
        A list of strictness configurations wrapped in a StrictnessConfigListResponse.

    Raises:
        AppException: If fetching strictness configurations fails.
    """
    configs = [
        StrictnessConfigDTO(level=0, localization_key="strictnessFree"),
        StrictnessConfigDTO(level=50, localization_key="strictnessNormal"),
        StrictnessConfigDTO(level=85, localization_key="strictnessStrict"),
        StrictnessConfigDTO(level=100, localization_key="strictnessAbsolute"),
    ]

    return StrictnessConfigListResponse(configs=configs)
