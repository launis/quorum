from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend_v2.exceptions import (
    AgentExecutionError,
    AppException,
    ConfigurationError,
    LLMSchemaValidationError,
    ServiceUnavailableError,
)
from backend_v2.llm.client import LLMClient
from backend_v2.models.enums import CognitiveTier, ExecutionProfile


class DummyConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = "mock_abcdef1234"
    provider: str = "openai"
    model_name: str = "pytest-model-1"
    temperature: float = 0.0
    default_max_tokens: int = 1000
    is_active: bool = True
    tpm_limit: int = 10000
    rpm_limit: int = 1000
    caching_strategy: str = "none"
    top_p: float | None = None
    top_k: int | None = None
    frequency_penalty: float | None = 0.0
    presence_penalty: float | None = 0.0


class DummyStrictModel(BaseModel):
    """Epic 12: Micro-CoT validation test model."""

    step_1_evidence_quote: str | None = Field(default=None)
    step_4_final_score: int

    @model_validator(mode="before")
    def force_logic(cls, values: Any) -> Any:
        """Socratic logic constraint."""
        if isinstance(values, dict):
            score = values.get("step_4_final_score")
            quote = values.get("step_1_evidence_quote")
            if score == 5 and not quote:
                raise ValueError("CRITICAL LOGICAL ERROR: High score but no quote.")
        return values


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_finops_circuit_breaker_missing_usage(mock_create_provider: MagicMock) -> None:
    """Epic 12 Phase 3: Assert missing token usage crashes the Node securely."""
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock()
    mock_create_provider.return_value = mock_provider

    # LLM Provider responds but "forgets" FinOps token metrics
    mock_response = MagicMock()
    mock_response.content = '{"step_4_final_score": 5}'
    mock_response.token_usage = None

    mock_provider.generate.return_value = mock_response

    client = LLMClient(config=DummyConfig().model_dump())

    # Circuit Breaker must trigger AgentExecutionError (CRITICAL)
    with pytest.raises(AgentExecutionError) as exc:
        await client.run_structured_task(
            messages=[{"role": "user", "content": "Test"}], response_model=DummyStrictModel
        )

    # Check for the correct 7807 Error Code inside the exception representation
    assert "AGENT_EXECUTION_CRITICAL" in str(exc.value)


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_semantic_self_healing_retry(mock_create_provider: MagicMock) -> None:
    """Epic 12 Phase 3: Assert Socratic prompt injection on logical validation errors."""
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock()
    mock_create_provider.return_value = mock_provider

    usage = {
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
        "cached_tokens": 0,
        "reasoning_tokens": 0,
        "cost_usd": 0.01,
    }

    # First Generation: LLM Hallucinates a high score without evidence
    mock_fail_response = MagicMock()
    mock_fail_response.content = '{"step_4_final_score": 5, "step_1_evidence_quote": null}'
    mock_fail_response.token_usage = usage

    # Second Generation: LLM fixes logic using the Socratic prompt
    mock_success_response = MagicMock()
    mock_success_response.content = '{"step_4_final_score": 5, "step_1_evidence_quote": "Found it"}'
    mock_success_response.token_usage = usage

    mock_provider.generate.side_effect = [mock_fail_response, mock_success_response]

    client = LLMClient(config=DummyConfig().model_dump())
    messages = [{"role": "user", "content": "Evaluate text"}]

    from backend_v2.services.llm_task_executor import LLMTaskExecutor
    from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler

    compiler = PromptCompiler()
    executor = LLMTaskExecutor(prompt_compiler=compiler)

    result_model, total_usage = await executor.execute_structured_task(
        client=client, messages=messages, response_model=DummyStrictModel, max_schema_retries=2, max_logical_retries=2
    )

    # 1. Structural Assertions
    assert mock_provider.generate.call_count == 2
    assert result_model.step_4_final_score == 5
    assert result_model.step_1_evidence_quote == "Found it"

    # 2. Cumulative FinOps Validation (10 + 10 prompt tokens, 5 + 5 completion)
    assert total_usage.completion_tokens == 10
    assert total_usage.total_tokens == 30
    assert abs(total_usage.cost_usd - 0.02) < 0.001

    # 3. Micro-CoT Feedback Injection Validation
    args, kwargs = mock_provider.generate.call_args_list[1]
    msgs = kwargs.get("messages", [])

    # The self-healing loop appends to the existing user message
    assert len(msgs) == 1
    last_msg = msgs[-1]
    socratic_system = last_msg.content if hasattr(last_msg, "content") else last_msg.get("content", "")

    # Confirm Semantic instruction strings
    assert "CRITICAL LOGICAL ERROR" in socratic_system
    assert "STRICT JSON SCHEMA VALIDATION FAILED" in socratic_system


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
@patch("backend_v2.llm.caching_service.LLMCachingService.prepare_caching_payload")
async def test_client_delegates_to_caching_service(mock_prepare: AsyncMock, mock_create_provider: MagicMock) -> None:
    """Ensure LLMClient delegates context caching to LLMCachingService and merges kwargs."""
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock()
    mock_create_provider.return_value = mock_provider

    mock_cache_response = MagicMock()
    mock_cache_response.content = '{"step_4_final_score": 3}'
    mock_cache_response.token_usage = {
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
        "cost_usd": 0.0,
    }
    mock_provider.generate.return_value = mock_cache_response

    mock_prepare.return_value = ([{"role": "system", "content": "mocked"}], {"caching_injected": True})

    c = DummyConfig()
    c.caching_strategy = "ephemeral"
    c.provider = "anthropic"
    client = LLMClient(config=c.model_dump())

    messages = [{"role": "system", "content": "Hello"}, {"role": "user", "content": "Test"}]
    await client.run_structured_task(messages=messages, response_model=DummyStrictModel)

    # Verify delegation
    mock_prepare.assert_called_once()

    # Verify that the generate call receives the manipulated messages and extra kwargs
    args, kwargs = mock_provider.generate.call_args
    assert kwargs["messages"] == [{"role": "system", "content": "mocked"}]
    assert kwargs["caching_injected"] is True


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_bubbles_up_service_unavailable_error(mock_create_provider: MagicMock) -> None:
    """Ensure transient network errors are not swallowed by the JSON schema parser."""
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock(side_effect=ServiceUnavailableError(message="Rate Limit", details=None))
    mock_create_provider.return_value = mock_provider

    client = LLMClient(config=DummyConfig().model_dump())
    messages = [{"role": "user", "content": "Test"}]

    # It MUST raise ServiceUnavailableError directly, NOT AgentExecutionError or LLMSchemaValidationError
    with pytest.raises(ServiceUnavailableError):
        await client.run_structured_task(messages=messages, response_model=DummyStrictModel)


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_bubbles_up_upstream_timeout_error(mock_create_provider: MagicMock) -> None:
    """Ensure upstream 503 / UPSTREAM_TIMEOUT errors bubble up directly and are not wrapped as LLMSchemaValidationError."""
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock(
        side_effect=AppException(
            message="Upstream LLM service timed out or is unavailable.",
            status_code=503,
            details={"error_code": "UPSTREAM_TIMEOUT"},
        )
    )
    mock_create_provider.return_value = mock_provider

    client = LLMClient(config=DummyConfig().model_dump())
    messages = [{"role": "user", "content": "Test"}]

    with pytest.raises(AppException) as exc_info:
        await client.run_structured_task(messages=messages, response_model=DummyStrictModel)

    assert not isinstance(exc_info.value, LLMSchemaValidationError)


