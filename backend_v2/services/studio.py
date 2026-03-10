"""Studio Management Service."""

from __future__ import annotations

import logging
from typing import Any

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData
from backend_v2.models.v2_core import PromptBlock, Step, SystemConfigModelRegistry, Workflow

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
            logger.error(f"[StudioService] PERMISSION_DENIED: User {initiator.id} attempted to access isolated {resource_type} {data.get('id')}.")
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
        if initiator.role != "ROOT":
            raise PermissionDeniedError("Only ROOT can modify workflows.")
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
        if initiator.role != "ROOT":
            raise PermissionDeniedError("Only ROOT can delete workflows.")
        data = await self.repo.get("workflows", id)
        if not data:
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        self._enforce_modification_rights(initiator, data.get("organization_id"))
        await self.repo.delete("workflows", id)

    async def list_steps(self, initiator: TokenData) -> list[Step]:
        all_data = await self.repo.get_all("steps")
        if initiator.role == "ROOT":
            return [Step.model_validate(x) for x in all_data]

        org_id = getattr(initiator, "organization_id", None)
        data = [x for x in all_data if x.get("organization_id") in [org_id, "system", None]]
        return [Step.model_validate(x) for x in data]

    async def get_step(self, initiator: TokenData, id: str) -> Step:
        data = await self.repo.get("steps", id)
        if not data:
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

        self._enforce_tenant_isolation(initiator, data, "step")
        return Step.model_validate(data)

    async def save_step(self, initiator: TokenData, id: str, data: Step) -> Step:
        if initiator.role != "ROOT":
            raise PermissionDeniedError("Only ROOT can modify steps.")
        org_id = getattr(data, "organization_id", None)
        self._enforce_modification_rights(initiator, org_id)

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.repo.create_raw("steps", dump)

        saved = await self.repo.get("steps", id)
        if not saved:
            raise ResourceNotFoundError(resource_type="step", resource_id=id)
        return Step.model_validate(saved)

    async def delete_step(self, initiator: TokenData, id: str, force_delete: bool = False) -> None:
        if initiator.role != "ROOT":
            raise PermissionDeniedError("Only ROOT can delete steps.")
        data = await self.repo.get("steps", id)
        if not data:
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

        self._enforce_modification_rights(initiator, data.get("organization_id"))
        await self.repo.delete_step(id, force_delete=force_delete)

    # --- Prompt Blocks ---

    async def list_prompt_blocks(self, initiator: TokenData) -> list[PromptBlock]:
        all_data = await self.repo.get_all("prompt_blocks")
        if initiator.role == "ROOT":
            return [PromptBlock.model_validate(x) for x in all_data]

        org_id = getattr(initiator, "organization_id", None)
        data = [x for x in all_data if x.get("organization_id") in [org_id, "system", None]]
        return [PromptBlock.model_validate(x) for x in data]

    async def get_prompt_block(self, initiator: TokenData, id: str) -> PromptBlock:
        data = await self.repo.get("prompt_blocks", id)
        if not data:
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)

        self._enforce_tenant_isolation(initiator, data, "prompt_block")
        return PromptBlock.model_validate(data)

    async def save_prompt_block(self, initiator: TokenData, id: str, data: PromptBlock) -> PromptBlock:
        org_id = getattr(data, "organization_id", None)
        self._enforce_modification_rights(initiator, org_id)

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.repo.create_raw("prompt_blocks", dump)

        saved = await self.repo.get("prompt_blocks", id)
        if not saved:
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)
        return PromptBlock.model_validate(saved)

    async def delete_prompt_block(self, initiator: TokenData, id: str, force_delete: bool = False) -> None:
        data = await self.repo.get("prompt_blocks", id)
        if not data:
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)

        self._enforce_modification_rights(initiator, data.get("organization_id"))
        await self.repo.delete_prompt_block(id, force_delete=force_delete)

    # --- System Configs (ROOT Only usually) ---

    async def list_system_configs(self, initiator: TokenData) -> list[SystemConfigModelRegistry]:
        all_data = await self.repo.get_all("system_config")
        if initiator.role == "ROOT":
            return [SystemConfigModelRegistry.model_validate(x) for x in all_data]
        return [] # Non-root sees no configs

    async def get_system_config(self, initiator: TokenData, id: str) -> SystemConfigModelRegistry:
        if initiator.role != "ROOT":
             raise PermissionDeniedError("Only ROOT can view system configs.")
        data = await self.repo.get("system_config", id)
        if not data:
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigModelRegistry.model_validate(data)

    async def save_system_config(self, initiator: TokenData, id: str, data: SystemConfigModelRegistry) -> SystemConfigModelRegistry:
        if initiator.role != "ROOT":
             raise PermissionDeniedError("Only ROOT can modify system configs.")

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.repo.create_raw("system_config", dump)

        saved = await self.repo.get("system_config", id)
        if not saved:
             raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigModelRegistry.model_validate(saved)

    async def delete_system_config(self, initiator: TokenData, id: str) -> None:
        if initiator.role != "ROOT":
             raise PermissionDeniedError("Only ROOT can delete system configs.")

        data = await self.repo.get("system_config", id)
        if not data:
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        await self.repo.delete("system_config", id)
