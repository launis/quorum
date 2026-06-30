"""Execution Management Service."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from arq.connections import ArqRedis
from pydantic import ValidationError

from backend_v2.database.interfaces import (
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
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
from backend_v2.models.auth import SystemOrganizations, TokenData
from backend_v2.models.state import WorkflowState  # noqa: F401 (Ensures ExecutionRecord is rebuilt)
from backend_v2.models.v2_core import (
    ComponentType,
    DataDictionaryField,
    ExecutionCreate,
    ExecutionRecord,
    ExecutionStatus,
    ExecutionStepState,
    FrozenContext,
    HumanOverrideRequest,
    PromptBlock,
    Step,
    Workflow,
    WorkflowInputs,
)
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.document_extraction import DocumentExtractionService
from backend_v2.services.flattener import FlatFileService
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.storage import get_storage_driver
from backend_v2.services.usage_service import UsageService

if TYPE_CHECKING:
    from backend_v2.services.orchestrator.dag_executor import DAGExecutor

logger = logging.getLogger(__name__)


def create_execution_record(
    execution_id: str,
    workflow_id: str,
    raw_inputs: WorkflowInputs,
    frozen_context: FrozenContext,
    source_identity_manifest: dict[str, str],
    **extra_persistence_fields: Any,
) -> ExecutionRecord:
    """Type-safe factory for ExecutionRecord creation.

    Centralizes initialization logic to prevent field drift between
    dag_executor.py and execution.py instantiation sites.

    Args:
        execution_id: Opaque Stripe ID for the execution.
        workflow_id: ID of the workflow definition.
        raw_inputs: Validated user inputs by role.
        frozen_context: Immutable snapshot of context at execution start.
        **extra_persistence_fields: Additional presentation-layer fields.

    Returns:
        A strictly validated ExecutionRecord instance.

    Raises:
        AppException: If Pydantic validation fails (VALIDATION_FAILED).
    """
    try:
        return ExecutionRecord(
            id=execution_id,
            workflow_id=workflow_id,
            raw_inputs=raw_inputs,
            frozen_context=frozen_context,
            source_identity_manifest=source_identity_manifest,
            **extra_persistence_fields,
        )
    except ValidationError as e:
        logger.error(
            "[ExecutionService] Fail-Fast: ExecutionRecord creation failed: %s",
            e,
            exc_info=True,
        )
        raise AppException(
            message=f"ExecutionRecord creation failed: {e}",
            status_code=500,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        ) from e


class ExecutionService:
    """Domain Service for Orchestration Executions enforcing Tenant Isolation and Authorization."""

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository,
        identity_repo: IIdentityRepository,
        system_repo: ISystemRepository,
        usage_service: UsageService,
        executor: DAGExecutor,
    ):
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo
        self.comp_repo = comp_repo
        self.identity_repo = identity_repo
        self.system_repo = system_repo
        self.usage_service = usage_service
        self.executor = executor

    async def list_executions(self, initiator: TokenData) -> list[ExecutionRecord]:
        """Fetch executions securely based on Tenant/Role."""
        try:
            executions = await self.exec_repo.get_all_executions()

            # SSOT MANDATE: Tenant Isolation Check
            if initiator.role != "ROOT":
                org_id = getattr(initiator, "organization_id", None)
                # Filtering logic to only show executions that belong to this organization or user
                # Currently simple filtering, will evolve as data schema strictly bounds executions to orgs
                executions = [e for e in executions if e.organization_id == org_id or e.created_by == initiator.id]

            # Dynamic projection of is_resumable using TaskGroup for maximum concurrent caching
            async with asyncio.TaskGroup() as tg:
                tasks = []
                for e in executions:
                    tasks.append(tg.create_task(self.check_resumability(e)))

            updated_executions = []
            for e, t in zip(executions, tasks, strict=True):
                updated_executions.append(e.model_copy(update={"is_resumable": t.result()}))

            return updated_executions
        except Exception as e:
            msg = f"Failed to list executions: {str(e)}"
            logger.error("[ExecutionService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
            ) from e

    async def get_execution(self, initiator: TokenData, execution_id: str) -> ExecutionRecord:
        """Fetch single execution securely."""
        data = await self.exec_repo.get_execution(execution_id)
        if not data:
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)

        # SSOT MANDATE: Tenant Isolation Check
        org_id = getattr(initiator, "organization_id", None)
        if initiator.role != "ROOT" and data.organization_id != org_id and data.created_by != initiator.id:
            msg = "You do not have permission to view this execution."
            raise PermissionDeniedError(msg)

        # Dynamic projection of is_resumable flag on fetch
        is_resumable = await self.check_resumability(data)
        return data.model_copy(update={"is_resumable": is_resumable})

    async def stream_status(self, initiator: TokenData, execution_id: str) -> AsyncGenerator[str]:
        """Stream execution status and results securely via Server-Sent Events (SSE)."""
        # 1. Authorize connection first
        await self.get_execution(initiator=initiator, execution_id=execution_id)

        try:
            while True:
                # Poll database (Fallback from Redis Pub/Sub for simpler local portability)
                record = await self.get_execution(initiator=initiator, execution_id=execution_id)

                # V2 Protocol Requirement: JSON Payload inside 'data: '
                yield f"data: {record.model_dump_json()}\n\n"

                if record.status in [ExecutionStatus.COMPLETED, ExecutionStatus.FAILED]:
                    break

                await asyncio.sleep(2)
        except Exception as e:
            logger.error("SSE Error for execution %s: %s", execution_id, str(e), exc_info=True)
            yield f'data: {{"error": "SSE Stream Interrupted: {str(e)}"}}\n\n'

    async def delete_execution(self, initiator: TokenData, execution_id: str) -> bool:
        """Securely delete an execution."""
        record = await self.exec_repo.get_execution(execution_id, hydrate=False)
        if not record:
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)

        # SSOT MANDATE: Tenant Isolation Check
        org_id = getattr(initiator, "organization_id", None)
        if initiator.role != "ROOT" and record.organization_id != org_id and record.created_by != initiator.id:
            msg = "You do not have permission to delete this execution."
            raise PermissionDeniedError(msg)

        try:
            # Clean up all offloaded blobs and input files (Total Annihilation)
            storage = get_storage_driver()
            try:
                await storage.delete_directory(f"executions/{execution_id}")
            except AppException as e:
                if e.status_code == 404:
                    logger.warning("[ExecutionService] Execution directory not found during cleanup, ignoring.")
                else:
                    msg = f"Failed to clean up directory executions/{execution_id} during deletion."
                    logger.error("[ExecutionService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                    ) from e
            except Exception as e:
                msg = f"Failed to clean up directory executions/{execution_id} during deletion."
                logger.error("[ExecutionService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                ) from e

            return await self.exec_repo.delete_execution(execution_id)
        except Exception as e:
            msg = f"Failed to delete execution {execution_id}: {str(e)}"
            logger.error("[ExecutionService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
            ) from e

    async def start_execution(
        self,
        initiator: TokenData,
        payload: ExecutionCreate,
        arq_pool: ArqRedis,
        doc_service: DocumentExtractionService | None = None,
    ) -> ExecutionRecord:
        """Initialize and trigger workflow securely."""
        # 1. O(1) Manifesti: Poimi alkuperäiset tiedostojen nimet (ja muut näyttönimet)
        # ennen kuin Eager Extraction muuntaa ne pelkäksi tekstiksi.
        source_identity_manifest: dict[str, str] = {}
        if payload.raw_inputs and payload.raw_inputs.dynamic_inputs:
            for k, v in payload.raw_inputs.dynamic_inputs.items():
                if isinstance(v, dict) and "content_base64" in v:
                    source_identity_manifest[k] = v.get("filename", "Tuntematon lähde")

        # EAGER EXTRACTION MUST HAPPEN HERE BEFORE DB COMMIT
        if doc_service and payload.raw_inputs:
            processed_ingress = await doc_service.process_ingress_payload(payload.raw_inputs)
            payload = payload.model_copy(update={"raw_inputs": processed_ingress})

        workflow_dict = await self.workflow_repo.get_workflow_by_id(payload.workflow_id)
        if not workflow_dict:
            raise ResourceNotFoundError(resource_type="workflow", resource_id=payload.workflow_id)

        workflow = Workflow.model_validate(workflow_dict)

        # Auth Check
        org_id = getattr(initiator, "organization_id", None)
        if initiator.role != "ROOT" and workflow.organization_id not in [org_id, SystemOrganizations.ROOT_SYSTEM, None]:
            msg = "You do not have permission to execute this workflow."
            raise PermissionDeniedError(msg)

        # Circuit Breaker: Denial of Wallet Protection
        if org_id:
            is_quota_safe = await self.usage_service.check_quota(org_id)
            if not is_quota_safe:
                msg = f"Organization '{org_id}' has exceeded its execution quota."
                logger.warning("[ExecutionService] Circuit Breaker Tripped: %s", msg)
                raise AppException(
                    message=msg,
                    status_code=402,
                    details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value},
                )

        # V2 MANDATE: Strict Fail-Fast Validation of required inputs synchronously
        raw_inputs_dict = payload.raw_inputs.model_dump(exclude_unset=True)
        dynamic_inputs = raw_inputs_dict.get("dynamic_inputs", {})
        missing_fields = []
        for expected in workflow.expected_inputs:
            if expected.required:
                val = raw_inputs_dict.get(expected.input_key)
                if val is None:
                    val = dynamic_inputs.get(expected.input_key)

                if val is None:
                    missing_fields.append(expected.input_key)
                elif isinstance(val, str) and not val.strip():
                    missing_fields.append(expected.input_key)
                elif isinstance(val, list) and not val:
                    missing_fields.append(expected.input_key)
                elif isinstance(val, dict) and not val:
                    missing_fields.append(expected.input_key)

        if missing_fields:
            msg = f"Missing required inputs from payload: {', '.join(missing_fields)}"
            raise AppException(
                message=msg,
                status_code=400,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "fields": missing_fields},
            )

        # Strict Target Locale from Payload (Fail-Fast)
        target_locale = payload.target_locale

        # 2. O(1) Manifesti: Täytä puuttuvat lähteet workflow schema labelilla
        for expected in workflow.expected_inputs:
            if expected.input_key not in source_identity_manifest:
                source_identity_manifest[expected.input_key] = expected.label.resolve(target_locale)

        # V2 MANDATE: Dynamically generate SDUI hints synchronously before execution
        ui_hints: dict[str, DataDictionaryField] = {}
        step_states: dict[str, ExecutionStepState] = {}
        for step_rule in workflow.steps:
            # We fetch the step definition to find its core mapped matrices/blocks
            step_dict = await self.workflow_repo.get_step_by_id(step_rule.task_blueprint)
            if not step_dict:
                msg = f"Missing task blueprint {step_rule.task_blueprint} for DAG."
                logger.error("[ExecutionService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ConfigurationError(msg)

            try:
                # V2 MANDATE: Enforce Pydantic validation on the Step
                step_obj = Step.model_validate(step_dict)
            except Exception as e:
                msg = f"Invalid step format in blueprint {step_rule.task_blueprint}: {str(e)}"
                logger.error("[ExecutionService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                ) from e

            # Populate initial pending step state for timeline
            step_label = step_obj.name.resolve(target_locale)
            step_states[step_rule.id] = ExecutionStepState(id=step_rule.id, label=step_label, status="pending")

            prompt_blocks_refs = []
            if step_obj.role_block_id:
                prompt_blocks_refs.append(step_obj.role_block_id)
            if step_obj.extraction_protocol_block_id:
                prompt_blocks_refs.append(step_obj.extraction_protocol_block_id)
            if step_obj.criteria_block_ids:
                prompt_blocks_refs.extend(step_obj.criteria_block_ids)

            for pb_id in prompt_blocks_refs:
                pb_dict = await self.comp_repo.get_prompt_block_by_id(pb_id)
                if not pb_dict:
                    # V2 strictly says Fail Fast to guarantee auditability:
                    msg = (
                        f"SDUI Engine Error: PromptBlock '{pb_id}' is missing "
                        f"but referenced in step '{step_rule.task_blueprint}'."
                    )
                    logger.error("[ExecutionService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    raise ConfigurationError(msg)

                try:
                    pb_obj = PromptBlock.model_validate(pb_dict)
                except Exception as e:
                    msg = f"Invalid PromptBlock format for '{pb_id}': {str(e)}"
                    logger.error("[ExecutionService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    ) from e

                dt = pb_obj.type

                # Define component defaults based on Strict Block Types
                comp_type = ComponentType.HIDDEN
                if dt in ["float", "int", "string"] and pb_obj.scales:
                    # Only numeric or scaled blocks map to sliders/gauges
                    comp_type = ComponentType.SLIDER
                elif dt in ["float", "int"]:
                    comp_type = ComponentType.SLIDER
                elif dt == "panel":
                    comp_type = ComponentType.DROPDOWN

                max_val = None
                if pb_obj.scales:
                    try:
                        scores = [float(s.score) for s in pb_obj.scales if hasattr(s, "score") and s.score is not None]
                        if scores:
                            max_val = float(max(scores))
                    except (ValueError, TypeError) as e:
                        msg = f"Fail-Fast SDUI Generator: Corrupted scale scores in PromptBlock '{pb_id}'."
                        logger.error("[ExecutionService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                        raise ConfigurationError(msg) from e

                if comp_type == ComponentType.SLIDER and max_val is None:
                    msg = (
                        f"Fail-Fast SDUI Generator: PromptBlock '{pb_id}' uses a SDUI Slider "
                        "but has no valid scales defined to calculate max_val."
                    )
                    logger.error("[ExecutionService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                    raise ConfigurationError(msg)

                # Extract translation map for UI label
                label_obj = pb_obj.label.model_dump(exclude_unset=True) if pb_obj.label else {}

                val_rules = {}
                if max_val is not None:
                    val_rules["max"] = max_val

                # Lock the hint
                ui_hints[pb_id] = DataDictionaryField(
                    field_id=pb_id,
                    component_type=comp_type,
                    options=[{"label": label_obj}] if label_obj else None,
                    validation_rules=val_rules if val_rules else None,
                )

        # Fail-Fast: Resolve and Validate Output Profile immediately at ingress
        resolved_profile_id = payload.profile_id or workflow.default_profile_id
        if not workflow.output_profiles or resolved_profile_id not in workflow.output_profiles:
            msg = f"Profile ID '{resolved_profile_id}' not found in workflow '{workflow.id}'."
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        execution_id = f"exe_{uuid4().hex}"
        initial_record = create_execution_record(
            execution_id=execution_id,
            workflow_id=workflow.id,
            raw_inputs=WorkflowInputs.model_validate(payload.raw_inputs.model_dump(exclude_unset=True)),
            frozen_context=FrozenContext(ui_hints_snapshot=ui_hints),
            source_identity_manifest=source_identity_manifest,
            output_profile_id=resolved_profile_id,
            step_states=step_states,
            metadata={
                "target_locale": target_locale,
                "profile_id": resolved_profile_id,
                "matrix_sampling_strategy": payload.matrix_sampling_strategy,
                "workflow_version": workflow.version,
            },
            created_by=initiator.id,
            organization_id=getattr(initiator, "organization_id", None),
        )

        await self.exec_repo.create_execution(initial_record.model_dump(mode="json"))

        # Fire Async Process into durable Redis Queue
        await arq_pool.enqueue_job(
            "execute_workflow_job",
            workflow_id=workflow.id,
            inputs=payload.raw_inputs.model_dump(mode="json"),
            execution_id=execution_id,
            organization_id=getattr(initiator, "organization_id", None),
            user_id=initiator.id,
        )

        return initial_record

    async def check_resumability(self, record: ExecutionRecord) -> bool:
        """Evaluates whether an execution record can be resumed based on strict mathematical and FinOps boundaries.

        Rules for is_resumable = True:
        1. Execution status must be FAILED.
        2. Execution trace must contain at least one successful 'output' event (checkpoint after initial ingestion).
        3. The active DAG workflow blueprint must exist, its step IDs must perfectly match step_states,
           and workflow version must not have drifted.
        4. The tenant organization must have sufficient FinOps quota.
        """
        # Rule 1: Status check (resumable only from FAILED state)
        if record.status != ExecutionStatus.FAILED:
            return False

        # Rule 2: Removed Duck-Typing check. Executions that crash before their first 'output' checkpoint MUST be resumable.
        # This guarantees that early failures (e.g., Pydantic validation on the first LLM call) can be retired via the Event Sourced history.

        # Rule 3: Workflow Blueprint & Seed structural parity check
        workflow_dict = await self.workflow_repo.get_workflow_by_id(record.workflow_id)
        if not workflow_dict:
            return False

        # Fail-Fast: validation error during hydration will crash audibly (obeying the Zero-Compromise Pledge)
        workflow = Workflow.model_validate(workflow_dict)

        # Structural validation: Step set parity (detect if DAG was restructured mid-flight)
        workflow_step_ids = {step.id for step in workflow.steps}
        # V2 Fix: Filter out virtual system steps (sys_render_*) that are dynamically injected for PDF rendering.
        exec_step_ids = {k for k in record.step_states.keys() if not k.startswith("sys_render_")}
        if workflow_step_ids != exec_step_ids:
            return False

        # Version validation: Detect seed blueprint drift
        orig_version = record.metadata.get("workflow_version")
        if orig_version is not None and workflow.version != orig_version:
            return False

        # Rule 4: FinOps Quota protection
        org_id = record.organization_id
        if org_id:
            # Let quota check exceptions propagate naturally to prevent Silent Failures
            is_quota_safe = await self.usage_service.check_quota(org_id)
            if not is_quota_safe:
                return False

        return True

    async def resume_execution(self, initiator: TokenData, execution_id: str, arq_pool: ArqRedis) -> ExecutionRecord:
        """Securely resume an existing FAILED execution."""
        # 1. Authorize via get (Fail-Fast ResourceNotFound / PermissionDenied)
        record = await self.get_execution(initiator, execution_id)

        # 2. Strict API Resumption Firewall (Zero-Math Resumption check)
        is_resumable = await self.check_resumability(record)
        if not is_resumable:
            msg = (
                f"Execution {execution_id} cannot be resumed due to unresumable state, "
                "missing checkpoint history, workflow blueprint drift, or insufficient quota."
            )
            logger.error("[ExecutionService] %s: %s", ErrorCodes.UNRESUMABLE_STATE_ERROR.name, msg)
            raise AppException(
                message=msg, status_code=400, details={"error_code": ErrorCodes.UNRESUMABLE_STATE_ERROR.value}
            )

        # Circuit Breaker: Denial of Wallet Protection
        org_id = getattr(initiator, "organization_id", None)
        if org_id:
            is_quota_safe = await self.usage_service.check_quota(org_id)
            if not is_quota_safe:
                msg = f"Organization '{org_id}' has exceeded its execution quota. Resumption blocked."
                logger.warning("[ExecutionService] Circuit Breaker Tripped: %s", msg)
                raise AppException(
                    message=msg,
                    status_code=402,
                    details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value},
                )

        record = record.model_copy(update={"status": ExecutionStatus.RUNNING})
        await self.exec_repo.update_execution(execution_id, {"status": "running"})

        # 2. Fire Async Process into durable Redis Queue using original raw inputs
        await arq_pool.enqueue_job(
            "execute_workflow_job",
            workflow_id=record.workflow_id,
            inputs=record.raw_inputs.model_dump(mode="json"),
            execution_id=execution_id,
            organization_id=getattr(initiator, "organization_id", None),
            user_id=initiator.id,
        )

        return record

    async def get_frozen_context_bytes(self, initiator: TokenData, execution_id: str) -> tuple[bytes, str]:
        execution = await self.get_execution(initiator=initiator, execution_id=execution_id)
        if execution.frozen_context_storage_path:
            storage = get_storage_driver()
            try:
                raw_bytes = await storage.read(execution.frozen_context_storage_path)
                parsed_context = FrozenContext.model_validate_json(raw_bytes)
                pretty_bytes = parsed_context.model_dump_json(indent=2).encode("utf-8")
                return pretty_bytes, f"frozen_context_{execution_id}.json"
            except Exception as strg_err:
                logger.error(
                    "[ExecutionService] Failed to fetch frozen context from storage",
                    exc_info=True,
                    extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "execution_id": execution_id},
                )
                raise AppException(
                    message="Forensic context file not found in storage",
                    status_code=404,
                    details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
                ) from strg_err
        frozen_json = execution.frozen_context.model_dump_json(indent=2)
        return frozen_json.encode("utf-8"), f"frozen_context_{execution_id}.json"

    async def get_execution_export_bytes(self, initiator: TokenData, execution_id: str) -> tuple[bytes, str]:
        """Generates an Excel export for the execution including Summary and Raw Data tabs.

        Args:
            initiator: The authenticated user making the request.
            execution_id: The unique identifier of the execution.

        Returns:
            A tuple of the Excel file bytes and the suggested filename.

        Raises:
            AppException: If parsing fails or storage access fails.
        """
        import io
        import json

        import pandas as pd

        execution = await self.get_execution(initiator=initiator, execution_id=execution_id)
        frozen_bytes, _ = await self.get_frozen_context_bytes(initiator, execution_id)

        trace_data: list[Any] = []
        if execution.execution_trace_storage_path:
            storage = get_storage_driver()
            try:
                raw_trace = await storage.read(execution.execution_trace_storage_path)
                trace_data = json.loads(raw_trace.decode("utf-8"))
            except Exception as e:
                logger.error("[ExecutionService] Failed to load trace from storage", exc_info=True)
                raise AppException(
                    message="Failed to load execution trace for export",
                    status_code=500,
                    details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                ) from e
        else:
            trace_data = [t.model_dump(mode="json") for t in execution.execution_trace]

        def find_evals(obj: Any) -> list[dict[str, Any]]:
            found: list[dict[str, Any]] = []
            if isinstance(obj, dict):
                if "atom_id" in obj and ("status" in obj or "decision" in obj):
                    found.append(obj)
                for v in obj.values():
                    found.extend(find_evals(v))
            elif isinstance(obj, list):
                for item in obj:
                    found.extend(find_evals(item))
            return found

        components = await self.comp_repo.get_all_components("prompt_block")
        blocks_by_id = {}
        for b in components:
            try:
                b_obj = PromptBlock.model_validate(b)
                blocks_by_id[b_obj.id] = b_obj
            except Exception:
                pass

        atom_to_matrix_title = {}
        atom_to_claim_label = {}
        for step_state in execution.step_states.values():
            for s_atom in step_state.scorecard_atoms.values():
                atom_to_matrix_title[s_atom.atom_id] = step_state.label
                atom_to_claim_label[s_atom.atom_id] = s_atom.claim_label

        all_evals = find_evals(trace_data)
        rows: list[dict[str, Any]] = []
        for ev in all_evals:
            status_val = ev.get("status")
            if status_val is None:
                status_val = ev.get("decision")
            num_status = 1 if status_val == "PASS" else 0 if status_val == "CONTESTED" else None
            reasoning = ev.get("reasoning_steps", "")
            word_count = len(str(reasoning).split()) if reasoning else 0
            atom_id = ev.get("atom_id")
            matrix_title = ""
            claim_rule = ""
            claim_translation = ""

            # V2 Protocol Data Fetching
            if atom_id and not claim_translation:
                if atom_id in atom_to_claim_label:
                    claim_translation = atom_to_claim_label[atom_id]
                    matrix_title = atom_to_matrix_title.get(atom_id, "")
                elif atom_id in blocks_by_id:
                    pb = blocks_by_id[atom_id]
                    claim_translation = pb.label.translations.get(
                        "fi", pb.label.translations.get(pb.label.default_locale, "Unknown")
                    )
                    matrix_title = pb.category_id

                if atom_id in blocks_by_id:
                    claim_rule = blocks_by_id[atom_id].ai_description or ""
            quotes = ev.get("exact_quotes", [])
            if isinstance(quotes, list):
                quotes_str = "; ".join([q.get("text", str(q)) if isinstance(q, dict) else str(q) for q in quotes])
            else:
                quotes_str = str(quotes)
            sources = ev.get("used_source_aliases", [])
            sources_str = ", ".join(sources) if isinstance(sources, list) else str(sources)
            rows.append(
                {
                    "Matriisi": matrix_title,
                    "Kriteerin Nimi (UI)": claim_translation,
                    "Tekoälyn Sääntö": claim_rule,
                    "Sisäistetty Sääntö": ev.get("rule_internalization", ""),
                    "Tulos (Status)": num_status,
                    "Varmuusarvio": ev.get("confidence"),
                    "Perustelun Pituus": word_count,
                    "Löydetyt Lainaukset": quotes_str,
                    "Käytetyt Lähteet": sources_str,
                    "Tekoälyn Perustelu": reasoning,
                    "Falsifiointi": ev.get("falsification_argument", ""),
                }
            )

        df_raw = pd.DataFrame(rows)
        summary_rows: list[dict[str, Any]] = []
        for event in trace_data:
            content = event.get("content", {})
            if isinstance(content, dict) and "scoring_results" in content:
                for matrix_score in content.get("scoring_results", []):
                    m_id = matrix_score.get("matrix_id")
                    m_title = matrix_score.get("matrix_title", m_id)
                    score = matrix_score.get("score")
                    max_score = matrix_score.get("max_score")
                    summary_rows.append({"Matriisi": m_title, "Arvosana (Grade)": score, "Maksimipisteet": max_score})

        df_summary = pd.DataFrame(summary_rows)
        output = io.BytesIO()
        try:
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                if not df_summary.empty:
                    df_summary.to_excel(writer, sheet_name="Yhteenveto", index=False)
                else:
                    pd.DataFrame([{"Huomio": "Ei pisteytystuloksia tässä ajossa"}]).to_excel(
                        writer, sheet_name="Yhteenveto", index=False
                    )
                if not df_raw.empty:
                    df_raw.to_excel(writer, sheet_name="Raakadata", index=False)
                else:
                    pd.DataFrame([{"Huomio": "Ei atomeja löytynyt"}]).to_excel(
                        writer, sheet_name="Raakadata", index=False
                    )
        except Exception as e:
            logger.error("[ExecutionService] Excel writing failed", exc_info=True)
            raise AppException(
                message="Failed to generate Excel export",
                status_code=500,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            ) from e

        output.seek(0)
        return output.getvalue(), f"execution_export_{execution_id}.xlsx"

    async def clear_profile_synthesis(self, initiator: TokenData, execution_id: str, profile_id: str) -> None:
        """Removes the synthesized data for a specific profile to force re-render via LLM Hook."""
        execution = await self.get_execution(initiator=initiator, execution_id=execution_id)

        if execution.profile_syntheses and profile_id in execution.profile_syntheses:
            new_syntheses = dict(execution.profile_syntheses)
            del new_syntheses[profile_id]
            execution = execution.model_copy(update={"profile_syntheses": new_syntheses})

        workflow_data = await self.workflow_repo.get_workflow_by_id(execution.workflow_id)
        if not workflow_data:
            raise ResourceNotFoundError(resource_type="workflow", resource_id=execution.workflow_id)

        workflow_obj = Workflow.model_validate(workflow_data)
        default_pid = workflow_obj.default_profile_id

        update_payload: dict[str, Any] = {"profile_syntheses": execution.profile_syntheses}

        if profile_id == default_pid and execution.pdf_report_path:
            try:
                storage = get_storage_driver()
                await storage.delete(execution.pdf_report_path)
            except AppException as e:
                if e.status_code == 404:
                    logger.warning("[ExecutionService] Old PDF blob %s not found, ignoring.", execution.pdf_report_path)
                elif e.status_code == 409:
                    raise e
                else:
                    msg = "Failed to delete old PDF blob"
                    logger.error("[ExecutionService] %s", msg, exc_info=True)
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                    ) from e
            except Exception as e:
                msg = "Failed to delete old PDF blob"
                logger.error("[ExecutionService] %s", msg, exc_info=True)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                ) from e
            update_payload["pdf_report_path"] = None

        # Always update timestamp to invalidate any cached Arq background task locks
        update_payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        await self.exec_repo.update_execution(execution_id, update_payload)

        logger.info(
            "[ExecutionService] Cleared profile synthesis",
            extra={"execution_id": execution_id, "profile_id": profile_id},
        )

    async def override_atom(
        self,
        initiator: TokenData,
        execution_id: str,
        atom_id: str,
        payload: HumanOverrideRequest,
    ) -> None:
        """Apply a human override to a specific ScorecardAtomDTO."""
        record = await self.get_execution(initiator, execution_id)

        # SSOT MANDATE: Tenant Isolation Check
        org_id = getattr(initiator, "organization_id", None)
        if initiator.role != "ROOT" and record.organization_id != org_id and record.created_by != initiator.id:
            msg = "You do not have permission to modify this execution."
            raise PermissionDeniedError(msg)

        found_step_id = None
        for step_id, state in record.step_states.items():
            if atom_id in state.scorecard_atoms:
                found_step_id = step_id
                break

        if not found_step_id:
            raise AppException(f"Atom '{atom_id}' not found in any step_states", status_code=404)

        from datetime import datetime, timezone

        from backend_v2.models.v2_core import HumanOverrideDTO

        override_dto = HumanOverrideDTO(
            new_status=payload.new_status,
            reason=payload.reason,
            evidence_quotes=payload.evidence_quotes,
            overridden_by=initiator.id,
            overridden_at=datetime.now(timezone.utc),
        )

        # Compliantly update the scorecard_atoms and step_states of frozen models
        updated_atoms = dict(record.step_states[found_step_id].scorecard_atoms)
        updated_atoms[atom_id] = updated_atoms[atom_id].model_copy(update={"human_override": override_dto})

        new_step_states = dict(record.step_states)
        new_step_states[found_step_id] = new_step_states[found_step_id].model_copy(
            update={"scorecard_atoms": updated_atoms}
        )

        record = record.model_copy(update={"step_states": new_step_states})

        for _k, v in record.context_variables.items():
            if isinstance(v, dict) and "evaluated_atoms" in v:
                if atom_id in v["evaluated_atoms"]:
                    v["evaluated_atoms"][atom_id] = payload.new_status
                    if "raw_atoms" in v and isinstance(v["raw_atoms"], list):
                        for ra in v["raw_atoms"]:
                            if ra.get("tda_id") == atom_id or ra.get("atom_id") == atom_id:
                                ra["human_override"] = payload.new_status

        from typing import cast

        from backend_v2.core.hook_registry import HookDependencies
        from backend_v2.hooks.scoring import recalculate

        deps = HookDependencies(
            exec_repo=self.exec_repo,
            workflow_repo=self.workflow_repo,
            comp_repo=self.comp_repo,
            identity_repo=self.identity_repo,
            audit_repo=cast(Any, None),
            system_repo=self.system_repo,
        )
        await recalculate(record.context_variables, record.active_profile_id, deps)

        update_payload = {
            "step_states": {k: v.model_dump(mode="json") for k, v in record.step_states.items()},
            "context_variables": record.context_variables,
        }
        await self.exec_repo.update_execution(execution_id, update_payload)

        from backend_v2.models.state import TraceEvent

        event = TraceEvent(
            step_name="manual_override",
            event_type="evidence_override",
            content={"atom_id": atom_id, "override": override_dto.model_dump(mode="json")},
        )
        await self.exec_repo.append_trace_event(execution_id, event.model_dump(mode="json"))

    async def reject_evidence_quote(self, initiator: TokenData, execution_id: str, evq_id: str, reason: str) -> None:
        """Reject an evidence quote and append the event to the execution trace."""
        record = await self.get_execution(initiator, execution_id)

        # SSOT MANDATE: Tenant Isolation Check
        org_id = getattr(initiator, "organization_id", None)
        if initiator.role != "ROOT" and record.organization_id != org_id and record.created_by != initiator.id:
            msg = "You do not have permission to modify this execution."
            raise PermissionDeniedError(msg)

        from backend_v2.models.state import EvidenceOverrideDTO, TraceEvent

        dto = EvidenceOverrideDTO(
            evq_id=evq_id,
            user_rejected=True,
            rejection_reason=reason,
            rejected_by=initiator.id,
            rejected_at=datetime.now(timezone.utc),
        )

        event = TraceEvent(
            step_name="manual_override", event_type="evidence_override", content=dto.model_dump(mode="json")
        )

        await self.exec_repo.append_trace_event(execution_id, event.model_dump(mode="json"))

    async def render_execution(
        self,
        initiator: TokenData,
        execution_id: str,
        format_type: str,
        profile_id: str | None,
        accept_language: str | None,
        arq_pool: ArqRedis,
        custom_preface_md: str | None = None,
        local_time_str: str | None = None,
    ) -> tuple[bytes | list[Any] | dict[str, Any] | Any, str, str | None]:
        execution = await self.get_execution(initiator=initiator, execution_id=execution_id)

        if execution.status != ExecutionStatus.COMPLETED:
            msg = f"Execution is not in COMPLETED state. Current status: {execution.status.value}"
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        fmt = format_type.lower()

        if fmt == "flat":
            flat_data = FlatFileService.flatten_results(execution)
            return flat_data, "application/json", None

        workflow_data = await self.workflow_repo.get_workflow_by_id(execution.workflow_id)
        if not workflow_data:
            msg = "Workflow not found"
            logger.error(
                "[ExecutionService] Workflow not found", extra={"error_code": ErrorCodes.VALIDATION_FAILED.value}
            )
            raise AppException(message=msg, status_code=500, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        workflow_obj = Workflow.model_validate(workflow_data)

        default_pid = workflow_obj.default_profile_id

        resolved_pid = profile_id
        # Strict parsing: Do not map "default" to an undefined legacy slug if missing.
        if not resolved_pid or resolved_pid == "default":
            resolved_pid = default_pid

        # NEW ON-DEMAND RENDERING LOGIC (Epic 14 M4)
        if resolved_pid not in execution.profile_syntheses:
            # Epic 14: Use deterministic job ID to prevent infinite enqueues while UI is polling

            # Incorporate updated_at to ensure regenerating (which updates DB) creates a fresh valid job lock
            updated_ts = "0"
            if execution.updated_at:
                updated_ts = (
                    str(execution.updated_at).replace(":", "").replace("-", "").replace(".", "").replace(" ", "_")
                )

            job_id = f"render_{execution_id}_{resolved_pid}_{accept_language or 'default'}_{updated_ts}"

            await arq_pool.enqueue_job(
                "render_profile_job",
                _job_id=job_id,
                execution_id=execution_id,
                profile_id=resolved_pid,
                accept_language=accept_language,
            )

            v_step_id = f"sys_render_{resolved_pid}"
            if v_step_id in execution.step_states:
                active_message = execution.step_states[v_step_id].label
            else:
                active_message = "Valmistellaan tulostusta..."

            from backend_v2.models.v2_core import JobAcceptedDTO

            return (
                JobAcceptedDTO(status="pending", message=active_message, execution_id=execution_id),
                "application/json",
                None,
            )

        if fmt == "json":
            transformer = BlueprintTransformer(
                self.exec_repo, self.workflow_repo, self.comp_repo, self.identity_repo, self.system_repo
            )
            dto = await transformer.build_report_dto(
                execution_id, resolved_pid, accept_language, custom_preface_md, local_time_str
            )

            return dto.model_dump(mode="json"), "application/json", None

        elif fmt == "html":
            if not accept_language:
                if "target_locale" not in execution.metadata:
                    msg = "Strict Fail-Fast Enforced: 'target_locale' missing from execution metadata."
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )
                accept_language = str(execution.metadata["target_locale"])

            transformer = BlueprintTransformer(
                self.exec_repo, self.workflow_repo, self.comp_repo, self.identity_repo, self.system_repo
            )
            dto = await transformer.build_report_dto(
                execution_id, resolved_pid, accept_language, custom_preface_md, local_time_str
            )

            pdf_service = PdfReportService(self.exec_repo, self.workflow_repo)
            html_string = await pdf_service.generate_execution_html(execution_id, report_dto=dto)

            return html_string.encode("utf-8"), "text/html", f"execution_{execution_id}.html"

        elif fmt == "pdf":
            if (
                resolved_pid == default_pid
                and execution.pdf_report_path
                and not custom_preface_md
                and not local_time_str
            ):
                storage = get_storage_driver()
                try:
                    pdf_bytes = await storage.read(execution.pdf_report_path)
                    return pdf_bytes, "application/pdf", f"execution_{execution_id}.pdf"
                except Exception as strg_err:
                    msg = "Failed to fetch pre-generated PDF from storage"
                    logger.error(
                        "[ExecutionService] %s",
                        msg,
                        exc_info=True,
                        extra={"error": str(strg_err), "execution_id": execution_id},
                    )
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                    ) from strg_err

            if not accept_language:
                if "target_locale" not in execution.metadata:
                    msg = "Strict Fail-Fast Enforced: 'target_locale' missing from execution metadata."
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    )
                accept_language = str(execution.metadata["target_locale"])

            transformer = BlueprintTransformer(
                self.exec_repo, self.workflow_repo, self.comp_repo, self.identity_repo, self.system_repo
            )
            dto = await transformer.build_report_dto(
                execution_id, resolved_pid, accept_language, custom_preface_md, local_time_str
            )

            pdf_service = PdfReportService(self.exec_repo, self.workflow_repo)
            pdf_bytes = await pdf_service.generate_execution_pdf(execution_id, report_dto=dto)

            if resolved_pid == default_pid:
                try:
                    storage = get_storage_driver()
                    output_path_rel = f"executions/{execution_id}/report.pdf"
                    saved_path = await storage.save(output_path_rel, pdf_bytes)
                    if not execution.pdf_report_path or execution.pdf_report_path != saved_path:
                        await self.exec_repo.update_execution(execution_id, {"pdf_report_path": saved_path})
                    logger.info(
                        "[ExecutionService] Generated missing PDF",
                        extra={"execution_id": execution_id, "saved_path": saved_path},
                    )
                except Exception as heal_err:
                    msg = "Failed to save generated PDF to storage"
                    logger.error(
                        "[ExecutionService] %s",
                        msg,
                        exc_info=True,
                        extra={"execution_id": execution_id, "error": str(heal_err)},
                    )
                    raise AppException(
                        message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                    ) from heal_err

            return pdf_bytes, "application/pdf", f"execution_{execution_id}.pdf"

        else:
            msg = f"Unsupported format: {format_type}"
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

    async def enqueue_pdf_generation(
        self,
        initiator: TokenData,
        execution_id: str,
        accept_language: str | None,
        profile_id: str,
        arq_pool: ArqRedis,
        custom_preface_md: str | None = None,
        local_time_str: str | None = None,
    ) -> None:
        """Securely enqueue a PDF generation job and inject a Virtual Step into the trace."""
        # 1. Authorize connection first via Security Dependency
        await self.get_execution(initiator=initiator, execution_id=execution_id)

        # 2. Inject Virtual Step
        v_step_id = f"sys_render_{profile_id}"
        v_step = ExecutionStepState(id=v_step_id, label=v_step_id, status="running")

        exec_record_local = await self.exec_repo.get_execution(execution_id, hydrate=False)
        if exec_record_local:
            exec_record_local.step_states[v_step_id] = v_step
            await self.exec_repo.update_execution(
                execution_id,
                {
                    "status": "running",
                    "step_states": {k: v.model_dump() for k, v in exec_record_local.step_states.items()},
                },
            )

        # 3. Queue the background task into Redis
        await arq_pool.enqueue_job(
            "generate_pdf_job",
            execution_id=execution_id,
            accept_language=accept_language,
            profile_id=profile_id,
            custom_preface_md=custom_preface_md,
            local_time_str=local_time_str,
        )

    async def get_workflow_ui_schema(self, workflow_id: str) -> dict[str, Any]:
        """Retrieve the expected inputs schema for frontend dynamic rendering.

        Enforces Fail-Fast if the workflow is missing or structurally invalid.

        Args:
            workflow_id: The opaque Stripe ID of the target workflow.

        Returns:
            The UI schema dictionary for dynamic form generation.

        Raises:
            ResourceNotFoundError: If the workflow does not exist.
        """
        workflow_record = await self.workflow_repo.get_workflow_by_id(workflow_id)
        if not workflow_record:
            raise ResourceNotFoundError(resource_type="workflow", resource_id=workflow_id)

        workflow = Workflow.model_validate(workflow_record)
        return dict(workflow.ui_schema)
