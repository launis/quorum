"""Execution Management Service."""

from __future__ import annotations

import logging
from uuid import uuid4

from fastapi import BackgroundTasks

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, PermissionDeniedError, ResourceNotFoundError
from backend_v2.models.auth import TokenData
from backend_v2.models.v2_core import (
    ComponentType,
    DataDictionaryField,
    ExecutionCreate,
    ExecutionRecord,
    ExecutionStatus,
    ExecutionStepState,
    FrozenContext,
    Workflow,
)
from backend_v2.services.orchestrator.dag_executor import DAGExecutor

logger = logging.getLogger(__name__)

class ExecutionService:
    """Domain Service for Orchestration Executions enforcing Tenant Isolation and Authorization."""

    def __init__(self, repo: AbstractWorkflowRepository, executor: DAGExecutor):
        self.repo = repo
        self.executor = executor

    async def list_executions(self, initiator: TokenData) -> list[ExecutionRecord]:
        """Fetch executions securely based on Tenant/Role."""
        try:
            executions = await self.repo.get_all_executions()

            # SSOT MANDATE: Tenant Isolation Check
            if initiator.role != "ROOT":
                org_id = getattr(initiator, "organization_id", None)
                # Filtering logic to only show executions that belong to this organization or user
                # Currently simple filtering, will evolve as data schema strictly bounds executions to orgs
                executions = [
                    e for e in executions
                    if e.organization_id == org_id or e.created_by == initiator.id
                ]

            return executions
        except Exception as e:
            msg = f"Failed to list executions: {str(e)}"
            logger.error(f"[ExecutionService] {ErrorCodes.INTERNAL_SERVER_ERROR.name}: {msg}", exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR}
            ) from e

    async def get_execution(self, initiator: TokenData, execution_id: str) -> ExecutionRecord:
        """Fetch single execution securely."""
        data = await self.repo.get_execution(execution_id)
        if not data:
             logger.error(
                 f"[ExecutionService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: "
                 f"Execution {execution_id} not found."
             )
             raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)

        # SSOT MANDATE: Tenant Isolation Check
        org_id = getattr(initiator, "organization_id", None)
        if (initiator.role != "ROOT" and
            data.organization_id != org_id and
            data.created_by != initiator.id):
            msg = "You do not have permission to view this execution."
            logger.error(
                f"[ExecutionService] {ErrorCodes.PERMISSION_DENIED.name}: "
                f"User {initiator.id} attempted to access foreign execution {execution_id}."
            )
            raise PermissionDeniedError(msg)

        return data

    async def delete_execution(self, initiator: TokenData, execution_id: str) -> bool:
        """Securely delete an execution."""
        # This will also perform the authorization check
        await self.get_execution(initiator=initiator, execution_id=execution_id)

        try:
            return await self.repo.delete_execution(execution_id)
        except Exception as e:
            msg = f"Failed to delete execution {execution_id}: {str(e)}"
            logger.error(f"[ExecutionService] {ErrorCodes.INTERNAL_SERVER_ERROR.name}: {msg}", exc_info=True)
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR}
            ) from e

    async def start_execution(
        self,
        initiator: TokenData,
        payload: ExecutionCreate,
        background_tasks: BackgroundTasks
    ) -> ExecutionRecord:
        """Initialize and trigger workflow securely."""
        workflow_dict = await self.repo.get_workflow_by_id(payload.workflow_id)
        if not workflow_dict:
            logger.error(
                f"[ExecutionService] {ErrorCodes.RESOURCE_NOT_FOUND.name}: "
                f"Workflow {payload.workflow_id} not found."
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=payload.workflow_id)

        workflow = Workflow.model_validate(workflow_dict)

        # Auth Check
        org_id = getattr(initiator, "organization_id", None)
        if initiator.role != "ROOT" and workflow.organization_id not in [org_id, "system", None]:
            msg = "You do not have permission to execute this workflow."
            logger.error(
                f"[ExecutionService] {ErrorCodes.PERMISSION_DENIED.name}: "
                f"{initiator.id} tried to start foreign workflow '{workflow.id}'."
            )
            raise PermissionDeniedError(msg)

        # V2 MANDATE: Dynamically generate SDUI hints synchronously before execution
        ui_hints: dict[str, DataDictionaryField] = {}
        step_states: dict[str, ExecutionStepState] = {}
        for step_rule in workflow.steps:
            # We fetch the step definition to find its core mapped matrices/blocks
            step_dict = await self.repo.get_step(step_rule.task_blueprint)
            if not step_dict:
                from backend_v2.exceptions import ConfigurationError
                msg = f"Missing task blueprint {step_rule.task_blueprint} for DAG."
                logger.error(f"[ExecutionService] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                raise ConfigurationError(msg)

            # Populate initial pending step state for timeline
            step_name_raw = step_dict.get("name", step_rule.task_blueprint)
            step_label = step_rule.task_blueprint
            if isinstance(step_name_raw, dict):
                # Handle I18nText dict or legacy dict
                translations = step_name_raw.get("translations", step_name_raw)
                step_label = translations.get("fi", translations.get("en", step_rule.task_blueprint))
            elif isinstance(step_name_raw, str):
                step_label = step_name_raw

            step_states[step_rule.id] = ExecutionStepState(
                id=step_rule.id,
                label=step_label,
                status="pending"
            )

            prompt_blocks_refs = step_dict.get("prompt_blocks", [])
            for pb_slug in prompt_blocks_refs:
                pb_dict = await self.repo.get_prompt_block(pb_slug)
                if not pb_dict:
                     # V2 strictly says Fail Fast to guarantee auditability:
                     from backend_v2.exceptions import ConfigurationError
                     msg = (
                         f"SDUI Engine Error: PromptBlock '{pb_slug}' is missing "
                         f"but referenced in step '{step_rule.task_blueprint}'."
                     )
                     logger.error(f"[ExecutionService] {ErrorCodes.VALIDATION_FAILED.name}: {msg}", exc_info=True)
                     raise ConfigurationError(msg)

                dt = pb_dict.get("type")

                # Define component defaults based on Strict Block Types
                comp_type = ComponentType.HIDDEN
                if dt in ["float", "int", "string"] and pb_dict.get("scales"):
                    # Only numeric or scaled blocks map to sliders/gauges
                    comp_type = ComponentType.SLIDER
                elif dt in ["float", "int"]:
                    comp_type = ComponentType.SLIDER
                elif dt == "panel":
                    comp_type = ComponentType.DROPDOWN

                max_val = 6.0
                if "scales" in pb_dict and pb_dict["scales"]:
                    try:
                         # Attempt to find actual scaling max dynamically
                         max_val = float(max([s.get("score", 0) for s in pb_dict["scales"]]))
                    except Exception:
                         pass

                # Extract translation map for UI label
                label_obj = pb_dict.get("label", {})

                # Lock the hint
                ui_hints[pb_slug] = DataDictionaryField(
                    field_id=pb_slug,
                    component_type=comp_type,
                    options=[{"label": label_obj}] if label_obj else None,
                    validation_rules={"max": max_val}
                )

        # Strict Target Locale from Payload (Fail-Fast)
        target_locale = payload.target_locale

        execution_id = str(uuid4())
        initial_record = ExecutionRecord(
            id=execution_id,
            workflow_id=workflow.id,
            strictness_level=payload.strictness_level,
            status=ExecutionStatus.PENDING,
            render_blueprint=workflow.render_blueprint.model_dump(mode="json") if workflow.render_blueprint else None,
            raw_inputs=payload.raw_inputs,
            frozen_context=FrozenContext(ui_hints_snapshot=ui_hints),
            step_states=step_states,
            metadata={"target_locale": target_locale},
            results={},
            created_by=initiator.id,
            organization_id=getattr(initiator, "organization_id", None)
        )

        await self.repo.create_execution(initial_record.model_dump(mode="json"))

        # Fire Async Process
        background_tasks.add_task(
            self.executor.execute_workflow,
            execution_id=execution_id,
            workflow=workflow,
            raw_inputs=payload.raw_inputs.model_dump(mode="json")
        )

        return initial_record