from enum import StrEnum


class DummyEnum(StrEnum):
    PASSED = "PASSED"
    FAILED = "FAILED"


class DummyStrictEnumModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    status: DummyEnum


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_parses_strict_enum_from_json(mock_create_provider: MagicMock) -> None:
    """Tier 4 Regression: Ensure strict models with Enums are successfully parsed from LLM JSON strings."""
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock()
    mock_create_provider.return_value = mock_provider

    mock_response = MagicMock()
    mock_response.content = '{"status": "PASSED"}'
    mock_response.token_usage = {
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
        "cached_tokens": 0,
        "reasoning_tokens": 0,
        "cost_usd": 0.01,
    }
    mock_provider.generate.return_value = mock_response

    client = LLMClient(config=DummyConfig().model_dump())
    messages = [{"role": "user", "content": "Test"}]

    # This will raise LLMSchemaValidationError if the bug is present, failing the test if we assert it succeeds.
    # The proof of failure step means the test should crash/fail.
    result, usage = await client.run_structured_task(messages=messages, response_model=DummyStrictEnumModel)
    assert result.status == DummyEnum.PASSED


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_run_chat_success(mock_create_provider: MagicMock) -> None:
    """Test successful free-form chat generation."""
    mock_provider = AsyncMock()
    mock_provider.generate = AsyncMock()
    mock_create_provider.return_value = mock_provider

    mock_response = MagicMock()
    mock_response.content = "Chat success"
    mock_response.tool_calls = None
    mock_provider.generate.return_value = mock_response

    client = LLMClient(config=DummyConfig().model_dump())
    messages = [{"role": "user", "content": "Test"}]

    res = await client.run_chat(messages=messages, model="test-model")
    assert res == "Chat success"


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_run_chat_cache_miss_fallback(mock_create_provider: MagicMock) -> None:
    """Test run_chat cache miss fallback when cache returns 404."""
    mock_provider = AsyncMock()
    mock_create_provider.return_value = mock_provider

    mock_success_response = MagicMock()
    mock_success_response.content = "Fallback success"
    mock_success_response.tool_calls = None

    mock_provider.generate.side_effect = [Exception("404 Cached content not found"), mock_success_response]

    c = DummyConfig()
    c.caching_strategy = "ephemeral"
    client = LLMClient(config=c.model_dump())
    messages = [{"role": "user", "content": "Test"}]

    with patch(
        "backend_v2.llm.caching_service.LLMCachingService.prepare_caching_payload", new_callable=AsyncMock
    ) as mock_prepare:
        mock_prepare.return_value = ([{"role": "user", "content": "Test"}], {"cached_content": "cache_id"})
        res = await client.run_chat(messages=messages, model="test-model")
        assert res == "Fallback success"
        assert mock_provider.generate.call_count == 2
        # Assert cached_content was stripped in second call
        kwargs = mock_provider.generate.call_args_list[1].kwargs
        assert "cached_content" not in kwargs


