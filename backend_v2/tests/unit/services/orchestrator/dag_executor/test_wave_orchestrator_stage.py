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
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.prompt_blocks import AnyPromptBlock, MatrixPromptBlock
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
from backend_v2.models.enums import (
    BlockDataType,
    CognitiveTier,
    ExecutionStatus,
    HistoricalContextMode,
    PromptBlockCategory,
    StepType,
)
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
    blocks_by_id: dict[str, AnyPromptBlock] | None = None,
) -> WorkflowExecutionState:
    wf = Workflow(
        organization_id="org_0195f3a0000070008000000000000001",
        id="wf_0195f3a0000070008000111122223333",
        slug="wf_wave_orch",
        name=I18nText(translations={"en": "Wave WF", "fi": "Aalto WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        status="active",
        version=1,
        historical_context_mode=HistoricalContextMode.DISABLED,
        default_profile_id="prf_0195f3a0000070008000111122223333",
        model_registry_id="mrg_0195f3a0000070008000111122223333",
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
        id="exe_0195f3a0000070008000111122223333",
        workflow_id=wf.id,
        target_locale="en",
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "input"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.RUNNING,
        steps=exec_steps,
        execution_trace=[],
        metadata=ExecutionMetadata(
            workflow_version=1,
            model_registry_id="mrg_0195f3a0000070008000111122223333",
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
        blocks_by_id=blocks_by_id or {},
        steps_by_id={s.id: s for s in steps},
        step_exceptions=dlq_fallback_step_exceptions(),
    )


@pytest.mark.asyncio
async def test_execute_topological_waves_stage_runs_parallel_wave_steps() -> None:
    """Contract: execute_topological_waves_stage dispatches independent wave steps concurrently inside TaskGroup."""
    repo = InMemoryUnifiedWorkflowRepository()
    step_a = StepRule(
        id="stp_0195f3a0000070008000111111111111", task_blueprint="stp_0195f3a0000070008000111111111111", depends_on=[]
    )
    step_b = StepRule(
        id="stp_0195f3a0000070008000222222222222", task_blueprint="stp_0195f3a0000070008000111111111111", depends_on=[]
    )
    step_c = StepRule(
        id="stp_0195f3a0000070008000333333333333",
        task_blueprint="stp_0195f3a0000070008000111111111111",
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
    steps_by_id = {s.id: s for s in record.steps}
    assert steps_by_id[step_a.id].status == ExecutionStatus.PASSED
    assert steps_by_id[step_b.id].status == ExecutionStatus.PASSED
    assert steps_by_id[step_c.id].status == ExecutionStatus.PASSED


@pytest.mark.asyncio
async def test_execute_topological_waves_stage_marks_downstream_steps_blocked_on_failure() -> None:
    """Contract: execute_topological_waves_stage traps step exceptions, marks downstream steps BLOCKED, and re-raises."""
    repo = InMemoryUnifiedWorkflowRepository()
    step_fail = StepRule(
        id="stp_0195f3a0000070008000111111111111", task_blueprint="stp_0195f3a0000070008000111111111111", depends_on=[]
    )
    step_sibling = StepRule(
        id="stp_0195f3a0000070008000222222222222", task_blueprint="stp_0195f3a0000070008000111111111111", depends_on=[]
    )
    step_downstream = StepRule(
        id="stp_0195f3a0000070008000333333333333",
        task_blueprint="stp_0195f3a0000070008000111111111111",
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
    steps_by_id = {s.id: s for s in state.exec_record.steps}
    assert steps_by_id[step_fail.id].status == ExecutionStatus.FAILED
    assert steps_by_id[step_sibling.id].status == ExecutionStatus.FAILED
    assert steps_by_id[step_downstream.id].status == ExecutionStatus.BLOCKED
    dlq_ids = {sid for sid, _ in dlq_events}
    assert {step_fail.id, step_sibling.id, step_downstream.id}.issubset(dlq_ids)


@pytest.mark.asyncio
async def test_finalize_step_output_and_commit_causal_fusion_cohesion_and_context_updates() -> None:
    """Verify finalize_step_output_and_commit evaluates causal TDA fusion, updates context vars, and deduplicates MCP."""
    repo = InMemoryUnifiedWorkflowRepository()
    causal_step = StepRule(
        id="stp_0195f3a0000070008000111122223333",
        task_blueprint="stp_0195f3a0000070008000111122223333",
    )
    tda_step = StepRule(
        id="stp_0195f3a0000070008000555566667777",
        task_blueprint="stp_0195f3a0000070008000555566667777",
        depends_on=[causal_step.id],
        causal_source_step_id=causal_step.id,
    )
    cohesion_mat_id = "blk_0195f3a0000070008000440a5fef9331"
    cohesion_mat = MatrixPromptBlock(
        organization_id="org_0195f3a0000070008000000000000001",
        id=cohesion_mat_id,
        slug="mat_causal_cohesion",
        label=I18nText(translations={"en": "Causal Cohesion", "fi": "Kausaalinen koheesio"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        category_id=PromptBlockCategory.MATRIX,
        type=BlockDataType.FLOAT,
        scales=[
            MatrixScale(
                score=lvl,
                ai_label=f"L{lvl}",
                claims=[
                    MatrixClaim(
                        label=I18nText(translations={"en": f"Claim L{lvl}"}),
                        tda_assertions=[
                            TDAAssertion(
                                tda_id=f"tda_0195f3a000007000880000000000000{lvl}",
                                inverse_evidence=False,
                                aggregation_mode="EXISTS",
                                concept_description=f"Causal cohesion assertion for level {lvl}",
                                extraction_rule=f"Rule L{lvl}",
                                depends_on=(),
                            )
                        ],
                    )
                ],
            )
            for lvl in range(1, 6)
        ],
    )
    causal_bp = Step(
        organization_id="org_0195f3a0000070008000000000000001",
        id=causal_step.task_blueprint,
        slug="step_causal",
        name=I18nText(translations={"en": "Causal Step", "fi": "Kausaaliaskel"}),
        type=StepType.CAUSAL_DISCOVERY,
        extraction_protocol_block_id="blk_0195f3a0000070008000abcdef012345",
        criteria_block_ids=[cohesion_mat_id],
        cognitive_tier=CognitiveTier.FAST,
        mcp_tool_params={},
    )
    state = _build_state(
        steps=[causal_step, tda_step],
        step_definitions={causal_bp.id: causal_bp},
        step_statuses={causal_step.id: ExecutionStatus.PASSED, tda_step.id: ExecutionStatus.RUNNING},
        blocks_by_id={cohesion_mat_id: cohesion_mat},
    )
    repo.set_execution(state.exec_record)
    committer = ExecutionCommitter(exec_repo=repo, execution_id=state.execution_id)

    graph = CausalGraphPayloadDTO(
        nodes=[
            CausalNodeDTO(
                node_id="tda_0195f3a0000070008000111122223333",
                claim="Claim 1",
                source_quotes=("Quote 1",),
                paragraph_ref="P1",
                status=ExecutionStatus.PASSED,
                blame_parent_ids=[],
                dependent_child_ids=[],
                short_circuited_by_claims=[],
                falsified_warrant_claims=[],
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
        tda_id="tda_0195f3a0000070008000111122223333",
        status=ExecutionStatus.PASSED,
        evaluation_reasoning="Valid evidence",
        source_quotes=("Quote 1",),
        extracted_data=ExtractedValueDTO(value=4.0),
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    mcp_trace = MCPAuditTrace(
        id="tr_0195f3a0000070018111222233334444",
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
                evaluative_matrices={"blk_0195f3a0000070008000111122223333": 80.0},
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

    assert next(s for s in state.exec_record.steps if s.id == tda_step.id).status == ExecutionStatus.PASSED
    assert state.global_context_vars.passivity_detected is True
    assert state.global_context_vars.evaluative_matrices is not None
    assert "blk_0195f3a0000070008000111122223333" in state.global_context_vars.evaluative_matrices
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
    assert next(s for s in state_unexp.exec_record.steps if s.id == causal_step.id).status == ExecutionStatus.FAILED


@pytest.mark.asyncio
async def test_execute_topological_waves_stage_traps_direct_runtime_error_and_app_exception_in_wave(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify non-AppException outer error marks RUNNING step FAILED and wave AppException re-raises."""
    from backend_v2.services.orchestrator.dag_compiler import DAGCompilerService

    repo = InMemoryUnifiedWorkflowRepository()
    step_a = StepRule(
        id="stp_0195f3a0000070008000111122223333", task_blueprint="stp_0195f3a0000070008000111122223333", depends_on=[]
    )
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
    outer_step = next(s for s in state_outer_rt.exec_record.steps if s.id == step_a.id)
    assert outer_step.status == ExecutionStatus.FAILED
    assert outer_step.last_error == "compiler crash while step running"


@pytest.mark.asyncio
async def test_wave_orchestrator_stage_raises_quota_exceeded_when_tokens_or_cost_breach_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify per-run ExecutionBudget ceilings (tokens, USD cost, step count) and boundary behavior."""
    from unittest.mock import MagicMock

    import backend_v2.services.orchestrator.dag_executor.wave_orchestrator_stage as wave_mod
    from backend_v2.settings import Settings

    # Verify Settings validator rejects negative max_cost_usd_per_run
    with pytest.raises(ValueError, match="max_cost_usd_per_run"):
        Settings.validate_max_cost_usd_per_run_non_negative(-0.01)
    assert Settings.validate_max_cost_usd_per_run_non_negative(0.0) == 0.0
    assert Settings.validate_max_cost_usd_per_run_non_negative(25.0) == 25.0

    repo = InMemoryUnifiedWorkflowRepository()
    step_1 = StepRule(
        id="stp_0195f3a0000070008000111111111111", task_blueprint="stp_0195f3a0000070008000111111111111", depends_on=[]
    )
    step_2 = StepRule(
        id="stp_0195f3a0000070008000222222222222",
        task_blueprint="stp_0195f3a0000070008000111111111111",
        depends_on=[step_1.id],
    )

    mock_settings = MagicMock()
    mock_settings.max_tokens_per_run = 5000
    mock_settings.max_cost_usd_per_run = 25.0
    mock_settings.max_total_steps_per_run = 50
    monkeypatch.setattr(wave_mod, "get_settings", lambda: mock_settings)

    # 1. Boundary: exactly 5000 tokens (limit) proceeds cleanly
    state_ok = _build_state(steps=[step_1])
    state_ok.exec_record = state_ok.exec_record.model_copy(
        update={"prompt_tokens": 3000, "completion_tokens": 1500, "reasoning_tokens": 500}
    )
    repo.set_execution(state_ok.exec_record)
    committer_ok = ExecutionCommitter(exec_repo=repo, execution_id=state_ok.execution_id)

    async def _pass_runner(st: WorkflowExecutionState, sid: str, *_args: Any) -> None:
        st.exec_record = st.exec_record.transition_step(step_id=sid, status=ExecutionStatus.PASSED, progress=100)

    res_ok = await execute_topological_waves_stage(
        state=state_ok,
        node_executor=NodeExecutor(deps=_build_deps(repo)),
        committer=committer_ok,
        step_runner_fn=_pass_runner,
    )
    assert next(s for s in res_ok.steps if s.id == step_1.id).status == ExecutionStatus.PASSED

    # 2. Negative: 5001 tokens (limit + 1) raises QUOTA_EXCEEDED (429) and marks PENDING steps BLOCKED
    state_tok = _build_state(steps=[step_1, step_2])
    state_tok.exec_record = state_tok.exec_record.model_copy(update={"prompt_tokens": 4000, "completion_tokens": 1001})
    repo.set_execution(state_tok.exec_record)
    committer_tok = ExecutionCommitter(exec_repo=repo, execution_id=state_tok.execution_id)

    with pytest.raises(AppException) as exc_tok:
        await execute_topological_waves_stage(
            state=state_tok,
            node_executor=NodeExecutor(deps=_build_deps(repo)),
            committer=committer_tok,
            step_runner_fn=_pass_runner,
        )
    assert exc_tok.value.status_code == 429
    assert exc_tok.value.details["error_code"] == ErrorCodes.QUOTA_EXCEEDED
    assert state_tok.exec_record.status == ExecutionStatus.FAILED
    tok_steps = {s.id: s for s in state_tok.exec_record.steps}
    assert tok_steps[step_1.id].status == ExecutionStatus.BLOCKED
    assert tok_steps[step_2.id].status == ExecutionStatus.BLOCKED

    # 3. Negative: Cost breach after wave 1 completes blocks wave 2
    mock_settings.max_tokens_per_run = 0
    mock_settings.max_cost_usd_per_run = 10.0
    state_cost = _build_state(steps=[step_1, step_2])
    repo.set_execution(state_cost.exec_record)
    committer_cost = ExecutionCommitter(exec_repo=repo, execution_id=state_cost.execution_id)

    async def _cost_spike_runner(st: WorkflowExecutionState, sid: str, *_args: Any) -> None:
        st.exec_record = st.exec_record.transition_step(step_id=sid, status=ExecutionStatus.PASSED, progress=100)
        st.exec_record = st.exec_record.model_copy(update={"dag_cost_usd": 10.01})

    with pytest.raises(AppException) as exc_cost:
        await execute_topological_waves_stage(
            state=state_cost,
            node_executor=NodeExecutor(deps=_build_deps(repo)),
            committer=committer_cost,
            step_runner_fn=_cost_spike_runner,
        )
    assert exc_cost.value.status_code == 429
    assert exc_cost.value.details["error_code"] == ErrorCodes.QUOTA_EXCEEDED
    cost_steps = {s.id: s for s in state_cost.exec_record.steps}
    assert cost_steps[step_1.id].status == ExecutionStatus.PASSED
    assert cost_steps[step_2.id].status == ExecutionStatus.BLOCKED

    # 4. Negative: Step count breach (max_total_steps_per_run = 1) after wave 1 completes
    mock_settings.max_cost_usd_per_run = 0.0
    mock_settings.max_total_steps_per_run = 1
    step_1b = StepRule(
        id="stp_0195f3a0000070008000333333333333", task_blueprint="stp_0195f3a0000070008000111111111111", depends_on=[]
    )
    state_steps = _build_state(steps=[step_1, step_1b, step_2])
    repo.set_execution(state_steps.exec_record)
    committer_steps = ExecutionCommitter(exec_repo=repo, execution_id=state_steps.execution_id)

    with pytest.raises(AppException) as exc_steps:
        await execute_topological_waves_stage(
            state=state_steps,
            node_executor=NodeExecutor(deps=_build_deps(repo)),
            committer=committer_steps,
            step_runner_fn=_pass_runner,
        )
    assert exc_steps.value.status_code == 429
    assert exc_steps.value.details["error_code"] == ErrorCodes.QUOTA_EXCEEDED
    assert next(s for s in state_steps.exec_record.steps if s.id == step_2.id).status == ExecutionStatus.BLOCKED
