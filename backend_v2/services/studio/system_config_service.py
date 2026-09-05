"""Studio System Config Service."""

from __future__ import annotations

import logging
from typing import Any

from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.dtos.studio import GCPLocationDTO
from backend_v2.models.enums import EntityPrefix, GCPVertexLocation, LLMPlatformType
from backend_v2.models.v2_core import (
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.services.studio.auth_validator import enforce_modification_rights

logger = logging.getLogger(__name__)


class StudioSystemConfigService:
    """Domain Service for System Config management."""

    def __init__(self, system_repo: ISystemRepository):
        """Initialize the service.

        Args:
            system_repo: Parameter system_repo.
        """
        self.system_repo = system_repo

    def get_available_models(
        self,
        initiator: TokenData,
        llm_handler: Any,
        platform: LLMPlatformType = LLMPlatformType.ALL,
        location: str | None = None,
    ) -> list[str]:
        """Get available models filtered by platform and location.

        Args:
            initiator: The authenticated user initiating the request.
            llm_handler: The underlying LLM registry handler.
            platform: Target platform type (e.g. vertex_ai, ai_studio, openai, anthropic, all).
            location: Optional GCP region location for Vertex AI models.

        Returns:
            A sorted list of available AI models.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
        """
        if initiator.role not in [UserRole.ROOT, UserRole.ADMIN]:
            logger.error(
                "[StudioSystemConfigService] %s: User %s (Role: %s) unauthorized to fetch available models.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                initiator.role,
                extra={
                    "error_code": ErrorCodes.PERMISSION_DENIED.value,
                    "user_id": initiator.id,
                    "user_role": initiator.role.value,
                },
            )
            raise PermissionDeniedError("Only ROOT or ADMIN can fetch available models.")

        platform_val = platform.value if isinstance(platform, LLMPlatformType) else str(platform)
        result = llm_handler.fetch_all_available_models(
            location=location,
            platform=platform_val,
        )

        flat_list: list[str] = []
        for models in result.values():
            if isinstance(models, list):
                flat_list.extend(models)
            elif isinstance(models, str):
                flat_list.append(models)

        return sorted(list(set(flat_list)))

    def get_supported_locations(self, initiator: TokenData) -> list[GCPLocationDTO]:
        """Get all supported GCP Vertex AI locations and regions.

        Args:
            initiator: The authenticated user initiating the request.

        Returns:
            List of supported GCP locations.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If user is not authorized.
        """
        if initiator.role not in [UserRole.ROOT, UserRole.ADMIN]:
            logger.error(
                "[StudioSystemConfigService] %s: User %s attempted to list locations without ROOT/ADMIN permissions.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("Only ROOT or ADMIN can access supported locations.")

        return [
            GCPLocationDTO(
                id=GCPVertexLocation.EUROPE_NORTH1.value,
                label="Hamina, Finland (europe-north1)",
                description="Google Cloud Nordic flagship datacenter with 100% carbon-free energy.",
            ),
            GCPLocationDTO(
                id=GCPVertexLocation.EUROPE_WEST1.value,
                label="St. Ghislain, Belgium (europe-west1)",
                description="Primary Western European Google Cloud region with broad Gemini availability.",
            ),
            GCPLocationDTO(
                id=GCPVertexLocation.EUROPE_WEST4.value,
                label="Eemshaven, Netherlands (europe-west4)",
                description="Netherlands enterprise datacenter hub.",
            ),
            GCPLocationDTO(
                id=GCPVertexLocation.EUROPE_WEST3.value,
                label="Frankfurt, Germany (europe-west3)",
                description="Central European financial and enterprise cloud hub.",
            ),
            GCPLocationDTO(
                id=GCPVertexLocation.US_CENTRAL1.value,
                label="Council Bluffs, Iowa (us-central1)",
                description="Primary Google Cloud AI and Model Garden launch region.",
            ),
            GCPLocationDTO(
                id=GCPVertexLocation.US_EAST4.value,
                label="Ashburn, Virginia (us-east4)",
                description="US East enterprise corridor with extensive compute capacity.",
            ),
        ]

    async def get_all_system_configs(self, initiator: TokenData) -> list[SystemConfigModelRegistry]:
        """Get all system configs.

        Args:
            initiator: The authenticated user.

        Returns:
            A list containing the SystemConfigModelRegistry if accessible.
        """
        if initiator.role == UserRole.ROOT:
            data = await self.system_repo.get_model_registry()
            if data and data.type == "model_registry":
                return [data]
        return []

    async def get_system_config(self, initiator: TokenData, id: str) -> SystemConfigModelRegistry:
        """Get system config.

        Args:
            initiator: The authenticated user.
            id: The system config identifier.

        Returns:
            The loaded SystemConfigModelRegistry.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[StudioSystemConfigService] %s: Only ROOT can view system configs (Initiator: %s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
            )
            raise PermissionDeniedError("Only ROOT can view system configs.")
        data = await self.system_repo.get_model_registry()
        if not data:
            logger.error(
                "[StudioSystemConfigService] %s: SystemConfig %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return data

    async def save_system_config(
        self, initiator: TokenData, id: str, data: SystemConfigModelRegistry
    ) -> SystemConfigModelRegistry:
        """Save system config.

        Args:
            initiator: The authenticated user.
            id: The system config identifier.
            data: The registry domain object.

        Returns:
            The saved SystemConfigModelRegistry.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[StudioSystemConfigService] %s: Only ROOT can modify system configs (Initiator: %s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
            )
            raise PermissionDeniedError("Only ROOT can modify system configs.")

        if data.id != id:
            data = data.model_copy(update={"id": id})
        await self.system_repo.update_model_registry(data)

        saved = await self.system_repo.get_model_registry()
        if not saved:
            logger.error(
                "[StudioSystemConfigService] %s: SystemConfig %s not found after save (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return saved

    async def create_system_config_draft(self, initiator: TokenData) -> SystemConfigModelRegistry:
        """Create system config draft.

        Args:
            initiator: The authenticated user.

        Returns:
            The drafted SystemConfigModelRegistry.
        """
        enforce_modification_rights(initiator, SystemOrganizations.ROOT_SYSTEM, allow_system=True)

        new_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
        draft = SystemConfigModelRegistry(
            id=new_id,
            slug=new_id,
            type="model_registry",
            models={},
        )
        return await self.save_system_config(initiator, new_id, draft)

    async def clone_system_config(self, initiator: TokenData, id: str) -> SystemConfigModelRegistry:
        """Clone system config.

        Args:
            initiator: The authenticated user.
            id: The system config identifier to clone.

        Returns:
            The cloned SystemConfigModelRegistry.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[StudioSystemConfigService] %s: Only ROOT can clone system configs (Initiator: %s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
            )
            raise PermissionDeniedError("Only ROOT can clone system configs.")
        data = await self.system_repo.get_model_registry()
        if not data:
            logger.error(
                "[StudioSystemConfigService] %s: Model registry not found for cloning (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)

        new_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
        if data.slug:
            cloned_slug = f"{data.slug}-copy"
        else:
            cloned_slug = None
        cloned_obj = data.model_copy(
            update={
                "id": new_id,
                "slug": cloned_slug,
            }
        )
        return await self.save_system_config(initiator, new_id, cloned_obj)

    async def delete_system_config(self, initiator: TokenData, id: str) -> None:
        """Delete system config.

        Args:
            initiator: The authenticated user.
            id: The system config identifier.

        Raises:
            PermissionDeniedError: If non-ROOT user attempts deletion.
            ResourceNotFoundError: If the system config is missing.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[StudioSystemConfigService] %s: Only ROOT can delete system configs (Initiator: %s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
            )
            raise PermissionDeniedError("Only ROOT can delete system configs.")
        data = await self.system_repo.get_model_registry()
        if not data:
            logger.error(
                "[StudioSystemConfigService] %s: SystemConfig %s not found for deletion (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)

    async def list_mcp_gateways(self, initiator: TokenData) -> list[SystemConfigMCPGateways]:
        """List mcp gateways.

        Args:
            initiator: The authenticated user.

        Returns:
            A list containing the MCP gateways config if accessible.
        """
        if initiator.role != UserRole.ROOT:
            return []
        data = await self.system_repo.get_mcp_gateways()
        if data and data.type == "mcp_gateways":
            return [data]
        return []

    async def get_mcp_gateways(self, initiator: TokenData, id: str) -> SystemConfigMCPGateways:
        """Get mcp gateways.

        Args:
            initiator: The authenticated user.
            id: The config identifier.

        Returns:
            The loaded SystemConfigMCPGateways.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[StudioSystemConfigService] %s: Only ROOT can view system configs (Initiator: %s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
            )
            raise PermissionDeniedError("Only ROOT can view system configs.")
        return await self.system_repo.get_mcp_gateways(id=id)

    async def save_mcp_gateways(
        self, initiator: TokenData, id: str, data: SystemConfigMCPGateways
    ) -> SystemConfigMCPGateways:
        """Save mcp gateways.

        Args:
            initiator: The authenticated user.
            id: The config identifier.
            data: The gateway domain object.

        Returns:
            The saved SystemConfigMCPGateways.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[StudioSystemConfigService] %s: Only ROOT can modify system configs (Initiator: %s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
            )
            raise PermissionDeniedError("Only ROOT can modify system configs.")

        if data.id != id:
            data = data.model_copy(update={"id": id})
        await self.system_repo.update_mcp_gateways(data)

        return await self.system_repo.get_mcp_gateways(id=id)

    async def create_mcp_gateway_draft(self, initiator: TokenData) -> SystemConfigMCPGateways:
        """Create mcp gateway draft.

        Args:
            initiator: The authenticated user.

        Returns:
            The drafted SystemConfigMCPGateways.
        """
        enforce_modification_rights(initiator, SystemOrganizations.ROOT_SYSTEM, allow_system=True)

        new_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
        draft = SystemConfigMCPGateways(id=new_id, slug=new_id, type="mcp_gateways", tools=[])
        return await self.save_mcp_gateways(initiator, new_id, draft)

    async def clone_mcp_gateways(self, initiator: TokenData, id: str) -> SystemConfigMCPGateways:
        """Clone mcp gateways.

        Args:
            initiator: The authenticated user.
            id: The config identifier to clone.

        Returns:
            The cloned SystemConfigMCPGateways.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[StudioSystemConfigService] %s: Only ROOT can clone system configs (Initiator: %s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
            )
            raise PermissionDeniedError("Only ROOT can clone system configs.")
        data = await self.system_repo.get_mcp_gateways(id=id)

        new_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
        cloned_obj = data.model_copy(update={"id": new_id})

        return await self.save_mcp_gateways(initiator, new_id, cloned_obj)

    async def list_system_configs(self, initiator: TokenData) -> list[SystemConfigModelRegistry]:
        """List system configs.

        Args:
            initiator: The authenticated user.

        Returns:
            A list containing the SystemConfigModelRegistry if accessible.
        """
        data = await self.system_repo.get_model_registry()
        if data and initiator.role == UserRole.ROOT:
            return [data]
        return []
