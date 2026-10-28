"""Unit tests for the backend_v2.services.orchestrator.dag_executor package facade.

Verifies that replacing dag_executor.py with dag_executor/__init__.py preserves all
public and test-patchable symbol exports, DAGExecutor initialization and DLQ static
methods, and end-to-end execute_workflow delegation.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

import backend_v2.services.orchestrator.dag_executor as dag_executor_pkg
from backend_v2.core.hook_registry import ExecutionInputsDTO, HookDeltaDTO, HookResult
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import EngineType, ExecutionStatus, HistoricalContextMode, StepType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.services.orchestrator.dag_executor import (
    DAGExecutor,
    ExecutionCommitter,
    ExecutionRecordUpdate,
    FrozenContextUpdate,
    MatrixReducer,
    NodeExecutor,
    NodeStrategyFactory,
    StepOutputContentValue,
    WorkflowExecutionState,
    bootstrap_workflow_execution_state,
    compute_causal_tda_fusion_result,
    dlq_fallback_step_exceptions,
    dlq_handle_progress_commit_error,
    dlq_record_step_failure,
    execute_dag_step_wrapper,
    execute_rag_preflight_stage,
    execute_topological_waves_stage,
    finalize_step_output_and_commit,
    get_settings,
    hook_registry,
    prepare_step_strategy_context,
    safe_commit_execution_state,
    transform_causal_nodes_to_atoms,
)
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _build_dag_executor(repo: InMemoryUnifiedWorkflowRepository) -> DAGExecutor:
    compiler = PromptCompiler()
    rag_preflight = RAGPreflightService(
        workflow_repo=repo,
        system_repo=repo,
        prompt_compiler=compiler,
    )
    return DAGExecutor(
        exec_repo=repo,
        workflow_repo=repo,
        comp_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=compiler,
        rag_preflight=rag_preflight,
    )


def test_dag_executor_package_facade_reexports_all_public_symbols() -> None:
    """Contract: importing public and patchable symbols from dag_executor package works identically."""
    expected_exports = {
        "DAGExecutor",
        "ExecutionCommitter",
        "ExecutionRecordUpdate",
        "FrozenContextUpdate",
        "MatrixReducer",
        "NodeExecutor",
        "NodeStrategyFactory",
        "Step",
        "StepOutputContentValue",
        "WorkflowExecutionState",
        "bootstrap_workflow_execution_state",
        "compute_causal_tda_fusion_result",
        "dlq_fallback_step_exceptions",
        "dlq_handle_progress_commit_error",
        "dlq_record_step_failure",
        "execute_dag_step_wrapper",
        "execute_rag_preflight_stage",
        "execute_topological_waves_stage",
        "finalize_step_output_and_commit",
        "get_settings",
        "hook_registry",
        "prepare_step_strategy_context",
        "safe_commit_execution_state",
        "transform_causal_nodes_to_atoms",
    }
    assert set(dag_executor_pkg.__all__) == expected_exports
    reexported_objects = (
        DAGExecutor,
        ExecutionCommitter,
        ExecutionRecordUpdate,
        FrozenContextUpdate,
        MatrixReducer,
        NodeExecutor,
        NodeStrategyFactory,
        dag_executor_pkg.Step,
        StepOutputContentValue,
        WorkflowExecutionState,
        bootstrap_workflow_execution_state,
        compute_causal_tda_fusion_result,
        dlq_fallback_step_exceptions,
        dlq_handle_progress_commit_error,
        dlq_record_step_failure,
        execute_dag_step_wrapper,
        execute_rag_preflight_stage,
        execute_topological_waves_stage,
        finalize_step_output_and_commit,
        get_settings,
        hook_registry,
        prepare_step_strategy_context,
        safe_commit_execution_state,
        transform_causal_nodes_to_atoms,
    )
    assert len(reexported_objects) == len(expected_exports)
    assert all(obj is not None for obj in reexported_objects)
    assert DAGExecutor is dag_executor_pkg.DAGExecutor
    assert ExecutionCommitter is dag_executor_pkg.ExecutionCommitter
    assert NodeExecutor is dag_executor_pkg.NodeExecutor
    assert callable(compute_causal_tda_fusion_result)
    assert callable(transform_causal_nodes_to_atoms)


def test_dag_executor_initialization_and_dlq_static_methods() -> None:
    """Verify DAGExecutor wires dependencies and delegates DLQ static helper methods."""
    repo = InMemoryUnifiedWorkflowRepository()
    executor = _build_dag_executor(repo)

    assert executor.exec_repo is repo
    assert executor.deps.exec_repo is repo
    assert isinstance(executor.committer, ExecutionCommitter)
    assert isinstance(executor.node_executor, NodeExecutor)

    fallback_excs = DAGExecutor._dlq_fallback_step_exceptions()
    assert AppException in fallback_excs
    DAGExecutor._dlq_record_step_failure("stp_1111222233334444", "STEP_FAILED", RuntimeError("boom"))
    DAGExecutor._dlq_handle_progress_commit_error("stp_1111222233334444", RuntimeError("commit err"))


@pytest.mark.asyncio
async def test_dag_executor_execute_workflow_end_to_end_and_missing_blueprint_failure() -> None:
    """Verify DAGExecutor.execute_workflow executes a single-step workflow and fails fast on missing blueprint."""
    repo = InMemoryUnifiedWorkflowRepository()
    executor = _build_dag_executor(repo)

    step_id = "stp_1111222233334444"
    step_def = Step(
        id=step_id,
        slug="step_facade_test",
        name=I18nText(translations={"en": "Facade Step", "fi": "Julkisivuvaihe"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LOGIC,
        hook="custom_logic_hook",
        engine_type=EngineType.PROMPT,
        criteria_block_ids=[],
    )
    repo.set_step(step_def)

    workflow = Workflow(
        id="wf_1111222233334444",
        slug="wf_facade_test",
        name=I18nText(translations={"en": "Facade WF", "fi": "Julkisivu WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        status="active",
        version=1,
        historical_context_mode=HistoricalContextMode.DISABLED,
        default_profile_id="prf_1111222233334444",
        model_registry_id="sys_1111222233334444",
        steps=[StepRule(id=step_id, task_blueprint=step_id, depends_on=[])],
    )
    repo.set_workflow(workflow)

    exec_id = "exe_1111222233334444"
    repo.set_execution(
        ExecutionRecord(
            id=exec_id,
            workflow_id=workflow.id,
            output_profile_id="prf_1111222233334444",
            target_locale="en",
            raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "Facade test document"}),
            metadata=ExecutionMetadata(workflow_version=1, model_registry_id="sys_1111222233334444"),
        )
    )

    class _StubNodeExecutor(NodeExecutor):
        async def execute(self, step: StepRule, *_args: object, **_kwargs: object) -> list[TraceEvent]:
            return [TraceEvent(step_name=step.id, event_type="output", content={"ok": True})]

    executor.node_executor = _StubNodeExecutor(deps=executor.deps)
    hook_res = HookResult(
        success=True,
        state_delta=HookDeltaDTO(
            delta=ExecutionInputsDTO(
                raw_inputs={"doc": "Facade test document"},
                dynamic_inputs={"doc": "Facade test document"},
            )
        ),
    )

    with patch(
        "backend_v2.services.orchestrator.dag_executor.hook_registry.execute",
        return_value=hook_res,
    ):
        result = await executor.execute_workflow(
            execution_id=exec_id,
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "Facade test document"}),
        )

    assert executor.committer.execution_id == exec_id
    assert result.status == ExecutionStatus.RUNNING
    assert result.step_states[step_id].status == ExecutionStatus.PASSED

    # Negative case: missing step blueprint raises ExceptionGroup containing AppException(CONFIGURATION_ERROR)
    empty_executor = _build_dag_executor(InMemoryUnifiedWorkflowRepository())
    missing_wf = workflow.model_copy(
        update={
            "id": "wf_5555666677778888",
            "steps": [StepRule(id="stp_9999888877776666", task_blueprint="stp_9999888877776666", depends_on=[])],
        }
    )
    with pytest.raises(ExceptionGroup) as exc_info:
        await empty_executor.execute_workflow(
            execution_id="exe_5555666677778888",
            workflow=missing_wf,
            raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "Facade test document"}),
        )
    sub_exc = exc_info.value.exceptions[0]
    assert isinstance(sub_exc, AppException)
    assert sub_exc.details is not None
    assert sub_exc.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


@pytest.mark.asyncio
async def test_dag_executor_execute_workflow_fails_fast_on_prehydration_and_wave_error() -> None:
    """Verify DAGExecutor.execute_workflow raises AppException on pre-hydration and wave execution failures."""
    repo = InMemoryUnifiedWorkflowRepository()
    executor = _build_dag_executor(repo)

    step_id = "stp_2222333344445555"
    repo.set_step(
        Step(
            id=step_id,
            slug="step_neg_facade",
            name=I18nText(translations={"en": "Neg Step", "fi": "Neg Vaihe"}),
            description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
            type=StepType.LOGIC,
            hook="custom_logic_hook",
            engine_type=EngineType.PROMPT,
            criteria_block_ids=[],
        )
    )
    workflow = Workflow(
        id="wf_2222333344445555",
        slug="wf_neg_facade",
        name=I18nText(translations={"en": "Neg WF", "fi": "Neg WF"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        status="active",
        version=1,
        historical_context_mode=HistoricalContextMode.DISABLED,
        default_profile_id="prf_1111222233334444",
        model_registry_id="sys_1111222233334444",
        steps=[StepRule(id=step_id, task_blueprint=step_id, depends_on=[])],
    )
    repo.set_workflow(workflow)

    # Negative partition 1: pre-hydration input_processing hook failure raises AppException(VALIDATION_FAILED)
    with (
        patch(
            "backend_v2.services.orchestrator.dag_executor.hook_registry.execute",
            side_effect=RuntimeError("corrupted input payload"),
        ),
        pytest.raises(AppException) as val_exc,
    ):
        await executor.execute_workflow(
            execution_id="exe_2222333344445555",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "Bad input"}),
        )
    assert val_exc.value.details is not None
    assert val_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED

    # Negative partition 2: step execution raising fatal AppException propagates AppException(WORKFLOW_EXECUTION_FAILED)
    class _FailingNodeExecutor(NodeExecutor):
        async def execute(self, step: StepRule, *_args: object, **_kwargs: object) -> list[TraceEvent]:
            raise AppException(
                message=f"Fatal step failure on {step.id}",
                status_code=500,
                details={"error_code": ErrorCodes.WORKFLOW_EXECUTION_FAILED},
            )

    executor.node_executor = _FailingNodeExecutor(deps=executor.deps)
    hook_ok = HookResult(
        success=True,
        state_delta=HookDeltaDTO(
            delta=ExecutionInputsDTO(
                raw_inputs={"doc": "Valid input"},
                dynamic_inputs={"doc": "Valid input"},
            )
        ),
    )
    with (
        patch(
            "backend_v2.services.orchestrator.dag_executor.hook_registry.execute",
            return_value=hook_ok,
        ),
        pytest.raises(AppException) as wf_exc,
    ):
        await executor.execute_workflow(
            execution_id="exe_3333444455556666",
            workflow=workflow,
            raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "Valid input"}),
        )
    assert wf_exc.value.details is not None
    assert wf_exc.value.details["error_code"] == ErrorCodes.WORKFLOW_EXECUTION_FAILED
