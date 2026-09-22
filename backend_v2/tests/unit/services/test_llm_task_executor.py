"""Unit tests for LLMTaskExecutor service.

Validates structured generation, schema-healing retries, logical error trapping,
and token usage telemetry with strict DTO typing and Fail-Fast guarantees.
"""

from __future__ import annotations

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
from backend_v2.models.dtos.sensor import SensorValidationContextDTO
from backend_v2.models.llm import LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt, PromptMetadataDTO
from backend_v2.services.llm_task_executor import LLMTaskExecutor, _validate_non_empty_payload
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


class MockResponseSchema(BaseModel):
    """Mock response model for structured task execution testing."""

    value: str


class MockOverrideSchema(BaseModel):
    """Mock response model with contextual override fields."""

    value: str
    contextual_override: bool = False
    override_reason: str | None = None


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

    async def mock_validator(model: MockResponseSchema) -> None:
        if model.value == "bad logic":
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
        "backend_v2.services.llm_task_executor.write_llm_telemetry_log",
        new_callable=AsyncMock,
        side_effect=OSError("Telemetry fail"),
    ):
        res, _ = await executor.execute_structured_task(
            client=mock_client,
            messages=[LLMMessageDTO(role="user", content="Long enough payload text for passing validation")],
            response_model=MockResponseSchema,
        )
        assert res.value == "ok"


@pytest.mark.asyncio
async def test_execute_structured_task_debug_prompt_logging(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove structured task logs debug prompt when execution_id and step_id are present in development."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    mock_client.run_structured_task.return_value = (
        MockResponseSchema(value="logged"),
        {"prompt_tokens": 5, "completion_tokens": 5, "total_tokens": 10},
    )

    with (
        patch("backend_v2.services.llm_task_executor.get_settings") as mock_settings,
        patch("backend_v2.services.llm_task_executor.log_structured_task_prompt", new_callable=AsyncMock) as mock_log,
    ):
        mock_settings.return_value.environment = "development"
        mock_settings.return_value.llm_max_schema_retries = 2
        mock_settings.return_value.llm_max_logical_retries = 2
        mock_settings.return_value.llm_min_payload_length = 1

        res, _ = await executor.execute_structured_task(
            client=mock_client,
            messages=[LLMMessageDTO(role="user", content="Long enough payload text for passing validation")],
            response_model=MockResponseSchema,
            validation_context={"execution_id": "exec_456", "step_id": "stp_789", "sub_task": "bo3_0"},
        )
        assert res.value == "logged"
        mock_log.assert_awaited_once()
        assert mock_log.call_args.kwargs["execution_id"] == "exec_456"
        assert mock_log.call_args.kwargs["step_id"] == "stp_789"
        assert mock_log.call_args.kwargs["sub_task"] == "bo3_0"


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


@pytest.mark.asyncio
async def test_validate_non_empty_payload_with_cdata_encapsulation() -> None:
    """PROMISE: Prove payload validation preserves CDATA contents rather than stripping them as XML tags."""
    cdata_content = "This is a legitimate source claim document that contains more than enough characters to verify."
    user_payload = f"<source_data>\n<![CDATA[{cdata_content}]]>\n</source_data>"

    # This MUST NOT raise AppException because the actual user payload is well above llm_min_payload_length.
    _validate_non_empty_payload([LLMMessageDTO(role="user", content=user_payload)])

    # Multiple CDATA blocks with interspersed text
    multi_cdata = (
        "<source_data><![CDATA[Block one content ]]><extra>middle</extra><![CDATA[block two content]]></source_data>"
    )
    _validate_non_empty_payload([LLMMessageDTO(role="user", content=multi_cdata)])

    # Unclosed CDATA with sufficient length should be handled gracefully without crashing
    unclosed_cdata = "<source_data>\n<![CDATA[This is an unclosed CDATA block that has enough text content"
    _validate_non_empty_payload([LLMMessageDTO(role="user", content=unclosed_cdata)])

    # Empty CDATA block MUST raise AppException
    empty_cdata = "<source_data>\n<![CDATA[]]>\n</source_data>"
    with pytest.raises(AppException) as exc_empty:
        _validate_non_empty_payload([LLMMessageDTO(role="user", content=empty_cdata)])
    assert exc_empty.value.status_code == 400
    assert exc_empty.value.details.get("error_code") == ErrorCodes.VALIDATION_FAILED.value

    # Whitespace-only CDATA block MUST raise AppException
    ws_cdata = "<source_data>\n<![CDATA[   \n\t  ]]>\n</source_data>"
    with pytest.raises(AppException) as exc_ws:
        _validate_non_empty_payload([LLMMessageDTO(role="user", content=ws_cdata)])
    assert exc_ws.value.status_code == 400
    assert exc_ws.value.details.get("error_code") == ErrorCodes.VALIDATION_FAILED.value