@pytest.mark.asyncio
async def test_client_run_structured_task_missing_config() -> None:
    """Test AppException is raised when client is not configured via Strategy and model is missing."""
    client = LLMClient(config=None)
    with pytest.raises(AppException) as exc_info:
        await client.run_structured_task(
            messages=[{"role": "user", "content": "Test"}], response_model=DummyStrictModel
        )
    assert "Model Configuration Missing" in str(exc_info.value)


@pytest.mark.asyncio
async def test_client_run_chat_missing_config() -> None:
    """Test AppException is raised when client is not configured via Strategy and model is missing for chat."""
    client = LLMClient(config=None)
    with pytest.raises(AppException) as exc_info:
        await client.run_chat(messages=[{"role": "user", "content": "Test"}])
    assert "Model Configuration Missing" in str(exc_info.value)


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_run_structured_task_cache_miss_fallback(mock_create_provider: MagicMock) -> None:
    """Test run_structured_task cache miss fallback when cache returns 404."""
    mock_provider = AsyncMock()
    mock_create_provider.return_value = mock_provider

    mock_success_response = MagicMock()
    mock_success_response.content = '{"step_4_final_score": 1}'
    mock_success_response.token_usage = {
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
        "cost_usd": 0.0,
    }

    mock_provider.generate.side_effect = [Exception("404 Cached content not found"), mock_success_response]

    c = DummyConfig()
    c.caching_strategy = "ephemeral"
    client = LLMClient(config=c.model_dump())
    messages = [{"role": "user", "content": "Test"}]

    with patch(
        "backend_v2.llm.caching_service.LLMCachingService.prepare_caching_payload", new_callable=AsyncMock
    ) as mock_prepare:
        mock_prepare.return_value = ([{"role": "user", "content": "Test"}], {"cached_content": "cache_id"})
        res, _ = await client.run_structured_task(messages=messages, response_model=DummyStrictModel)
        assert res.step_4_final_score == 1
        assert mock_provider.generate.call_count == 2


@pytest.mark.asyncio
async def test_build_adapter_structured_schema_unconfigured() -> None:
    """Verify _build_structured_schema returns basic json_object when unconfigured."""
    client = LLMClient(config=None)
    schema = client._build_structured_schema(DummyStrictModel, final_messages=[], validation_context=None)
    assert schema == {"type": "json_object"}


