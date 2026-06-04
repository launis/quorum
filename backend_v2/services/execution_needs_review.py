"""Execution Management Service."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from arq.connections import ArqRedis

from backend_v2.database.interfaces import (
    IComponentRepository,
    IExecutionRepository,
    IIdentityRepository,
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
from backend_v2.models.v2_core import (
    ComponentType,
    DataDictionaryField,
    ExecutionCreate,
    ExecutionRecord,
    ExecutionStatus,
    ExecutionStepState,
    FrozenContext,
    PromptBlock,
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

    def __init__(
        self,
        exec_repo: IExecutionRepository,
        workflow_repo: IWorkflowRepository,
        comp_repo: IComponentRepository,
        identity_repo: IIdentityRepository,
        usage_service: UsageService,
        executor: DAGExecutor,
    ):
        self.exec_repo = exec_repo
        self.workflow_repo = workflow_repo
        self.comp_repo = comp_repo
        self.identity_repo = identity_repo
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
        self, initiator: TokenData, payload: ExecutionCreate, arq_pool: ArqRedis
    ) -> ExecutionRecord:
        """Initialize and trigger workflow securely."""
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
        try:
            dynamic_inputs = raw_inputs_dict["dynamic_inputs"]
        except KeyError:
            dynamic_inputs = {}

        missing_fields = []
        for expected in workflow.expected_inputs:
            if expected.required:
                try:
                    val = raw_inputs_dict[expected.input_key]
                except KeyError:
                    try:
                        val = dynamic_inputs[expected.input_key]
                    except KeyError:
                        val = None

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
            step_dict = await self.workflow_repo.get_step_by_id(step_rule.task_blueprint)
            if not step_dict:
                msg = f"Missing task blueprint {step_rule.task_blueprint} for DAG."
                logger.error("[ExecutionService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                raise ConfigurationError(msg)

            try:
                step_obj = Step.model_validate(step_dict)
            except Exception as e:
                msg = f"Invalid step format in blueprint {step_rule.task_blueprint}: {str(e)}"
                logger.error("[ExecutionService] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                ) from e

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

                comp_type = ComponentType.HIDDEN
                if dt in ["float", "int", "string"] and pb_obj.scales:
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

                label_obj = pb_obj.label.model_dump(exclude_unset=True) if pb_obj.label else {}

                val_rules = {}
                if max_val is not None:
                    val_rules["max"] = max_val

                ui_hints[pb_id] = DataDictionaryField(
                    field_id=pb_id,
                    component_type=comp_type,
                    options=[{"label": label_obj}] if label_obj else None,
                    validation_rules=val_rules if val_rules else None,
                )

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
                "workflow_version": workflow.version,
            },
            created_by=initiator.id,
            organization_id=getattr(initiator, "organization_id", None),
        )

        await self.exec_repo.create_execution(initial_record.model_dump(mode="json"))

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
        """Evaluates whether an execution record can be resumed based on strict mathematical and FinOps boundaries."""
        if record.status != ExecutionStatus.FAILED:
            return False

        has_output_checkpoint = any(event.event_type == "output" for event in record.execution_trace)
        if not has_output_checkpoint:
            return False

        workflow_dict = await self.workflow_repo.get_workflow_by_id(record.workflow_id)
        if not workflow_dict:
            return False

        workflow = Workflow.model_validate(workflow_dict)

        workflow_step_ids = {step.id for step in workflow.steps}
        exec_step_ids = set(record.step_states.keys())
        if workflow_step_ids != exec_step_ids:
            return False

        try:
            orig_version = record.metadata["workflow_version"]
        except KeyError:
            orig_version = None

        if orig_version is not None and workflow.version != orig_version:
            return False

        org_id = record.organization_id
        if org_id:
            is_quota_safe = await self.usage_service.check_quota(org_id)
            if not is_quota_safe:
                return False

        return True

    async def resume_execution(self, initiator: TokenData, execution_id: str, arq_pool: ArqRedis) -> ExecutionRecord:
        """Securely resume an existing FAILED execution."""
        record = await self.get_execution(initiator=initiator, execution_id=execution_id)

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

        update_payload["updated_at"] = datetime.now(timezone.utc).isoformat()
        await self.exec_repo.update_execution(execution_id, update_payload)

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
        custom_preface_md: str | None = None,
        local_time_str: str | None = None,
    ) -> tuple[bytes | list[Any] | dict[str, Any], str, str | None]:
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
        if not resolved_pid or resolved_pid == "default":
            resolved_pid = default_pid

        if resolved_pid not in execution.profile_syntheses:
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

            return {"status": "pending", "message": active_message}, "application/json", None

        if fmt == "json":
            transformer = BlueprintTransformer(self.exec_repo, self.workflow_repo, self.comp_repo, self.identity_repo)
            dto = await transformer.build_report_dto(
                execution_id, resolved_pid, accept_language, custom_preface_md, local_time_str
            )

            return dto.model_dump(mode="json"), "application/json", None

        elif fmt == "html":
            if not accept_language:
                try:
                    accept_language = str(execution.metadata["target_locale"])
                except KeyError:
                    msg = "Strict Fail-Fast Enforced: 'target_locale' missing from execution metadata."
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from None

            transformer = BlueprintTransformer(self.exec_repo, self.workflow_repo, self.comp_repo, self.identity_repo)
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
                try:
                    accept_language = str(execution.metadata["target_locale"])
                except KeyError:
                    msg = "Strict Fail-Fast Enforced: 'target_locale' missing from execution metadata."
                    raise AppException(
                        message=msg,
                        status_code=500,
                        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                    ) from None

            transformer = BlueprintTransformer(self.exec_repo, self.workflow_repo, self.comp_repo, self.identity_repo)
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
        await self.get_execution(initiator=initiator, execution_id=execution_id)

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

        await arq_pool.enqueue_job(
            "generate_pdf_job",
            execution_id=execution_id,
            accept_language=accept_language,
            profile_id=profile_id,
            custom_preface_md=custom_preface_md,
            local_time_str=local_time_str,
        )
