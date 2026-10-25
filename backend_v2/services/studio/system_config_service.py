"""Studio System Config Service."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import TYPE_CHECKING, Any

from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    ModelProfile,
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)
from backend_v2.models.dtos.studio import GCPLocationDTO, LLMPlatformDTO
from backend_v2.models.enums import (
    CognitiveTier,
    EntityPrefix,
    LLMPlatformType,
    LLMProvider,
)
from backend_v2.services.cache.typed_cache import MCPGatewayCache
from backend_v2.services.mcp.generic_mcp_client import GenericMCPClient
from backend_v2.services.mcp.url_validator import MCPUrlValidator
from backend_v2.services.studio.auth_validator import enforce_modification_rights
from backend_v2.settings import get_settings

if TYPE_CHECKING:
    from backend_v2.llm.handler import LLMHandler

__all__ = ["StudioSystemConfigService"]

logger = logging.getLogger(__name__)

_SINGLE_UNDERSCORE_SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


class StudioSystemConfigService:
    """Domain Service for System Config management."""

    def __init__(
        self,
        system_repo: ISystemRepository,
        mcp_client: GenericMCPClient | None = None,
        gateway_cache: MCPGatewayCache | None = None,
    ) -> None:
        """Initialize the service.

        Args:
            system_repo: Repository for system configuration persistence.
            mcp_client: Optional protocol-agnostic MCP client for tool discovery.
            gateway_cache: Optional typed cache for MCP gateway manifests.
        """
        self.system_repo = system_repo
        self.mcp_client = mcp_client if mcp_client is not None else GenericMCPClient()
        self.gateway_cache = gateway_cache if gateway_cache is not None else MCPGatewayCache()

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
            PermissionDeniedError: If tenant access is violated.
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

        flat_set: set[str] = set()
        for models in result.values():
            if isinstance(models, list):
                flat_set.update(models)
            elif isinstance(models, str):
                flat_set.add(models)

        return sorted(flat_set)

    def get_supported_locations(
        self,
        initiator: TokenData,
        llm_handler: LLMHandler,
    ) -> list[GCPLocationDTO]:
        """Get all supported GCP Vertex AI locations and regions dynamically.

        Args:
            initiator: The authenticated user initiating the request.
            llm_handler: The LLM handler for dynamic provider discovery.

        Returns:
            List of supported GCP locations.

        Raises:
            PermissionDeniedError: If user is not authorized.
        """
        if initiator.role not in [UserRole.ROOT, UserRole.ADMIN]:
            logger.error(
                "[StudioSystemConfigService] %s: User %s attempted to list locations without ROOT/ADMIN permissions.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("Only ROOT or ADMIN can access supported locations.")

        settings = get_settings()
        return llm_handler.fetch_vertex_locations(settings)

    def get_supported_platforms(self, initiator: TokenData) -> list[LLMPlatformDTO]:
        """Get all supported LLM platform providers.

        Args:
            initiator: The authenticated user initiating the request.

        Returns:
            List of supported LLM platforms.

        Raises:
            PermissionDeniedError: If user is not authorized.
        """
        if initiator.role not in [UserRole.ROOT, UserRole.ADMIN]:
            logger.error(
                "[StudioSystemConfigService] %s: User %s attempted to list platforms without ROOT/ADMIN permissions.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("Only ROOT or ADMIN can access supported platforms.")

        return [
            LLMPlatformDTO(
                id="vertex_ai",
                label="Google Cloud Vertex AI",
                has_regions=True,
            ),
            LLMPlatformDTO(
                id="ai_studio",
                label="Google AI Studio",
                has_regions=False,
            ),
            LLMPlatformDTO(
                id="openai",
                label="OpenAI",
                has_regions=False,
            ),
            LLMPlatformDTO(
                id="anthropic",
                label="Anthropic",
                has_regions=False,
            ),
        ]

    async def get_all_system_configs(self, initiator: TokenData) -> list[SystemConfigModelRegistry]:
        """Get all system configs.

        Args:
            initiator: The authenticated user.

        Returns:
            A list containing all SystemConfigModelRegistry documents if accessible.
        """
        if initiator.role == UserRole.ROOT:
            return await self.system_repo.get_all_model_registries()
        return []

    async def get_system_config(self, initiator: TokenData, id: str) -> SystemConfigModelRegistry:
        """Get system config.

        Args:
            initiator: The authenticated user.
            id: The system config identifier.

        Returns:
            The loaded SystemConfigModelRegistry.

        Raises:
            PermissionDeniedError: If tenant access is violated.
            ResourceNotFoundError: If the resource is missing.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[StudioSystemConfigService] %s: Only ROOT can view system configs (Initiator: %s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
            )
            raise PermissionDeniedError("Only ROOT can view system configs.")
        data = await self.system_repo.get_model_registry(registry_id=id)
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
            PermissionDeniedError: If tenant access is violated.
            ResourceNotFoundError: If the resource is missing.
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

        saved = await self.system_repo.get_model_registry(registry_id=id)
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
            name="New Model Registry Draft",
            slug=new_id,
            type="model_registry",
            default_provider=LLMProvider.AI_STUDIO,
            tier_definitions={
                CognitiveTier.FAST: ModelProfile(
                    provider="ai_studio",
                    model_name="gemini/gemini-2.5-flash",
                    temperature=0.2,
                ),
                CognitiveTier.BALANCED: ModelProfile(
                    provider="ai_studio",
                    model_name="gemini/gemini-2.5-flash",
                    temperature=0.4,
                ),
                CognitiveTier.DEEP: ModelProfile(
                    provider="ai_studio",
                    model_name="gemini/gemini-2.5-pro",
                    temperature=0.7,
                ),
                CognitiveTier.REASONING: ModelProfile(
                    provider="ai_studio",
                    model_name="gemini/gemini-2.5-pro",
                    temperature=1.0,
                    thinking_budget_tokens=4096,
                ),
            },
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
            PermissionDeniedError: If tenant access is violated.
            ResourceNotFoundError: If the resource is missing.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[StudioSystemConfigService] %s: Only ROOT can clone system configs (Initiator: %s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
            )
            raise PermissionDeniedError("Only ROOT can clone system configs.")
        data = await self.system_repo.get_model_registry(registry_id=id)
        if not data:
            logger.error(
                "[StudioSystemConfigService] %s: Model registry %s not found for cloning (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)

        new_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
        cloned_name = f"{data.name} (Copy)"
        cloned_slug: str | None = None
        if data.slug:
            cloned_slug = f"{data.slug}-copy"
        cloned_obj = data.model_copy(
            update={
                "id": new_id,
                "name": cloned_name,
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
        data = await self.system_repo.get_model_registry(registry_id=id)
        if not data:
            logger.error(
                "[StudioSystemConfigService] %s: SystemConfig %s not found for deletion (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        await self.system_repo.delete_system_config(id)

    async def list_mcp_gateways(self, initiator: TokenData) -> list[SystemConfigMCPGateways]:
        """List all MCP gateway configurations.

        Args:
            initiator: The authenticated user.

        Returns:
            A list containing all MCP gateway configurations if accessible.
        """
        if initiator.role != UserRole.ROOT:
            return []
        return await self.system_repo.get_all_mcp_gateways()

    async def get_mcp_gateways(self, initiator: TokenData, id: str) -> SystemConfigMCPGateways:
        """Retrieve a specific MCP gateway configuration by ID.

        Args:
            initiator: The authenticated user.
            id: The gateway config identifier.

        Returns:
            The loaded SystemConfigMCPGateways.

        Raises:
            PermissionDeniedError: If tenant access is violated.
            ResourceNotFoundError: If the resource is missing.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[StudioSystemConfigService] %s: Only ROOT can view system configs (Initiator: %s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("Only ROOT can view system configs.")

        cached = await self.gateway_cache.get_gateway(id)
        if cached is not None:
            return cached

        all_gateways = await self.system_repo.get_all_mcp_gateways()
        for gw in all_gateways:
            if gw.id == id:
                await self.gateway_cache.set_gateway(gw)
                return gw

        logger.error(
            "[StudioSystemConfigService] %s: MCP gateway %s not found (Initiator: %s).",
            ErrorCodes.RESOURCE_NOT_FOUND.name,
            id,
            initiator.id,
            extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "gateway_id": id},
        )
        raise ResourceNotFoundError(resource_type="mcp_gateways", resource_id=id)

    async def save_mcp_gateways(
        self, initiator: TokenData, id: str, data: SystemConfigMCPGateways
    ) -> SystemConfigMCPGateways:
        """Save an MCP gateway configuration with unique single-underscore slug validation.

        # Phase 2, Step 2.3: Enforce unique single-underscore slugs and cache invalidation

        Args:
            initiator: The authenticated user.
            id: The config identifier.
            data: The gateway domain object.

        Returns:
            The saved SystemConfigMCPGateways.

        Raises:
            PermissionDeniedError: If tenant access is violated.
            AppException: If slug format is invalid or collides with another gateway.
            ResourceNotFoundError: If the resource is missing after persistence.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[StudioSystemConfigService] %s: Only ROOT can modify system configs (Initiator: %s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("Only ROOT can modify system configs.")

        if data.id != id:
            data = data.model_copy(update={"id": id})

        if not _SINGLE_UNDERSCORE_SLUG_PATTERN.match(data.slug):
            logger.error(
                "[StudioSystemConfigService] %s: Invalid MCP gateway slug format for %s.",
                ErrorCodes.VALIDATION_FAILED.name,
                id,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "gateway_id": id},
            )
            raise AppException(
                message=f"MCP gateway '{id}' has an invalid slug format; only lowercase alphanumeric and single underscores are permitted.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "gateway_id": id},
            )

        all_gateways = await self.system_repo.get_all_mcp_gateways()
        for existing_gw in all_gateways:
            if existing_gw.id != id and existing_gw.slug == data.slug:
                logger.error(
                    "[StudioSystemConfigService] %s: Duplicate MCP gateway slug collision between %s and %s.",
                    ErrorCodes.VALIDATION_FAILED.name,
                    id,
                    existing_gw.id,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "gateway_id": id},
                )
                raise AppException(
                    message=f"MCP gateway slug '{data.slug}' is already in use by gateway '{existing_gw.id}'.",
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "gateway_id": id},
                )

        await self.system_repo.update_mcp_gateways(data)
        await self.gateway_cache.invalidate(id)
        return await self.get_mcp_gateways(initiator, id)

    async def create_mcp_gateway_draft(self, initiator: TokenData) -> SystemConfigMCPGateways:
        """Create a new MCP gateway draft with a deterministic single-underscore slug.

        Args:
            initiator: The authenticated user.

        Returns:
            The drafted SystemConfigMCPGateways.

        Raises:
            PermissionDeniedError: If modification rights are denied.
        """
        enforce_modification_rights(initiator, SystemOrganizations.ROOT_SYSTEM, allow_system=True)

        new_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
        draft_slug = f"gateway_{new_id.removeprefix('sys_')[:8]}"
        draft = SystemConfigMCPGateways(id=new_id, slug=draft_slug, type="mcp_gateways", tools=[])
        return await self.save_mcp_gateways(initiator, new_id, draft)

    async def clone_mcp_gateways(self, initiator: TokenData, id: str) -> SystemConfigMCPGateways:
        """Clone an existing MCP gateway with a unique single-underscore copy slug.

        Args:
            initiator: The authenticated user.
            id: The config identifier to clone.

        Returns:
            The cloned SystemConfigMCPGateways.

        Raises:
            PermissionDeniedError: If tenant access is violated.
            ResourceNotFoundError: If the source gateway is missing.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[StudioSystemConfigService] %s: Only ROOT can clone system configs (Initiator: %s).",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("Only ROOT can clone system configs.")

        existing = await self.get_mcp_gateways(initiator, id)
        all_gateways = await self.system_repo.get_all_mcp_gateways()
        existing_slugs = {gw.slug for gw in all_gateways}

        base_copy_slug = f"{existing.slug}_copy"
        candidate_slug = base_copy_slug
        suffix = 2
        while candidate_slug in existing_slugs:
            candidate_slug = f"{base_copy_slug}_{suffix}"
            suffix += 1

        new_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
        cloned_obj = existing.model_copy(update={"id": new_id, "slug": candidate_slug})

        return await self.save_mcp_gateways(initiator, new_id, cloned_obj)

    async def delete_mcp_gateways(self, initiator: TokenData, id: str) -> None:
        """Delete an MCP gateway configuration and invalidate its cache entry.

        # Phase 2, Step 2.3: Dedicated delete_mcp_gateways method

        Args:
            initiator: The authenticated user.
            id: The MCP gateway identifier to delete.

        Raises:
            PermissionDeniedError: If non-ROOT user attempts deletion.
            ResourceNotFoundError: If the MCP gateway is missing.
        """
        enforce_modification_rights(initiator, SystemOrganizations.ROOT_SYSTEM, allow_system=True)
        all_gateways = await self.system_repo.get_all_mcp_gateways()
        target = next((gw for gw in all_gateways if gw.id == id), None)
        if target is None:
            logger.error(
                "[StudioSystemConfigService] %s: MCP gateway %s not found for deletion (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "gateway_id": id},
            )
            raise ResourceNotFoundError(resource_type="mcp_gateways", resource_id=id)

        await self.gateway_cache.invalidate(id)
        await self.system_repo.delete_system_config(id)

    async def discover_mcp_gateway_tools(
        self,
        initiator: TokenData,
        gateway_id: str,
    ) -> SystemConfigMCPGateways:
        """Connect to a remote MCP gateway, introspect tools via tools/list, and persist in-place.

        # Phase 2, Step 2.3: Studio runtime tool discovery and allowlist preservation

        Args:
            initiator: The authenticated user.
            gateway_id: Canonical Opaque Stripe ID of the target gateway.

        Returns:
            Updated SystemConfigMCPGateways containing merged discovered tools.

        Raises:
            PermissionDeniedError: If non-ROOT user attempts discovery.
            ResourceNotFoundError: If gateway_id does not exist.
            AppException: On SSRF violation, auth error, or MCP protocol failure.
        """
        enforce_modification_rights(initiator, SystemOrganizations.ROOT_SYSTEM, allow_system=True)
        gateway = await self.get_mcp_gateways(initiator, gateway_id)
        settings = get_settings()
        await asyncio.to_thread(
            MCPUrlValidator.validate_mcp_endpoint_url,
            gateway.endpoint_url,
            allow_private_networks=settings.mcp_allow_private_networks,
        )
        discovered_tools = await self.mcp_client.list_tools(gateway)
        merged_tools = self._merge_discovered_tools(
            existing_tools=gateway.tools,
            discovered_tools=discovered_tools,
        )
        updated_gateway = gateway.model_copy(update={"tools": merged_tools})
        await self.system_repo.update_mcp_gateways(updated_gateway)
        await self.gateway_cache.invalidate(gateway_id)
        return await self.get_mcp_gateways(initiator, gateway_id)

    def _merge_discovered_tools(
        self,
        *,
        existing_tools: list[AllowedMCPTool],
        discovered_tools: list[AllowedMCPTool],
    ) -> list[AllowedMCPTool]:
        """Preserve existing enabled, capability, and localized name settings for known tool_ids.

        Args:
            existing_tools: Previously saved AllowedMCPTool entries on the gateway.
            discovered_tools: Newly introspected AllowedMCPTool entries from tools/list.

        Returns:
            Merged list of AllowedMCPTool models.
        """
        existing_by_id: dict[str, AllowedMCPTool] = {tool.tool_id: tool for tool in existing_tools}
        merged: list[AllowedMCPTool] = []
        for disc_tool in discovered_tools:
            if disc_tool.tool_id in existing_by_id:
                prev = existing_by_id[disc_tool.tool_id]
                merged.append(
                    disc_tool.model_copy(
                        update={
                            "enabled": prev.enabled,
                            "capability": prev.capability,
                            "name": prev.name,
                        }
                    )
                )
            else:
                merged.append(disc_tool)
        return merged

    async def list_system_configs(self, initiator: TokenData) -> list[SystemConfigModelRegistry]:
        """List system configs.

        Args:
            initiator: The authenticated user.

        Returns:
            A list containing all SystemConfigModelRegistry documents if accessible.
        """
        return await self.get_all_system_configs(initiator)
