"""System router for exposing global configurations and enums."""

import logging

from fastapi import APIRouter, status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.system import StrictnessConfigDTO, StrictnessConfigListResponse
from backend_v2.models.enums import StrictnessAnchor

logger = logging.getLogger(__name__)

__all__ = [
    "build_strictness_config",
    "get_strictness_configurations",
    "router",
]

router = APIRouter(prefix="/configs", tags=["System Configs"])


def build_strictness_config(level: int, localization_key: str) -> StrictnessConfigDTO:
    """Validate and construct a single strictness configuration DTO.

    Args:
        level: Numeric strictness level bounded by StrictnessAnchor extrema (0 to 100).
        localization_key: Non-empty UI localization key for translation.

    Returns:
        Validated StrictnessConfigDTO instance.

    Raises:
        AppException: With error code `VALIDATION_FAILED` if `level` is outside
            `[StrictnessAnchor.NONE, StrictnessAnchor.ABSOLUTE]` or `localization_key` is blank.
    """
    if level < StrictnessAnchor.NONE.value or level > StrictnessAnchor.ABSOLUTE.value:
        logger.error(
            "[ConfigsRouter] %s: Strictness level %d outside allowed range [%d, %d].",
            ErrorCodes.VALIDATION_FAILED.name,
            level,
            StrictnessAnchor.NONE.value,
            StrictnessAnchor.ABSOLUTE.value,
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
        raise AppException(
            message=(
                f"Strictness level {level} is outside allowed range "
                f"[{StrictnessAnchor.NONE.value}, {StrictnessAnchor.ABSOLUTE.value}]."
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    if not localization_key.strip():
        logger.error(
            "[ConfigsRouter] %s: Strictness localization_key must not be empty.",
            ErrorCodes.VALIDATION_FAILED.name,
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
        raise AppException(
            message="Strictness localization_key must not be empty.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    return StrictnessConfigDTO(level=level, localization_key=localization_key)


@router.get("/strictness", response_model=StrictnessConfigListResponse)
async def get_strictness_configurations() -> StrictnessConfigListResponse:
    """Get the available strictness configurations and their localization keys.

    Returns:
        A list of strictness configurations wrapped in a StrictnessConfigListResponse.

    Raises:
        AppException: With error code `VALIDATION_FAILED` if any strictness configuration
            violates domain bounds, or `INTERNAL_SERVER_ERROR` if an unexpected internal
            system failure occurs.
    """
    try:
        configs = [
            build_strictness_config(
                level=StrictnessAnchor.NONE.value,
                localization_key="strictnessFree",
            ),
            build_strictness_config(
                level=StrictnessAnchor.STANDARD.value,
                localization_key="strictnessNormal",
            ),
            build_strictness_config(
                level=StrictnessAnchor.STRICT.value,
                localization_key="strictnessStrict",
            ),
            build_strictness_config(
                level=StrictnessAnchor.ABSOLUTE.value,
                localization_key="strictnessAbsolute",
            ),
        ]
        return StrictnessConfigListResponse(configs=configs)
    except AppException:
        raise
    except Exception as e:
        logger.error(
            "[ConfigsRouter] %s: Unhandled exception during strictness configuration retrieval: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        )
        raise AppException(
            message="Failed to retrieve strictness configurations.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e