@pytest.mark.asyncio
async def test_execute_structured_task_with_base_model_context_and_override(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove execute_structured_task accepts BaseModel validation context and logs contextual override."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    expected_model = MockOverrideSchema(value="ok", contextual_override=True, override_reason="Special edge case")
    expected_usage = TokenUsage(prompt_tokens=10, completion_tokens=15, total_tokens=25, cached_tokens=5)

    mock_client.run_structured_task.return_value = (expected_model, expected_usage)

    val_ctx = SensorValidationContextDTO(sub_task="bo3", execution_id="ex1", step_id="st1")

    res_model, res_usage = await executor.execute_structured_task(
        client=mock_client,
        messages=[LLMMessageDTO(role="user", content="Long valid payload for contextual override test")],
        response_model=MockOverrideSchema,
        validation_context=val_ctx,
    )

    assert res_model.contextual_override is True
    assert res_model.override_reason == "Special edge case"
    assert res_usage.total_tokens == 25


@pytest.mark.asyncio
async def test_execute_structured_task_schema_error_with_strictness_level(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove schema error healing passes strictness_level to compiler."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    expected_model = MockResponseSchema(value="healed")

    error = LLMSchemaValidationError(raw_llm_payload="bad json", validation_error_msg="syntax error", is_eof=False)

    mock_client.run_structured_task.side_effect = [
        error,
        (expected_model, TokenUsage(total_tokens=20, prompt_tokens=10, completion_tokens=10)),
    ]

    res, _ = await executor.execute_structured_task(
        client=mock_client,
        messages=[LLMMessageDTO(role="user", content="Valid long payload text for testing")],
        response_model=MockResponseSchema,
        max_schema_retries=1,
        validation_context={"strictness_level": 85},
    )

    assert res.value == "healed"
    mock_prompt_compiler.get_schema_healing_prompt.assert_called_with(
        error_msg="syntax error",
        is_logical_error=False,
        is_eof=False,
        strictness_level=85,
    )


@pytest.mark.asyncio
async def test_execute_structured_task_logical_error_stuck_loop(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove repeated identical logical errors trigger stuck loop detection."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    async def mock_validator(model: Any) -> None:
        raise LogicalValidationError(validation_error_msg="identical error")

    mock_client.run_structured_task.return_value = (
        MockResponseSchema(value="bad"),
        TokenUsage(total_tokens=10, prompt_tokens=5, completion_tokens=5),
    )

    with pytest.raises(AgentExecutionError) as exc_info:
        await executor.execute_structured_task(
            client=mock_client,
            messages=[LLMMessageDTO(role="user", content="Long enough payload text for passing validation")],
            response_model=MockResponseSchema,
            max_logical_retries=3,
            validator_hook=mock_validator,
        )
    assert exc_info.value.error_code == str(ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED)


@pytest.mark.asyncio
async def test_execute_structured_task_logical_error_empty_dynamic_messages_and_float_strictness(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove logical error with empty dynamic messages appends correctly and handles float strictness."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    async def mock_validator(model: Any) -> None:
        if model.value == "initial":
            raise LogicalValidationError(validation_error_msg="Float strictness logic error")

    mock_client.run_structured_task.side_effect = [
        (MockResponseSchema(value="initial"), TokenUsage(total_tokens=10, prompt_tokens=5, completion_tokens=5)),
        (MockResponseSchema(value="fixed"), TokenUsage(total_tokens=10, prompt_tokens=5, completion_tokens=5)),
    ]

    messages = CompiledPrompt(
        static_messages=[LLMMessageDTO(role="user", content="Long enough payload text for passing validation")],
        dynamic_messages=[],
        metadata=PromptMetadataDTO(),
    )

    res, _ = await executor.execute_structured_task(
        client=mock_client,
        messages=messages,
        response_model=MockResponseSchema,
        max_logical_retries=1,
        validator_hook=mock_validator,
        validation_context={"strictness_level": 70.0},
    )

    assert res.value == "fixed"
    mock_prompt_compiler.get_schema_healing_prompt.assert_called_with(
        error_msg="Float strictness logic error",
        is_logical_error=True,
        is_eof=False,
        strictness_level=70,
    )


@pytest.mark.asyncio
async def test_execute_structured_task_debug_prompt_logging_failure(
    mock_prompt_compiler: MagicMock, mock_client: AsyncMock
) -> None:
    """PROMISE: Prove debug prompt logging failure in development is gracefully dispatched without crashing."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)
    mock_client.run_structured_task.return_value = (
        MockResponseSchema(value="ok"),
        TokenUsage(total_tokens=10, prompt_tokens=5, completion_tokens=5),
    )

    with (
        patch("backend_v2.services.llm_task_executor.get_settings") as mock_settings,
        patch(
            "backend_v2.services.llm_task_executor.log_structured_task_prompt",
            new_callable=AsyncMock,
            side_effect=OSError("Log failure"),
        ),
    ):
        mock_settings.return_value.environment = "development"
        mock_settings.return_value.llm_max_schema_retries = 2
        mock_settings.return_value.llm_max_logical_retries = 2
        mock_settings.return_value.llm_min_payload_length = 1

        res, _ = await executor.execute_structured_task(
            client=mock_client,
            messages=[LLMMessageDTO(role="user", content="Long enough payload text for passing validation")],
            response_model=MockResponseSchema,
            validation_context={"execution_id": "exec_1", "step_id": "step_1"},
        )
        assert res.value == "ok"


@pytest.mark.asyncio
async def test_validate_non_empty_payload_with_dict_and_non_sequence() -> None:
    """PROMISE: Prove payload validation handles dictionary message input and non-sequence structures."""
    # Dict item in messages
    _validate_non_empty_payload([{"role": "user", "content": "Valid payload text inside a dictionary format."}])

    # Non-sequence payload falls back to empty and raises
    with pytest.raises(AppException) as exc_info:
        _validate_non_empty_payload(123)  # type: ignore[arg-type]
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_execute_structured_task_loop_exhaustion(mock_prompt_compiler: MagicMock, mock_client: AsyncMock) -> None:
    """PROMISE: Prove loop exhaustion raises AGENT_EXECUTION_CRITICAL when 0 attempts are allowed."""
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    with pytest.raises(AgentExecutionError) as exc_info:
        await executor.execute_structured_task(
            client=mock_client,
            messages=[LLMMessageDTO(role="user", content="Long enough payload text for passing validation")],
            response_model=MockResponseSchema,
            max_schema_retries=-1,
            max_logical_retries=-1,
        )
    assert exc_info.value.error_code == str(ErrorCodes.AGENT_EXECUTION_CRITICAL)
