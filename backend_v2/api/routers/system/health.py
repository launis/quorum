"""System router for exposing backend registry and configuration."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict

from backend_v2.api.dependencies import get_current_admin_user
from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.auth import TokenData

router = APIRouter(prefix="/system", tags=["System"])


class HookListResponse(BaseModel):
    """Schema for returning available configured hooks."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    hooks: list[str]


@router.get("/hooks", response_model=HookListResponse)
async def get_system_hooks(
    current_user: Annotated[TokenData, Depends(get_current_admin_user)],
) -> HookListResponse:
    """Get all registered hooks available for dynamic assignment.

    Requires admin privileges to view system internals.

    Returns:
        HookListResponse: List of all registered hook names.
    """
    try:
        import logging
        logger = logging.getLogger(__name__)
        available_hooks = hook_registry.get_all_hooks()
        return HookListResponse(hooks=sorted(available_hooks))
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        if isinstance(e, AppException):
            raise
        logger.error(
            "[SystemRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "error": str(e)},
        )
        raise AppException(
            message="Internal system failure fetching hooks",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e
