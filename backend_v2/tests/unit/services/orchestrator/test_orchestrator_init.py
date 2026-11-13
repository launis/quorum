"""Unit tests for backend_v2.services.orchestrator.__init__."""

from __future__ import annotations

from unittest.mock import patch

import pytest

import backend_v2.services.orchestrator as orchestrator_pkg
from backend_v2.core.hook_registry import ExecutionInputsDTO, HookDeltaDTO, HookResult
from backend_v2.exceptions import AppException, ErrorCodes, WorkflowCompilationError
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.step import ExpectedInput, Step, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import EngineType, EntityPrefix, ExecutionStatus, HistoricalContextMode, StepType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import TraceEvent
from backend_v2.services.orchestrator import (
    CausalCohesionEvaluationDTO,
    CausalCohesionEvaluator,
    ContextRouter,
    DAGCompilerService,
    MatrixReducer,
    PromptCompiler,
    PromptCompilerAdapter,
    RoutingModeConfig,
)
from backend_v2.services.orchestrator.dag_executor import DAGExecutor, NodeExecutor
from backend_v2.services.orchestrator.engines import (
    ENGINE_REGISTRY,
    ExecutionEngine,
    build_execution_engine,
)
from backend_v2.services.orchestrator.rag_preflight_service import RAGPreflightService
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


def _build_workflow(
    steps: list[StepRule],
    expected_inputs: list[ExpectedInput] | None = None,
) -> Workflow:
    """Create a canonical Workflow domain instance for orchestrator facade testing."""
    return Workflow(
        organization_id="org_0195f3a0000070008000000000000001",
        id=generate_opaque_id(EntityPrefix.WORKFLOW),
        slug="wf_orchestrator_init_test",
        name=I18nText(translations={"en": "Orchestrator Init WF", "fi": "Orkestroija WF"}),
        description=I18nText(translations={"en": "Description", "fi": "Kuvaus"}),
        status="active",
        version=1,
        historical_context_mode=HistoricalContextMode.DISABLED,
        default_profile_id=generate_opaque_id(EntityPrefix.OUTPUT_PROFILE),
        model_registry_id=generate_opaque_id(EntityPrefix.MODEL_REGISTRY),
        expected_inputs=expected_inputs if expected_inputs is not None else [],
        steps=steps,
    )


def _build_dag_executor(repo: InMemoryUnifiedWorkflowRepository) -> DAGExecutor:
    """Create a DAGExecutor instance backed by InMemoryUnifiedWorkflowRepository."""
    compiler = PromptCompiler()
    rag_preflight = RAGPreflightService(
        workflow_repo=repo,
        system_repo=repo,
        prompt_compiler=compiler,
    )
    return DAGExecutor(
        exec_repo=repo,
        workflow_repo=repo,
        prompt_block_repo=repo,
        output_profile_repo=repo,
        identity_repo=repo,
        audit_repo=repo,
        system_repo=repo,
        prompt_compiler=compiler,
        rag_preflight=rag_preflight,
    )


