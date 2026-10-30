"""Studio Workflow Service."""

from __future__ import annotations

import logging

from backend_v2.database.interfaces import (
    IOutputProfileRepository,
    IPromptBlockRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import SystemOrganizations, TokenData, UserRole
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.models.dtos.studio import WorkflowResponseDTO
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    EntityPrefix,
    HistoricalContextMode,
    PromptBlockCategory,
    StepFilterScope,
    StepType,
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
        system_repo: ISystemRepository,
    ) -> None:
        """Initialize the service.

        Args:
            workflow_repo: Workflow repository instance.
            output_profile_repo: Output profile repository instance.
            prompt_block_repo: Prompt block repository instance.
            system_repo: System repository instance.
        """
        self.workflow_repo = workflow_repo
        self.output_profile_repo = output_profile_repo
        self.prompt_block_repo = prompt_block_repo
        self.system_repo = system_repo

    def _to_output_profile_dto(self, profile: OutputProfile) -> OutputProfileResponseDTO:
        """Project a domain OutputProfile into an OutputProfileResponseDTO.

        Args:
            profile: Hydrated OutputProfile domain model.

        Returns:
            Projected OutputProfileResponseDTO instance.
        """
        return OutputProfileResponseDTO(
            id=profile.id,
            slug=profile.slug,
            workflow_id=profile.workflow_id,
            name=profile.name,
            description=profile.description,
            custom_preface=profile.custom_preface,
            user_role_label=profile.user_role_label,
            tone_instruction=profile.tone_instruction,
            executive_summary_directive=profile.executive_summary_directive,
            matrix_1d_synthesis_directive=profile.matrix_1d_synthesis_directive,
            matrix_2d_synthesis_directive=profile.matrix_2d_synthesis_directive,
            matrix_3d_synthesis_directive=profile.matrix_3d_synthesis_directive,
            matrix_text_synthesis_directive=profile.matrix_text_synthesis_directive,
            row_explanation_directive=profile.row_explanation_directive,
            xai_synthesis_directive=profile.xai_synthesis_directive,
            variance_synthesis_directive=profile.variance_synthesis_directive,
            language=profile.language,
            target_block_order=profile.target_block_order,
            visible_metadata=profile.visible_metadata,
            matrix_visible_columns=profile.matrix_visible_columns,
            visible_block_extensions=profile.visible_block_extensions,
            visible_workflow_extensions=profile.visible_workflow_extensions,
            max_extension_items=profile.max_extension_items,
            display_scale=profile.display_scale,
            custom_scale_min=profile.custom_scale_min,
            custom_scale_max=profile.custom_scale_max,
            synthesis_length_constraint=profile.synthesis_length_constraint,
            row_explanation_length_constraint=profile.row_explanation_length_constraint,
            xai_length_constraint=profile.xai_length_constraint,
            variance_length_constraint=profile.variance_length_constraint,
            matrix_graph_length_constraint=profile.matrix_graph_length_constraint,
            max_quotes_per_matrix=profile.max_quotes_per_matrix,
            max_unmet_criteria=profile.max_unmet_criteria,
            matrix_synthesis_groups=profile.matrix_synthesis_groups,
            content_blocks=profile.content_blocks,
            show_sources_summary_box=profile.show_sources_summary_box,
            sources_display_mode=profile.sources_display_mode,
            variance_target_block=profile.variance_target_block,
            user_role_target_block=profile.user_role_target_block,
        )

    def _to_workflow_response_dto(
        self,
        wf: Workflow,
        attached_profiles: dict[str, OutputProfileResponseDTO],
    ) -> WorkflowResponseDTO:
        """Project a domain Workflow and its attached output profiles into a WorkflowResponseDTO.

        Args:
            wf: Hydrated Workflow domain model.
            attached_profiles: Mapping of profile ID to OutputProfileResponseDTO.

        Returns:
            Projected WorkflowResponseDTO instance.
        """
        return WorkflowResponseDTO(
            id=wf.id,
            slug=wf.slug,
            name=wf.name,
            description=wf.description,
            status=wf.status,
            version=wf.version,
            is_public=wf.is_public,
            organization_id=wf.organization_id,
            default_profile_id=wf.default_profile_id,
            mcp_gateway_id=wf.mcp_gateway_id,
            model_registry_id=wf.model_registry_id,
            default_strictness_level=wf.default_strictness_level,
            default_lexical_strictness_level=wf.default_lexical_strictness_level,
            security_penalty=wf.security_penalty,
            post_hoc_penalty=wf.post_hoc_penalty,
            passivity_penalty=wf.passivity_penalty,
            enable_contextual_overrides=wf.enable_contextual_overrides,
            enable_semantic_smoothing=wf.enable_semantic_smoothing,
            enable_eager_anonymization=wf.enable_eager_anonymization,
            system_audit_trail=wf.system_audit_trail,
            expected_inputs=wf.expected_inputs,
            steps=wf.steps,
            historical_context_mode=wf.historical_context_mode,
            output_profiles=attached_profiles,
        )

    async def _stitch_profiles_to_workflows(self, workflows: list[Workflow]) -> list[WorkflowResponseDTO]:
        """Stitch output profiles to workflows.

        Args:
            workflows: List of workflows to stitch profiles to.

        Returns:
            The list of workflows with embedded profiles attached.

        Raises:
            AppException (ErrorCodes.STATE_INTEGRITY_ERROR): If an output profile fails strict validation.
        """
        all_profiles = await self.output_profile_repo.get_all_output_profiles()

        response_dtos: list[WorkflowResponseDTO] = []
        for wf in workflows:
            attached: dict[str, OutputProfileResponseDTO] = {
                profile.id: self._to_output_profile_dto(profile)
                for profile in all_profiles
                if profile.workflow_id == wf.id
            }
            response_dtos.append(self._to_workflow_response_dto(wf, attached))

        return response_dtos

    async def list_workflows(self, initiator: TokenData) -> list[WorkflowResponseDTO]:
        """List workflows accessible to the initiator.

        Args:
            initiator: The user token data.

        Returns:
            A list of workflows with attached output profiles.

        Raises:
            AppException (ErrorCodes.STATE_INTEGRITY_ERROR): On core validation errors.
        """
        workflows = await self.workflow_repo.get_all_workflows()

        if initiator.role == UserRole.ROOT:
            return await self._stitch_profiles_to_workflows(workflows)

        filtered = [x for x in workflows if is_resource_accessible(initiator, x.organization_id, is_public=x.is_public)]
        return await self._stitch_profiles_to_workflows(filtered)

    async def get_workflow(self, initiator: TokenData, id: str) -> WorkflowResponseDTO:
        """Get a workflow by ID.

        Args:
            initiator: The user token data.
            id: The workflow ID.

        Returns:
            The hydrated workflow response DTO.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant isolation is violated.
        """
        wf = await self.workflow_repo.get_workflow_by_id(id)
        if not wf:
            logger.error(
                "[StudioService] %s: Workflow %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "workflow_id": id},
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        enforce_tenant_isolation(initiator, wf.organization_id, "workflow", wf.id, is_public=wf.is_public)

        stitched = await self._stitch_profiles_to_workflows([wf])
        return stitched[0]

    async def get_workflow_available_extensions(self, initiator: TokenData, id: str) -> list[str]:
        """Get workflow available extensions across all referenced matrix prompt blocks.

        Args:
            initiator: The user token data.
            id: The workflow ID.

        Returns:
            A sorted list of available extension identifiers.

        Raises:
            AppException (ErrorCodes.RESOURCE_NOT_FOUND): If a prompt block cannot be resolved.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the workflow is not found.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant isolation is violated.
        """
        workflow = await self.get_workflow(initiator, id)
        # Step 1: Include both specialist and system-core steps when resolving workflow matrix extensions
        all_steps = await self.list_steps(initiator, scope=StepFilterScope.ALL)
        step_map = {s.id: s for s in all_steps}

        used_block_ids: set[str] = set()
        for step_rule in workflow.steps:
            if step_rule.task_blueprint in step_map:
                step = step_map[step_rule.task_blueprint]
                if step.criteria_block_ids:
                    used_block_ids.update(step.criteria_block_ids)

        extensions: set[str] = set()
        for block_id in used_block_ids:
            try:
                block = await self.prompt_block_repo.get_prompt_block_by_id(block_id)
                if isinstance(block, MatrixPromptBlock) and block.output_extensions:
                    extensions.update(block.output_extensions)
            except Exception as e:
                logger.error(
                    "[StudioService] %s: Could not resolve prompt block %s for extensions: %s",
                    ErrorCodes.RESOURCE_NOT_FOUND.name,
                    block_id,
                    str(e),
                    exc_info=True,
                    extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "block_id": block_id},
                )
                raise AppException(
                    message=f"Could not resolve prompt block {block_id} for extensions: {e}",
                    status_code=500,
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "block_id": block_id},
                ) from e

        return sorted(list(extensions))

    async def save_workflow(self, initiator: TokenData, id: str, data: Workflow) -> WorkflowResponseDTO:
        """Save a workflow definition in-place.

        Args:
            initiator: The user token data.
            id: The workflow ID.
            data: The workflow configuration data.

        Returns:
            The saved workflow response DTO.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are denied.
            AppException (ErrorCodes.WORKFLOW_COMPILATION_ERROR): If DAG validation fails.
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
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "workflow_id": id},
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        stitched = await self._stitch_profiles_to_workflows([saved])
        return stitched[0]

    async def delete_workflow(self, initiator: TokenData, id: str) -> None:
        """Delete a workflow by ID.

        Args:
            initiator: The user token data.
            id: The workflow ID.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are denied.
        """
        wf = await self.workflow_repo.get_workflow_by_id(id)
        if not wf:
            logger.error(
                "[StudioService] %s: Workflow %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "workflow_id": id},
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        enforce_modification_rights(initiator, wf.organization_id)
        await self.workflow_repo.delete_workflow(id)

    async def create_workflow_draft(self, initiator: TokenData) -> WorkflowResponseDTO:
        """Create a new workflow draft.

        Args:
            initiator: The user token data.

        Returns:
            The created workflow draft response DTO.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If no active model registries exist in database.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are denied.
        """
        new_id = generate_opaque_id(EntityPrefix.WORKFLOW)
        active_registries = await self.system_repo.get_all_model_registries()
        if not active_registries:
            logger.error(
                "[WorkflowService] %s: No active model registry found in database.",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
            raise ResourceNotFoundError(resource_type="system_config", resource_id="model_registry")
        chosen_registry_id = active_registries[0].id
        active_gateways = await self.system_repo.get_all_mcp_gateways()
        chosen_gateway_id: str | None = None
        if active_gateways:
            chosen_gateway_id = active_gateways[0].id

        # Phase 4, Step 4: Dynamic repository lookup and None default for draft profile
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
            historical_context_mode=HistoricalContextMode.DISABLED,
            default_profile_id=None,
            mcp_gateway_id=chosen_gateway_id,
            model_registry_id=chosen_registry_id,
            default_lexical_strictness_level=50,
        )
        return await self.save_workflow(initiator, new_id, draft)

    def _clone_workflow_steps(self, steps: list[StepRule], sr_mapping: dict[str, str]) -> list[StepRule]:
        """Remap step rule IDs, dependencies, input mappings, and causal source step references.

        Args:
            steps: Original workflow step rules.
            sr_mapping: Mapping from original step rule IDs to newly generated step rule IDs.

        Returns:
            List of cloned StepRule instances with remapped references.
        """
        new_steps: list[StepRule] = []
        for step_cfg in steps:
            new_depends = [sr_mapping[dep] if dep in sr_mapping else dep for dep in step_cfg.depends_on]
            new_mappings: dict[str, str] = {}
            for k, v in step_cfg.input_mappings.items():
                if v.startswith("$steps."):
                    new_v = v
                    for old_sr, new_sr in sr_mapping.items():
                        new_v = new_v.replace(old_sr, new_sr)
                    new_mappings[k] = new_v
                else:
                    new_mappings[k] = v
            new_causal_source = (
                sr_mapping[step_cfg.causal_source_step_id]
                if step_cfg.causal_source_step_id and step_cfg.causal_source_step_id in sr_mapping
                else step_cfg.causal_source_step_id
            )
            new_steps.append(
                step_cfg.model_copy(
                    update={
                        "id": sr_mapping[step_cfg.id],
                        "depends_on": new_depends,
                        "input_mappings": new_mappings,
                        "causal_source_step_id": new_causal_source,
                    }
                )
            )
        return new_steps

    async def _clone_workflow_profiles(
        self,
        initiator: TokenData,
        source_workflow_id: str,
        target_workflow_id: str,
    ) -> dict[str, str]:
        """Deep-clone output profiles attached to the source workflow.

        Args:
            initiator: The user token data.
            source_workflow_id: Original workflow ID.
            target_workflow_id: Newly generated workflow ID.

        Returns:
            Mapping from original output profile IDs to cloned output profile IDs.

        Raises:
            AppException (ErrorCodes.VALIDATION_FAILED): If a corrupted output profile is encountered.
        """
        all_profiles = await self.output_profile_repo.get_all_output_profiles()
        profile_mapping: dict[str, str] = {}

        for p_obj in all_profiles:
            if p_obj.workflow_id == source_workflow_id:
                new_profile_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
                profile_mapping[p_obj.id] = new_profile_id
                cloned_profile = p_obj.model_copy(
                    update={
                        "id": new_profile_id,
                        "workflow_id": target_workflow_id,
                        "organization_id": (
                            p_obj.organization_id if initiator.role == UserRole.ROOT else initiator.organization_id
                        ),
                    }
                )
                await self.output_profile_repo.create_output_profile(cloned_profile)

        return profile_mapping

    async def clone_workflow(self, initiator: TokenData, id: str) -> WorkflowResponseDTO:
        """Clone an existing workflow along with its step rules and output profiles.

        Args:
            initiator: The user token data.
            id: The workflow ID to clone.

        Returns:
            The cloned workflow response DTO.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant isolation is violated.
            AppException (ErrorCodes.VALIDATION_FAILED): If a corrupted output profile is encountered.
        """
        wf = await self.workflow_repo.get_workflow_by_id(id)
        if not wf:
            logger.error(
                "[StudioService] %s: Workflow %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "workflow_id": id},
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)

        enforce_tenant_isolation(initiator, wf.organization_id, "workflow", wf.id, is_public=wf.is_public)

        new_id = generate_opaque_id(EntityPrefix.WORKFLOW)
        target_org_id = wf.organization_id if initiator.role == UserRole.ROOT else initiator.organization_id
        cloned_name: I18nText | str = (
            wf.name.with_copy_suffix() if isinstance(wf.name, I18nText) else f"{wf.name} (Copy)"
        )

        sr_mapping: dict[str, str] = {
            step_cfg.id: generate_opaque_id(EntityPrefix.STEP_REFERENCE) for step_cfg in wf.steps
        }
        new_steps = self._clone_workflow_steps(wf.steps, sr_mapping)
        profile_mapping = await self._clone_workflow_profiles(initiator, id, new_id)

        new_default_profile_id = (
            profile_mapping[wf.default_profile_id]
            if wf.default_profile_id and wf.default_profile_id in profile_mapping
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

    async def list_steps(
        self, initiator: TokenData, scope: StepFilterScope = StepFilterScope.SPECIALISTS
    ) -> list[Step]:
        """List steps filtered by tenant accessibility and scope.

        Args:
            initiator: The user token data.
            scope: The filter scope for steps.

        Returns:
            A list of steps matching the requested scope.
        """
        steps = await self.workflow_repo.get_all_steps()

        if initiator.role != UserRole.ROOT:
            steps = [x for x in steps if is_resource_accessible(initiator, x.organization_id)]

        match scope:
            case StepFilterScope.SPECIALISTS:
                return [s for s in steps if not s.is_system_core]
            case StepFilterScope.SYSTEM_CORE:
                return [s for s in steps if s.is_system_core]
            case StepFilterScope.ALL:
                return steps

    async def get_step(self, initiator: TokenData, id: str) -> Step:
        """Get a step by ID.

        Args:
            initiator: The user token data.
            id: The step ID.

        Returns:
            The requested step.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the step is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant isolation is violated.
        """
        step = await self.workflow_repo.get_step_by_id(id)
        if not step:
            logger.error(
                "[StudioService] %s: Step %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "step_id": id},
            )
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

        enforce_tenant_isolation(initiator, step.organization_id, "step", step.id)
        return step

    async def save_step(self, initiator: TokenData, id: str, data: Step) -> Step:
        """Save a step definition in-place.

        Args:
            initiator: The user token data.
            id: The step ID.
            data: The step configuration data.

        Returns:
            The saved step.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are denied.
            AppException (ErrorCodes.SYSTEM_PROTECTED_RESOURCE): If attempting to mutate system core step.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing after save.
        """
        enforce_modification_rights(initiator, data.organization_id)

        existing_step = await self.workflow_repo.get_step_by_id(id)
        if existing_step and existing_step.is_system_core:
            if data.slug != existing_step.slug or data.is_system_core != existing_step.is_system_core:
                logger.error(
                    "[StudioService] %s: Cannot mutate protected system core step %s.",
                    ErrorCodes.SYSTEM_PROTECTED_RESOURCE.name,
                    id,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value, "step_id": id},
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
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "step_id": id},
            )
            raise ResourceNotFoundError(resource_type="step", resource_id=id)
        return saved

    async def delete_step(self, initiator: TokenData, id: str, force_delete: bool = False) -> None:
        """Delete a step by ID.

        Args:
            initiator: The user token data.
            id: The step ID.
            force_delete: Whether to forcefully delete.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are denied.
            AppException (ErrorCodes.SYSTEM_PROTECTED_RESOURCE): If attempting to delete a system core step.
        """
        step = await self.workflow_repo.get_step_by_id(id)
        if not step:
            logger.error(
                "[StudioService] %s: Step %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "step_id": id},
            )
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

        enforce_modification_rights(initiator, step.organization_id)

        if step.is_system_core:
            logger.error(
                "[StudioService] %s: Cannot delete protected system core step %s.",
                ErrorCodes.SYSTEM_PROTECTED_RESOURCE.name,
                id,
                exc_info=True,
                extra={"error_code": ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value, "step_id": id},
            )
            raise AppException(
                message=f"Cannot delete protected system core step {id}.",
                status_code=403,
                details={"error_code": ErrorCodes.SYSTEM_PROTECTED_RESOURCE.value},
            )

        await self.workflow_repo.delete_step(id, force_delete=force_delete)

    async def create_step_draft(self, initiator: TokenData) -> Step:
        """Create a new step draft.

        Args:
            initiator: The user token data.

        Returns:
            The created step draft.

        Raises:
            AppException (ErrorCodes.STATE_INTEGRITY_ERROR): If no protocol block is found.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are denied.
        """
        # Phase 4, Step 4: Resolve protocol and default criteria block dynamically from repository
        all_blocks = await self.prompt_block_repo.get_all_prompt_blocks()
        protocol_block_id: str | None = None
        default_criteria_id: str | None = None
        for b in all_blocks:
            if protocol_block_id is None and b.category_id == PromptBlockCategory.PROTOCOL:
                protocol_block_id = b.id
            if default_criteria_id is None and (
                b.category_id == PromptBlockCategory.MATRIX or b.type == BlockDataType.CRITERIA
            ):
                default_criteria_id = b.id

        if not protocol_block_id:
            logger.error(
                "[StudioService] %s: No protocol block found in database to create step draft.",
                ErrorCodes.STATE_INTEGRITY_ERROR.name,
                exc_info=True,
                extra={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.value},
            )
            raise AppException(
                message="No protocol block found to create step draft.",
                status_code=500,
                details={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.value},
            )

        if not default_criteria_id:
            logger.error(
                "[StudioService] %s: No matrix or criteria block found in database to create step draft.",
                ErrorCodes.STATE_INTEGRITY_ERROR.name,
                exc_info=True,
                extra={"error_code": ErrorCodes.STATE_INTEGRITY_ERROR.value},
            )
            raise AppException(
                message="No matrix or criteria block found to create step draft.",
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
            criteria_block_ids=[default_criteria_id],
            pre_hooks=[],
            post_hooks=[],
            safety="safe",
            allowed_mcp_tools=[],
            mcp_tool_params={},
            cognitive_tier=CognitiveTier.FAST,
            organization_id=target_org,
        )
        return await self.save_step(initiator, new_id, draft)

    async def clone_step(self, initiator: TokenData, id: str) -> Step:
        """Clone an existing step by ID.

        Args:
            initiator: The user token data.
            id: The step ID to clone.

        Returns:
            The cloned step.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant isolation is violated.
        """
        step = await self.workflow_repo.get_step_by_id(id)
        if not step:
            logger.error(
                "[StudioService] %s: Step %s not found (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "step_id": id},
            )
            raise ResourceNotFoundError(resource_type="step", resource_id=id)

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
