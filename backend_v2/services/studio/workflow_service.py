"""Studio Workflow Service."""

import logging
from typing import Any

from pydantic import BaseModel, ValidationError

from backend_v2.database.interfaces import (
    IOutputProfileRepository,
    IPromptBlockRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PromptBlockAdapter,
)
from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.models.dtos.studio import WorkflowResponseDTO
from backend_v2.models.enums import EntityPrefix, HistoricalContextMode, StepType
from backend_v2.models.v2_core import (
    I18nText,
    Step,
    StepRule,
    Workflow,
)
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.services.studio.auth_validator import (
    enforce_modification_rights,
    enforce_tenant_isolation,
    is_resource_accessible,
)

logger = logging.getLogger(__name__)

__all__ = ["StudioWorkflowService"]


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

    async def _stitch_profiles_to_workflows(self, workflows: list[Workflow]) -> list[WorkflowResponseDTO]:
        """Stitch profiles to workflows.

        Args:
            workflows: List of workflows to stitch profiles to.

        Returns:
            The list of workflows with embedded profiles attached.

        Raises:
            AppException (ErrorCodes.STATE_INTEGRITY_ERROR): If an output profile fails strict validation.
        """
        all_profiles_data = await self.output_profile_repo.get_all_output_profiles()
        all_profiles: list[OutputProfile] = []
        for p_data in all_profiles_data:
            try:
                all_profiles.append(OutputProfile.model_validate(p_data, strict=False))
            except ValidationError as e:
                if isinstance(p_data, OutputProfile):
                    p_id = p_data.id
                else:
                    p_id = "unknown"
                logger.error(
                    "[StudioService] %s: OutputProfile %s failed hydration. Error: %s",
                    ErrorCodes.STATE_INTEGRITY_ERROR.name,
                    p_id,
                    str(e),
                )
                raise AppException(
                    message=f"Database integrity error: OutputProfile {p_id} failed strict validation.",
                    status_code=500,
                    details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.value},
                ) from e

        response_dtos = []
        for wf in workflows:
            attached = {}
            for profile in all_profiles:
                if profile.workflow_id == wf.id:
                    # Safely convert to DTO without triggering extra_forbidden
                    p_dict = profile.model_dump(mode="json", exclude={"metric_mappings", "score_display_label"})
                    attached[profile.id] = OutputProfileResponseDTO.model_validate(p_dict, strict=False)

            wf_dict = wf.model_dump(mode="json")
            wf_dict["output_profiles"] = attached
            dto = WorkflowResponseDTO.model_validate(wf_dict, strict=False)
            response_dtos.append(dto)

        return response_dtos

    async def list_workflows(self, initiator: TokenData) -> list[WorkflowResponseDTO]:
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
                if isinstance(x, Workflow):
                    x_id = x.id
                else:
                    x_id = "unknown"
                logger.error(
                    "[StudioService] %s: Workflow %s failed hydration. DB is corrupt. Error: %s",
                    ErrorCodes.STATE_INTEGRITY_ERROR.name,
                    x_id,
                    str(e),
                )
                raise AppException(
                    message=f"Database integrity error: Workflow {x_id} failed strict validation.",
                    status_code=500,
                    details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.value},
                ) from e

        if initiator.role == UserRole.ROOT:
            return await self._stitch_profiles_to_workflows(workflows)

        filtered = [x for x in workflows if is_resource_accessible(initiator, x.organization_id, is_public=x.is_public)]
        return await self._stitch_profiles_to_workflows(filtered)

    async def get_workflow(self, initiator: TokenData, id: str) -> WorkflowResponseDTO:
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
        enforce_tenant_isolation(initiator, wf.organization_id, "workflow", wf.id, is_public=wf.is_public)

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
                    block = PromptBlockAdapter.validate_python(data, strict=False)
                    if isinstance(block, MatrixPromptBlock) and block.output_extensions:
                        extensions.update(block.output_extensions)
            except (AppException, ValidationError, ValueError, KeyError, TypeError, OSError) as e:
                logger.debug(
                    "[StudioService] Could not resolve prompt block %s for extensions: %s",
                    block_id,
                    str(e),
                )

        return sorted(list(extensions))

    async def save_workflow(self, initiator: TokenData, id: str, data: Workflow) -> WorkflowResponseDTO:
        """Save workflow.

        Args:
            initiator: The user token data.
            id: The workflow ID.
            data: The workflow configuration data.

        Returns:
            The saved workflow.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing after save.
        """
        enforce_modification_rights(initiator, data.organization_id)

        DAGCompilerService.validate_workflow(data)

        if data.id != id:
            data = data.model_copy(update={"id": id})

        await self.workflow_repo.save_workflow(data)

        saved = await self.workflow_repo.get_workflow_by_id(id)
        if not saved:
            logger.error(
                "[StudioService] %s: Workflow %s not found after save (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)
        wf = Workflow.model_validate(saved, strict=False)
        stitched = await self._stitch_profiles_to_workflows([wf])
        return stitched[0]

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

    async def create_workflow_draft(self, initiator: TokenData) -> WorkflowResponseDTO:
        """Create workflow draft.

        Args:
            initiator: The user token data.

        Returns:
            The created workflow draft.
        """
        new_id = generate_opaque_id(EntityPrefix.WORKFLOW)
        draft = Workflow(
            id=new_id,
            slug=new_id,
            name=I18nText(translations={"en": "New Työnkulku", "fi": "Uusi työnkulku"}),
            description=I18nText(translations={"en": "Draft workflow", "fi": "Luonnos"}),
            status="draft",
            version=1,
            organization_id=(
                SystemOrganizations.ROOT_SYSTEM if initiator.role == UserRole.ROOT else initiator.organization_id
            ),
            expected_inputs=[],
            steps=[],
            allowed_exports=["pdf"],
            historical_context_mode=HistoricalContextMode.DISABLED,
            default_profile_id="prf_0000000000000000",
        )
        return await self.save_workflow(initiator, new_id, draft)

    async def clone_workflow(self, initiator: TokenData, id: str) -> WorkflowResponseDTO:
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
        enforce_tenant_isolation(initiator, wf.organization_id, "workflow", wf.id, is_public=wf.is_public)

        new_id = generate_opaque_id(EntityPrefix.WORKFLOW)
        target_org_id = wf.organization_id if initiator.role == UserRole.ROOT else initiator.organization_id

        cloned_name: I18nText | str = (
            wf.name.with_copy_suffix() if isinstance(wf.name, I18nText) else f"{wf.name} (Copy)"
        )

        sr_mapping: dict[str, str] = {
            step_cfg.id: generate_opaque_id(EntityPrefix.STEP_REFERENCE) for step_cfg in wf.steps
        }

        new_steps: list[StepRule] = []
        for step_cfg in wf.steps:
            new_depends = [sr_mapping[dep] if dep in sr_mapping else dep for dep in step_cfg.depends_on]
            new_mappings: dict[str, Any] = {}
            for k, v in step_cfg.input_mappings.items():
                if isinstance(v, str) and v.startswith("$steps."):
                    new_v = v
                    for old_sr, new_sr in sr_mapping.items():
                        new_v = new_v.replace(old_sr, new_sr)
                    new_mappings[k] = new_v
                else:
                    new_mappings[k] = v
            new_step = step_cfg.model_copy(
                update={
                    "id": sr_mapping[step_cfg.id],
                    "depends_on": new_depends,
                    "input_mappings": new_mappings,
                }
            )
            new_steps.append(new_step)

        # Deep clone standalone output profiles mapped to this old workflow
        all_profiles = await self.output_profile_repo.get_all_output_profiles()
        profile_mapping: dict[str, str] = {}

        for p_data in all_profiles:
            try:
                p_obj = (
                    p_data if isinstance(p_data, OutputProfile) else OutputProfile.model_validate(p_data, strict=False)
                )
            except ValidationError:
                continue

            if p_obj.workflow_id == id:
                new_profile_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
                profile_mapping[p_obj.id] = new_profile_id
                cloned_profile = p_obj.model_copy(
                    update={
                        "id": new_profile_id,
                        "workflow_id": new_id,
                        "organization_id": (
                            p_obj.organization_id if initiator.role == UserRole.ROOT else initiator.organization_id
                        ),
                    }
                )

                await self.output_profile_repo.create_output_profile(cloned_profile)

        # Update the default profile ID referencing the old profile
        new_default_profile_id = (
            profile_mapping[wf.default_profile_id]
            if wf.default_profile_id in profile_mapping
            else wf.default_profile_id
        )

        cloned_workflow = wf.model_copy(
            update={
                "id": new_id,
                "name": cloned_name,
                "organization_id": target_org_id,
                "steps": new_steps,
                "default_profile_id": new_default_profile_id,
            }
        )
        return await self.save_workflow(initiator, new_id, cloned_workflow)

    async def list_steps(self, initiator: TokenData) -> list[Step]:
        """List steps.

        Args:
            initiator: The user token data.

        Returns:
            A list of steps.
        """
        steps = await self.workflow_repo.get_all_steps()

        if initiator.role == UserRole.ROOT:
            return steps

        return [x for x in steps if is_resource_accessible(initiator, x.organization_id)]

    async def get_step(self, initiator: TokenData, id: str) -> Step:
        """Get step.

        Args:
            initiator: The user token data.
            id: The step ID.

        Returns:
            The step.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the step is missing.
        """
        step = await self.workflow_repo.get_step_by_id(id)
        if not step:
            logger.error(
                "[StudioService] %s: Step %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

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
            AppException (ErrorCodes.SYSTEM_PROTECTED_RESOURCE): If attempting to mutate system core step.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing after save.
        """
        # Direct typed attribute access
        org_id = data.organization_id
        enforce_modification_rights(initiator, org_id)

        # System Core Protection
        existing_step = await self.workflow_repo.get_step_by_id(id)
        if existing_step:
            if existing_step.is_system_core:
                if data.slug != existing_step.slug or data.is_system_core != existing_step.is_system_core:
                    logger.error(
                        "[StudioService] %s: Cannot mutate protected system core step %s.",
                        ErrorCodes.SYSTEM_PROTECTED_RESOURCE.name,
                        id,
                    )
                    raise AppException(
                        message=f"Cannot mutate protected system core step {id}.",
                        status_code=403,
                        details={"error_code": ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value},
                    )

        if data.id != id:
            data = data.model_copy(update={"id": id})

        await self.workflow_repo.save_step(data)

        saved = await self.workflow_repo.get_step_by_id(id)
        if not saved:
            logger.error(
                "[StudioService] %s: Step %s not found after save (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
            )
            raise ResourceNotFoundError(resource_type="step", resource_id=id)
        return saved

    async def delete_step(self, initiator: TokenData, id: str, force_delete: bool = False) -> None:
        """Delete step.

        Args:
            initiator: The user token data.
            id: The step ID.
            force_delete: Whether to forcefully delete.

        Raises:
            AppException (ErrorCodes.SYSTEM_PROTECTED_RESOURCE): If attempting to delete a system core step.
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

        # Phase 3, Step 4: System Core Protection
        if step.is_system_core:
            logger.error(
                "[StudioService] %s: Cannot delete protected system core step %s.",
                ErrorCodes.SYSTEM_PROTECTED_RESOURCE.name,
                id,
            )
            raise AppException(
                message=f"Cannot delete protected system core step {id}.",
                status_code=403,
                details={"error_code": ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value},
            )

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
            b_block = PromptBlockAdapter.validate_python(b, strict=False) if not isinstance(b, BaseModel) else b
            if b_block.category_id == "protocol":
                protocol_block_id = b_block.id
                break

        if not protocol_block_id:
            logger.error("[StudioService] No protocol block found in database.")
            raise AppException(
                message="No protocol block found to create step draft.",
                status_code=500,
                details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.value},
            )

        new_id = generate_opaque_id(EntityPrefix.STEP)
        target_org = SystemOrganizations.ROOT_SYSTEM if initiator.role == UserRole.ROOT else initiator.organization_id
        draft = Step(
            id=new_id,
            slug=new_id,
            name=I18nText(translations={"en": "New Askel", "fi": "Uusi askel"}),
            description=I18nText(translations={"en": "Draft step", "fi": "Luonnos"}),
            type=StepType.LLM,
            role_block_id=None,
            extraction_protocol_block_id=protocol_block_id,
            criteria_block_ids=["blk_440a5fef9331451b"],
            pre_hooks=[],
            post_hooks=[],
            safety="safe",
            allowed_mcp_tools=[],
            model_strategy="fast",
            organization_id=target_org,
        )
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

        new_id = generate_opaque_id(EntityPrefix.STEP)
        target_org = step.organization_id if initiator.role == UserRole.ROOT else initiator.organization_id
        cloned_name = step.name.with_copy_suffix()

        cloned_obj = step.model_copy(
            update={
                "id": new_id,
                "organization_id": target_org,
                "name": cloned_name,
            }
        )
        return await self.save_step(initiator, new_id, cloned_obj)