@pytest.mark.asyncio
async def test_build_adapter_structured_schema_adapter_error() -> None:
    """Verify _build_structured_schema falls back to json_object on adapter exception."""
    c = DummyConfig()
    client = LLMClient(config=c.model_dump())
    with patch(
        "backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter",
        side_effect=Exception("Adapter boom"),
    ):
        schema = client._build_structured_schema(DummyStrictModel, final_messages=[], validation_context=None)
        assert schema == {"type": "json_object"}


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_run_structured_task_compiled_prompt(mock_create_provider: MagicMock) -> None:
    """Verify run_structured_task works when messages is a CompiledPrompt."""
    mock_provider = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = '{"step_4_final_score": 4}'
    mock_response.token_usage = {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15, "cost_usd": 0.0}
    mock_response.provider_metadata = None
    mock_provider.generate.return_value = mock_response
    mock_create_provider.return_value = mock_provider

    c = DummyConfig()
    client = LLMClient(config=c.model_dump())
    from backend_v2.models.llm import LLMMessageDTO
    from backend_v2.models.prompt import CompiledPrompt

    cp = CompiledPrompt(
        static_messages=[LLMMessageDTO(role="system", content="Sys")],
        dynamic_messages=[LLMMessageDTO(role="user", content="Hello")],
    )
    res, _ = await client.run_structured_task(messages=cp, response_model=DummyStrictModel)
    assert res.step_4_final_score == 4


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_run_chat_compiled_prompt(mock_create_provider: MagicMock) -> None:
    """Verify run_chat works when messages is a CompiledPrompt."""
    mock_provider = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = "Chat from compiled"
    mock_response.tool_calls = None
    mock_provider.generate.return_value = mock_response
    mock_create_provider.return_value = mock_provider

    c = DummyConfig()
    client = LLMClient(config=c.model_dump())
    from backend_v2.models.llm import LLMMessageDTO
    from backend_v2.models.prompt import CompiledPrompt

    cp = CompiledPrompt(
        static_messages=[LLMMessageDTO(role="system", content="Sys")],
        dynamic_messages=[LLMMessageDTO(role="user", content="Hello")],
    )
    res = await client.run_chat(messages=cp)
    assert res == "Chat from compiled"


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_from_tier_one_shot_execution_profile(
    mock_create_provider: MagicMock, mock_repository: AsyncMock
) -> None:
    """Verify from_tier disables caching when ExecutionProfile.ONE_SHOT is requested."""
    mock_create_provider.return_value = AsyncMock()
    client = await LLMClient.from_tier(
        tier=CognitiveTier.FAST,
        repository=mock_repository,
        execution_profile=ExecutionProfile.ONE_SHOT,
    )
    assert client.config.caching_strategy == "none"


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_run_chat_success(mock_create_provider: MagicMock) -> None:
    """Verify run_chat executes successfully and returns raw string content."""
    mock_provider = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = "Chat output"
    mock_response.tool_calls = None
    mock_provider.generate.return_value = mock_response
    mock_create_provider.return_value = mock_provider

    c = DummyConfig()
    client = LLMClient(config=c.model_dump())
    result = await client.run_chat(messages=[{"role": "user", "content": "Hello"}])
    assert result == "Chat output"


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_run_chat_tool_calls(mock_create_provider: MagicMock) -> None:
    """Verify run_chat returns tool_calls dictionary when tools are called."""
    mock_provider = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = "Tool output"
    mock_response.tool_calls = [{"name": "search", "arguments": {}}]
    mock_provider.generate.return_value = mock_response
    mock_create_provider.return_value = mock_provider

    c = DummyConfig()
    client = LLMClient(config=c.model_dump())
    result = await client.run_chat(
        messages=[{"role": "user", "content": "Call tool"}],
        tools=[{"type": "function"}],
    )
    assert isinstance(result, dict)
    assert "tool_calls" in result
    assert result["content"] == "Tool output"


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_run_chat_general_exception(mock_create_provider: MagicMock) -> None:
    """Verify run_chat wraps unexpected provider exceptions in AgentExecutionError."""
    mock_provider = AsyncMock()
    mock_provider.generate.side_effect = RuntimeError("Fatal LLM crash")
    mock_create_provider.return_value = mock_provider

    c = DummyConfig()
    client = LLMClient(config=c.model_dump())
    with pytest.raises(AgentExecutionError):
        await client.run_chat(messages=[{"role": "user", "content": "Boom"}])


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_run_structured_task_legacy_passthrough(mock_create_provider: MagicMock) -> None:
    """Verify run_structured_task works with explicit model argument when unconfigured."""
    mock_provider = AsyncMock()
    mock_response = MagicMock()
    mock_response.content = '{"step_4_final_score": 3}'
    mock_response.token_usage = {
        "prompt_tokens": 10,
        "completion_tokens": 5,
        "total_tokens": 15,
        "cost_usd": 0.0,
    }
    mock_response.provider_metadata = None
    mock_provider.generate.return_value = mock_response
    mock_create_provider.return_value = mock_provider

    client = LLMClient(config=None)
    result, usage = await client.run_structured_task(
        messages=[{"role": "user", "content": "Score"}],
        model="gpt-4",
        response_model=DummyStrictModel,
    )
    assert result.step_4_final_score == 3
    assert usage.total_tokens == 15


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_run_structured_task_general_exception(mock_create_provider: MagicMock) -> None:
    """Verify run_structured_task wraps unexpected exceptions in AgentExecutionError."""
    mock_provider = AsyncMock()
    mock_provider.generate.side_effect = RuntimeError("Network partition")
    mock_create_provider.return_value = mock_provider

    c = DummyConfig()
    client = LLMClient(config=c.model_dump())
    with pytest.raises(AgentExecutionError):
        await client.run_structured_task(
            messages=[{"role": "user", "content": "Fail"}],
            response_model=DummyStrictModel,
        )


