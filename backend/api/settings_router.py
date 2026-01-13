"""API Router for Global System Settings."""

import logging

from fastapi import APIRouter, HTTPException

from backend.dependencies import AuditServiceDep, AuthService, CurrentUserDep, EngineDep
from backend.models.auth import UserRole
from backend.models.settings import SystemSettings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["Global Settings"])


@router.get("", response_model=SystemSettings)
async def get_settings(engine: EngineDep):
    """Retrieves the current global system connection settings."""
    try:
        raw_settings = await engine.repository.get_system_settings()
        return SystemSettings(**raw_settings)
    except Exception:
        # If empty or error, return defaults
        return SystemSettings()


@router.patch("", response_model=SystemSettings)
async def update_settings(
    updates: SystemSettings,
    engine: EngineDep,
    current_user: CurrentUserDep,
    audit_service: AuditServiceDep,  # Injected
):
    """Updates global system settings.

    Requires ROOT.
    """
    # 1. Verify Permission
    AuthService.require_role(UserRole.ROOT)
    if current_user.role != UserRole.ROOT:
        error_code = "PERMISSION_DENIED_ROOT_ONLY"
        logger.error(f"{error_code}: User {current_user.uid} denied.", exc_info=True)
        raise HTTPException(status_code=403, detail=error_code)

    try:
        # 2. Persist
        data = updates.model_dump()
        await engine.repository.update_system_settings(data)

        # Audit
        if audit_service:
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
        error_code = "SETTINGS_UPDATE_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_code) from e
