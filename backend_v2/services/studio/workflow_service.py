"""Studio Workflow Service."""

from __future__ import annotations

import logging

from backend_v2.database.interfaces import (
    IOutputProfileRepository,
    IPromptBlockRepository,
    ISystemRepository,
    IWorkflowRepository,
    UnitOfWorkFactory,
    open_uow_session,
)
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError
from backend_v2.models.auth import TokenData, UserRole
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.output_profile import OutputProfileResponseDTO
from backend_v2.models.dtos.studio import WorkflowResponseDTO
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    EntityPrefix,
    HistoricalContextMode,
    PresetView,
    PromptBlockCategory,
    StepFilterScope,
    StepType,
    TargetBlockType,
    XaiExtensionType,
)
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.services.studio.auth_validator import (
    enforce_modification_rights,
    enforce_tenant_isolation,
    is_resource_accessible,
    resolve_create_organization_id,
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
        uow_factory: UnitOfWorkFactory | None = None,
    ) -> None:
        """Initialize the service.

        Args:
            workflow_repo: Workflow repository instance.
            output_profile_repo: Output profile repository instance.
            prompt_block_repo: Prompt block repository instance.
            system_repo: System repository instance.
            uow_factory: Optional UnitOfWork factory for multi-entity transactions.
        """
        self.workflow_repo = workflow_repo
        self.output_profile_repo = output_profile_repo
        self.prompt_block_repo = prompt_block_repo
        self.system_repo = system_repo
        self._uow_factory = uow_factory

    async def _require_workflow(self, initiator: TokenData, id: str, *, after_save: bool = False) -> Workflow:
        """Fetch a workflow by ID or raise ResourceNotFoundError.

        Args:
            initiator: The authenticated user requesting the workflow.
            id: Canonical workflow identifier.
            after_save: Whether the lookup occurs during post-save roundtrip verification.

        Returns:
            Hydrated Workflow domain model.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the workflow does not exist.
        """
        wf = await self.workflow_repo.get_workflow_by_id(id)
        if not wf:
            context_suffix = " after save" if after_save else ""
            logger.error(
                "[StudioService] %s: Workflow %s not found%s (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                context_suffix,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "workflow_id": id},
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=id)
        return wf

    async def _require_step(self, initiator: TokenData, id: str, *, after_save: bool = False) -> Step:
        """Fetch a step by ID or raise ResourceNotFoundError.

        Args:
            initiator: The authenticated user requesting the step.
            id: Canonical step identifier.
            after_save: Whether the lookup occurs during post-save roundtrip verification.

        Returns:
            Hydrated Step domain model.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the step does not exist.
        """
        step = await self.workflow_repo.get_step_by_id(id)
        if not step:
            context_suffix = " after save" if after_save else ""
            logger.error(
                "[StudioService] %s: Step %s not found%s (Initiator: %s).",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                id,
                context_suffix,
                initiator.id,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "step_id": id},
            )
            raise ResourceNotFoundError(resource_type="step", resource_id=id)
        return step

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
            organization_id=profile.organization_id,
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
        wf = await self._require_workflow(initiator, id)
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

    async def _persist_and_stitch_workflow(
        self, initiator: TokenData, id: str, normalized: Workflow
    ) -> WorkflowResponseDTO:
        """Validate DAG topology, persist a Workflow, synchronize linked profiles, and stitch DTO.

        Args:
            initiator: The authenticated user performing the write.
            id: Authoritative workflow identifier.
            normalized: Validated Workflow domain model bound to id.

        Returns:
            Hydrated WorkflowResponseDTO with stitched output profiles.

        Raises:
            AppException (ErrorCodes.WORKFLOW_COMPILATION_ERROR): If DAG validation fails.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the workflow cannot be reloaded after save.
        """
        DAGCompilerService.validate_workflow(normalized)
        await self.workflow_repo.save_workflow(normalized)
        saved = await self._require_workflow(initiator, id, after_save=True)
        await self._sync_output_profiles_for_workflow(saved)
        stitched = await self._stitch_profiles_to_workflows([saved])
        return stitched[0]

    async def _insert_validated_workflow(self, initiator: TokenData, id: str, data: Workflow) -> WorkflowResponseDTO:
        """Insert a newly drafted Workflow inside an atomic Unit of Work session.

        Args:
            initiator: The authenticated user creating the workflow.
            id: Server-issued workflow identifier.
            data: Newly constructed Workflow domain model.

        Returns:
            Persisted WorkflowResponseDTO reloaded from the repository.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are denied.
            AppException (ErrorCodes.WORKFLOW_COMPILATION_ERROR): If DAG validation fails.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the workflow is missing after save.
        """
        enforce_modification_rights(initiator, data.organization_id)
        normalized = data
        if normalized.id != id:
            normalized = normalized.model_copy(update={"id": id})
        async with open_uow_session(self._uow_factory):
            return await self._persist_and_stitch_workflow(initiator, id, normalized)

    async def save_workflow(self, initiator: TokenData, id: str, data: Workflow) -> WorkflowResponseDTO:
        """Update an existing workflow definition in-place inside an atomic Unit of Work session.

        Args:
            initiator: The user token data.
            id: The workflow ID.
            data: The workflow configuration data.

        Returns:
            The saved workflow response DTO.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the target workflow does not exist.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are denied.
            AppException (ErrorCodes.WORKFLOW_COMPILATION_ERROR): If DAG validation fails.
        """
        async with open_uow_session(self._uow_factory):
            existing = await self._require_workflow(initiator, id)
            enforce_modification_rights(initiator, existing.organization_id)

            target_org: str = existing.organization_id
            if initiator.role == UserRole.ROOT:
                target_org = data.organization_id
                enforce_modification_rights(initiator, target_org)

            normalized = data.model_copy(update={"id": id, "organization_id": target_org})
            return await self._persist_and_stitch_workflow(initiator, id, normalized)

    def _prune_stale_profile_targets(
        self,
        profile: OutputProfile,
        allowed_prompt_blocks: set[str],
        allowed_layout_targets: set[str],
    ) -> OutputProfile | None:
        """Return an updated OutputProfile with stale block targets pruned, or None if unchanged.

        Args:
            profile: The output profile to inspect.
            allowed_prompt_blocks: Valid prompt block IDs across workflow steps.
            allowed_layout_targets: Valid layout target IDs across workflow steps.

        Returns:
            Updated OutputProfile instance if changes were made, or None if already synchronized.
        """
        changed = False
        updated_groups: list[MatrixSynthesisGroup] = []
        for group in profile.matrix_synthesis_groups:
            filtered_targets = [b for b in group.target_blocks if b in allowed_layout_targets]
            if len(filtered_targets) != len(group.target_blocks):
                changed = True
            if not filtered_targets:
                changed = True
                continue
            coerced_view_type = group.view_type
            if group.view_type == PresetView.MATRIX_3D and len(filtered_targets) == 2:
                coerced_view_type = PresetView.COMPARE_2D
                changed = True
            elif group.view_type in (PresetView.COMPARE_2D, PresetView.MATRIX_3D) and len(filtered_targets) == 1:
                coerced_view_type = PresetView.METRICS_1D
                changed = True

            if filtered_targets != group.target_blocks or coerced_view_type != group.view_type:
                updated_groups.append(
                    group.model_copy(
                        update={
                            "target_blocks": filtered_targets,
                            "view_type": coerced_view_type,
                        }
                    )
                )
            else:
                updated_groups.append(group)

        updated_target_block_order = list(profile.target_block_order)
        if not updated_groups and TargetBlockType.MATRIX_GRAPHS_BLOCK in updated_target_block_order:
            updated_target_block_order = [
                b for b in updated_target_block_order if b != TargetBlockType.MATRIX_GRAPHS_BLOCK
            ]
            changed = True

        updated_variance_target = profile.variance_target_block
        updated_extensions = list(profile.visible_workflow_extensions)
        if updated_variance_target is not None and updated_variance_target not in allowed_prompt_blocks:
            updated_variance_target = None
            updated_target_block_order = [
                b for b in updated_target_block_order if b != TargetBlockType.VARIANCE_VALIDATION_BLOCK
            ]
            updated_extensions = [ext for ext in updated_extensions if ext != XaiExtensionType.VARIANCE_VALIDATION]
            changed = True

        updated_user_role_target = profile.user_role_target_block
        if updated_user_role_target is not None and updated_user_role_target not in allowed_prompt_blocks:
            updated_user_role_target = None
            changed = True

        if not changed:
            return None

        return profile.model_copy(
            update={
                "matrix_synthesis_groups": updated_groups,
                "target_block_order": updated_target_block_order,
                "visible_workflow_extensions": updated_extensions,
                "variance_target_block": updated_variance_target,
                "user_role_target_block": updated_user_role_target,
            }
        )

    async def _sync_output_profiles_for_workflow(self, workflow: Workflow) -> None:
        """Prune stale block references from linked output profiles when a workflow is saved.

        Args:
            workflow: The saved workflow domain model.
        """
        all_steps = await self.workflow_repo.get_all_steps()
        all_profiles = await self.output_profile_repo.get_all_output_profiles()
        allowed_prompt_blocks = workflow.get_allowed_prompt_block_targets(all_steps)
        allowed_layout_targets = workflow.get_allowed_layout_targets(all_steps)

        for profile in all_profiles:
            if profile.workflow_id != workflow.id:
                continue

            updated_profile = self._prune_stale_profile_targets(
                profile,
                allowed_prompt_blocks,
                allowed_layout_targets,
            )
            if updated_profile is not None:
                await self.output_profile_repo.create_output_profile(updated_profile)

    async def delete_workflow(self, initiator: TokenData, id: str) -> None:
        """Delete a workflow by ID inside an atomic Unit of Work session.

        Args:
            initiator: The user token data.
            id: The workflow ID.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are denied.
        """
        async with open_uow_session(self._uow_factory):
            wf = await self._require_workflow(initiator, id)
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

        target_org = resolve_create_organization_id(initiator)
        draft = Workflow(
            id=new_id,
            slug=new_id,
            name=I18nText(translations={"en": "New Workflow", "fi": "Uusi työnkulku"}),
            description=I18nText(translations={"en": "Draft workflow", "fi": "Luonnos"}),
            status="draft",
            version=1,
            organization_id=target_org,
            expected_inputs=[],
            steps=[],
            historical_context_mode=HistoricalContextMode.DISABLED,
            default_profile_id=None,
            mcp_gateway_id=chosen_gateway_id,
            model_registry_id=chosen_registry_id,
            default_lexical_strictness_level=50,
        )
        return await self._insert_validated_workflow(initiator, new_id, draft)

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
                new_v = v
                for old_sr, new_sr in sr_mapping.items():
                    new_v = new_v.replace(old_sr, new_sr)
                new_mappings[k] = new_v
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

    async def _persist_cloned_workflow_profiles(
        self,
        initiator: TokenData,
        source_profiles: list[OutputProfile],
        target_workflow_id: str,
        profile_mapping: dict[str, str],
    ) -> None:
        """Persist deep-cloned output profiles bound to pre-generated target IDs.

        Args:
            initiator: The user token data.
            source_profiles: Source OutputProfile models attached to the original workflow.
            target_workflow_id: Newly generated workflow ID.
            profile_mapping: Pre-generated mapping from original profile IDs to cloned profile IDs.
        """
        for p_obj in source_profiles:
            if initiator.role == UserRole.ROOT:
                cloned_profile_org = p_obj.organization_id
            else:
                cloned_profile_org = resolve_create_organization_id(initiator)
            cloned_profile = p_obj.model_copy(
                update={
                    "id": profile_mapping[p_obj.id],
                    "workflow_id": target_workflow_id,
                    "organization_id": cloned_profile_org,
                }
            )
            await self.output_profile_repo.create_output_profile(cloned_profile)

    async def clone_workflow(self, initiator: TokenData, id: str) -> WorkflowResponseDTO:
        """Clone an existing workflow and its output profiles inside one atomic Unit of Work session.

        Pre-generates cloned output profile IDs so the cloned Workflow is persisted once (version=1)
        with its target default_profile_id while workflows_default_profile_id_fkey is deferred until commit.

        Args:
            initiator: The user token data.
            id: The workflow ID to clone.

        Returns:
            The cloned workflow response DTO.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant isolation or modification rights fail.
            AppException (ErrorCodes.VALIDATION_FAILED): If a corrupted output profile is encountered.
            AppException (ErrorCodes.WORKFLOW_COMPILATION_ERROR): If cloned DAG validation fails.
        """
        async with open_uow_session(self._uow_factory):
            wf = await self._require_workflow(initiator, id)
            enforce_tenant_isolation(initiator, wf.organization_id, "workflow", wf.id, is_public=wf.is_public)

            if initiator.role == UserRole.ROOT:
                target_org_id = wf.organization_id
            else:
                target_org_id = resolve_create_organization_id(initiator)
            enforce_modification_rights(initiator, target_org_id)

            all_profiles = await self.output_profile_repo.get_all_output_profiles()
            source_profiles = [p_obj for p_obj in all_profiles if p_obj.workflow_id == id]
            profile_mapping: dict[str, str] = {
                p_obj.id: generate_opaque_id(EntityPrefix.OUTPUT_PROFILE) for p_obj in source_profiles
            }
            resolved_default_profile_id: str | None = None
            if wf.default_profile_id is not None:
                if wf.default_profile_id not in profile_mapping:
                    msg = (
                        f"Cannot clone workflow '{wf.id}': default_profile_id "
                        f"'{wf.default_profile_id}' is missing from workflow output profiles."
                    )
                    logger.error(
                        "[StudioWorkflowService] %s: %s",
                        ErrorCodes.VALIDATION_FAILED.name,
                        msg,
                        extra={
                            "error_code": ErrorCodes.VALIDATION_FAILED.value,
                            "workflow_id": wf.id,
                            "default_profile_id": wf.default_profile_id,
                        },
                    )
                    raise AppException(
                        message=msg,
                        status_code=422,
                        details={
                            "error_code": ErrorCodes.VALIDATION_FAILED.value,
                            "workflow_id": wf.id,
                            "default_profile_id": wf.default_profile_id,
                        },
                    )
                resolved_default_profile_id = profile_mapping[wf.default_profile_id]

            new_id = generate_opaque_id(EntityPrefix.WORKFLOW)
            cloned_name: I18nText | str = (
                wf.name.with_copy_suffix() if isinstance(wf.name, I18nText) else f"{wf.name} (Copy)"
            )
            sr_mapping: dict[str, str] = {
                step_cfg.id: generate_opaque_id(EntityPrefix.STEP_REFERENCE) for step_cfg in wf.steps
            }
            new_steps = self._clone_workflow_steps(wf.steps, sr_mapping)

            cloned_workflow = wf.model_copy(
                update={
                    "id": new_id,
                    "name": cloned_name,
                    "organization_id": target_org_id,
                    "version": 1,
                    "steps": new_steps,
                    "default_profile_id": resolved_default_profile_id,
                }
            )
            DAGCompilerService.validate_workflow(cloned_workflow)
            await self.workflow_repo.save_workflow(cloned_workflow)
            await self._persist_cloned_workflow_profiles(initiator, source_profiles, new_id, profile_mapping)

            saved = await self._require_workflow(initiator, new_id, after_save=True)
            await self._sync_output_profiles_for_workflow(saved)
            stitched = await self._stitch_profiles_to_workflows([saved])
            return stitched[0]

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
        step = await self._require_step(initiator, id)
        enforce_tenant_isolation(initiator, step.organization_id, "step", step.id)
        return step

    async def _insert_validated_step(self, initiator: TokenData, id: str, data: Step) -> Step:
        """Insert a newly drafted or cloned Step after RBAC verification.

        Args:
            initiator: The user token data.
            id: Server-issued step identifier.
            data: Newly constructed Step domain model.

        Returns:
            Persisted Step reloaded from the repository.

        Raises:
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are denied.
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the step cannot be reloaded after save.
        """
        enforce_modification_rights(initiator, data.organization_id)
        normalized = data
        if normalized.id != id:
            normalized = normalized.model_copy(update={"id": id})
        await self.workflow_repo.save_step(normalized)
        return await self._require_step(initiator, id, after_save=True)

    async def save_step(self, initiator: TokenData, id: str, data: Step) -> Step:
        """Update an existing step definition in-place under its authoritative ID.

        Args:
            initiator: The user token data.
            id: The step ID.
            data: The step configuration data.

        Returns:
            The saved step.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the target step does not exist.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are denied.
            AppException (ErrorCodes.SYSTEM_PROTECTED_RESOURCE): If attempting to mutate system core step.
        """
        existing_step = await self._require_step(initiator, id)
        enforce_modification_rights(initiator, existing_step.organization_id)

        if existing_step.is_system_core:
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

        target_org: str = existing_step.organization_id
        if initiator.role == UserRole.ROOT:
            target_org = data.organization_id
            enforce_modification_rights(initiator, target_org)

        normalized = data.model_copy(update={"id": id, "organization_id": target_org})
        await self.workflow_repo.save_step(normalized)
        return await self._require_step(initiator, id, after_save=True)

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
            AppException (ErrorCodes.DELETE_BLOCKED_BY_USAGE): If the step is referenced by a workflow.
        """
        step = await self._require_step(initiator, id)
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
            AppException (ErrorCodes.STATE_INTEGRITY_ERROR): If no protocol or criteria block is found.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If modification rights are denied.
        """
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
        target_org = resolve_create_organization_id(initiator)
        draft = Step(
            id=new_id,
            slug=new_id,
            name=I18nText(translations={"en": "New Step", "fi": "Uusi askel"}),
            description=I18nText(translations={"en": "Draft step", "fi": "Luonnos"}),
            type=StepType.LLM,
            role_block_id=None,
            extraction_protocol_block_id=protocol_block_id,
            criteria_block_ids=[default_criteria_id],
            expected_inputs=[],
            pre_hooks=[],
            post_hooks=[],
            safety="safe",
            allowed_mcp_tools=[],
            mcp_tool_params={},
            cognitive_tier=CognitiveTier.FAST,
            organization_id=target_org,
        )
        return await self._insert_validated_step(initiator, new_id, draft)

    async def clone_step(self, initiator: TokenData, id: str) -> Step:
        """Clone an existing step by ID.

        Args:
            initiator: The user token data.
            id: The step ID to clone.

        Returns:
            The cloned step.

        Raises:
            ResourceNotFoundError (ErrorCodes.RESOURCE_NOT_FOUND): If the resource is missing.
            PermissionDeniedError (ErrorCodes.PERMISSION_DENIED): If tenant isolation or modification rights fail.
        """
        step = await self._require_step(initiator, id)
        enforce_tenant_isolation(initiator, step.organization_id, "step", step.id)

        new_id = generate_opaque_id(EntityPrefix.STEP)
        if initiator.role == UserRole.ROOT:
            target_org = step.organization_id
        else:
            target_org = resolve_create_organization_id(initiator)
        cloned_name = step.name.with_copy_suffix()

        cloned_obj = step.model_copy(
            update={
                "id": new_id,
                "organization_id": target_org,
                "name": cloned_name,
                "is_system_core": False,
            }
        )
        return await self._insert_validated_step(initiator, new_id, cloned_obj)
