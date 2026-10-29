"""Unit tests for the orchestrator strategies package facade (__init__.py).

Verifies public facade re-exports, factory dispatch for LogicNodeStrategy and
LLMNodeStrategy, StrategyContext strict Pydantic V2 invariants, LLMNodeStrategy
pipeline execution, and ISTQB negative boundary/invalid input error cases.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, ConfigDict, ValidationError

import backend_v2.services.orchestrator.strategies as strategies_pkg
from backend_v2.core.hook_registry import HookResult, HookState
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.step import StepRule
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.context_variables import ContextVariablesDTO
from backend_v2.models.dtos.engine import EngineExecutionResult
from backend_v2.models.dtos.global_context import GlobalContextVarsDTO
from backend_v2.models.dtos.hook_state import ExecutionInputsDTO
from backend_v2.models.enums import StepType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.state import StateProjector, StepOutputDTO
from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler
from backend_v2.services.orchestrator.strategies import (
    NODE_STRATEGY_REGISTRY,
    LLMNodeStrategy,
    LogicNodeStrategy,
    NodeStrategy,
    NodeStrategyFactory,
    StrategyBuilder,
    StrategyContext,
    StrategyDependencies,
)
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


class _DummyDynamicSchemaDTO(BaseModel):
    """Strict dummy schema returned by mock PromptCompiler during unit tests."""

    model_config = ConfigDict(extra="forbid", strict=True)
    result_text: str = ""


@pytest.fixture
def in_memory_repo() -> InMemoryUnifiedWorkflowRepository:
    """Provide a stateful in-memory unified workflow repository."""
    return InMemoryUnifiedWorkflowRepository()


@pytest.fixture
def mock_prompt_compiler() -> MagicMock:
    """Provide a strictly specced PromptCompiler mock."""
    compiler = MagicMock(spec=PromptCompiler)
    compiler.compile_static_instructions.return_value = "Compiled static instructions"
    compiler.build_dynamic_schema.return_value = _DummyDynamicSchemaDTO
    return compiler


@pytest.fixture
def strategy_deps(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    mock_prompt_compiler: MagicMock,
) -> StrategyDependencies:
    """Provide a frozen StrategyDependencies container backed by InMemoryUnifiedWorkflowRepository."""
    return StrategyDependencies(
        exec_repo=in_memory_repo,
        workflow_repo=in_memory_repo,
        comp_repo=in_memory_repo,
        prompt_block_repo=in_memory_repo,
        output_profile_repo=in_memory_repo,
        identity_repo=in_memory_repo,
        audit_repo=in_memory_repo,
        system_repo=in_memory_repo,
        prompt_compiler=mock_prompt_compiler,
    )


def test_strategies_facade_exports_and_registry_contract(
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify strategies package facade exports and StrategyBuilder registry contract."""
    expected_exports = [
        "LLMNodeStrategy",
        "LogicNodeStrategy",
        "NODE_STRATEGY_REGISTRY",
        "NodeStrategy",
        "NodeStrategyFactory",
        "StrategyBuilder",
        "StrategyContext",
        "StrategyDependencies",
    ]
    assert sorted(strategies_pkg.__all__) == expected_exports
    assert issubclass(LogicNodeStrategy, NodeStrategy)
    assert issubclass(LLMNodeStrategy, NodeStrategy)
    assert StepType.LOGIC in NODE_STRATEGY_REGISTRY
    assert StepType.LLM in NODE_STRATEGY_REGISTRY

    logic_builder: StrategyBuilder = NODE_STRATEGY_REGISTRY[StepType.LOGIC]
    strategy = logic_builder(strategy_deps, None)
    assert isinstance(strategy, LogicNodeStrategy)
    assert strategy.deps is strategy_deps


