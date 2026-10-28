"""Post-step causal fusion/commit and topological wave TaskGroup orchestrator stage."""

from __future__ import annotations

import asyncio
import contextlib
import logging
import sys
from collections.abc import Callable, Coroutine
from typing import Any

import opentelemetry.trace as otel_trace
from pydantic import JsonValue, TypeAdapter

from backend_v2.core.hook_registry import GlobalContextVarsDTO
from backend_v2.core.telemetry import get_tracer
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.execution import ExecutionRecord, FrozenContext
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.causal_discovery import CausalGraphPayloadDTO
from backend_v2.models.dtos.node_execution import StepOutputContentDTO
from backend_v2.models.dtos.schema_manifest import GeneratedSchemaManifestDTO
from backend_v2.models.dtos.trace import TraceEventMetadataDTO
from backend_v2.models.enums import ExecutionStatus
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent, TraceEvent
from backend_v2.services.orchestrator.causal_cohesion_evaluator import CausalCohesionEvaluator
from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService
from backend_v2.services.orchestrator.dag_executor.causal_tda_fusion import compute_causal_tda_fusion_result
from backend_v2.services.orchestrator.dag_executor.execution_committer import (
    ExecutionCommitter,
)
from backend_v2.services.orchestrator.dag_executor.node_executor import NodeExecutor
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    WorkflowExecutionState,
    dlq_handle_progress_commit_error,
    dlq_record_step_failure,
    execute_rag_preflight_stage,
    safe_commit_execution_state,
)
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)
__all__ = ["execute_topological_waves_stage", "finalize_step_output_and_commit"]
_DAG_EXECUTOR_MODULE = "backend_v2.services.orchestrator.dag_executor"


def _resolve_settings() -> Any:
    """Resolve settings using dag_executor.get_settings when present for patch compatibility."""
    getter = sys.modules[_DAG_EXECUTOR_MODULE].get_settings if _DAG_EXECUTOR_MODULE in sys.modules else get_settings
    return getter()


def _extract_evaluated_atoms(events: list[TraceEvent]) -> list[AtomResultDTO]:
    """Extract evaluated AtomResultDTO items from step output TraceEvents."""
    evaluated_atoms: list[AtomResultDTO] = []
    atom_adapter = TypeAdapter(AtomResultDTO)
    for evt in events:
        if isinstance(evt.content, AtomResultDTO):
            evaluated_atoms.append(evt.content)
            continue
        raw = evt.content.data if isinstance(evt.content, StepOutputContentDTO) else evt.content
        if type(raw) is dict and "results" in raw and isinstance(raw["results"], list):
            evaluated_atoms.extend(
                item if isinstance(item, AtomResultDTO) else atom_adapter.validate_python(item)
                for item in raw["results"]
            )
    return evaluated_atoms


async def _commit_record_snapshot(
    committer: ExecutionCommitter, rec: ExecutionRecord, error: str | None = None
) -> None:
    """Persist ExecutionRecord trace, status, step_states, and context_variables via ExecutionCommitter."""
    await committer.commit_trace(
        rec.execution_trace, rec.status, rec.step_states, error, None, rec.context_variables, rec.steps
    )


