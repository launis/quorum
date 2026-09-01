"""Database repository implementation module for System config, MCP config, and Model registries."""

from __future__ import annotations

import logging

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import ResourceNotFoundError
from backend_v2.models.dtos.system import (
    AnySystemConfig,
    AnySystemConfigAdapter,
    SystemConfigCreateDTO,
    SystemConfigUpdateDTO,
    SystemSettingsDTO,
)
from backend_v2.models.v2_core import SystemConfigMCPGateways, SystemConfigModelRegistry

logger = logging.getLogger(__name__)


class SystemRepositoryImpl(BaseRepository):
    """Repository implementation for System config, MCP config, and Model registries."""

    async def get_model_registry(self) -> SystemConfigModelRegistry:
        """Retrieves the system model registry configuration.

        Returns:
            The validated SystemConfigModelRegistry domain model.

        Raises:
            ResourceNotFoundError: If the model_registry configuration document is missing.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "model_registry")], limit=1)
        res = res_list[0] if res_list else None
        if not res:
            logger.error("[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: 'model_registry' document is missing.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id="model_registry")
        return SystemConfigModelRegistry.model_validate(res, strict=False)

    async def update_model_registry(self, registry_data: SystemConfigModelRegistry) -> bool:
        """Updates the system model registry configuration.

        Args:
            registry_data: SystemConfigModelRegistry containing updated model registry fields.

        Returns:
            True if updated successfully.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "model_registry")], limit=1)
        payload = registry_data.model_dump(mode="json", exclude_unset=True)
        doc_id = res_list[0]["id"] if res_list else (payload["id"] if "id" in payload else "model_registry")
        payload["id"] = doc_id
        payload["type"] = "model_registry"
        await self.driver.upsert("system_config", payload, doc_id)
        return True

    async def get_mcp_gateways(self, id: str | None = None) -> SystemConfigMCPGateways:
        """Fetch MCP gateways configuration by ID or fallback to type 'mcp_gateways'.

        Args:
            id: Optional specific system_config ID.

        Returns:
            The validated SystemConfigMCPGateways domain model.

        Raises:
            ResourceNotFoundError: If the configuration document is not found.
        """
        if id:
            filters = [Filter("id", "==", id)]
            target_id = id
        else:
            filters = [Filter("type", "==", "mcp_gateways")]
            target_id = "mcp_gateways"

        res_list = await self.driver.query("system_config", filters, limit=1)
        res = res_list[0] if res_list else None
        if not res:
            logger.error("[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: '%s' document is missing.", target_id)
            raise ResourceNotFoundError(resource_type="system_config", resource_id=target_id)
        return SystemConfigMCPGateways.model_validate(res, strict=False)

    async def update_mcp_gateways(self, gateways_data: SystemConfigMCPGateways) -> bool:
        """Updates the MCP gateways configuration.

        Args:
            gateways_data: SystemConfigMCPGateways containing MCP gateway settings.

        Returns:
            True if updated successfully.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "mcp_gateways")], limit=1)
        payload = gateways_data.model_dump(mode="json", exclude_unset=True)
        doc_id = res_list[0]["id"] if res_list else (payload["id"] if "id" in payload else "cfg_mcpGateways01")
        payload["id"] = doc_id
        payload["type"] = "mcp_gateways"
        await self.driver.upsert("system_config", payload, doc_id)
        return True

    async def get_system_settings(self) -> SystemSettingsDTO | None:
        """Retrieves global system settings.

        Returns:
            The SystemSettingsDTO if found.

        Raises:
            ResourceNotFoundError: If the global_settings document is missing.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "global_settings")], limit=1)
        res = res_list[0] if res_list else None
        if not res:
            logger.error("[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: 'global_settings' document is missing.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id="global_settings")
        return SystemSettingsDTO.model_validate(res, strict=False)

    async def update_system_settings(self, updates: SystemConfigUpdateDTO) -> bool:
        """Updates global system settings.

        Args:
            updates: SystemConfigUpdateDTO containing settings updates.

        Returns:
            True if updated successfully.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "global_settings")], limit=1)
        payload = updates.model_dump(mode="json", exclude_unset=True)
        doc_id = res_list[0]["id"] if res_list else (payload["id"] if "id" in payload else "global_settings")
        payload["id"] = doc_id
        payload["type"] = "global_settings"
        await self.driver.upsert("system_config", payload, doc_id)
        return True

    async def get_system_config(self, config_id: str) -> AnySystemConfig | None:
        """Gets a system configuration document by its ID.

        Args:
            config_id: Unique identifier for the system config document.

        Returns:
            The typed AnySystemConfig if found, otherwise None.
        """
        doc = await self.driver.get("system_config", config_id)
        if not doc:
            return None
        return AnySystemConfigAdapter.validate_python(doc, strict=False)

    async def create_system_config(self, config_data: SystemConfigCreateDTO) -> str:
        """Creates a new system configuration document.

        Args:
            config_data: SystemConfigCreateDTO containing configuration fields.

        Returns:
            The document ID.
        """
        payload = config_data.model_dump(mode="json")
        doc_id = payload["id"] if "id" in payload else f"cfg_{config_data.type}"
        payload["id"] = doc_id
        return await self.driver.upsert("system_config", payload, doc_id)
