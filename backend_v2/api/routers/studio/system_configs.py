"""Admin Studio System Configs API Router.

Provides the router factory, identifier validation, and configuration boundary
for Studio system configurations.
"""

import logging
import re
from typing import Final

from fastapi import APIRouter, status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX
from backend_v2.models.enums import EntityPrefix

logger = logging.getLogger(__name__)

__all__ = [
    "SYSTEM_CONFIGS_PREFIX",
    "SYSTEM_CONFIGS_TAG",
    "build_system_config_router",
    "router",
    "validate_system_config_id",
]

SYSTEM_CONFIGS_PREFIX: Final[str] = "/system-configs"
SYSTEM_CONFIGS_TAG: Final[str] = "Admin Studio V2 - System Configs"
_ROUTER_PREFIX_PATTERN: Final[re.Pattern[str]] = re.compile(r"^/[a-z0-9-]+$")
_OPAQUE_ID_PATTERN: Final[re.Pattern[str]] = re.compile(OPAQUE_STRIPE_ID_REGEX)


def validate_system_config_id(config_id: str) -> str:
    """Validate that a system configuration identifier matches the canonical Opaque Stripe ID contract.

    Args:
        config_id: Candidate Opaque Stripe ID string to validate.

    Returns:
        The validated system configuration identifier string.

    Raises:
        AppException: With `ErrorCodes.VALIDATION_FAILED` if `config_id` does not match
            `OPAQUE_STRIPE_ID_REGEX` or does not carry the `EntityPrefix.SYSTEM_CONFIG` prefix.
    """
    match = _OPAQUE_ID_PATTERN.match(config_id)
    if match is None or match.group(1) != EntityPrefix.SYSTEM_CONFIG.value:
        logger.error(
            "[SystemConfigsRouter] %s: Invalid system config ID '%s'; expected prefix '%s_' and canonical hex format.",
            ErrorCodes.VALIDATION_FAILED.name,
            config_id,
            EntityPrefix.SYSTEM_CONFIG.value,
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
        raise AppException(
            message=(
                f"Invalid system config identifier '{config_id}'; must match canonical "
                f"'{EntityPrefix.SYSTEM_CONFIG.value}_' Opaque Stripe ID format."
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    return config_id


def build_system_config_router(
    prefix: str = SYSTEM_CONFIGS_PREFIX,
    tag: str = SYSTEM_CONFIGS_TAG,
) -> APIRouter:
    """Validate router metadata and construct the Studio System Configs APIRouter.

    Args:
        prefix: Canonical router path prefix starting with `/` and lowercase kebab-case segments.
        tag: Non-empty OpenAPI tag label for the router.

    Returns:
        Configured FastAPI `APIRouter` instance.

    Raises:
        AppException: With `ErrorCodes.VALIDATION_FAILED` if `prefix` fails route pattern validation
            or if `tag` is empty or whitespace-only.
    """
    if _ROUTER_PREFIX_PATTERN.match(prefix) is None:
        logger.error(
            "[SystemConfigsRouter] %s: Invalid system configs router prefix '%s'.",
            ErrorCodes.VALIDATION_FAILED.name,
            prefix,
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
        raise AppException(
            message=f"Invalid system configs router prefix '{prefix}'; must match '^/[a-z0-9-]+$'.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    if not tag.strip():
        logger.error(
            "[SystemConfigsRouter] %s: System configs router tag must not be empty.",
            ErrorCodes.VALIDATION_FAILED.name,
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
        raise AppException(
            message="System configs router tag must not be empty.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    return APIRouter(prefix=prefix, tags=[tag])


router = build_system_config_router()
