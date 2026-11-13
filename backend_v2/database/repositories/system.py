"""Database repository implementation module for Model Registries and MCP Gateways."""

from __future__ import annotations

import logging

from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import ResourceNotFoundError
from backend_v2.models.domain.system_config import SystemConfigMCPGateways, SystemConfigModelRegistry

logger = logging.getLogger(__name__)

__all__ = ["SystemRepositoryImpl"]


class SystemRepositoryImpl(BaseRepository):
    """Repository implementation for SystemConfigModelRegistry and SystemConfigMCPGateways."""

    async def get_model_registry(self, registry_id: str) -> SystemConfigModelRegistry:
        """Retrieve a model registry configuration by its explicit mrg_<hex32> ID.

        Args:
            registry_id: Authoritative mrg_<hex32> model registry ID.

        Returns:
            Validated SystemConfigModelRegistry domain model.

        Raises:
            ResourceNotFoundError: If registry_id is empty or not found.
        """
        if not registry_id:
            logger.error("[SystemRepository] MODEL_REGISTRY_NOT_FOUND: registry_id is required.")
            raise ResourceNotFoundError(resource_type="model_registry", resource_id="")

        async with self._acquire_entities() as entities:
            cfg = await entities.get_model_registry(registry_id)
        if cfg is None:
            logger.error(
                "[SystemRepository] MODEL_REGISTRY_NOT_FOUND: Model registry '%s' is missing.",
                registry_id,
            )
            raise ResourceNotFoundError(resource_type="model_registry", resource_id=registry_id)
        return cfg

    async def get_all_model_registries(self) -> list[SystemConfigModelRegistry]:
        """Retrieve all model registry configurations ordered deterministically by name and ID.

        Returns:
            List of validated SystemConfigModelRegistry domain models.
        """
        async with self._acquire_entities() as entities:
            models = await entities.list_model_registries()
        return sorted(models, key=lambda m: (m.name, m.id))

    async def update_model_registry(self, registry_data: SystemConfigModelRegistry) -> bool:
        """Upsert a SystemConfigModelRegistry using its authoritative mrg_<hex32> ID.

        Args:
            registry_data: Validated SystemConfigModelRegistry domain model.

        Returns:
            True once persisted.
        """
        async with self._acquire_entities() as entities:
            await entities.upsert_model_registry(registry_data)
        return True

    async def delete_model_registry(self, registry_id: str) -> bool:
        """Delete a model registry record by primary key ID.

        Args:
            registry_id: Canonical mrg_<hex32> model registry identifier.

        Returns:
            True if deleted, False otherwise.
        """
        async with self._acquire_entities() as entities:
            return await entities.delete_model_registry(registry_id)

    async def get_mcp_gateways(self, id: str | None = None) -> SystemConfigMCPGateways:
        """Fetch an MCP gateway configuration by explicit ID or first available gateway document.

        Args:
            id: Optional explicit mcp_<hex32> MCP gateway ID.

        Returns:
            Validated SystemConfigMCPGateways domain model.

        Raises:
            ResourceNotFoundError: If no matching MCP gateway configuration exists.
        """
        async with self._acquire_entities() as entities:
            if id:
                cfg = await entities.get_mcp_gateway(id)
                if cfg is None:
                    logger.error("[SystemRepository] MCP_GATEWAY_NOT_FOUND: '%s' document is missing.", id)
                    raise ResourceNotFoundError(resource_type="mcp_gateways", resource_id=id)
                return cfg

            gateways = await entities.list_mcp_gateways()
        if not gateways:
            logger.error("[SystemRepository] MCP_GATEWAY_NOT_FOUND: 'mcp_gateways' document is missing.")
            raise ResourceNotFoundError(resource_type="mcp_gateways", resource_id="mcp_gateways")
        gateways.sort(key=lambda m: (m.slug, m.id))
        return gateways[0]

    async def get_all_mcp_gateways(self) -> list[SystemConfigMCPGateways]:
        """Retrieve all MCP gateway configurations ordered deterministically by slug and ID.

        Returns:
            List of validated SystemConfigMCPGateways domain models.
        """
        async with self._acquire_entities() as entities:
            models = await entities.list_mcp_gateways()
        return sorted(models, key=lambda m: (m.slug, m.id))

    async def update_mcp_gateways(self, gateways_data: SystemConfigMCPGateways) -> bool:
        """Upsert a SystemConfigMCPGateways configuration using its authoritative mcp_<hex32> ID.

        Args:
            gateways_data: Validated SystemConfigMCPGateways domain model.

        Returns:
            True once persisted.
        """
        async with self._acquire_entities() as entities:
            await entities.upsert_mcp_gateway(gateways_data)
        return True

    async def delete_mcp_gateways(self, gateway_id: str) -> bool:
        """Delete an MCP gateway record by primary key ID.

        Args:
            gateway_id: Canonical mcp_<hex32> MCP gateway identifier.

        Returns:
            True if deleted, False otherwise.
        """
        async with self._acquire_entities() as entities:
            return await entities.delete_mcp_gateway(gateway_id)
