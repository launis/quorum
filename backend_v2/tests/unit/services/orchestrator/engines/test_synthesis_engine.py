"""Unit tests for SynthesisEngine."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException
from backend_v2.llm.client import LLMClient
from backend_v2.models.dtos.engine import EngineExecutionRequest
from backend_v2.models.state import TokenUsage
from backend_v2.models.v2_core import StepRule
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.engines.synthesis_engine import SynthesisEngine
from backend_v2.services.orchestrator.strategies.base import StrategyContext


class MockSynthesisOutput(BaseModel):
    """Mock structured output for synthesis."""

    title: str = Field(...)
    content: str = Field(...)
    model_config = ConfigDict(strict=True, extra="forbid")


@pytest.fixture
def mock_executor() -> AsyncMock:
    """Provides a mocked LLMTaskExecutor."""
    executor = AsyncMock(spec=LLMTaskExecutor)
    return executor


@pytest.fixture
def engine(mock_executor: AsyncMock) -> SynthesisEngine:
    """Provides a configured SynthesisEngine."""
    return SynthesisEngine(llm_executor=mock_executor)


@pytest.fixture
def base_request() -> EngineExecutionRequest:
    """Provides a base valid request with hydrated messages."""
    step = StepRule(id="sr_1234567890abcdef1234", task_blueprint="bp_1")
    context = StrategyContext(
        execution_id="exec_1",
        workflow_id="wf_1",
        metadata={},
        context_variables={
            "__GLOBAL_ATOM_BLACKBOARD__": {
                "atoms_by_input": {},
            }
        },
    )

    return EngineExecutionRequest(
        bound_client=MagicMock(spec=LLMClient),
        compiled_schema=MockSynthesisOutput,
        hydrated_messages=[{"role": "system", "content": "You are an assistant."}],
        system_prompt="You are an assistant.",
        step=step,
        context=context,
        global_source_text="Test source text.",
        target_locale="en",
        semaphore=asyncio.Semaphore(1),
        running_event=None,
        progress_callback=None,
        trace_callback=None,
        prompt_compiler=None,
    )


@pytest.mark.asyncio
async def test_synthesis_engine_missing_blackboard_crashes(
    engine: SynthesisEngine, base_request: EngineExecutionRequest
) -> None:
    """Tests that missing blackboard fails fast with AppException."""
    # Remove blackboard
    base_request.context.context_variables.pop("__GLOBAL_ATOM_BLACKBOARD__")

    with pytest.raises(AppException) as exc_info:
        await engine.execute(base_request)

    assert exc_info.value.details is not None
    assert exc_info.value.details.get("error_code") == "SYNTHESIS_ENGINE_ERROR"


@pytest.mark.asyncio
async def test_synthesis_engine_happy_path(
    engine: SynthesisEngine, mock_executor: AsyncMock, base_request: EngineExecutionRequest
) -> None:
    """Tests successful synthesis execution."""
    mock_output = MockSynthesisOutput(title="Test", content="Data")
    mock_usage = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30, cost_usd=0.01)

    mock_executor.execute_structured_task.return_value = (mock_output, mock_usage)

    result = await engine.execute(base_request)

    assert result.results == []
    assert result.hydrated_references == {}
    assert result.synthesis_output is not None
    assert result.synthesis_output["title"] == "Test"
    assert result.synthesis_output["content"] == "Data"

    assert len(result.trace_events) == 1
    trace = result.trace_events[0]
    assert trace.step_name == "sr_1234567890abcdef1234"
    assert trace.event_type == "output"
    assert trace.content["title"] == "Test"
    assert trace.content["_step_metadata"]["token_usage"]["total_tokens"] == 30


@pytest.mark.asyncio
async def test_synthesis_engine_immutable_messages(
    engine: SynthesisEngine, mock_executor: AsyncMock, base_request: EngineExecutionRequest
) -> None:
    """Tests that original request.hydrated_messages is not mutated by engine injection."""
    mock_output = MockSynthesisOutput(title="Test", content="Data")
    mock_usage = TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
    mock_executor.execute_structured_task.return_value = (mock_output, mock_usage)

    original_messages_len = len(base_request.hydrated_messages)  # type: ignore

    await engine.execute(base_request)

    # original message list length should be unchanged
    assert len(base_request.hydrated_messages) == original_messages_len  # type: ignore


@pytest.mark.asyncio
async def test_synthesis_engine_exception_wrapping(
    engine: SynthesisEngine, mock_executor: AsyncMock, base_request: EngineExecutionRequest
) -> None:
    """Tests that raw exceptions are wrapped in AppException."""
    mock_executor.execute_structured_task.side_effect = ValueError("Network Error")

    with pytest.raises(AppException) as exc_info:
        await engine.execute(base_request)

    assert "Network Error" in str(exc_info.value)
    assert exc_info.value.status_code == 500
    assert exc_info.value.details is not None
    assert exc_info.value.details.get("error_code") == "SYNTHESIS_ENGINE_ERROR"
