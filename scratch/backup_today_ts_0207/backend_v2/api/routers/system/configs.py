"""System router for exposing global configurations and enums."""

import logging

from fastapi import APIRouter

from backend_v2.models.dtos.system import StrictnessConfigDTO, StrictnessConfigListResponse
from backend_v2.models.enums import StrictnessAnchor

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
        StrictnessConfigDTO(level=StrictnessAnchor.STRICT.value, localization_key="strictnessStrict"),
        StrictnessConfigDTO(level=StrictnessAnchor.ABSOLUTE.value, localization_key="strictnessAbsolute"),
    ]

    return StrictnessConfigListResponse(configs=configs)
