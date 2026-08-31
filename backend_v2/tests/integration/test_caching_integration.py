"""Integration tests for LLM Caching integration, Self-Healing purity, and Fail-Soft path."""

import hashlib
import json
import sys
from typing import Any, cast
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

# Mock vertexai / GCP SDK BEFORE any imports
if not hasattr(sys, "_mock_cached_contents"):
    sys._mock_cached_contents = MagicMock()  # type: ignore[attr-defined]

mock_cached_contents = sys._mock_cached_contents  # type: ignore[attr-defined]


class MockGenerativeModels:
    cached_contents = mock_cached_contents


class MockPreview:
    generative_models = MockGenerativeModels


class MockVertexAI:
    preview = MockPreview

    @classmethod
    def init(cls, *args: Any, **kwargs: Any) -> None:
        pass


sys.modules["vertexai"] = cast(Any, MockVertexAI)
sys.modules["vertexai.preview"] = cast(Any, MockPreview)
sys.modules["vertexai.preview.generative_models"] = cast(Any, MockGenerativeModels)

from backend_v2.llm.client import LLMClient
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.models.prompt import CompiledPrompt
from backend_v2.services.llm_task_executor import LLMTaskExecutor
from backend_v2.services.orchestrator.prompt_compiler import PromptCompiler


class IntegrationResponseSchema(BaseModel):
    extracted_value: str


