"""Execution Management Service."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from arq.connections import ArqRedis

from backend_v2.database.repository import AbstractWorkflowRepository
from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from backend_v2.hooks.translation_hook import translate_sdui_payload
from backend_v2.models.auth import SystemOrganizations, TokenData
from backend_v2.models.v2_core import (
    ComponentType,
    DataDictionaryField,
    ExecutionCreate,
    ExecutionRecord,
    ExecutionStatus,
    ExecutionStepState,
    FrozenContext,
    Step,
    Workflow,
)
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.flattener import FlatFileService
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.storage import get_storage_driver
from backend_v2.services.usage_service import UsageService

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
                executions = [e for e in executions if e.organization_id == org_id or e.created_by == initiator.id]

            return executions
        except Exception as e:
            msg = f"Failed to list executions: {str(e)}"
            logger.error("[ExecutionService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
            ) from e

    async def get_execution(self, initiator: TokenData, execution_id: str) -> ExecutionRecord:
        """Fetch single execution securely."""
        data = await self.repo.get_execution(execution_id)
        if not data:
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)

        # SSOT MANDATE: Tenant Isolation Check
        org_id = getattr(initiator, "organization_id", None)
        if initiator.role != "ROOT" and data.organization_id != org_id and data.created_by != initiator.id:
            msg = "You do not have permission to view this execution."
            raise PermissionDeniedError(msg)

        return data

    async def delete_execution(self, initiator: TokenData, execution_id: str) -> bool:
        """Securely delete an execution."""
        # 1. Raw fetch to bypass hydration (Fail-Fast ResourceNotFound / PermissionDenied).
        # This allows deleting corrupted executions where blob files are missing.
        repo_driver = getattr(self.repo, "driver", None)
        raw_data = await repo_driver.get("executions", execution_id) if repo_driver else None
        if not raw_data:
            raise ResourceNotFoundError(resource_type="execution", resource_id=execution_id)

        # SSOT MANDATE: Tenant Isolation Check
        org_id = getattr(initiator, "organization_id", None)
        if (
            initiator.role != "ROOT"
            and raw_data.get("organization_id") != org_id
            and raw_data.get("created_by") != initiator.id
        ):
            msg = "You do not have permission to delete this execution."
            raise PermissionDeniedError(msg)

        try:
            # Clean up offloaded blobs if they exist
            storage = get_storage_driver()
            for key in ["execution_trace_storage_path", "frozen_context_storage_path", "pdf_report_path"]:
                if raw_data.get(key):
                    try:
                        await storage.delete(raw_data[key])
                    except Exception as e:
                        msg = f"Failed to clean up blob {raw_data[key]} during execution deletion."
                        logger.error(
                            "[ExecutionService] %s: %s",
                            ErrorCodes.INTERNAL_SERVER_ERROR.name,
                            msg,
                            exc_info=True,
                            extra={"execution_id": execution_id},
                        )
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                        ) from e

            return await self.repo.delete_execution(execution_id)
        except Exception as e:
            msg = f"Failed to delete execution {execution_id}: {str(e)}"
            logger.error("[ExecutionService] %s: %s", ErrorCodes.INTERNAL_SERVER_ERROR.name, msg, exc_info=True)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
            ) from e

    async def start_execution(
        self, initiator: TokenData, payload: ExecutionCreate, arq_pool: ArqRedis
    ) -> ExecutionRecord:
        """Initialize and trigger workflow securely."""
        workflow_dict = await self.repo.get_workflow_by_id(payload.workflow_id)
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
            usage_service = UsageService(self.repo)
            is_quota_safe = await usage_service.check_quota(org_id)
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
        missing_fields = []
        for expected in workflow.expected_inputs:
            if expected.required:
                val = raw_inputs_dict.get(expected.input_key)
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

        # V2 MANDATE: Dynamically generate SDUI hints synchronously before execution
        ui_hints: dict[str, DataDictionaryField] = {}
        step_states: dict[str, ExecutionStepState] = {}
        for step_rule in workflow.steps:
            # We fetch the step definition to find its core mapped matrices/blocks
            step_dict = await self.repo.get_step(step_rule.task_blueprint)
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

            prompt_blocks_refs = step_obj.prompt_blocks
            for pb_id in prompt_blocks_refs:
                pb_dict = await self.repo.get_prompt_block(pb_id)
                if not pb_dict:
                    # V2 strictly says Fail Fast to guarantee auditability:
                    msg = (
                        f"SDUI Engine Error: PromptBlock '{pb_id}' is missing "
                        f"but referenced in step '{step_rule.task_blueprint}'."
                    )
                    logger.error("[ExecutionService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
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

                max_val = None
                if pb_dict.get("scales"):
                    try:
                        scores = [float(s["score"]) for s in pb_dict["scales"] if "score" in s]
                        if scores:
                            max_val = float(max(scores))
                    except (ValueError, TypeError, KeyError) as e:
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
                label_obj = pb_dict.get("label", {})

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
        initial_record = ExecutionRecord(
            id=execution_id,
            workflow_id=workflow.id,
            status=ExecutionStatus.PENDING,
            raw_inputs=payload.raw_inputs,
            output_profile_id=resolved_profile_id,
            frozen_context=FrozenContext(ui_hints_snapshot=ui_hints),
            step_states=step_states,
            metadata={
                "target_locale": target_locale,
                "profile_id": resolved_profile_id,
                "matrix_sampling_strategy": payload.matrix_sampling_strategy,
            },
            created_by=initiator.id,
            organization_id=getattr(initiator, "organization_id", None),
        )

        await self.repo.create_execution(initial_record.model_dump(mode="json"))

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

    async def resume_execution(self, initiator: TokenData, execution_id: str, arq_pool: ArqRedis) -> ExecutionRecord:
        """Securely resume an existing FAILED execution."""
        # 1. Authorize via get (Fail-Fast ResourceNotFound / PermissionDenied)
        record = await self.get_execution(initiator, execution_id)

        if record.status not in [ExecutionStatus.FAILED, ExecutionStatus.PENDING]:
            msg = (
                f"Cannot resume execution in state {record.status.value}. "
                "Only FAILED or PENDING executions can be resumed."
            )
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        # Circuit Breaker: Denial of Wallet Protection
        org_id = getattr(initiator, "organization_id", None)
        if org_id:
            usage_service = UsageService(self.repo)
            is_quota_safe = await usage_service.check_quota(org_id)
            if not is_quota_safe:
                msg = f"Organization '{org_id}' has exceeded its execution quota. Resumption blocked."
                logger.warning("[ExecutionService] Circuit Breaker Tripped: %s", msg)
                raise AppException(
                    message=msg,
                    status_code=402,
                    details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value},
                )

        record.status = ExecutionStatus.RUNNING
        await self.repo.update_execution(execution_id, {"status": "running"})

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

    async def clear_profile_synthesis(self, initiator: TokenData, execution_id: str, profile_id: str) -> None:
        """Removes the synthesized data for a specific profile to force re-render via LLM Hook."""
        execution = await self.get_execution(initiator=initiator, execution_id=execution_id)

        if profile_id in execution.profile_syntheses:
            del execution.profile_syntheses[profile_id]

        workflow_data = await self.repo.get_workflow_by_id(execution.workflow_id)
        if not workflow_data:
            raise ResourceNotFoundError(resource_type="workflow", resource_id=execution.workflow_id)

        workflow_obj = Workflow.model_validate(workflow_data)
        default_pid = workflow_obj.default_profile_id

        update_payload: dict[str, Any] = {"profile_syntheses": execution.profile_syntheses}

        if profile_id == default_pid and execution.pdf_report_path:
            try:
                storage = get_storage_driver()
                await storage.delete(execution.pdf_report_path)
            except Exception as e:
                msg = "Failed to delete old PDF blob"
                logger.error("[ExecutionService] %s", msg, exc_info=True)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                ) from e
            update_payload["pdf_report_path"] = None

        # Always update timestamp to invalidate any cached Arq background task locks
        update_payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        await self.repo.update_execution(execution_id, update_payload)

        logger.info(
            "[ExecutionService] Cleared profile synthesis",
            extra={"execution_id": execution_id, "profile_id": profile_id},
        )

    async def render_execution(
        self,
        initiator: TokenData,
        execution_id: str,
        format_type: str,
        profile_id: str | None,
        accept_language: str | None,
        arq_pool: ArqRedis,
    ) -> tuple[bytes | list[Any] | dict[str, Any], str, str | None]:
        execution = await self.get_execution(initiator=initiator, execution_id=execution_id)

        if execution.status != ExecutionStatus.COMPLETED:
            msg = f"Execution is not in COMPLETED state. Current status: {execution.status.value}"
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})

        fmt = format_type.lower()

        if fmt == "flat":
            flat_data = FlatFileService.flatten_results(execution)
            return flat_data, "application/json", None

        workflow_data = await self.repo.get_workflow_by_id(execution.workflow_id)
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
            return {"status": "pending", "message": "Synthesis generating"}, "application/json", None

        if fmt == "json":
            transformer = BlueprintTransformer(self.repo)
            dto = await transformer.build_report_dto(execution_id, profile_id, accept_language)

            # API Pipeline Splicing (Epic 35)
            # Apply immutable translation hook before dumping to dictionary
            if accept_language and accept_language.lower() != "en":
                dto = await translate_sdui_payload(dto, accept_language, self.repo)

            return dto.model_dump(mode="json"), "application/json", None

        elif fmt == "pdf":
            if resolved_pid == default_pid and execution.pdf_report_path:
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

            if not accept_language and execution.metadata:
                accept_language = execution.metadata.get("target_locale")

            transformer = BlueprintTransformer(self.repo)
            dto = await transformer.build_report_dto(execution_id, resolved_pid, accept_language)

            pdf_service = PdfReportService(self.repo)
            pdf_bytes = await pdf_service.generate_execution_pdf(execution_id, report_dto=dto)

            if resolved_pid == default_pid:
                try:
                    storage = get_storage_driver()
                    output_path_rel = f"executions/{execution_id}/report.pdf"
                    saved_path = await storage.save(output_path_rel, pdf_bytes)
                    if not execution.pdf_report_path or execution.pdf_report_path != saved_path:
                        await self.repo.update_execution(execution_id, {"pdf_report_path": saved_path})
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
