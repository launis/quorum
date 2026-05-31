import logging

from fastapi import APIRouter, Depends

from backend_v2.api.dependencies import get_current_admin_user
from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.system import HookListResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system", tags=["System"])


@router.get(
    "/hooks",
    response_model=HookListResponse,
    dependencies=[Depends(get_current_admin_user)],
)
async def get_system_hooks() -> HookListResponse:
    """Retrieves all registered system hooks.

    This endpoint returns a sorted list of all hook names currently registered
    within the system's hook registry. Requires admin privileges.

    Returns:
        An object containing a sorted list of all registered hook names.

    Raises:
        AppException: With error code `INTERNAL_SERVER_ERROR` if an unexpected
                      internal system failure occurs.
    """
    try:
        available_hooks = hook_registry.get_all_hooks()
        hooks = sorted(list(available_hooks))
        return HookListResponse(hooks=hooks)
    except AppException:
        # Re-raise known application exceptions directly to the client.
        raise
    except Exception as e:
        logger.error(
            "[SystemRouter] Unhandled exception during hook retrieval: %s",
            e,
            exc_info=True,
        )
        # Rule 18: Translate unexpected errors into a structured AppException.
        raise AppException(ErrorCodes.INTERNAL_SERVER_ERROR) from e
