"""System router for exposing global configurations and enums."""

import logging

from fastapi import APIRouter

from backend_v2.models.dtos.base import BaseDTO, BaseResponseDTO
from backend_v2.models.enums import StrictnessAnchor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/configs", tags=["System Configs"])


class StrictnessConfigDTO(BaseDTO):
    level: int
    localization_key: str


class StrictnessConfigListResponse(BaseResponseDTO):
    configs: list[StrictnessConfigDTO]


@router.get("/strictness", response_model=StrictnessConfigListResponse)
async def get_strictness_configurations() -> StrictnessConfigListResponse:
    """Get the available strictness configurations and their localization keys."""
    configs = [
        StrictnessConfigDTO(level=StrictnessAnchor.FLEXIBLE.value, localization_key="strictnessFullFlex"),
        StrictnessConfigDTO(level=StrictnessAnchor.LENIENT.value, localization_key="strictnessLenient"),
        StrictnessConfigDTO(level=StrictnessAnchor.BALANCED.value, localization_key="strictnessBalanced"),
        StrictnessConfigDTO(level=StrictnessAnchor.STRICT.value, localization_key="strictnessStrict"),
        StrictnessConfigDTO(level=StrictnessAnchor.ABSOLUTE.value, localization_key="strictnessAbsolute"),
    ]

    return StrictnessConfigListResponse(configs=configs)
