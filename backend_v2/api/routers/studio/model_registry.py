"""Admin Studio Model Registry API Router.

Provides endpoints to manage global model registry configurations.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Query

from backend_v2.api.dependencies import CurrentUserDep, LLMHandlerDep, StudioSystemConfigServiceDep
from backend_v2.models.dtos.studio import GCPLocationDTO, ModelRegistryDeleteResponse
from backend_v2.models.enums import LLMPlatformType
from backend_v2.models.v2_core import SystemConfigModelRegistry

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/model-registry", tags=["Admin Studio V2 - Model Registry"])


@router.get("/available-models", response_model=list[str])
def get_available_models(
    current_user: CurrentUserDep,
    llm_handler: LLMHandlerDep,
    studio_service: StudioSystemConfigServiceDep,
    platform: Annotated[LLMPlatformType, Query(description="Target LLM platform")] = LLMPlatformType.ALL,
    location: Annotated[str | None, Query(description="Target GCP region for Vertex AI")] = None,
) -> list[str]:
    """Retrieve all available LLM models discovered by the LLM Handler.

    Args:
        current_user: The authenticated user making the request.
        llm_handler: The LLM handler dependency.
        studio_service: The studio service dependency.
        platform: Target platform filter (vertex_ai, ai_studio, openai, anthropic, all).
        location: Target GCP region location (e.g. europe-north1).

    Returns:
        A list of available model names.

    Raises:
        AppException: If fetching available models fails.
    """
    return studio_service.get_available_models(current_user, llm_handler, platform=platform, location=location)


@router.get("/locations", response_model=list[GCPLocationDTO])
def get_supported_locations(
    current_user: CurrentUserDep,
    studio_service: StudioSystemConfigServiceDep,
) -> list[GCPLocationDTO]:
    """Retrieve all supported GCP Vertex AI locations and regions.

    Args:
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        A list of supported GCP locations.

    Raises:
        AppException: If user is unauthorized or listing fails.
    """
    return studio_service.get_supported_locations(current_user)


@router.get("/", response_model=list[SystemConfigModelRegistry])
async def get_all_model_registries(
    current_user: CurrentUserDep, studio_service: StudioSystemConfigServiceDep
) -> list[SystemConfigModelRegistry]:
    """Retrieve all global model registry configurations securely via SSOT Service Layer.

    Args:
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        A list of model registry configurations.

    Raises:
        AppException: If fetching model registries fails.
    """
    return await studio_service.list_system_configs(current_user)


@router.post("/", response_model=SystemConfigModelRegistry)
async def create_model_registry(
    current_user: CurrentUserDep, studio_service: StudioSystemConfigServiceDep
) -> SystemConfigModelRegistry:
    """Create a new Model Registry config draft securely via SSOT Service Layer.

    Args:
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The newly created model registry draft configuration.

    Raises:
        AppException: If creating the draft fails.
    """
    return await studio_service.create_model_registry_draft(current_user)


@router.get("/{registry_id}", response_model=SystemConfigModelRegistry)
async def get_model_registry(
    registry_id: str,
    current_user: CurrentUserDep,
    studio_service: StudioSystemConfigServiceDep,
) -> SystemConfigModelRegistry:
    """Retrieve a single model registry configuration securely via SSOT Service Layer.

    Args:
        registry_id: The unique identifier of the model registry.
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The requested model registry configuration.

    Raises:
        ResourceNotFoundError: If the model registry is not found.
        AppException: If fetching the model registry fails.
    """
    return await studio_service.get_system_config(current_user, registry_id)


@router.put("/{registry_id}", response_model=SystemConfigModelRegistry)
async def save_model_registry(
    registry_id: str,
    data: SystemConfigModelRegistry,
    current_user: CurrentUserDep,
    studio_service: StudioSystemConfigServiceDep,
) -> SystemConfigModelRegistry:
    """Update a model registry configuration securely via SSOT Service Layer.

    Args:
        registry_id: The unique identifier of the model registry.
        data: The new configuration data.
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The updated model registry configuration.

    Raises:
        ResourceNotFoundError: If the model registry is not found.
        AppException: If updating the model registry fails.
    """
    return await studio_service.save_system_config(current_user, registry_id, data)


@router.delete("/{registry_id}", response_model=ModelRegistryDeleteResponse)
async def delete_model_registry(
    registry_id: str, current_user: CurrentUserDep, studio_service: StudioSystemConfigServiceDep
) -> ModelRegistryDeleteResponse:
    """Delete a model registry configuration securely via SSOT Service Layer.

    Args:
        registry_id: The unique identifier of the model registry to delete.
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        A ModelRegistryDeleteResponse confirming the deletion.

    Raises:
        ResourceNotFoundError: If the model registry is not found.
        AppException: If deleting the model registry fails.
    """
    await studio_service.delete_system_config(current_user, registry_id)
    return ModelRegistryDeleteResponse(status="success", deleted_id=registry_id)


@router.post("/{registry_id}/clone", response_model=SystemConfigModelRegistry)
async def clone_model_registry(
    registry_id: str,
    current_user: CurrentUserDep,
    studio_service: StudioSystemConfigServiceDep,
) -> SystemConfigModelRegistry:
    """Deep clone a model registry configuration securely via SSOT Service Layer.

    Args:
        registry_id: The unique identifier of the model registry to clone.
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The newly cloned model registry configuration.

    Raises:
        ResourceNotFoundError: If the source model registry is not found.
        AppException: If cloning the model registry fails.
    """
    return await studio_service.clone_system_config(current_user, registry_id)