def _append_causal_fusion_and_cohesion_events(
    state: WorkflowExecutionState,
    step_id: str,
    src_step_id: str,
    events: list[TraceEvent],
    upstream_graph: CausalGraphPayloadDTO,
    causal_cohesion_evaluator: CausalCohesionEvaluator | None,
) -> None:
    """Evaluate causal TDA fusion and BARS causal cohesion, appending output and decision TraceEvents."""
    settings = _resolve_settings()
    evaluated_atoms = _extract_evaluated_atoms(events)
    atoms_arg: list[AtomResultDTO] | None = None
    if evaluated_atoms:
        atoms_arg = evaluated_atoms
    eval_m = state.global_context_vars.evaluative_matrices
    damp = settings.causal_secondary_fault_dampening
    fusion_res = compute_causal_tda_fusion_result(
        upstream_graph, eval_m, atoms_arg, damp, state.workflow.expected_inputs
    )
    events.append(TraceEvent(step_name=step_id, event_type="output", content={"fusion": fusion_res}))
    if src_step_id not in state.evaluated_causal_sources:
        state.evaluated_causal_sources.add(src_step_id)
        evaluator = causal_cohesion_evaluator if causal_cohesion_evaluator is not None else CausalCohesionEvaluator()
        eval_dto = evaluator.evaluate_causal_cohesion(
            audit=fusion_res.anti_fluff_audit,
            total_nodes=fusion_res.total_deliverable_nodes,
            strictness_level=state.workflow.default_strictness_level,
            matrix_block_id=settings.causal_cohesion_matrix_block_id,
        )
        m_dump = eval_dto.matrix_output.model_dump(mode="json", exclude_none=True)
        events.append(
            TraceEvent(
                step_name=src_step_id,
                event_type="output",
                content={
                    "results": eval_dto.atom_results,
                    "hydrated_references": eval_dto.hydrated_references,
                    eval_dto.matrix_block_id: m_dump,
                },
            )
        )
        gvar_evt = GlobalContextVarsDTO(evaluative_matrices={eval_dto.matrix_block_id: eval_dto.score_result.score})
        meta_upd = TraceEventMetadataDTO(is_context_update=True)
        events.append(TraceEvent(step_name=src_step_id, event_type="decision", metadata=meta_upd, content=gvar_evt))


def _merge_global_context_vars(state: WorkflowExecutionState, parsed: GlobalContextVarsDTO) -> bool:
    """Merge validated GlobalContextVarsDTO fields from a decision event into state."""
    has_gvar_updates = False
    if parsed.evaluative_matrices is not None:
        cur = state.global_context_vars.evaluative_matrices
        merged = {**cur, **parsed.evaluative_matrices} if cur else parsed.evaluative_matrices
        state.global_context_vars = state.global_context_vars.model_copy(update={"evaluative_matrices": merged})
        has_gvar_updates = True
    if parsed.passivity_detected is not None:
        state.global_context_vars = state.global_context_vars.model_copy(
            update={"passivity_detected": parsed.passivity_detected}
        )
        has_gvar_updates = True
    return has_gvar_updates


def _deduplicate_mcp_traces(
    current_traces: list[MCPAuditTrace], step_mcp_traces: list[MCPAuditTrace]
) -> list[MCPAuditTrace]:
    """Deduplicate step MCPAuditTrace entries against existing FrozenContext traces by ID."""
    seen_ids: set[str] = {t.id for t in current_traces if t.id}
    new_unique: list[MCPAuditTrace] = []
    for trace_item in step_mcp_traces:
        if trace_item.id is None or trace_item.id not in seen_ids:
            new_unique.append(trace_item)
            if trace_item.id:
                seen_ids.add(trace_item.id)
    return new_unique


