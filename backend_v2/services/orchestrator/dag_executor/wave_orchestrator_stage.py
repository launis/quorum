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
    ExecutionRecordUpdate,
    FrozenContextUpdate,
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
        trace=rec.execution_trace,
        status=rec.status,
        step_states=rec.step_states,
        error=error,
        context_variables=rec.context_variables,
        steps=rec.steps,
    )


# Phase 3, Step 1: Extract post-step causal fusion evaluation and atomic trace/schema/MCP-audit persistence
async def finalize_step_output_and_commit(
    state: WorkflowExecutionState,
    step_id: str,
    events: list[TraceEvent],
    committer: ExecutionCommitter,
    upstream_graph: CausalGraphPayloadDTO | None = None,
    causal_cohesion_evaluator: CausalCohesionEvaluator | None = None,
) -> None:
    """Finalize step output events, evaluate causal cohesion/fusion, and commit execution state."""
    step_obj = state.steps_by_id[step_id]
    settings = _resolve_settings()
    if step_obj.causal_source_step_id is not None and upstream_graph is not None:
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
        src_step_id = step_obj.causal_source_step_id
        if src_step_id not in state.evaluated_causal_sources:
            state.evaluated_causal_sources.add(src_step_id)
            evaluator = causal_cohesion_evaluator or CausalCohesionEvaluator()
            eval_dto = evaluator.evaluate_causal_cohesion(
                audit=fusion_res.anti_fluff_audit,
                total_nodes=fusion_res.total_deliverable_nodes,
                strictness_level=state.workflow.default_strictness_level,
                matrix_block_id=settings.causal_cohesion_matrix_block_id,
            )
            events.append(
                TraceEvent(
                    step_name=src_step_id,
                    event_type="output",
                    content={
                        "results": eval_dto.atom_results,
                        "hydrated_references": eval_dto.hydrated_references,
                        eval_dto.matrix_block_id: eval_dto.matrix_output.model_dump(mode="json"),
                    },
                )
            )
            gvar_evt = GlobalContextVarsDTO(evaluative_matrices={eval_dto.matrix_block_id: eval_dto.score_result.score})
            meta_upd = TraceEventMetadataDTO(is_context_update=True)
            events.append(TraceEvent(step_name=src_step_id, event_type="decision", metadata=meta_upd, content=gvar_evt))

    has_error_evt = any(isinstance(evt, ErrorTraceEvent) for evt in events)
    _update_lock = state.update_lock
    async with _update_lock:
        step_mcp_traces: list[MCPAuditTrace] = []
        step_generated_schemas: dict[str, JsonValue] = {}
        new_cv = state.exec_record.context_variables
        has_cv_updates = False
        has_gvar_updates = False
        for evt in events:
            state.exec_record.execution_trace.append(evt)
            state.projector.apply_delta(evt)
            is_ctx_upd = evt.event_type == "decision" and bool(evt.metadata and evt.metadata.is_context_update)
            if is_ctx_upd and evt.content is not None and not isinstance(evt.content, (str, int, float, bool, list)):
                content_dict = dict(evt.content)
                new_cv = new_cv.with_update(**content_dict)
                has_cv_updates = True
                gvar_data = {k: v for k, v in content_dict.items() if k in GlobalContextVarsDTO.model_fields}
                if gvar_data:
                    parsed = GlobalContextVarsDTO.model_validate(gvar_data)
                    if parsed.evaluative_matrices is not None:
                        cur = state.global_context_vars.evaluative_matrices
                        merged = {**cur, **parsed.evaluative_matrices} if cur else parsed.evaluative_matrices
                        gvars = state.global_context_vars
                        state.global_context_vars = gvars.model_copy(update={"evaluative_matrices": merged})
                        has_gvar_updates = True
                    if parsed.passivity_detected is not None:
                        gvars = state.global_context_vars
                        state.global_context_vars = gvars.model_copy(
                            update={"passivity_detected": parsed.passivity_detected}
                        )
                        has_gvar_updates = True
            if evt.mcp_audit_traces:
                step_mcp_traces.extend(evt.mcp_audit_traces)
            elif evt.metadata and evt.metadata.generated_schema is not None:
                step_generated_schemas[evt.step_name] = evt.metadata.generated_schema
        schema_manifest = GeneratedSchemaManifestDTO(schemas=step_generated_schemas)
        updates: dict[str, ExecutionRecordUpdate] = {}
        if has_cv_updates:
            updates["context_variables"] = new_cv
        if has_gvar_updates:
            base_meta = state.exec_record.metadata or ExecutionMetadata(
                workflow_version=state.workflow.version, model_registry_id=state.workflow.model_registry_id
            )
            updates["metadata"] = base_meta.model_copy(update={"global_context_vars": state.global_context_vars})
        fc_updates: dict[str, FrozenContextUpdate] = {}
        base_fc = state.exec_record.frozen_context or FrozenContext()
        if step_mcp_traces:
            current_traces: list[MCPAuditTrace] = list(base_fc.mcp_tool_audit)
            seen_ids: set[str] = {t.id for t in current_traces if t.id}
            new_unique: list[MCPAuditTrace] = []
            for t in step_mcp_traces:
                if t.id is None or t.id not in seen_ids:
                    new_unique.append(t)
                    if t.id:
                        seen_ids.add(t.id)
            if new_unique:
                fc_updates["mcp_tool_audit"] = current_traces + new_unique
        if schema_manifest.schemas:
            merged_schemas = {**base_fc.generated_schemas.schemas, **schema_manifest.schemas}
            fc_updates["generated_schemas"] = GeneratedSchemaManifestDTO(schemas=merged_schemas)
        if fc_updates:
            updates["frozen_context"] = base_fc.model_copy(update=fc_updates)
        step_status = ExecutionStatus.FAILED if has_error_evt else ExecutionStatus.PASSED
        step_prog = 100 if step_status == ExecutionStatus.PASSED else None
        if updates:
            state.exec_record = state.exec_record.model_copy(update=updates)
        state.exec_record = state.exec_record.transition_step(step_id=step_id, status=step_status, progress=step_prog)
    if has_error_evt:
        err_msg = [evt.error_message for evt in events if isinstance(evt, ErrorTraceEvent)][0]
        msg = f"Step {step_id} emitted ErrorTraceEvent: {err_msg}"
        logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg)
        raise AppException(
            message=msg, status_code=500, details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED.value}
        )
    await safe_commit_execution_state(state=state, committer=committer)