@pytest.fixture(autouse=True)
def mock_redis_client(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Mock get_redis_client to return FakeRedis instance to avoid event loop issues."""
    from fakeredis.aioredis import FakeRedis

    fake_client = FakeRedis()

    async def mock_get_redis_client() -> Any:
        return fake_client

    monkeypatch.setattr(
        "backend_v2.llm.adapters.vertex_adapter.get_redis_client",
        mock_get_redis_client,
    )
    return fake_client


@pytest.fixture
def mock_prompt_compiler() -> MagicMock:
    compiler = MagicMock(spec=PromptCompiler)
    compiler.get_schema_healing_prompt.return_value = "FIX THIS JSON"
    return compiler


@pytest.mark.asyncio
async def test_executor_with_mock_cache_adapter_success(
    mock_prompt_compiler: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that LLMTaskExecutor executes a structured call successfully with MockCacheAdapter."""
    # 1. Setup provider config utilizing our mock provider
    provider_config = LLMProviderConfig(
        id="prv_mocktest123",
        provider="mock_llm_99",
        model_name="mock",
        api_key="mock_key",
        temperature=0.7,
        tpm_limit=10000,
        rpm_limit=100,
        caching_strategy="ephemeral",
    )

    client = LLMClient(config=provider_config)
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    # 2. Spy on run_structured_task calls
    captured_calls = []

    async def spy_run(
        response_model: Any,
        messages: Any,
        **kwargs: Any,
    ) -> Any:
        captured_calls.append(messages)
        # Mock LLM success return
        return IntegrationResponseSchema(extracted_value="mocked-success"), TokenUsage(
            prompt_tokens=100, completion_tokens=50, total_tokens=150
        )

    monkeypatch.setattr(client, "run_structured_task", spy_run)

    # 3. Execute
    messages = [
        {"role": "system", "content": "You are a specialized parser system."},
        {"role": "user", "content": "Input raw payload analysis."},
    ]

    res_model, usage = await executor.execute_structured_task(
        client=client,
        messages=messages,
        response_model=IntegrationResponseSchema,
    )

    # 4. Assertions
    assert res_model.extracted_value == "mocked-success"
    assert usage.total_tokens == 150
    assert len(captured_calls) == 1

    # Verify that the flat messages compiled under caching are passed
    first_call_msg = captured_calls[0]
    assert isinstance(first_call_msg, CompiledPrompt)
    assert first_call_msg.static_messages[0]["content"] == "You are a specialized parser system."


@pytest.mark.asyncio
async def test_self_healing_static_purity_preservation(
    mock_prompt_compiler: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that during Self-Healing retries, static prompt SHA-256 remains 100% pure."""
    provider_config = LLMProviderConfig(
        id="prv_mocktest456",
        provider="mock_llm_99",
        model_name="mock",
        api_key="mock_key",
        temperature=0.7,
        tpm_limit=10000,
        rpm_limit=100,
        caching_strategy="ephemeral",
    )

    client = LLMClient(config=provider_config)
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    call_count = 0
    captured_messages: list[Any] = []

    async def mock_run_structured(
        response_model: Any,
        messages: Any,
        **kwargs: Any,
    ) -> Any:
        nonlocal call_count
        call_count += 1
        captured_messages.append(messages)

        if call_count == 1:
            # First call fails schema validation (syntax error)
            from backend_v2.exceptions import LLMSchemaValidationError

            raise LLMSchemaValidationError(
                raw_llm_payload="invalid-json",
                validation_error_msg="Missing closing brace",
                is_eof=False,
                token_usage=TokenUsage(prompt_tokens=10, completion_tokens=0, total_tokens=10),
            )

        # Second call succeeds
        return IntegrationResponseSchema(extracted_value="healed-success"), TokenUsage(
            prompt_tokens=200, completion_tokens=50, total_tokens=250
        )

    monkeypatch.setattr(client, "run_structured_task", mock_run_structured)

    # 3. Execute with caching active
    initial_messages = [
        {"role": "system", "content": "Primal instructions"},
        {"role": "user", "content": "Analyze document"},
    ]

    res_model, usage = await executor.execute_structured_task(
        client=client,
        messages=initial_messages,
        response_model=IntegrationResponseSchema,
        max_schema_retries=2,
    )

    # 4. Verify Static Purity & Hash parity
    assert res_model.extracted_value == "healed-success"
    assert len(captured_messages) == 2

    first_prompt = captured_messages[0]
    second_prompt = captured_messages[1]

    assert isinstance(first_prompt, CompiledPrompt)
    assert isinstance(second_prompt, CompiledPrompt)

    # Static parts must match exactly!
    assert first_prompt.static_messages == second_prompt.static_messages

    # Get SHA-256 of static messages for both attempts
    hash_1 = hashlib.sha256(json.dumps(first_prompt.static_messages, sort_keys=True).encode()).hexdigest()
    hash_2 = hashlib.sha256(json.dumps(second_prompt.static_messages, sort_keys=True).encode()).hexdigest()

    assert hash_1 == hash_2  # 100% static-purity preservation!

    # The error should reside strictly at the tail of dynamic_messages
    assert len(second_prompt.dynamic_messages) > 0
    assert "<PREVIOUS_SCHEMA_ERROR>" in second_prompt.dynamic_messages[-1]["content"]


@pytest.mark.asyncio
async def test_vertex_fail_soft_resilience_integration(
    mock_prompt_compiler: MagicMock, monkeypatch: pytest.MonkeyPatch, mock_redis_client: Any
) -> None:
    """Verify Fail-Soft fallback: when Vertex Cache adapter throws, completion executes uncached."""
    # Reset call counts
    mock_cached_contents.CachedContent.create.reset_mock()
    # Mock CachedContent.create to throw a GCP Quota / Network exception
    mock_cached_contents.CachedContent.create.side_effect = Exception("Vertex Context Cache quota exceeded.")

    provider_config = LLMProviderConfig(
        id="prv_vertextest",
        provider="vertex_ai",
        model_name="vertex_ai/gemini-1.5-pro",
        api_key="mock_vertex_key",
        temperature=0.7,
        tpm_limit=10000,
        rpm_limit=100,
        caching_strategy="ephemeral",
    )

    client = LLMClient(config=provider_config)
    executor = LLMTaskExecutor(prompt_compiler=mock_prompt_compiler)

    # Mock LiteLLMProvider.generate to bypass the actual Vertex call
    generate_called = False

    async def mock_provider_generate(*args: Any, **kwargs: Any) -> Any:
        nonlocal generate_called
        generate_called = True

        # Verify that "cached_content" is NOT passed down since creation failed!
        assert "cached_content" not in kwargs

        # Returns mock response
        from backend_v2.models.llm import LLMResponse

        return LLMResponse(
            content=json.dumps({"extracted_value": "fail-soft-success"}),
            parsed_content=None,
            token_usage=TokenUsage(prompt_tokens=200000, completion_tokens=100, total_tokens=200100),
            provider_metadata={},
        )

    # Apply mock to LiteLLMProvider.generate
    monkeypatch.setattr("backend_v2.llm.provider.LiteLLMProvider.generate", mock_provider_generate)

    # Generate a massive prompt (over Vertex caching character threshold)
    large_static = "A" * 150000
    messages = [
        {"role": "system", "content": "You are a helpful analyst."},
        {"role": "user", "content": large_static},
        {"role": "user", "content": "Extract dynamic insight"},
    ]

    # Execute structuring task, should complete cleanly despite the Vertex API Context Caching failure!
    res_model, usage = await executor.execute_structured_task(
        client=client,
        messages=messages,
        response_model=IntegrationResponseSchema,
    )

    # Verify fail-soft success
    assert res_model.extracted_value == "fail-soft-success"
    assert generate_called is True
    assert mock_cached_contents.CachedContent.create.call_count == 1

    # Verify that the FAILED sentinel status was written to the shared ledger to lock it out
    from backend_v2.services.orchestrator.prompt_compiler_adapter import PromptCompilerAdapter

    # The actual static_messages is compiled by PromptCompilerAdapter.compile_prompt
    compiled_p = PromptCompilerAdapter().compile_prompt(messages)
    actual_hash = hashlib.sha256(json.dumps(compiled_p.static_messages, sort_keys=True).encode()).hexdigest()
    redis_key = f"vertex_cache:europe-north1:vertex_ai/gemini-1.5-pro:{actual_hash}"

    status = await mock_redis_client.get(redis_key)
    if isinstance(status, bytes):
        status = status.decode("utf-8")
    assert status == "FAILED"
