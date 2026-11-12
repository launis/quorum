"""Database repository implementation module for System config, MCP gateways, and Model registries."""

from __future__ import annotations

import logging

from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import ResourceNotFoundError
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry
from backend_v2.models.dtos.system import (
    AnySystemConfig,
    SystemConfigCreateDTO,
)

logger = logging.getLogger(__name__)

__all__ = ["SystemRepositoryImpl"]


class SystemRepositoryImpl(BaseRepository):
    """Repository implementation for SystemConfigModelRegistry and SystemConfigMCPGateways."""

    async def get_model_registry(self, registry_id: str) -> SystemConfigModelRegistry:
        """Retrieve a system model registry configuration by its explicit ID.

        Args:
            registry_id: Authoritative sys_<hex32> model registry ID.

        Returns:
            Validated SystemConfigModelRegistry domain model.

        Raises:
            ResourceNotFoundError: If registry_id is empty, not found, or not a model registry.
        """
        if not registry_id:
            logger.error("[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: registry_id is required.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id="")

        async with self._acquire_entities() as entities:
            cfg = await entities.get_system_config(registry_id)
        if cfg is None or not isinstance(cfg, SystemConfigModelRegistry):
            logger.error(
                "[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: Model registry '%s' is missing.",
                registry_id,
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=registry_id)
        return cfg

    async def get_all_model_registries(self) -> list[SystemConfigModelRegistry]:
        """Retrieve all model registry configurations ordered deterministically by name and ID.

        Returns:
            List of validated SystemConfigModelRegistry domain models.
        """
        async with self._acquire_entities() as entities:
            configs = await entities.list_system_configs()
        models = [cfg for cfg in configs if isinstance(cfg, SystemConfigModelRegistry)]
        return sorted(models, key=lambda m: (m.name, m.id))

    async def update_model_registry(self, registry_data: SystemConfigModelRegistry) -> bool:
        """Upsert a SystemConfigModelRegistry using its authoritative ID.

        Args:
            registry_data: Validated SystemConfigModelRegistry domain model.

        Returns:
            True once persisted.
        """
        async with self._acquire_entities() as entities:
            await entities.upsert_system_config(registry_data)
        return True

    async def delete_system_config(self, config_id: str) -> bool:
        """Delete a system configuration record by primary key ID.

        Args:
            config_id: Canonical sys_<hex32> system configuration identifier.

        Returns:
            True if deleted, False otherwise.
        """
        async with self._acquire_entities() as entities:
            return await entities.delete_system_config(config_id)

    async def get_mcp_gateways(self, id: str | None = None) -> SystemConfigMCPGateways:
        """Fetch an MCP gateways configuration by explicit ID or first available gateway document.

        Args:
            id: Optional explicit sys_<hex32> system configuration ID.

        Returns:
            Validated SystemConfigMCPGateways domain model.

        Raises:
            ResourceNotFoundError: If no matching MCP gateways configuration exists.
        """
        async with self._acquire_entities() as entities:
            if id:
                cfg = await entities.get_system_config(id)
                if cfg is None or not isinstance(cfg, SystemConfigMCPGateways):
                    logger.error("[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: '%s' document is missing.", id)
                    raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
                return cfg

            configs = await entities.list_system_configs()
        gateways = [cfg for cfg in configs if isinstance(cfg, SystemConfigMCPGateways)]
        if not gateways:
            logger.error("[SystemRepository] SYSTEM_CONFIG_NOT_FOUND: 'mcp_gateways' document is missing.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id="mcp_gateways")
        gateways.sort(key=lambda m: (m.slug, m.id))
        return gateways[0]

    async def get_all_mcp_gateways(self) -> list[SystemConfigMCPGateways]:
        """Retrieve all MCP gateway configurations ordered deterministically by slug and ID.

        Returns:
            List of validated SystemConfigMCPGateways domain models.
        """
        async with self._acquire_entities() as entities:
            configs = await entities.list_system_configs()
        models = [cfg for cfg in configs if isinstance(cfg, SystemConfigMCPGateways)]
        return sorted(models, key=lambda m: (m.slug, m.id))

    async def update_mcp_gateways(self, gateways_data: SystemConfigMCPGateways) -> bool:
        """Upsert a SystemConfigMCPGateways configuration using its authoritative ID.

        Args:
            gateways_data: Validated SystemConfigMCPGateways domain model.

        Returns:
            True once persisted.
        """
        async with self._acquire_entities() as entities:
            await entities.upsert_system_config(gateways_data)
        return True

    async def get_system_config(self, config_id: str) -> AnySystemConfig | None:
        """Retrieve a polymorphic AnySystemConfig by primary key ID.

        Args:
            config_id: Canonical sys_<hex32> system configuration identifier.

        Returns:
            Validated SystemConfigModelRegistry or SystemConfigMCPGateways if found, else None.
        """
        async with self._acquire_entities() as entities:
            return await entities.get_system_config(config_id)

    async def create_system_config(self, config_data: SystemConfigCreateDTO) -> str:
        """Persist a new SystemConfig document from a SystemConfigCreateDTO.

        Args:
            config_data: Validated SystemConfigCreateDTO carrying typed content.

        Returns:
            Persisted canonical sys_<hex32> identifier.
        """
        cfg_to_save: AnySystemConfig = config_data.content
        if (
            config_data.slug is not None
            and isinstance(cfg_to_save, SystemConfigMCPGateways)
            and cfg_to_save.slug != config_data.slug
        ):
            cfg_to_save = cfg_to_save.model_copy(update={"slug": config_data.slug})
        async with self._acquire_entities() as entities:
            return await entities.upsert_system_config(cfg_to_save)
