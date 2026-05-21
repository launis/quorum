"""Studio Management Service."""

from __future__ import annotations

import logging
import string
import uuid
from typing import Any

from backend_v2.database.interfaces import (
    IComponentRepository,
    IKnowledgeRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.v2_core import PromptBlock, Step, SystemConfigMCPGateways, SystemConfigModelRegistry, Workflow
from backend_v2.services.orchestrator.atomizer import PromptAtomizer
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService

logger = logging.getLogger(__name__)


class StudioService:
    """Domain Service for Admin Studio resources enforcing Tenant Isolation and Authorization."""

    def __init__(
        self,
        workflow_repo: IWorkflowRepository,
        component_repo: IComponentRepository,
        knowledge_repo: IKnowledgeRepository,
        system_repo: ISystemRepository,
    ):
        self.workflow_repo = workflow_repo
        self.component_repo = component_repo
        self.knowledge_repo = knowledge_repo
        self.system_repo = system_repo

    def _enforce_tenant_isolation(
        self,
        initiator: TokenData,
        data_org_id: str | None,
        resource_type: str,
        resource_id: str,
        allow_system: bool = True,
    ) -> None:
        """Helper to enforce tenant boundaries for reads."""
        org_id = getattr(initiator, "organization_id", None)
        allowed_orgs = [org_id]
        if allow_system:
            allowed_orgs.append(SystemOrganizations.ROOT_SYSTEM)

        if initiator.role not in ["ROOT", UserRole.ROOT] and data_org_id not in allowed_orgs:
            logger.error(
                "[StudioService] PERMISSION_DENIED: User %s attempted to access isolated %s %s.",
                initiator.id,
                resource_type,
                resource_id,
            )
            raise PermissionDeniedError(f"You do not have permission to view this {resource_type}.")

    def _enforce_modification_rights(
        self, initiator: TokenData, data_org_id: str | None, allow_system: bool = False
    ) -> None:
        """Helper to enforce modification boundaries (e.g. only ROOT can modify system)."""
        if initiator.role not in ["ROOT", "ADMIN", "MANAGER", UserRole.ROOT, UserRole.ADMIN, UserRole.MANAGER]:
            logger.error(
                "[StudioService] %s: Only ADMIN or MANAGER can modify resources.", ErrorCodes.PERMISSION_DENIED.name
            )
            raise PermissionDeniedError("Only ADMIN or MANAGER can modify resources.")

        org_id = getattr(initiator, "organization_id", None)
        if initiator.role not in ["ROOT", UserRole.ROOT]:
            if data_org_id == SystemOrganizations.ROOT_SYSTEM and not allow_system:
                logger.error(
                    "[StudioService] %s: Only ROOT can modify system resources.", ErrorCodes.PERMISSION_DENIED.name
                )
                raise PermissionDeniedError("Only ROOT can modify system resources.")
            if data_org_id != org_id:
                msg = "Cannot modify resources outside your organization."
                logger.error(f"[StudioService] {ErrorCodes.PERMISSION_DENIED.value}: {msg}")
                raise PermissionDeniedError(msg)

    async def _stitch_profiles_to_workflows(self, workflows: list[Workflow]) -> list[Workflow]:
        """Dynamically attach standalone output profiles to the workflow dict for backward compatibility.
        Supports the client App during the V2 transition.
        """
        from backend_v2.models.v2_core import EmbeddedOutputProfile

        all_profiles_data = await self.component_repo.get_all_output_profiles()
        all_profiles = [OutputProfile.model_validate(p) for p in all_profiles_data]

        for wf in workflows:
            attached = {}
            for p in all_profiles:
                if p.workflow_id == wf.id or p.workflow_id == "*":
                    attached[p.id] = EmbeddedOutputProfile(
                        name=p.name,
                        description=p.description,
                        custom_preface=p.custom_preface,
                        visible_metadata=list(p.visible_metadata),
                        visible_extensions=list(p.visible_extensions),
                        max_extension_items=p.max_extension_items,
                        display_scale=p.display_scale,
                        synthesis=p.synthesis,
                        include_diagnostic_scorecard=p.include_diagnostic_scorecard,
                        strictness_level=p.strictness_level,
                        scoring_strategy=p.scoring_strategy,
                        layouts=list(p.layouts),
                    )

            if not isinstance(wf.output_profiles, dict):
                wf.output_profiles = {}
            wf.output_profiles.update(attached)

        return workflows

    # --- Workflows ---

    async def list_workflows(self, initiator: TokenData) -> list[Workflow]:
        all_data = await self.workflow_repo.get_all_workflows()
        workflows = [Workflow.model_validate(x) for x in all_data]

        if initiator.role in ["ROOT", UserRole.ROOT]:
            return await self._stitch_profiles_to_workflows(workflows)

        org_id = getattr(initiator, "organization_id", None)
        filtered = [x for x in workflows if x.organization_id in [org_id, SystemOrganizations.ROOT_SYSTEM]]
        return await self._stitch_profiles_to_workflows(filtered)

    async def get_workflow(self, initiator: TokenData, id: str) -> Workflow:
        data = await self.workflow_repo.get_workflow_by_id(id)
        if not data:
            logger.error("[StudioService] %s: Workflow %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        wf = Workflow.model_validate(data)
        self._enforce_tenant_isolation(initiator, wf.organization_id, "workflow", wf.id)

        stitched = await self._stitch_profiles_to_workflows([wf])
        return stitched[0]

    async def save_workflow(self, initiator: TokenData, id: str, data: Workflow) -> Workflow:
        self._enforce_modification_rights(initiator, data.organization_id)

        DAGCompilerService.validate_workflow(data)

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.workflow_repo.create_workflow(dump)

        saved = await self.workflow_repo.get_workflow_by_id(id)
        if not saved:
            logger.error("[StudioService] %s: Workflow %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)
        return Workflow.model_validate(saved)

    async def delete_workflow(self, initiator: TokenData, id: str) -> None:
        data = await self.workflow_repo.get_workflow_by_id(id)
        if not data:
            logger.error("[StudioService] %s: Workflow %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        wf = Workflow.model_validate(data)
        self._enforce_modification_rights(initiator, wf.organization_id)
        await self.workflow_repo.delete_workflow(id)

    async def create_workflow_draft(self, initiator: TokenData) -> Workflow:
        """System-level creation of an initial Workflow Draft."""
        new_id = f"wf_{uuid.uuid4().hex[:16]}"
        draft_dict: dict[str, Any] = {
            "id": new_id,
            "slug": new_id,
            "name": {"default_locale": "en", "translations": {"en": "New Työnkulku", "fi": "Uusi työnkulku"}},
            "description": {"default_locale": "en", "translations": {"en": "Draft workflow", "fi": "Luonnos"}},
            "status": "draft",
            "version": 1,
            "organization_id": (
                SystemOrganizations.ROOT_SYSTEM
                if initiator.role in ["ROOT", UserRole.ROOT]
                else getattr(initiator, "organization_id", None)
            ),
            "expected_inputs": [],
            "steps": [],
        }
        draft = Workflow.model_validate(draft_dict)
        return await self.save_workflow(initiator, new_id, draft)

    async def clone_workflow(self, initiator: TokenData, id: str) -> Workflow:
        """Deep Clones a Workflow into the initiator's tenant organization.
        Implements Shallow-Deep Copy constraint: StepRules are copied, TaskBlueprints are referenced.
        """
        data = await self.workflow_repo.get_workflow_by_id(id)
        if not data:
            logger.error("[StudioService] %s: Workflow %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        wf = Workflow.model_validate(data)
        self._enforce_tenant_isolation(initiator, wf.organization_id, "workflow", wf.id)

        new_id = f"wf_{uuid.uuid4().hex[:16]}"
        cloned_data = wf.model_dump(mode="json")
        cloned_data["id"] = new_id

        if initiator.role not in ["ROOT", UserRole.ROOT]:
            cloned_data["organization_id"] = getattr(initiator, "organization_id", None)

        if "name" in cloned_data and isinstance(cloned_data["name"], dict):
            for locale, text in cloned_data["name"].get("translations", {}).items():
                cloned_data["name"]["translations"][locale] = text + " (Copy)"
        elif "name" in cloned_data:
            cloned_data["name"] = str(cloned_data["name"]) + " (Copy)"

        sr_mapping = {}
        for step in cloned_data.get("steps", []):
            old_sr_id = step.get("id")
            if old_sr_id:
                new_sr_id = f"sr_{uuid.uuid4().hex[:16]}"
                sr_mapping[old_sr_id] = new_sr_id
                step["id"] = new_sr_id

        for step in cloned_data.get("steps", []):
            old_depends = step.get("depends_on", [])
            step["depends_on"] = [sr_mapping.get(dep, dep) for dep in old_depends]

            old_mappings = step.get("input_mappings", {})
            new_mappings = {}
            for k, v in old_mappings.items():
                if isinstance(v, str) and v.startswith("$steps."):
                    new_v = v
                    for old_sr, new_sr in sr_mapping.items():
                        new_v = new_v.replace(old_sr, new_sr)
                    new_mappings[k] = new_v
                else:
                    new_mappings[k] = v
            step["input_mappings"] = new_mappings

        # Deep clone standalone output profiles mapped to this old workflow
        all_profiles = await self.component_repo.get_all_output_profiles()
        profile_mapping = {}

        for p in all_profiles:
            if p.get("workflow_id") == id:
                new_profile_id = f"prof_{uuid.uuid4().hex[:30]}"
                profile_mapping[p.get("id")] = new_profile_id

                cloned_profile = p.copy()
                cloned_profile["id"] = new_profile_id
                cloned_profile["workflow_id"] = new_id
                if initiator.role not in ["ROOT", UserRole.ROOT]:
                    cloned_profile["organization_id"] = getattr(initiator, "organization_id", None)

                # Remap the step IDs inside layout
                for layout in cloned_profile.get("layouts", []):
                    old_layout_steps = layout.get("steps", [])
                    layout["steps"] = [sr_mapping.get(s, s) for s in old_layout_steps]

                await self.component_repo.create_output_profile(cloned_profile)

        # Update the default profile ID referencing the old profile
        if cloned_data.get("default_profile_id") in profile_mapping:
            cloned_data["default_profile_id"] = profile_mapping[cloned_data["default_profile_id"]]

        # Clear embedded profiles from workflow clone since they are standalone now
        if "output_profiles" in cloned_data:
            cloned_data["output_profiles"] = {}

        cloned_workflow = Workflow.model_validate(cloned_data)
        return await self.save_workflow(initiator, new_id, cloned_workflow)

    async def list_steps(self, initiator: TokenData) -> list[Step]:
        all_data = await self.workflow_repo.get_all_steps()
        steps = [Step.model_validate(x) for x in all_data]

        if initiator.role in ["ROOT", UserRole.ROOT]:
            return steps

        org_id = getattr(initiator, "organization_id", None)
        return [x for x in steps if x.organization_id in [org_id, SystemOrganizations.ROOT_SYSTEM]]

    async def get_step(self, initiator: TokenData, id: str) -> Step:
        data = await self.workflow_repo.get_step_by_id(id)
        if not data:
            logger.error("[StudioService] %s: Step %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

        step = Step.model_validate(data)
        self._enforce_tenant_isolation(initiator, step.organization_id, "step", step.id)
        return step

    async def save_step(self, initiator: TokenData, id: str, data: Step) -> Step:
        org_id = getattr(data, "organization_id", None)
        self._enforce_modification_rights(initiator, org_id)

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.workflow_repo.create_step(dump)

        saved = await self.workflow_repo.get_step_by_id(id)
        if not saved:
            logger.error("[StudioService] %s: Step %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="step", resource_id=id)
        return Step.model_validate(saved)

    async def delete_step(self, initiator: TokenData, id: str, force_delete: bool = False) -> None:
        data = await self.workflow_repo.get_step_by_id(id)
        if not data:
            logger.error("[StudioService] %s: Step %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

        step = Step.model_validate(data)
        self._enforce_modification_rights(initiator, step.organization_id)
        await self.workflow_repo.delete_step(id, force_delete=force_delete)

    async def create_step_draft(self, initiator: TokenData) -> Step:
        """System-level creation of an initial Step Draft."""
        new_id = f"step_{uuid.uuid4().hex[:16]}"
        draft_dict: dict[str, Any] = {
            "id": new_id,
            "slug": new_id,
            "name": {"default_locale": "en", "translations": {"en": "New Askel", "fi": "Uusi askel"}},
            "description": {"default_locale": "en", "translations": {"en": "Draft step", "fi": "Luonnos"}},
            "type": "llm",
            "prompt_blocks": ["blk_440a5fef9331451b"],
            "pre_hooks": [],
            "post_hooks": [],
            "safety": "safe",
            "allowed_mcp_tools": [],
            "model_strategy": "fast",
            "organization_id": (
                SystemOrganizations.ROOT_SYSTEM
                if initiator.role in ["ROOT", UserRole.ROOT]
                else getattr(initiator, "organization_id", None)
            ),
        }
        draft = Step.model_validate(draft_dict)
        return await self.save_step(initiator, new_id, draft)

    async def clone_step(self, initiator: TokenData, id: str) -> Step:
        """Deep Clones a Step into the initiator's tenant organization."""
        data = await self.workflow_repo.get_step_by_id(id)
        if not data:
            logger.error("[StudioService] %s: Step %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

        step = Step.model_validate(data)
        self._enforce_tenant_isolation(initiator, step.organization_id, "step", step.id)

        new_id = f"step_{uuid.uuid4().hex[:16]}"

        cloned_data = step.model_dump(mode="json")
        cloned_data["id"] = new_id

        if initiator.role not in ["ROOT", UserRole.ROOT]:
            cloned_data["organization_id"] = getattr(initiator, "organization_id", None)

        if "name" in cloned_data and isinstance(cloned_data["name"], dict):
            for locale, text in cloned_data["name"].get("translations", {}).items():
                cloned_data["name"]["translations"][locale] = text + " (Copy)"
        elif "name" in cloned_data:
            cloned_data["name"] = str(cloned_data["name"]) + " (Copy)"

        cloned_obj = Step.model_validate(cloned_data)
        return await self.save_step(initiator, new_id, cloned_obj)

    # --- Prompt Blocks ---

    async def list_prompt_blocks(self, initiator: TokenData) -> list[PromptBlock]:
        all_data = await self.component_repo.get_all_prompt_blocks()
        blocks = [PromptBlock.model_validate(x) for x in all_data]

        if initiator.role in ["ROOT", UserRole.ROOT]:
            return blocks

        org_id = getattr(initiator, "organization_id", None)
        return [x for x in blocks if x.organization_id in [org_id, SystemOrganizations.ROOT_SYSTEM]]

    async def get_prompt_block(self, initiator: TokenData, id: str) -> PromptBlock:
        data = await self.component_repo.get_prompt_block_by_id(id)
        if not data:
            logger.error("[StudioService] %s: PromptBlock %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)

        block = PromptBlock.model_validate(data)
        self._enforce_tenant_isolation(initiator, block.organization_id, "prompt_block", block.id)
        return block

    async def save_prompt_block(self, initiator: TokenData, id: str, data: PromptBlock) -> PromptBlock:
        org_id = getattr(data, "organization_id", None)
        self._enforce_modification_rights(initiator, org_id)

        # -- EPIC 20: Design-Time Syvä-atomisointi
        try:
            data = await PromptAtomizer.atomize_prompt_block(data, repository=self.system_repo)
        except Exception as e:
            logger.error("[StudioService] Atomization failed prior to save: %s", e)
            raise AppException(
                message=f"Atomization failed: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.AGENT_EXECUTION_CRITICAL},
            ) from e

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.component_repo.create_prompt_block(dump)

        saved = await self.component_repo.get_prompt_block_by_id(id)
        if not saved:
            logger.error("[StudioService] %s: PromptBlock %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)
        return PromptBlock.model_validate(saved)

    async def delete_prompt_block(self, initiator: TokenData, id: str, force_delete: bool = False) -> None:
        data = await self.component_repo.get_prompt_block_by_id(id)
        if not data:
            logger.error("[StudioService] %s: PromptBlock %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)

        block = PromptBlock.model_validate(data)
        self._enforce_modification_rights(initiator, block.organization_id)
        await self.component_repo.delete_prompt_block(id, force_delete=force_delete)

    async def create_prompt_block_draft(self, initiator: TokenData) -> PromptBlock:
        """System-level creation of an initial PromptBlock Draft."""
        new_id = f"blk_{uuid.uuid4().hex[:16]}"

        draft_dict: dict[str, Any] = {
            "id": new_id,
            "slug": new_id,
            "label": {"default_locale": "en", "translations": {"en": "New Block", "fi": "Uusi lohko"}},
            "description": {"default_locale": "en", "translations": {"en": "Draft block", "fi": "Luonnos"}},
            "ai_description": "Initial AI logic draft.",
            "category_id": "general",
            "type": "string",
            "allow_decimals": False,
            "output_extensions": [],
            "scales": None,
            "rows": None,
            "columns": None,
            "organization_id": (
                SystemOrganizations.ROOT_SYSTEM
                if initiator.role in ["ROOT", UserRole.ROOT]
                else getattr(initiator, "organization_id", None)
            ),
        }
        draft = PromptBlock.model_validate(draft_dict)
        return await self.save_prompt_block(initiator, new_id, draft)

    async def clone_prompt_block(self, initiator: TokenData, id: str) -> PromptBlock:
        """Deep Clones a PromptBlock into the initiator's tenant organization."""
        data = await self.component_repo.get_prompt_block_by_id(id)
        if not data:
            logger.error("[StudioService] %s: PromptBlock %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)

        block = PromptBlock.model_validate(data)
        self._enforce_tenant_isolation(initiator, block.organization_id, "prompt_block", block.id)

        new_id = f"blk_{uuid.uuid4().hex[:16]}"

        cloned_data = block.model_dump(mode="json")
        cloned_data["id"] = new_id

        if initiator.role not in ["ROOT", UserRole.ROOT]:
            cloned_data["organization_id"] = getattr(initiator, "organization_id", None)

        if "label" in cloned_data and isinstance(cloned_data["label"], dict):
            for locale, text in cloned_data["label"].get("translations", {}).items():
                cloned_data["label"]["translations"][locale] = text + " (Copy)"
        elif "label" in cloned_data:
            cloned_data["label"] = str(cloned_data["label"]) + " (Copy)"

        cloned_obj = PromptBlock.model_validate(cloned_data)
        return await self.save_prompt_block(initiator, new_id, cloned_obj)

    # --- System Configs (ROOT Only usually) ---

    def get_available_models(self, initiator: TokenData, llm_handler: Any) -> list[str]:
        """Fetches and flattens available models using the LLM Handler. Enforces ADMIN/ROOT."""
        if initiator.role not in [UserRole.ROOT, UserRole.ADMIN, "ROOT", "ADMIN"]:
            logger.error(
                "[StudioService] %s: User %s (Role: %s) attempted to fetch available models without ROOT or ADMIN.",
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
        if initiator.role == "ROOT":
            all_data = [await self.system_repo.get_model_registry()]
            if all_data[0]:
                return [
                    SystemConfigModelRegistry.model_validate(x) for x in all_data if x.get("type") == "model_registry"
                ]  # noqa: E501
        return []  # Non-root sees no configs

    async def get_system_config(self, initiator: TokenData, id: str) -> SystemConfigModelRegistry:
        if initiator.role != "ROOT":
            logger.error("[StudioService] %s: Only ROOT can view system configs.", ErrorCodes.PERMISSION_DENIED.name)
            raise PermissionDeniedError("Only ROOT can view system configs.")
        data = await self.system_repo.get_model_registry()
        if not data:
            logger.error("[StudioService] %s: SystemConfig %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigModelRegistry.model_validate(data)

    async def save_system_config(
        self, initiator: TokenData, id: str, data: SystemConfigModelRegistry
    ) -> SystemConfigModelRegistry:
        if initiator.role != "ROOT":
            logger.error("[StudioService] %s: Only ROOT can modify system configs.", ErrorCodes.PERMISSION_DENIED.name)
            raise PermissionDeniedError("Only ROOT can modify system configs.")

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.system_repo.update_model_registry(dump)

        saved = await self.system_repo.get_model_registry()
        if not saved:
            logger.error("[StudioService] %s: SystemConfig %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigModelRegistry.model_validate(saved)

    async def delete_system_config(self, initiator: TokenData, id: str) -> None:
        if initiator.role != "ROOT":
            logger.error("[StudioService] %s: Only ROOT can delete system configs.", ErrorCodes.PERMISSION_DENIED.name)
            raise PermissionDeniedError("Only ROOT can delete system configs.")

        data = await self.system_repo.get_model_registry()
        if not data:
            logger.error("[StudioService] %s: SystemConfig %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        # Deleting system config is a specific feature. In V2 we might just clear it or block it.
        # But for now, we leave it. Or maybe not implement since system repo doesn't have delete.

    async def create_model_registry_draft(self, initiator: TokenData) -> SystemConfigModelRegistry:
        """System-level creation of an initial ModelConfig Draft."""
        self._enforce_modification_rights(initiator, SystemOrganizations.ROOT_SYSTEM, allow_system=True)

        new_id = f"sys_{uuid.uuid4().hex[:16]}"
        draft_dict: dict[str, Any] = {"id": new_id, "slug": new_id, "type": "model_registry", "models": {}}
        draft = SystemConfigModelRegistry.model_validate(draft_dict)
        return await self.save_system_config(initiator, new_id, draft)

    async def clone_system_config(self, initiator: TokenData, id: str) -> SystemConfigModelRegistry:
        """Deep Clones a System Config for the ROOT tenant."""
        if initiator.role not in ["ROOT", UserRole.ROOT]:
            logger.error("[StudioService] %s: Only ROOT can clone system configs.", ErrorCodes.PERMISSION_DENIED.name)
            raise PermissionDeniedError("Only ROOT can clone system configs.")
        data = await self.system_repo.get_model_registry()
        if not data:
            logger.error("[StudioService] %s: SystemConfig %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)

        new_id = f"sys_{uuid.uuid4().hex}"

        cloned_data = SystemConfigModelRegistry.model_validate(data).model_dump(mode="json")
        cloned_data["id"] = new_id
        if "description" in cloned_data and getattr(cloned_data["description"], "strip", None) is not None:
            cloned_data["description"] = f"{cloned_data['description']} (Copy)"

        await self.system_repo.update_model_registry(cloned_data)

        saved = await self.system_repo.get_model_registry()
        return SystemConfigModelRegistry.model_validate(saved)

    async def list_mcp_gateways(self, initiator: TokenData) -> list[SystemConfigMCPGateways]:
        all_data = [await self.system_repo.get_mcp_gateways()]
        if all_data[0] and initiator.role == "ROOT":
            return [SystemConfigMCPGateways.model_validate(x) for x in all_data if x.get("type") == "mcp_gateways"]
        return []

    async def get_mcp_gateways(self, initiator: TokenData, id: str) -> SystemConfigMCPGateways:
        if initiator.role != "ROOT":
            logger.error("[StudioService] %s: Only ROOT can view system configs.", ErrorCodes.PERMISSION_DENIED.name)
            raise PermissionDeniedError("Only ROOT can view system configs.")
        data = await self.system_repo.get_mcp_gateways()
        if not data or data.get("type") != "mcp_gateways":
            logger.error(
                "[StudioService] %s: MCP Gateways Config %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigMCPGateways.model_validate(data)

    async def save_mcp_gateways(
        self, initiator: TokenData, id: str, data: SystemConfigMCPGateways
    ) -> SystemConfigMCPGateways:
        if initiator.role != "ROOT":
            logger.error("[StudioService] %s: Only ROOT can modify system configs.", ErrorCodes.PERMISSION_DENIED.name)
            raise PermissionDeniedError("Only ROOT can modify system configs.")

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.system_repo.update_mcp_gateways(dump)

        saved = await self.system_repo.get_mcp_gateways()
        if not saved:
            logger.error(
                "[StudioService] %s: MCP Gateways Config %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigMCPGateways.model_validate(saved)

    async def create_mcp_gateway_draft(self, initiator: TokenData) -> SystemConfigMCPGateways:
        """System-level creation of an initial MCP Gateway Config Draft."""
        self._enforce_modification_rights(initiator, SystemOrganizations.ROOT_SYSTEM, allow_system=True)

        new_id = f"mcp_{uuid.uuid4().hex[:16]}"
        draft_dict: dict[str, Any] = {"id": new_id, "slug": new_id, "type": "mcp_gateways", "tools": []}
        draft = SystemConfigMCPGateways.model_validate(draft_dict)
        return await self.save_mcp_gateways(initiator, new_id, draft)

    async def clone_mcp_gateways(self, initiator: TokenData, id: str) -> SystemConfigMCPGateways:
        """Deep Clones an MCP Gateway Config for the ROOT tenant."""
        if initiator.role not in ["ROOT", UserRole.ROOT]:
            logger.error("[StudioService] %s: Only ROOT can clone system configs.", ErrorCodes.PERMISSION_DENIED.name)
            raise PermissionDeniedError("Only ROOT can clone system configs.")
        data = await self.system_repo.get_mcp_gateways()
        if not data or data.get("type") != "mcp_gateways":
            logger.error("[StudioService] %s: MCP Gateway Config %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)

        new_id = f"mcp_{uuid.uuid4().hex}"

        cloned_data = SystemConfigMCPGateways.model_validate(data).model_dump(mode="json")
        cloned_data["id"] = new_id

        # Opaque pattern: copy the original slug so user realizes it needs modification
        if "description" in cloned_data and cloned_data["description"]:
            pass

        await self.system_repo.update_mcp_gateways(cloned_data)

        saved = await self.system_repo.get_mcp_gateways()
        return SystemConfigMCPGateways.model_validate(saved)

    async def list_system_configs(self, initiator: TokenData) -> list[SystemConfigModelRegistry]:
        data = await self.system_repo.get_model_registry()
        if data and initiator.role == "ROOT":
            return [SystemConfigModelRegistry.model_validate(data)]
        return []

    # --- Output Profiles ---

    async def list_output_profiles(self, initiator: TokenData) -> list[OutputProfile]:
        all_data = await self.component_repo.get_all_output_profiles()
        if initiator.role == "ROOT":
            return [OutputProfile.model_validate(x) for x in all_data]

        org_id = getattr(initiator, "organization_id", None)
        data = [x for x in all_data if x.get("organization_id") in [org_id, SystemOrganizations.ROOT_SYSTEM]]
        return [OutputProfile.model_validate(x) for x in data]

    async def get_output_profile(self, initiator: TokenData, id: str) -> OutputProfile:
        data = await self.component_repo.get_output_profile_by_id(id)
        if not data:
            logger.error("[StudioService] %s: Output Profile %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)

        profile = OutputProfile.model_validate(data)
        self._enforce_tenant_isolation(initiator, profile.organization_id, "output_profile", profile.id)
        return profile

    async def save_output_profile(
        self, initiator: TokenData, id: str, data: dict[str, Any] | OutputProfile
    ) -> OutputProfile:
        # Pydantic hydration for validation
        if isinstance(data, dict):
            profile = OutputProfile.model_validate(data)
        else:
            profile = data

        self._enforce_modification_rights(initiator, getattr(profile, "organization_id", None))

        # Workflow Constraint Validation:
        # Output Profile components MUST belong to the targeted Workflow DAG.
        workflow = await self.get_workflow(initiator, profile.workflow_id)
        all_steps = await self.list_steps(initiator)

        task_blueprints = {rule.task_blueprint for rule in workflow.steps}
        allowed_blocks = set()

        for step in all_steps:
            if step.id in task_blueprints:
                allowed_blocks.update(step.prompt_blocks)

        for layout in profile.layouts:
            for comp in layout.target_blocks:
                if comp != "*" and comp not in allowed_blocks:
                    msg = f"Target Component '{comp}' does not exist in the context of Workflow '{workflow.slug}'."
                    logger.error("[StudioService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED}
                    )

        dump = profile.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id

        await self.component_repo.create_output_profile(dump)

        saved = await self.component_repo.get_output_profile_by_id(id)
        if not saved:
            logger.error(
                "[StudioService] %s: Output Profile %s not found after save.", ErrorCodes.RESOURCE_NOT_FOUND.name, id
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)
        return OutputProfile.model_validate(saved)

    async def delete_output_profile(self, initiator: TokenData, id: str) -> None:
        data = await self.component_repo.get_output_profile_by_id(id)
        if not data:
            logger.error("[StudioService] %s: Output Profile %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)

        self._enforce_modification_rights(initiator, data.get("organization_id"))
        await self.component_repo.delete_output_profile(id)

    async def create_output_profile_draft(self, initiator: TokenData) -> OutputProfile:
        """System-level creation of an initial OutputProfile Draft."""
        new_id = f"opt_{uuid.uuid4().hex[:16]}"
        draft_dict: dict[str, Any] = {
            "id": new_id,
            "slug": new_id,
            "name": {"default_locale": "en", "translations": {"en": "New Profile", "fi": "Uusi profiili"}},
            "category_id": "report",
            "layouts": [
                {"layout_type": "default_pdf", "layout_config": {"columns": 1, "theme": "light"}, "blocks": []}
            ],
            "organization_id": (
                SystemOrganizations.ROOT_SYSTEM
                if initiator.role in ["ROOT", UserRole.ROOT]
                else getattr(initiator, "organization_id", None)
            ),
        }
        draft = OutputProfile.model_validate(draft_dict)
        return await self.save_output_profile(initiator, new_id, draft)

    async def clone_output_profile(self, initiator: TokenData, id: str) -> OutputProfile:
        """Deep Clones an Output Profile into the initiator's tenant organization."""
        data = await self.component_repo.get_output_profile_by_id(id)
        if not data:
            logger.error("[StudioService] %s: OutputProfile %s not found.", ErrorCodes.RESOURCE_NOT_FOUND.name, id)
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)

        profile = OutputProfile.model_validate(data)
        self._enforce_tenant_isolation(initiator, profile.organization_id, "output_profile", profile.id)

        new_id = f"prof_{uuid.uuid4().hex}"

        cloned_data = profile.model_dump(mode="json")
        cloned_data["id"] = new_id

        if initiator.role not in ["ROOT", UserRole.ROOT]:
            cloned_data["organization_id"] = getattr(initiator, "organization_id", None)

        if "name" in cloned_data and isinstance(cloned_data["name"], dict):
            default_locale = cloned_data["name"].get("default_locale", "en")
            translations = cloned_data["name"].get("translations", {})
            if default_locale in translations:
                translations[default_locale] = translations[default_locale] + " (Copy)"
                cloned_data["name"]["translations"] = translations
        elif "name" in cloned_data and isinstance(cloned_data["name"], str):
            cloned_data["name"] = cloned_data["name"] + " (Copy)"

        await self.component_repo.create_output_profile(cloned_data)

        saved = await self.component_repo.get_output_profile_by_id(new_id)
        if not saved:
            logger.error(
                "[StudioService] %s: OutputProfile %s not found after clone.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                new_id,
            )
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=new_id)

        return OutputProfile.model_validate(saved)

    # --- Workflow Simulation (DAG Dry-Run) ---
    async def simulate_workflow(self, initiator: TokenData, data: Workflow) -> dict[str, Any]:
        """Provides a static analysis of a Workflow DAG to validate dependencies and input wirings."""
        errors = []
        step_status = {}

        # 1. Map expected inputs
        available_inputs = [inp.input_key for inp in data.expected_inputs]

        # 2. Track provided outputs step by step
        _provided_outputs = set(available_inputs)

        # 3. Build Dependency Graph
        dag_order = []
        visited = set()
        in_progress = set()

        all_steps = {s.id: s for s in data.steps}

        def resolve_deps(step_id: str) -> None:
            if step_id in in_progress:
                errors.append(f"Cycle detected involving step {step_id}")
                return
            if step_id in visited:
                return

            in_progress.add(step_id)
            step = all_steps.get(step_id)
            if not step:
                # Missing reference in depends_on
                return

            for dep in step.depends_on:
                resolve_deps(dep)

            in_progress.remove(step_id)
            visited.add(step_id)
            dag_order.append(step_id)

        try:
            for s_id in all_steps:
                resolve_deps(s_id)
        except Exception as e:
            logger.error("[StudioService] Simulation graph resolution failed: %s", e)
            errors.append("Fatal error resolving DAG structure.")

        # 4. Step-by-Step topological check
        for step_id in dag_order:
            step = all_steps[step_id]
            is_valid = True
            step_errors = []

            # Check mappings
            for _tgt, src in step.input_mappings.items():
                if isinstance(src, str) and src.startswith("$"):
                    if src.startswith("$inputs."):
                        var = src.split(".")[1]
                        if var not in available_inputs:
                            step_errors.append(f"Missing input reference: {var}")
                            is_valid = False
                    elif src.startswith("$steps."):
                        parts = src.split(".")
                        if len(parts) >= 3:
                            dep_step = parts[1]
                            if dep_step not in step.depends_on:
                                step_errors.append(f"Undeclared dependency on step: {dep_step}")
                                is_valid = False

            if is_valid:
                step_status[step_id] = "OK"
            else:
                step_status[step_id] = "ERROR"
                errors.extend([f"Step {step_id}: {e}" for e in step_errors])

        return {"valid": len(errors) == 0, "errors": errors, "step_status": step_status, "execution_order": dag_order}

    async def simulate_prompt_block(
        self, initiator: TokenData, data: PromptBlock, mock_inputs: dict[str, Any]
    ) -> dict[str, Any]:
        """Provides a static analysis of a PromptBlock template rendering, including BARS matrix claims."""
        errors: list[str] = []
        rendered = data.ai_description or ""

        # 1. Base rendering using template syntax if needed
        if rendered and mock_inputs:
            # Basic python formatting simulation if {} brackets exist
            if "{" in rendered and "}" in rendered:
                # Very simple loose formatting for dry-run safely
                t = string.Formatter()
                keys = [k[1] for k in t.parse(rendered) if k[1] is not None]
                clean_mocks = {k: mock_inputs.get(k, f"[{k} MOCKED]") for k in keys}
                rendered = rendered.format(**clean_mocks)

        # 2. Append Matrix Logic
        if data.category_id == "matrix" and data.scales:
            rendered += "\n\n--- EVALUATION SCALES ---\n"
            for scale in data.scales:
                rendered += f"\nScore {scale.score}:\n"
                for claim in scale.claims:
                    fallback = claim.label.translations.get(claim.label.default_locale, "")
                    en_text = claim.label.translations.get("en", fallback)
                    if en_text:
                        rendered += f"- {en_text.strip()}\n"
                    if getattr(claim, "ai_description", None):
                        rendered += f"  Rule: {claim.ai_description.strip()}\n"

        return {"valid": len(errors) == 0, "errors": errors, "rendered_prompt": rendered.strip()}

    async def simulate_step(self, initiator: TokenData, data: Step, mock_inputs: dict[str, Any]) -> dict[str, Any]:
        """Provides a static analysis of a Step's generated context by resolving all its Prompt Blocks."""
        errors = []
        rendered_parts = []

        # Resolve prompt blocks
        for block_ref in data.prompt_blocks:
            try:
                block = await self.get_prompt_block(initiator, block_ref)
                sim = await self.simulate_prompt_block(initiator, block, mock_inputs)
                if not sim["valid"]:
                    errors.extend(sim.get("errors", []))

                rendered_parts.append(f"--- Prompt Block: {block.id} ---")
                rendered_parts.append(sim.get("rendered_prompt", ""))
            except ResourceNotFoundError:
                errors.append(f"Missing referenced Prompt Block: {block_ref}")
                rendered_parts.append(f"--- Prompt Block: {block_ref} [NOT FOUND] ---")

        if data.hook:
            rendered_parts.append(f"\n[Execution Hook: {data.hook}]")

        return {"valid": len(errors) == 0, "errors": errors, "rendered_prompt": "\n\n".join(rendered_parts)}
