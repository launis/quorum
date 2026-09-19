"""Execution Ingress Service for startup, slot resolution, SDUI hint generation, and job dispatch."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import TypeAdapter, ValidationError

from backend_v2.database.interfaces import (
    IExecutionRepository,
    IOutputProfileRepository,
    IPromptBlockRepository,
    ISystemRepository,
    IWorkflowRepository,
)
from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.models.auth import TokenData
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.execution import ExecutionCreate, ExecutionRecord, ExecutionStep, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlockAdapter
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import DataDictionaryField
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.trace import ExecutionCreateDTO
from backend_v2.models.dtos.workflow_schema import WorkflowSchemaResponseDTO
from backend_v2.models.enums import ComponentType, EntityPrefix, ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.document_extraction import DocumentExtractionService
from backend_v2.services.ingress.smart_ingress_resolver import SmartIngressResolver
from backend_v2.services.studio.auth_validator import is_resource_accessible
from backend_v2.services.usage_service import UsageService

logger = logging.getLogger(__name__)

__all__ = ["ExecutionIngressService", "create_execution_record"]


def create_execution_record(
    execution_id: str,
    workflow_id: str,
    raw_inputs: WorkflowInputs,
    frozen_context: FrozenContext,
    source_identity_manifest: dict[str, str],
    target_locale: str = "en",
    output_profile_id: str | None = None,
    metadata: ExecutionMetadata | None = None,
    status: ExecutionStatus = ExecutionStatus.PENDING,
    steps: list[ExecutionStep] | None = None,
    step_states: dict[str, ExecutionStep] | None = None,
    created_by: str | None = None,
    organization_id: str | None = None,
) -> ExecutionRecord:
    """Type-safe factory for ExecutionRecord creation."""
    try:
        resolved_metadata = (
            TypeAdapter(ExecutionMetadata).validate_python(metadata) if metadata is not None else ExecutionMetadata()
        )
        return ExecutionRecord(
            id=execution_id,
            workflow_id=workflow_id,
            target_locale=target_locale,
            output_profile_id=output_profile_id,
            metadata=resolved_metadata,
            status=status,
            raw_inputs=raw_inputs,
            frozen_context=frozen_context,
            source_identity_manifest=source_identity_manifest,
            steps=steps if steps is not None else [],
            step_states=step_states if step_states is not None else {},
            created_by=created_by,
            organization_id=organization_id,
            progress=None,
            status_message=None,
        )
    except ValidationError as e:
        logger.error("[ExecutionIngressService] Fail-Fast: ExecutionRecord creation failed: %s", e, exc_info=True)
        raise AppException(
            message=f"ExecutionRecord creation failed: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        ) from e


async def _generate_sdui_hints(
    workflow: Workflow,
    prompt_block_repo: IPromptBlockRepository,
    workflow_repo: IWorkflowRepository,
    target_locale: str,
) -> tuple[dict[str, DataDictionaryField], list[ExecutionStep], dict[str, ExecutionStep]]:
    """Generates SDUI hints and initial timeline step states."""
    ui_hints: dict[str, DataDictionaryField] = {}
    steps: list[ExecutionStep] = []
    step_states: dict[str, ExecutionStep] = {}

    for step_rule in workflow.steps:
        step_dict = await workflow_repo.get_step_by_id(step_rule.task_blueprint)
        if not step_dict:
            msg = f"Missing task blueprint {step_rule.task_blueprint} for DAG."
            logger.error("[ExecutionIngressService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ConfigurationError(msg)

        try:
            step_obj = Step.model_validate(step_dict)
        except Exception as e:
            msg = f"Invalid step format in blueprint {step_rule.task_blueprint}: {e}"
            logger.error("[ExecutionIngressService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(
                message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            ) from e

        st = ExecutionStep(id=step_rule.id, label=step_obj.name.resolve(target_locale), status=ExecutionStatus.PENDING)
        steps.append(st)
        step_states[step_rule.id] = st

        pb_refs = [b for b in [step_obj.role_block_id, step_obj.extraction_protocol_block_id] if b] + (
            step_obj.criteria_block_ids if step_obj.criteria_block_ids is not None else []
        )

        for pb_id in pb_refs:
            pb_dict = await prompt_block_repo.get_prompt_block_by_id(pb_id)
            if not pb_dict:
                msg = f"PromptBlock '{pb_id}' is missing but referenced in step '{step_rule.task_blueprint}'."
                logger.error("[ExecutionIngressService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise ConfigurationError(msg)

            try:
                pb_obj = PromptBlockAdapter.validate_python(pb_dict, strict=False)
            except Exception as e:
                msg = f"Invalid prompt block format for {pb_id}: {e}"
                logger.error("[ExecutionIngressService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                ) from e

            if isinstance(pb_obj, MatrixPromptBlock):
                max_val = float(max((s.score for s in pb_obj.scales), default=5))
                ui_hints[pb_id] = DataDictionaryField(
                    field_id=pb_id,
                    component_type=ComponentType.SLIDER,
                    options=None,
                    validation_rules={"max": max_val},
                )
            else:
                ui_hints[pb_id] = DataDictionaryField(
                    field_id=pb_id,
                    component_type=ComponentType.HIDDEN,
                    options=None,
                    validation_rules=None,
                )

    return ui_hints, steps, step_states


class ExecutionIngressService:
    """Service managing execution creation, validation, dynamic hints, and worker dispatch."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        prompt_block_repo: IPromptBlockRepository | None = None,
        output_profile_repo: IOutputProfileRepository | None = None,
        system_repo: ISystemRepository | None = None,
        usage_service: UsageService | None = None,
    ) -> None:
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo
        self.prompt_block_repo = prompt_block_repo
        self.output_profile_repo = output_profile_repo
        self.system_repo = system_repo
        self.usage_service = usage_service

    async def get_workflow_ui_schema(self, workflow_id: str) -> WorkflowSchemaResponseDTO:
        """Retrieve expected inputs schema for dynamic frontend forms."""
        workflow_record = await self.workflow_repo.get_workflow_by_id(workflow_id)
        if not workflow_record:
            raise ResourceNotFoundError(resource_type="workflow", resource_id=workflow_id)
        workflow = Workflow.model_validate(workflow_record)
        return WorkflowSchemaResponseDTO(expected_inputs=workflow.expected_inputs)

    async def start_execution(
        self,
        initiator: TokenData,
        payload: ExecutionCreate,
        arq_pool: Any,
        doc_service: DocumentExtractionService | None = None,
    ) -> ExecutionRecord:
        """Initialize and trigger workflow execution asynchronously."""
        workflow_dict = await self.workflow_repo.get_workflow_by_id(payload.workflow_id)
        if not workflow_dict:
            raise ResourceNotFoundError(resource_type="workflow", resource_id=payload.workflow_id)

        workflow = Workflow.model_validate(workflow_dict)
        if not is_resource_accessible(initiator, workflow.organization_id, is_public=workflow.is_public):
            raise PermissionDeniedError("You do not have permission to execute this workflow.")

        org_id = initiator.organization_id
        if org_id and self.usage_service is not None:
            is_quota_safe = await self.usage_service.check_quota(org_id)
            if not is_quota_safe:
                msg = f"Organization '{org_id}' has exceeded its execution quota."
                logger.warning("[ExecutionIngressService] Circuit Breaker Tripped: %s", msg)
                raise AppException(
                    message=msg, status_code=402, details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value}
                )

        target_locale = payload.target_locale
        resolver = SmartIngressResolver()
        resolved_ingress = resolver.resolve(payload.raw_inputs, workflow.expected_inputs, target_locale)

        if payload.raw_inputs is not None:
            updated_raw = payload.raw_inputs.model_copy(update={"dynamic_inputs": resolved_ingress.resolved_inputs})
            payload = payload.model_copy(update={"raw_inputs": updated_raw})

        if doc_service and payload.raw_inputs:
            processed_ingress = await doc_service.process_ingress_payload(payload.raw_inputs)
            payload = payload.model_copy(update={"raw_inputs": processed_ingress})

        source_identity_manifest = dict(resolved_ingress.source_identity_manifest)
        if self.prompt_block_repo is None:
            raise AppException("PromptBlock repository is required for execution start", 500)

        ui_hints, steps, step_states = await _generate_sdui_hints(
            workflow, self.prompt_block_repo, self.workflow_repo, target_locale
        )

        resolved_profile_id: str | None = (
            payload.profile_id if payload.profile_id is not None else workflow.default_profile_id
        )
        if resolved_profile_id is not None:
            if self.output_profile_repo is None:
                raise AppException("OutputProfile repository is required for profile resolution", 500)
            profile_dict = await self.output_profile_repo.get_output_profile_by_id(resolved_profile_id)
            if not profile_dict:
                raise AppException(
                    f"Profile '{resolved_profile_id}' not found.",
                    404,
                    {"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                )
            profile_obj = OutputProfile.model_validate(profile_dict)
            if profile_obj.workflow_id and profile_obj.workflow_id != workflow.id:
                raise AppException(
                    f"Profile '{resolved_profile_id}' mismatch.",
                    400,
                    {"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

        resolved_registry_id = (
            payload.model_registry_id if payload.model_registry_id is not None else workflow.model_registry_id
        )
        if not resolved_registry_id:
            raise AppException(
                f"No model_registry_id provided and workflow '{workflow.id}' has no model_registry_id.",
                404,
                {"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )

        if self.system_repo is None:
            raise AppException("System repository is required for registry resolution", 500)
        registry_obj = await self.system_repo.get_model_registry(resolved_registry_id)
        if not registry_obj:
            raise AppException(
                f"Model registry '{resolved_registry_id}' not found.",
                404,
                {"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )

        execution_id = generate_opaque_id(EntityPrefix.EXECUTION)
        initial_record = create_execution_record(
            execution_id=execution_id,
            workflow_id=workflow.id,
            raw_inputs=WorkflowInputs.model_validate(payload.raw_inputs.model_dump(exclude_unset=True)),
            frozen_context=FrozenContext(ui_hints_snapshot=ui_hints),
            source_identity_manifest=source_identity_manifest,
            output_profile_id=resolved_profile_id,
            target_locale=target_locale,
            steps=steps,
            step_states=step_states,
            metadata=ExecutionMetadata(
                matrix_sampling_strategy=payload.matrix_sampling_strategy,
                workflow_version=workflow.version,
                provider_override=payload.provider_override,
                model_registry_id=resolved_registry_id,
            ),
            created_by=initiator.id,
            organization_id=initiator.organization_id,
        )

        create_dto = ExecutionCreateDTO(
            workflow_id=workflow.id,
            id=execution_id,
            target_locale=target_locale,
            status=ExecutionStatus.PENDING.value,
            active_profile_id=resolved_profile_id,
            output_profile_id=resolved_profile_id,
            raw_inputs=payload.raw_inputs,
            organization_id=initiator.organization_id,
            created_by=initiator.id,
            metadata=initial_record.metadata,
        )
        await self.exec_repo.create_execution(create_dto)

        await arq_pool.enqueue_job(
            "execute_workflow_job",
            workflow_id=workflow.id,
            inputs=payload.raw_inputs.model_dump(mode="json"),
            execution_id=execution_id,
            organization_id=initiator.organization_id,
            user_id=initiator.id,
        )

        return initial_record