async def _apply_step_events_to_record(
    state: WorkflowExecutionState, step_id: str, events: list[TraceEvent], has_error_evt: bool
) -> None:
    """Apply step TraceEvents, context updates, MCP traces, and schemas to state.exec_record."""
    _update_lock = state.update_lock
    async with _update_lock:
        step_mcp_traces: list[MCPAuditTrace] = []
        step_generated_schemas: dict[str, JsonValue] = {}
        new_cv = state.exec_record.context_variables
        has_cv_updates, has_gvar_updates = False, False
        for evt in events:
            state.exec_record.execution_trace.append(evt)
            state.projector.apply_delta(evt)
            is_ctx_upd = evt.event_type == "decision" and bool(evt.metadata and evt.metadata.is_context_update)
            if is_ctx_upd and evt.content is not None and not isinstance(evt.content, (str, int, float, bool, list)):
                content_dict = dict(evt.content)
                new_cv, has_cv_updates = new_cv.with_update(**content_dict), True
                gvar_data = {k: v for k, v in content_dict.items() if k in GlobalContextVarsDTO.model_fields}
                if gvar_data and _merge_global_context_vars(state, GlobalContextVarsDTO.model_validate(gvar_data)):
                    has_gvar_updates = True
            if evt.mcp_audit_traces:
                step_mcp_traces.extend(evt.mcp_audit_traces)
            elif evt.metadata and evt.metadata.generated_schema is not None:
                step_generated_schemas[evt.step_name] = evt.metadata.generated_schema
        schema_manifest = GeneratedSchemaManifestDTO(schemas=step_generated_schemas)

        if has_cv_updates:
            state.exec_record = state.exec_record.model_copy(update={"context_variables": new_cv})

        if has_gvar_updates:
            default_meta = ExecutionMetadata(
                workflow_version=state.workflow.version, model_registry_id=state.workflow.model_registry_id
            )
            base_meta = state.exec_record.metadata if state.exec_record.metadata is not None else default_meta
            updated_meta = base_meta.model_copy(update={"global_context_vars": state.global_context_vars})
            state.exec_record = state.exec_record.model_copy(update={"metadata": updated_meta})

        base_fc = state.exec_record.frozen_context if state.exec_record.frozen_context is not None else FrozenContext()
        new_mcp_traces = list(base_fc.mcp_tool_audit)
        if step_mcp_traces:
            new_unique = _deduplicate_mcp_traces(new_mcp_traces, step_mcp_traces)
            if new_unique:
                new_mcp_traces = new_mcp_traces + new_unique

        merged_schemas = base_fc.generated_schemas.schemas
        if schema_manifest.schemas:
            merged_schemas = {**base_fc.generated_schemas.schemas, **schema_manifest.schemas}

        if new_mcp_traces != list(base_fc.mcp_tool_audit) or merged_schemas != base_fc.generated_schemas.schemas:
            updated_fc = base_fc.model_copy(
                update={
                    "mcp_tool_audit": new_mcp_traces,
                    "generated_schemas": GeneratedSchemaManifestDTO(schemas=merged_schemas),
                }
            )
            state.exec_record = state.exec_record.model_copy(update={"frozen_context": updated_fc})

        if has_error_evt:
            step_status = ExecutionStatus.FAILED
            step_prog = None
        else:
            step_status = ExecutionStatus.PASSED
            step_prog = 100

        state.exec_record = state.exec_record.transition_step(step_id=step_id, status=step_status, progress=step_prog)


async def finalize_step_output_and_commit(
    state: WorkflowExecutionState,
    step_id: str,
    events: list[TraceEvent],
    committer: ExecutionCommitter,
    upstream_graph: CausalGraphPayloadDTO | None = None,
    causal_cohesion_evaluator: CausalCohesionEvaluator | None = None,
) -> None:
    """Finalize step output events, evaluate causal cohesion/fusion, and commit execution state.

    Args:
        state: Active WorkflowExecutionState containing execution record, projector, and lock.
        step_id: Canonical Opaque Stripe ID of the step being finalized.
        events: List of TraceEvent instances emitted by the step execution.
        committer: ExecutionCommitter persisting execution trace and state updates.
        upstream_graph: Optional upstream CausalGraphPayloadDTO when step has causal_source_step_id.
        causal_cohesion_evaluator: Optional CausalCohesionEvaluator override for BARS cohesion scoring.

    Raises:
        AppException: Triggered with WORKFLOW_EXECUTION_FAILED when an ErrorTraceEvent is present.
    """
    step_obj = state.steps_by_id[step_id]
    if step_obj.causal_source_step_id is not None and upstream_graph is not None:
        _append_causal_fusion_and_cohesion_events(
            state, step_id, step_obj.causal_source_step_id, events, upstream_graph, causal_cohesion_evaluator
        )
    has_error_evt = any(isinstance(evt, ErrorTraceEvent) for evt in events)
    await _apply_step_events_to_record(state=state, step_id=step_id, events=events, has_error_evt=has_error_evt)
    if has_error_evt:
        err_msg = [evt.error_message for evt in events if isinstance(evt, ErrorTraceEvent)][0]
        msg = f"Step {step_id} emitted ErrorTraceEvent: {err_msg}"
        logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg, status_code=500, details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED.value}
        )
    await safe_commit_execution_state(state=state, committer=committer)


