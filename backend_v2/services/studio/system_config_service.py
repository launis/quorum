"""Studio System Config Service."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import TYPE_CHECKING

from backend_v2.database.interfaces import ISystemRepository, IWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.core_base import PrefixedUUID7, generate_opaque_id
from backend_v2.models.domain.system_config import (
    AllowedMCPTool,
    ModelProfile,
    ProviderExtraParamsDTO,
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
    """Domain Service for System Config management.

    Attributes:
        system_repo: Repository interface for system configuration persistence.
        mcp_client: Protocol-agnostic MCP client for tool discovery.
        gateway_cache: Typed cache for MCP gateway manifests.
        workflow_repo: Optional workflow repository for delete referential-integrity checks.
    """

    def __init__(
        self,
        system_repo: ISystemRepository,
        mcp_client: GenericMCPClient | None = None,
        gateway_cache: MCPGatewayCache | None = None,
        workflow_repo: IWorkflowRepository | None = None,
    ) -> None:
        """Initialize the service.

        Args:
            system_repo: Repository for system configuration persistence.
            mcp_client: Optional protocol-agnostic MCP client for tool discovery.
            gateway_cache: Optional typed cache for MCP gateway manifests.
            workflow_repo: Optional workflow repository for delete referential-integrity checks.
        """
        self.system_repo = system_repo
        self.mcp_client = mcp_client if mcp_client is not None else GenericMCPClient()
        self.gateway_cache = gateway_cache if gateway_cache is not None else MCPGatewayCache()
        self.workflow_repo = workflow_repo

    def _require_root_or_admin(self, initiator: TokenData, action_description: str) -> None:
        """Verify that the initiator holds ROOT or ADMIN privileges.

        Args:
            initiator: The authenticated user initiating the request.
            action_description: Human-readable action description for error reporting.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If the user lacks ROOT or ADMIN role.
        """
        if initiator.role not in (UserRole.ROOT, UserRole.ADMIN):
            logger.error(
                "[StudioSystemConfigService] %s: User %s (Role: %s) unauthorized to %s.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                initiator.role,
                action_description,
                exc_info=True,
                extra={
                    "error_code": ErrorCodes.PERMISSION_DENIED.value,
                    "user_id": initiator.id,
                    "user_role": initiator.role.value,
                },
            )
            raise PermissionDeniedError(f"Only ROOT or ADMIN can {action_description}.")

    def _require_root(self, initiator: TokenData, action_description: str) -> None:
        """Verify that the initiator holds ROOT privileges.

        Args:
            initiator: The authenticated user initiating the request.
            action_description: Human-readable action description for error reporting.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If the user is not ROOT.
        """
        if initiator.role != UserRole.ROOT:
            logger.error(
                "[StudioSystemConfigService] %s: Only ROOT can %s (Initiator: %s).",
                ErrorCodes.PERMISSION_DENIED.name,
                action_description,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError(f"Only ROOT can {action_description}.")

    async def _ensure_not_referenced_by_workflows(
        self,
        *,
        entity_id: str,
        entity_label: str,
        id_detail_key: str,
        is_mcp_gateway: bool,
    ) -> None:
        """Ensure no workflow references the target system config entity before deletion.

        Args:
            entity_id: Canonical Opaque Stripe ID of the entity being deleted.
            entity_label: Human-readable entity type label for error messages.
            id_detail_key: Structured detail key for the entity ID in AppException details.
            is_mcp_gateway: True when checking Workflow.mcp_gateway_id; False for Workflow.model_registry_id.

        Raises:
            AppException (ErrorCodes.DELETE_BLOCKED_BY_USAGE): If any workflow references the entity.
        """
        if self.workflow_repo is None:
            return
        workflows = await self.workflow_repo.get_all_workflows()
        for wf in workflows:
            referenced_id = wf.mcp_gateway_id if is_mcp_gateway else wf.model_registry_id
            if referenced_id == entity_id:
                logger.error(
                    "[StudioSystemConfigService] %s: Cannot delete %s %s because it is referenced by workflow %s.",
                    ErrorCodes.DELETE_BLOCKED_BY_USAGE.name,
                    entity_label,
                    entity_id,
                    wf.id,
                    exc_info=True,
                    extra={
                        "error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value,
                        id_detail_key: entity_id,
                        "workflow_id": wf.id,
                    },
                )
                raise AppException(
                    message=f"Cannot delete {entity_label} '{entity_id}' because it is referenced by workflow '{wf.id}'.",
                    status_code=400,
                    details={
                        "error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value,
                        id_detail_key: entity_id,
                        "workflow_id": wf.id,
                    },
                )

    def get_available_models(
        self,
        initiator: TokenData,
        llm_handler: LLMHandler,
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
        self._require_root_or_admin(initiator, "fetch available models")

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
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If user is not authorized.
        """
        self._require_root_or_admin(initiator, "access supported locations")

        settings = get_settings()
        return llm_handler.fetch_vertex_locations(settings)

    def get_supported_platforms(self, initiator: TokenData) -> list[LLMPlatformDTO]:
        """Get all supported LLM platform providers.

        Args:
            initiator: The authenticated user initiating the request.

        Returns:
            List of supported LLM platforms.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If user is not authorized.
        """
        self._require_root_or_admin(initiator, "access supported platforms")

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

    async def _require_mcp_gateway(self, initiator: TokenData, id: str) -> SystemConfigMCPGateways:
        """Resolve an MCP gateway by ID from the repository or raise ResourceNotFoundError.

        Args:
            initiator: The authenticated user requesting the gateway.
            id: Canonical MCP gateway identifier.

        Returns:
            Matching SystemConfigMCPGateways domain model.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If no gateway matches id.
        """
        all_gateways = await self.system_repo.get_all_mcp_gateways()
        for gw in all_gateways:
            if gw.id == id:
                return gw
        logger.error(
            "[StudioSystemConfigService] %s: MCP gateway %s not found (Initiator: %s).",
            ErrorCodes.RESOURCE_NOT_FOUND.name,
            id,
            initiator.id,
            exc_info=True,
            extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "gateway_id": id},
        )
        raise ResourceNotFoundError(resource_type="mcp_gateways", resource_id=id)

    async def get_all_system_configs(self, initiator: TokenData) -> list[SystemConfigModelRegistry]:
        """List all model registry configurations for ROOT and ADMIN callers.

        Args:
            initiator: The authenticated user.

        Returns:
            List containing all SystemConfigModelRegistry documents.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If caller lacks ROOT or ADMIN role.
            AppException (ErrorCodes.STORAGE_ACCESS_FAILED): If repository retrieval fails.
        """
        self._require_root_or_admin(initiator, "list system configs")
        return await self.system_repo.get_all_model_registries()

    async def get_system_config(self, initiator: TokenData, id: str) -> SystemConfigModelRegistry:
        """Retrieve a specific model registry configuration by ID for ROOT and ADMIN callers.

        Args:
            initiator: The authenticated user.
            id: The system config identifier.

        Returns:
            The loaded SystemConfigModelRegistry.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If caller lacks ROOT or ADMIN role.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        self._require_root_or_admin(initiator, "view system configs")
        return await self.system_repo.get_model_registry(registry_id=id)

    async def _insert_validated_system_config(
        self, initiator: TokenData, id: str, data: SystemConfigModelRegistry
    ) -> SystemConfigModelRegistry:
        """Insert or persist a ROOT-authorized SystemConfigModelRegistry and reload by ID.

        Args:
            initiator: The authenticated ROOT user.
            id: Authoritative model registry identifier.
            data: Validated SystemConfigModelRegistry payload.

        Returns:
            Reloaded SystemConfigModelRegistry persisted under id.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If caller is not ROOT.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the registry cannot be reloaded after save.
        """
        self._require_root(initiator, "modify system configs")
        normalized = data
        if normalized.id != id:
            normalized = normalized.model_copy(update={"id": id})
        await self.system_repo.update_model_registry(normalized)
        return await self.system_repo.get_model_registry(registry_id=id)

    async def save_system_config(
        self, initiator: TokenData, id: str, data: SystemConfigModelRegistry
    ) -> SystemConfigModelRegistry:
        """Update an existing model registry configuration in-place under its authoritative ID.

        Args:
            initiator: The authenticated user.
            id: The system config identifier.
            data: The registry domain object.

        Returns:
            The saved SystemConfigModelRegistry.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the target registry does not exist.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If caller is not ROOT.
        """
        await self.system_repo.get_model_registry(registry_id=id)
        return await self._insert_validated_system_config(initiator, id, data)

    async def create_system_config_draft(self, initiator: TokenData) -> SystemConfigModelRegistry:
        """Create system config draft.

        Args:
            initiator: The authenticated user.

        Returns:
            The drafted SystemConfigModelRegistry.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If caller is not ROOT.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the drafted resource is missing after save.
        """
        self._require_root(initiator, "create system config drafts")

        new_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
        draft = SystemConfigModelRegistry(
            id=new_id,
            name="New Model Registry Draft",
            slug=new_id,
            type="model_registry",
            default_provider=LLMProvider.AI_STUDIO,
            tier_definitions={
                CognitiveTier.FAST: ModelProfile(
                    provider=LLMProvider.AI_STUDIO,
                    model_name="gemini/gemini-2.5-flash",
                    temperature=0.2,
                    allowed_tools=[],
                    additional_params=ProviderExtraParamsDTO(),
                ),
                CognitiveTier.BALANCED: ModelProfile(
                    provider=LLMProvider.AI_STUDIO,
                    model_name="gemini/gemini-2.5-flash",
                    temperature=0.4,
                    allowed_tools=[],
                    additional_params=ProviderExtraParamsDTO(),
                ),
                CognitiveTier.DEEP: ModelProfile(
                    provider=LLMProvider.AI_STUDIO,
                    model_name="gemini/gemini-2.5-pro",
                    temperature=0.7,
                    allowed_tools=[],
                    additional_params=ProviderExtraParamsDTO(),
                ),
                CognitiveTier.REASONING: ModelProfile(
                    provider=LLMProvider.AI_STUDIO,
                    model_name="gemini/gemini-2.5-pro",
                    temperature=1.0,
                    thinking_budget_tokens=4096,
                    allowed_tools=[],
                    additional_params=ProviderExtraParamsDTO(),
                ),
            },
        )
        return await self._insert_validated_system_config(initiator, new_id, draft)

    async def clone_system_config(self, initiator: TokenData, id: str) -> SystemConfigModelRegistry:
        """Clone an existing model registry configuration while preserving informational slug metadata.

        Args:
            initiator: The authenticated user.
            id: The system config identifier to clone.

        Returns:
            The cloned SystemConfigModelRegistry.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If caller is not ROOT.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        self._require_root(initiator, "clone system configs")
        data = await self.system_repo.get_model_registry(registry_id=id)

        new_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
        cloned_name = f"{data.name} (Copy)"
        cloned_obj = data.model_copy(
            update={
                "id": new_id,
                "name": cloned_name,
                "slug": data.slug,
            }
        )
        return await self._insert_validated_system_config(initiator, new_id, cloned_obj)

    async def delete_system_config(self, initiator: TokenData, id: str) -> None:
        """Delete system config.

        Args:
            initiator: The authenticated user.
            id: The system config identifier.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If non-ROOT user attempts deletion.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the system config is missing.
            AppException (ErrorCodes.SYSTEM_PROTECTED_RESOURCE): If attempting to delete the last model registry.
            AppException (ErrorCodes.DELETE_BLOCKED_BY_USAGE): If the model registry is referenced by a workflow.
        """
        self._require_root(initiator, "delete system configs")
        await self.system_repo.get_model_registry(registry_id=id)

        all_registries = await self.system_repo.get_all_model_registries()
        if len(all_registries) <= 1:
            logger.error(
                "[StudioSystemConfigService] %s: Cannot delete the last remaining model registry %s.",
                ErrorCodes.SYSTEM_PROTECTED_RESOURCE.name,
                id,
                exc_info=True,
                extra={"error_code": ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value, "registry_id": id},
            )
            raise AppException(
                message=f"Cannot delete the last remaining model registry '{id}'.",
                status_code=403,
                details={"error_code": ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value},
            )

        await self._ensure_not_referenced_by_workflows(
            entity_id=id,
            entity_label="model registry",
            id_detail_key="registry_id",
            is_mcp_gateway=False,
        )

        await self.system_repo.delete_system_config(id)

    async def list_mcp_gateways(self, initiator: TokenData) -> list[SystemConfigMCPGateways]:
        """List all MCP gateway configurations for ROOT and ADMIN users.

        Args:
            initiator: The authenticated user.

        Returns:
            List containing all MCP gateway configurations.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If caller lacks ROOT or ADMIN role.
            AppException (ErrorCodes.STORAGE_ACCESS_FAILED): If repository retrieval fails.
        """
        self._require_root_or_admin(initiator, "list MCP gateways")
        return await self.system_repo.get_all_mcp_gateways()

    async def get_mcp_gateways(self, initiator: TokenData, id: str) -> SystemConfigMCPGateways:
        """Retrieve a specific MCP gateway configuration by ID for ROOT and ADMIN users.

        Args:
            initiator: The authenticated user.
            id: The gateway config identifier.

        Returns:
            The loaded SystemConfigMCPGateways.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If caller lacks ROOT or ADMIN role.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        self._require_root_or_admin(initiator, "view MCP gateways")

        cached = await self.gateway_cache.get_gateway(id)
        if cached is not None:
            return cached

        gw = await self._require_mcp_gateway(initiator, id)
        await self.gateway_cache.set_gateway(gw)
        return gw

    async def _validate_and_persist_mcp_gateway(
        self, initiator: TokenData, id: str, data: SystemConfigMCPGateways
    ) -> SystemConfigMCPGateways:
        """Validate single-underscore slug uniqueness, persist an MCP gateway, and reload by ID.

        Args:
            initiator: The authenticated ROOT user.
            id: Authoritative MCP gateway identifier.
            data: SystemConfigMCPGateways payload to validate and persist.

        Returns:
            Reloaded SystemConfigMCPGateways persisted under id.

        Raises:
            AppException (ErrorCodes.VALIDATION_FAILED): If slug format is invalid or collides with another gateway.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the gateway is missing after persistence.
        """
        normalized = data
        if normalized.id != id:
            normalized = normalized.model_copy(update={"id": id})

        if not _SINGLE_UNDERSCORE_SLUG_PATTERN.match(normalized.slug):
            logger.error(
                "[StudioSystemConfigService] %s: Invalid MCP gateway slug format for %s.",
                ErrorCodes.VALIDATION_FAILED.name,
                id,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "gateway_id": id},
            )
            raise AppException(
                message=f"MCP gateway '{id}' has an invalid slug format; only lowercase alphanumeric and single underscores are permitted.",
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "gateway_id": id},
            )

        all_gateways = await self.system_repo.get_all_mcp_gateways()
        for existing_gw in all_gateways:
            if existing_gw.id != id and existing_gw.slug == normalized.slug:
                logger.error(
                    "[StudioSystemConfigService] %s: Duplicate MCP gateway slug collision between %s and %s.",
                    ErrorCodes.VALIDATION_FAILED.name,
                    id,
                    existing_gw.id,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value, "gateway_id": id},
                )
                raise AppException(
                    message=f"MCP gateway '{id}' has a duplicate slug already in use by gateway '{existing_gw.id}'.",
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "gateway_id": id},
                )

        await self.system_repo.update_mcp_gateways(normalized)
        await self.gateway_cache.invalidate(id)
        return await self.get_mcp_gateways(initiator, id)

    async def _insert_validated_mcp_gateways(
        self, initiator: TokenData, id: str, data: SystemConfigMCPGateways
    ) -> SystemConfigMCPGateways:
        """Insert a newly drafted or cloned MCP gateway after ROOT RBAC verification.

        Args:
            initiator: The authenticated ROOT user.
            id: Server-issued MCP gateway identifier.
            data: Newly constructed SystemConfigMCPGateways payload.

        Returns:
            Reloaded SystemConfigMCPGateways persisted under id.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If caller is not ROOT.
            AppException (ErrorCodes.VALIDATION_FAILED): If slug validation fails.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the gateway is missing after persistence.
        """
        self._require_root(initiator, "modify system configs")
        return await self._validate_and_persist_mcp_gateway(initiator, id, data)

    async def save_mcp_gateways(
        self, initiator: TokenData, id: str, data: SystemConfigMCPGateways
    ) -> SystemConfigMCPGateways:
        """Update an existing MCP gateway configuration in-place with single-underscore slug validation.

        Args:
            initiator: The authenticated user.
            id: The config identifier.
            data: The gateway domain object.

        Returns:
            The saved SystemConfigMCPGateways.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the target MCP gateway does not exist.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If caller is not ROOT.
            AppException (ErrorCodes.VALIDATION_FAILED): If slug format is invalid or collides with another gateway.
        """
        await self._require_mcp_gateway(initiator, id)
        return await self._insert_validated_mcp_gateways(initiator, id, data)

    async def create_mcp_gateway_draft(self, initiator: TokenData) -> SystemConfigMCPGateways:
        """Create a new MCP gateway draft with a deterministic single-underscore slug.

        Args:
            initiator: The authenticated user.

        Returns:
            The drafted SystemConfigMCPGateways.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If caller is not ROOT.
            AppException (ErrorCodes.VALIDATION_FAILED): If draft slug validation fails.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the drafted resource is missing after save.
        """
        self._require_root(initiator, "create MCP gateway drafts")

        new_id = generate_opaque_id(EntityPrefix.SYSTEM_CONFIG)
        draft_slug = f"gateway_{new_id.removeprefix(f'{EntityPrefix.SYSTEM_CONFIG}_')}"
        draft = SystemConfigMCPGateways(
            id=new_id,
            name="New MCP Gateway Draft",
            slug=draft_slug,
            type="mcp_gateways",
            tools=[],
        )
        return await self._insert_validated_mcp_gateways(initiator, new_id, draft)

    async def clone_mcp_gateways(self, initiator: TokenData, id: str) -> SystemConfigMCPGateways:
        """Clone an existing MCP gateway with a unique single-underscore copy slug.

        Args:
            initiator: The authenticated user.
            id: The config identifier to clone.

        Returns:
            The cloned SystemConfigMCPGateways.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If caller is not ROOT.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the source gateway is missing.
            AppException (ErrorCodes.VALIDATION_FAILED): If cloned slug validation fails.
        """
        self._require_root(initiator, "clone system configs")

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
        # Append copy suffix to cloned MCP gateway name to distinguish the duplicated gateway.
        cloned_obj = existing.model_copy(
            update={"id": new_id, "name": f"{existing.name} (Copy)", "slug": candidate_slug}
        )

        return await self._insert_validated_mcp_gateways(initiator, new_id, cloned_obj)

    async def delete_mcp_gateways(self, initiator: TokenData, id: str) -> None:
        """Delete an MCP gateway configuration and invalidate its cache entry.

        Args:
            initiator: The authenticated user.
            id: The MCP gateway identifier to delete.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If non-ROOT user attempts deletion.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the MCP gateway is missing.
            AppException (ErrorCodes.DELETE_BLOCKED_BY_USAGE): If the MCP gateway is referenced by a workflow.
        """
        enforce_modification_rights(initiator, SystemOrganizations.ROOT_SYSTEM, allow_system=False)
        all_gateways = await self.system_repo.get_all_mcp_gateways()
        target = next((gw for gw in all_gateways if gw.id == id), None)
        if target is None:
            logger.error(
                "[StudioSystemConfigService] %s: MCP gateway %s not found for deletion (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "gateway_id": id},
            )
            raise ResourceNotFoundError(resource_type="mcp_gateways", resource_id=id)

        await self._ensure_not_referenced_by_workflows(
            entity_id=id,
            entity_label="MCP gateway",
            id_detail_key="gateway_id",
            is_mcp_gateway=True,
        )

        await self.gateway_cache.invalidate(id)
        await self.system_repo.delete_system_config(id)

    async def discover_mcp_gateway_tools(
        self,
        initiator: TokenData,
        gateway_id: str,
    ) -> SystemConfigMCPGateways:
        """Connect to a remote MCP gateway, introspect tools via tools/list, and persist in-place.

        Args:
            initiator: The authenticated user.
            gateway_id: Canonical Opaque Stripe ID of the target gateway.

        Returns:
            Updated SystemConfigMCPGateways containing merged discovered tools.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If non-ROOT user attempts discovery.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If gateway_id does not exist.
            AppException (ErrorCodes.SECURITY_VIOLATION, ErrorCodes.AGENT_EXECUTION_CRITICAL): On SSRF violation, auth error, or MCP protocol failure.
        """
        enforce_modification_rights(initiator, SystemOrganizations.ROOT_SYSTEM, allow_system=False)
        gateway = await self.get_mcp_gateways(initiator, gateway_id)
        settings = get_settings()
        await asyncio.to_thread(
            MCPUrlValidator.validate_mcp_endpoint_url,
            gateway.endpoint_url,
            allow_private_networks=settings.mcp_allow_private_networks,
        )
        # Resolve caller organization_id (defaulting to ROOT_SYSTEM) for dynamic UI secret binding.
        effective_org_id: PrefixedUUID7 = SystemOrganizations.ROOT_SYSTEM.value
        if initiator.organization_id is not None:
            effective_org_id = initiator.organization_id
        discovered_tools = await self.mcp_client.list_tools(gateway, organization_id=effective_org_id)
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

        Raises:
            AppException (ErrorCodes.STORAGE_ACCESS_FAILED): If repository retrieval fails.
        """
        return await self.get_all_system_configs(initiator)
