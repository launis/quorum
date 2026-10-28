"""Unit tests for backend_v2.services.orchestrator.dag_executor.wave_orchestrator_stage.

Verifies finalize_step_output_and_commit (post-step causal TDA fusion, CausalCohesionEvaluator,
context variable updates, MCP audit deduplication, and ErrorTraceEvent fail-fast) and
execute_topological_waves_stage (parallel wave execution via asyncio.TaskGroup, except*
BaseException error trapping, and downstream BLOCKED step propagation).
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

import pytest

from backend_v2.core.hook_registry import GlobalContextVarsDTO
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import (
    ExecutionRecord,
    ExecutionStep,
    FrozenContext,
)
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.atom_result import AtomResultDTO, ExtractedValueDTO
from backend_v2.models.dtos.causal_discovery import (
    CausalGraphPayloadDTO,
    CausalNodeDTO,
)
from backend_v2.models.dtos.node_execution import StepOutputContentDTO
from backend_v2.models.dtos.trace import TraceEventMetadataDTO
from backend_v2.models.enums import ExecutionStatus, HistoricalContextMode
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent, StateProjector, TraceEvent
from backend_v2.services.orchestrator.dag_executor.execution_committer import ExecutionCommitter
from backend_v2.services.orchestrator.dag_executor.node_executor import NodeExecutor
from backend_v2.services.orchestrator.dag_executor.wave_orchestrator_stage import (
    execute_topological_waves_stage,
    finalize_step_output_and_commit,
)
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    WorkflowExecutionState,
    dlq_fallback_step_exceptions,
)
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService
from backend_v2.services.orchestrator.strategies.base import StrategyDependencies
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _build_deps(repo: InMemoryUnifiedWorkflowRepository) -> StrategyDependencies:
    return StrategyDependencies(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=None,
    )


def _build_state(
    steps: list[StepRule],
    step_definitions: dict[str, Step] | None = None,
    step_statuses: dict[str, ExecutionStatus] | None = None,
) -> WorkflowExecutionState:
    wf = Workflow(
        id="wf_1111222233334444",
        slug="wf_wave_orch",
        name=I18nText(translations={"en": "Wave WF", "fi": "Aalto WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        status="active",
        version=1,
        historical_context_mode=HistoricalContextMode.DISABLED,
        default_profile_id="prf_1111222233334444",
        model_registry_id="sys_1111222233334444",
        steps=steps,
    )
    statuses = step_statuses or {}
    exec_steps = [
        ExecutionStep(
            id=s.id,
            label=s.id,
            status=statuses[s.id] if s.id in statuses else ExecutionStatus.PENDING,
        )
        for s in steps
    ]
    rec = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id=wf.id,
        target_locale="en",
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "input"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.RUNNING,
        steps=exec_steps,
        step_states={s.id: s for s in exec_steps},
        execution_trace=[],
        metadata=ExecutionMetadata(
            workflow_version=1,
            model_registry_id="sys_1111222233334444",
            global_context_vars=GlobalContextVarsDTO(language="en", target_locale="en"),
        ),
    )
    return WorkflowExecutionState(
        execution_id=rec.id,
        workflow=wf,
        exec_record=rec,
        global_context_vars=GlobalContextVarsDTO(language="en", target_locale="en"),
        projector=StateProjector(),
        step_definitions=step_definitions or {},
        steps_by_id={s.id: s for s in steps},
        step_exceptions=dlq_fallback_step_exceptions(),
    )


@pytest.mark.asyncio
async def test_execute_topological_waves_stage_runs_parallel_wave_steps() -> None:
    """Contract: execute_topological_waves_stage dispatches independent wave steps concurrently inside TaskGroup."""
    repo = InMemoryUnifiedWorkflowRepository()
    step_a = StepRule(id="stp_1111111111111111", task_blueprint="stp_1111111111111111", depends_on=[])
    step_b = StepRule(id="stp_2222222222222222", task_blueprint="stp_1111111111111111", depends_on=[])
    step_c = StepRule(
        id="stp_3333333333333333",
        task_blueprint="stp_1111111111111111",
        depends_on=[step_a.id, step_b.id],
    )
    state = _build_state(steps=[step_a, step_b, step_c])
    repo.set_execution(state.exec_record)
    committer = ExecutionCommitter(exec_repo=repo, execution_id=state.execution_id)

    executed_order: list[str] = []

    class _ParallelNodeExecutor(NodeExecutor):
        async def execute(self, step: StepRule, *args: Any, **kwargs: Any) -> list[TraceEvent]:
            _ = (args, kwargs)
            await asyncio.sleep(0.01)
            executed_order.append(step.id)
            return [TraceEvent(step_name=step.id, event_type="output", content={"done": step.id})]

    record = await execute_topological_waves_stage(
        state=state,
        node_executor=_ParallelNodeExecutor(deps=_build_deps(repo)),
        committer=committer,
    )

    assert set(executed_order[:2]) == {step_a.id, step_b.id}
    assert executed_order[2] == step_c.id
    assert record.step_states[step_a.id].status == ExecutionStatus.PASSED
    assert record.step_states[step_b.id].status == ExecutionStatus.PASSED
    assert record.step_states[step_c.id].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_execute_topological_waves_stage_marks_downstream_steps_blocked_on_failure() -> None:
    """Contract: execute_topological_waves_stage traps step exceptions, marks downstream steps BLOCKED, and re-raises."""
    repo = InMemoryUnifiedWorkflowRepository()
    step_fail = StepRule(id="stp_1111111111111111", task_blueprint="stp_1111111111111111", depends_on=[])
    step_sibling = StepRule(id="stp_2222222222222222", task_blueprint="stp_1111111111111111", depends_on=[])
    step_downstream = StepRule(
        id="stp_3333333333333333",
        task_blueprint="stp_1111111111111111",
        depends_on=[step_fail.id],
    )
    state = _build_state(steps=[step_fail, step_sibling, step_downstream])
    repo.set_execution(state.exec_record)
    committer = ExecutionCommitter(exec_repo=repo, execution_id=state.execution_id)

    class _WaveFailingNodeExecutor(NodeExecutor):
        async def execute(self, step: StepRule, *args: Any, **kwargs: Any) -> list[TraceEvent]:
            _ = (args, kwargs)
            if step.id == step_fail.id:
                raise RuntimeError("wave 0 fatal failure")
            await asyncio.sleep(0.5)
            return []

    dlq_events: list[tuple[str, str]] = []
    with pytest.raises(AppException) as exc_info:
        await execute_topological_waves_stage(
            state=state,
            node_executor=_WaveFailingNodeExecutor(deps=_build_deps(repo)),
            committer=committer,
            dlq_on_step_failure=lambda sid, code, _exc: dlq_events.append((sid, code)),
        )

    assert exc_info.value.status_code == 500
    assert state.exec_record.status == ExecutionStatus.FAILED
    assert state.exec_record.step_states[step_fail.id].status == ExecutionStatus.FAILED
    assert state.exec_record.step_states[step_sibling.id].status == ExecutionStatus.FAILED
    assert state.exec_record.step_states[step_downstream.id].status == ExecutionStatus.BLOCKED
    dlq_ids = {sid for sid, _ in dlq_events}
    assert {step_fail.id, step_sibling.id, step_downstream.id}.issubset(dlq_ids)


@pytest.mark.asyncio
async def test_finalize_step_output_and_commit_causal_fusion_cohesion_and_context_updates() -> None:
    """Verify finalize_step_output_and_commit evaluates causal TDA fusion, updates context vars, and deduplicates MCP."""
    repo = InMemoryUnifiedWorkflowRepository()
    causal_step = StepRule(id="stp_1111222233334444", task_blueprint="stp_1111222233334444")
    tda_step = StepRule(
        id="stp_5555666677778888",
        task_blueprint="stp_5555666677778888",
        depends_on=[causal_step.id],
        causal_source_step_id=causal_step.id,
    )
    state = _build_state(
        steps=[causal_step, tda_step],
        step_statuses={causal_step.id: ExecutionStatus.PASSED, tda_step.id: ExecutionStatus.RUNNING},
    )
    repo.set_execution(state.exec_record)
    committer = ExecutionCommitter(exec_repo=repo, execution_id=state.execution_id)

    graph = CausalGraphPayloadDTO(
        nodes=[
            CausalNodeDTO(
                node_id="tda_1111222233334444",
                claim="Claim 1",
                source_quotes=("Quote 1",),
                paragraph_ref="P1",
                status=ExecutionStatus.PASSED,
                blame_parent_ids=[],
                dependent_child_ids=[],
            )
        ],
        edges=[],
        root_cause_node_ids=[],
        cycle_detected=False,
        isolated_node_ids=[],
        partition_node_ids={},
        edge_root_causes=[],
    )
    atom_dto = AtomResultDTO(
        tda_id="tda_1111222233334444",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Valid evidence",
        source_quotes=("Quote 1",),
        extracted_data=ExtractedValueDTO(value=4.0),
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    mcp_trace = MCPAuditTrace(
        id="tr_1111222233334444",
        tool_id="mcp_search",
        step_name=tda_step.id,
        query="search query",
        timestamp=datetime.now(UTC),
    )
    events = [
        TraceEvent(step_name=tda_step.id, event_type="output", content=atom_dto, mcp_audit_traces=[mcp_trace]),
        TraceEvent(
            step_name=tda_step.id,
            event_type="output",
            content=StepOutputContentDTO(data={"results": [atom_dto]}),
            mcp_audit_traces=[mcp_trace],
        ),
        TraceEvent(
            step_name=tda_step.id,
            event_type="output",
            content={"results": [atom_dto]},
        ),
        TraceEvent(
            step_name=tda_step.id,
            event_type="decision",
            metadata=TraceEventMetadataDTO(is_context_update=True, generated_schema={"type": "object"}),
            content=GlobalContextVarsDTO(
                evaluative_matrices={"blk_1111222233334444": 80.0},
                passivity_detected=True,
            ),
        ),
    ]

    await finalize_step_output_and_commit(
        state=state,
        step_id=tda_step.id,
        events=events,
        committer=committer,
        upstream_graph=graph,
    )

    assert state.exec_record.step_states[tda_step.id].status == ExecutionStatus.PASSED
    assert state.global_context_vars.passivity_detected is True
    assert state.global_context_vars.evaluative_matrices is not None
    assert "blk_1111222233334444" in state.global_context_vars.evaluative_matrices
    assert state.exec_record.frozen_context is not None
    assert len(state.exec_record.frozen_context.mcp_tool_audit) == 1

    # Verify ErrorTraceEvent raises AppException(WORKFLOW_EXECUTION_FAILED)
    err_events: list[TraceEvent] = [
        ErrorTraceEvent(
            step_name=tda_step.id,
            error_code="STEP_FAILED",
            error_message="node emitted error",
        )
    ]
    with pytest.raises(AppException) as exc_err:
        await finalize_step_output_and_commit(
            state=state,
            step_id=tda_step.id,
            events=err_events,
            committer=committer,
        )
    assert exc_err.value.status_code == 500
    assert exc_err.value.details["error_code"] == ErrorCodes.WORKFLOW_EXECUTION_FAILED.value

    # Verify post-wave failed_statuses check and top-level unexpected_err handling
    state_post_fail = _build_state(
        steps=[causal_step, tda_step],
        step_statuses={causal_step.id: ExecutionStatus.PASSED, tda_step.id: ExecutionStatus.PENDING},
    )
    repo.set_execution(state_post_fail.exec_record)

    async def _blocking_runner(st: WorkflowExecutionState, sid: str, *_args: Any) -> None:
        st.exec_record = st.exec_record.transition_step(step_id=sid, status=ExecutionStatus.BLOCKED)

    with pytest.raises(AppException) as exc_post:
        await execute_topological_waves_stage(
            state=state_post_fail,
            node_executor=NodeExecutor(deps=_build_deps(repo)),
            committer=committer,
            step_runner_fn=_blocking_runner,
        )
    assert exc_post.value.status_code == 500
    assert state_post_fail.exec_record.status == ExecutionStatus.FAILED

    class _FailingPreflight(RAGPreflightService):
        def __init__(self) -> None:
            pass

        async def execute_preflight(self, **_kwargs: Any) -> Any:
            raise RuntimeError("preflight explosion")

    state_unexp = _build_state(
        steps=[causal_step],
        step_statuses={causal_step.id: ExecutionStatus.RUNNING},
    )
    repo.set_execution(state_unexp.exec_record)
    with pytest.raises(AppException) as exc_unexp:
        await execute_topological_waves_stage(
            state=state_unexp,
            node_executor=NodeExecutor(deps=_build_deps(repo)),
            committer=committer,
            rag_preflight=_FailingPreflight(),
        )
    assert exc_unexp.value.status_code == 500
    assert state_unexp.exec_record.step_states[causal_step.id].status == ExecutionStatus.FAILED


@pytest.mark.asyncio
async def test_execute_topological_waves_stage_traps_direct_runtime_error_and_app_exception_in_wave(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify non-AppException outer error marks RUNNING step FAILED and wave AppException re-raises."""
    from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService

    repo = InMemoryUnifiedWorkflowRepository()
    step_a = StepRule(id="stp_1111222233334444", task_blueprint="stp_1111222233334444", depends_on=[])
    state_app_exc = _build_state(steps=[step_a])
    repo.set_execution(state_app_exc.exec_record)
    committer = ExecutionCommitter(exec_repo=repo, execution_id=state_app_exc.execution_id)

    async def _app_exc_runner(_st: WorkflowExecutionState, _sid: str, *_args: Any) -> None:
        raise AppException(
            message="Domain step failure",
            status_code=422,
            details={"error_code": ErrorCodes.VALIDATION_FAILED},
        )

    with pytest.raises(AppException) as exc_wave_app:
        await execute_topological_waves_stage(
            state=state_app_exc,
            node_executor=NodeExecutor(deps=_build_deps(repo)),
            committer=committer,
            step_runner_fn=_app_exc_runner,
        )
    assert exc_wave_app.value.status_code == 422

    state_outer_rt = _build_state(
        steps=[step_a],
        step_statuses={step_a.id: ExecutionStatus.RUNNING},
    )
    repo.set_execution(state_outer_rt.exec_record)

    def _boom_waves(_steps: list[StepRule]) -> list[list[StepRule]]:
        raise RuntimeError("compiler crash while step running")

    monkeypatch.setattr(DAGCompilerService, "compute_topological_waves", _boom_waves)
    with pytest.raises(AppException) as exc_outer_rt:
        await execute_topological_waves_stage(
            state=state_outer_rt,
            node_executor=NodeExecutor(deps=_build_deps(repo)),
            committer=committer,
        )
    assert exc_outer_rt.value.status_code == 500
    assert state_outer_rt.exec_record.step_states[step_a.id].status == ExecutionStatus.FAILED
    assert state_outer_rt.exec_record.step_states[step_a.id].last_error == "compiler crash while step running"
