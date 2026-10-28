"""Step strategy context preparation and isolated DAG step execution wrapper stage."""

from __future__ import annotations

import contextlib
import logging
import sys
from collections.abc import Callable
from typing import Any

import opentelemetry.trace as otel_trace
from pydantic import TypeAdapter, ValidationError
from tenacity import AsyncRetrying, before_sleep_log, retry_if_exception, stop_after_attempt, wait_exponential

from backend_v2.core.telemetry import get_tracer
from backend_v2.exceptions import AppException, ErrorCodes, WorkflowExecutionError
from backend_v2.llm.provider import _is_transient_llm_error
from backend_v2.models.domain.step import Step
from backend_v2.models.dtos.causal_discovery import CausalGraphPayloadDTO
from backend_v2.models.dtos.node_execution import StepOutputContentDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent, TraceEvent
from backend_v2.services.orchestrator.causal_cohesion_evaluator import CausalCohesionEvaluator
from backend_v2.services.orchestrator.dag_executor.causal_tda_fusion import transform_causal_nodes_to_atoms
from backend_v2.services.orchestrator.dag_executor.execution_committer import ExecutionCommitter
from backend_v2.services.orchestrator.dag_executor.node_executor import NodeExecutor
from backend_v2.services.orchestrator.dag_executor.wave_orchestrator_stage import finalize_step_output_and_commit
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    WorkflowExecutionState,
    dlq_handle_progress_commit_error,
    dlq_record_step_failure,
    safe_commit_execution_state,
)
from backend_v2.services.orchestrator.matrix_reducer import MatrixReducer
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)
__all__ = ["execute_dag_step_wrapper", "prepare_step_strategy_context"]
_DAG_EXECUTOR_MODULE = "backend_v2.services.orchestrator.dag_executor"


def _resolve_matrix_reducer() -> Any:
    """Resolve MatrixReducer dynamically from dag_executor module when loaded for test patch compatibility.

    Returns:
        MatrixReducer class reference from the loaded facade module or local import.
    """
    if _DAG_EXECUTOR_MODULE in sys.modules:
        return sys.modules[_DAG_EXECUTOR_MODULE].MatrixReducer
    return MatrixReducer


def _resolve_settings() -> Any:
    """Resolve settings dynamically from dag_executor.get_settings when loaded for test patch compatibility.

    Returns:
        Active Settings instance resolved via the facade module or global settings getter.
    """
    getter = sys.modules[_DAG_EXECUTOR_MODULE].get_settings if _DAG_EXECUTOR_MODULE in sys.modules else get_settings
    return getter()


def _parse_causal_graph_candidate(raw_candidate: Any, err_prefix: str) -> CausalGraphPayloadDTO:
    """Validate and hydrate a CausalGraphPayloadDTO from trace output or snapshot payload.

    Args:
        raw_candidate: Raw trace event content, StepOutputContentDTO, or CausalGraphPayloadDTO instance.
        err_prefix: Contextual error message prefix logged and raised on validation failure.

    Returns:
        Validated CausalGraphPayloadDTO instance.

    Raises:
        AppException: Triggered with VALIDATION_FAILED when payload schema validation fails.
    """
    try:
        unwrapped = raw_candidate.data if isinstance(raw_candidate, StepOutputContentDTO) else raw_candidate
        payload = unwrapped["graph"] if type(unwrapped) is dict and "graph" in unwrapped else unwrapped
        if isinstance(payload, CausalGraphPayloadDTO):
            return payload
        return TypeAdapter(CausalGraphPayloadDTO).validate_python(payload, strict=False)
    except ValidationError as err:
        logger.error(
            "[DAGExecutor] %s: %s: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            err_prefix,
            err,
            exc_info=True,
        )
        raise AppException(
            message=f"{err_prefix}: {err}",
            status_code=500,
            details={"error_code": ErrorCodes.VALIDATION_FAILED},
        ) from err


