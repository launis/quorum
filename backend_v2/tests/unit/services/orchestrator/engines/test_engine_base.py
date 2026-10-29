"""Unit tests for ExecutionEngine protocol."""

from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.step import StepRule
from backend_v2.models.dtos.engine import EngineExecutionRequest, EngineExecutionResult
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.services.orchestrator.engines.base import ExecutionEngine
from backend_v2.services.orchestrator.strategies.base import StrategyContext


class ValidEngine:
    """Valid engine implementation for protocol testing."""

    @property
    def telemetry_strategy_label(self) -> str:
        return "valid_engine"

    async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:
        return EngineExecutionResult(results=[], hydrated_references={})


class MissingExecuteEngine:
    """Invalid engine missing execute method."""

    @property
    def telemetry_strategy_label(self) -> str:
        return "missing_execute"


class MissingLabelEngine:
    """Invalid engine missing telemetry_strategy_label property."""

    async def execute(self, request: EngineExecutionRequest) -> EngineExecutionResult:
        return EngineExecutionResult(results=[], hydrated_references={})


class NonEngine:
    """Completely unrelated class."""

    pass


class DummyResponseSchema(BaseModel):
    pass


def test_execution_engine_protocol_valid_implementation() -> None:
    """Verify that a compliant class satisfies the runtime checkable protocol."""
    engine = ValidEngine()
    assert isinstance(engine, ExecutionEngine)
    assert engine.telemetry_strategy_label == "valid_engine"


def test_execution_engine_protocol_negative_missing_methods() -> None:
    """Verify that incomplete classes fail the runtime checkable protocol check."""
    assert not isinstance(MissingExecuteEngine(), ExecutionEngine)
    assert not isinstance(MissingLabelEngine(), ExecutionEngine)
    assert not isinstance(NonEngine(), ExecutionEngine)


@pytest.mark.asyncio
async def test_execution_engine_protocol_execution_roundtrip() -> None:
    """Verify that a valid engine executes and returns EngineExecutionResult."""
    engine = ValidEngine()
    step = StepRule(
        id="stp_0195f3a0000070018111111111111111",
        task_blueprint="bp_0195f3a0000070018111111111111111",
    )
    context = StrategyContext(
        execution_id="exe_0195f3a0000070018111111111111111",
        workflow_id="wf_0195f3a0000070018111111111111111",
        output_profile_id="prof_0195f3a0000070018111111111111111",
        target_locale="en",
        metadata=ExecutionMetadata(),
        expected_inputs=[],
        strictness_level=0,
        global_context_vars={},
        context_variables={},
    )
    request = EngineExecutionRequest(
        bound_client=MagicMock(spec=LLMClient),
        compiled_schema=DummyResponseSchema,
        hydrated_messages=[],
        system_prompt="Test system prompt",
        step=step,
        context=context,
        global_source_text="Test source text",
        target_locale="en",
        progress_callback=None,
        trace_callback=None,
        prompt_compiler=MagicMock(),
    )
    result = await engine.execute(request)
    assert isinstance(result, EngineExecutionResult)
    assert result.results == []
    assert result.hydrated_references == {}
