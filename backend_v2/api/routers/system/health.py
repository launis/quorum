"""System Health API Router.

Provides endpoints to monitor system health and registry state.
"""

import logging
from typing import Literal

from fastapi import APIRouter, Depends, Request, status
from starlette.datastructures import State

from backend_v2.api.dependencies import get_current_admin_user
from backend_v2.core.hook_registry import hook_registry
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.system import HealthCheckResponseDTO, HookListResponse
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = [
    "get_system_health",
    "get_system_hooks",
    "router",
]

router = APIRouter(tags=["System"])


@router.get(
    "/health",
    response_model=HealthCheckResponseDTO,
)
async def get_system_health(request: Request) -> HealthCheckResponseDTO:
    """Evaluates in-memory lifespan readiness and returns Cloud Run health probe status.

    Args:
        request: Active HTTP request providing access to FastAPI application state.

    Returns:
        Typed HealthCheckResponseDTO reporting operational status and deployment metadata.

    Raises:
        AppException: With error code `INTERNAL_SERVER_ERROR` if an unexpected
            failure occurs during health evaluation, or re-raises any upstream `AppException`.
    """
    try:
        # Step 2: Evaluate O(1) in-memory readiness and resolve Settings SSOT metadata
        cfg = get_settings()
        is_ready = (
            isinstance(request.app.state, State)
            and "pool_manager" in request.app.state._state
            and request.app.state.pool_manager is not None
            and "arq_pool" in request.app.state._state
            and request.app.state.arq_pool is not None
        )
        health_status: Literal["ok", "degraded"] = "ok" if is_ready else "degraded"
        return HealthCheckResponseDTO(
            status=health_status,
            version=cfg.app_version,
            environment=cfg.environment,
            storage_backend=cfg.active_backend.value,
            gcp_region=cfg.gcp_region,
            primary_domain=cfg.primary_domain,
        )
    except AppException:
        raise
    except Exception as e:
        logger.error(
            "[SystemRouter] %s: Unhandled exception during system health check: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        )
        raise AppException(
            message="Failed to evaluate system health status.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e


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
            internal system failure occurs, or re-raises any upstream `AppException`.
    """
    try:
        available_hooks = hook_registry.get_all_hooks()
        hooks = sorted(available_hooks)
        return HookListResponse(hooks=hooks)
    except AppException:
        # Re-raise known application exceptions directly to the client.
        raise
    except Exception as e:
        logger.error(
            "[SystemRouter] %s: Unhandled exception during hook retrieval: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        )
        # Translate unexpected errors into a structured RFC 7807 AppException.
        raise AppException(
            message="Failed to retrieve registered system hooks.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e
