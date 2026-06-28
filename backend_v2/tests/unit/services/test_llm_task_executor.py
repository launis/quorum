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
    client._config = None
    return client


@pytest.mark.asyncio
async def test_execute_structured_task_success(mock_prompt_compiler: MagicMock, mock_client: AsyncMock) -> None:
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    expected_model = MockResponseSchema(value="success")
    expected_usage = {"total_tokens": 100, "prompt_tokens": 50, "completion_tokens": 50}

    mock_client.run_structured_task.return_value = (expected_model, expected_usage)

    messages = [{"role": "user", "content": "hello world payload"}]

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
    retry_prompt = calls[1].kwargs["messages"]
    flat_messages = retry_prompt.to_flat_messages()

    # Should still only be 2 messages (system, user), no new assistant message appended
    assert len(flat_messages) == 2
    assert flat_messages[0]["role"] == "system"
    assert flat_messages[1]["role"] == "user"
    assert "user_payload" in flat_messages[1]["content"]
    assert "<PREVIOUS_SCHEMA_ERROR>" in flat_messages[1]["content"]
    assert "FIX THIS JSON" in flat_messages[1]["content"]


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
    assert isinstance(exc_info.value.original_error, LLMSchemaValidationError)
    assert exc_info.value.original_error.validation_error_msg == "syntax error 2"


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
        (MockResponseSchema(value="bad logic"), {"total_tokens": 10, "prompt_tokens": 5, "completion_tokens": 5}),
        (expected_model, {"total_tokens": 15, "prompt_tokens": 7, "completion_tokens": 8}),
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
    retry_prompt = calls[1].kwargs["messages"]
    flat_messages = retry_prompt.to_flat_messages()

    assert len(flat_messages) == 2
    assert flat_messages[0]["role"] == "system"
    assert flat_messages[1]["role"] == "user"
    assert "user_payload" in flat_messages[1]["content"]
    assert "<PREVIOUS_SCHEMA_ERROR>" in flat_messages[1]["content"]
    assert "Failed Output" in flat_messages[1]["content"]


@pytest.mark.asyncio
async def test_execute_chat_task(mock_prompt_compiler: MagicMock, mock_client: AsyncMock) -> None:
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    mock_client.run_chat.return_value = "chat response"

    res = await executor.execute_chat_task(client=mock_client, messages=[])
    assert res == "chat response"
    mock_client.run_chat.assert_called_once()


@pytest.mark.asyncio
async def test_execute_structured_task_system_wide_lexical_verifier(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    class TestResponseModel(BaseModel):
        exact_quotes: list[str] | None = None
        reasoning_trace: str
        score: int | None = None
        justification: str | None = None

    expected_model = TestResponseModel(exact_quotes=["fake quote"], reasoning_trace="fake trace")

    mock_client.run_structured_task.side_effect = [
        (expected_model, {"total_tokens": 10, "prompt_tokens": 5, "completion_tokens": 5}),
        (expected_model, {"total_tokens": 15, "prompt_tokens": 7, "completion_tokens": 8}),
    ]

    from unittest.mock import patch

    from backend_v2.exceptions import SemanticEvidenceError

    with patch("backend_v2.services.llm_task_executor.AnchorValidationService.validate_evidence") as mock_validate:
        mock_validate.side_effect = SemanticEvidenceError(message="fail fast")

        with pytest.raises(AgentExecutionError) as exc_info:
            await executor.execute_structured_task(
                client=mock_client,
                messages=[{"role": "user", "content": "this is a valid test payload"}],
                response_model=TestResponseModel,
                max_logical_retries=1,
                validation_context={"source_text": "real text"},
            )

        assert exc_info.value.error_code == str(ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED)
        mock_validate.assert_called_with("real text", ["fake quote"], reasoning_trace="fake trace", locale=None)


@pytest.mark.asyncio
async def test_execute_structured_task_dynamic_model_fallback(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    class AtomResponse(BaseModel):
        atom_id: str
        exact_quotes: list[str] | None = None
        localized_anchors_found: list[str] = []
        contextual_override: bool = False
        semantic_reasoning: str = ""

    class DynamicResponseModel(BaseModel):
        reasoning_trace: str
        evaluation_notes: str
        evaluations: list[AtomResponse]

    expected_model = DynamicResponseModel(
        reasoning_trace="fake trace",
        evaluation_notes="fake notes",
        evaluations=[
            AtomResponse(
                atom_id="atom_1",
                exact_quotes=["hallucinated quote"],
                localized_anchors_found=[],
                contextual_override=False,
                semantic_reasoning="some reasoning",
            )
        ],
    )

    mock_client.run_structured_task.side_effect = [
        (expected_model, {"total_tokens": 10, "prompt_tokens": 5, "completion_tokens": 5}),
        (expected_model, {"total_tokens": 15, "prompt_tokens": 7, "completion_tokens": 8}),
    ]

    from unittest.mock import patch

    from backend_v2.exceptions import SemanticEvidenceError

    with patch("backend_v2.services.llm_task_executor.AnchorValidationService.validate_evidence") as mock_validate:
        mock_validate.side_effect = SemanticEvidenceError(message="fail fast")

        with pytest.raises(AgentExecutionError) as exc_info:
            await executor.execute_structured_task(
                client=mock_client,
                messages=[{"role": "user", "content": "this is a valid test payload"}],
                response_model=DynamicResponseModel,
                max_logical_retries=1,
                validation_context={"source_text": "real text"},
            )

        assert exc_info.value.error_code == str(ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED)