async def prepare_step_strategy_context(
    state: WorkflowExecutionState,
    step_id: str,
) -> tuple[CausalGraphPayloadDTO | None, Step | None]:
    """Prepare upstream causal discovery atoms and pre-synthesis MatrixReducer state for a DAG step.

    Args:
        state: Active WorkflowExecutionState containing execution record, projector, and locks.
        step_id: Canonical Opaque Stripe ID of the step being prepared.

    Returns:
        Two-element tuple of (resolved upstream CausalGraphPayloadDTO or None, Step blueprint definition or None).

    Raises:
        AppException: Triggered with VALIDATION_FAILED if causal_source_step_id is invalid or graph
            validation fails, or CAUSAL_DISCOVERY_DATA_STARVATION if upstream causal step did not pass
            or produced zero proposition nodes.
        WorkflowExecutionError: Triggered with WORKFLOW_EXECUTION_FAILED if pre-synthesis MatrixReducer fails.
    """
    step_obj = state.steps_by_id[step_id]
    _update_lock = state.update_lock
    upstream_graph: CausalGraphPayloadDTO | None = None

    if step_obj.causal_source_step_id is not None:
        src_id = step_obj.causal_source_step_id
        if src_id not in state.steps_by_id:
            msg = f"Step '{step_id}' references causal_source_step_id '{src_id}' which does not exist in workflow."
            logger.error("[DAGExecutor] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise AppException(message=msg, status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED})

        if (
            src_id not in state.exec_record.step_states
            or state.exec_record.step_states[src_id].status != ExecutionStatus.PASSED
        ):
            logger.error(
                "[DAGExecutor] %s: Upstream causal step '%s' did not complete successfully.",
                ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION.name,
                src_id,
                exc_info=True,
            )
            raise AppException(
                message="Upstream causal discovery step produced 0 valid proposition nodes for downstream evaluation.",
                status_code=500,
                details={"error_code": ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION},
            )

        for evt in reversed(state.exec_record.execution_trace):
            if evt.step_name == src_id and evt.event_type == "output":
                match evt.content:
                    case CausalGraphPayloadDTO() as direct_graph:
                        upstream_graph = direct_graph
                    case raw_evt_content:
                        upstream_graph = _parse_causal_graph_candidate(
                            raw_evt_content, "Failed to parse upstream causal graph"
                        )
                break

        if upstream_graph is None:
            for snap_dto in state.projector.snapshot:
                if snap_dto.step_id == src_id:
                    match snap_dto.payload:
                        case CausalGraphPayloadDTO() as snap_graph:
                            upstream_graph = snap_graph
                        case raw_snap_content:
                            upstream_graph = _parse_causal_graph_candidate(
                                raw_snap_content, "Failed to parse upstream causal graph from snapshot payload"
                            )
                    break

        if upstream_graph is None or not upstream_graph.nodes:
            msg = "Upstream causal discovery step produced 0 valid proposition nodes for downstream evaluation."
            logger.error(
                "[DAGExecutor] %s: %s",
                ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION.name,
                msg,
                exc_info=True,
            )
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION}
            )

        fusion_atoms = transform_causal_nodes_to_atoms(upstream_graph.nodes)
        async with _update_lock:
            state.global_context_vars = state.global_context_vars.model_copy(update={"shuffled_atoms": fusion_atoms})
            default_meta = ExecutionMetadata(
                workflow_version=state.workflow.version,
                model_registry_id=state.workflow.model_registry_id,
            )
            base_meta = state.exec_record.metadata if state.exec_record.metadata is not None else default_meta
            state.exec_record = state.exec_record.model_copy(
                update={"metadata": base_meta.model_copy(update={"global_context_vars": state.global_context_vars})}
            )

    step_def: Step | None = None
    if step_obj.task_blueprint is not None and step_obj.task_blueprint in state.step_definitions:
        step_def = state.step_definitions[step_obj.task_blueprint]
    if step_def and ("atom_flattening_hook" in step_def.pre_hooks or "synthesis_distiller_hook" in step_def.pre_hooks):
        has_evaluated_atoms = any(state.exec_record.step_states.values()) or any(
            evt.event_type == "output" and evt.step_name != "matrix_reducer"
            for evt in state.exec_record.execution_trace
        )
        if has_evaluated_atoms:
            try:
                reducer_cls = _resolve_matrix_reducer()
                lightweight_matrix = reducer_cls.reduce_matrix(state.exec_record)
                reduce_event = TraceEvent(step_name="matrix_reducer", event_type="output", content=lightweight_matrix)
                async with _update_lock:
                    state.exec_record.execution_trace.append(reduce_event)
                    state.projector.apply_delta(reduce_event)
                    new_cv = state.exec_record.context_variables.with_update(
                        __MATRIX_REDUCER_OUTPUT__=lightweight_matrix
                    )
                    state.exec_record = state.exec_record.model_copy(update={"context_variables": new_cv})
                logger.info("[DAGExecutor] Successfully applied MatrixReducer pre-synthesis.")
            except Exception as e:
                logger.error(
                    "[DAGExecutor] %s: Failed to project and reduce matrix pre-synthesis: %s",
                    ErrorCodes.WORKFLOW_EXECUTION_FAILED.name,
                    e,
                    exc_info=True,
                )
                raise WorkflowExecutionError(step_id=step_id, task_key=step_obj.task_blueprint, original_error=e) from e

    return upstream_graph, step_def


