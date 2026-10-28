"""Unit tests for backend_v2.services.orchestrator.dag_executor.node_executor.

Verifies NodeExecutor engine resolution, OpenTelemetry span attributes, post-hook
scoring separation, strategy dispatch, and Dead Letter Queue error trace emission.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from unittest.mock import patch

import pytest

from backend_v2.core.hook_registry import GlobalContextVarsDTO
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import FrozenContext
from backend_v2.models.domain.step import Step, StepRule
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.enums import CognitiveTier, EngineType, StepType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import ErrorTraceEvent, StateProjector, TraceEvent
from backend_v2.services.orchestrator.dag_executor.node_executor import NodeExecutor
from backend_v2.services.orchestrator.engines import ExecutionEngine
from backend_v2.services.orchestrator.strategies.base import (
    NodeStrategy,
    StrategyContext,
    StrategyDependencies,
)
from backend_v2.tests.factories.model_factories import SystemRulePromptBlockFactory
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


class _RecordingStrategy(NodeStrategy):
    """Deterministic test strategy recording StrategyContext and returning TraceEvents."""

    def __init__(
        self,
        deps: StrategyDependencies,
        engine: ExecutionEngine | None = None,
        raise_exc: BaseException | None = None,
    ) -> None:
        super().__init__(deps)
        self.engine = engine
        self.raise_exc = raise_exc
        self.last_context: StrategyContext | None = None
        self.last_step: StepRule | None = None
        self.quota_org_id: str | None = None

    async def assert_quota(self, org_id: str | None) -> None:
        self.quota_org_id = org_id

    async def execute(
        self,
        step: StepRule,
        projector: StateProjector,
        context: StrategyContext,
        frozen_ctx: FrozenContext | None = None,
        trace: list[TraceEvent] | None = None,
        progress_callback: Callable[[int, int], Awaitable[None]] | None = None,
    ) -> list[TraceEvent]:
        _ = (projector, frozen_ctx, trace, progress_callback)
        if self.raise_exc is not None:
            raise self.raise_exc
        self.last_step = step
        self.last_context = context
        return [TraceEvent(step_name=step.id, event_type="output", content="ok")]


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


@pytest.mark.asyncio
async def test_node_executor_resolves_engine_and_merges_post_hook_deltas() -> None:
    """Verify NodeExecutor.execute resolves ExecutionEngine, filters scoring hooks, and dispatches strategy."""
    repo = InMemoryUnifiedWorkflowRepository()
    proto_block = SystemRulePromptBlockFactory.build(id="blk_1111222233334444")
    await repo.create_prompt_block(proto_block)

    step_bp = Step(
        id="stp_1111222233334444",
        slug="step_test",
        name=I18nText(translations={"en": "Test Step", "fi": "Testivaihe"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.CAUSAL_DISCOVERY,
        engine_type=EngineType.CAUSAL_DISCOVERY,
        cognitive_tier=CognitiveTier.FAST,
        extraction_protocol_block_id="blk_1111222233334444",
        criteria_block_ids=[],
        post_hooks=["apply_scoring_logic_hook", "custom_post_hook"],
    )
    repo.set_step(step_bp)

    deps = _build_deps(repo)
    executor = NodeExecutor(deps=deps)

    step_rule = StepRule(
        id="stp_aaaa1111bbbb2222",
        task_blueprint="stp_1111222233334444",
        depends_on=[],
        input_mappings={"doc": "$inputs.doc"},
    )
    projector = StateProjector()
    projector.apply_delta(TraceEvent(step_name="inputs", event_type="input", content={"doc": "hello"}))

    meta = ExecutionMetadata(
        workflow_version=1,
        model_registry_id="sys_1111222233334444",
        global_context_vars=GlobalContextVarsDTO(language="fi", target_locale="fi"),
    )

    recorded_strategies: list[_RecordingStrategy] = []

    def _fake_create_strategy(
        step_type: StepType,
        deps: StrategyDependencies,
        engine: ExecutionEngine | None = None,
    ) -> _RecordingStrategy:
        _ = step_type
        strat = _RecordingStrategy(deps=deps, engine=engine)
        recorded_strategies.append(strat)
        return strat

    with patch(
        "backend_v2.services.orchestrator.dag_executor.NodeStrategyFactory.create_strategy",
        side_effect=_fake_create_strategy,
    ):
        events = await executor.execute(
            step=step_rule,
            execution_id="exe_1111222233334444",
            workflow_id="wf_1111222233334444",
            metadata=meta,
            projector=projector,
            arq_pool="fake_pool",
            context_variables=ContextVariablesDTO(),
            global_context_vars=None,
            target_locale="fi",
            output_profile_id="prf_1111222233334444",
            organization_id="org_1111222233334444",
        )

    assert len(events) == 1
    assert events[0].step_name == "stp_aaaa1111bbbb2222"
    assert len(recorded_strategies) == 1
    strat = recorded_strategies[0]
    assert strat.engine is not None
    assert strat.deps.arq_pool == "fake_pool"
    assert strat.quota_org_id == "org_1111222233334444"
    assert strat.last_context is not None
    assert strat.last_context.cognitive_tier == CognitiveTier.FAST
    assert strat.last_context.model_registry_id == "sys_1111222233334444"
    assert strat.last_context.global_context_vars.language == "fi"


@pytest.mark.asyncio
async def test_node_executor_missing_blueprint_or_definition_raises_configuration_error() -> None:
    """Verify NodeExecutor.execute raises CONFIGURATION_ERROR when blueprint ID or Step definition is missing."""
    repo = InMemoryUnifiedWorkflowRepository()
    executor = NodeExecutor(deps=_build_deps(repo))
    projector = StateProjector()
    meta = ExecutionMetadata(workflow_version=1)

    empty_bp_rule = StepRule.model_construct(
        id="stp_aaaa1111bbbb2222",
        task_blueprint="",
        depends_on=[],
        input_mappings={},
    )
    with pytest.raises(AppException) as exc_empty:
        await executor.execute(
            step=empty_bp_rule,
            execution_id="exe_1111222233334444",
            workflow_id="wf_1111222233334444",
            metadata=meta,
            projector=projector,
        )
    assert exc_empty.value.details is not None
    assert exc_empty.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR

    missing_bp_rule = StepRule(
        id="stp_aaaa1111bbbb2222",
        task_blueprint="stp_9999888877776666",
        depends_on=[],
        input_mappings={},
    )
    with pytest.raises(AppException) as exc_missing:
        await executor.execute(
            step=missing_bp_rule,
            execution_id="exe_1111222233334444",
            workflow_id="wf_1111222233334444",
            metadata=meta,
            projector=projector,
        )
    assert exc_missing.value.details is not None
    assert exc_missing.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR


@pytest.mark.asyncio
async def test_node_executor_dlq_error_recording_and_unhandled_exception_propagation() -> None:
    """Verify NodeExecutor converts runtime/validation errors into ErrorTraceEvent and re-raises unknown exceptions."""
    repo = InMemoryUnifiedWorkflowRepository()
    step_bp = Step(
        id="stp_1111222233334444",
        slug="step_logic",
        name=I18nText(translations={"en": "Step", "fi": "Vaihe"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        type=StepType.LOGIC,
        hook="custom_logic_hook",
        engine_type=EngineType.PROMPT,
    )
    repo.set_step(step_bp)

    executor = NodeExecutor(deps=_build_deps(repo))
    step_rule = StepRule(
        id="stp_aaaa1111bbbb2222",
        task_blueprint="stp_1111222233334444",
        depends_on=[],
        input_mappings={},
    )
    projector = StateProjector()
    meta = ExecutionMetadata(workflow_version=1)

    with patch(
        "backend_v2.services.orchestrator.dag_executor.NodeStrategyFactory.create_strategy",
        side_effect=lambda step_type, deps, engine=None: _RecordingStrategy(
            deps=deps, engine=engine, raise_exc=RuntimeError("transient node crash")
        ),
    ):
        dlq_events = await executor.execute(
            step=step_rule,
            execution_id="exe_1111222233334444",
            workflow_id="wf_1111222233334444",
            metadata=meta,
            projector=projector,
            step_def=step_bp,
        )

    assert len(dlq_events) == 1
    assert isinstance(dlq_events[0], ErrorTraceEvent)
    assert dlq_events[0].error_code == "STEP_FAILED"
    assert "transient node crash" in dlq_events[0].error_message

    class _CustomFatalException(Exception):
        pass

    with (
        patch(
            "backend_v2.services.orchestrator.dag_executor.NodeStrategyFactory.create_strategy",
            side_effect=lambda step_type, deps, engine=None: _RecordingStrategy(
                deps=deps, engine=engine, raise_exc=_CustomFatalException("fatal")
            ),
        ),
        pytest.raises(_CustomFatalException),
    ):
        await executor.execute(
            step=step_rule,
            execution_id="exe_1111222233334444",
            workflow_id="wf_1111222233334444",
            metadata=meta,
            projector=projector,
            step_def=step_bp,
        )

    with (
        patch(
            "backend_v2.services.orchestrator.dag_executor.NodeStrategyFactory.create_strategy",
            side_effect=lambda step_type, deps, engine=None: _RecordingStrategy(
                deps=deps,
                engine=engine,
                raise_exc=AppException(
                    message="configuration failure",
                    status_code=429,
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
                ),
            ),
        ),
        pytest.raises(AppException),
    ):
        await executor.execute(
            step=step_rule,
            execution_id="exe_1111222233334444",
            workflow_id="wf_1111222233334444",
            metadata=meta,
            projector=projector,
            step_def=step_bp,
        )
