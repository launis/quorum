"""Studio Workflow Service."""

import logging
import uuid
from typing import Any

from pydantic import ValidationError

from backend_v2.database.interfaces import (
    IOutputProfileRepository,
    IPromptBlockRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.v2_core import (
    EmbeddedOutputProfile,
    PromptBlock,
    Step,
    Workflow,
)
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.services.studio.auth_validator import (
    enforce_modification_rights,
    enforce_tenant_isolation,
)

logger = logging.getLogger(__name__)


class StudioWorkflowService:
    """Domain Service for Admin Studio Workflow and Step resources."""

    def __init__(
        self,
        workflow_repo: IWorkflowRepository,
        output_profile_repo: IOutputProfileRepository,
        prompt_block_repo: IPromptBlockRepository,
    ):
        """Initialize the service.

        Args:
            workflow_repo: Workflow repository instance.
            output_profile_repo: Output profile repository instance.
            prompt_block_repo: Prompt block repository instance.
        """
        self.workflow_repo = workflow_repo
        self.output_profile_repo = output_profile_repo
        self.prompt_block_repo = prompt_block_repo

    async def _stitch_profiles_to_workflows(self, workflows: list[Workflow]) -> list[Workflow]:
        """Stitch profiles to workflows.

        Args:
            workflows: List of workflows to stitch profiles to.

        Returns:
            The list of workflows with embedded profiles attached.
        """
        all_profiles_data = await self.output_profile_repo.get_all_output_profiles()
        all_profiles = [OutputProfile.model_validate(p, strict=False) for p in all_profiles_data]

        for wf in workflows:
            attached = {}
            for p in all_profiles:
                if p.workflow_id == wf.id or p.workflow_id == "*":
                    attached[p.id] = EmbeddedOutputProfile(
                        name=p.name,
                        description=p.description,
                        custom_preface=p.custom_preface,
                        visible_metadata=list(p.visible_metadata),
                        visible_block_extensions=list(p.visible_block_extensions),
                        visible_workflow_extensions=list(p.visible_workflow_extensions),
                        max_extension_items=p.max_extension_items,
                        display_scale=p.display_scale,
                        include_diagnostic_scorecard=p.include_diagnostic_scorecard,
                        strictness_level=p.strictness_level,
                        scoring_strategy=p.scoring_strategy,
                        layouts=list(p.layouts),
                    )

            if not isinstance(wf.output_profiles, dict):
                wf.output_profiles = {}
            wf.output_profiles.update(attached)

        return workflows

    async def list_workflows(self, initiator: TokenData) -> list[Workflow]:
        """List workflows.

        Args:
            initiator: The user token data.

        Returns:
            A list of workflows.

        Raises:
            AppException (ErrorCodes.STATE_INTEGRITY_ERROR): On core validation errors.
        """
        all_data = await self.workflow_repo.get_all_workflows()

        workflows = []
        for x in all_data:
            try:
                workflows.append(Workflow.model_validate(x, strict=False))
            except ValidationError as e:
                logger.error(
                    "[StudioService] %s: Workflow %s failed hydration. DB is corrupt. Error: %s",
                    ErrorCodes.STATE_INTEGRITY_ERROR.name,
                    x.get("id"),
                    str(e),
                )
                raise AppException(
                    message=f"Database integrity error: Workflow {x.get('id')} failed strict validation.",
                    status_code=500,
                    details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR},
                ) from e

        if initiator.role == UserRole.ROOT:
            return await self._stitch_profiles_to_workflows(workflows)

        org_id = initiator.organization_id
        filtered = [x for x in workflows if x.organization_id in [org_id, SystemOrganizations.ROOT_SYSTEM]]
        return await self._stitch_profiles_to_workflows(filtered)

    async def get_workflow(self, initiator: TokenData, id: str) -> Workflow:
        """Get workflow.

        Args:
            initiator: The user token data.
            id: The workflow ID.

        Returns:
            The workflow.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        data = await self.workflow_repo.get_workflow_by_id(id)
        if not data:
            logger.error(
                "[StudioService] %s: Workflow %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        wf = Workflow.model_validate(data, strict=False)
        enforce_tenant_isolation(initiator, wf.organization_id, "workflow", wf.id)

        stitched = await self._stitch_profiles_to_workflows([wf])
        return stitched[0]

    async def get_workflow_available_extensions(self, initiator: TokenData, id: str) -> list[str]:
        """Get workflow available extensions.

        Args:
            initiator: The user token data.
            id: The workflow ID.

        Returns:
            A list of available extensions.
        """
        workflow = await self.get_workflow(initiator, id)
        all_steps = await self.list_steps(initiator)
        step_map = {s.id: s for s in all_steps}

        used_block_ids = set()
        for step_rule in workflow.steps:
            step = step_map.get(step_rule.task_blueprint)
            if step and step.criteria_block_ids:
                used_block_ids.update(step.criteria_block_ids)

        extensions = set()
        for block_id in used_block_ids:
            try:
                data = await self.prompt_block_repo.get_prompt_block_by_id(block_id)
                if data:
                    block = PromptBlock.model_validate(data, strict=False)
                    if block.category_id == "matrix" and block.output_extensions:
                        extensions.update(block.output_extensions)
            except Exception:
                pass

        return sorted(list(extensions))

    async def save_workflow(self, initiator: TokenData, id: str, data: Workflow) -> Workflow:
        """Save workflow.

        Args:
            initiator: The user token data.
            id: The workflow ID.
            data: The workflow configuration data.

        Returns:
            The saved workflow.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing after creation.
        """
        enforce_modification_rights(initiator, data.organization_id)

        DAGCompilerService.validate_workflow(data)

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.workflow_repo.create_workflow(dump)

        saved = await self.workflow_repo.get_workflow_by_id(id)
        if not saved:
            logger.error(
                "[StudioService] %s: Workflow %s not found after save (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)
        return Workflow.model_validate(saved, strict=False)

    async def delete_workflow(self, initiator: TokenData, id: str) -> None:
        """Delete workflow.

        Args:
            initiator: The user token data.
            id: The workflow ID.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        data = await self.workflow_repo.get_workflow_by_id(id)
        if not data:
            logger.error(
                "[StudioService] %s: Workflow %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        wf = Workflow.model_validate(data, strict=False)
        enforce_modification_rights(initiator, wf.organization_id)
        await self.workflow_repo.delete_workflow(id)

    async def create_workflow_draft(self, initiator: TokenData) -> Workflow:
        """Create workflow draft.

        Args:
            initiator: The user token data.

        Returns:
            The created workflow draft.
        """
        new_id = f"wf_{uuid.uuid4().hex[:16]}"
        draft_dict: dict[str, Any] = {
            "id": new_id,
            "slug": new_id,
            "name": {"default_locale": "en", "translations": {"en": "New Työnkulku", "fi": "Uusi työnkulku"}},
            "description": {"default_locale": "en", "translations": {"en": "Draft workflow", "fi": "Luonnos"}},
            "status": "draft",
            "version": 1,
            "organization_id": (
                SystemOrganizations.ROOT_SYSTEM if initiator.role == UserRole.ROOT else initiator.organization_id
            ),
            "expected_inputs": [],
            "steps": [],
            "allowed_exports": ["pdf"],
            "historical_context_mode": "DISABLED",
            "default_profile_id": "prof_0000000000000000",
        }
        draft = Workflow.model_validate(draft_dict, strict=False)
        return await self.save_workflow(initiator, new_id, draft)

    async def clone_workflow(self, initiator: TokenData, id: str) -> Workflow:
        """Clone workflow.

        Args:
            initiator: The user token data.
            id: The workflow ID to clone.

        Returns:
            The cloned workflow.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        data = await self.workflow_repo.get_workflow_by_id(id)
        if not data:
            logger.error(
                "[StudioService] %s: Workflow %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        wf = Workflow.model_validate(data, strict=False)
        enforce_tenant_isolation(initiator, wf.organization_id, "workflow", wf.id)

        new_id = f"wf_{uuid.uuid4().hex[:16]}"
        cloned_data = wf.model_dump(mode="json")
        cloned_data["id"] = new_id

        if initiator.role != UserRole.ROOT:
            cloned_data["organization_id"] = initiator.organization_id

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
        all_profiles = await self.output_profile_repo.get_all_output_profiles()
        profile_mapping = {}

        for p in all_profiles:
            if p.get("workflow_id") == id:
                new_profile_id = f"prof_{uuid.uuid4().hex[:30]}"
                profile_mapping[p.get("id")] = new_profile_id

                cloned_profile = p.copy()
                cloned_profile["id"] = new_profile_id
                cloned_profile["workflow_id"] = new_id
                if initiator.role not in ["ROOT", UserRole.ROOT]:
                    cloned_profile["organization_id"] = initiator.organization_id

                # Remap the step IDs inside layout
                for layout in cloned_profile.get("layouts", []):
                    old_layout_steps = layout.get("steps", [])
                    layout["steps"] = [sr_mapping.get(s, s) for s in old_layout_steps]

                await self.output_profile_repo.create_output_profile(cloned_profile)

        # Update the default profile ID referencing the old profile
        if cloned_data.get("default_profile_id") in profile_mapping:
            cloned_data["default_profile_id"] = profile_mapping[cloned_data["default_profile_id"]]

        # Clear embedded profiles from workflow clone since they are standalone now
        if "output_profiles" in cloned_data:
            cloned_data["output_profiles"] = {}

        cloned_workflow = Workflow.model_validate(cloned_data, strict=False)
        return await self.save_workflow(initiator, new_id, cloned_workflow)

    async def list_steps(self, initiator: TokenData) -> list[Step]:
        """List steps.

        Args:
            initiator: The user token data.

        Returns:
            A list of steps.

        Raises:
            AppException (ErrorCodes.STATE_INTEGRITY_ERROR): On core validation errors.
        """
        all_data = await self.workflow_repo.get_all_steps()

        steps = []
        for x in all_data:
            try:
                steps.append(Step.model_validate(x, strict=False))
            except ValidationError as e:
                logger.error(
                    "[StudioService] %s: Step %s failed hydration. DB is corrupt. Error: %s",
                    ErrorCodes.STATE_INTEGRITY_ERROR.name,
                    x.get("id"),
                    str(e),
                )
                raise AppException(
                    message=f"Database integrity error: Step {x.get('id')} failed strict validation.",
                    status_code=500,
                    details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR},
                ) from e

        if initiator.role == UserRole.ROOT:
            return steps

        org_id = initiator.organization_id
        return [x for x in steps if x.organization_id in [org_id, SystemOrganizations.ROOT_SYSTEM]]

    async def get_step(self, initiator: TokenData, id: str) -> Step:
        """Get step.

        Args:
            initiator: The user token data.
            id: The step ID.

        Returns:
            The step.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        data = await self.workflow_repo.get_step_by_id(id)
        if not data:
            logger.error(
                "[StudioService] %s: Step %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

        step = Step.model_validate(data, strict=False)
        enforce_tenant_isolation(initiator, step.organization_id, "step", step.id)
        return step

    async def save_step(self, initiator: TokenData, id: str, data: Step) -> Step:
        """Save step.

        Args:
            initiator: The user token data.
            id: The step ID.
            data: The step configuration data.

        Returns:
            The saved step.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing after creation.
        """
        org_id = getattr(data, "organization_id", None)
        enforce_modification_rights(initiator, org_id)

        dump = data.model_dump(mode="json")
        if "id" not in dump:
            dump["id"] = id
        await self.workflow_repo.create_step(dump)

        saved = await self.workflow_repo.get_step_by_id(id)
        if not saved:
            logger.error(
                "[StudioService] %s: Step %s not found after save (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="step", resource_id=id)
        return Step.model_validate(saved, strict=False)

    async def delete_step(self, initiator: TokenData, id: str, force_delete: bool = False) -> None:
        """Delete step.

        Args:
            initiator: The user token data.
            id: The step ID.
            force_delete: Whether to forcefully delete.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        data = await self.workflow_repo.get_step_by_id(id)
        if not data:
            logger.error(
                "[StudioService] %s: Step %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

        step = Step.model_validate(data, strict=False)
        enforce_modification_rights(initiator, step.organization_id)
        await self.workflow_repo.delete_step(id, force_delete=force_delete)

    async def create_step_draft(self, initiator: TokenData) -> Step:
        """Create step draft.

        Args:
            initiator: The user token data.

        Returns:
            The created step draft.

        Raises:
            AppException (ErrorCodes.STATE_INTEGRITY_ERROR): If no protocol block is found.
        """
        all_blocks = await self.prompt_block_repo.get_all_prompt_blocks()
        protocol_block_id = None
        for b in all_blocks:
            if b.get("category_id") == "protocol":
                protocol_block_id = b.get("id")
                break

        if not protocol_block_id:
            logger.error("[StudioService] No protocol block found in database.")
            raise AppException(
                message="No protocol block found to create step draft.",
                status_code=500,
                details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR},
            )

        new_id = f"step_{uuid.uuid4().hex[:16]}"
        draft_dict: dict[str, Any] = {
            "id": new_id,
            "slug": new_id,
            "name": {"default_locale": "en", "translations": {"en": "New Askel", "fi": "Uusi askel"}},
            "description": {"default_locale": "en", "translations": {"en": "Draft step", "fi": "Luonnos"}},
            "type": "llm",
            "role_block_id": None,
            "extraction_protocol_block_id": protocol_block_id,
            "criteria_block_ids": ["blk_440a5fef9331451b"],
            "pre_hooks": [],
            "post_hooks": [],
            "safety": "safe",
            "allowed_mcp_tools": [],
            "model_strategy": "fast",
            "organization_id": (
                SystemOrganizations.ROOT_SYSTEM if initiator.role == UserRole.ROOT else initiator.organization_id
            ),
        }
        draft = Step.model_validate(draft_dict, strict=False)
        return await self.save_step(initiator, new_id, draft)

    async def clone_step(self, initiator: TokenData, id: str) -> Step:
        """Clone step.

        Args:
            initiator: The user token data.
            id: The step ID to clone.

        Returns:
            The cloned step.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
        """
        data = await self.workflow_repo.get_step_by_id(id)
        if not data:
            logger.error(
                "[StudioService] %s: Step %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

        step = Step.model_validate(data, strict=False)
        enforce_tenant_isolation(initiator, step.organization_id, "step", step.id)

        new_id = f"step_{uuid.uuid4().hex[:16]}"

        cloned_data = step.model_dump(mode="json")
        cloned_data["id"] = new_id

        if initiator.role != UserRole.ROOT:
            cloned_data["organization_id"] = initiator.organization_id

        if "name" in cloned_data and isinstance(cloned_data["name"], dict):
            for locale, text in cloned_data["name"].get("translations", {}).items():
                cloned_data["name"]["translations"][locale] = text + " (Copy)"
        elif "name" in cloned_data:
            cloned_data["name"] = str(cloned_data["name"]) + " (Copy)"

        cloned_obj = Step.model_validate(cloned_data, strict=False)
        return await self.save_step(initiator, new_id, cloned_obj)
