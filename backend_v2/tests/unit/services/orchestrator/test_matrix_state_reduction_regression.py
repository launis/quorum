"""Regression test for MatrixHookResultDTO reduction and scoring logic pipeline.

Reproduces the bug where:
1. MatrixHookResultDTO is reduced into HookState.global_context_vars.evaluative_matrices
   without emitting a decision TraceEvent (with is_context_update=True), causing the
   evaluative matrices to be discarded from dag_executor execution trace and context variables.
2. apply_scoring_logic_hook only checks state.inputs for '_evaluative_matrices' and ignores
   state.global_context_vars.evaluative_matrices, crashing with HTTP 500:
   "Strict Fail-Fast Enforced: '_evaluative_matrices' missing from state. Matrix normalization failed or was bypassed."
"""

from __future__ import annotations

import pytest

from backend_v2.core.hook_registry import HookDeltaDTO, HookState
from backend_v2.hooks.scoring.falsifier_hook import apply_scoring_logic_hook
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.hook_delta import MatrixHookResultDTO
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.dtos.lightweight_matrix import LightweightMatrixOutput
from backend_v2.models.dtos.trace import TraceScoringPayloadDTO
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.orchestrator.state_reducer import reduce_hook_delta
from backend_v2.tests.unit.hooks.test_scoring import (
    _build_test_scoring_deps,
    _create_test_scoring_repo,
)


def _build_test_hook_state(step_id: str = "st_matrix") -> HookState:
    """Build a standard HookState for matrix testing."""
    return HookState(
        execution_id="exec_0000000000000001",
        workflow_id="wf_1",
        step_id=step_id,
        task_blueprint=step_id,
        metadata=ExecutionMetadata(matrix_sampling_strategy=10, workflow_version=1),
        global_context_vars=GlobalContextVarsDTO(language="fi"),
        inputs=ExecutionInputsDTO(raw_inputs={"steps": []}),
    )


def test_reduce_hook_delta_matrix_must_emit_decision_trace_event() -> None:
    """RED TEST: reduce_hook_delta MUST emit a decision TraceEvent for MatrixHookResultDTO.

    Without this event, dag_executor does not update execution.context_variables and
    execution_trace lacks the decision event, causing evaluative_matrices to be lost
    across DAG step boundaries.
    """
    state = _build_test_hook_state()
    matrix_output = LightweightMatrixOutput(
        raw_score=4.0,
        normalized_score=80.0,
        evaluated_atoms={},
    )
    delta_dto = HookDeltaDTO(
        delta=MatrixHookResultDTO(
            matrix_outputs={"blk_1": matrix_output},
            missing_contexts={},
            atom_quotes={},
        )
    )

    new_state, emitted_events = reduce_hook_delta(state, delta_dto, step_id="st_matrix")

    # In current buggy code, emitted_events is []
    # This assertion EXPECTS emitted_events to contain the decision event for context updates!
    assert len(emitted_events) == 1, (
        f"Expected exactly 1 decision TraceEvent for MatrixHookResultDTO, but got {len(emitted_events)}. "
        "MatrixHookResultDTO reduction must emit a TraceEvent with is_context_update=True so that "
        "dag_executor commits evaluative_matrices into execution.context_variables and execution_trace."
    )

    evt = emitted_events[0]
    assert evt.event_type == "decision"
    assert evt.step_name == "st_matrix"
    assert evt.metadata.is_context_update is True
    assert type(evt.content) is dict
    assert "evaluative_matrices" in evt.content
    assert evt.content["evaluative_matrices"] == {"blk_1": 80.0}


@pytest.mark.asyncio
async def test_apply_scoring_logic_hook_reads_evaluative_matrices_from_global_context_vars() -> None:
    """RED TEST: apply_scoring_logic_hook MUST read evaluative_matrices from state.global_context_vars.

    When MatrixHookResultDTO is reduced into GlobalContextVarsDTO.evaluative_matrices,
    apply_scoring_logic_hook must extract these scores even if state.inputs lacks '_evaluative_matrices'.
    In current buggy code, this raises AppException with:
    "Strict Fail-Fast Enforced: '_evaluative_matrices' missing from state. Matrix normalization failed or was bypassed."
    """
    eval_matrices = {"blk_1": 80.0, "blk_2": 90.0}
    state = HookState(
        execution_id="exec_0000000000000001",
        workflow_id="wf_1",
        step_id="step_final",
        task_blueprint="step_final",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(evaluative_matrices=eval_matrices),
        inputs=ExecutionInputsDTO(dynamic_inputs={"steps": []}),
    )
    repo = await _create_test_scoring_repo()
    deps = _build_test_scoring_deps(repo)

    result = await apply_scoring_logic_hook(state, deps)
    assert result.success is True
    delta = result.state_delta.delta if isinstance(result.state_delta, HookDeltaDTO) else result.state_delta
    assert isinstance(delta, TraceScoringPayloadDTO)
    assert delta.total_score == 85.0
    assert delta.final_score == 85.0