@pytest.mark.asyncio
async def test_logic_strategy_execution_via_facade_factory(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify LogicNodeStrategy resolved via NodeStrategyFactory executes and emits TraceEvents."""
    in_memory_repo.set_step(
        {
            "id": "stp_0123456789abcdef0123456789abcdef",
            "slug": "logic_guard_step",
            "name": {"translations": {"en": "Logic Guard", "fi": "Logiikkavahti"}},
            "description": {"translations": {"en": "Logic Step", "fi": "Logiikkavaihe"}},
            "type": "logic",
            "hook": "noop_logic_hook",
        }
    )

    strategy = NodeStrategyFactory.create_strategy(StepType.LOGIC, deps=strategy_deps)
    assert isinstance(strategy, LogicNodeStrategy)

    step = StepRule(
        id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0123456789abcdef0123456789abcdef",
    )
    projector = MagicMock(spec=StateProjector)
    projector.snapshot = []
    context = StrategyContext(
        execution_id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        metadata=ExecutionMetadata(),
    )

    with patch(
        "backend_v2.services.orchestrator.strategies.logic.hook_registry.execute",
        new_callable=AsyncMock,
        return_value=HookResult(success=True),
    ):
        events = await strategy.execute(step=step, projector=projector, context=context)

    assert len(events) == 1
    assert events[0].step_name == step.id
    assert events[0].event_type == "output"


def test_llm_node_strategy_helper_delegation(
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify LLMNodeStrategy helper delegation for debug log errors and metadata extraction."""
    mock_engine = MagicMock(spec=SynthesisEngine)
    strategy = NodeStrategyFactory.create_strategy(
        StepType.LLM,
        deps=strategy_deps,
        engine=mock_engine,
    )
    assert isinstance(strategy, LLMNodeStrategy)

    # Exercise static debug log error handler
    LLMNodeStrategy._dlq_handle_debug_log_error(RuntimeError("Simulated debug write error"))

    # Exercise step context metadata extraction
    hook_state = HookState(
        execution_id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(language="en"),
        inputs=ExecutionInputsDTO(raw_inputs={"input_text": "Sample text"}),
    )
    ctx = StrategyContext(
        execution_id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        metadata=ExecutionMetadata(),
        context_variables=ContextVariablesDTO(variables={"doc_1": "Appendix B"}),
    )
    meta = strategy._extract_step_context_metadata(hook_state, ctx)
    assert meta.gvars["language"] == "en"
    assert meta.doc_aliases == ["N/A"]


@pytest.mark.asyncio
async def test_llm_node_strategy_execute_pipeline_via_facade(
    in_memory_repo: InMemoryUnifiedWorkflowRepository,
    strategy_deps: StrategyDependencies,
) -> None:
    """Verify full 4-stage pipeline orchestration of LLMNodeStrategy exported by strategies facade."""
    in_memory_repo.set_output_profiles(
        [
            {
                "id": "prf_0123456789abcdef0123456789abcdef",
                "slug": "test_profile",
                "name": {"translations": {"en": "Test Profile", "fi": "Testiprofiili"}},
                "workflow_id": "wf_0123456789abcdef0123456789abcdef",
                "organization_id": "root",
                "matrix_synthesis_groups": [
                    {
                        "id": "grp_0195f3a0000070018234567890123456",
                        "title": {"translations": {"en": "Test Group"}},
                        "target_blocks": ["*"],
                    }
                ],
            }
        ]
    )
    in_memory_repo.set_step(
        {
            "id": "stp_0123456789abcdef0123456789abcdef",
            "slug": "facade_test_step",
            "name": {"translations": {"en": "Facade Step", "fi": "Julkisivuvaihe"}},
            "description": {"translations": {"en": "Description", "fi": "Kuvaus"}},
            "role_block_id": None,
            "extraction_protocol_block_id": "blk_0195f3a000007005873802341db9d68c",
            "criteria_block_ids": ["blk_0123456789abcdef0123456789abcdef"],
        }
    )
    in_memory_repo.set_prompt_blocks(
        [
            {
                "id": "blk_0123456789abcdef0123456789abcdef",
                "slug": "criteria_block",
                "category_id": "system_rule",
                "type": "string",
                "label": {"translations": {"en": "Label", "fi": "Otsikko"}},
                "description": {"translations": {"en": "Desc", "fi": "Kuvaus"}},
                "instruction_text": "Evaluate input clarity.",
            },
            {
                "id": "blk_0195f3a000007005873802341db9d68c",
                "slug": "zero_trust_extraction_protocol",
                "category_id": "system_rule",
                "type": "instruction",
                "label": {"translations": {"en": "Zero-Trust", "fi": "Zero-Trust"}},
                "description": {"translations": {"en": "Zero-Trust", "fi": "Zero-Trust"}},
                "instruction_text": "Strict extraction protocol.",
            },
        ]
    )
    in_memory_repo.set_workflow(
        {
            "id": "wf_0123456789abcdef0123456789abcdef",
            "slug": "test_wf",
            "name": {"translations": {"en": "Test Workflow", "fi": "Testityönkulku"}},
            "description": {"translations": {"en": "Desc", "fi": "Kuvaus"}},
            "status": "draft",
            "version": 1,
            "default_profile_id": "prf_0123456789abcdef0123456789abcdef",
            "historical_context_mode": "DISABLED",
            "model_registry_id": "sys_0195f3a00000700e826807f3bfa3454d",
            "steps": [],
        }
    )

    mock_engine = MagicMock(spec=SynthesisEngine)
    mock_engine.execute = AsyncMock(
        return_value=EngineExecutionResult(
            results=[],
            hydrated_references={},
            usage=TokenUsage(prompt_tokens=20, completion_tokens=10, total_tokens=30, cost_usd=0.0005),
        )
    )

    strategy = NodeStrategyFactory.create_strategy(
        StepType.LLM,
        deps=strategy_deps,
        engine=mock_engine,
    )

    step = StepRule(
        id="sr_0195f3a0000070008123456789abcdef",
        task_blueprint="stp_0123456789abcdef0123456789abcdef",
        input_mappings={"$doc": "inputs.doc"},
    )
    projector = MagicMock(spec=StateProjector)
    projector.snapshot = [
        StepOutputDTO(step_id="inputs", block_id="doc", data_type="text", payload="Sample payload text")
    ]
    context = StrategyContext(
        execution_id="exe_0123456789abcdef0123456789abcdef",
        workflow_id="wf_0123456789abcdef0123456789abcdef",
        output_profile_id="prf_0123456789abcdef0123456789abcdef",
        metadata=ExecutionMetadata(),
    )

    hook_state = HookState(
        execution_id=context.execution_id,
        workflow_id=context.workflow_id,
        metadata=ExecutionMetadata(),
        global_context_vars=GlobalContextVarsDTO(),
        inputs=ExecutionInputsDTO(raw_inputs={"doc": "Sample payload text"}),
    )

    with (
        patch.object(strategy, "run_pre_hooks", new_callable=AsyncMock) as mock_pre,
        patch.object(strategy, "run_post_hooks", new_callable=AsyncMock) as mock_post,
        patch(
            "backend_v2.services.orchestrator.strategies.llm_strategy.LLMClient.from_tier",
            new_callable=AsyncMock,
            return_value=MagicMock(spec=LLMClient),
        ),
        patch("litellm.token_counter", return_value=12),
    ):
        mock_pre.return_value = (hook_state, [])
        mock_post.return_value = (hook_state, [])

        traces = await strategy.execute(
            step=step,
            projector=projector,
            context=context,
            frozen_ctx=None,
            trace=[],
        )

    assert len(traces) == 1
    assert traces[0].event_type == "output"
    assert traces[0].step_name == step.id


def test_negative_factory_missing_engine_for_llm_raises_app_exception(
    strategy_deps: StrategyDependencies,
) -> None:
    """Negative test (ISTQB): creating LLMNodeStrategy without ExecutionEngine raises AppException."""
    with pytest.raises(AppException) as exc_info:
        NodeStrategyFactory.create_strategy(StepType.LLM, deps=strategy_deps, engine=None)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
    assert "LLMNodeStrategy requires a non-null ExecutionEngine instance." in exc_info.value.message


def test_negative_factory_unregistered_step_type_raises_app_exception(
    strategy_deps: StrategyDependencies,
) -> None:
    """Negative test (ISTQB): requesting an unregistered StepType raises fail-fast AppException."""
    with (
        patch.dict(
            "backend_v2.services.orchestrator.strategies.registry.NODE_STRATEGY_REGISTRY",
            clear=True,
        ),
        pytest.raises(AppException) as exc_info,
    ):
        NodeStrategyFactory.create_strategy(StepType.LOGIC, deps=strategy_deps)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
    assert "Unsupported step type 'logic'. Must be registered in NODE_STRATEGY_REGISTRY." in exc_info.value.message


def test_negative_strategy_context_extra_field_and_strict_type_violation() -> None:
    """Negative test (ISTQB): StrategyContext rejects extra fields and invalid strict field types."""
    with pytest.raises(ValidationError):
        StrategyContext.model_validate(
            {
                "execution_id": "exe_1",
                "workflow_id": "wf_1",
                "metadata": ExecutionMetadata(),
                "undeclared_field": "forbidden",
            }
        )

    with pytest.raises(ValidationError):
        StrategyContext.model_validate(
            {
                "execution_id": "exe_1",
                "workflow_id": "wf_1",
                "metadata": ExecutionMetadata(),
                "strictness_level": "invalid_strictness_string",
            }
        )


@pytest.mark.asyncio
async def test_negative_llm_node_strategy_missing_blueprint_raises_app_exception(
    strategy_deps: StrategyDependencies,
) -> None:
    """Negative test (ISTQB): LLMNodeStrategy.execute fails fast when step has no task_blueprint."""
    mock_engine = MagicMock(spec=SynthesisEngine)
    strategy = LLMNodeStrategy(deps=strategy_deps, engine=mock_engine)

    step = MagicMock(spec=StepRule)
    step.id = "sr_0195f3a0000070008123456789abcdef"
    step.task_blueprint = None
    step.input_mappings = {}

    projector = MagicMock(spec=StateProjector)
    projector.snapshot = []
    context = StrategyContext(
        execution_id="exe_1",
        workflow_id="wf_1",
        metadata=ExecutionMetadata(),
    )

    with pytest.raises(AppException) as exc_info:
        await strategy.execute(step=step, projector=projector, context=context)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
