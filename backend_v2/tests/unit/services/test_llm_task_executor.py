from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel

from backend_v2.exceptions import AgentExecutionError, ErrorCodes, LLMSchemaValidationError, LogicalValidationError
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


class MockResponseSchema(BaseModel):
    value: str


@pytest.fixture
def mock_prompt_compiler() -> MagicMock:
    compiler = MagicMock(spec=PromptCompiler)
    compiler.get_schema_healing_prompt.return_value = "FIX THIS JSON"
    return compiler


@pytest.fixture
def mock_client() -> AsyncMock:
    client = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_execute_structured_task_success(mock_prompt_compiler: MagicMock, mock_client: AsyncMock) -> None:
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    expected_model = MockResponseSchema(value="success")
    expected_usage = {"total_tokens": 100, "prompt_tokens": 50, "completion_tokens": 50}

    mock_client.run_structured_task.return_value = (expected_model, expected_usage)

    messages = [{"role": "user", "content": "hello"}]

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
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    expected_model = MockResponseSchema(value="fixed")

    error = LLMSchemaValidationError(raw_llm_payload="bad json 1", validation_error_msg="syntax error 1", is_eof=False)

    mock_client.run_structured_task.side_effect = [
        error,
        (expected_model, {"total_tokens": 50, "prompt_tokens": 20, "completion_tokens": 30}),
    ]

    res_model, res_usage = await executor.execute_structured_task(
        client=mock_client,
        messages=[{"role": "system", "content": "sys"}, {"role": "user", "content": "user_payload"}],
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
    retry_messages = calls[1].kwargs["messages"]
    
    # Should still only be 2 messages (system, user), no new assistant message appended
    assert len(retry_messages) == 2
    assert retry_messages[0]["role"] == "system"
    assert retry_messages[1]["role"] == "user"
    assert "user_payload" in retry_messages[1]["content"]
    assert "<PREVIOUS_SCHEMA_ERROR>" in retry_messages[1]["content"]
    assert "FIX THIS JSON" in retry_messages[1]["content"]


@pytest.mark.asyncio
async def test_execute_structured_task_max_schema_retries_exceeded(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    error1 = LLMSchemaValidationError(raw_llm_payload="bad json 1", validation_error_msg="syntax error 1", is_eof=False)
    error2 = LLMSchemaValidationError(raw_llm_payload="bad json 2", validation_error_msg="syntax error 2", is_eof=False)

    mock_client.run_structured_task.side_effect = [error1, error2]

    with pytest.raises(AgentExecutionError) as exc_info:
        await executor.execute_structured_task(
            client=mock_client,
            messages=[{"role": "system", "content": "sys"}, {"role": "user", "content": "user_payload"}],
            response_model=MockResponseSchema,
            max_schema_retries=1,
        )

    assert exc_info.value.error_code == str(ErrorCodes.AGENT_SCHEMA_VALIDATION_FAILED)
    assert exc_info.value.details["validation_error_msg"] == "syntax error 2"


@pytest.mark.asyncio
async def test_execute_structured_task_stuck_loop_detection(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    # Identical payloads will trigger stuck loop immediately on the second attempt
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
            messages=[{"role": "user", "content": "user_payload"}],
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
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    expected_model = MockResponseSchema(value="fixed logic")

    # The client returns valid model, but validator_hook fails
    async def mock_validator(model: Any) -> None:
        if getattr(model, "value", None) == "bad logic":
            raise LogicalValidationError(validation_error_msg="Logical flaw detected")

    mock_client.run_structured_task.side_effect = [
        (MockResponseSchema(value="bad logic"), {"total_tokens": 10}),
        (expected_model, {"total_tokens": 15}),
    ]

    res_model, res_usage = await executor.execute_structured_task(
        client=mock_client,
        messages=[{"role": "system", "content": "sys"}, {"role": "user", "content": "user_payload"}],
        response_model=MockResponseSchema,
        max_logical_retries=1,
        validator_hook=mock_validator,
    )

    assert res_model.value == "fixed logic"
    # FinOps must accumulate tokens from both attempts
    assert res_usage.total_tokens == 25
    assert mock_client.run_structured_task.call_count == 2

    # Assert Prompt Topology and Tail-End Injection
    calls = mock_client.run_structured_task.call_args_list
    assert len(calls) == 2
    retry_messages = calls[1].kwargs["messages"]
    
    assert len(retry_messages) == 2
    assert retry_messages[0]["role"] == "system"
    assert retry_messages[1]["role"] == "user"
    assert "user_payload" in retry_messages[1]["content"]
    assert "<PREVIOUS_SCHEMA_ERROR>" in retry_messages[1]["content"]
    assert "Failed Output" in retry_messages[1]["content"]


@pytest.mark.asyncio
async def test_execute_chat_task(mock_prompt_compiler: MagicMock, mock_client: AsyncMock) -> None:
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    mock_client.run_chat.return_value = "chat response"

    res = await executor.execute_chat_task(client=mock_client, messages=[])
    assert res == "chat response"
    mock_client.run_chat.assert_called_once()
