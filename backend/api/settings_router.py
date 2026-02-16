"""API Router for Global System Settings."""

import logging

from fastapi import APIRouter

from backend.dependencies import AuditServiceDep, AuthService, CurrentUserDep, RepositoryDep
from backend.models.auth import UserRole
from backend.models.settings import SystemSettings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["Global Settings"])


@router.get("", response_model=SystemSettings)
async def get_settings(repo: RepositoryDep):
    """Retrieves the current global system connection settings."""
    # Fail Fast: If DB is down, strictly raise 500 (handled by global handler or let bubble).
    # Do NOT return defaults if the source of truth is unreachable.
    raw_settings = await repo.get_system_settings()
    if raw_settings is None:
        # If DB returns None (first run), return default model.
        # But if DB fails, it raises Exception.
        return SystemSettings()
    return SystemSettings(**raw_settings)


@router.patch("", response_model=SystemSettings)
async def update_settings(
    updates: SystemSettings,
    repo: RepositoryDep,
    current_user: CurrentUserDep,
    audit_service: AuditServiceDep,  # Injected
):
    """Updates global system settings.

    Requires ROOT.
    """
    # 1. Verify Permission
    AuthService.require_role(UserRole.ROOT)
    if current_user.role != UserRole.ROOT:
        from backend.exceptions import PermissionDeniedError

        error_code = "PERMISSION_DENIED_ROOT_ONLY"
        logger.error(f"{error_code}: User {current_user.uid} denied.", exc_info=True)
        raise PermissionDeniedError(message="ROOT access required", details={"error_code": error_code})

    try:
        # 2. Persist
        data = updates.model_dump()
        await repo.update_system_settings(data)

        # Audit
        # AuditServiceDep is strict, so no None check needed.
        await audit_service.log_event(
            actor_uid=current_user.uid,
            action="SETTINGS_UPDATED",
            organization_id="system",
            target_uid="global_settings",
            details=data,
        )

        # 3. Return Updated
        return updates
    except Exception as e:
        from backend.exceptions import AppException

        error_code = "SETTINGS_UPDATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message="Settings update failed",
            status_code=500,
            details={"error_code": error_code, "original_error": str(e)},
        ) from e
