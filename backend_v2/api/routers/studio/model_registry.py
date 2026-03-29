import logging
from typing import Any

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, LLMHandlerDep, StudioServiceDep
from backend_v2.models.v2_core import SystemConfigModelRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/model-registry", tags=["Admin Studio V2 - Model Registry"])


@router.get("/available-models", response_model=list[str])
def get_available_models(current_user: CurrentUserDep, llm_handler: LLMHandlerDep) -> list[str]:
    """Retrieve all available LLM models discovered by the LLM Handler."""
    if current_user.role != "ROOT" and current_user.role != "ADMIN":
        from backend_v2.exceptions import ErrorCodes, PermissionDeniedError

        msg = (
            f"User {current_user.id} (Role: {current_user.role}) attempted to fetch "
            "available models without ROOT or ADMIN."
        )
        logger.error(f"[ModelRegistry] {ErrorCodes.PERMISSION_DENIED.name}: {msg}")
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
async def get_all_model_registries(
    current_user: CurrentUserDep, studio_service: StudioServiceDep
) -> list[SystemConfigModelRegistry]:
    """Retrieve all global model registry configurations securely via SSOT Service Layer."""
    # Temporarily, model registry relies on system_config collection
    return await studio_service.list_system_configs(current_user)


@router.get("/{registry_id}", response_model=SystemConfigModelRegistry)
async def get_model_registry(
    registry_id: str,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> SystemConfigModelRegistry:
    """Retrieve a single model registry configuration securely via SSOT Service Layer."""
    return await studio_service.get_system_config(current_user, registry_id)


@router.put("/{registry_id}", response_model=SystemConfigModelRegistry)
async def save_model_registry(
    registry_id: str,
    data: SystemConfigModelRegistry,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> SystemConfigModelRegistry:
    """Update a model registry configuration securely via SSOT Service Layer."""
    return await studio_service.save_system_config(current_user, registry_id, data)


@router.delete("/{registry_id}")
async def delete_model_registry(
    registry_id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep
) -> dict[str, Any]:
    """Delete a model registry configuration securely via SSOT Service Layer."""
    await studio_service.delete_system_config(current_user, registry_id)
    return {"status": "success", "deleted_id": registry_id}


@router.post("/{registry_id}/clone", response_model=SystemConfigModelRegistry)
async def clone_model_registry(
    registry_id: str,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> SystemConfigModelRegistry:
    """Deep clone a model registry configuration securely via SSOT Service Layer."""
    return await studio_service.clone_system_config(current_user, registry_id)
