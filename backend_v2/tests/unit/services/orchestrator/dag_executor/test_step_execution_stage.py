"""Unit tests for backend_v2.services.orchestrator.dag_executor.step_execution_stage.

Verifies prepare_step_strategy_context (upstream causal graph extraction, validation
failures, and MatrixReducer invocation) and execute_dag_step_wrapper (resumption skip,
dependency blocking, progress_callback, NodeExecutor retry dispatch, and DLQ failure
recording).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any
from unittest.mock import patch

import pytest

from backend_v2.core.hook_registry import GlobalContextVarsDTO
from backend_v2.exceptions import AppException, ErrorCodes, WorkflowExecutionError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import (
    ExecutionRecord,
    ExecutionStep,
    FrozenContext,
)
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.causal_discovery import (
    CausalGraphPayloadDTO,
    CausalNodeDTO,
)
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.node_execution import StepOutputContentDTO
from backend_v2.models.dtos.trace import TraceEventMetadataDTO
from backend_v2.models.enums import EngineType, ExecutionStatus, HistoricalContextMode, StepType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent, StateProjector, TraceEvent
from backend_v2.services.orchestrator.dag_executor.execution_committer import ExecutionCommitter
from backend_v2.services.orchestrator.dag_executor.node_executor import NodeExecutor
from backend_v2.services.orchestrator.dag_executor.step_execution_stage import (
    _extract_app_exception_error_code,
    _parse_causal_graph_candidate,
    _resolve_matrix_reducer,
    execute_dag_step_wrapper,
    prepare_step_strategy_context,
)
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    WorkflowExecutionState,
    dlq_fallback_step_exceptions,
)
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
    step_definitions: dict[str, Step],
    step_statuses: dict[str, ExecutionStatus] | None = None,
    trace: list[TraceEvent] | None = None,
) -> WorkflowExecutionState:
    wf = Workflow(
        id="wf_0195f3a0000070018111222233334444",
        slug="wf_step_exec",
        name=I18nText(translations={"en": "Step Exec WF", "fi": "Step Exec WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        status="active",
        version=1,
        historical_context_mode=HistoricalContextMode.DISABLED,
        default_profile_id="prf_0195f3a0000070018111222233334444",
        model_registry_id="sys_0195f3a0000070018111222233334444",
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
        id="exe_0195f3a0000070018111222233334444",
        workflow_id=wf.id,
        target_locale="en",
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "input"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.RUNNING,
        steps=exec_steps,
        step_states={s.id: s for s in exec_steps},
        execution_trace=list(trace) if trace else [],
        metadata=ExecutionMetadata(
            workflow_version=1,
            model_registry_id="sys_0195f3a0000070018111222233334444",
            global_context_vars=GlobalContextVarsDTO(language="en", target_locale="en"),
        ),
    )
    projector = StateProjector()
    for evt in rec.execution_trace:
        projector.apply_delta(evt)
    return WorkflowExecutionState(
        execution_id=rec.id,
        workflow=wf,
        exec_record=rec,
        global_context_vars=GlobalContextVarsDTO(language="en", target_locale="en"),
        projector=projector,
        step_definitions=step_definitions,
        steps_by_id={s.id: s for s in steps},
        step_exceptions=dlq_fallback_step_exceptions(),
    )


@pytest.mark.asyncio
async def test_execute_dag_step_wrapper_reduces_matrix_and_commits_trace() -> None:
    """Contract: execute_dag_step_wrapper prepares context, reduces matrix, runs NodeExecutor, and commits trace."""
    repo = InMemoryUnifiedWorkflowRepository()
    bp = Step(
        id="stp_0195f3a0000070018111222233334444",
        slug="synth_step",
        name=I18nText(translations={"en": "Synth", "fi": "Synteesi"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LOGIC,
        hook="custom_logic_hook",
        engine_type=EngineType.SYNTHESIS,
        pre_hooks=["synthesis_distiller_hook"],
        mcp_tool_params={},
    )
    step_rule = StepRule(
        id="stp_0195f3a00000700a8aaa1111bbbb2222",
        task_blueprint=bp.id,
        depends_on=[],
        input_mappings={},
    )
    state = _build_state(steps=[step_rule], step_definitions={bp.id: bp})
    repo.set_execution(state.exec_record)
    committer = ExecutionCommitter(exec_repo=repo, execution_id=state.execution_id)

    class _FakeNodeExecutor(NodeExecutor):
        async def execute(
            self,
            step: StepRule,
            execution_id: str,
            workflow_id: str,
            metadata: ExecutionMetadata,
            projector: StateProjector,
            expected_inputs: list[Any] | None = None,
            frozen_ctx: FrozenContext | None = None,
            trace: list[TraceEvent] | None = None,
            strictness_level: int = 50,
            lexical_strictness_level: int = 50,
            arq_pool: Any | None = None,
            context_variables: ContextVariablesDTO | None = None,
            progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
            step_def: Step | None = None,
            global_context_vars: GlobalContextVarsDTO | None = None,
            target_locale: str = "en",
            output_profile_id: str | None = None,
            organization_id: str | None = None,
        ) -> list[TraceEvent]:
            _ = (
                execution_id,
                workflow_id,
                metadata,
                projector,
                expected_inputs,
                frozen_ctx,
                trace,
                strictness_level,
                lexical_strictness_level,
                arq_pool,
                context_variables,
                step_def,
                global_context_vars,
                target_locale,
                output_profile_id,
                organization_id,
            )
            if progress_callback is not None:
                await progress_callback(0, 0)
                await progress_callback(1, 2)
                repo.inject_fault("update_execution", OSError("transient progress error"))
                try:
                    await progress_callback(100, 100)
                finally:
                    repo.clear_faults()
            return [
                TraceEvent(
                    step_name=step.id,
                    event_type="output",
                    content={"summary": "completed"},
                    metadata=TraceEventMetadataDTO(generated_schema={"type": "object"}),
                )
            ]

    reduced_dto = LightweightMatrixOutput(
        raw_score=4.5,
        normalized_score=85.0,
        justification="Reduced",
        evaluated_atoms={},
        extensions={},
    )
    progress_errors: list[tuple[str, Exception]] = []

    with patch(
        "backend_v2.services.orchestrator.dag_executor.MatrixReducer.reduce_matrix",
        return_value=reduced_dto,
    ) as mock_reduce:
        await execute_dag_step_wrapper(
            state=state,
            step_id=step_rule.id,
            node_executor=_FakeNodeExecutor(deps=_build_deps(repo)),
            committer=committer,
            dlq_on_progress_commit_error=lambda sid, err: progress_errors.append((sid, err)),
        )

    mock_reduce.assert_called_once()
    assert len(progress_errors) == 1
    assert state.exec_record.step_states[step_rule.id].status == ExecutionStatus.PASSED
    assert state.exec_record.context_variables.matrix_reducer_output == reduced_dto
    assert state.exec_record.frozen_context is not None
    assert step_rule.id in state.exec_record.frozen_context.generated_schemas.schemas


@pytest.mark.asyncio
async def test_prepare_step_strategy_context_upstream_causal_graph_and_failure_branches() -> None:
    """Verify prepare_step_strategy_context extracts causal graphs from trace/snapshot and enforces fail-fast gates."""
    causal_step = StepRule(
        id="stp_0195f3a0000070018111222233334444", task_blueprint="stp_0195f3a0000070018111222233334444"
    )
    tda_step = StepRule(
        id="stp_0195f3a0000070058555666677778888",
        task_blueprint="stp_0195f3a0000070058555666677778888",
        depends_on=[causal_step.id],
        causal_source_step_id=causal_step.id,
    )
    graph = CausalGraphPayloadDTO(
        nodes=[
            CausalNodeDTO(
                node_id="tda_0195f3a0000070018111222233334444",
                claim="Claim A",
                source_quotes=("Quote A",),
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

    # 1. Valid causal graph extracted from projector.snapshot (direct CausalGraphPayloadDTO)
    state_snap = _build_state(
        steps=[causal_step, tda_step],
        step_definitions={},
        step_statuses={causal_step.id: ExecutionStatus.PASSED},
    )
    state_snap.projector.apply_delta(TraceEvent(step_name=causal_step.id, event_type="output", content=graph))
    resolved_graph, _ = await prepare_step_strategy_context(state=state_snap, step_id=tda_step.id)
    assert resolved_graph is not None
    assert len(resolved_graph.nodes) == 1
    assert state_snap.global_context_vars.shuffled_atoms is not None
    assert len(state_snap.global_context_vars.shuffled_atoms) == 1

    # 1b. Valid causal graph extracted from trace wrapped in StepOutputContentDTO
    state_wrapped = _build_state(
        steps=[causal_step, tda_step],
        step_definitions={},
        step_statuses={causal_step.id: ExecutionStatus.PASSED},
        trace=[
            TraceEvent(
                step_name=causal_step.id,
                event_type="output",
                content=StepOutputContentDTO(data={"graph": graph.model_dump(mode="json")}),
            )
        ],
    )
    resolved_wrapped, _ = await prepare_step_strategy_context(state=state_wrapped, step_id=tda_step.id)
    assert resolved_wrapped is not None
    assert len(resolved_wrapped.nodes) == 1

    # 2. Missing causal_source_step_id in workflow steps_by_id raises VALIDATION_FAILED
    state_bad_ref = _build_state(steps=[causal_step, tda_step], step_definitions={})
    del state_bad_ref.steps_by_id[causal_step.id]
    with pytest.raises(AppException) as exc_bad_ref:
        await prepare_step_strategy_context(state=state_bad_ref, step_id=tda_step.id)
    assert exc_bad_ref.value.status_code == 400

    # 3. Upstream step not PASSED raises CAUSAL_DISCOVERY_DATA_STARVATION
    state_not_passed = _build_state(
        steps=[causal_step, tda_step],
        step_definitions={},
        step_statuses={causal_step.id: ExecutionStatus.FAILED},
    )
    with pytest.raises(AppException) as exc_starve:
        await prepare_step_strategy_context(state=state_not_passed, step_id=tda_step.id)
    assert exc_starve.value.details["error_code"] == ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION

    # 4. Malformed graph in trace raises VALIDATION_FAILED
    state_bad_trace = _build_state(
        steps=[causal_step, tda_step],
        step_definitions={},
        step_statuses={causal_step.id: ExecutionStatus.PASSED},
        trace=[TraceEvent(step_name=causal_step.id, event_type="output", content={"graph": {"nodes": "invalid"}})],
    )
    with pytest.raises(AppException) as exc_parse:
        await prepare_step_strategy_context(state=state_bad_trace, step_id=tda_step.id)
    assert exc_parse.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    # 5. Empty graph nodes raises CAUSAL_DISCOVERY_DATA_STARVATION
    empty_graph = graph.model_copy(update={"nodes": []})
    state_empty_nodes = _build_state(
        steps=[causal_step, tda_step],
        step_definitions={},
        step_statuses={causal_step.id: ExecutionStatus.PASSED},
        trace=[TraceEvent(step_name=causal_step.id, event_type="output", content=empty_graph)],
    )
    with pytest.raises(AppException) as exc_empty_nodes:
        await prepare_step_strategy_context(state=state_empty_nodes, step_id=tda_step.id)
    assert exc_empty_nodes.value.details["error_code"] == ErrorCodes.CAUSAL_DISCOVERY_DATA_STARVATION

    # 6. MatrixReducer failure raises WorkflowExecutionError
    bp = Step(
        id="stp_0195f3a0000070058555666677778888",
        slug="synth_fail",
        name=I18nText(translations={"en": "Synth", "fi": "Synteesi"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LOGIC,
        hook="custom_logic_hook",
        engine_type=EngineType.SYNTHESIS,
        pre_hooks=["atom_flattening_hook"],
        mcp_tool_params={},
    )
    synth_rule = StepRule(id="stp_0195f3a00000700a8aaa1111bbbb2222", task_blueprint=bp.id)
    state_red_fail = _build_state(steps=[synth_rule], step_definitions={bp.id: bp})
    with (
        patch(
            "backend_v2.services.orchestrator.dag_executor.MatrixReducer.reduce_matrix",
            side_effect=RuntimeError("reducer crash"),
        ),
        pytest.raises(WorkflowExecutionError),
    ):
        await prepare_step_strategy_context(state=state_red_fail, step_id=synth_rule.id)


@pytest.mark.asyncio
async def test_execute_dag_step_wrapper_resumption_skip_blocked_dependency_and_error_recording() -> None:
    """Verify execute_dag_step_wrapper skips PASSED steps, blocks on failed dependencies, and records step errors."""
    repo = InMemoryUnifiedWorkflowRepository()
    dep_step = StepRule(
        id="stp_0195f3a0000070018111222233334444", task_blueprint="stp_0195f3a0000070018111222233334444"
    )
    child_step = StepRule(
        id="stp_0195f3a0000070058555666677778888",
        task_blueprint="stp_0195f3a0000070018111222233334444",
        depends_on=[dep_step.id],
    )

    # 1. Resumption skip when step is already PASSED
    state_passed = _build_state(
        steps=[dep_step],
        step_definitions={},
        step_statuses={dep_step.id: ExecutionStatus.PASSED},
    )
    committer = ExecutionCommitter(exec_repo=repo, execution_id=state_passed.execution_id)
    await execute_dag_step_wrapper(
        state=state_passed,
        step_id=dep_step.id,
        node_executor=NodeExecutor(deps=_build_deps(repo)),
        committer=committer,
    )
    assert repo.get_call_count("update_execution") == 0

    # 2. Dependency not PASSED marks child step BLOCKED
    state_blocked = _build_state(
        steps=[dep_step, child_step],
        step_definitions={},
        step_statuses={dep_step.id: ExecutionStatus.FAILED, child_step.id: ExecutionStatus.PENDING},
    )
    repo.set_execution(state_blocked.exec_record)
    await execute_dag_step_wrapper(
        state=state_blocked,
        step_id=child_step.id,
        node_executor=NodeExecutor(deps=_build_deps(repo)),
        committer=committer,
    )
    assert state_blocked.exec_record.step_states[child_step.id].status == ExecutionStatus.BLOCKED

    # 3. Step raising known step_exceptions (AppException) appends ErrorTraceEvent and records FAILED
    class _AppExcNodeExecutor(NodeExecutor):
        async def execute(self, *args: Any, **kwargs: Any) -> list[TraceEvent]:
            _ = (args, kwargs)
            raise AppException(
                message="validation error", status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED}
            )

    state_app_err = _build_state(steps=[dep_step], step_definitions={})
    repo.set_execution(state_app_err.exec_record)
    app_dlq_calls: list[tuple[str, str]] = []
    with pytest.raises(AppException):
        await execute_dag_step_wrapper(
            state=state_app_err,
            step_id=dep_step.id,
            node_executor=_AppExcNodeExecutor(deps=_build_deps(repo)),
            committer=committer,
            dlq_on_step_failure=lambda sid, code, _exc: app_dlq_calls.append((sid, code)),
        )
    assert state_app_err.exec_record.step_states[dep_step.id].status == ExecutionStatus.FAILED
    assert app_dlq_calls == [(dep_step.id, "VALIDATION_FAILED")]
    assert any(isinstance(evt, ErrorTraceEvent) for evt in state_app_err.exec_record.execution_trace)

    # 4. Step raising unexpected exception records FAILED status
    class _UnexpectedCrashException(Exception):
        pass

    class _CrashingNodeExecutor(NodeExecutor):
        async def execute(self, *args: Any, **kwargs: Any) -> list[TraceEvent]:
            _ = (args, kwargs)
            raise _UnexpectedCrashException("unexpected step boom")

    state_crash = _build_state(steps=[dep_step], step_definitions={})
    repo.set_execution(state_crash.exec_record)
    dlq_calls: list[tuple[str, str]] = []
    with pytest.raises(_UnexpectedCrashException):
        await execute_dag_step_wrapper(
            state=state_crash,
            step_id=dep_step.id,
            node_executor=_CrashingNodeExecutor(deps=_build_deps(repo)),
            committer=committer,
            dlq_on_step_failure=lambda sid, code, _exc: dlq_calls.append((sid, code)),
        )
    assert state_crash.exec_record.step_states[dep_step.id].status == ExecutionStatus.FAILED
    assert dlq_calls == [(dep_step.id, "UNEXPECTED_STEP_EXCEPTION")]

    # Verify _extract_app_exception_error_code branches
    class _EnumCodeAppException(AppException):
        @property
        def error_code(self) -> ErrorCodes:
            return ErrorCodes.VALIDATION_FAILED

    assert _extract_app_exception_error_code(_EnumCodeAppException(message="err", status_code=400)) == (
        "VALIDATION_FAILED"
    )
    app_exc_details_enum = AppException(
        message="err", status_code=400, details={"error_code": ErrorCodes.VALIDATION_FAILED}
    )
    assert _extract_app_exception_error_code(app_exc_details_enum) == "VALIDATION_FAILED"
    app_exc_str = AppException(message="err", status_code=400, details={"error_code": "CUSTOM_STR_CODE"})
    assert _extract_app_exception_error_code(app_exc_str) == "CUSTOM_STR_CODE"

    # Verify _parse_causal_graph_candidate direct CausalGraphPayloadDTO branch and snapshot dict branch
    causal_step_snap = StepRule(
        id="stp_0195f3a0000070018111222233334444", task_blueprint="stp_0195f3a0000070018111222233334444"
    )
    tda_step_snap = StepRule(
        id="stp_0195f3a0000070058555666677778888",
        task_blueprint="stp_0195f3a0000070058555666677778888",
        depends_on=[causal_step_snap.id],
        causal_source_step_id=causal_step_snap.id,
    )
    graph_dto = CausalGraphPayloadDTO(
        nodes=[
            CausalNodeDTO(
                node_id="tda_0195f3a0000070018111222233334444",
                claim="Claim A",
                source_quotes=("Quote A",),
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
    assert _parse_causal_graph_candidate(StepOutputContentDTO(data={"graph": graph_dto}), "err") == graph_dto

    state_snap_raw = _build_state(
        steps=[causal_step_snap, tda_step_snap],
        step_definitions={},
        step_statuses={causal_step_snap.id: ExecutionStatus.PASSED},
    )
    state_snap_raw.projector.apply_delta(
        TraceEvent(
            step_name=causal_step_snap.id,
            event_type="output",
            content=StepOutputContentDTO(data={"graph": graph_dto.model_dump(mode="json")}),
        )
    )
    snap_resolved, _ = await prepare_step_strategy_context(state=state_snap_raw, step_id=tda_step_snap.id)
    assert snap_resolved is not None
    assert len(snap_resolved.nodes) == 1

    # Verify snapshot malformed payload raises AppException (VALIDATION_FAILED)
    state_snap_invalid = _build_state(
        steps=[causal_step_snap, tda_step_snap],
        step_definitions={},
        step_statuses={causal_step_snap.id: ExecutionStatus.PASSED},
    )
    state_snap_invalid.projector.apply_delta(
        TraceEvent(
            step_name=causal_step_snap.id,
            event_type="output",
            content=StepOutputContentDTO(data={"graph": {"nodes": "malformed_nodes"}}),
        )
    )
    with pytest.raises(AppException) as exc_snap_invalid:
        await prepare_step_strategy_context(state=state_snap_invalid, step_id=tda_step_snap.id)
    assert exc_snap_invalid.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    # Verify _resolve_matrix_reducer fallback when facade module is not in sys.modules
    with patch(
        "backend_v2.services.orchestrator.dag_executor.step_execution_stage._DAG_EXECUTOR_MODULE",
        "__unloaded_dag_executor__",
    ):
        assert _resolve_matrix_reducer() is not None
