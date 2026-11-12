"""Database repository implementation module for Workflows and Steps."""

from __future__ import annotations

import logging

from backend_v2.database.repositories.base import BaseRepository
from backend_v2.exceptions import AppException, ErrorCodes, ResourceNotFoundError, WorkflowNotFoundError
from backend_v2.models.auth import SystemOrganizations
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.studio import (
    StepCreateDTO,
    StepUpdateDTO,
    WorkflowCreateDTO,
    WorkflowUpdateDTO,
)
from backend_v2.models.enums import EntityPrefix

logger = logging.getLogger(__name__)

__all__ = ["WorkflowRepositoryImpl"]


class WorkflowRepositoryImpl(BaseRepository):
    """Repository implementation for Workflows and Steps backed by EntityPersistencePort."""

    async def get_workflow_definition(self, workflow_id: str) -> Workflow | None:
        """Retrieve a workflow definition by primary key ID from PostgreSQL 19.

        Args:
            workflow_id: Canonical wf_<hex32> workflow identifier.

        Returns:
            Validated Workflow domain model if found, otherwise None.
        """
        async with self._acquire_entities() as entities:
            return await entities.get_workflow(workflow_id)

    async def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Retrieve a workflow by primary key ID.

        Args:
            workflow_id: Canonical wf_<hex32> workflow identifier.

        Returns:
            Validated Workflow domain model if found, otherwise None.
        """
        return await self.get_workflow_definition(workflow_id)

    async def get_all_workflows(
        self,
        organization_id: str | None = None,
        role: str | None = None,
    ) -> list[Workflow]:
        """Retrieve all workflows accessible to the caller's organization and role.

        Args:
            organization_id: Optional caller organization filter.
            role: Optional caller role identifier (e.g., 'ROOT').

        Returns:
            List of validated Workflow domain models.
        """
        async with self._acquire_entities() as entities:
            all_workflows = await entities.list_workflows()
        if role != "ROOT" and organization_id:
            allowed_orgs = {organization_id, SystemOrganizations.ROOT_SYSTEM.value, "SYSTEM"}
            return [wf for wf in all_workflows if wf.organization_id in allowed_orgs]
        return all_workflows

    async def get_workflow_by_id(self, workflow_id: str) -> Workflow | None:
        """Retrieve a workflow by ID from PostgreSQL 19.

        Args:
            workflow_id: Canonical wf_<hex32> workflow identifier.

        Returns:
            Validated Workflow domain model if found, otherwise None.
        """
        return await self.get_workflow_definition(workflow_id)

    async def save_workflow(self, workflow: Workflow) -> str:
        """Persist a validated Workflow domain model in-place via atomic upsert.

        Args:
            workflow: Validated Workflow domain model.

        Returns:
            Persisted canonical wf_<hex32> identifier.
        """
        async with self._acquire_entities() as entities:
            return await entities.upsert_workflow(workflow)

    async def create_workflow(self, workflow_data: WorkflowCreateDTO) -> str:
        """Create a new Workflow from a WorkflowCreateDTO.

        Args:
            workflow_data: Validated WorkflowCreateDTO payload.

        Returns:
            Created canonical wf_<hex32> identifier.

        Raises:
            AppException: With VALIDATION_FAILED (HTTP 422) if model_registry_id is missing.
        """
        if workflow_data.model_registry_id is None:
            msg = "WorkflowCreateDTO.model_registry_id is required to persist a Workflow."
            logger.error(
                "[WorkflowRepository] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg,
                status_code=422,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )

        org_id = "SYSTEM"
        if workflow_data.organization_id is not None:
            org_id = workflow_data.organization_id
        desc: I18nText | str = ""
        if workflow_data.description is not None:
            desc = workflow_data.description

        workflow = Workflow(
            id=generate_opaque_id(EntityPrefix.WORKFLOW),
            slug=workflow_data.slug,
            name=workflow_data.name,
            description=desc,
            status=workflow_data.status,
            version=workflow_data.version,
            is_public=workflow_data.is_public,
            organization_id=org_id,
            default_profile_id=workflow_data.default_profile_id,
            mcp_gateway_id=workflow_data.mcp_gateway_id,
            model_registry_id=workflow_data.model_registry_id,
            default_strictness_level=workflow_data.default_strictness_level,
            default_lexical_strictness_level=workflow_data.default_lexical_strictness_level,
            security_penalty=workflow_data.security_penalty,
            post_hoc_penalty=workflow_data.post_hoc_penalty,
            passivity_penalty=workflow_data.passivity_penalty,
            enable_contextual_overrides=workflow_data.enable_contextual_overrides,
            enable_semantic_smoothing=workflow_data.enable_semantic_smoothing,
            enable_eager_anonymization=workflow_data.enable_eager_anonymization,
            system_audit_trail=workflow_data.system_audit_trail,
            expected_inputs=workflow_data.expected_inputs,
            steps=workflow_data.steps,
            historical_context_mode=workflow_data.historical_context_mode,
        )
        async with self._acquire_entities() as entities:
            return await entities.upsert_workflow(workflow)

    async def update_workflow(self, workflow_id: str, updates: WorkflowUpdateDTO) -> str:
        """Update an existing Workflow in-place.

        Args:
            workflow_id: Canonical wf_<hex32> workflow identifier.
            updates: Validated WorkflowUpdateDTO carrying updated fields.

        Returns:
            Updated canonical wf_<hex32> identifier.

        Raises:
            WorkflowNotFoundError: If the target workflow does not exist.
        """
        fields_set = updates.model_fields_set
        async with self._acquire_entities() as entities:
            existing = await entities.get_workflow(workflow_id)
            if existing is None:
                logger.error(
                    "[WorkflowRepository] %s: Workflow %s not found for update",
                    ErrorCodes.RESOURCE_NOT_FOUND.name,
                    workflow_id,
                    extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "workflow_id": workflow_id},
                )
                raise WorkflowNotFoundError(workflow_id)
            if not fields_set:
                return workflow_id

            next_name = existing.name
            if updates.name is not None:
                next_name = updates.name
            next_description = existing.description
            if updates.description is not None:
                next_description = updates.description
            next_slug = existing.slug
            if updates.slug is not None:
                next_slug = updates.slug
            next_expected_inputs = existing.expected_inputs
            if updates.expected_inputs is not None:
                next_expected_inputs = updates.expected_inputs
            next_steps = existing.steps
            if updates.steps is not None:
                next_steps = updates.steps
            next_historical_mode = existing.historical_context_mode
            if updates.historical_context_mode is not None:
                next_historical_mode = updates.historical_context_mode
            next_default_profile_id = existing.default_profile_id
            if "default_profile_id" in fields_set:
                next_default_profile_id = updates.default_profile_id
            next_strictness = existing.default_strictness_level
            if updates.default_strictness_level is not None:
                next_strictness = updates.default_strictness_level
            next_lexical_strictness = existing.default_lexical_strictness_level
            if updates.default_lexical_strictness_level is not None:
                next_lexical_strictness = updates.default_lexical_strictness_level
            next_security_penalty = existing.security_penalty
            if updates.security_penalty is not None:
                next_security_penalty = updates.security_penalty
            next_post_hoc_penalty = existing.post_hoc_penalty
            if updates.post_hoc_penalty is not None:
                next_post_hoc_penalty = updates.post_hoc_penalty
            next_passivity_penalty = existing.passivity_penalty
            if updates.passivity_penalty is not None:
                next_passivity_penalty = updates.passivity_penalty
            next_status = existing.status
            if updates.status is not None:
                next_status = updates.status
            next_model_registry_id = existing.model_registry_id
            if updates.model_registry_id is not None:
                next_model_registry_id = updates.model_registry_id

            validated = Workflow(
                id=existing.id,
                slug=next_slug,
                name=next_name,
                description=next_description,
                status=next_status,
                version=existing.version,
                is_public=existing.is_public,
                organization_id=existing.organization_id,
                default_profile_id=next_default_profile_id,
                mcp_gateway_id=existing.mcp_gateway_id,
                model_registry_id=next_model_registry_id,
                default_strictness_level=next_strictness,
                default_lexical_strictness_level=next_lexical_strictness,
                security_penalty=next_security_penalty,
                post_hoc_penalty=next_post_hoc_penalty,
                passivity_penalty=next_passivity_penalty,
                enable_contextual_overrides=existing.enable_contextual_overrides,
                enable_semantic_smoothing=existing.enable_semantic_smoothing,
                enable_eager_anonymization=existing.enable_eager_anonymization,
                system_audit_trail=existing.system_audit_trail,
                expected_inputs=next_expected_inputs,
                steps=next_steps,
                historical_context_mode=next_historical_mode,
            )
            return await entities.upsert_workflow(validated)

    async def update_workflow_definition(self, workflow_id: str, definition_data: WorkflowUpdateDTO) -> str:
        """Update a workflow definition in-place.

        Args:
            workflow_id: Canonical wf_<hex32> workflow identifier.
            definition_data: Validated WorkflowUpdateDTO carrying updated fields.

        Returns:
            Updated canonical wf_<hex32> identifier.
        """
        return await self.update_workflow(workflow_id, definition_data)

    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete a workflow by primary key ID.

        Args:
            workflow_id: Canonical wf_<hex32> workflow identifier.

        Returns:
            True if deleted, False otherwise.
        """
        async with self._acquire_entities() as entities:
            return await entities.delete_workflow(workflow_id)

    async def count_workflows(self) -> int:
        """Count total persisted workflows.

        Returns:
            Total workflow count.
        """
        async with self._acquire_entities() as entities:
            return len(await entities.list_workflows())

    async def get_all_steps(self) -> list[Step]:
        """Retrieve all persisted steps.

        Returns:
            List of validated Step domain models.
        """
        async with self._acquire_entities() as entities:
            return await entities.list_steps()

    async def get_step_by_id(self, step_id: str) -> Step | None:
        """Retrieve a step by primary key ID from the steps table.

        Args:
            step_id: Canonical stp_<hex32> step identifier.

        Returns:
            Validated Step domain model if found, otherwise None.
        """
        async with self._acquire_entities() as entities:
            return await entities.get_step(step_id)

    async def get_step(self, step_id: str) -> Step | None:
        """Retrieve a step by primary key ID.

        Args:
            step_id: Canonical stp_<hex32> step identifier.

        Returns:
            Validated Step domain model if found, otherwise None.
        """
        return await self.get_step_by_id(step_id)

    async def save_step(self, step: Step) -> str:
        """Persist a validated Step domain model in-place via atomic upsert.

        Args:
            step: Validated Step domain model.

        Returns:
            Persisted canonical stp_<hex32> identifier.
        """
        async with self._acquire_entities() as entities:
            return await entities.upsert_step(step)

    async def create_step(self, step_data: StepCreateDTO) -> str:
        """Create a new Step from a StepCreateDTO.

        Args:
            step_data: Validated StepCreateDTO payload.

        Returns:
            Created canonical stp_<hex32> identifier.
        """
        org_id = "SYSTEM"
        if step_data.organization_id is not None:
            org_id = step_data.organization_id
        step = Step(
            id=generate_opaque_id(EntityPrefix.STEP),
            slug=step_data.slug,
            organization_id=org_id,
            name=step_data.name,
            description=step_data.description,
            type=step_data.type,
            hook=step_data.hook,
            role_block_id=step_data.role_block_id,
            extraction_protocol_block_id=step_data.extraction_protocol_block_id,
            execution_persona_block_id=step_data.execution_persona_block_id,
            criteria_block_ids=step_data.criteria_block_ids,
            pre_hooks=step_data.pre_hooks,
            post_hooks=step_data.post_hooks,
            safety=step_data.safety,
            allowed_mcp_tools=step_data.allowed_mcp_tools,
            mcp_tool_params=step_data.mcp_tool_params,
            cognitive_tier=step_data.cognitive_tier,
            expected_inputs=step_data.expected_inputs,
            is_system_core=step_data.is_system_core,
        )
        async with self._acquire_entities() as entities:
            return await entities.upsert_step(step)

    async def update_step(self, step_id: str, updates: StepUpdateDTO) -> str:
        """Update an existing Step in-place.

        Args:
            step_id: Canonical stp_<hex32> step identifier.
            updates: Validated StepUpdateDTO carrying updated fields.

        Returns:
            Updated canonical stp_<hex32> identifier.

        Raises:
            ResourceNotFoundError: If the target step does not exist.
        """
        fields_set = updates.model_fields_set
        async with self._acquire_entities() as entities:
            existing = await entities.get_step(step_id)
            if existing is None:
                logger.error(
                    "[WorkflowRepository] %s: Step %s not found for update",
                    ErrorCodes.RESOURCE_NOT_FOUND.name,
                    step_id,
                    extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "step_id": step_id},
                )
                raise ResourceNotFoundError(resource_type="step", resource_id=step_id)
            if not fields_set:
                return step_id

            next_name = existing.name
            if updates.name is not None:
                next_name = updates.name
            next_description = existing.description
            if "description" in fields_set:
                next_description = updates.description
            next_slug = existing.slug
            if updates.slug is not None:
                next_slug = updates.slug
            next_type = existing.type
            if updates.type is not None:
                next_type = updates.type
            next_hook = existing.hook
            if "hook" in fields_set:
                next_hook = updates.hook
            next_role_block_id = existing.role_block_id
            if "role_block_id" in fields_set:
                next_role_block_id = updates.role_block_id
            next_extraction_block_id = existing.extraction_protocol_block_id
            if "extraction_protocol_block_id" in fields_set:
                next_extraction_block_id = updates.extraction_protocol_block_id
            next_persona_block_id = existing.execution_persona_block_id
            if "execution_persona_block_id" in fields_set:
                next_persona_block_id = updates.execution_persona_block_id
            next_criteria_ids = existing.criteria_block_ids
            if updates.criteria_block_ids is not None:
                next_criteria_ids = updates.criteria_block_ids
            next_pre_hooks = existing.pre_hooks
            if updates.pre_hooks is not None:
                next_pre_hooks = updates.pre_hooks
            next_post_hooks = existing.post_hooks
            if updates.post_hooks is not None:
                next_post_hooks = updates.post_hooks
            next_safety = existing.safety
            if updates.safety is not None:
                next_safety = updates.safety
            next_mcp_tools = existing.allowed_mcp_tools
            if updates.allowed_mcp_tools is not None:
                next_mcp_tools = updates.allowed_mcp_tools
            next_mcp_params = existing.mcp_tool_params
            if updates.mcp_tool_params is not None:
                next_mcp_params = updates.mcp_tool_params
            next_cognitive_tier = existing.cognitive_tier
            if "cognitive_tier" in fields_set:
                next_cognitive_tier = updates.cognitive_tier
            next_expected_inputs = existing.expected_inputs
            if updates.expected_inputs is not None:
                next_expected_inputs = updates.expected_inputs

            validated = Step(
                id=existing.id,
                slug=next_slug,
                organization_id=existing.organization_id,
                name=next_name,
                description=next_description,
                type=next_type,
                hook=next_hook,
                role_block_id=next_role_block_id,
                extraction_protocol_block_id=next_extraction_block_id,
                execution_persona_block_id=next_persona_block_id,
                criteria_block_ids=next_criteria_ids,
                pre_hooks=next_pre_hooks,
                post_hooks=next_post_hooks,
                safety=next_safety,
                allowed_mcp_tools=next_mcp_tools,
                mcp_tool_params=next_mcp_params,
                cognitive_tier=next_cognitive_tier,
                expected_inputs=next_expected_inputs,
                is_system_core=existing.is_system_core,
                engine_type=existing.engine_type,
                zone=existing.zone,
            )
            return await entities.upsert_step(validated)

    async def delete_step(self, step_id: str, force_delete: bool = False) -> bool:
        """Delete a step by primary key ID after checking active workflow step references.

        Args:
            step_id: Canonical stp_<hex32> step identifier.
            force_delete: When True, bypasses the active workflow reference check.

        Returns:
            True if deleted, False if the step did not exist.

        Raises:
            AppException: With DELETE_BLOCKED_BY_USAGE (HTTP 400) if referenced by a workflow.
        """
        async with self._acquire_entities() as entities:
            existing = await entities.get_step(step_id)
            if existing is None:
                return False

            if not force_delete:
                workflows = await entities.list_workflows()
                for wf in workflows:
                    for rule in wf.steps:
                        if rule.task_blueprint == step_id:
                            logger.error(
                                "[WorkflowRepository] %s: Step delete blocked by workflow %s usage for step %s",
                                ErrorCodes.DELETE_BLOCKED_BY_USAGE.name,
                                wf.id,
                                step_id,
                                extra={
                                    "error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value,
                                    "step_id": step_id,
                                    "workflow_id": wf.id,
                                },
                            )
                            raise AppException(
                                message="Step delete blocked by workflow usage.",
                                details={
                                    "error_code": ErrorCodes.DELETE_BLOCKED_BY_USAGE.value,
                                    "step_id": step_id,
                                    "workflow_id": wf.id,
                                },
                                status_code=400,
                            )

            return await entities.delete_step(step_id)
