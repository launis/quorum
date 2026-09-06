"""Arq Worker configuration and startup logic.

Modernized for GraphEngine and TaskRegistry (V2.9).
"""

import asyncio
import logging
import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any, cast

import logfire
from arq.connections import RedisSettings
from arq.typing import StartupShutdown, WorkerCoroutine
from arq.worker import Function
from pydantic import BaseModel, ConfigDict, TypeAdapter, ValidationError

import backend_v2.hooks  # noqa: F401
import backend_v2.utils.scoring.variance_engine as variance_engine
from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDependencies,
    HookState,
)
from backend_v2.core.registry import TaskRegistry
from backend_v2.database.factory import get_driver
from backend_v2.database.repository import UnifiedWorkflowRepository
from backend_v2.exceptions import AppException, ErrorCodes, WorkflowNotFoundError
from backend_v2.llm.client import LLMClient
from backend_v2.logging_config import configure_logfire, setup_logging
from backend_v2.models.domain.linguistics import LinguisticsResultDTO
from backend_v2.models.domain.prompt_blocks import (
    MatrixPromptBlock,
    PromptBlockAdapter,
)
from backend_v2.models.dtos.lightweight_matrix import LevelStatsDTO, LightweightMatrixOutput
from backend_v2.models.dtos.synthesis import (
    ExecutiveSummarySectionResult,
    LlmSduiBlock,
    MatrixExplanationContextDTO,
    MatrixExplanationContextList,
    MatrixExplanationsResult,
    MatrixSectionSynthesesResult,
    XaiHighlightItem,
    XaiHighlightsResult,
)
from backend_v2.models.dtos.trace import (
    ExecutionUpdateDTO,
    StepTraceMetadataDTO,
    TraceEventMetadataEnvelope,
)
from backend_v2.models.enums import ExecutionStatus, PresetView, StrictnessAnchor, TargetBlockType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.prompts import (
    ANTI_JARGON_MANDATE_BLOCK,
    EXECUTIVE_SUMMARY_SECTION_ID,
    ROW_EXPLANATION_SYSTEM_PROMPT,
    SECTION_SYNTHESIS_DIRECTIVE_BLOCK,
    STATIC_LINGUISTIC_PROTOCOL,
    SYNTHESIS_CITATION_RULES_HARVARD,
    SYNTHESIS_SDUI_MANDATES,
    SYNTHESIS_SECTION_RULES_PREFIX,
    SYNTHESIS_SYSTEM_PROMPT,
    SYNTHESIS_XAI_CURATION,
    VARIANCE_SYSTEM_PROMPT,
    build_linguistic_parameters,
)
from backend_v2.models.state import ErrorTraceEvent, StateProjector, TombstoneEvent, TraceEvent
from backend_v2.models.v2_core import (
    DataStarvationEvent,
    ExecutionRecord,
    ExecutionStep,
    ExecutionSummarySnapshot,
    ExtensionMetricsDTO,
    OutputProfile,
    RenderedSynthesisCache,
    Workflow,
    WorkflowInputs,
)
from backend_v2.models.view.sdui import AnySduiBlock, ParagraphBlock
from backend_v2.services.blueprint import BlueprintTransformer
from backend_v2.services.length_budget_enforcer import enforce_sentence_boundary_budget
from backend_v2.services.localization import set_language
from backend_v2.services.orchestrator.dag_executor import DAGExecutor
from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService
from backend_v2.services.orchestrator.synthesis_distiller import synthesis_distiller_hook
from backend_v2.services.pdf_generator import PdfReportService
from backend_v2.services.storage import get_storage_driver
from backend_v2.settings import get_settings
from backend_v2.utils.math_utils import normalize_score_to_100
from backend_v2.utils.scoring import get_scoring_engine

__all__ = [
    "VarianceExplanationResult",
    "WorkerSettings",
    "execute_workflow_job",
    "generate_pdf_job",
    "generate_pdf_task",
    "generate_profile_synthesis_and_pdf_task",
    "health_check",
    "render_profile_job",
    "shutdown",
    "startup",
]


class VarianceExplanationResult(BaseModel):
    """Result model for cognitive-mechanical variance explanation."""

    model_config = ConfigDict(strict=True, extra="forbid")

    row_explanation: str


# Initialize settings
settings = get_settings()
logger = logging.getLogger(__name__)

# Pre-register all hooks for background execution
# --- Worker Job Tasks ---


# The main orchestrator loop polling Redis will now pick this up and execute MatrixReducer


