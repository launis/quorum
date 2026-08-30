"""Unit tests for PromptEngine execution and fail-fast validation."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel, Field

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.engine import EngineExecutionRequest
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.models.v2_core import StepRule
from backend_v2.services.orchestrator.engines.prompt_engine import PromptEngine
from backend_v2.services.orchestrator.strategies.base import StrategyContext


class MockResponseModel(BaseModel):
    summary: str = Field(description="Summary text.")


@pytest.fixture
def mock_executor() -> MagicMock:
    executor = MagicMock()
    executor.execute_structured_task = AsyncMock()
    return executor


@pytest.fixture
def base_request() -> EngineExecutionRequest:
    step = StepRule(
        id="stp_1111111111111111",
        task_blueprint="bp_1111111111111111",
    )
    context = StrategyContext(
        execution_id="exe_1111111111111111",
        workflow_id="wf_1111111111111111",
        metadata=ExecutionMetadata(profile_id="prof_1111111111111111", target_locale="en"),
        expected_inputs=[],
        model_strategy="fast",
        strictness_level=0,
        global_context_vars={},
        context_variables={},
    )
    client = MagicMock(spec=LLMClient)

    return EngineExecutionRequest(
        bound_client=client,
        compiled_schema=MockResponseModel,
        hydrated_messages=[{"role": "user", "content": "Hello"}],
        system_prompt="Test",
        step=step,
        context=context,
        global_source_text="Test source text",
        target_locale="en",
        semaphore=None,
        running_event=None,
        progress_callback=None,
        trace_callback=None,
        prompt_compiler=MagicMock(),
    )


@pytest.mark.asyncio
async def test_prompt_engine_executes_successfully(
    mock_executor: MagicMock, base_request: EngineExecutionRequest
) -> None:
    """Verify PromptEngine executes structured task and returns typed result."""
    expected_output = MockResponseModel(summary="Generated summary")
    expected_usage = TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    mock_executor.execute_structured_task.return_value = (expected_output, expected_usage)

    running_event = asyncio.Event()
    request = base_request.model_copy(update={"running_event": running_event})

    engine = PromptEngine(task_executor=mock_executor)
    result = await engine.execute(request)

    assert running_event.is_set()
    assert result.synthesis_output == expected_output
    assert result.usage == expected_usage
    assert result.results == []
    assert result.hydrated_references == {}
    mock_executor.execute_structured_task.assert_called_once_with(
        client=request.bound_client,
        messages=request.hydrated_messages,
        response_model=MockResponseModel,
    )


@pytest.mark.asyncio
async def test_prompt_engine_fails_fast_when_schema_missing(
    mock_executor: MagicMock, base_request: EngineExecutionRequest
) -> None:
    """Verify PromptEngine raises AppException with PROMPT_ENGINE_ERROR if compiled_schema is None."""
    request = base_request.model_copy(update={"compiled_schema": None})
    engine = PromptEngine(task_executor=mock_executor)

    with pytest.raises(AppException) as exc_info:
        await engine.execute(request)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.PROMPT_ENGINE_ERROR.value
    assert "requires compiled_schema" in exc_info.value.message


@pytest.mark.asyncio
async def test_prompt_engine_fails_fast_when_messages_empty(
    mock_executor: MagicMock, base_request: EngineExecutionRequest
) -> None:
    """Verify PromptEngine raises AppException with PROMPT_ENGINE_ERROR if hydrated_messages is empty."""
    request = base_request.model_copy(update={"hydrated_messages": []})
    engine = PromptEngine(task_executor=mock_executor)

    with pytest.raises(AppException) as exc_info:
        await engine.execute(request)

    assert exc_info.value.status_code == 500
    assert exc_info.value.details["error_code"] == ErrorCodes.PROMPT_ENGINE_ERROR.value
    assert "empty hydrated_messages" in exc_info.value.message


@pytest.mark.asyncio
async def test_prompt_engine_respects_semaphore(mock_executor: MagicMock, base_request: EngineExecutionRequest) -> None:
    """Verify PromptEngine acquires semaphore during execution."""
    expected_output = MockResponseModel(summary="Semaphore test")
    expected_usage = TokenUsage(prompt_tokens=5, completion_tokens=5, total_tokens=10)
    mock_executor.execute_structured_task.return_value = (expected_output, expected_usage)

    semaphore = asyncio.Semaphore(1)
    request = base_request.model_copy(update={"semaphore": semaphore})

    engine = PromptEngine(task_executor=mock_executor)
    result = await engine.execute(request)

    assert result.synthesis_output == expected_output
    assert semaphore._value == 1


def test_engines_exports_all_symbols() -> None:
    """Verify __all__ contains exactly the intended public engine symbols."""
    import backend_v2.services.orchestrator.engines as engines_module
    from backend_v2.services.orchestrator.engines import (
        ExecutionEngine,
        PromptEngine,
        SynthesisEngine,
        TDAEngine,
    )

    expected_symbols = {
        "ExecutionEngine",
        "PromptEngine",
        "SynthesisEngine",
        "TDAEngine",
    }
    assert set(engines_module.__all__) == expected_symbols
    assert ExecutionEngine is not None
    assert PromptEngine is not None
    assert SynthesisEngine is not None
    assert TDAEngine is not None