@pytest.mark.asyncio
@patch("backend_v2.llm.provider.LLMFactory.create_provider")
async def test_client_run_structured_task_adapter_failure(mock_create_provider: MagicMock) -> None:
    """Verify run_structured_task raises ConfigurationError if adapter kwargs loading fails."""
    c = DummyConfig()
    client = LLMClient(config=c.model_dump())
    with patch(
        "backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter",
        side_effect=Exception("Adapter loading error"),
    ):
        with pytest.raises(ConfigurationError, match="LLM Adapter loading failed"):
            await client.run_structured_task(
                messages=[{"role": "user", "content": "Fail"}],
                response_model=DummyStrictModel,
            )


from backend_v2.tests.unit.llm.test_llm_client_tiers import (
    TestLLMClientCognitiveTiers as TestLLMClientCognitiveTiers,
    TestLLMClientTiersFailFast as TestLLMClientTiersFailFast,
    mock_repository as mock_repository,
)


def test_client_properties_unconfigured() -> None:
    """Verify unconfigured client defaults to 'unknown' and None config."""
    client = LLMClient()
    assert client.provider_name == "unknown"
    assert client.model_name == "unknown"
    assert client.config is None


@pytest.mark.asyncio
async def test_from_tier_query_failure_raises_configuration_error() -> None:
    """Verify repository query error bubbles up as ConfigurationError."""
    mock_repo = MagicMock()
    mock_repo.get_model_registry = AsyncMock(side_effect=ConnectionError("Database offline"))
    with pytest.raises(ConfigurationError, match="missing or query failed"):
        await LLMClient.from_tier(CognitiveTier.FAST, repository=mock_repo)


@patch("backend_v2.llm.provider.LLMFactory.create_provider")
@pytest.mark.asyncio
async def test_finops_invalid_token_usage_payload(mock_create_provider: MagicMock) -> None:
    """Verify FinOps raises AgentExecutionError when token_usage structure fails Pydantic validation."""
    mock_provider = AsyncMock()
    mock_create_provider.return_value = mock_provider
    mock_response = MagicMock()
    mock_response.token_usage = "not_a_valid_usage_structure"
    mock_provider.generate.return_value = mock_response

    c = DummyConfig()
    client = LLMClient(config=c.model_dump())
    with pytest.raises(AgentExecutionError):
        await client.run_structured_task(
            messages=[{"role": "user", "content": "Hi"}],
            response_model=DummyStrictModel,
        )


@patch("backend_v2.llm.provider.LLMFactory.create_provider")
@pytest.mark.asyncio
async def test_safety_filter_triggered(mock_create_provider: MagicMock) -> None:
    """Verify finish_reason safety triggers AgentExecutionError."""
    mock_provider = AsyncMock()
    mock_create_provider.return_value = mock_provider
    mock_response = MagicMock()
    mock_response.token_usage = {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
    mock_response.content = "Filtered output"
    mock_response.provider_metadata = MagicMock()
    mock_response.provider_metadata.finish_reason = "safety"
    mock_provider.generate.return_value = mock_response

    c = DummyConfig()
    client = LLMClient(config=c.model_dump())
    with pytest.raises(AgentExecutionError, match="Safety Filter Triggered"):
        await client.run_structured_task(
            messages=[{"role": "user", "content": "Hi"}],
            response_model=DummyStrictModel,
        )