async def execute_workflow_job(
    ctx: Any,
    workflow_id: str,
    inputs: dict[str, Any],
    execution_id: str | None = None,
    organization_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Background job to execute a workflow using GraphEngine.

    Args:
        ctx: Arq worker context containing initialized services.
        workflow_id: ID of the workflow configuration to run.
        inputs: Raw input arguments for the workflow.
        execution_id: ID of the execution record to update.
        organization_id: Organization ID context.
        user_id: User ID context.

    Returns:
        The final workflow state.

    Raises:
        AppException: Inherited from execution logic.
    """
    msg = (
        f"[Job] Executing workflow: {workflow_id} "
        f"(Execution ID: {execution_id}, Org: {organization_id}, User: {user_id})"
    )
    logger.info(msg)

    # LOGFIRE INTEGRATION: Bind execution_id to this trace context
    # This groups all subsequent logs (Agent, LLM, DB) under this execution_id.
    with logfire.span("execute_workflow_job", tags={"execution_id": execution_id or "unknown"}):
        # Inject Organization ID into inputs (Blackboard State) if provided
        # This ensures that valid WorkflowState objects created from this dict will have organization_id populated.  # noqa: E501
        if organization_id and "organization_id" not in inputs:
            inputs["organization_id"] = organization_id

        # Inject User ID into inputs (Blackboard State) if provided
        if user_id and "user_id" not in inputs:
            inputs["user_id"] = user_id

        # Retrieve pre-initialized Engine
        engine = ctx["engine"]
        # Retrieve Repository (for loading definition)
        repository = ctx["repository"]

        # V2 Strict Context Execution Engine
        exec_id = execution_id or f"exe_{uuid.uuid4().hex}"

        try:
            # Load Definition
            # We must load the definition to pass it to the engine.
            workflow_dict = await repository.get_workflow(workflow_id)

            if not workflow_dict:
                raise WorkflowNotFoundError(workflow_id)

            # V2 MUST validate strictly before execution
            workflow_def = Workflow.model_validate(workflow_dict)

            start_time = datetime.now(UTC)

            inputs_obj = WorkflowInputs.model_validate(inputs)

            # Retrieve dynamic strictness level from DB (No Hardcoding)
            execution_data = await repository.get_execution(exec_id)
            if not execution_data:
                msg = f"Execution {exec_id} not found in DB before execution! Cannot resolve dynamic strictness."
                logger.error("[Job] %s", msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
                )

            # Enforce schema validation
            exec_record = ExecutionRecord.model_validate(execution_data, strict=False)

            # Dynamic Strictness Level resolution
            profile_id = exec_record.output_profile_id

            p_dict = await repository.get_output_profile_by_id(profile_id) if profile_id else None
            active_profile_dto = OutputProfile.model_validate(p_dict, strict=False) if p_dict else None

            strictness_level: int | None = None
            if active_profile_dto and active_profile_dto.strictness_level is not None:
                strictness_level = active_profile_dto.strictness_level
            elif workflow_def:
                strictness_level = workflow_def.default_strictness_level

            if strictness_level is None:
                msg = (
                    "Strict Fail-Fast Enforced: Missing mandatory "
                    f"strictness_level configuration for workflow '{workflow_def.id}'."
                )
                logger.error("[Worker] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )

            # SSOT Language Context Initialization for Background Worker
            if not exec_record.target_locale:
                msg = f"Strict Fail-Fast Enforced: Execution '{exec_record.id}' is missing mandatory 'target_locale'."
                logger.error("[Worker] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )
            set_language(exec_record.target_locale)

            redis = ctx.get("redis")
            updated_exec_record = await engine.execute_workflow(
                execution_id=exec_id,
                workflow=workflow_def,
                raw_inputs=inputs_obj,
                strictness_level=strictness_level,
                arq_pool=redis,
            )

            # Final Status Update (Completed)
            if exec_id:
                # Phase 2, Step 2.1: Parse execution_trace to extract final models_used, step_telemetry, and FinOps
                def _has_step_metadata(evt: ErrorTraceEvent | TombstoneEvent | TraceEvent) -> bool:
                    if not evt.content:
                        return False
                    try:
                        envelope = TraceEventMetadataEnvelope.model_validate(evt.content)
                        return envelope.step_metadata is not None
                    except ValidationError, ValueError:
                        return False

                trace_events = list(updated_exec_record.execution_trace)
                if (
                    not any(_has_step_metadata(e) for e in trace_events)
                    and updated_exec_record.execution_trace_storage_path
                ):
                    try:
                        storage_driver = get_storage_driver()
                        blob_data = await storage_driver.read(updated_exec_record.execution_trace_storage_path)
                        if blob_data:
                            trace_events = TypeAdapter(
                                list[ErrorTraceEvent | TombstoneEvent | TraceEvent]
                            ).validate_json(blob_data)
                    except (OSError, UnicodeDecodeError, ValidationError, ValueError, KeyError) as err:
                        logger.warning("[Worker] Failed to hydrate offloaded trace for telemetry: %s", err)

                models_used: dict[str, int] = (
                    updated_exec_record.models_used.copy() if updated_exec_record.models_used else {}
                )
                step_telemetry: dict[str, dict[str, Any]] = {}
                total_cost_usd = 0.0
                total_prompt_tokens = 0
                total_completion_tokens = 0
                total_cached_tokens = 0
                total_reasoning_tokens = 0
                is_degraded = False

                for event in trace_events:
                    if event.event_type in ("error", "dlq_routed"):
                        is_degraded = True
                    try:
                        step_meta = TraceEventMetadataEnvelope.model_validate(event.content).step_metadata
                        if step_meta is None:
                            continue
                        usage = step_meta.token_usage
                    except (ValidationError, ValueError) as err:
                        logger.debug("Skipping non-metadata trace event during telemetry aggregation: %s", err)
                        continue

                    model_strategy = step_meta.model_strategy
                    chunk_size = step_meta.chunk_size

                    if usage is not None:
                        total_prompt_tokens += usage.prompt_tokens
                        total_completion_tokens += usage.completion_tokens
                        total_cached_tokens += usage.cached_tokens
                        total_reasoning_tokens += usage.reasoning_tokens
                        total_cost_usd += usage.cost_usd
                        t_tokens = usage.total_tokens
                        c_cost = usage.cost_usd
                        p_tokens = usage.prompt_tokens
                        comp_tokens = usage.completion_tokens
                        cac_tokens = usage.cached_tokens
                        reas_tokens = usage.reasoning_tokens
                    else:
                        t_tokens = 0
                        c_cost = 0.0
                        p_tokens = 0
                        comp_tokens = 0
                        cac_tokens = 0
                        reas_tokens = 0

                    curr_model_tokens = models_used[model_strategy] if model_strategy in models_used else 0
                    models_used[model_strategy] = curr_model_tokens + t_tokens

                    step_id = event.step_name
                    if step_id not in step_telemetry:
                        step_telemetry[step_id] = {
                            "model_strategy": model_strategy,
                            "physical_model": step_meta.physical_model,
                            "system_fingerprint": step_meta.system_fingerprint,
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "cached_tokens": 0,
                            "reasoning_tokens": 0,
                            "cost_usd": 0.0,
                            "chunk_count": 0,
                        }
                    st_entry = step_telemetry[step_id]
                    if step_meta.physical_model and not st_entry["physical_model"]:
                        st_entry["physical_model"] = step_meta.physical_model
                    if step_meta.system_fingerprint and not st_entry["system_fingerprint"]:
                        st_entry["system_fingerprint"] = step_meta.system_fingerprint
                    st_entry["prompt_tokens"] += p_tokens
                    st_entry["completion_tokens"] += comp_tokens
                    st_entry["cached_tokens"] += cac_tokens
                    st_entry["reasoning_tokens"] += reas_tokens
                    st_entry["cost_usd"] += c_cost
                    st_entry["chunk_count"] += chunk_size

                # Build updated ExecutionStep list
                updated_steps: list[ExecutionStep] = []
                existing_steps = (
                    updated_exec_record.steps
                    if updated_exec_record.steps
                    else [
                        ExecutionStep(
                            id=k,
                            label=v.label,
                            status=v.status,
                            last_error=v.last_error,
                            message_code=v.message_code,
                            scorecard_atoms=v.scorecard_atoms,
                        )
                        for k, v in updated_exec_record.step_states.items()
                    ]
                )
                for st in existing_steps:
                    st_state = updated_exec_record.step_states.get(st.id)
                    actual_status = st_state.status if st_state else st.status
                    last_err = st_state.last_error if st_state else st.last_error
                    msg_code = st_state.message_code if st_state else st.message_code
                    scorecard = st_state.scorecard_atoms if st_state else st.scorecard_atoms

                    tel = step_telemetry.get(st.id)
                    if tel:
                        updated_st = st.model_copy(
                            update={
                                "status": actual_status,
                                "last_error": last_err,
                                "message_code": msg_code,
                                "scorecard_atoms": scorecard,
                                "model_strategy": tel["model_strategy"],
                                "physical_model": tel["physical_model"],
                                "system_fingerprint": tel["system_fingerprint"],
                                "prompt_tokens": tel["prompt_tokens"],
                                "completion_tokens": tel["completion_tokens"],
                                "cached_tokens": tel["cached_tokens"],
                                "reasoning_tokens": tel["reasoning_tokens"],
                                "cost_usd": tel["cost_usd"],
                                "chunk_count": max(1, tel["chunk_count"]),
                            }
                        )
                        updated_steps.append(updated_st)
                    else:
                        updated_st = st.model_copy(
                            update={
                                "status": actual_status,
                                "last_error": last_err,
                                "message_code": msg_code,
                                "scorecard_atoms": scorecard,
                            }
                        )
                        updated_steps.append(updated_st)

                actual_locale = updated_exec_record.target_locale

                # Execution summary snapshot
                summary_snapshot = ExecutionSummarySnapshot(
                    strictness_level=strictness_level,
                    is_ensemble_run=(workflow_def.default_strictness_level >= 3),
                    is_degraded=is_degraded,
                    system_concurrency_snapshot={
                        "LLM_MAX_CHUNK_SIZE": get_settings().llm_max_chunk_size,
                        "SCHEMA_MAX_EVALUATIONS": get_settings().schema_max_evaluations,
                        "SCHEMA_MAX_CHUNK_RECORDS": get_settings().schema_max_chunk_records,
                        "MATRIX_SAMPLING_LIMIT": get_settings().matrix_sampling_limit,
                    },
                )

                combined_cost_estimate = total_cost_usd + updated_exec_record.cumulative_synthesis_cost
                updated_exec_record = updated_exec_record.model_copy(
                    update={
                        "models_used": models_used,
                        "cost_estimate": combined_cost_estimate,
                        "dag_cost_usd": total_cost_usd,
                        "prompt_tokens": total_prompt_tokens,
                        "completion_tokens": total_completion_tokens,
                        "cached_tokens": total_cached_tokens,
                        "reasoning_tokens": total_reasoning_tokens,
                        "execution_summary": summary_snapshot,
                        "steps": updated_steps,
                    }
                )

                duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

                # TRIGGER ASYNC RENDER JOB (Epic 14 M4)
                redis = ctx.get("redis")
                if redis:
                    # Enqueue job to generate Synthesis cache and Static PDF
                    profile_id = updated_exec_record.output_profile_id

                    v_step_id = f"sys_render_{profile_id}"
                    v_step = ExecutionStep(
                        id=v_step_id, label="Generating Output Report", status=ExecutionStatus.RUNNING
                    )

                    new_steps = [s for s in updated_exec_record.steps if s.id != v_step_id] + [v_step]
                    new_states = dict(updated_exec_record.step_states)
                    new_states[v_step_id] = v_step
                    updated_exec_record = updated_exec_record.model_copy(
                        update={"steps": new_steps, "step_states": new_states}
                    )

                    await repository.update_execution(
                        exec_id,
                        ExecutionUpdateDTO(
                            status=ExecutionStatus.RUNNING,  # keep execution running until PDF is done
                            steps=updated_exec_record.steps,
                            step_states=updated_exec_record.step_states,
                            duration_ms=duration_ms,
                            models_used=models_used,
                            metadata=updated_exec_record.metadata,
                            cost_estimate=combined_cost_estimate,
                            dag_cost_usd=total_cost_usd,
                            prompt_tokens=total_prompt_tokens,
                            completion_tokens=total_completion_tokens,
                            cached_tokens=total_cached_tokens,
                            reasoning_tokens=total_reasoning_tokens,
                            execution_summary=summary_snapshot,
                            execution_trace=updated_exec_record.execution_trace,
                        ),
                    )

                    await redis.enqueue_job(
                        "render_profile_job", exec_id, accept_language=actual_locale, profile_id=profile_id
                    )
                    logger.info(f"[Job] Enqueued render_profile_job for {exec_id} with profile {profile_id}")
                else:
                    logger.warning(f"[Job] Redis context missing. Could not enqueue render_profile_job for {exec_id}")
                    await repository.update_execution(
                        exec_id,
                        ExecutionUpdateDTO(
                            status=ExecutionStatus.PASSED,
                            completed_at=datetime.now(UTC),
                            steps=updated_exec_record.steps,
                            step_states=updated_exec_record.step_states,
                            duration_ms=duration_ms,
                            models_used=models_used,
                            metadata=updated_exec_record.metadata,
                            cost_estimate=combined_cost_estimate,
                            dag_cost_usd=total_cost_usd,
                            prompt_tokens=total_prompt_tokens,
                            completion_tokens=total_completion_tokens,
                            cached_tokens=total_cached_tokens,
                            reasoning_tokens=total_reasoning_tokens,
                            execution_summary=summary_snapshot,
                            execution_trace=updated_exec_record.execution_trace,
                        ),
                    )

            return {
                "status": "COMPLETED",
                "execution_id": exec_id,
                "workflow_id": workflow_id,
                "duration_ms": duration_ms if exec_id else 0,
            }

        except Exception as e:  # noqa: QGR003 [REASON: Background worker top-level DLQ catch-all]
            if not isinstance(e, AppException):
                msg = f"Workflow {workflow_id} failed: {e}"
                logger.error(
                    "[Worker] %s", msg, exc_info=True, extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                )
                e = AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                )

            # Final Status Update (Failed)
            if exec_id:
                try:
                    await repository.update_execution(
                        exec_id,
                        ExecutionUpdateDTO(
                            status=ExecutionStatus.FAILED,
                            error=str(e),
                            completed_at=datetime.now(UTC),
                        ),
                    )
                except Exception as update_err:  # noqa: QGR003 [REASON: Best-effort failure status DB update]
                    update_msg = f"Failed to update execution failure status: {update_err}"
                    logger.error(
                        "[Worker] %s",
                        update_msg,
                        exc_info=True,
                        extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                    )
            return {"_dlq_status": "FAILED/DLQ"}
        except asyncio.CancelledError:
            logger.warning(f"[Job] Workflow {workflow_id} CANCELLED (Timeout/Shutdown). Execution ID: {exec_id}")  # noqa: E501
            if exec_id:
                try:
                    await repository.update_execution(
                        exec_id,
                        ExecutionUpdateDTO(
                            status=ExecutionStatus.FAILED,
                            error="Task execution was cancelled or timed out.",
                            completed_at=datetime.now(UTC),
                        ),
                    )
                except Exception as update_err:  # noqa: QGR003 [REASON: Best-effort failure status DB update]
                    update_msg = f"Failed to update execution cancellation status: {update_err}"
                    logger.error(
                        "[Worker] %s",
                        update_msg,
                        exc_info=True,
                        extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                    )
            return {"_dlq_status": "FAILED/DLQ"}


async def generate_pdf_job(
    ctx: Any, execution_id: str, accept_language: str | None = None, profile_id: str | None = None
) -> str | dict[str, str]:
    """Invoked by Arq Worker to ensure background PDF compilation resilience.

    Args:
        ctx: Arq worker context.
        execution_id: Target execution identifier.
        accept_language: Optional locale override.
        profile_id: Target output profile identifier.

    Returns:
        Status message string upon completion, or DLQ dict on failure.
    """
    try:
        await generate_pdf_task(execution_id, accept_language, profile_id)
        return f"PDF Generated for {execution_id}"
    except asyncio.CancelledError:
        logger.warning(f"[Worker] generate_pdf_job cancelled for {execution_id}")
        return {"_dlq_status": "FAILED/DLQ"}
    except Exception as e:  # noqa: QGR003 [REASON: Background job top-level DLQ handler]
        logger.error(f"[Worker] generate_pdf_job failed for {execution_id}: {e}", exc_info=True)
        return {"_dlq_status": "FAILED/DLQ"}


async def generate_pdf_task(
    execution_id: str, accept_language: str | None = None, profile_id: str | None = None
) -> None:  # noqa: E501
    """Background Task. Assembles the SDUI JSON via Transformer and passes to PDF generator.

    Called by Arq worker for resilient PDF background compilation.

    Args:
        execution_id: Target execution identifier.
        accept_language: Optional locale override.
        profile_id: Target output profile identifier.

    Raises:
        AppException: Inherited from inner logic if generation or update fails.
    """
    logger.info(f"[Task] Starting Async PDF Koonti for execution {execution_id}")
    try:
        driver = await get_driver(get_settings())
        repo = UnifiedWorkflowRepository(driver)
        transformer = BlueprintTransformer(
            exec_repo=repo,
            workflow_repo=repo,
            comp_repo=repo,
            prompt_block_repo=repo,
            output_profile_repo=repo,
            identity_repo=repo,
            system_repo=repo,
        )  # noqa: E501

        # 0. Guard: Execution may have been deleted while PDF job was queued
        execution_dict = await repo.get_execution(execution_id)
        if not execution_dict:
            logger.warning(f"[Task] Execution {execution_id} no longer exists (deleted?). Skipping PDF generation.")  # noqa: E501
            return

        # V2 MANDATE: Strict Pydantic parsing at the boundary
        execution_record = ExecutionRecord.model_validate(execution_dict, strict=False)

        # 0b. Get explicit locale via Execution
        if not accept_language:
            accept_language = execution_record.target_locale

        if accept_language:
            set_language(accept_language)

        # 0c. Override default profile dynamically if present in SSOT ExecutionRecord
        if execution_record.output_profile_id:
            profile_id = execution_record.output_profile_id

        # 1. Generate Omni-Channel JSON Payload
        dto = await transformer.build_report_dto(execution_id, profile_id, accept_language)

        # 2. Feed structured DTO to PDF Engine instead of DB fetching
        service = PdfReportService()
        pdf_bytes = await service.generate_execution_pdf(execution_id, report_dto=dto, locale=accept_language)

        # 3. Save bytes
        storage = get_storage_driver()
        output_path_rel = f"executions/{execution_id}/report.pdf"
        saved_path = await storage.save(output_path_rel, pdf_bytes)

        # 4. Save path to DB so frontend can fetch it
        v_step_id = f"sys_render_{profile_id}"

        exec_record_local = await repo.get_execution(execution_id, hydrate=False)
        step_states = None
        steps = None
        if exec_record_local:
            exec_record_local = ExecutionRecord.model_validate(exec_record_local, strict=False)
            if v_step_id in exec_record_local.step_states:
                old_state = exec_record_local.step_states[v_step_id]
                new_states = dict(exec_record_local.step_states)
                new_step = old_state.model_copy(update={"status": ExecutionStatus.PASSED})
                new_states[v_step_id] = new_step
                new_steps = [
                    s.model_copy(update={"status": ExecutionStatus.PASSED}) if s.id == v_step_id else s
                    for s in exec_record_local.steps
                ]
                exec_record_local = exec_record_local.model_copy(update={"step_states": new_states, "steps": new_steps})
            step_states = exec_record_local.step_states
            steps = exec_record_local.steps

        await repo.update_execution(
            execution_id,
            ExecutionUpdateDTO(
                pdf_report_path=saved_path,
                status=ExecutionStatus.PASSED,
                steps=steps,
                step_states=step_states,
            ),
        )
        logger.info(f"[Task] PDF generated successfully and path saved: {saved_path}")

    except Exception as e:
        logger.error(
            "[Task] PDF generation failed for %s. Cause: %s",
            execution_id,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.PDF_GENERATION_FAILED.value},
        )
        try:
            driver = await get_driver(get_settings())
            repo = UnifiedWorkflowRepository(driver)
            v_step_id = f"sys_render_{profile_id}"
            fail_step_states = None
            fail_steps = None
            exec_record_local = await repo.get_execution(execution_id, hydrate=False)
            if exec_record_local:
                exec_record_local = ExecutionRecord.model_validate(exec_record_local, strict=False)
                if v_step_id in exec_record_local.step_states:
                    old_state = exec_record_local.step_states[v_step_id]
                    new_states = dict(exec_record_local.step_states)
                    new_step = old_state.model_copy(update={"status": ExecutionStatus.FAILED, "last_error": str(e)})
                    new_states[v_step_id] = new_step
                    new_steps = [
                        s.model_copy(update={"status": ExecutionStatus.FAILED, "last_error": str(e)})
                        if s.id == v_step_id
                        else s
                        for s in exec_record_local.steps
                    ]
                    exec_record_local = exec_record_local.model_copy(
                        update={"step_states": new_states, "steps": new_steps}
                    )
                fail_step_states = exec_record_local.step_states
                fail_steps = exec_record_local.steps

            await repo.update_execution(
                execution_id,
                ExecutionUpdateDTO(
                    status=ExecutionStatus.FAILED,
                    error=f"PDF Generation failed: {str(e)}",
                    completed_at=datetime.now(UTC),
                    steps=fail_steps,
                    step_states=fail_step_states,
                ),
            )
        except Exception:  # noqa: QGR003 [REASON: Best-effort failure status DB update]
            logger.error(
                "[Task] Failed to update execution failure status",
                exc_info=True,
                extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )
        raise e


async def render_profile_job(
    ctx: Any, execution_id: str, accept_language: str | None = None, profile_id: str | None = None
) -> str | dict[str, str]:
    """Invoked by Arq Worker to ensure background synthesis & PDF compilation resilience.

    Args:
        ctx: Arq worker context.
        execution_id: Target execution identifier.
        accept_language: Optional locale override.
        profile_id: Target output profile identifier.

    Returns:
        Status message string upon completion, or DLQ dict on failure.
    """
    try:
        await generate_profile_synthesis_and_pdf_task(execution_id, accept_language, profile_id, ctx.get("redis"))  # noqa: E501
        return f"Render Job Completed for {execution_id}"
    except asyncio.CancelledError:
        logger.warning(f"[Worker] render_profile_job cancelled for {execution_id}")
        return {"_dlq_status": "FAILED/DLQ"}
    except Exception as e:  # noqa: QGR003 [REASON: Background job top-level DLQ handler]
        logger.error(f"[Worker] render_profile_job failed for {execution_id}: {e}", exc_info=True)
        return {"_dlq_status": "FAILED/DLQ"}


async def generate_profile_synthesis_and_pdf_task(
    execution_id: str,
    accept_language: str | None = None,
    profile_id: str | None = None,
    redis: Any | None = None,  # noqa: E501
) -> None:
    """Background Task. Synthesizes Markdown and enqueues PDF generation.

    Args:
        execution_id: Target execution identifier.
        accept_language: Optional locale override.
        profile_id: Target output profile identifier.
        redis: Optional Redis context.

    Raises:
        AppException: If synthesis or execution update fails with VALIDATION_FAILED,
            CONFIGURATION_ERROR, or INTERNAL_SERVER_ERROR.
    """
    if not accept_language:
        msg = "Strict Fail-Fast Enforced: 'accept_language' is mandatory and cannot be None."
        logger.error("[Task] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
        raise AppException(
            message=msg,
            status_code=400,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
    logger.info(f"[Task] Starting Async Text Synthesis for execution {execution_id} (Profile: {profile_id})")  # noqa: E501
    try:
        driver = await get_driver(get_settings())
        repo = UnifiedWorkflowRepository(driver)

        execution_data = await repo.get_execution(execution_id)
        if not execution_data:
            logger.warning(f"[Task] Execution {execution_id} no longer exists. Skipping render.")
            return

        # V2 MANDATE: Strict Pydantic parsing at the boundary
        execution = ExecutionRecord.model_validate(execution_data, strict=False)
        v_step_id = f"sys_render_{profile_id}"

        syntheses = execution.profile_syntheses if execution.profile_syntheses is not None else {}
        has_synthesis = profile_id in syntheses
        if has_synthesis:
            logger.info(f"[Task] Synthesis already exists for profile {profile_id}. Proceeding to PDF generation.")  # noqa: E501
            if redis:
                await redis.enqueue_job("generate_pdf_job", execution_id, accept_language, profile_id)
            return

        async def _update_render_status(msg: str) -> None:
            exec_record_local = await repo.get_execution(execution_id, hydrate=False)
            if exec_record_local:
                exec_record_local = ExecutionRecord.model_validate(exec_record_local, strict=False)
                old_state = (
                    exec_record_local.step_states[v_step_id] if v_step_id in exec_record_local.step_states else None
                )
                if old_state:
                    updated_state = old_state.model_copy(update={"label": msg, "status": ExecutionStatus.RUNNING})
                else:
                    updated_state = ExecutionStep(id=v_step_id, label=msg, status=ExecutionStatus.RUNNING)
                new_states = dict(exec_record_local.step_states)
                new_states[v_step_id] = updated_state
                new_steps = [
                    s.model_copy(update={"label": msg, "status": ExecutionStatus.RUNNING}) if s.id == v_step_id else s
                    for s in exec_record_local.steps
                ]
                if not any(s.id == v_step_id for s in exec_record_local.steps):
                    new_steps.append(updated_state)
                await repo.update_execution(
                    execution_id,
                    ExecutionUpdateDTO(steps=new_steps, step_states=new_states),
                )

        await _update_render_status("Lasketaan dynaamisia tuloksia...")

        projector = StateProjector()
        for evt in execution.execution_trace:
            # Memory FinOps Protocol: Prevent 200-page RAW inputs from hydrating into RAM
            # Synthesis only needs the analytical DTOs (event_type="output")
            if evt.event_type == "input":
                continue
            projector.apply_delta(evt)
        final_inputs = projector._build_dto_list()

        # 0b. Get explicit locale via Execution
        if not accept_language and execution.target_locale:
            accept_language = execution.target_locale

        if accept_language:
            set_language(accept_language)

        # Check for starvation short-circuit from SynthesisEngine
        starvation_detected = False
        for trace_evt in execution.execution_trace:
            if trace_evt.event_type == "output":
                try:
                    t_content = TypeAdapter(dict[str, Any]).validate_python(trace_evt.content)
                    if t_content.get("event_type") == "starvation":
                        starvation_detected = True
                        break
                except Exception:
                    continue

        if starvation_detected:
            logger.warning(
                "[Task] Data starvation detected in execution %s trace. Short-circuiting synthesis tasks.",
                execution_id,
            )
            starvation_dto = DataStarvationEvent(total_atoms=0, reason="Data starvation: insufficient atoms")
            cache = RenderedSynthesisCache(
                section_syntheses={},
                row_explanations={},
                cited_sources=[],
                xai_highlights=[],
                user_role=None,
                user_role_justification=None,
                extension_metrics=None,
                data_starvation=starvation_dto,
            )

            current_syntheses = dict(execution.profile_syntheses) if execution.profile_syntheses is not None else {}
            starvation_pid: str = profile_id if profile_id is not None else "default"
            current_syntheses[starvation_pid] = cache

            await repo.update_execution(
                execution_id,
                ExecutionUpdateDTO(profile_syntheses=current_syntheses),
            )

            logger.info(f"[Task] Starvation synthesis cached for {execution_id} (Profile: {profile_id})")

            await _update_render_status("Koostetaan tulosteita valmiiksi...")
            if redis:
                await redis.enqueue_job("generate_pdf_job", execution_id, accept_language, profile_id)
            return

        # Fetch output profile to resolve dynamic strictness & strategy
        p_dict = await repo.get_output_profile_by_id(profile_id) if profile_id else None
        active_profile_dto = OutputProfile.model_validate(p_dict, strict=False) if p_dict else None

        w_dict = await repo.get_workflow_by_id(execution.workflow_id)
        workflow_def = Workflow.model_validate(w_dict) if w_dict else None

        strictness_level = StrictnessAnchor.STANDARD.value
        scoring_strategy_val = "AVERAGE"
        if active_profile_dto:
            if active_profile_dto.strictness_level is not None:
                strictness_level = active_profile_dto.strictness_level
            elif workflow_def:
                strictness_level = workflow_def.default_strictness_level

            if active_profile_dto.scoring_strategy is not None:
                scoring_strategy_val = str(active_profile_dto.scoring_strategy)
            elif workflow_def:
                scoring_strategy_val = str(workflow_def.default_scoring_strategy)
        else:
            if workflow_def:
                strictness_level = workflow_def.default_strictness_level
                scoring_strategy_val = str(workflow_def.default_scoring_strategy)

        # Calculate scores dynamically for all matrices
        engine = get_scoring_engine(scoring_strategy_val)

        # Pre-fetch block metadata for math_min/math_max
        all_blocks_raw = await repo.get_all_prompt_blocks()
        blocks_meta = {}
        for rb in all_blocks_raw:
            pb = PromptBlockAdapter.validate_python(rb, strict=False)
            if isinstance(pb, MatrixPromptBlock) and pb.scales:
                s_vals = [float(s.score) for s in pb.scales]
                if s_vals:
                    blocks_meta[pb.id] = {"math_min": min(s_vals), "math_max": max(s_vals)}

        for i, step_dto in enumerate(final_inputs):
            pb_id = step_dto.block_id
            data = step_dto.payload
            if pb_id in blocks_meta:
                try:
                    try:
                        data_dict = TypeAdapter(dict[str, Any]).validate_python(data)
                        clean_data = {k: v for k, v in data_dict.items() if k in LightweightMatrixOutput.model_fields}
                    except Exception:
                        clean_data = data
                    lw_matrix = LightweightMatrixOutput.model_validate(clean_data, strict=False)
                    if lw_matrix.level_breakdown:
                        stats = {
                            float(k): LevelStatsDTO(
                                hits=v["hits"], total=v["total"], dlqs=v["dlqs"] if "dlqs" in v else 0
                            )
                            for k, v in lw_matrix.level_breakdown.items()
                        }
                        b_meta = blocks_meta.get(pb_id)
                        if b_meta:
                            math_min = b_meta["math_min"]
                            math_max = b_meta["math_max"]
                            calculated_score, xai_log_dto, _ = engine.calculate(
                                stats, math_min, math_max, strictness_level=strictness_level
                            )
                            norm_val = normalize_score_to_100(
                                score=calculated_score,
                                math_min=b_meta["math_min"],
                                math_max=b_meta["math_max"],
                            )
                            lw_matrix = lw_matrix.model_copy(
                                update={
                                    "raw_score": float(calculated_score),
                                    "normalized_score": float(norm_val),
                                    "xai_log": xai_log_dto,
                                }
                            )

                            new_payload = lw_matrix.model_dump(exclude_none=True)

                            # V2 Infrastructure Mandate: Preserve accumulators that bypass strict schemas
                            if "atom_quotes" in data:
                                new_payload["atom_quotes"] = data["atom_quotes"]

                            # V2 Frozen Model update
                            final_inputs[i] = step_dto.model_copy(update={"payload": new_payload})

                            # Persist the dynamic score back to the execution trace so blueprint.py can find it
                            for trace_evt in execution.execution_trace:
                                valid_event = trace_evt.event_type in ["output", "input"]
                                if valid_event and trace_evt.step_name == step_dto.step_id:
                                    if pb_id in trace_evt.content:
                                        trace_evt.content[pb_id] = new_payload
                                        break
                except Exception as e:  # noqa: QGR003 [REASON: Resilient best-effort dynamic matrix calculation]
                    logger.warning(f"Failed to calculate dynamic score for {pb_id}: {e}")

        # Extract Synthesis from DAG Execution Trace (Phase 3/4)
        await _update_render_status("Generoidaan tekoälysynteesiä (tämä saattaa kestää verkosta riippuen)...")
        is_synthesis_expected = active_profile_dto.is_synthesis_expected if active_profile_dto else True

        # Inject dynamic locale and execution context into hook_state for synthesis_distiller
        hook_metadata = execution.metadata or ExecutionMetadata()

        hook_state = HookState(
            execution_id=execution_id,
            workflow_id=execution.workflow_id,
            metadata=hook_metadata,
            global_context_vars=GlobalContextVarsDTO(vars={"language": accept_language, "profile_id": profile_id}),
            inputs=ExecutionInputsDTO(target_locale=accept_language, dynamic_inputs={"steps": final_inputs}),
        )
        hook_deps = HookDependencies(
            exec_repo=repo,
            workflow_repo=repo,
            comp_repo=repo,
            prompt_block_repo=repo,
            output_profile_repo=repo,
            identity_repo=repo,
            audit_repo=repo,
            system_repo=repo,
        )
        hook_result = await synthesis_distiller_hook(hook_state, hook_deps)
        if hook_result.state_delta is None or not hook_result.state_delta.delta:
            raise AppException(
                message="Fail-Fast: hook_result.state_delta cannot be None.",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        distilled_data = hook_result.state_delta.delta
        if "distilled_inputs" not in distilled_data:
            raise AppException(
                message="Fail-Fast: distilled_inputs missing from state_delta.",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        distilled_inputs = distilled_data["distilled_inputs"]
        raw_matrices = distilled_data["matrices_to_explain"] if "matrices_to_explain" in distilled_data else []
        matrices_to_explain: list[MatrixExplanationContextDTO] = [
            m if isinstance(m, MatrixExplanationContextDTO) else MatrixExplanationContextDTO.model_validate(m)
            for m in raw_matrices
        ]

        synthesis_model_strategy = "synthesis"

        t_exec_summary = None
        t_matrix_sections: list[tuple[str, Any]] = []
        t_xai = None
        t_row = None
        t_variance = None
        ext_metrics = None

        async with asyncio.TaskGroup() as tg:
            if is_synthesis_expected:
                # sys_prompt MUST remain 100% static for cache prefix survival
                sys_prompt = f"{SYNTHESIS_SYSTEM_PROMPT}\n\n{SYNTHESIS_SDUI_MANDATES}\n\n{ANTI_JARGON_MANDATE_BLOCK}\n\n{STATIC_LINGUISTIC_PROTOCOL}"

                # Dynamic context parts injected into user message <dynamic_context>
                base_dynamic_parts: list[str] = [
                    SYNTHESIS_CITATION_RULES_HARVARD,
                ]
                lang_params = build_linguistic_parameters(source_language="Unknown", target_locale=accept_language)
                base_dynamic_parts.append(lang_params)

                if active_profile_dto and active_profile_dto.synthesis_length_constraint:
                    base_dynamic_parts.append(
                        f"<global_length_constraint_chars>{active_profile_dto.synthesis_length_constraint}</global_length_constraint_chars>"
                    )

                if active_profile_dto and active_profile_dto.tone_instruction:
                    tone = active_profile_dto.tone_instruction.strip()
                    if tone:
                        base_dynamic_parts.append(f"<tone_instruction>{tone}</tone_instruction>")
                    else:
                        logger.warning(
                            "[generate_profile_synthesis_and_pdf_task] OutputProfile '%s' has empty tone_instruction. Skipping tone directive.",
                            active_profile_dto.id,
                        )
                elif active_profile_dto:
                    logger.warning(
                        "[generate_profile_synthesis_and_pdf_task] OutputProfile '%s' has no tone_instruction configured. Skipping tone directive.",
                        active_profile_dto.id,
                    )

                client = await LLMClient.from_strategy(synthesis_model_strategy, repository=repo)

                matrix_context = ""
                if matrices_to_explain:
                    matrix_context = f"\n\nMATRICES TO EXPLAIN:\n{MatrixExplanationContextList.dump_json(matrices_to_explain, indent=2, exclude_none=True).decode('utf-8')}"

                # 1. Dedicated Executive Summary task
                if active_profile_dto is None or active_profile_dto.requires_executive_synthesis:
                    exec_directive = None
                    if active_profile_dto:
                        if (
                            not active_profile_dto.executive_summary_directive
                            or not active_profile_dto.executive_summary_directive.strip()
                        ):
                            logger.warning(
                                "[generate_profile_synthesis_and_pdf_task] OutputProfile '%s' is missing executive_summary_directive. Skipping Executive Summary synthesis.",
                                active_profile_dto.id,
                            )
                            exec_directive = None
                        else:
                            exec_directive = active_profile_dto.executive_summary_directive.strip()

                    if exec_directive:
                        exec_dynamic_parts = list(base_dynamic_parts)
                        if active_profile_dto and active_profile_dto.synthesis_length_constraint:
                            exec_dynamic_parts.append(
                                f"<section_budget>{active_profile_dto.synthesis_length_constraint}</section_budget>"
                            )
                        exec_section_rule = (
                            f'{SYNTHESIS_SECTION_RULES_PREFIX}\n<section_instruction id="{EXECUTIVE_SUMMARY_SECTION_ID}" title="Executive Summary">\n'
                            f"{exec_directive}\n"
                            "</section_instruction>\n"
                        )
                        exec_dynamic_parts.append(exec_section_rule)
                        exec_dynamic_context = "\n\n".join(exec_dynamic_parts)

                        exec_messages: list[dict[str, Any]] = [
                            {"role": "system", "content": sys_prompt},
                            {
                                "role": "user",
                                "content": (
                                    f"<dynamic_context>\n{exec_dynamic_context}\n</dynamic_context>"
                                    f"\n\nDATA TO SYNTHESIZE:\n{distilled_inputs}{matrix_context}"
                                ),
                            },
                        ]
                        t_exec_summary = tg.create_task(
                            client.run_structured_task(
                                messages=exec_messages,
                                response_model=ExecutiveSummarySectionResult,
                                mock_identity="ExecutiveSummaryTask",
                            )
                        )
                    else:
                        logger.warning(
                            "[generate_profile_synthesis_and_pdf_task] No executive_summary_directive configured in database OutputProfile. Skipping Executive Summary synthesis."
                        )

                # 2. Dedicated Matrix Synthesis Groups tasks
                if active_profile_dto and active_profile_dto.requires_group_synthesis:
                    language = distilled_data["language"] if "language" in distilled_data else "en"
                    title_map = distilled_data["title_map"] if "title_map" in distilled_data else {}

                    for grp in active_profile_dto.matrix_synthesis_groups:
                        grp_id = grp.id
                        grp_title = grp.title.resolve(language) if grp.title else grp_id

                        directive_content = None
                        match grp.view_type:
                            case PresetView.METRICS_1D | "1d_metrics":
                                directive_content = active_profile_dto.matrix_1d_synthesis_directive
                            case PresetView.COMPARE_2D | "2d_compare":
                                directive_content = active_profile_dto.matrix_2d_synthesis_directive
                            case PresetView.MATRIX_3D | "3d_matrix":
                                directive_content = active_profile_dto.matrix_3d_synthesis_directive
                            case PresetView.TEXT_ONLY | "text_only":
                                directive_content = active_profile_dto.matrix_text_synthesis_directive
                            case _:
                                directive_content = None

                        if not directive_content or not directive_content.strip():
                            logger.warning(
                                "[generate_profile_synthesis_and_pdf_task] OutputProfile '%s' is missing matrix synthesis directive for view_type '%s' (group '%s'). Skipping group synthesis.",
                                active_profile_dto.id,
                                grp.view_type,
                                grp_id,
                            )
                            continue
                        directive_content = directive_content.strip()

                        target_titles = []
                        if grp.target_blocks:
                            for tb in grp.target_blocks:
                                if tb.lower() in title_map:
                                    target_titles.append(title_map[tb.lower()])
                        target_str = f' targets="{", ".join(target_titles)}"' if target_titles else ""

                        grp_dynamic_parts = list(base_dynamic_parts)
                        if active_profile_dto and active_profile_dto.matrix_graph_length_constraint:
                            grp_dynamic_parts.append(
                                f"<section_budget>{active_profile_dto.matrix_graph_length_constraint}</section_budget>"
                            )
                        grp_section_rule = (
                            f'{SYNTHESIS_SECTION_RULES_PREFIX}\n<section_instruction id="{grp_id}" title="{grp_title}"{target_str}>\n'
                            f"{directive_content}\n"
                            f"</section_instruction>\n\n{SECTION_SYNTHESIS_DIRECTIVE_BLOCK}"
                        )
                        grp_dynamic_parts.append(grp_section_rule)
                        grp_dynamic_context = "\n\n".join(grp_dynamic_parts)

                        grp_messages: list[dict[str, Any]] = [
                            {"role": "system", "content": sys_prompt},
                            {
                                "role": "user",
                                "content": (
                                    f"<dynamic_context>\n{grp_dynamic_context}\n</dynamic_context>"
                                    f"\n\nDATA TO SYNTHESIZE:\n{distilled_inputs}{matrix_context}"
                                ),
                            },
                        ]
                        task_handle = tg.create_task(
                            client.run_structured_task(
                                messages=grp_messages,
                                response_model=MatrixSectionSynthesesResult,
                                mock_identity=f"MatrixSectionTask_{grp_id}",
                            )
                        )
                        t_matrix_sections.append((grp_id, task_handle))

                # 3. Dedicated XAI Highlights task
                if active_profile_dto and (
                    active_profile_dto.visible_block_extensions or active_profile_dto.visible_workflow_extensions
                ):
                    max_ext = active_profile_dto.max_extension_items
                    if max_ext is None:
                        raise AppException(
                            message="Fail-Fast: max_extension_items is mandatory if extensions are visible.",
                            status_code=400,
                            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                        )
                    wf_exts: list[Any] = []
                    if active_profile_dto.visible_workflow_extensions:
                        wf_exts.extend(active_profile_dto.visible_workflow_extensions)
                    if active_profile_dto.visible_block_extensions:
                        wf_exts.extend(active_profile_dto.visible_block_extensions)
                    wf_exts = list(dict.fromkeys(wf_exts))
                    req_exts = ", ".join([str(e) for e in wf_exts]) if wf_exts else "none"

                    if (
                        not active_profile_dto.xai_synthesis_directive
                        or not active_profile_dto.xai_synthesis_directive.strip()
                    ):
                        logger.warning(
                            "[generate_profile_synthesis_and_pdf_task] OutputProfile '%s' is missing xai_synthesis_directive. Skipping XAI highlights synthesis.",
                            active_profile_dto.id,
                        )
                    else:
                        xai_directive_str = active_profile_dto.xai_synthesis_directive.strip()

                        xai_cur = (
                            f"{xai_directive_str}\n\n"
                            f"{SYNTHESIS_XAI_CURATION.replace('<max_extension_items>', str(max_ext)).replace('<requested_extensions>', req_exts)}"
                        )

                        xai_dynamic_parts = list(base_dynamic_parts)
                        if active_profile_dto.xai_length_constraint:
                            xai_dynamic_parts.append(
                                f"<section_budget>{active_profile_dto.xai_length_constraint}</section_budget>"
                            )
                        xai_dynamic_parts.append(xai_cur)
                        xai_dynamic_context = "\n\n".join(xai_dynamic_parts)

                        xai_messages: list[dict[str, Any]] = [
                            {"role": "system", "content": sys_prompt},
                            {
                                "role": "user",
                                "content": (
                                    f"<dynamic_context>\n{xai_dynamic_context}\n</dynamic_context>"
                                    f"\n\nDATA TO SYNTHESIZE:\n{distilled_inputs}{matrix_context}"
                                ),
                            },
                        ]
                        t_xai = tg.create_task(
                            client.run_structured_task(
                                messages=xai_messages,
                                response_model=XaiHighlightsResult,
                                mock_identity="XaiHighlightsTask",
                            )
                        )

            if matrices_to_explain and (active_profile_dto is None or active_profile_dto.requires_row_explanations):
                client = await LLMClient.from_strategy("strict", repository=repo)
                row_sys_prompt = f"{ROW_EXPLANATION_SYSTEM_PROMPT}\n\n{STATIC_LINGUISTIC_PROTOCOL}"

                row_lang_params = build_linguistic_parameters(source_language="Unknown", target_locale=accept_language)
                row_directive_str = None
                if active_profile_dto:
                    if (
                        not active_profile_dto.row_explanation_directive
                        or not active_profile_dto.row_explanation_directive.strip()
                    ):
                        logger.warning(
                            "[generate_profile_synthesis_and_pdf_task] OutputProfile '%s' is missing row_explanation_directive. Skipping row explanation synthesis.",
                            active_profile_dto.id,
                        )
                    else:
                        row_directive_str = active_profile_dto.row_explanation_directive.strip()
                else:
                    logger.warning(
                        "[generate_profile_synthesis_and_pdf_task] No active OutputProfile for row explanation synthesis. Skipping row explanations."
                    )

                if row_directive_str:
                    row_dynamic_parts = [
                        row_lang_params,
                    ]
                    if active_profile_dto and active_profile_dto.tone_instruction:
                        tone = active_profile_dto.tone_instruction.strip()
                        if tone:
                            row_dynamic_parts.append(f"<tone_instruction>{tone}</tone_instruction>")
                    row_dynamic_parts.append(row_directive_str)
                    if active_profile_dto and active_profile_dto.row_explanation_length_constraint:
                        row_dynamic_parts.append(
                            f"<section_budget>{active_profile_dto.row_explanation_length_constraint}</section_budget>"
                        )
                    row_dynamic_ctx = "\n\n".join(row_dynamic_parts)

                    row_messages: list[dict[str, Any]] = [
                        {"role": "system", "content": row_sys_prompt},
                        {
                            "role": "user",
                            "content": (
                                f"<dynamic_context>\n{row_dynamic_ctx}\n</dynamic_context>"
                                f"\n\nMATRICES TO EXPLAIN:\n{MatrixExplanationContextList.dump_json(matrices_to_explain, indent=2, exclude_none=True).decode('utf-8')}"
                            ),
                        },
                    ]
                    t_row = tg.create_task(
                        client.run_structured_task(
                            messages=row_messages,
                            response_model=MatrixExplanationsResult,
                            mock_identity="row_explainer",
                        )
                    )

            if (
                active_profile_dto
                and active_profile_dto.visible_workflow_extensions
                and (
                    "variance_validation" in active_profile_dto.visible_workflow_extensions
                    or "authenticity_evaluation" in active_profile_dto.visible_workflow_extensions
                )
            ):
                authenticity_score = None
                performative_phrases_count = None
                cv = execution.context_variables

                # 1. Linguistics comes from global_context_vars via the linguistics post-hook
                if cv is not None and "step_linguistics" in cv:
                    step_ling = cv["step_linguistics"]
                    if step_ling is not None:
                        ling_out = LinguisticsResultDTO.model_validate(step_ling, strict=False)
                        patterns = ling_out.performative_patterns
                        if isinstance(patterns, list):
                            performative_phrases_count = len(patterns)

                # 2. Performativity Detector comes from the DAG step output in the trace
                perf_step_id = active_profile_dto.performativity_detector_step_id

                # Dynamically resolve missing values from execution trace
                if authenticity_score is None or performative_phrases_count is None:
                    for event in reversed(execution.execution_trace):
                        if not isinstance(event, TraceEvent):
                            continue

                        # Fallback for Linguistics (decision event with is_context_update)
                        if event.event_type == "decision" and performative_phrases_count is None:
                            try:
                                dec_content = TypeAdapter(dict[str, Any]).validate_python(event.content)
                                if "step_linguistics" in dec_content:
                                    trace_ling = dec_content["step_linguistics"]
                                    ling_out = LinguisticsResultDTO.model_validate(trace_ling, strict=False)
                                    patterns = ling_out.performative_patterns
                                    if isinstance(patterns, list):
                                        performative_phrases_count = len(patterns)
                            except (ValidationError, TypeError, ValueError) as e:
                                logger.warning(
                                    "Failed to parse linguistics from decision trace event",
                                    extra={"error": str(e), "execution_id": execution.id},
                                )

                        # Extract Performativity Detector output using the canonical step_id from profile
                        if event.event_type == "output" and perf_step_id and authenticity_score is None:
                            is_match = False
                            out_content: dict[str, Any] | None = None
                            try:
                                out_content = TypeAdapter(dict[str, Any]).validate_python(event.content)
                            except (ValidationError, TypeError, ValueError) as e:
                                logger.warning(
                                    "Failed to parse output content dictionary from trace event",
                                    extra={"error": str(e), "execution_id": execution.id},
                                )
                                out_content = None

                            if event.step_name == perf_step_id:
                                is_match = True
                            elif out_content and "_step_metadata" in out_content:
                                try:
                                    step_meta = StepTraceMetadataDTO.model_validate(out_content["_step_metadata"])
                                    if step_meta.task_blueprint == perf_step_id:
                                        is_match = True
                                except (ValidationError, TypeError, ValueError) as e:
                                    logger.warning(
                                        "Failed to parse step trace metadata from detector output",
                                        extra={"error": str(e), "execution_id": execution.id},
                                    )

                            if is_match and out_content:
                                for key, val in out_content.items():
                                    if key.startswith("blk_"):
                                        det_out = LightweightMatrixOutput.model_validate(val, strict=False)
                                        if det_out.raw_score is not None:
                                            authenticity_score = float(det_out.raw_score)
                                        break

                        if authenticity_score is not None and performative_phrases_count is not None:
                            break

                if authenticity_score is not None and performative_phrases_count is not None:
                    variance_res = variance_engine.calculate_mechanical_cognitive_variance(
                        llm_authenticity_score=authenticity_score,
                        performative_phrases_count=performative_phrases_count,
                    )

                    ext_metrics = ExtensionMetricsDTO(
                        authenticity_score=float(authenticity_score),
                        performative_phrases_count=float(performative_phrases_count),
                        variance_score=float(variance_res["variance_score"]),
                        alignment_verdict=str(variance_res["alignment_verdict"]),
                    )

                    client_var = await LLMClient.from_strategy("strict", repository=repo)
                    var_sys_prompt = f"{VARIANCE_SYSTEM_PROMPT}\n\n{STATIC_LINGUISTIC_PROTOCOL}"

                    var_lang_params = build_linguistic_parameters(
                        source_language="Unknown", target_locale=accept_language
                    )
                    if (
                        not active_profile_dto.variance_synthesis_directive
                        or not active_profile_dto.variance_synthesis_directive.strip()
                    ):
                        logger.warning(
                            "[generate_profile_synthesis_and_pdf_task] OutputProfile '%s' is missing variance_synthesis_directive. Skipping variance synthesis.",
                            active_profile_dto.id,
                        )
                    else:
                        var_directive_str = active_profile_dto.variance_synthesis_directive.strip()

                        var_dynamic_parts = [
                            var_lang_params,
                        ]
                        if active_profile_dto and active_profile_dto.tone_instruction:
                            tone = active_profile_dto.tone_instruction.strip()
                            if tone:
                                var_dynamic_parts.append(f"<tone_instruction>{tone}</tone_instruction>")
                        var_dynamic_parts.append(var_directive_str)
                        if active_profile_dto.variance_length_constraint:
                            var_dynamic_parts.append(
                                f"<section_budget>{active_profile_dto.variance_length_constraint}</section_budget>"
                            )
                        var_dynamic_ctx = "\n\n".join(var_dynamic_parts)

                        var_messages: list[dict[str, Any]] = [
                            {"role": "system", "content": var_sys_prompt},
                            {
                                "role": "user",
                                "content": (
                                    f"<dynamic_context>\n{var_dynamic_ctx}\n</dynamic_context>"
                                    f"\n\nSCORES TO EXPLAIN:\nCognitive Score: {authenticity_score}\nMechanical Phrases Count: {performative_phrases_count}"
                                ),
                            },
                        ]

                        t_variance = tg.create_task(
                            client_var.run_structured_task(
                                messages=var_messages,
                                response_model=VarianceExplanationResult,
                                mock_identity="variance_explainer",
                            )
                        )

        synth_cost = 0.0
        synth_tokens = 0

        sec_dict: dict[str, list[AnySduiBlock]] = {}
        exec_dto: ExecutiveSummarySectionResult | None = None

        if t_exec_summary and t_exec_summary.result():
            exec_res, usage = t_exec_summary.result()
            exec_dto = exec_res
            if exec_dto and exec_dto.executive_summary:
                summary_blocks = exec_dto.executive_summary
                if active_profile_dto and active_profile_dto.synthesis_length_constraint:
                    budget = active_profile_dto.synthesis_length_constraint
                    budgeted_blocks: list[LlmSduiBlock] = []
                    for blk in summary_blocks:
                        if isinstance(blk, ParagraphBlock) and len(blk.text) > budget:
                            blk = blk.model_copy(update={"text": enforce_sentence_boundary_budget(blk.text, budget)})
                        budgeted_blocks.append(blk)
                    summary_blocks = budgeted_blocks
                    exec_dto = exec_dto.model_copy(update={"executive_summary": summary_blocks})
                sec_dict[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value] = cast(list[AnySduiBlock], summary_blocks)
            if usage:
                synth_cost += usage.cost_usd
                synth_tokens += usage.total_tokens

        for lay_id, lay_task in t_matrix_sections:
            if lay_task and lay_task.result():
                mat_res, usage = lay_task.result()
                if mat_res and isinstance(mat_res, MatrixSectionSynthesesResult):
                    aggregated_blocks: list[AnySduiBlock] = []
                    for sec in mat_res.sections:
                        if sec.content_blocks:
                            aggregated_blocks.extend(cast(list[AnySduiBlock], sec.content_blocks))
                    if aggregated_blocks:
                        sec_dict[lay_id] = aggregated_blocks
                if usage:
                    synth_cost += usage.cost_usd
                    synth_tokens += usage.total_tokens

        xai_highlights_list: list[XaiHighlightItem] = []
        if t_xai and t_xai.result():
            xai_res, usage = t_xai.result()
            if xai_res and isinstance(xai_res, XaiHighlightsResult):
                xai_highlights_list = xai_res.xai_highlights
                if active_profile_dto and active_profile_dto.xai_length_constraint:
                    xai_budget = active_profile_dto.xai_length_constraint
                    xai_highlights_list = [
                        item.model_copy(update={"content": enforce_sentence_boundary_budget(item.content, xai_budget)})
                        if len(item.content) > xai_budget
                        else item
                        for item in xai_highlights_list
                    ]
            if usage:
                synth_cost += usage.cost_usd
                synth_tokens += usage.total_tokens

        row_expl_res = None
        if t_row and t_row.result():
            row_dto, usage = t_row.result()
            row_expl_res = row_dto
            if usage:
                synth_cost += usage.cost_usd
                synth_tokens += usage.total_tokens

        variance_expl = None
        if t_variance and t_variance.result():
            var_dto, usage = t_variance.result()
            variance_expl = var_dto.row_explanation
            if variance_expl and active_profile_dto and active_profile_dto.variance_length_constraint:
                if len(variance_expl) > active_profile_dto.variance_length_constraint:
                    variance_expl = enforce_sentence_boundary_budget(
                        variance_expl, active_profile_dto.variance_length_constraint
                    )
            if usage:
                synth_cost += usage.cost_usd
                synth_tokens += usage.total_tokens

        _raw_row_explanations = (
            {item.matrix_id: item.row_explanation for item in row_expl_res.explanations}
            if row_expl_res and row_expl_res.explanations
            else {}
        )

        cache_row_explanations = {}
        if matrices_to_explain:
            for m_dto in matrices_to_explain:
                real_id = m_dto.real_matrix_id
                alias_id = m_dto.matrix_id
                if not real_id:
                    continue

                if alias_id in _raw_row_explanations:
                    expl = _raw_row_explanations[alias_id]
                elif real_id in _raw_row_explanations:
                    expl = _raw_row_explanations[real_id]
                else:
                    # Fail-Fast protection: If the LLM omits a matrix, provide a fallback to prevent pipeline crash
                    expl = " - "

                if (
                    expl
                    and expl.strip() not in {"-", " - "}
                    and active_profile_dto
                    and active_profile_dto.row_explanation_length_constraint
                ):
                    if len(expl) > active_profile_dto.row_explanation_length_constraint:
                        expl = enforce_sentence_boundary_budget(
                            expl, active_profile_dto.row_explanation_length_constraint
                        )

                cache_row_explanations[real_id] = expl

        if variance_expl:
            cache_row_explanations["variance_validation"] = variance_expl

        cache = RenderedSynthesisCache(
            section_syntheses=sec_dict,
            row_explanations=cache_row_explanations,
            cited_sources=exec_dto.cited_sources if exec_dto else [],
            xai_highlights=xai_highlights_list,
            user_role=exec_dto.user_role if exec_dto else None,
            user_role_justification=exec_dto.user_role_justification if exec_dto else None,
            extension_metrics=ext_metrics,
        )

        # Add new synthesis to record
        current_syntheses = dict(execution.profile_syntheses) if execution.profile_syntheses is not None else {}
        pid: str = profile_id if profile_id is not None else "default"
        current_syntheses[pid] = cache

        prev_tokens = execution.cumulative_synthesis_tokens
        prev_cost = execution.cumulative_synthesis_cost
        new_cum_tokens = prev_tokens + synth_tokens
        new_cum_cost = prev_cost + synth_cost

        dag_cost = float(execution.dag_cost_usd)
        recovered_prompt_tokens = None
        recovered_comp_tokens = None
        recovered_cached_tokens = None
        recovered_reasoning_tokens = None

        if dag_cost == 0.0 and execution.cost_estimate > 0.0 and execution.cost_estimate > prev_cost:
            dag_cost = float(execution.cost_estimate - prev_cost)

        if dag_cost == 0.0 and execution.execution_trace_storage_path:
            try:
                storage_driver = get_storage_driver()
                blob_data = await storage_driver.read(execution.execution_trace_storage_path)
                if blob_data:
                    stored_trace = TypeAdapter(list[ErrorTraceEvent | TombstoneEvent | TraceEvent]).validate_json(
                        blob_data
                    )
                    rec_p = 0
                    rec_c = 0
                    rec_cac = 0
                    rec_r = 0
                    rec_cost = 0.0
                    for ev in stored_trace:
                        if ev.content:
                            try:
                                env = TraceEventMetadataEnvelope.model_validate(ev.content)
                                if env.step_metadata and env.step_metadata.token_usage:
                                    u = env.step_metadata.token_usage
                                    rec_p += u.prompt_tokens
                                    rec_c += u.completion_tokens
                                    rec_cac += u.cached_tokens
                                    rec_r += u.reasoning_tokens
                                    rec_cost += u.cost_usd
                            except ValidationError, ValueError:
                                pass
                    if rec_cost > 0.0:
                        dag_cost = rec_cost
                    if rec_p > 0 or rec_c > 0:
                        recovered_prompt_tokens = rec_p
                        recovered_comp_tokens = rec_c
                        recovered_cached_tokens = rec_cac
                        recovered_reasoning_tokens = rec_r
            except (OSError, UnicodeDecodeError, ValidationError, ValueError, KeyError) as err:
                logger.warning("[Task] Failed to recover DAG telemetry from storage blob: %s", err)

        total_cost = dag_cost + new_cum_cost

        dto = ExecutionUpdateDTO(
            profile_syntheses=current_syntheses,
            cumulative_synthesis_tokens=new_cum_tokens,
            cumulative_synthesis_cost=new_cum_cost,
            cost_estimate=total_cost,
        )
        if dag_cost > execution.dag_cost_usd:
            dto = dto.model_copy(update={"dag_cost_usd": dag_cost})
        if recovered_prompt_tokens is not None and execution.prompt_tokens == 0:
            dto = dto.model_copy(update={"prompt_tokens": recovered_prompt_tokens})
        if recovered_comp_tokens is not None and execution.completion_tokens == 0:
            dto = dto.model_copy(update={"completion_tokens": recovered_comp_tokens})
        if recovered_cached_tokens is not None and execution.cached_tokens == 0:
            dto = dto.model_copy(update={"cached_tokens": recovered_cached_tokens})
        if recovered_reasoning_tokens is not None and execution.reasoning_tokens == 0:
            dto = dto.model_copy(update={"reasoning_tokens": recovered_reasoning_tokens})

        await repo.update_execution(execution_id, dto)

        logger.info(f"[Task] Synthesis cached for {execution_id} (Profile: {profile_id})")

        # Now trigger the statically cached PDF job based on our newly cached synthesis
        await _update_render_status("Koostetaan tulosteita valmiiksi...")
        if redis:
            await redis.enqueue_job("generate_pdf_job", execution_id, accept_language, profile_id)

    except Exception as e:
        is_validation_err = isinstance(e, ValidationError)
        if not is_validation_err and isinstance(e, ExceptionGroup):
            val_errors, _ = e.split(ValidationError)
            if val_errors:
                is_validation_err = True

        if is_validation_err:
            msg = f"Strictness Fail-Fast: Invalid data payload during synthesis/pdf task: {str(e)}"
            logger.error(
                "[Task] %s: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            e = AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        else:
            logger.error(
                "[Task] Text Synthesis generation failed for %s. Cause: %s",
                execution_id,
                str(e),
                exc_info=True,
                extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )
        try:
            driver = await get_driver(get_settings())
            repo = UnifiedWorkflowRepository(driver)
            v_step_id = f"sys_render_{profile_id}"
            fail_step_states = None
            fail_steps = None
            exec_record_local = await repo.get_execution(execution_id, hydrate=False)
            if exec_record_local:
                exec_record_local = ExecutionRecord.model_validate(exec_record_local, strict=False)
                if v_step_id in exec_record_local.step_states:
                    old_state = exec_record_local.step_states[v_step_id]
                    updated_state = old_state.model_copy(
                        update={"status": ExecutionStatus.FAILED, "last_error": str(e)}
                    )
                    new_step_states = dict(exec_record_local.step_states)
                    new_step_states[v_step_id] = updated_state
                    new_steps = [
                        s.model_copy(update={"status": ExecutionStatus.FAILED, "last_error": str(e)})
                        if s.id == v_step_id
                        else s
                        for s in exec_record_local.steps
                    ]
                    exec_record_local = exec_record_local.model_copy(
                        update={"step_states": new_step_states, "steps": new_steps}
                    )
                fail_step_states = exec_record_local.step_states
                fail_steps = exec_record_local.steps

            await repo.update_execution(
                execution_id,
                ExecutionUpdateDTO(
                    status=ExecutionStatus.FAILED,
                    error=f"Render Profile Job failed: {str(e)}",
                    completed_at=datetime.now(UTC),
                    steps=fail_steps,
                    step_states=fail_step_states,
                ),
            )
        except Exception:  # noqa: QGR003 [REASON: Best-effort failure status DB update]
            logger.error(
                "[Task] Failed to update execution failure status",
                exc_info=True,
                extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            )
        raise e


# --- Lifecycle ---


async def startup(ctx: Any) -> None:
    """Called when the worker starts.

    Initializes dependencies and registers tasks.

    Args:
        ctx: Arq worker context to store initialized services.
    """
    setup_logging()
    configure_logfire()

    # VISUAL SEPARATOR FOR LOG READABILITY (File Only)
    logger.info("======================================================================")
    logger.info("   ARQ WORKER (V2.9) - STARTING UP")
    logger.info("======================================================================")

    # 1. PRINT TO CONSOLE (Minimal)
    logger.info("===================================================")
    logger.info("  CQ WORKER (V2.9) STARTED")
    logger.info("  -> Log: backend_debug.log (CHECK FOR DETAILS)")
    logger.info("===================================================")

    # 1. CRITICAL: Register Tasks & Hooks
    # Import all task modules and hooks here to trigger their decorators.
    # This ensures the Registries are populated before we try to run anything.
    logger.info(f"TaskRegistry initialized. Registered tasks: {list(TaskRegistry._tasks.keys())}")

    # 2. Initialize Dependencies
    # Repository (Firestore/TinyDB)
    driver = await get_driver(get_settings())
    repository = UnifiedWorkflowRepository(driver)

    # LLM Client (Instructor) - Singleton init
    llm_client = LLMClient()
    # Note: LLMClient is usually stateless or singleton, but good to init here.

    # 3. Initialize DAGExecutor (V2 SSOT Enforcer)
    compiler = PromptCompilerAdapter()
    rag_preflight = RAGPreflightService(
        workflow_repo=repository,
        system_repo=repository,
        prompt_compiler=compiler,
    )
    engine = DAGExecutor(
        exec_repo=repository,
        workflow_repo=repository,
        comp_repo=repository,
        prompt_block_repo=repository,
        output_profile_repo=repository,
        identity_repo=repository,
        audit_repo=repository,
        system_repo=repository,
        prompt_compiler=compiler,
        rag_preflight=rag_preflight,
    )

    # 4. Store in Context
    ctx["engine"] = engine
    ctx["repository"] = repository
    ctx["llm_client"] = llm_client

    logger.info("Worker services initialized.")


async def shutdown(ctx: Any) -> None:
    """Called when the worker shuts down.

    Args:
        ctx: Arq worker context.
    """
    logger.info("Arq Worker shutting down.")


async def health_check(ctx: Any) -> str:
    """Simple health check task.

    Args:
        ctx: Arq worker context.

    Returns:
        String 'OK' on success.
    """
    return "OK"


class WorkerSettings:
    """Configuration for the Arq worker."""

    functions: Sequence[WorkerCoroutine | Function] = [
        health_check,
        execute_workflow_job,
        generate_pdf_job,
        render_profile_job,
    ]
    cron_jobs: Sequence[Any] | None = None
    on_startup: StartupShutdown | None = startup
    on_shutdown: StartupShutdown | None = shutdown

    redis_settings: RedisSettings = RedisSettings(
        host=settings.redis_host,
        port=settings.redis_port,
    )
    job_timeout: int = settings.worker_job_timeout
    max_jobs: int = get_settings().max_concurrent_workflows