async def _transition_and_commit_wave_failure(
    state: WorkflowExecutionState,
    committer: ExecutionCommitter,
    orch_span: otel_trace.Span,
    waves: list[list[StepRule]],
    wave_idx: int,
    wave: list[StepRule],
    primary_err: BaseException,
    dlq_on_step_failure: Callable[[str, str, BaseException], None],
) -> None:
    """Transition wave and downstream steps on TaskGroup failure and commit the failed record snapshot."""
    async with state.update_lock:
        for s_rule in wave:
            curr_st = state.exec_record.step_states[s_rule.id]
            if curr_st.status in (ExecutionStatus.RUNNING, ExecutionStatus.PENDING):
                state.exec_record = state.exec_record.transition_step(
                    step_id=s_rule.id, status=ExecutionStatus.FAILED, last_error=str(primary_err), has_warning=True
                )
                dlq_on_step_failure(s_rule.id, "WAVE_TASKGROUP_CANCELLED", primary_err)
        for remaining_wave in waves[wave_idx + 1 :]:
            for ds in remaining_wave:
                if state.exec_record.step_states[ds.id].status == ExecutionStatus.PENDING:
                    blk_err = f"Blocked due to wave {wave_idx} failure: {primary_err}"
                    state.exec_record = state.exec_record.transition_step(
                        step_id=ds.id, status=ExecutionStatus.BLOCKED, last_error=blk_err, has_warning=True
                    )
                    dlq_on_step_failure(ds.id, "DOWNSTREAM_WAVE_BLOCKED", primary_err)
        state.exec_record = state.exec_record.model_copy(
            update={"status": ExecutionStatus.FAILED, "error": str(primary_err)}
        )
    await _commit_record_snapshot(committer, state.exec_record, error=state.exec_record.error)
    orch_span.record_exception(primary_err)
    orch_span.set_status(otel_trace.StatusCode.ERROR, str(primary_err))


async def _transition_and_commit_unexpected_error(
    state: WorkflowExecutionState,
    committer: ExecutionCommitter,
    orch_span: otel_trace.Span,
    unexpected_err: Exception,
) -> None:
    """Transition running steps to FAILED on outer orchestration error and commit state."""
    async with state.update_lock:
        for s in state.exec_record.steps:
            if s.status == ExecutionStatus.RUNNING:
                state.exec_record = state.exec_record.transition_step(
                    step_id=s.id, status=ExecutionStatus.FAILED, last_error=str(unexpected_err), has_warning=True
                )
        state.exec_record = state.exec_record.model_copy(
            update={"status": ExecutionStatus.FAILED, "error": str(unexpected_err)}
        )
    await _commit_record_snapshot(committer, state.exec_record, error=state.exec_record.error)
    orch_span.record_exception(unexpected_err)
    orch_span.set_status(otel_trace.StatusCode.ERROR, str(unexpected_err))


