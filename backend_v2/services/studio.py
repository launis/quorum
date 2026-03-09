"""Studio Management Service."""

from __future__ import annotations

import logging
from typing import Any

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData
from backend_v2.models.v2_core import PromptBlock, SystemConfigModelRegistry, TaskBlueprint, Workflow

logger = logging.getLogger(__name__)

class StudioService:
    """Domain Service for Admin Studio resources enforcing Tenant Isolation and Authorization."""

    def __init__(self, repo: AbstractWorkflowRepository):
        self.repo = repo

    def _enforce_tenant_isolation(self, initiator: TokenData, data: dict[str, Any], resource_type: str, allow_system: bool = True) -> None:
        """Helper to enforce tenant boundaries for reads."""
        org_id = getattr(initiator, "organization_id", None)
        allowed_orgs = [org_id]
        if allow_system:
            allowed_orgs.append("system")
        # Legacy support
        allowed_orgs.append(None)

        if initiator.role != "ROOT" and data.get("organization_id") not in allowed_orgs:
            logger.error(f"[StudioService] PERMISSION_DENIED: User {initiator.uid} attempted to access isolated {resource_type} {data.get('id')}.")
            raise PermissionDeniedError(f"You do not have permission to view this {resource_type}.")

    def _enforce_modification_rights(self, initiator: TokenData, data_org_id: str | None, allow_system: bool = False) -> None:
        """Helper to enforce modification boundaries (e.g. only ROOT can modify system)."""
        org_id = getattr(initiator, "organization_id", None)
        if initiator.role != "ROOT":
            if data_org_id == "system" and not allow_system:
                raise PermissionDeniedError("Only ROOT can modify system resources.")
            if data_org_id not in [org_id, None]:
                raise PermissionDeniedError("Cannot modify resources outside your organization.")

    # --- Workflows ---

    async def list_workflows(self, initiator: TokenData) -> list[Workflow]:
        all_data = await self.repo.get_all("workflows")
        if initiator.role == "ROOT":
            return [Workflow.model_validate(x) for x in all_data]

        org_id = getattr(initiator, "organization_id", None)
        data = [x for x in all_data if x.get("organization_id") in [org_id, "system", None]]
        return [Workflow.model_validate(x) for x in data]

    async def get_workflow(self, initiator: TokenData, id: str) -> Workflow:
        data = await self.repo.get("workflows", id)
        if not data:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: Workflow {id} not found.")
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        self._enforce_tenant_isolation(initiator, data, "workflow")
        return Workflow.model_validate(data)

    async def save_workflow(self, initiator: TokenData, id: str, data: Workflow) -> Workflow:
        self._enforce_modification_rights(initiator, data.organization_id)

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.repo.create_raw("workflows", dump)

        saved = await self.repo.get("workflows", id)
        if not saved:
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)
        return Workflow.model_validate(saved)

    async def delete_workflow(self, initiator: TokenData, id: str) -> None:
        data = await self.repo.get("workflows", id)
        if not data:
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        self._enforce_modification_rights(initiator, data.get("organization_id"))
        await self.repo.delete("workflows", id)

    # --- Task Blueprints ---

    async def list_task_blueprints(self, initiator: TokenData) -> list[TaskBlueprint]:
        all_data = await self.repo.get_all("task_blueprints")
        if initiator.role == "ROOT":
            return [TaskBlueprint.model_validate(x) for x in all_data]

        org_id = getattr(initiator, "organization_id", None)
        data = [x for x in all_data if x.get("organization_id") in [org_id, "system", None]]
        return [TaskBlueprint.model_validate(x) for x in data]

    async def get_task_blueprint(self, initiator: TokenData, id: str) -> TaskBlueprint:
        data = await self.repo.get("task_blueprints", id)
        if not data:
            raise ResourceNotFoundError(resource_type="task_blueprint", resource_id=id)

        self._enforce_tenant_isolation(initiator, data, "task_blueprint")
        return TaskBlueprint.model_validate(data)

    async def save_task_blueprint(self, initiator: TokenData, id: str, data: TaskBlueprint) -> TaskBlueprint:
        self._enforce_modification_rights(initiator, data.organization_id)

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.repo.create_raw("task_blueprints", dump)

        saved = await self.repo.get("task_blueprints", id)
        if not saved:
            raise ResourceNotFoundError(resource_type="task_blueprint", resource_id=id)
        return TaskBlueprint.model_validate(saved)

    async def delete_task_blueprint(self, initiator: TokenData, id: str) -> None:
        data = await self.repo.get("task_blueprints", id)
        if not data:
            raise ResourceNotFoundError(resource_type="task_blueprint", resource_id=id)

        self._enforce_modification_rights(initiator, data.get("organization_id"))
        await self.repo.delete("task_blueprints", id)

    # --- Matrices ---

    async def list_matrices(self, initiator: TokenData) -> list[PromptBlock]:
        all_data = await self.repo.get_all("matrices")
        if initiator.role == "ROOT":
            return [PromptBlock.model_validate(x) for x in all_data]

        org_id = getattr(initiator, "organization_id", None)
        data = [x for x in all_data if x.get("organization_id") in [org_id, "system", None]]
        return [PromptBlock.model_validate(x) for x in data]

    async def get_matrix(self, initiator: TokenData, id: str) -> PromptBlock:
        data = await self.repo.get("matrices", id)
        if not data:
            raise ResourceNotFoundError(resource_type="matrix", resource_id=id)

        self._enforce_tenant_isolation(initiator, data, "matrix")
        return PromptBlock.model_validate(data)

    async def save_matrix(self, initiator: TokenData, id: str, data: PromptBlock) -> PromptBlock:
        self._enforce_modification_rights(initiator, data.organization_id)

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.repo.create_raw("matrices", dump)

        saved = await self.repo.get("matrices", id)
        if not saved:
            raise ResourceNotFoundError(resource_type="matrix", resource_id=id)
        return PromptBlock.model_validate(saved)

    async def delete_matrix(self, initiator: TokenData, id: str) -> None:
        data = await self.repo.get("matrices", id)
        if not data:
            raise ResourceNotFoundError(resource_type="matrix", resource_id=id)

        self._enforce_modification_rights(initiator, data.get("organization_id"))
        await self.repo.delete("matrices", id)

    # --- System Configs (ROOT Only usually) ---

    async def list_system_configs(self, initiator: TokenData) -> list[SystemConfigModelRegistry]:
        all_data = await self.repo.get_all("system_configs")
        if initiator.role == "ROOT":
            return [SystemConfigModelRegistry.model_validate(x) for x in all_data]
        return [] # Non-root sees no configs

    async def get_system_config(self, initiator: TokenData, id: str) -> SystemConfigModelRegistry:
        if initiator.role != "ROOT":
             raise PermissionDeniedError("Only ROOT can view system configs.")
        data = await self.repo.get("system_configs", id)
        if not data:
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigModelRegistry.model_validate(data)

    async def save_system_config(self, initiator: TokenData, id: str, data: SystemConfigModelRegistry) -> SystemConfigModelRegistry:
        if initiator.role != "ROOT":
             raise PermissionDeniedError("Only ROOT can modify system configs.")

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.repo.create_raw("system_configs", dump)

        saved = await self.repo.get("system_configs", id)
        if not saved:
             raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigModelRegistry.model_validate(saved)

    async def delete_system_config(self, initiator: TokenData, id: str) -> None:
        if initiator.role != "ROOT":
             raise PermissionDeniedError("Only ROOT can delete system configs.")

        data = await self.repo.get("system_configs", id)
        if not data:
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        await self.repo.delete("system_configs", id)
