"""Execution Worker for Quorum Workflow Execution.

Phase 1 Heavy LLM Execution & DAG Orchestration worker.
Decoupled from Phase 2/3 rendering per Tripartite Pipeline Architecture.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from datetime import UTC, datetime
from typing import Any

import opentelemetry.trace as trace
from pydantic import TypeAdapter, ValidationError

from backend_v2.core.telemetry import get_tracer, use_trace_context
from backend_v2.exceptions import AppException, ErrorCodes, WorkflowNotFoundError
from backend_v2.models.core_base import generate_opaque_id
from backend_v2.models.domain.execution import ExecutionRecord, ExecutionStep, ExecutionSummarySnapshot
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.hook_delta import WorkerJobResultDTO
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.step_telemetry import StepTelemetryEntryDTO
from backend_v2.models.dtos.telemetry import TraceContextCarrierDTO
from backend_v2.models.dtos.trace import ExecutionUpdateDTO, StepTraceMetadataDTO, TraceEventMetadataEnvelope
from backend_v2.models.enums import EntityPrefix, ExecutionStatus
from backend_v2.models.state import ErrorTraceEvent, TombstoneEvent, TraceEvent
from backend_v2.services.localization import set_language
from backend_v2.services.storage import get_storage_driver
from backend_v2.settings import get_settings

__all__ = ["execute_workflow_job"]

logger = logging.getLogger(__name__)


def _format_dlq_failure(
    execution_id: str | None = None,
    workflow_id: str | None = None,
) -> WorkerJobResultDTO:
    """Format Dead Letter Queue failure payload.

    Args:
        execution_id: Optional ID of the execution record.
        workflow_id: Optional ID of the workflow configuration.

    Returns:
        WorkerJobResultDTO indicating DLQ failure status.
    """
    return WorkerJobResultDTO(
        status="FAILED/DLQ",
        execution_id=execution_id,
        workflow_id=workflow_id,
        duration_ms=0,
    )


def _record_dlq_error(err_msg: str) -> None:
    """Log DLQ error details when failure status update fails.

    Args:
        err_msg: Error message describing the update failure.
    """
    logger.error(
        "[ExecutionWorker] %s",
        err_msg,
        exc_info=True,
        extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
    )


def _resolve_workflow_inputs(
    inputs: ExecutionInputsDTO | WorkflowInputs,
    organization_id: str | None,
    user_id: str | None,
) -> WorkflowInputs:
    """Resolve and normalize polymorphic workflow inputs into a WorkflowInputs model.

    Args:
        inputs: Strongly typed ExecutionInputsDTO or WorkflowInputs instance.
        organization_id: Optional organization ID context.
        user_id: Optional user ID context.

    Returns:
        Normalized WorkflowInputs instance.

    Raises:
        ValidationError: If raw inputs fail TypeAdapter validation.
    """
    resolved_inputs = (
        inputs
        if isinstance(inputs, (WorkflowInputs, ExecutionInputsDTO))
        else TypeAdapter(WorkflowInputs | ExecutionInputsDTO).validate_python(inputs)
    )
    if isinstance(resolved_inputs, WorkflowInputs):
        return resolved_inputs

    merged_dynamic = dict(resolved_inputs.dynamic_inputs)
    merged_dynamic.update(resolved_inputs.raw_inputs)
    org_id = organization_id
    if not org_id and "organization_id" in resolved_inputs.raw_inputs:
        raw_dto_org = resolved_inputs.raw_inputs["organization_id"]
        if isinstance(raw_dto_org, str):
            org_id = raw_dto_org
    u_id = user_id
    if not u_id and "user_id" in resolved_inputs.raw_inputs:
        raw_dto_u = resolved_inputs.raw_inputs["user_id"]
        if isinstance(raw_dto_u, str):
            u_id = raw_dto_u
    return WorkflowInputs(
        organization_id=org_id,
        user_id=u_id,
        dynamic_inputs=merged_dynamic,
    )


async def _fetch_and_validate_workflow(repository: Any, workflow_id: str) -> Workflow:
    """Fetch workflow blueprint from repository and validate into Workflow model.

    Args:
        repository: Initialized workflow repository instance.
        workflow_id: Opaque Stripe ID of the workflow.

    Returns:
        Validated Workflow domain model.

    Raises:
        WorkflowNotFoundError: If the workflow does not exist in the repository.
        ValidationError: If the stored workflow fails Pydantic schema validation.
    """
    workflow_dict = await repository.get_workflow(workflow_id)
    if not workflow_dict:
        missing_msg = f"Workflow '{workflow_id}' not found."
        logger.error(
            "[Worker] %s: %s",
            ErrorCodes.RESOURCE_NOT_FOUND.name,
            missing_msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "workflow_id": workflow_id},
        )
        raise WorkflowNotFoundError(workflow_id)
    return Workflow.model_validate(workflow_dict)


async def _fetch_and_validate_execution(
    repository: Any,
    exec_id: str,
    existing_record: ExecutionRecord | None,
) -> ExecutionRecord:
    """Fetch and validate the active execution record and its target locale.

    Args:
        repository: Initialized workflow repository instance.
        exec_id: Opaque Stripe ID of the execution record.
        existing_record: Pre-fetched ExecutionRecord if already loaded for trace carrier.

    Returns:
        Validated ExecutionRecord with active target_locale.

    Raises:
        AppException: With ErrorCodes.RESOURCE_NOT_FOUND if execution record is missing,
            or ErrorCodes.CONFIGURATION_ERROR if target_locale is missing.
    """
    exec_record = existing_record
    if exec_record is None:
        execution_data = await repository.get_execution(exec_id)
        if not execution_data:
            msg = f"Execution {exec_id} not found in DB before execution! Cannot resolve dynamic strictness."
            logger.error(
                "[Job] %s: %s",
                ErrorCodes.RESOURCE_NOT_FOUND.name,
                msg,
                exc_info=True,
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value, "execution_id": exec_id},
            )
            raise AppException(
                message=msg,
                status_code=500,
                details={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.value},
            )
        exec_record = (
            execution_data
            if isinstance(execution_data, ExecutionRecord)
            else ExecutionRecord.model_validate(execution_data, strict=False)
        )

    if not exec_record.target_locale:
        msg = f"Strict Fail-Fast Enforced: Execution '{exec_record.id}' is missing mandatory 'target_locale'."
        logger.error(
            "[Worker] %s: %s",
            ErrorCodes.CONFIGURATION_ERROR.name,
            msg,
            exc_info=True,
            extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.value, "execution_id": exec_record.id},
        )
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )
    return exec_record


async def _load_trace_events(
    updated_exec_record: ExecutionRecord,
) -> list[ErrorTraceEvent | TombstoneEvent | TraceEvent]:
    """Load execution trace events, hydrating from offloaded blob storage if present.

    Args:
        updated_exec_record: ExecutionRecord returned from GraphEngine execution.

    Returns:
        Complete list of trace events for FinOps and telemetry aggregation.

    Raises:
        AppException: With ErrorCodes.INTERNAL_SERVER_ERROR if offloaded trace reading fails.
    """
    trace_events = list(updated_exec_record.execution_trace)
    if not updated_exec_record.execution_trace_storage_path:
        return trace_events

    try:
        storage_driver = get_storage_driver()
        blob_data = await storage_driver.read(updated_exec_record.execution_trace_storage_path)
        if blob_data:
            offloaded_events = TypeAdapter(list[ErrorTraceEvent | TombstoneEvent | TraceEvent]).validate_json(blob_data)
            if len(offloaded_events) >= len(trace_events):
                return offloaded_events
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
    return trace_events


def _extract_step_trace_metadata(
    event: ErrorTraceEvent | TombstoneEvent | TraceEvent,
) -> StepTraceMetadataDTO | None:
    """Extract validated StepTraceMetadataDTO from a trace event content payload.

    Args:
        event: TraceEvent, ErrorTraceEvent, or TombstoneEvent instance.

    Returns:
        Validated StepTraceMetadataDTO if present on the event, else None.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if step_metadata is corrupted.
    """
    if isinstance(event.content, TraceEventMetadataEnvelope):
        return event.content.step_metadata
    if type(event.content) is dict:
        try:
            envelope = TraceEventMetadataEnvelope.model_validate(event.content)
            return envelope.step_metadata
        except (ValidationError, ValueError) as err:
            logger.error(
                "[Worker] Corrupted StepTraceMetadataDTO in execution trace: %s",
                err,
                exc_info=True,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
            raise AppException(
                message=f"Corrupted StepTraceMetadataDTO in execution trace: {err}",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from err
    return None


def _merge_step_telemetry_entry(
    step_telemetry: dict[str, StepTelemetryEntryDTO],
    step_id: str,
    step_meta: StepTraceMetadataDTO,
) -> None:
    """Accumulate per-step token and cost telemetry into the step_telemetry mapping.

    Args:
        step_telemetry: Mutable mapping of step_id to StepTelemetryEntryDTO.
        step_id: Step identifier from the trace event.
        step_meta: Validated StepTraceMetadataDTO containing usage and model info.
    """
    usage = step_meta.token_usage
    if usage is not None:
        p_tokens = usage.prompt_tokens
        comp_tokens = usage.completion_tokens
        cac_tokens = usage.cached_tokens
        reas_tokens = usage.reasoning_tokens
        c_cost = usage.cost_usd
    else:
        p_tokens = 0
        comp_tokens = 0
        cac_tokens = 0
        reas_tokens = 0
        c_cost = 0.0

    if step_id not in step_telemetry:
        step_telemetry[step_id] = StepTelemetryEntryDTO(
            model_strategy=step_meta.model_strategy,
            physical_model=step_meta.physical_model,
            system_fingerprint=step_meta.system_fingerprint,
            prompt_tokens=p_tokens,
            completion_tokens=comp_tokens,
            cached_tokens=cac_tokens,
            reasoning_tokens=reas_tokens,
            cost_usd=c_cost,
            chunk_count=step_meta.chunk_size,
        )
        return

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
            "chunk_count": prev.chunk_count + step_meta.chunk_size,
        }
    )


def _reconcile_execution_steps(
    updated_exec_record: ExecutionRecord,
    step_telemetry: dict[str, StepTelemetryEntryDTO],
) -> list[ExecutionStep]:
    """Reconcile ExecutionStep statuses and attach aggregated step telemetry.

    Args:
        updated_exec_record: ExecutionRecord returned from GraphEngine execution.
        step_telemetry: Mapping of step_id to aggregated StepTelemetryEntryDTO.

    Returns:
        List of updated ExecutionStep instances.
    """
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
    updated_steps: list[ExecutionStep] = []
    for st in existing_steps:
        st_state = None
        if st.id in updated_exec_record.step_states:
            st_state = updated_exec_record.step_states[st.id]
        actual_status = st_state.status if st_state else st.status
        last_err = st_state.last_error if st_state else st.last_error
        msg_code = st_state.message_code if st_state else st.message_code
        scorecard = st_state.scorecard_atoms if st_state else st.scorecard_atoms
        actual_progress = st_state.progress if st_state else st.progress
        actual_warning = st_state.has_warning if st_state else st.has_warning

        tel = None
        if st.id in step_telemetry:
            tel = step_telemetry[st.id]
        if tel:
            updated_steps.append(
                st.model_copy(
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
            )
        else:
            updated_steps.append(
                st.model_copy(
                    update={
                        "status": actual_status,
                        "last_error": last_err,
                        "message_code": msg_code,
                        "scorecard_atoms": scorecard,
                        "progress": actual_progress,
                        "has_warning": actual_warning,
                    }
                )
            )
    return updated_steps


async def _finalize_and_persist_execution(
    repository: Any,
    redis: Any,
    exec_id: str,
    workflow_def: Workflow,
    updated_exec_record: ExecutionRecord,
    start_time: datetime,
) -> int:
    """Aggregate FinOps trace telemetry, persist PASSED execution record, and notify Redis.

    Args:
        repository: Initialized workflow repository instance.
        redis: Optional Redis client/pool for pub/sub completion notification.
        exec_id: Opaque Stripe ID of the execution record.
        workflow_def: Validated Workflow domain model.
        updated_exec_record: ExecutionRecord returned from GraphEngine execution.
        start_time: UTC timestamp when workflow execution began.

    Returns:
        Execution duration in milliseconds.

    Raises:
        AppException: If offloaded trace reading or metadata validation fails.
    """
    trace_events = await _load_trace_events(updated_exec_record)
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
        step_meta = _extract_step_trace_metadata(event)
        if step_meta is None:
            continue
        usage = step_meta.token_usage
        t_tokens = 0
        if usage is not None:
            total_prompt_tokens += usage.prompt_tokens
            total_completion_tokens += usage.completion_tokens
            total_cached_tokens += usage.cached_tokens
            total_reasoning_tokens += usage.reasoning_tokens
            total_cost_usd += usage.cost_usd
            t_tokens = usage.total_tokens

        curr_model_tokens = 0
        if step_meta.model_strategy in models_used:
            curr_model_tokens = models_used[step_meta.model_strategy]
        models_used[step_meta.model_strategy] = curr_model_tokens + t_tokens
        _merge_step_telemetry_entry(step_telemetry, event.step_name, step_meta)

    updated_steps = _reconcile_execution_steps(updated_exec_record, step_telemetry)
    settings = get_settings()
    summary_snapshot = ExecutionSummarySnapshot(
        strictness_level=workflow_def.default_strictness_level,
        is_ensemble_run=(workflow_def.default_strictness_level >= 3),
        is_degraded=is_degraded,
        system_concurrency_snapshot={
            "LLM_MAX_CHUNK_SIZE": settings.llm_max_chunk_size,
            "SCHEMA_MAX_EVALUATIONS": settings.schema_max_evaluations,
            "SCHEMA_MAX_CHUNK_RECORDS": settings.schema_max_chunk_records,
            "MATRIX_SAMPLING_LIMIT": settings.matrix_sampling_limit,
        },
    )

    combined_cost_estimate = total_cost_usd + updated_exec_record.cumulative_synthesis_cost
    duration_ms = int((datetime.now(UTC) - start_time).total_seconds() * 1000)

    await repository.update_execution(
        exec_id,
        ExecutionUpdateDTO(
            status=ExecutionStatus.PASSED,
            completed_at=datetime.now(UTC),
            steps=updated_steps,
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
        workflow_def.id,
        exec_id,
    )
    if redis:
        with contextlib.suppress(OSError, RuntimeError, ConnectionError):
            await redis.publish(f"execution:{exec_id}", ExecutionStatus.PASSED.value)
    return duration_ms


async def _persist_failed_execution(
    repository: Any,
    exec_id: str,
    error_msg: str,
    failure_label: str,
) -> None:
    """Persist ExecutionStatus.FAILED on the execution record with DLQ error resilience.

    Args:
        repository: Initialized workflow repository instance.
        exec_id: Opaque Stripe ID of the execution record.
        error_msg: Error message describing the failure or cancellation.
        failure_label: Contextual label ('failure' or 'cancellation') for DLQ logging.
    """
    try:
        await repository.update_execution(
            exec_id,
            ExecutionUpdateDTO(
                status=ExecutionStatus.FAILED,
                error=error_msg,
                completed_at=datetime.now(UTC),
            ),
        )
    except (OSError, ValidationError, ValueError, KeyError, RuntimeError) as update_err:
        _record_dlq_error(f"Failed to update execution {failure_label} status: {update_err}")


async def execute_workflow_job(
    ctx: Any,
    workflow_id: str,
    inputs: ExecutionInputsDTO | WorkflowInputs,
    execution_id: str | None = None,
    organization_id: str | None = None,
    user_id: str | None = None,
) -> WorkerJobResultDTO:
    """Background job to execute a workflow using GraphEngine.

    Performs Phase 1 analytical execution, updates the execution record to PASSED,
    and terminates without auto-enqueuing downstream report or presentation jobs.

    Args:
        ctx: Arq worker context containing initialized services.
        workflow_id: ID of the workflow configuration to run.
        inputs: Strongly typed execution inputs DTO for the workflow.
        execution_id: ID of the execution record to update.
        organization_id: Organization ID context.
        user_id: User ID context.

    Returns:
        WorkerJobResultDTO containing execution status, ID, and duration.

    Raises:
        AppException: With ErrorCodes.RESOURCE_NOT_FOUND if workflow or execution is missing,
            ErrorCodes.CONFIGURATION_ERROR if target_locale is missing,
            ErrorCodes.INTERNAL_SERVER_ERROR if trace hydration fails,
            or ErrorCodes.VALIDATION_FAILED if trace metadata is corrupted.
    """
    logger.info(
        "[Job] Executing workflow: %s (Execution ID: %s, Org: %s, User: %s)",
        workflow_id,
        execution_id,
        organization_id,
        user_id,
    )

    engine = ctx["engine"]
    repository = ctx["repository"]
    if execution_id:
        exec_id = execution_id
    else:
        exec_id = generate_opaque_id(EntityPrefix.EXECUTION)

    carrier: TraceContextCarrierDTO | None = None
    exec_record: ExecutionRecord | None = None
    if execution_id:
        raw_exec = await repository.get_execution(exec_id)
        if isinstance(raw_exec, ExecutionRecord):
            exec_record = raw_exec
            if exec_record.metadata is not None:
                carrier = exec_record.metadata.telemetry

    tracer = get_tracer(__name__)
    with use_trace_context(carrier), tracer.start_as_current_span("execution.worker_process") as worker_span:
        worker_span.set_attribute("execution.id", exec_id)
        worker_span.set_attribute("workflow.id", workflow_id)
        if organization_id:
            worker_span.set_attribute("organization.id", organization_id)
        if user_id:
            worker_span.set_attribute("user.id", user_id)
        if carrier is None:
            worker_span.set_attribute("telemetry.orphan_execution", True)

        inputs_obj = _resolve_workflow_inputs(inputs, organization_id, user_id)

        try:
            workflow_def = await _fetch_and_validate_workflow(repository, workflow_id)
            start_time = datetime.now(UTC)
            exec_record = await _fetch_and_validate_execution(repository, exec_id, exec_record)
            set_language(exec_record.target_locale)

            redis = None
            if "redis" in ctx:
                redis = ctx["redis"]
            updated_exec_record = await engine.execute_workflow(
                execution_id=exec_id,
                workflow=workflow_def,
                raw_inputs=inputs_obj,
                strictness_level=workflow_def.default_strictness_level,
                lexical_strictness_level=workflow_def.default_lexical_strictness_level,
                arq_pool=redis,
            )

            duration_ms = await _finalize_and_persist_execution(
                repository=repository,
                redis=redis,
                exec_id=exec_id,
                workflow_def=workflow_def,
                updated_exec_record=updated_exec_record,
                start_time=start_time,
            )
            return WorkerJobResultDTO(
                status="COMPLETED",
                execution_id=exec_id,
                workflow_id=workflow_id,
                duration_ms=duration_ms,
            )

        except (AppException, ValidationError, OSError, RuntimeError, ValueError, KeyError) as e:
            worker_span.record_exception(e)
            worker_span.set_status(trace.StatusCode.ERROR, str(e))
            if not isinstance(e, AppException):
                msg = f"Workflow {workflow_id} failed: {e}"
                logger.error(
                    "[Worker] %s",
                    msg,
                    exc_info=True,
                    extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                )
                e = AppException(
                    message=msg,
                    status_code=500,
                    details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                )
            await _persist_failed_execution(repository, exec_id, str(e), "failure")
            return _format_dlq_failure(execution_id=exec_id, workflow_id=workflow_id)
        except asyncio.CancelledError:
            worker_span.set_status(trace.StatusCode.ERROR, "Cancelled")
            logger.warning("[Job] Workflow %s CANCELLED (Timeout/Shutdown). Execution ID: %s", workflow_id, exec_id)
            await _persist_failed_execution(
                repository,
                exec_id,
                "Task execution was cancelled or timed out.",
                "cancellation",
            )
            return _format_dlq_failure(execution_id=exec_id, workflow_id=workflow_id)
