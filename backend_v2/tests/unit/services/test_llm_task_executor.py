"""Unit tests for LLMTaskExecutor service.

Validates structured generation, schema-healing retries, logical error trapping,
and token usage telemetry with strict DTO typing and Fail-Fast guarantees.
"""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from backend_v2.exceptions import (
    AgentExecutionError,
    AppException,
    ErrorCodes,
    LLMSchemaValidationError,
    LogicalValidationError,
)
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.prompt_context import PromptContextDTO
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt, PromptMetadataDTO
from backend_v2.services.llm_task_executor import LLMTaskExecutor, _validate_non_empty_payload
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


class MockResponseSchema(BaseModel):
    """Mock response model for structured task execution testing."""

    value: str


@pytest.fixture
def mock_prompt_compiler() -> MagicMock:
    """Fixture providing a mocked PromptCompiler."""
    compiler = MagicMock(spec=PromptCompiler)
    compiler.get_schema_healing_prompt.return_value = "FIX THIS JSON"
    return compiler


@pytest.fixture
def mock_client() -> AsyncMock:
    """Fixture providing a mocked LLMClient."""
    client = AsyncMock()
    client._config = None
    return client


@pytest.mark.asyncio
async def test_execute_structured_task_success(mock_prompt_compiler: MagicMock, mock_client: AsyncMock) -> None:
    """PROMISE: Prove execute_structured_task parses valid responses and aggregates token usage."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    expected_model = MockResponseSchema(value="success")
    expected_usage = {"total_tokens": 100, "prompt_tokens": 50, "completion_tokens": 50}

    mock_client.run_structured_task.return_value = (expected_model, expected_usage)

    messages = [LLMMessageDTO(role="user", content="hello world payload")]

    res_model, res_usage = await executor.execute_structured_task(
        client=mock_client, messages=messages, response_model=MockResponseSchema
    )

    assert res_model.value == "success"
    assert res_usage.total_tokens == 100
    mock_client.run_structured_task.assert_called_once()


@pytest.mark.asyncio
async def test_execute_structured_task_retry_on_schema_error(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove execute_structured_task retries on schema validation failure with healing prompt."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    expected_model = MockResponseSchema(value="fixed")

    error = LLMSchemaValidationError(raw_llm_payload="bad json 1", validation_error_msg="syntax error 1", is_eof=False)

    mock_client.run_structured_task.side_effect = [
        error,
        (expected_model, {"total_tokens": 50, "prompt_tokens": 20, "completion_tokens": 30}),
    ]

    res_model, res_usage = await executor.execute_structured_task(
        client=mock_client,
        messages=[
            LLMMessageDTO(role="system", content="sys"),
            LLMMessageDTO(role="user", content="user_payload"),
        ],
        response_model=MockResponseSchema,
        max_schema_retries=1,
    )

    assert res_model.value == "fixed"
    assert res_usage.total_tokens == 50
    assert mock_client.run_structured_task.call_count == 2
    mock_prompt_compiler.get_schema_healing_prompt.assert_called_once()

    # Assert Prompt Topology and Tail-End Injection
    calls = mock_client.run_structured_task.call_args_list
    assert len(calls) == 2
    retry_prompt = calls[1].kwargs["messages"]
    flat_messages = retry_prompt.to_flat_messages()

    # Should still only be 2 messages (system, user), no new assistant message appended
    assert len(flat_messages) == 2
    assert flat_messages[0].role == "system"
    assert flat_messages[1].role == "user"
    assert "user_payload" in flat_messages[1].content
    assert "<PREVIOUS_SCHEMA_ERROR>" in flat_messages[1].content
    assert "FIX THIS JSON" in flat_messages[1].content


@pytest.mark.asyncio
async def test_execute_structured_task_max_schema_retries_exceeded(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove execute_structured_task raises AgentExecutionError when max retries are exceeded."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    error1 = LLMSchemaValidationError(raw_llm_payload="bad json 1", validation_error_msg="syntax error 1", is_eof=False)
    error2 = LLMSchemaValidationError(raw_llm_payload="bad json 2", validation_error_msg="syntax error 2", is_eof=False)

    mock_client.run_structured_task.side_effect = [error1, error2]

    with pytest.raises(AgentExecutionError) as exc_info:
        await executor.execute_structured_task(
            client=mock_client,
            messages=[
                LLMMessageDTO(role="system", content="sys"),
                LLMMessageDTO(role="user", content="user_payload"),
            ],
            response_model=MockResponseSchema,
            max_schema_retries=1,
        )

    assert exc_info.value.error_code == str(ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED)
    assert isinstance(exc_info.value.original_error, LLMSchemaValidationError)
    assert exc_info.value.original_error.validation_error_msg == "syntax error 2"


@pytest.mark.asyncio
async def test_execute_structured_task_stuck_loop_detection(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove execute_structured_task aborts stuck loop on identical schema error payloads."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    error1 = LLMSchemaValidationError(
        raw_llm_payload="identical bad json", validation_error_msg="syntax error", is_eof=False
    )
    error2 = LLMSchemaValidationError(
        raw_llm_payload="identical bad json", validation_error_msg="syntax error", is_eof=False
    )

    mock_client.run_structured_task.side_effect = [error1, error2]

    with pytest.raises(AgentExecutionError) as exc_info:
        await executor.execute_structured_task(
            client=mock_client,
            messages=[LLMMessageDTO(role="user", content="user_payload")],
            response_model=MockResponseSchema,
            max_schema_retries=5,
        )

    # Should fail on 2nd attempt, not wait for 5
    assert mock_client.run_structured_task.call_count == 2
    assert exc_info.value.error_code == str(ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED)


@pytest.mark.asyncio
async def test_execute_structured_task_logical_error_retry(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove execute_structured_task retries on logical validator failure and accumulates tokens."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    expected_model = MockResponseSchema(value="fixed logic")

    async def mock_validator(model: Any) -> None:
        if getattr(model, "value", None) == "bad logic":
            raise LogicalValidationError(validation_error_msg="Logical flaw detected")

    mock_client.run_structured_task.side_effect = [
        (MockResponseSchema(value="bad logic"), {"total_tokens": 10, "prompt_tokens": 5, "completion_tokens": 5}),
        (expected_model, {"total_tokens": 15, "prompt_tokens": 7, "completion_tokens": 8}),
    ]

    res_model, res_usage = await executor.execute_structured_task(
        client=mock_client,
        messages=[
            LLMMessageDTO(role="system", content="sys"),
            LLMMessageDTO(role="user", content="user_payload"),
        ],
        response_model=MockResponseSchema,
        max_logical_retries=1,
        validator_hook=mock_validator,
    )

    assert res_model.value == "fixed logic"
    assert res_usage.total_tokens == 25
    assert mock_client.run_structured_task.call_count == 2

    # Assert Prompt Topology and Tail-End Injection
    calls = mock_client.run_structured_task.call_args_list
    assert len(calls) == 2
    retry_prompt = calls[1].kwargs["messages"]
    flat_messages = retry_prompt.to_flat_messages()

    assert len(flat_messages) == 2
    assert flat_messages[0].role == "system"
    assert flat_messages[1].role == "user"
    assert "user_payload" in flat_messages[1].content
    assert "<PREVIOUS_SCHEMA_ERROR>" in flat_messages[1].content
    assert "Failed Output" in flat_messages[1].content


@pytest.mark.asyncio
async def test_validate_non_empty_payload_too_short(mock_prompt_compiler: MagicMock, mock_client: AsyncMock) -> None:
    """PROMISE: Prove execute_structured_task rejects payload that is too short with status_code 400."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    with pytest.raises(AppException) as exc_info:
        await executor.execute_structured_task(
            client=mock_client,
            messages=[LLMMessageDTO(role="user", content="a")],
            response_model=MockResponseSchema,
        )
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_execute_structured_task_compiled_prompt_and_metadata(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove execute_structured_task processes CompiledPrompt with custom validation context."""
    executor = LLMTaskExecutor(
        prompt_compiler=mock_prompt_compiler,
        default_validation_context={"execution_id": "test", "step_id": "test_step"},
    )

    messages = CompiledPrompt(
        static_messages=[
            LLMMessageDTO(
                role="user", content="This is a very long payload to pass the minimum validation length check."
            )
        ],
        dynamic_messages=[],
        metadata=PromptMetadataDTO(),
    )

    mock_client.run_structured_task.return_value = (
        MockResponseSchema(value="ok"),
        {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
    )
    res_model, _ = await executor.execute_structured_task(
        client=mock_client, messages=messages, response_model=MockResponseSchema, validation_context={"custom": "meta"}
    )
    assert res_model.value == "ok"


@pytest.mark.asyncio
async def test_execute_structured_task_telemetry_failure(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove telemetry failure does not crash successful structured task execution."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    mock_client.run_structured_task.return_value = (
        MockResponseSchema(value="ok"),
        {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
    )

    with patch(
        "backend_v2.services.llm_task_executor.write_llm_telemetry_log", side_effect=Exception("Telemetry fail")
    ):
        res, _ = await executor.execute_structured_task(
            client=mock_client,
            messages=[LLMMessageDTO(role="user", content="Long enough payload text for passing validation")],
            response_model=MockResponseSchema,
        )
        assert res.value == "ok"


@pytest.mark.asyncio
async def test_execute_structured_task_schema_error_no_dynamic_messages(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove schema error retries work correctly when CompiledPrompt has empty dynamic_messages."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    error = LLMSchemaValidationError(raw_llm_payload="bad json", validation_error_msg="syntax error", is_eof=False)
    error.token_usage = TokenUsage(total_tokens=5, prompt_tokens=2, completion_tokens=3)

    mock_client.run_structured_task.side_effect = [
        error,
        (MockResponseSchema(value="fixed"), {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10}),
    ]

    messages = CompiledPrompt(
        static_messages=[LLMMessageDTO(role="user", content="Long enough payload text for passing validation")],
        dynamic_messages=[],
        metadata=PromptMetadataDTO(),
    )

    res, usage = await executor.execute_structured_task(
        client=mock_client,
        messages=messages,
        response_model=MockResponseSchema,
        max_schema_retries=1,
    )

    assert res.value == "fixed"
    assert usage.total_tokens == 15


@pytest.mark.asyncio
async def test_execute_structured_task_logical_error_max_retries_and_stuck_loop(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove logical error exceeding max retries raises AGENT_LOGICAL_VALIDATION_FAILED."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    async def mock_validator(model: Any) -> None:
        raise LogicalValidationError(validation_error_msg="Logical flaw detected")

    mock_client.run_structured_task.return_value = (
        MockResponseSchema(value="bad logic"),
        {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
    )

    with pytest.raises(AgentExecutionError) as exc_info:
        await executor.execute_structured_task(
            client=mock_client,
            messages=[LLMMessageDTO(role="user", content="Long enough payload text for passing validation")],
            response_model=MockResponseSchema,
            max_logical_retries=1,
            validator_hook=mock_validator,
        )
    assert exc_info.value.error_code == str(ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED)


@pytest.mark.asyncio
async def test_execute_structured_task_logical_error_coaching_notes(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove coaching directives for ellipses and brackets are injected into retry prompt."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    async def mock_validator(model: Any) -> None:
        if "bad" in model.value:
            raise LogicalValidationError(validation_error_msg="Logic error")

    bad_model = MockResponseSchema(value="bad logic ... [")
    good_model = MockResponseSchema(value="good logic")

    mock_client.run_structured_task.side_effect = [
        (bad_model, {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10}),
        (good_model, {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10}),
    ]

    res, _ = await executor.execute_structured_task(
        client=mock_client,
        messages=[LLMMessageDTO(role="user", content="Long enough payload text for passing validation")],
        response_model=MockResponseSchema,
        max_logical_retries=1,
        validator_hook=mock_validator,
    )

    assert res.value == "good logic"

    calls = mock_client.run_structured_task.call_args_list
    retry_prompt = calls[1].kwargs["messages"]
    flat_messages = retry_prompt.to_flat_messages()
    assert "COACHING: You used ellipses" in flat_messages[-1].content
    assert "COACHING: You injected square brackets" in flat_messages[-1].content


@pytest.mark.asyncio
async def test_execute_structured_task_with_prompt_context_dto(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove PromptContextDTO is properly accepted and converted by execute_structured_task."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    expected_model = MockResponseSchema(value="context_dto_success")
    expected_usage = {"total_tokens": 80, "prompt_tokens": 40, "completion_tokens": 40}

    mock_client.run_structured_task.return_value = (expected_model, expected_usage)

    prompt_context = PromptContextDTO(
        static_messages=[LLMMessageDTO(role="system", content="System instruction context.")],
        dynamic_messages=[LLMMessageDTO(role="user", content="User payload for analysis.")],
        metadata={"token_proxy_score": 0.95},
    )

    res_model, res_usage = await executor.execute_structured_task(
        client=mock_client,
        messages=prompt_context,
        response_model=MockResponseSchema,
    )

    assert res_model.value == "context_dto_success"
    assert res_usage.total_tokens == 80


@pytest.mark.asyncio
async def test_execute_chat_task(mock_prompt_compiler: MagicMock, mock_client: AsyncMock) -> None:
    """PROMISE: Prove execute_chat_task delegates cleanly to client.run_chat."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    mock_client.run_chat.return_value = "chat response output"

    res = await executor.execute_chat_task(client=mock_client, prompt="hello chat")

    assert res == "chat response output"
    mock_client.run_chat.assert_called_once_with(prompt="hello chat")


@pytest.mark.asyncio
async def test_validate_non_empty_payload_edge_cases(mock_prompt_compiler: MagicMock) -> None:
    """PROMISE: Prove _validate_non_empty_payload edge cases and type validations."""
    # Valid message list with LLMMessageDTO
    _validate_non_empty_payload([LLMMessageDTO(role="user", content="Adequate non-empty payload content here.")])

    # Too short payload raises AppException
    with pytest.raises(AppException):
        _validate_non_empty_payload([LLMMessageDTO(role="user", content="a")])
