"""Studio Management Service."""

from __future__ import annotations

import logging
from typing import Any

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.v2_core import PromptBlock, Step, SystemConfigMCPGateways, SystemConfigModelRegistry, Workflow

logger = logging.getLogger(__name__)

class StudioService:
    """Domain Service for Admin Studio resources enforcing Tenant Isolation and Authorization."""

    def __init__(self, repo: AbstractWorkflowRepository):
        self.repo = repo

    def _enforce_tenant_isolation(
        self, initiator: TokenData, data: dict[str, Any], resource_type: str, allow_system: bool = True
    ) -> None:
        """Helper to enforce tenant boundaries for reads."""
        org_id = getattr(initiator, "organization_id", None)
        allowed_orgs = [org_id]
        if allow_system:
            allowed_orgs.append("system")
        # Legacy support
        allowed_orgs.append(None)

        if initiator.role != "ROOT" and data.get("organization_id") not in allowed_orgs:
            logger.error(
                f"[StudioService] PERMISSION_DENIED: User {initiator.id} "
                f"attempted to access isolated {resource_type} {data.get('id')}."
            )
            raise PermissionDeniedError(f"You do not have permission to view this {resource_type}.")

    def _enforce_modification_rights(
        self, initiator: TokenData, data_org_id: str | None, allow_system: bool = False
    ) -> None:
        """Helper to enforce modification boundaries (e.g. only ROOT can modify system)."""
        if initiator.role not in ["ROOT", "ADMIN", "MANAGER", UserRole.ROOT, UserRole.ADMIN, UserRole.MANAGER]:
            logger.error(
                f"[StudioService] {ErrorCodes.PERMISSION_DENIED.name}: "
                "Only ADMIN or MANAGER can modify resources."
            )
            raise PermissionDeniedError("Only ADMIN or MANAGER can modify resources.")

        org_id = getattr(initiator, "organization_id", None)
        if initiator.role not in ["ROOT", UserRole.ROOT]:
            if data_org_id == "system" and not allow_system:
                logger.error(
                    f"[StudioService] {ErrorCodes.PERMISSION_DENIED.name}: "
                    "Only ROOT can modify system resources."
                )
                raise PermissionDeniedError("Only ROOT can modify system resources.")
            if data_org_id not in [org_id, None]:
                logger.error(
                    f"[StudioService] {ErrorCodes.PERMISSION_DENIED.name}: "
                    "Cannot modify resources outside your organization."
                )
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

        from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
        DAGCompilerService.validate_workflow(data)

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.repo.create_raw("workflows", dump)

        saved = await self.repo.get("workflows", id)
        if not saved:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: Workflow {id} not found.")
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)
        return Workflow.model_validate(saved)

    async def delete_workflow(self, initiator: TokenData, id: str) -> None:
        data = await self.repo.get("workflows", id)
        if not data:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: Workflow {id} not found.")
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        self._enforce_modification_rights(initiator, data.get("organization_id"))
        await self.repo.delete("workflows", id)

    async def clone_workflow(self, initiator: TokenData, id: str) -> Workflow:
        """Deep Clones a Workflow into the initiator's tenant organization.
        Implements Shallow-Deep Copy constraint: StepRules are copied, TaskBlueprints are referenced.
        """
        data = await self.repo.get("workflows", id)
        if not data:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: Workflow {id} not found.")
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        self._enforce_tenant_isolation(initiator, data, "workflow")

        import uuid
        new_id = f"wf_{uuid.uuid4().hex}"

        cloned_data = Workflow.model_validate(data).model_dump(mode="json")
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

        await self.repo.create_raw("workflows", cloned_data)

        saved = await self.repo.get("workflows", new_id)
        if not saved:
            logger.error(
                f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: "
                f"Workflow {new_id} not found after clone."
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=new_id)

        return Workflow.model_validate(saved)

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
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: Step {id} not found.")
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

        self._enforce_tenant_isolation(initiator, data, "step")
        return Step.model_validate(data)

    async def save_step(self, initiator: TokenData, id: str, data: Step) -> Step:
        org_id = getattr(data, "organization_id", None)
        self._enforce_modification_rights(initiator, org_id)

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.repo.create_raw("steps", dump)

        saved = await self.repo.get("steps", id)
        if not saved:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: Step {id} not found.")
            raise ResourceNotFoundError(resource_type="step", resource_id=id)
        return Step.model_validate(saved)

    async def delete_step(self, initiator: TokenData, id: str, force_delete: bool = False) -> None:
        data = await self.repo.get("steps", id)
        if not data:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: Step {id} not found.")
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

        self._enforce_modification_rights(initiator, data.get("organization_id"))
        await self.repo.delete_step(id, force_delete=force_delete)

    async def clone_step(self, initiator: TokenData, id: str) -> Step:
        """Deep Clones a Step into the initiator's tenant organization."""
        data = await self.repo.get("steps", id)
        if not data:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: Step {id} not found.")
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

        self._enforce_tenant_isolation(initiator, data, "step")

        import uuid
        new_id = f"step_{uuid.uuid4().hex}"

        cloned_data = Step.model_validate(data).model_dump(mode="json")
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

        await self.repo.create_raw("steps", cloned_data)

        saved = await self.repo.get("steps", new_id)
        if not saved:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: Step {new_id} not found after clone.")
            raise ResourceNotFoundError(resource_type="step", resource_id=new_id)

        return Step.model_validate(saved)

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
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: PromptBlock {id} not found.")
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
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: PromptBlock {id} not found.")
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)
        return PromptBlock.model_validate(saved)

    async def delete_prompt_block(self, initiator: TokenData, id: str, force_delete: bool = False) -> None:
        data = await self.repo.get("prompt_blocks", id)
        if not data:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: PromptBlock {id} not found.")
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)

        self._enforce_modification_rights(initiator, data.get("organization_id"))
        await self.repo.delete_prompt_block(id, force_delete=force_delete)

    async def clone_prompt_block(self, initiator: TokenData, id: str) -> PromptBlock:
        """Deep Clones a PromptBlock into the initiator's tenant organization."""
        data = await self.repo.get("prompt_blocks", id)
        if not data:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: PromptBlock {id} not found.")
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=id)

        self._enforce_tenant_isolation(initiator, data, "prompt_block")

        import uuid
        new_id = f"blk_{uuid.uuid4().hex}"

        cloned_data = PromptBlock.model_validate(data).model_dump(mode="json")
        cloned_data["id"] = new_id

        if initiator.role not in ["ROOT", UserRole.ROOT]:
             cloned_data["organization_id"] = getattr(initiator, "organization_id", None)

        if "label" in cloned_data and isinstance(cloned_data["label"], dict):
             default_locale = cloned_data["label"].get("default_locale", "en")
             translations = cloned_data["label"].get("translations", {})
             if default_locale in translations:
                 translations[default_locale] = translations[default_locale] + " (Copy)"
                 cloned_data["label"]["translations"] = translations

        await self.repo.create_raw("prompt_blocks", cloned_data)

        saved = await self.repo.get("prompt_blocks", new_id)
        if not saved:
            logger.error(
                f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: "
                f"PromptBlock {new_id} not found after clone."
            )
            raise ResourceNotFoundError(resource_type="prompt_block", resource_id=new_id)

        return PromptBlock.model_validate(saved)

    # --- System Configs (ROOT Only usually) ---

    async def list_system_configs(self, initiator: TokenData) -> list[SystemConfigModelRegistry]:
        all_data = await self.repo.get_all("system_config")
        if initiator.role == "ROOT":
            return [SystemConfigModelRegistry.model_validate(x) for x in all_data if x.get("type") == "model_registry"]
        return [] # Non-root sees no configs

    async def get_system_config(self, initiator: TokenData, id: str) -> SystemConfigModelRegistry:
        if initiator.role != "ROOT":
             logger.error(f"[StudioService] {ErrorCodes.PERMISSION_DENIED.name}: Only ROOT can view system configs.")
             raise PermissionDeniedError("Only ROOT can view system configs.")
        data = await self.repo.get("system_config", id)
        if not data:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: SystemConfig {id} not found.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigModelRegistry.model_validate(data)

    async def save_system_config(
        self, initiator: TokenData, id: str, data: SystemConfigModelRegistry
    ) -> SystemConfigModelRegistry:
        if initiator.role != "ROOT":
             logger.error(
                 f"[StudioService] {ErrorCodes.PERMISSION_DENIED.name}: "
                 "Only ROOT can modify system configs."
             )
             raise PermissionDeniedError("Only ROOT can modify system configs.")

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.repo.create_raw("system_config", dump)

        saved = await self.repo.get("system_config", id)
        if not saved:
             logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: SystemConfig {id} not found.")
             raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigModelRegistry.model_validate(saved)

    async def delete_system_config(self, initiator: TokenData, id: str) -> None:
        if initiator.role != "ROOT":
             logger.error(f"[StudioService] {ErrorCodes.PERMISSION_DENIED.name}: Only ROOT can delete system configs.")
             raise PermissionDeniedError("Only ROOT can delete system configs.")

        data = await self.repo.get("system_config", id)
        if not data:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: SystemConfig {id} not found.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        await self.repo.delete("system_config", id)

    async def clone_system_config(self, initiator: TokenData, id: str) -> SystemConfigModelRegistry:
        """Deep Clones a System Config for the ROOT tenant."""
        if initiator.role != "ROOT":
             logger.error(f"[StudioService] {ErrorCodes.PERMISSION_DENIED.name}: Only ROOT can clone system configs.")
             raise PermissionDeniedError("Only ROOT can clone system configs.")
        data = await self.repo.get("system_config", id)
        if not data:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: SystemConfig {id} not found.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)

        import uuid
        new_id = f"system_config_{uuid.uuid4().hex}"

        cloned_data = SystemConfigModelRegistry.model_validate(data).model_dump(mode="json")
        cloned_data["id"] = new_id
        if "description" in cloned_data:
             cloned_data["description"] = f"{cloned_data['description']} (Copy)"

        await self.repo.create_raw("system_config", cloned_data)

        saved = await self.repo.get("system_config", new_id)
        return SystemConfigModelRegistry.model_validate(saved)

    async def list_mcp_gateways(self, initiator: TokenData) -> list[SystemConfigMCPGateways]:
        all_data = await self.repo.get_all("system_config")
        if initiator.role == "ROOT":
            return [SystemConfigMCPGateways.model_validate(x) for x in all_data if x.get("type") == "mcp_gateways"]
        return []

    async def get_mcp_gateways(self, initiator: TokenData, id: str) -> SystemConfigMCPGateways:
        if initiator.role != "ROOT":
             logger.error(f"[StudioService] {ErrorCodes.PERMISSION_DENIED.name}: Only ROOT can view system configs.")
             raise PermissionDeniedError("Only ROOT can view system configs.")
        data = await self.repo.get("system_config", id)
        if not data or data.get("type") != "mcp_gateways":
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: MCP Gateways Config {id} not found.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigMCPGateways.model_validate(data)

    async def save_mcp_gateways(
        self, initiator: TokenData, id: str, data: SystemConfigMCPGateways
    ) -> SystemConfigMCPGateways:
        if initiator.role != "ROOT":
             logger.error(
                 f"[StudioService] {ErrorCodes.PERMISSION_DENIED.name}: "
                 "Only ROOT can modify system configs."
             )
             raise PermissionDeniedError("Only ROOT can modify system configs.")

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.repo.create_raw("system_config", dump)

        saved = await self.repo.get("system_config", id)
        if not saved:
             logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: MCP Gateways Config {id} not found.")
             raise ResourceNotFoundError(resource_type="system_config", resource_id=id)
        return SystemConfigMCPGateways.model_validate(saved)

    async def clone_mcp_gateways(self, initiator: TokenData, id: str) -> SystemConfigMCPGateways:
        """Deep Clones an MCP Gateway Config for the ROOT tenant."""
        if initiator.role != "ROOT":
             logger.error(f"[StudioService] {ErrorCodes.PERMISSION_DENIED.name}: Only ROOT can clone system configs.")
             raise PermissionDeniedError("Only ROOT can clone system configs.")
        data = await self.repo.get("system_config", id)
        if not data or data.get("type") != "mcp_gateways":
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: MCP Gateway Config {id} not found.")
            raise ResourceNotFoundError(resource_type="system_config", resource_id=id)

        import uuid
        new_id = f"mcp_{uuid.uuid4().hex}"

        cloned_data = SystemConfigMCPGateways.model_validate(data).model_dump(mode="json")
        cloned_data["id"] = new_id
        
        # Opaque pattern: copy the original slug so user realizes it needs modification
        if "description" in cloned_data and cloned_data["description"]:
             pass 

        await self.repo.create_raw("system_config", cloned_data)

        saved = await self.repo.get("system_config", new_id)
        return SystemConfigMCPGateways.model_validate(saved)

    # --- Output Profiles ---

    async def list_output_profiles(self, initiator: TokenData) -> list[OutputProfile]:
        all_data = await self.repo.get_all_output_profiles()
        if initiator.role == "ROOT":
            return [OutputProfile.model_validate(x) for x in all_data]

        org_id = getattr(initiator, "organization_id", None)
        data = [x for x in all_data if x.get("organization_id") in [org_id, "system", None]]
        return [OutputProfile.model_validate(x) for x in data]

    async def get_output_profile(self, initiator: TokenData, id: str) -> OutputProfile:
        data = await self.repo.get_output_profile_by_id(id)
        if not data:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: Output Profile {id} not found.")
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)

        self._enforce_tenant_isolation(initiator, data, "output_profile")
        return OutputProfile.model_validate(data)

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
            if step.slug in task_blueprints or step.id in task_blueprints:
                allowed_blocks.update(step.prompt_blocks)

        for layout in profile.layouts:
            for comp in layout.components:
                if comp != "*" and comp not in allowed_blocks:
                    msg = f"Target Component '{comp}' does not exist in the context of Workflow '{workflow.slug}'."
                    logger.error(f"[StudioService] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
                    raise AppException(
                        message=msg,
                        status_code=400,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED}
                    )

        dump = profile.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id

        # Enforce synchronous create
        await self.repo.create_output_profile(dump)

        saved = await self.repo.get_output_profile_by_id(id)
        if not saved:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: "
                         f"Output Profile {id} not found after save.")
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)
        return OutputProfile.model_validate(saved)

    async def delete_output_profile(self, initiator: TokenData, id: str) -> None:
        data = await self.repo.get_output_profile_by_id(id)
        if not data:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: Output Profile {id} not found.")
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)

        self._enforce_modification_rights(initiator, data.get("organization_id"))
        await self.repo.delete_output_profile(id)

    async def clone_output_profile(self, initiator: TokenData, id: str) -> OutputProfile:
        """Deep Clones an Output Profile into the initiator's tenant organization."""
        data = await self.repo.get_output_profile_by_id(id)
        if not data:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: OutputProfile {id} not found.")
            raise ResourceNotFoundError(resource_type="output_profile", resource_id=id)

        self._enforce_tenant_isolation(initiator, data, "output_profile")

        import uuid
        new_id = f"profile_{uuid.uuid4().hex}"

        cloned_data = OutputProfile.model_validate(data).model_dump(mode="json")
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

        await self.repo.create_output_profile(cloned_data)

        saved = await self.repo.get_output_profile_by_id(new_id)
        if not saved:
            logger.error(f"[StudioService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: OutputProfile {new_id} not found after clone.")
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
            logger.error(f"[StudioService] Simulation graph resolution failed: {e}")
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

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "step_status": step_status,
            "execution_order": dag_order
        }

    async def simulate_prompt_block(
        self, initiator: TokenData, data: PromptBlock, mock_inputs: dict[str, Any]
    ) -> dict[str, Any]:
        """Provides a static analysis of a PromptBlock template rendering, including BARS matrix claims."""
        import string

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

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "rendered_prompt": rendered.strip()
        }

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

                rendered_parts.append(f"--- Prompt Block: {block.slug} ---")
                rendered_parts.append(sim.get("rendered_prompt", ""))
            except ResourceNotFoundError:
                errors.append(f"Missing referenced Prompt Block: {block_ref}")
                rendered_parts.append(f"--- Prompt Block: {block_ref} [NOT FOUND] ---")

        if data.hook:
            rendered_parts.append(f"\n[Execution Hook: {data.hook}]")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "rendered_prompt": "\n\n".join(rendered_parts)
        }
