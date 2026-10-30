"""Admin Studio Model Registry API Router.

Provides endpoints to manage global model registry configurations.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from backend_v2.api.dependencies import CurrentUserDep, LLMHandlerDep, StudioSystemConfigServiceDep
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import OPAQUE_STRIPE_ID_REGEX
from backend_v2.models.domain.system_config import SystemConfigModelRegistry
from backend_v2.models.dtos.studio import GCPLocationDTO, LLMPlatformDTO, ModelRegistryDeleteResponse
from backend_v2.models.enums import LLMPlatformType

logger = logging.getLogger(__name__)

__all__ = ["router"]

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
        location: Target GCP region location identifier for Vertex AI.

    Returns:
        A sorted list of available model identifiers.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks ROOT or ADMIN role.
        AppException: With ErrorCodes.CONFIGURATION_ERROR or ErrorCodes.SERVICE_DEPENDENCY_MISSING if provider discovery fails.
    """
    return studio_service.get_available_models(current_user, llm_handler, platform=platform, location=location)


@router.get("/locations", response_model=list[GCPLocationDTO])
def get_supported_locations(
    current_user: CurrentUserDep,
    studio_service: StudioSystemConfigServiceDep,
    llm_handler: LLMHandlerDep,
) -> list[GCPLocationDTO]:
    """Retrieve all supported GCP Vertex AI locations and regions.

    Args:
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.
        llm_handler: The LLM handler dependency for dynamic discovery.

    Returns:
        A list of supported GCP locations.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks ROOT or ADMIN role.
        AppException: With ErrorCodes.CONFIGURATION_ERROR if dynamic region discovery fails.
    """
    return studio_service.get_supported_locations(current_user, llm_handler)


@router.get("/platforms", response_model=list[LLMPlatformDTO])
def get_supported_platforms(
    current_user: CurrentUserDep,
    studio_service: StudioSystemConfigServiceDep,
) -> list[LLMPlatformDTO]:
    """Retrieve all supported LLM platform providers.

    Args:
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        A list of supported LLM platforms.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks ROOT or ADMIN role.
    """
    return studio_service.get_supported_platforms(current_user)


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
        AppException: With ErrorCodes.DATABASE_ERROR if fetching model registries fails.
    """
    return await studio_service.get_all_system_configs(current_user)


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
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks ROOT modification rights.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the persisted draft cannot be reloaded.
    """
    return await studio_service.create_system_config_draft(current_user)


@router.get("/{registry_id}", response_model=SystemConfigModelRegistry)
async def get_model_registry(
    registry_id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    studio_service: StudioSystemConfigServiceDep,
) -> SystemConfigModelRegistry:
    """Retrieve a single model registry configuration securely via SSOT Service Layer.

    Args:
        registry_id: The unique Opaque Stripe ID of the model registry.
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The requested model registry configuration.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks ROOT role.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the model registry is not found.
    """
    return await studio_service.get_system_config(current_user, registry_id)


@router.put("/{registry_id}", response_model=SystemConfigModelRegistry)
async def save_model_registry(
    registry_id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    data: SystemConfigModelRegistry,
    current_user: CurrentUserDep,
    studio_service: StudioSystemConfigServiceDep,
) -> SystemConfigModelRegistry:
    """Update a model registry configuration securely via SSOT Service Layer.

    Args:
        registry_id: The unique Opaque Stripe ID of the model registry.
        data: The new configuration data.
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The updated model registry configuration.

    Raises:
        AppException: With ErrorCodes.ID_MISMATCH if path registry_id does not match payload id.
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks ROOT role.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the model registry is not found after save.
    """
    if data.id != registry_id:
        logger.error(
            "[ModelRegistryRouter] %s: Path registry_id '%s' does not match payload id '%s' (Initiator: %s).",
            ErrorCodes.ID_MISMATCH.name,
            registry_id,
            data.id,
            current_user.id,
            exc_info=True,
            extra={"error_code": ErrorCodes.ID_MISMATCH.value, "registry_id": registry_id},
        )
        raise AppException(
            message=f"Path registry_id '{registry_id}' does not match payload id '{data.id}'",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.ID_MISMATCH.value},
        )

    return await studio_service.save_system_config(current_user, registry_id, data)


@router.delete("/{registry_id}", response_model=ModelRegistryDeleteResponse)
async def delete_model_registry(
    registry_id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    studio_service: StudioSystemConfigServiceDep,
) -> ModelRegistryDeleteResponse:
    """Delete a model registry configuration securely via SSOT Service Layer.

    Args:
        registry_id: The unique Opaque Stripe ID of the model registry to delete.
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        A ModelRegistryDeleteResponse confirming the deletion.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks ROOT role.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the model registry is not found.
    """
    await studio_service.delete_system_config(current_user, registry_id)
    return ModelRegistryDeleteResponse(status="success", deleted_id=registry_id)


@router.post("/{registry_id}/clone", response_model=SystemConfigModelRegistry)
async def clone_model_registry(
    registry_id: Annotated[str, Path(pattern=OPAQUE_STRIPE_ID_REGEX)],
    current_user: CurrentUserDep,
    studio_service: StudioSystemConfigServiceDep,
) -> SystemConfigModelRegistry:
    """Deep clone a model registry configuration securely via SSOT Service Layer.

    Args:
        registry_id: The unique Opaque Stripe ID of the model registry to clone.
        current_user: The authenticated user making the request.
        studio_service: The studio service dependency.

    Returns:
        The newly cloned model registry configuration.

    Raises:
        PermissionDeniedError: With ErrorCodes.PERMISSION_DENIED if the user lacks ROOT role.
        ResourceNotFoundError: With ErrorCodes.RESOURCE_NOT_FOUND if the source model registry is not found.
    """
    return await studio_service.clone_system_config(current_user, registry_id)
