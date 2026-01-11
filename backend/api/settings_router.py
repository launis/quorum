"""API Router for Global System Settings."""

from fastapi import APIRouter, HTTPException

from backend.dependencies import AuditServiceDep, AuthService, CurrentUserDep, EngineDep
from backend.models.auth import UserRole
from backend.models.settings import SystemSettings

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
    audit_service: AuditServiceDep = None,  # Injected
):
    """Updates global system settings.

    Requires ROOT.
    """
    # 1. Verify Permission
    AuthService.require_role(UserRole.ROOT)
    if current_user.role != UserRole.ROOT:
        raise HTTPException(status_code=403, detail="Only Root can change system settings.")

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
        import logging
        import traceback

        logger = logging.getLogger(__name__)
        logger.error(f"Settings Update Failed: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e)) from e