@pytest.mark.asyncio
async def test_orchestrator_init_public_interface_and_resolution() -> None:
    """Verify orchestrator.__init__ exports and functional execution of re-exported services."""
    expected = [
        "CausalCohesionEvaluationDTO",
        "CausalCohesionEvaluator",
        "ContextRouter",
        "DAGCompilerService",
        "MatrixReducer",
        "PromptCompiler",
        "PromptCompilerAdapter",
        "RoutingModeConfig",
    ]
    assert sorted(orchestrator_pkg.__all__) == expected

    compiler = PromptCompiler()
    adapter = PromptCompilerAdapter()
    assert adapter.resolve_i18n(I18nText(translations={"en": "Hello", "fi": "Hei"}), "fi") == "Hei"
    engine = build_execution_engine(EngineType.TDA, compiler)
    assert isinstance(engine, ExecutionEngine)
    assert EngineType.TDA in ENGINE_REGISTRY
    assert CausalCohesionEvaluator is orchestrator_pkg.CausalCohesionEvaluator
    assert CausalCohesionEvaluationDTO is orchestrator_pkg.CausalCohesionEvaluationDTO
    assert ContextRouter is orchestrator_pkg.ContextRouter
    assert DAGCompilerService is orchestrator_pkg.DAGCompilerService
    assert MatrixReducer is orchestrator_pkg.MatrixReducer
    assert PromptCompiler is orchestrator_pkg.PromptCompiler
    assert PromptCompilerAdapter is orchestrator_pkg.PromptCompilerAdapter
    assert RoutingModeConfig is orchestrator_pkg.RoutingModeConfig

    step_1_id = generate_opaque_id(EntityPrefix.STEP)
    step_2_id = generate_opaque_id(EntityPrefix.STEP)
    wf = _build_workflow(
        steps=[
            StepRule(id=step_1_id, task_blueprint=step_1_id, depends_on=[]),
            StepRule(id=step_2_id, task_blueprint=step_2_id, depends_on=[step_1_id]),
        ]
    )
    DAGCompilerService.validate_workflow(wf)
    waves = DAGCompilerService.compute_topological_waves(wf.steps)
    assert len(waves) == 2
    assert waves[0][0].id == step_1_id
    assert waves[1][0].id == step_2_id

    repo = InMemoryUnifiedWorkflowRepository()
    executor = _build_dag_executor(repo)
    assert DAGExecutor._dlq_fallback_step_exceptions()

    repo.set_step(
        Step(
            organization_id="org_0195f3a0000070008000000000000001",
            id=step_1_id,
            slug="step_1_test",
            name=I18nText(translations={"en": "Step 1", "fi": "Vaihe 1"}),
            description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
            type=StepType.LOGIC,
            hook="custom_logic_hook",
            engine_type=EngineType.PROMPT,
            criteria_block_ids=[],
        )
    )
    single_wf = _build_workflow(steps=[StepRule(id=step_1_id, task_blueprint=step_1_id, depends_on=[])])
    repo.set_workflow(single_wf)
    exec_id = generate_opaque_id(EntityPrefix.EXECUTION)
    repo.set_execution(
        ExecutionRecord(
            id=exec_id,
            workflow_id=single_wf.id,
            output_profile_id=single_wf.default_profile_id,
            target_locale="en",
            raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "Test document"}),
            metadata=ExecutionMetadata(workflow_version=1, model_registry_id=single_wf.model_registry_id),
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
                raw_inputs={"doc": "Test document"},
                dynamic_inputs={"doc": "Test document"},
            )
        ),
    )
    with patch(
        "backend_v2.services.orchestrator.dag_executor.hook_registry.execute",
        return_value=hook_res,
    ):
        record = await executor.execute_workflow(
            execution_id=exec_id,
            workflow=single_wf,
            raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "Test document"}),
        )
    assert next(s for s in record.steps if s.id == step_1_id).status == ExecutionStatus.PASSED


def test_negative_orchestrator_init_cyclic_dag_raises_app_exception() -> None:
    """Negative test (ISTQB): cyclic dependency in workflow steps raises WorkflowCompilationError."""
    step_a = generate_opaque_id(EntityPrefix.STEP)
    step_b = generate_opaque_id(EntityPrefix.STEP)
    steps = [
        StepRule(id=step_a, task_blueprint=step_a, depends_on=[step_b]),
        StepRule(id=step_b, task_blueprint=step_b, depends_on=[step_a]),
    ]
    with pytest.raises(WorkflowCompilationError) as exc_info:
        DAGCompilerService._ensure_acyclic(steps)

    assert isinstance(exc_info.value, AppException)
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.WORKFLOW_COMPILATION_ERROR


def test_negative_orchestrator_init_strictness_and_routing_validation_fail_fast() -> None:
    """Negative test (ISTQB): invalid strictness level or missing routing mode raises AppException."""
    compiler = PromptCompiler()
    with pytest.raises(AppException) as exc_info:
        compiler.calibrate_strictness(float("nan"))

    assert exc_info.value.status_code == 400
    assert exc_info.value.details is not None
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value

    with pytest.raises(AppException) as route_exc:
        ContextRouter.validate_routing_mode("$steps.step_1", {"invalid_key": "bad"})

    assert route_exc.value.details is not None
    assert route_exc.value.details["error_code"] == ErrorCodes.MISSING_ROUTING_MODE
