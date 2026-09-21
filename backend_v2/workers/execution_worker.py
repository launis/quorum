"""Execution Worker for Quorum Workflow Execution.

Phase 1 Heavy LLM Execution & DAG Orchestration worker.
Decoupled from Phase 2/3 rendering per Tripartite Pipeline Architecture.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import uuid
from datetime import UTC, datetime
from typing import Any

import logfire
from pydantic import TypeAdapter, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes, WorkflowNotFoundError
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep, ExecutionSummarySnapshot
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.step_telemetry import StepTelemetryEntryDTO
from backend_v2.models.dtos.trace import ExecutionUpdateDTO, StepTraceMetadataDTO, TraceEventMetadataEnvelope
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent
from backend_v2.services.localization import set_language
from backend_v2.services.storage import get_storage_driver
from backend_v2.settings import get_settings

__all__ = ["execute_workflow_job"]

logger = logging.getLogger(__name__)


def _format_dlq_failure() -> dict[str, str]:
    """Helper to format Dead Letter Queue failure payload."""
    return {"_dlq_status": "FAILED/DLQ"}


def _record_dlq_error(err_msg: str) -> None:
    """Log DLQ error details when failure status update fails."""
    logger.error(
        "[ExecutionWorker] %s",
        err_msg,
        exc_info=True,
        extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
    )


async def execute_workflow_job(
    ctx: Any,
    workflow_id: str,
    inputs: dict[str, Any],
    execution_id: str | None = None,
    organization_id: str | None = None,
    user_id: str | None = None,
) -> dict[str, Any]:
    """Background job to execute a workflow using GraphEngine.

    Performs Phase 1 analytical execution, updates the execution record to PASSED,
    and terminates without auto-enqueuing downstream report or presentation jobs.

    Args:
        ctx: Arq worker context containing initialized services.
        workflow_id: ID of the workflow configuration to run.
        inputs: Raw input arguments for the workflow.
        execution_id: ID of the execution record to update.
        organization_id: Organization ID context.
        user_id: User ID context.

    Returns:
        The final workflow execution summary dictionary.

    Raises:
        AppException: Inherited from execution logic.
    """
    msg = (
        f"[Job] Executing workflow: {workflow_id} "
        f"(Execution ID: {execution_id}, Org: {organization_id}, User: {user_id})"
    )
    logger.info(msg)

    # LOGFIRE INTEGRATION: Bind execution_id to this trace context
    span_execution_id = execution_id or "unknown"
    with logfire.span("execute_workflow_job", tags={"execution_id": span_execution_id}):
        if organization_id and "organization_id" not in inputs:
            inputs["organization_id"] = organization_id

        if user_id and "user_id" not in inputs:
            inputs["user_id"] = user_id

        engine = ctx["engine"]
        repository = ctx["repository"]

        exec_id = execution_id or f"exe_{uuid.uuid4().hex}"

        try:
            workflow_dict = await repository.get_workflow(workflow_id)
            if not workflow_dict:
                raise WorkflowNotFoundError(workflow_id)

            workflow_def = Workflow.model_validate(workflow_dict)
            start_time = datetime.now(UTC)
            inputs_obj = WorkflowInputs.model_validate(inputs)

            execution_data = await repository.get_execution(exec_id)
            if not execution_data:
                msg = f"Execution {exec_id} not found in DB before execution! Cannot resolve dynamic strictness."
                logger.error("[Job] %s", msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value}
                )

            exec_record = ExecutionRecord.model_validate(execution_data, strict=False)
            strictness_level: int = workflow_def.default_strictness_level

            if not exec_record.target_locale:
                msg = f"Strict Fail-Fast Enforced: Execution '{exec_record.id}' is missing mandatory 'target_locale'."
                logger.error("[Worker] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                )
            set_language(exec_record.target_locale)

            redis = ctx["redis"] if "redis" in ctx else None
            updated_exec_record = await engine.execute_workflow(
                execution_id=exec_id,
                workflow=workflow_def,
                raw_inputs=inputs_obj,
                strictness_level=strictness_level,
                arq_pool=redis,
            )

            if exec_id:

                def _has_step_metadata(evt: ErrorTraceEvent | TombstoneEvent | TraceEvent) -> bool:
                    if not evt.content:
                        return False
                    if isinstance(evt.content, TraceEventMetadataEnvelope):
                        return evt.content.step_metadata is not None
                    if type(evt.content) is dict:
                        return "_step_metadata" in evt.content or "step_metadata" in evt.content
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
                        trace_path = updated_exec_record.execution_trace_storage_path
                        msg = f"Failed to hydrate offloaded trace from '{trace_path}' for telemetry: {err}"
                        logger.error(
                            "[ExecutionWorker] %s: %s",
                            ErrorCodes.INTERNAL_SERVER_ERROR.name,
                            msg,
                            extra={
                                "error_code": ErrorCodes.INTERNAL_SERVER_ERROR.name,
                                "execution_id": updated_exec_record.id,
                                "path": updated_exec_record.execution_trace_storage_path,
                            },
                            exc_info=True,
                        )
                        raise AppException(
                            message=msg,
                            status_code=500,
                            details={
                                "error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value,
                                "execution_id": updated_exec_record.id,
                            },
                        ) from err

                models_used: dict[str, int] = {}
                if updated_exec_record.models_used:
                    models_used = updated_exec_record.models_used.copy()
                step_telemetry: dict[str, StepTelemetryEntryDTO] = {}
                total_cost_usd = 0.0
                total_prompt_tokens = 0
                total_completion_tokens = 0
                total_cached_tokens = 0
                total_reasoning_tokens = 0
                is_degraded = False

                for event in trace_events:
                    if event.event_type in ("error", "dlq_routed"):
                        is_degraded = True
                    step_meta: StepTraceMetadataDTO | None = None
                    if isinstance(event.content, TraceEventMetadataEnvelope):
                        step_meta = event.content.step_metadata
                    elif type(event.content) is dict and (
                        "_step_metadata" in event.content or "step_metadata" in event.content
                    ):
                        try:
                            step_meta = TraceEventMetadataEnvelope.model_validate(event.content).step_metadata
                        except (ValidationError, ValueError) as err:
                            logger.error(
                                "[Worker] Corrupted TraceEventMetadataEnvelope in execution trace: %s",
                                err,
                                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
                            )
                            raise AppException(
                                message=f"Corrupted TraceEventMetadataEnvelope in execution trace: {err}",
                                status_code=500,
                                details={"error_code": ErrorCodes.VALIDATION_FAILED},
                            ) from err
                    if step_meta is None:
                        continue
                    usage = step_meta.token_usage

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

                    curr_model_tokens = 0
                    if model_strategy in models_used:
                        curr_model_tokens = models_used[model_strategy]
                    models_used[model_strategy] = curr_model_tokens + t_tokens

                    step_id = event.step_name
                    if step_id not in step_telemetry:
                        step_telemetry[step_id] = StepTelemetryEntryDTO(
                            model_strategy=model_strategy,
                            physical_model=step_meta.physical_model,
                            system_fingerprint=step_meta.system_fingerprint,
                            prompt_tokens=p_tokens,
                            completion_tokens=comp_tokens,
                            cached_tokens=cac_tokens,
                            reasoning_tokens=reas_tokens,
                            cost_usd=c_cost,
                            chunk_count=chunk_size,
                        )
                    else:
                        prev = step_telemetry[step_id]
                        phys_model = prev.physical_model or step_meta.physical_model
                        sys_fp = prev.system_fingerprint or step_meta.system_fingerprint
                        step_telemetry[step_id] = prev.model_copy(
                            update={
                                "physical_model": phys_model,
                                "system_fingerprint": sys_fp,
                                "prompt_tokens": prev.prompt_tokens + p_tokens,
                                "completion_tokens": prev.completion_tokens + comp_tokens,
                                "cached_tokens": prev.cached_tokens + cac_tokens,
                                "reasoning_tokens": prev.reasoning_tokens + reas_tokens,
                                "cost_usd": prev.cost_usd + c_cost,
                                "chunk_count": prev.chunk_count + chunk_size,
                            }
                        )

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
                            progress=v.progress,
                            has_warning=v.has_warning,
                        )
                        for k, v in updated_exec_record.step_states.items()
                    ]
                )
                for st in existing_steps:
                    st_state = (
                        updated_exec_record.step_states[st.id] if st.id in updated_exec_record.step_states else None
                    )
                    actual_status = st_state.status if st_state else st.status
                    last_err = st_state.last_error if st_state else st.last_error
                    msg_code = st_state.message_code if st_state else st.message_code
                    scorecard = st_state.scorecard_atoms if st_state else st.scorecard_atoms
                    actual_progress = st_state.progress if st_state else st.progress
                    actual_warning = st_state.has_warning if st_state else st.has_warning

                    tel = step_telemetry[st.id] if st.id in step_telemetry else None
                    if tel:
                        updated_st = st.model_copy(
                            update={
                                "status": actual_status,
                                "last_error": last_err,
                                "message_code": msg_code,
                                "scorecard_atoms": scorecard,
                                "progress": actual_progress,
                                "has_warning": actual_warning,
                                "model_strategy": tel.model_strategy,
                                "physical_model": tel.physical_model,
                                "system_fingerprint": tel.system_fingerprint,
                                "prompt_tokens": tel.prompt_tokens,
                                "completion_tokens": tel.completion_tokens,
                                "cached_tokens": tel.cached_tokens,
                                "reasoning_tokens": tel.reasoning_tokens,
                                "cost_usd": tel.cost_usd,
                                "chunk_count": max(1, tel.chunk_count),
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
                                "progress": actual_progress,
                                "has_warning": actual_warning,
                            }
                        )
                        updated_steps.append(updated_st)

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

                # Phase 1 Sovereignty: Persist ExecutionStatus.PASSED immediately.
                # Eradicate worker-to-worker auto-enqueuing of render_profile_job.
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
                logger.info(
                    "[Job] Workflow %s execution %s completed Phase 1 DAG (Status: PASSED)",
                    workflow_id,
                    exec_id,
                )

                if redis:
                    with contextlib.suppress(Exception):
                        await redis.publish(f"execution:{exec_id}", ExecutionStatus.PASSED.value)

            final_duration = duration_ms if exec_id else 0
            return {
                "status": "COMPLETED",
                "execution_id": exec_id,
                "workflow_id": workflow_id,
                "duration_ms": final_duration,
            }

        except (AppException, ValidationError, OSError, RuntimeError, ValueError, KeyError) as e:
            if not isinstance(e, AppException):
                msg = f"Workflow {workflow_id} failed: {e}"
                logger.error(
                    "[Worker] %s", msg, exc_info=True, extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                )
                e = AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
                )

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
                except (OSError, ValidationError, ValueError, KeyError, RuntimeError) as update_err:
                    update_msg = f"Failed to update execution failure status: {update_err}"
                    _record_dlq_error(update_msg)
            return _format_dlq_failure()
        except asyncio.CancelledError:
            logger.warning("[Job] Workflow %s CANCELLED (Timeout/Shutdown). Execution ID: %s", workflow_id, exec_id)
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
                except (OSError, ValidationError, ValueError, KeyError, RuntimeError) as update_err:
                    update_msg = f"Failed to update execution cancellation status: {update_err}"
                    _record_dlq_error(update_msg)
            return _format_dlq_failure()
