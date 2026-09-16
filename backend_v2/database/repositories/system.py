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
from backend_v2.models.enums import SystemConfigID
from backend_v2.models.v2_core import (
    SystemConfigMCPGateways,
    SystemConfigModelRegistry,
)

logger = logging.getLogger(__name__)

__all__ = ["SystemRepositoryImpl"]


class SystemRepositoryImpl(BaseRepository):
    """Repository implementation for System config, MCP config, and Model registries."""

    async def get_model_registry(self, registry_id: str | None = None) -> SystemConfigModelRegistry:
        """Retrieves a system model registry configuration.

        Args:
            registry_id: Optional specific model registry ID. If omitted, retrieves the default/first registry.

        Returns:
            The validated SystemConfigModelRegistry domain model.

        Raises:
            ResourceNotFoundError: If the model registry configuration document is missing.
        """
        if registry_id:
            res = await self.driver.get("system_config", registry_id)
            if not res or "type" not in res or res["type"] != "model_registry":
                logger.error(
                    "[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: Model registry '%s' is missing.",
                    registry_id,
                )
                raise ResourceNotFoundError(resource_type="system_config", resource_id=registry_id)
            return SystemConfigModelRegistry.model_validate(res, strict=False)

        res_list = await self.driver.query("system_config", [Filter("type", "==", "model_registry")])
        if not res_list:
            logger.error("[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: 'model_registry' document is missing.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id="model_registry")
        models = [SystemConfigModelRegistry.model_validate(r, strict=False) for r in res_list]
        sorted_models = sorted(
            models,
            key=lambda m: (m.id != "sys_e26807f3bfa3454d", m.name, m.id),
        )
        return sorted_models[0]

    async def get_all_model_registries(self) -> list[SystemConfigModelRegistry]:
        """Retrieves all model registry configurations ordered deterministically.

        Returns:
            A list of validated SystemConfigModelRegistry domain models.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "model_registry")])
        models = [SystemConfigModelRegistry.model_validate(r, strict=False) for r in res_list]
        return sorted(
            models,
            key=lambda m: (m.id != "sys_e26807f3bfa3454d", m.name, m.id),
        )

    async def update_model_registry(self, registry_data: SystemConfigModelRegistry) -> bool:
        """Updates or inserts a system model registry configuration using its authoritative ID.

        Args:
            registry_data: SystemConfigModelRegistry containing updated model registry fields.

        Returns:
            True if updated successfully.
        """
        doc_id = registry_data.id or SystemConfigID.MODEL_REGISTRY.value
        payload = registry_data.model_dump(mode="json", exclude_unset=True)
        payload["id"] = doc_id
        payload["type"] = "model_registry"
        await self.driver.upsert("system_config", payload, doc_id)
        return True

    async def delete_system_config(self, config_id: str) -> bool:
        """Deletes a system configuration document by ID.

        Args:
            config_id: Unique identifier for the system config document.

        Returns:
            True if deleted, False otherwise.
        """
        return await self.driver.delete("system_config", config_id)

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
        if not res_list:
            logger.error("[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: '%s' document is missing.", target_id)
            raise ResourceNotFoundError(resource_type="system_config", resource_id=target_id)
        return SystemConfigMCPGateways.model_validate(res_list[0], strict=False)

    async def update_mcp_gateways(self, gateways_data: SystemConfigMCPGateways) -> bool:
        """Updates the MCP gateways configuration.

        Args:
            gateways_data: SystemConfigMCPGateways containing MCP gateway settings.

        Returns:
            True if updated successfully.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "mcp_gateways")], limit=1)
        payload = gateways_data.model_dump(mode="json", exclude_unset=True)
        if res_list:
            doc_id = str(res_list[0]["id"])
        elif gateways_data.id:
            doc_id = gateways_data.id
        else:
            doc_id = SystemConfigID.MCP_GATEWAYS.value
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
        if not res_list:
            logger.error("[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: 'global_settings' document is missing.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id="global_settings")
        return SystemSettingsDTO.model_validate(res_list[0], strict=False)

    async def update_system_settings(self, updates: SystemConfigUpdateDTO) -> bool:
        """Updates global system settings.

        Args:
            updates: SystemConfigUpdateDTO containing settings updates.

        Returns:
            True if updated successfully.
        """
        res_list = await self.driver.query("system_config", [Filter("type", "==", "global_settings")], limit=1)
        payload = updates.model_dump(mode="json", exclude_unset=True)
        if res_list:
            doc_id = str(res_list[0]["id"])
        elif "id" in payload:
            doc_id = str(payload["id"])
        else:
            doc_id = "global_settings"
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
        if "id" in payload:
            doc_id = str(payload["id"])
        else:
            doc_id = f"cfg_{config_data.type}"
        payload["id"] = doc_id
        return await self.driver.upsert("system_config", payload, doc_id)
