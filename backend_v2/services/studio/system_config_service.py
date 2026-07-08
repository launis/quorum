"""Studio System Config Service."""

from __future__ import annotations

import logging
import uuid
from typing import Any

from backend_v2.database.interfaces import ISystemRepository
from backend_v2.exceptions import ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
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

    def get_available_models(self, initiator: TokenData, llm_handler: Any) -> list[str]:
        """Get available models.

        Args:
            initiator: The authenticated user initiating the request.
            llm_handler: The underlying LLM registry handler.

        Returns:
            A sorted list of available AI models.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
        """
        if initiator.role not in [UserRole.ROOT, UserRole.ADMIN]:
            logger.error(
                "[StudioSystemConfigService] %s: User %s (Role: %s) attempted to fetch available models without ROOT or ADMIN.",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                initiator.role,
                extra={
                    "error_code": ErrorCodes.PERMISSION_DENIED.value,
                    "user_id": initiator.id,
                    "user_role": getattr(initiator.role, "value", initiator.role),
                },
            )
            raise PermissionDeniedError("Only ROOT or ADMIN can fetch available models.")

        result = llm_handler.fetch_all_available_models()

        flat_list: list[str] = []
        for models in result.values():
            if isinstance(models, list):
                flat_list.extend(models)
            elif isinstance(models, str):
                flat_list.append(models)

        return sorted(list(set(flat_list)))

    async def get_all_system_configs(self, initiator: TokenData) -> list[SystemConfigModelRegistry]:
        """Get all system configs.

        Args:
            initiator: The authenticated user.

        Returns:
            A list containing the SystemConfigModelRegistry if accessible.
        """
        if initiator.role == UserRole.ROOT:
            all_data = [await self.system_repo.get_model_registry()]
            if all_data[0]:
                return [
                    SystemConfigModelRegistry.model_validate(x, strict=False)
                    for x in all_data
                    if x.get("type") == "model_registry"
                ]
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
        return SystemConfigModelRegistry.model_validate(data, strict=False)

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

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.system_repo.update_model_registry(dump)

        saved = await self.system_repo.get_model_registry()
        if not saved:
            logger.error(
                "[StudioSystemConfigService] %s: SystemConfig %s not found after save (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigModelRegistry.model_validate(saved, strict=False)

    async def delete_system_config(self, initiator: TokenData, id: str) -> None:
        """Delete system config.

        Args:
            initiator: The authenticated user.
            id: The system config identifier.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant access is violated.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
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
                "[StudioSystemConfigService] %s: SystemConfig %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)

    async def create_model_registry_draft(self, initiator: TokenData) -> SystemConfigModelRegistry:
        """Create model registry draft.

        Args:
            initiator: The authenticated user.

        Returns:
            The drafted SystemConfigModelRegistry.
        """
        enforce_modification_rights(initiator, SystemOrganizations.ROOT_SYSTEM, allow_system=True)

        new_id = f"sys_{uuid.uuid4().hex[:16]}"
        draft_dict: dict[str, Any] = {"id": new_id, "slug": new_id, "type": "model_registry", "models": {}}
        draft = SystemConfigModelRegistry.model_validate(draft_dict, strict=False)
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
                "[StudioSystemConfigService] %s: SystemConfig %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)

        new_id = f"sys_{uuid.uuid4().hex}"

        cloned_data = SystemConfigModelRegistry.model_validate(data, strict=False).model_dump(mode="json")
        cloned_data["id"] = new_id
        if "description" in cloned_data and getattr(cloned_data["description"], "strip", None) is not None:
            cloned_data["description"] = f"{cloned_data['description']} (Copy)"

        await self.system_repo.update_model_registry(cloned_data)

        saved = await self.system_repo.get_model_registry()
        return SystemConfigModelRegistry.model_validate(saved, strict=False)

    async def list_mcp_gateways(self, initiator: TokenData) -> list[SystemConfigMCPGateways]:
        """List mcp gateways.

        Args:
            initiator: The authenticated user.

        Returns:
            A list containing the MCP gateways config if accessible.
        """
        all_data = [await self.system_repo.get_mcp_gateways()]
        if all_data[0] and initiator.role == UserRole.ROOT:
            return [
                SystemConfigMCPGateways.model_validate(x, strict=False)
                for x in all_data
                if x.get("type") == "mcp_gateways"
            ]
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
        data = await self.system_repo.get_mcp_gateways()
        if not data or data.get("type") != "mcp_gateways":
            logger.error(
                "[StudioSystemConfigService] %s: MCP Gateways Config %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigMCPGateways.model_validate(data, strict=False)

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

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.system_repo.update_mcp_gateways(dump)

        saved = await self.system_repo.get_mcp_gateways()
        if not saved:
            logger.error(
                "[StudioSystemConfigService] %s: MCP Gateways Config %s not found after save (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigMCPGateways.model_validate(saved, strict=False)

    async def create_mcp_gateway_draft(self, initiator: TokenData) -> SystemConfigMCPGateways:
        """Create mcp gateway draft.

        Args:
            initiator: The authenticated user.

        Returns:
            The drafted SystemConfigMCPGateways.
        """
        enforce_modification_rights(initiator, SystemOrganizations.ROOT_SYSTEM, allow_system=True)

        new_id = f"mcp_{uuid.uuid4().hex[:16]}"
        draft_dict: dict[str, Any] = {"id": new_id, "slug": new_id, "type": "mcp_gateways", "tools": []}
        draft = SystemConfigMCPGateways.model_validate(draft_dict, strict=False)
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
        data = await self.system_repo.get_mcp_gateways()
        if not data or data.get("type") != "mcp_gateways":
            logger.error(
                "[StudioSystemConfigService] %s: MCP Gateway Config %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)

        new_id = f"mcp_{uuid.uuid4().hex}"

        cloned_data = SystemConfigMCPGateways.model_validate(data, strict=False).model_dump(mode="json")
        cloned_data["id"] = new_id

        if "description" in cloned_data and cloned_data["description"]:
            pass

        await self.system_repo.update_mcp_gateways(cloned_data)

        saved = await self.system_repo.get_mcp_gateways()
        return SystemConfigMCPGateways.model_validate(saved, strict=False)

    async def list_system_configs(self, initiator: TokenData) -> list[SystemConfigModelRegistry]:
        """List system configs.

        Args:
            initiator: The authenticated user.

        Returns:
            A list containing the SystemConfigModelRegistry if accessible.
        """
        data = await self.system_repo.get_model_registry()
        if data and initiator.role == UserRole.ROOT:
            return [SystemConfigModelRegistry.model_validate(data, strict=False)]
        return []
