"""System router for exposing backend registry and configuration."""

from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend_v2.api.dependencies import get_current_admin_user
from backend_v2.core.hook_registry import hook_registry

router = APIRouter(prefix="/system", tags=["System"])


class HookListResponse(BaseModel):
    """Schema for returning available configured hooks."""

    hooks: list[str]


@router.get("/hooks", response_model=HookListResponse)
async def get_system_hooks(
    current_user: dict[str, Any] = Depends(get_current_admin_user),
) -> HookListResponse:
    """Get all registered hooks available for dynamic assignment.

    Requires admin privileges to view system internals.

    Returns:
        HookListResponse: List of all registered hook names.
    """
    available_hooks = hook_registry.get_all_hooks()
    return HookListResponse(hooks=sorted(available_hooks))
