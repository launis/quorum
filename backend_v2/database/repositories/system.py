"""Database repository implementation module for System config, MCP config, and Model registries."""

import logging
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import ResourceNotFoundError
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

    async def update_model_registry(self, registry_data: dict[str, Any]) -> bool:
        """Updates the system model registry configuration.

        Args:
            registry_data: Dictionary containing updated model registry fields.

        Returns:
            True if updated successfully.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "model_registry")], limit=1)
        doc_id = res_list[0]["id"] if res_list else (registry_data["id"] if "id" in registry_data else "model_registry")
        if doc_id != "model_registry" and "type" not in registry_data:
            registry_data["type"] = "model_registry"
        await self.driver.upsert("system_config", registry_data, doc_id)
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

    async def update_mcp_gateways(self, gateways_data: dict[str, Any]) -> bool:
        """Updates the MCP gateways configuration.

        Args:
            gateways_data: Dictionary containing MCP gateway settings.

        Returns:
            True if updated successfully.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "mcp_gateways")], limit=1)
        doc_id = (
            res_list[0]["id"] if res_list else (gateways_data["id"] if "id" in gateways_data else "cfg_mcpGateways01")
        )
        if doc_id != "cfg_mcpGateways01" and "type" not in gateways_data:
            gateways_data["type"] = "mcp_gateways"
        await self.driver.upsert("system_config", gateways_data, doc_id)
        return True

    async def get_system_settings(self) -> dict[str, Any] | None:
        """Retrieves global system settings.

        Returns:
            The global settings dictionary if found.

        Raises:
            ResourceNotFoundError: If the global_settings document is missing.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "global_settings")], limit=1)
        res = res_list[0] if res_list else None
        if not res:
            logger.error("[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: 'global_settings' document is missing.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id="global_settings")
        return res

    async def update_system_settings(self, updates: dict[str, Any]) -> bool:
        """Updates global system settings.

        Args:
            updates: Dictionary of settings updates.

        Returns:
            True if updated successfully.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "global_settings")], limit=1)
        doc_id = res_list[0]["id"] if res_list else (updates["id"] if "id" in updates else "global_settings")
        if doc_id != "global_settings" and "type" not in updates:
            updates["type"] = "global_settings"
        await self.driver.upsert("system_config", updates, doc_id)
        return True

    async def get_system_config(self, config_id: str) -> dict[str, Any] | None:
        """Gets a system configuration document by its ID.

        Args:
            config_id: Unique identifier for the system config document.

        Returns:
            The document dictionary if found, otherwise None.
        """
        return await self.driver.get("system_config", config_id)

    async def create_system_config(self, config_data: dict[str, Any]) -> str:
        """Creates a new system configuration document.

        Args:
            config_data: Dictionary containing configuration fields.

        Returns:
            The document ID.
        """
        doc_id = str(config_data["id"])
        return await self.driver.upsert("system_config", config_data, doc_id)
