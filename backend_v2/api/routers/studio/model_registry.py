import logging

from fastapi import APIRouter

from backend_v2.api.dependencies import CurrentUserDep, LLMHandlerDep, StudioServiceDep
from backend_v2.models.dtos.studio import ModelRegistryDeleteResponse
from backend_v2.models.v2_core import SystemConfigModelRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/model-registry", tags=["Admin Studio V2 - Model Registry"])


@router.get("/available-models", response_model=list[str])
def get_available_models(
    current_user: CurrentUserDep, llm_handler: LLMHandlerDep, studio_service: StudioServiceDep
) -> list[str]:
    """Retrieve all available LLM models discovered by the LLM Handler."""
    return studio_service.get_available_models(current_user, llm_handler)


@router.get("/", response_model=list[SystemConfigModelRegistry])
async def get_all_model_registries(
    current_user: CurrentUserDep, studio_service: StudioServiceDep
) -> list[SystemConfigModelRegistry]:
    """Retrieve all global model registry configurations securely via SSOT Service Layer."""
    return await studio_service.list_system_configs(current_user)


@router.post("/", response_model=SystemConfigModelRegistry)
async def create_model_registry(
    current_user: CurrentUserDep, studio_service: StudioServiceDep
) -> SystemConfigModelRegistry:
    """Create a new Model Registry config draft securely via SSOT Service Layer."""
    return await studio_service.create_model_registry_draft(current_user)


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


@router.delete("/{registry_id}", response_model=ModelRegistryDeleteResponse)
async def delete_model_registry(
    registry_id: str, current_user: CurrentUserDep, studio_service: StudioServiceDep
) -> ModelRegistryDeleteResponse:
    """Delete a model registry configuration securely via SSOT Service Layer."""
    await studio_service.delete_system_config(current_user, registry_id)
    return ModelRegistryDeleteResponse(status="success", deleted_id=registry_id)


@router.post("/{registry_id}/clone", response_model=SystemConfigModelRegistry)
async def clone_model_registry(
    registry_id: str,
    current_user: CurrentUserDep,
    studio_service: StudioServiceDep,
) -> SystemConfigModelRegistry:
    """Deep clone a model registry configuration securely via SSOT Service Layer."""
    return await studio_service.clone_system_config(current_user, registry_id)