def _extract_app_exception_error_code(exc: BaseException) -> str:
    """Resolve canonical error_code string from an exception instance.

    Args:
        exc: Exception instance caught at the DAG step execution boundary.

    Returns:
        Canonical error code string or UNKNOWN_ERROR if not present on the exception.
    """
    err_code = "UNKNOWN_ERROR"
    if isinstance(exc, AppException):
        if isinstance(exc.error_code, ErrorCodes):
            err_code = exc.error_code.name
        elif (
            not isinstance(exc.details, (str, int, float, bool, list))
            and exc.details is not None
            and "error_code" in exc.details
        ):
            code_val = exc.details["error_code"]
            if isinstance(code_val, ErrorCodes):
                err_code = code_val.name
            elif isinstance(code_val, str):
                err_code = code_val
    return err_code


async def execute_dag_step_wrapper(
    state: WorkflowExecutionState,
    step_id: str,
    node_executor: NodeExecutor,
    committer: ExecutionCommitter,
    causal_cohesion_evaluator: CausalCohesionEvaluator | None = None,
    dlq_on_step_failure: Callable[[str, str, BaseException], None] = dlq_record_step_failure,
    dlq_on_progress_commit_error: Callable[[str, Exception], None] = dlq_handle_progress_commit_error,
) -> None:
    """Execute a single DAG step with dependency gating, retry loop, progress callback, and trace commit.

    Args:
        state: Active WorkflowExecutionState holding execution record, locks, and step definitions.
        step_id: Canonical Opaque Stripe ID of the step to execute.
        node_executor: NodeExecutor instance dispatching strategy execution.
        committer: ExecutionCommitter persisting step state and trace events.
        causal_cohesion_evaluator: Optional evaluator computing post-step causal cohesion telemetry.
        dlq_on_step_failure: Callback recording dead-letter error telemetry when the step fails.
        dlq_on_progress_commit_error: Callback handling non-terminal progress commit failures.

    Raises:
        AppException: Triggered with VALIDATION_FAILED or CAUSAL_DISCOVERY_DATA_STARVATION when
            context preparation or node strategy execution fails with a domain error.
        WorkflowExecutionError: Triggered with WORKFLOW_EXECUTION_FAILED when pre-synthesis reduction
            or step execution fails.
    """
    step_obj = state.steps_by_id[step_id]
    if state.exec_record.step_states[step_id].status == ExecutionStatus.PASSED:
        return

    _update_lock = state.update_lock
    tracer = get_tracer(__name__)
    node_stack = contextlib.ExitStack()
    node_span = node_stack.enter_context(tracer.start_as_current_span(f"dag.node.{step_id}"))
    node_span.set_attribute("node.id", step_id)
    if step_obj.task_blueprint is not None:
        node_span.set_attribute("node.blueprint", step_obj.task_blueprint)
    node_span.set_attribute("node.depends_on", list(step_obj.depends_on))

    try:
        for dep in step_obj.depends_on:
            if (
                dep in state.exec_record.step_states
                and state.exec_record.step_states[dep].status != ExecutionStatus.PASSED
            ):
                async with _update_lock:
                    state.exec_record = state.exec_record.transition_step(
                        step_id=step_id,
                        status=ExecutionStatus.BLOCKED,
                        last_error=f"Dependency {dep} did not pass",
                        has_warning=True,
                    )
                await safe_commit_execution_state(state=state, committer=committer)
                logger.warning(
                    "[DAGExecutor] Cascading failure: Step %s blocked because dependency %s did not pass.",
                    step_id,
                    dep,
                )
                return

        upstream_graph, node_step_def = await prepare_step_strategy_context(state=state, step_id=step_id)

        async with _update_lock:
            state.exec_record = state.exec_record.transition_step(step_id=step_id, status=ExecutionStatus.RUNNING)
        await safe_commit_execution_state(state=state, committer=committer)

        async def progress_callback(completed: int, total: int) -> None:
            if total == 100:
                prog = completed
                label = f"Processing... {prog}%"
            else:
                prog = 0
                if total > 0:
                    prog = int((completed / total) * 100)
                label = f"Evaluating batch {completed}/{total}..."

            async with _update_lock:
                state.exec_record = state.exec_record.transition_step(
                    step_id=step_id,
                    status=state.exec_record.step_states[step_id].status,
                    progress=prog,
                    label=label,
                )
                state.exec_record = state.exec_record.model_copy(update={"progress": prog, "status_message": label})
            try:
                await safe_commit_execution_state(state=state, committer=committer)
                logger.info("Progress updated for step %s: %s", step_id, label)
            except (OSError, AppException, TimeoutError, ConnectionError) as commit_err:
                dlq_on_progress_commit_error(step_id, commit_err)

        settings = _resolve_settings()
        events: list[TraceEvent] = []
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(settings.llm_max_transient_retries),
            wait=wait_exponential(
                multiplier=settings.llm_retry_multiplier,
                min=settings.llm_retry_min_seconds,
                max=settings.llm_retry_max_seconds,
            ),
            retry=retry_if_exception(_is_transient_llm_error),
            reraise=True,
            before_sleep=before_sleep_log(logger, logging.WARNING),
        ):
            with attempt:
                default_exec_meta = ExecutionMetadata(
                    workflow_version=state.workflow.version,
                    model_registry_id=state.workflow.model_registry_id,
                )
                step_meta = state.exec_record.metadata if state.exec_record.metadata is not None else default_exec_meta
                events = await node_executor.execute(
                    step=step_obj,
                    execution_id=state.execution_id,
                    workflow_id=state.workflow.id,
                    metadata=step_meta,
                    target_locale=state.exec_record.target_locale,
                    output_profile_id=state.exec_record.output_profile_id,
                    organization_id=state.exec_record.organization_id,
                    projector=state.projector,
                    expected_inputs=state.workflow.expected_inputs,
                    frozen_ctx=state.exec_record.frozen_context,
                    trace=state.exec_record.execution_trace,
                    strictness_level=state.strictness_level,
                    lexical_strictness_level=state.lexical_strictness_level,
                    context_variables=state.exec_record.context_variables,
                    progress_callback=progress_callback,
                    step_def=node_step_def,
                    global_context_vars=state.global_context_vars,
                )

        await finalize_step_output_and_commit(
            state=state,
            step_id=step_id,
            events=events,
            committer=committer,
            upstream_graph=upstream_graph,
            causal_cohesion_evaluator=causal_cohesion_evaluator,
        )

    except state.step_exceptions as e:
        node_span.record_exception(e)
        node_span.set_status(otel_trace.StatusCode.ERROR, str(e))
        err_code = _extract_app_exception_error_code(e)
        async with _update_lock:
            state.exec_record = state.exec_record.transition_step(
                step_id=step_id, status=ExecutionStatus.FAILED, last_error=str(e), has_warning=True
            )
            error_evt = ErrorTraceEvent(
                step_name=step_id,
                error_code=err_code,
                error_message=str(e),
                content={"error_code": err_code, "message": str(e)},
            )
            state.exec_record.execution_trace.append(error_evt)
            state.projector.apply_delta(error_evt)
        await safe_commit_execution_state(
            state=state, committer=committer, status_override=ExecutionStatus.FAILED, error_override=str(e)
        )
        dlq_on_step_failure(step_id, err_code, e)
        raise
    except Exception as e:
        node_span.record_exception(e)
        node_span.set_status(otel_trace.StatusCode.ERROR, str(e))
        async with _update_lock:
            state.exec_record = state.exec_record.transition_step(
                step_id=step_id, status=ExecutionStatus.FAILED, last_error=str(e), has_warning=True
            )
        await safe_commit_execution_state(
            state=state, committer=committer, status_override=ExecutionStatus.FAILED, error_override=str(e)
        )
        dlq_on_step_failure(step_id, "UNEXPECTED_STEP_EXCEPTION", e)
        raise
    finally:
        node_stack.close()
