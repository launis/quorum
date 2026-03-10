import logging
from typing import Any

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, StudioServiceDep, LLMHandlerDep
from backend_v2.models.v2_core import SystemConfigModelRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/system-configs", tags=["Admin Studio V2 - System Configs"])

@router.get("/available-models", response_model=list[str])
def get_available_models(current_user: CurrentUserDep, llm_handler: LLMHandlerDep) -> list[str]:
    """Retrieve all available LLM models discovered by the LLM Handler."""
    if current_user.role != "ROOT" and current_user.role != "ADMIN":
        from backend_v2.exceptions import PermissionDeniedError
        raise PermissionDeniedError("Only ROOT or ADMIN can fetch available models.")
    result = llm_handler.fetch_all_available_models()
    
    # Flatten dict[str, list[str] | str] into list[str]
    flat_list: list[str] = []
    for models in result.values():
        if isinstance(models, list):
            flat_list.extend(models)
        elif isinstance(models, str):
            flat_list.append(models)
            
    return sorted(list(set(flat_list)))

@router.get("/", response_model=list[SystemConfigModelRegistry])
async def get_all_system_configs(current_user: CurrentUserDep, studio_service: StudioServiceDep) -> list[SystemConfigModelRegistry]:
    """Retrieve all global system configurations securely via SSOT Service Layer."""
    return await studio_service.list_system_configs(current_user)

@router.get("/{id}", response_model=SystemConfigModelRegistry)
async def get_system_config(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> SystemConfigModelRegistry:
    """Retrieve a specific application state configuration securely via SSOT Service Layer."""
    return await studio_service.get_system_config(current_user, id)

@router.put("/{id}", response_model=SystemConfigModelRegistry)
async def save_system_config(id: str, data: SystemConfigModelRegistry, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> SystemConfigModelRegistry:
    """Update a global system configuration securely via SSOT Service Layer."""
    return await studio_service.save_system_config(current_user, id, data)

@router.delete("/{id}")
async def delete_system_config(id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep) -> dict[str, Any]:
    """Delete a global system configuration securely via SSOT Service Layer."""
    await studio_service.delete_system_config(current_user, id)
    return {"status": "success", "deleted_id": id}
