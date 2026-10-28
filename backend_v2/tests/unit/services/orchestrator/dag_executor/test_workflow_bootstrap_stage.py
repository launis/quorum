"""Unit tests for backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage.

Verifies concurrent blueprint pre-fetching via asyncio.TaskGroup, WorkflowExecutionState
initialization and resumption, safe_commit_execution_state, execute_rag_preflight_stage,
and Dead Letter Queue helper functions.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from backend_v2.core.hook_registry import (
    ExecutionInputsDTO,
    GlobalContextVarsDTO,
    HookDeltaDTO,
    HookResult,
)
from backend_v2.exceptions import AppException, ErrorCodes, WorkflowExecutionError
from backend_v2.models.auth import User, UserRole
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.blackboard import GlobalAtomBlackboard
from backend_v2.models.domain.execution import (
    ExecutionRecord,
    ExecutionStep,
    FrozenContext,
)
from backend_v2.models.domain.inputs import WorkflowInputs
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.enums import EngineType, ExecutionStatus, HistoricalContextMode, StepType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.orchestrator.dag_executor.execution_committer import ExecutionCommitter
from backend_v2.services.orchestrator.dag_executor.workflow_bootstrap_stage import (
    _extract_input_delta_dict,
    bootstrap_workflow_execution_state,
    dlq_fallback_step_exceptions,
    dlq_handle_progress_commit_error,
    dlq_record_step_failure,
    execute_rag_preflight_stage,
    safe_commit_execution_state,
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


def _build_workflow(blueprint_id: str = "stp_1111222233334444") -> Workflow:
    return Workflow(
        id="wf_1111222233334444",
        slug="workflow_test",
        name=I18nText(translations={"en": "Test Workflow", "fi": "Testityonkulku"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        status="active",
        version=1,
        historical_context_mode=HistoricalContextMode.DISABLED,
        default_profile_id="prf_1111222233334444",
        model_registry_id="sys_1111222233334444",
        steps=[
            StepRule(
                id="stp_aaaa1111bbbb2222",
                task_blueprint=blueprint_id,
                depends_on=[],
                input_mappings={},
            )
        ],
    )


@pytest.mark.asyncio
async def test_bootstrap_workflow_execution_state_prefetches_blueprints_via_taskgroup() -> None:
    """Verify bootstrap_workflow_execution_state pre-fetches blueprints via TaskGroup and initializes state."""
    repo = InMemoryUnifiedWorkflowRepository()
    step_bp = Step(
        id="stp_1111222233334444",
        slug="step_en",
        name=I18nText(translations={"en": "Step EN", "fi": "Vaihe FI"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LOGIC,
        hook="custom_logic_hook",
        engine_type=EngineType.PROMPT,
        criteria_block_ids=[],
        post_hooks=["apply_scoring_logic_hook", "keep_hook"],
    )
    repo.set_step(step_bp)

    user = User(
        id="usr_1111222233334444",
        email="coach@example.com",
        name="Coach",
        role=UserRole.ADMIN,
        organization_id="org_1111222233334444",
        is_active=True,
        language="fi",
        theme_mode="system",
        created_at=datetime.now(UTC),
    )
    await repo.create_user(user)

    wf = _build_workflow()
    inputs = WorkflowInputs(
        user_id="usr_1111222233334444",
        language="fi",
        dynamic_inputs={"doc": "raw text"},
    )
    hook_res = HookResult(
        success=True,
        state_delta=HookDeltaDTO(
            delta=ExecutionInputsDTO(raw_inputs={"doc": "processed"}, dynamic_inputs={"doc": "processed"})
        ),
    )

    with patch(
        "backend_v2.services.orchestrator.dag_executor.hook_registry.execute",
        return_value=hook_res,
    ):
        state = await bootstrap_workflow_execution_state(
            execution_id="exe_1111222233334444",
            workflow=wf,
            raw_inputs=inputs,
            deps=_build_deps(repo),
        )

    assert state.exec_id == "exe_1111222233334444"
    assert "stp_1111222233334444" in state.step_definitions
    assert state.step_definitions["stp_1111222233334444"].post_hooks == ["keep_hook"]
    assert state.exec_record.status == ExecutionStatus.RUNNING
    assert state.global_context_vars.language == "fi"
    assert len(state.exec_record.execution_trace) == 2

    # Verify _extract_input_delta_dict variants
    assert _extract_input_delta_dict(HookDeltaDTO(delta=None)) == {}
    assert _extract_input_delta_dict(GlobalContextVarsDTO(language="en"))["language"] == "en"
    assert _extract_input_delta_dict("scalar") == {"value": "scalar"}
    assert _extract_input_delta_dict({"k": "v"}) == {"k": "v"}


@pytest.mark.asyncio
async def test_bootstrap_workflow_execution_state_missing_blueprint_raises_not_found() -> None:
    """Verify bootstrap_workflow_execution_state raises CONFIGURATION_ERROR on missing blueprint."""
    repo = InMemoryUnifiedWorkflowRepository()
    wf = _build_workflow(blueprint_id="stp_9999888877776666")
    inputs = WorkflowInputs(dynamic_inputs={"doc": "text"})

    with pytest.raises(ExceptionGroup) as exc_info:
        await bootstrap_workflow_execution_state(
            execution_id="exe_1111222233334444",
            workflow=wf,
            raw_inputs=inputs,
            deps=_build_deps(repo),
        )
    sub_exc = exc_info.value.exceptions[0]
    assert isinstance(sub_exc, AppException)
    assert sub_exc.details is not None
    assert sub_exc.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR

    # Verify pre-hydration hook exception translates to VALIDATION_FAILED
    repo.set_step(
        Step(
            id="stp_9999888877776666",
            slug="step_missing_hook",
            name=I18nText(translations={"en": "Step", "fi": "Vaihe"}),
            description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
            type=StepType.LOGIC,
            hook="custom_logic_hook",
            engine_type=EngineType.PROMPT,
        )
    )
    with (
        patch(
            "backend_v2.services.orchestrator.dag_executor.hook_registry.execute",
            side_effect=RuntimeError("hook crash"),
        ),
        pytest.raises(AppException) as val_exc,
    ):
        await bootstrap_workflow_execution_state(
            execution_id="exe_1111222233334444",
            workflow=wf,
            raw_inputs=inputs,
            deps=_build_deps(repo),
        )
    assert val_exc.value.details is not None
    assert val_exc.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED


@pytest.mark.asyncio
async def test_bootstrap_workflow_execution_state_resumes_existing_record_and_resets_failed_steps() -> None:
    """Verify bootstrap_workflow_execution_state resumes existing ExecutionRecord and resets FAILED steps."""
    repo = InMemoryUnifiedWorkflowRepository()
    step_bp = Step(
        id="stp_1111222233334444",
        slug="step_resolved",
        name=I18nText(translations={"en": "Resolved Label", "fi": "Valmis Otsikko"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LOGIC,
        hook="custom_logic_hook",
        engine_type=EngineType.PROMPT,
    )
    repo.set_step(step_bp)

    failed_step = ExecutionStep(
        id="stp_aaaa1111bbbb2222",
        label="stp_aaaa1111bbbb2222",
        status=ExecutionStatus.FAILED,
    )
    existing_rec = ExecutionRecord(
        id="exe_1111222233334444",
        workflow_id="wf_1111222233334444",
        target_locale="en",
        raw_inputs=WorkflowInputs(dynamic_inputs={"doc": "text"}),
        frozen_context=FrozenContext(),
        source_identity_manifest={},
        status=ExecutionStatus.FAILED,
        steps=[failed_step],
        step_states={"stp_aaaa1111bbbb2222": failed_step},
        metadata=ExecutionMetadata(
            workflow_version=1,
            model_registry_id=None,
            global_context_vars=GlobalContextVarsDTO(language="en", target_locale="en"),
        ),
    )
    repo.set_execution(existing_rec)

    with patch(
        "backend_v2.services.orchestrator.dag_executor.hook_registry.execute",
        return_value=HookResult(success=True, state_delta=None),
    ):
        state = await bootstrap_workflow_execution_state(
            execution_id="exe_1111222233334444",
            workflow=_build_workflow(),
            raw_inputs=existing_rec.raw_inputs,
            deps=_build_deps(repo),
            strictness_level=75,
            lexical_strictness_level=80,
        )

    assert state.strictness_level == 75
    assert state.lexical_strictness_level == 80
    assert state.exec_record.step_states["stp_aaaa1111bbbb2222"].status == ExecutionStatus.PENDING
    assert state.exec_record.steps[0].label == "Resolved Label"
    assert state.exec_record.metadata is not None
    assert state.exec_record.metadata.model_registry_id == "sys_1111222233334444"


@pytest.mark.asyncio
async def test_safe_commit_execution_state_and_execute_rag_preflight_stage() -> None:
    """Verify safe_commit_execution_state and execute_rag_preflight_stage persist progress and blackboard."""
    repo = InMemoryUnifiedWorkflowRepository()
    step_bp = Step(
        id="stp_1111222233334444",
        slug="step_preflight",
        name=I18nText(translations={"en": "Preflight Target", "fi": "Esivaihe"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LOGIC,
        hook="custom_logic_hook",
        engine_type=EngineType.PROMPT,
        pre_hooks=["atom_flattening_hook"],
    )
    repo.set_step(step_bp)

    wf = _build_workflow()
    inputs = WorkflowInputs(dynamic_inputs={"doc": "content"})

    with patch(
        "backend_v2.services.orchestrator.dag_executor.hook_registry.execute",
        return_value=HookResult(success=True, state_delta=None),
    ):
        state = await bootstrap_workflow_execution_state(
            execution_id="exe_1111222233334444",
            workflow=wf,
            raw_inputs=inputs,
            deps=_build_deps(repo),
        )
    repo.set_execution(state.exec_record)
    committer = ExecutionCommitter(exec_repo=repo, execution_id=state.execution_id)

    class _FakeRAGPreflight(RAGPreflightService):
        def __init__(self) -> None:
            pass

        async def execute(
            self,
            target_step: StepRule,
            step_def: Step,
            exec_record: ExecutionRecord,
            emit_progress: Callable[[str, int], Awaitable[None]],
        ) -> GlobalAtomBlackboard:
            _ = (target_step, step_def, exec_record)
            await emit_progress("Atomizing", 50)
            repo.inject_fault("update_execution", OSError("transient commit glitch"))
            try:
                await emit_progress("Retrying progress", 75)
            finally:
                repo.clear_faults()
            return GlobalAtomBlackboard(atoms_by_input={})

    commit_errors: list[tuple[str, Exception]] = []
    await execute_rag_preflight_stage(
        state=state,
        rag_preflight=_FakeRAGPreflight(),
        committer=committer,
        dlq_on_progress_commit_error=lambda sid, err: commit_errors.append((sid, err)),
    )

    assert len(commit_errors) == 1
    assert state.exec_record.context_variables.global_atom_blackboard == GlobalAtomBlackboard(atoms_by_input={})
    sys_steps = [k for k in state.exec_record.step_states if k.startswith("sys_rag_")]
    assert len(sys_steps) == 1
    assert state.exec_record.step_states[sys_steps[0]].status == ExecutionStatus.PASSED

    # Verify failing preflight transitions virtual step to FAILED and raises WorkflowExecutionError
    class _FailingRAGPreflight(RAGPreflightService):
        def __init__(self) -> None:
            pass

        async def execute(
            self,
            target_step: StepRule,
            step_def: Step,
            exec_record: ExecutionRecord,
            emit_progress: Callable[[str, int], Awaitable[None]],
        ) -> GlobalAtomBlackboard:
            _ = (target_step, step_def, exec_record, emit_progress)
            raise RuntimeError("preflight explosion")

    with pytest.raises(WorkflowExecutionError):
        await execute_rag_preflight_stage(
            state=state,
            rag_preflight=_FailingRAGPreflight(),
            committer=committer,
        )

    dlq_record_step_failure("stp_aaaa1111bbbb2222", "TEST_ERR", RuntimeError("err"))
    dlq_handle_progress_commit_error("stp_aaaa1111bbbb2222", OSError("io"))
    assert AppException in dlq_fallback_step_exceptions()
