"""Execution Ingress Service for startup, slot resolution, SDUI hint generation, and job dispatch."""

from __future__ import annotations

import logging
from typing import Any

from pydantic import ConfigDict, Field, TypeAdapter, ValidationError

from backend_v2.core.telemetry import inject_trace_context
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
from backend_v2.models.core_base import V2CoreBase, generate_opaque_id
from backend_v2.models.domain.execution import ExecutionCreate, ExecutionRecord, ExecutionStep, FrozenContext
from backend_v2.models.domain.inputs import WorkflowInputs, WorkflowInputsIngress
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlockAdapter
from backend_v2.models.domain.step import Step
from backend_v2.models.domain.system_config import DataDictionaryField, SystemValidationRulesDTO
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
    """Type-safe factory for ExecutionRecord creation.

    Args:
        execution_id: Canonical Opaque Stripe ID for the execution.
        workflow_id: Target workflow identifier.
        raw_inputs: Initial workflow input domain model.
        frozen_context: Snapshot context including dynamic UI hints.
        source_identity_manifest: Mapping of source identity aliases.
        target_locale: Target localization code.
        output_profile_id: Optional output profile identifier.
        metadata: Optional execution telemetry and metadata.
        status: Initial execution status.
        steps: Optional list of execution steps.
        step_states: Optional dictionary mapping step IDs to steps.
        created_by: Optional creator user identifier.
        organization_id: Optional owning organization identifier.

    Returns:
        Instantiated and validated ExecutionRecord.

    Raises:
        AppException: If ValidationError occurs during instantiation (ErrorCodes.VALIDATION_FAILED).
    """
    try:
        injected_carrier = inject_trace_context()
        if isinstance(metadata, ExecutionMetadata):
            resolved_telemetry = metadata.telemetry if metadata.telemetry is not None else injected_carrier
            resolved_metadata = metadata.model_copy(update={"telemetry": resolved_telemetry})
        elif metadata is not None:
            resolved_metadata = TypeAdapter(ExecutionMetadata).validate_python(metadata)
            if resolved_metadata.telemetry is None:
                resolved_metadata = resolved_metadata.model_copy(update={"telemetry": injected_carrier})
        else:
            resolved_metadata = ExecutionMetadata(telemetry=injected_carrier)
        final_steps: list[ExecutionStep] = []
        if steps is not None:
            final_steps = steps

        final_step_states: dict[str, ExecutionStep] = {}
        if step_states is not None:
            final_step_states = step_states

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
            steps=final_steps,
            step_states=final_step_states,
            created_by=created_by,
            organization_id=organization_id,
            progress=None,
            status_message=None,
        )
    except ValidationError as e:
        logger.error(
            "[ExecutionIngressService] Fail-Fast: ExecutionRecord creation failed: %s",
            e,
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
        raise AppException(
            message=f"ExecutionRecord creation failed: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        ) from e


class SduiHintsGenerationDTO(V2CoreBase):
    """Result of generating SDUI hints and initial timeline step states."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    ui_hints: dict[str, DataDictionaryField] = Field(default_factory=dict)
    steps: list[ExecutionStep] = Field(default_factory=list)
    step_states: dict[str, ExecutionStep] = Field(default_factory=dict)


async def _generate_sdui_hints(
    workflow: Workflow,
    prompt_block_repo: IPromptBlockRepository,
    workflow_repo: IWorkflowRepository,
    target_locale: str,
) -> SduiHintsGenerationDTO:
    """Generates SDUI hints and initial timeline step states.

    Args:
        workflow: Workflow domain model containing step rules.
        prompt_block_repo: Repository for prompt block lookups.
        workflow_repo: Repository for step blueprint lookups.
        target_locale: Target localization code.

    Returns:
        SduiHintsGenerationDTO containing ui_hints, steps, and step_states.

    Raises:
        ConfigurationError: If a referenced step or prompt block blueprint is missing.
        AppException: If step blueprint format or prompt block model validation fails.
    """
    ui_hints: dict[str, DataDictionaryField] = {}
    steps: list[ExecutionStep] = []
    step_states: dict[str, ExecutionStep] = {}

    for step_rule in workflow.steps:
        step_dict = await workflow_repo.get_step_by_id(step_rule.task_blueprint)
        if not step_dict:
            msg = f"Missing task blueprint {step_rule.task_blueprint} for DAG."
            logger.error(
                "[ExecutionIngressService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise ConfigurationError(msg)

        try:
            step_obj = Step.model_validate(step_dict)
        except Exception as e:
            msg = f"Invalid step format in blueprint {step_rule.task_blueprint}: {e}"
            logger.error(
                "[ExecutionIngressService] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            ) from e

        st = ExecutionStep(id=step_rule.id, label=step_obj.name.resolve(target_locale), status=ExecutionStatus.PENDING)
        steps.append(st)
        step_states[step_rule.id] = st

        criteria_ids: list[str] = []
        if step_obj.criteria_block_ids is not None:
            criteria_ids = step_obj.criteria_block_ids
        pb_refs = [b for b in [step_obj.role_block_id, step_obj.extraction_protocol_block_id] if b] + criteria_ids

        for pb_id in pb_refs:
            pb_dict = await prompt_block_repo.get_prompt_block_by_id(pb_id)
            if not pb_dict:
                msg = f"PromptBlock '{pb_id}' is missing but referenced in step '{step_rule.task_blueprint}'."
                logger.error(
                    "[ExecutionIngressService] %s: %s",
                    ErrorCodes.VALIDATION_FAILED.name,
                    msg,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
                raise ConfigurationError(msg)

            try:
                pb_obj = PromptBlockAdapter.validate_python(pb_dict, strict=False)
            except Exception as e:
                msg = f"Invalid prompt block format for {pb_id}: {e}"
                logger.error(
                    "[ExecutionIngressService] %s: %s",
                    ErrorCodes.INTERNAL_SERVER_ERROR.name,
                    msg,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                )
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                ) from e

            if isinstance(pb_obj, MatrixPromptBlock):
                max_val = float(max((s.score for s in pb_obj.scales), default=5))
                ui_hints[pb_id] = DataDictionaryField(
                    field_id=pb_id,
                    component_type=ComponentType.SLIDER,
                    options=None,
                    validation_rules=SystemValidationRulesDTO(max=max_val),
                )
            else:
                ui_hints[pb_id] = DataDictionaryField(
                    field_id=pb_id,
                    component_type=ComponentType.HIDDEN,
                    options=None,
                    validation_rules=None,
                )

    return SduiHintsGenerationDTO(ui_hints=ui_hints, steps=steps, step_states=step_states)


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
        """Initializes the execution ingress service with repository dependencies.

        Args:
            exec_repo: Execution record repository.
            workflow_repo: Workflow definitions repository.
            prompt_block_repo: Optional prompt block repository.
            output_profile_repo: Optional output profile repository.
            system_repo: Optional system repository.
            usage_service: Optional usage tracking service.
        """
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo
        self.prompt_block_repo = prompt_block_repo
        self.output_profile_repo = output_profile_repo
        self.system_repo = system_repo
        self.usage_service = usage_service

    async def get_workflow_ui_schema(self, workflow_id: str) -> WorkflowSchemaResponseDTO:
        """Retrieve expected inputs schema for dynamic frontend forms.

        Args:
            workflow_id: Canonical Opaque Stripe ID of the workflow.

        Returns:
            WorkflowSchemaResponseDTO containing the list of expected input models.

        Raises:
            ResourceNotFoundError: If the specified workflow cannot be located.
        """
        workflow_record = await self.workflow_repo.get_workflow_by_id(workflow_id)
        if not workflow_record:
            logger.error(
                "[ExecutionIngressService] %s: Resource 'workflow' with id '%s' not found",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                workflow_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
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
        """Initialize and trigger workflow execution asynchronously.

        Args:
            initiator: Authenticated user token claims.
            payload: Execution creation request payload.
            arq_pool: Async Arq Redis pool for queueing jobs.
            doc_service: Optional document extraction service.

        Returns:
            Initial ExecutionRecord with PENDING status.

        Raises:
            ResourceNotFoundError: If workflow, profile, or model registry does not exist.
            PermissionDeniedError: If initiator lacks access to the workflow.
            AppException: If quota exceeded (402 RATE_LIMIT_EXCEEDED), profile mismatch (400 VALIDATION_FAILED),
                or required repository is missing (500 SERVICE_DEPENDENCY_MISSING).
        """
        workflow_dict = await self.workflow_repo.get_workflow_by_id(payload.workflow_id)
        if not workflow_dict:
            logger.error(
                "[ExecutionIngressService] %s: Resource 'workflow' with id '%s' not found",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                payload.workflow_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
            raise ResourceNotFoundError(resource_type="workflow", resource_id=payload.workflow_id)

        workflow = Workflow.model_validate(workflow_dict)
        if not is_resource_accessible(initiator, workflow.organization_id, is_public=workflow.is_public):
            logger.error(
                "[ExecutionIngressService] %s: User '%s' denied access to workflow '%s'",
                ErrorCodes.PERMISSION_DENIED.name,
                initiator.id,
                workflow.id,
                extra={"error_code": ErrorCodes.PERMISSION_DENIED.value},
            )
            raise PermissionDeniedError("You do not have permission to execute this workflow.")

        org_id = initiator.organization_id
        if org_id and self.usage_service is not None:
            is_quota_safe = await self.usage_service.check_quota(org_id)
            if not is_quota_safe:
                msg = f"Organization '{org_id}' has exceeded its execution quota."
                logger.error(
                    "[ExecutionIngressService] Circuit Breaker Tripped: %s",
                    msg,
                    extra={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value},
                )
                raise AppException(
                    message=msg, status_code=402, details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value}
                )

        target_locale = payload.target_locale
        resolver = SmartIngressResolver()
        ingress_inputs: WorkflowInputsIngress | None = None
        if isinstance(payload.raw_inputs, WorkflowInputsIngress):
            ingress_inputs = payload.raw_inputs
        resolved_ingress = resolver.resolve(ingress_inputs, workflow.expected_inputs, target_locale)

        if payload.raw_inputs is not None:
            updated_raw = payload.raw_inputs.model_copy(update={"dynamic_inputs": resolved_ingress.resolved_inputs})
            payload = payload.model_copy(update={"raw_inputs": updated_raw})

        if doc_service and isinstance(payload.raw_inputs, WorkflowInputsIngress):
            processed_ingress = await doc_service.process_ingress_payload(payload.raw_inputs)
            payload = payload.model_copy(update={"raw_inputs": processed_ingress})

        source_identity_manifest = dict(resolved_ingress.source_identity_manifest)
        if self.prompt_block_repo is None:
            logger.error(
                "[ExecutionIngressService] %s: PromptBlock repository is required for execution start",
                ErrorCodes.SERVICE_DEPENDENCY_MISSING.name,
                extra={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )
            raise AppException(
                message="PromptBlock repository is required for execution start",
                status_code=500,
                details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )

        sdui_hints = await _generate_sdui_hints(workflow, self.prompt_block_repo, self.workflow_repo, target_locale)
        ui_hints = sdui_hints.ui_hints
        steps = sdui_hints.steps
        step_states = sdui_hints.step_states

        resolved_profile_id: str | None = (
            payload.profile_id if payload.profile_id is not None else workflow.default_profile_id
        )
        if resolved_profile_id is not None:
            if self.output_profile_repo is None:
                logger.error(
                    "[ExecutionIngressService] %s: OutputProfile repository is required for profile resolution",
                    ErrorCodes.SERVICE_DEPENDENCY_MISSING.name,
                    extra={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
                )
                raise AppException(
                    message="OutputProfile repository is required for profile resolution",
                    status_code=500,
                    details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
                )
            profile_dict = await self.output_profile_repo.get_output_profile_by_id(resolved_profile_id)
            if not profile_dict:
                logger.error(
                    "[ExecutionIngressService] %s: Profile '%s' not found",
                    ErrorCodes.RESOURCE_NOT_FOUND.name,
                    resolved_profile_id,
                    extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                )
                raise AppException(
                    message=f"Profile '{resolved_profile_id}' not found.",
                    status_code=404,
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                )
            profile_obj = OutputProfile.model_validate(profile_dict)
            if profile_obj.workflow_id and profile_obj.workflow_id != workflow.id:
                logger.error(
                    "[ExecutionIngressService] %s: Profile '%s' mismatch with workflow '%s'",
                    ErrorCodes.VALIDATION_FAILED.name,
                    resolved_profile_id,
                    workflow.id,
                    extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )
                raise AppException(
                    message=f"Profile '{resolved_profile_id}' mismatch.",
                    status_code=400,
                    details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                )

        resolved_registry_id = (
            payload.model_registry_id if payload.model_registry_id is not None else workflow.model_registry_id
        )
        if not resolved_registry_id:
            logger.error(
                "[ExecutionIngressService] %s: No model_registry_id provided and workflow '%s' has none",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                workflow.id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
            raise AppException(
                message=f"No model_registry_id provided and workflow '{workflow.id}' has no model_registry_id.",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )

        if self.system_repo is None:
            logger.error(
                "[ExecutionIngressService] %s: System repository is required for registry resolution",
                ErrorCodes.SERVICE_DEPENDENCY_MISSING.name,
                extra={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )
            raise AppException(
                message="System repository is required for registry resolution",
                status_code=500,
                details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )
        registry_obj = await self.system_repo.get_model_registry(resolved_registry_id)
        if not registry_obj:
            logger.error(
                "[ExecutionIngressService] %s: Model registry '%s' not found",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                resolved_registry_id,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
            raise AppException(
                message=f"Model registry '{resolved_registry_id}' not found.",
                status_code=404,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )

        injected_carrier = inject_trace_context()
        exec_metadata = ExecutionMetadata(
            matrix_sampling_strategy=payload.matrix_sampling_strategy,
            workflow_version=workflow.version,
            provider_override=payload.provider_override,
            model_registry_id=resolved_registry_id,
            telemetry=injected_carrier,
        )

        create_dto = ExecutionCreateDTO(
            workflow_id=workflow.id,
            target_locale=target_locale,
            status=ExecutionStatus.PENDING.value,
            active_profile_id=resolved_profile_id,
            output_profile_id=resolved_profile_id,
            raw_inputs=payload.raw_inputs,
            organization_id=initiator.organization_id,
            created_by=initiator.id,
            metadata=exec_metadata,
        )
        created_id = await self.exec_repo.create_execution(create_dto)
        execution_id = (
            created_id
            if isinstance(created_id, str) and created_id.startswith("exe_")
            else generate_opaque_id(EntityPrefix.EXECUTION)
        )

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
            metadata=exec_metadata,
            created_by=initiator.id,
            organization_id=initiator.organization_id,
        )

        await arq_pool.enqueue_job(
            "execute_workflow_job",
            workflow_id=workflow.id,
            inputs=payload.raw_inputs.model_dump(mode="json"),
            execution_id=execution_id,
            organization_id=initiator.organization_id,
            user_id=initiator.id,
        )

        return initial_record
