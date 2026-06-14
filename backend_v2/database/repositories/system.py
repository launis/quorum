"""Database repository implementation module."""

import logging
from typing import Any

from backend_v2.database.driver import Filter
from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


class SystemRepositoryImpl(BaseRepository):
    """Repository implementation for System config, MCP config, and Model registries."""

    async def get_model_registry(self) -> dict[str, Any]:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "model_registry")], limit=1)
        res = res_list[0] if res_list else None
        if not res:
            logger.error("[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: 'model_registry' document is missing.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id="model_registry")
        return res

    async def update_model_registry(self, registry_data: dict[str, Any]) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "model_registry")], limit=1)
        doc_id = res_list[0]["id"] if res_list else registry_data.get("id", "model_registry")
        if doc_id != "model_registry" and "slug" not in registry_data:
            registry_data["slug"] = "model_registry"
        await self.driver.upsert("system_config", registry_data, doc_id)
        return True

    async def get_mcp_gateways(self) -> dict[str, Any]:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "mcp_gateways")], limit=1)
        res = res_list[0] if res_list else None
        if not res:
            logger.error("[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: 'mcp_gateways' document is missing.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id="mcp_gateways")
        return res

    async def update_mcp_gateways(self, gateways_data: dict[str, Any]) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "mcp_gateways")], limit=1)
        doc_id = res_list[0]["id"] if res_list else gateways_data.get("id", "cfg_mcpGateways01")
        if doc_id != "cfg_mcpGateways01" and "slug" not in gateways_data:
            gateways_data["slug"] = "mcp_gateways"
        await self.driver.upsert("system_config", gateways_data, doc_id)
        return True

    async def get_system_settings(self) -> dict[str, Any] | None:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "global_settings")], limit=1)
        res = res_list[0] if res_list else None
        if not res:
            logger.error("[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: 'global_settings' document is missing.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id="global_settings")
        return res

    async def update_system_settings(self, updates: dict[str, Any]) -> bool:
        """Repository method implementation.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            The expected result of the operation.

        Raises:
            AppException: If a critical operation fails.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "global_settings")], limit=1)
        doc_id = res_list[0]["id"] if res_list else updates.get("id", "global_settings")
        if doc_id != "global_settings" and "slug" not in updates:
            updates["slug"] = "global_settings"
        await self.driver.upsert("system_config", updates, doc_id)
        return True