async def execute_topological_waves_stage(
    state: WorkflowExecutionState,
    node_executor: NodeExecutor,
    committer: ExecutionCommitter,
    rag_preflight: RAGPreflightService | None = None,
    causal_cohesion_evaluator: CausalCohesionEvaluator | None = None,
    dlq_on_step_failure: Callable[[str, str, BaseException], None] = dlq_record_step_failure,
    dlq_on_progress_commit_error: Callable[[str, Exception], None] = dlq_handle_progress_commit_error,
    step_runner_fn: Callable[..., Coroutine[Any, Any, None]] | None = None,
) -> ExecutionRecord:
    """Orchestrate topological waves inside asyncio.TaskGroup with except* BaseException trapping.

    Args:
        state: Active WorkflowExecutionState holding workflow steps, execution record, and lock.
        node_executor: NodeExecutor instance executing individual step strategies.
        committer: ExecutionCommitter persisting execution trace and step states.
        rag_preflight: Optional RAGPreflightService executed prior to wave dispatch.
        causal_cohesion_evaluator: Optional CausalCohesionEvaluator passed to step finalization.
        dlq_on_step_failure: Callback recording dead-letter error telemetry on step failure.
        dlq_on_progress_commit_error: Callback handling non-terminal progress commit errors.
        step_runner_fn: Optional step runner coroutine override for wave task dispatch.

    Returns:
        Updated ExecutionRecord after all topological waves complete.

    Raises:
        AppException: Triggered with WORKFLOW_EXECUTION_FAILED when a wave or step fails.
    """
    tracer = get_tracer(__name__)
    orch_stack = contextlib.ExitStack()
    orch_span = orch_stack.enter_context(tracer.start_as_current_span("dag.orchestration"))
    orch_span.set_attribute("execution.id", state.execution_id)
    orch_span.set_attribute("workflow.id", state.workflow.id)
    orch_span.set_attribute("workflow.node_count", len(state.workflow.steps))
    runner: Callable[..., Coroutine[Any, Any, None]] = (
        step_runner_fn if step_runner_fn is not None else sys.modules[_DAG_EXECUTOR_MODULE].execute_dag_step_wrapper
    )
    try:
        if rag_preflight is not None:
            await execute_rag_preflight_stage(state, rag_preflight, committer, dlq_on_progress_commit_error)
        waves = DAGCompilerService.compute_topological_waves(state.workflow.steps)
        for wave_idx, wave in enumerate(waves):
            steps_to_run = [s for s in wave if state.exec_record.step_states[s.id].status != ExecutionStatus.PASSED]
            if not steps_to_run:
                continue
            try:
                common = (node_executor, committer, causal_cohesion_evaluator)
                dlq_cbs = (dlq_on_step_failure, dlq_on_progress_commit_error)
                async with asyncio.TaskGroup() as tg:
                    for s_rule in steps_to_run:
                        tg.create_task(runner(state, s_rule.id, *common, *dlq_cbs))
            except* BaseException as eg:
                primary_err = eg.exceptions[0]
                logger.error("[DAGExecutor] Wave %d execution failed: %s", wave_idx, eg, exc_info=True)
                await _transition_and_commit_wave_failure(
                    state, committer, orch_span, waves, wave_idx, wave, primary_err, dlq_on_step_failure
                )
                if isinstance(primary_err, AppException):
                    raise primary_err from eg
                msg = f"Workflow failed: {primary_err}"
                logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg, exc_info=True)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED}
                ) from eg

        failed_statuses = (ExecutionStatus.FAILED, ExecutionStatus.BLOCKED)
        if any(s.status in failed_statuses for s in state.exec_record.step_states.values()):
            async with state.update_lock:
                state.exec_record = state.exec_record.model_copy(update={"status": ExecutionStatus.FAILED})
            await _commit_record_snapshot(committer, state.exec_record)
            msg = "Workflow completed with failed steps"
            logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg, exc_info=True)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED}
            )
        await _commit_record_snapshot(committer, state.exec_record)
        return state.exec_record
    except Exception as unexpected_err:
        await _transition_and_commit_unexpected_error(state, committer, orch_span, unexpected_err)
        if isinstance(unexpected_err, AppException):
            raise
        msg = f"Workflow failed: {unexpected_err}"
        logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg, exc_info=True)
        raise AppException(
            message=msg, details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED}, status_code=500
        ) from unexpected_err
    finally:
        orch_stack.close()