# Phase 3, Step 1: Extract topological wave TaskGroup orchestrator stage
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
    """Orchestrate topological waves inside asyncio.TaskGroup with except* BaseException trapping."""
    tracer = get_tracer(__name__)
    orch_stack = contextlib.ExitStack()
    orch_span = orch_stack.enter_context(tracer.start_as_current_span("dag.orchestration"))
    orch_span.set_attribute("execution.id", state.execution_id)
    orch_span.set_attribute("workflow.id", state.workflow.id)
    orch_span.set_attribute("workflow.node_count", len(state.workflow.steps))
    _update_lock = state.update_lock
    runner: Callable[..., Coroutine[Any, Any, None]] = (
        step_runner_fn or sys.modules[_DAG_EXECUTOR_MODULE].execute_dag_step_wrapper
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
                async with _update_lock:
                    for s_rule in wave:
                        curr_st = state.exec_record.step_states[s_rule.id]
                        if curr_st.status in (ExecutionStatus.RUNNING, ExecutionStatus.PENDING):
                            err_s = str(primary_err)
                            state.exec_record = state.exec_record.transition_step(
                                step_id=s_rule.id, status=ExecutionStatus.FAILED, last_error=err_s, has_warning=True
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
                if isinstance(primary_err, AppException):
                    raise primary_err from eg
                msg = f"Workflow failed: {primary_err}"
                logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=500, details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED}
                ) from eg

        failed_statuses = (ExecutionStatus.FAILED, ExecutionStatus.BLOCKED)
        if any(s.status in failed_statuses for s in state.exec_record.step_states.values()):
            async with _update_lock:
                state.exec_record = state.exec_record.model_copy(update={"status": ExecutionStatus.FAILED})
            await _commit_record_snapshot(committer, state.exec_record)
            msg = "Workflow completed with failed steps"
            logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg)
            raise AppException(
                message=msg, status_code=500, details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED}
            )
        await _commit_record_snapshot(committer, state.exec_record)
        return state.exec_record
    except Exception as unexpected_err:
        async with _update_lock:
            for s in state.exec_record.steps:
                if s.status == ExecutionStatus.RUNNING:
                    err_s = str(unexpected_err)
                    state.exec_record = state.exec_record.transition_step(
                        step_id=s.id, status=ExecutionStatus.FAILED, last_error=err_s, has_warning=True
                    )
            state.exec_record = state.exec_record.model_copy(
                update={"status": ExecutionStatus.FAILED, "error": str(unexpected_err)}
            )
        await _commit_record_snapshot(committer, state.exec_record, error=state.exec_record.error)
        orch_span.record_exception(unexpected_err)
        orch_span.set_status(otel_trace.StatusCode.ERROR, str(unexpected_err))
        if isinstance(unexpected_err, AppException):
            raise
        msg = f"Workflow failed: {unexpected_err}"
        logger.error("[DAGExecutor] %s: %s", ErrorCodes.WORKFLOW_EXECUTION_FAILED.name, msg)
        raise AppException(
            message=msg, details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED}, status_code=500
        ) from unexpected_err
    finally:
        orch_stack.close()
