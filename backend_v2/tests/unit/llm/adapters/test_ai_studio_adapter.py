"""Unit tests for GoogleAIStudioCacheAdapter."""

from __future__ import annotations

import asyncio
import hashlib
import json
import sys
from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.prompt import CompiledPrompt

# Setup mock modules for google.genai BEFORE importing adapter
if not hasattr(sys, "_mock_genai_client"):
    sys._mock_genai_client = MagicMock()  # type: ignore[attr-defined]

mock_genai_client = sys._mock_genai_client  # type: ignore[attr-defined]


class MockGenAITypes:
    @staticmethod
    def CreateCachedContentConfig(*args: Any, **kwargs: Any) -> Any:
        config = MagicMock()
        config.contents = kwargs.get("contents")
        config.ttl = kwargs.get("ttl")
        config.system_instruction = kwargs.get("system_instruction")
        return config


class MockGenAIModule:
    types = MockGenAITypes

    @staticmethod
    def Client(*args: Any, **kwargs: Any) -> Any:
        return mock_genai_client


mock_google = MagicMock()
mock_google.genai = MockGenAIModule
mock_google.genai.types = MockGenAITypes

sys.modules["google"] = cast(Any, mock_google)
sys.modules["google.genai"] = cast(Any, MockGenAIModule)
sys.modules["google.genai.types"] = cast(Any, MockGenAITypes)

from backend_v2.llm.adapters.ai_studio_adapter import (  # noqa: E402
    GoogleAIStudioCacheAdapter,
    GoogleAIStudioTokenUsage,
    get_redis_client,
)


@pytest.fixture(autouse=True)
def mock_redis_client(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Mock get_redis_client to return a fresh FakeRedis instance per test, avoiding event loop issues."""
    from fakeredis.aioredis import FakeRedis

    fake_client = FakeRedis()

    async def mock_get_redis_client() -> Any:
        return fake_client

    monkeypatch.setattr(
        "backend_v2.llm.adapters.ai_studio_adapter.get_redis_client",
        mock_get_redis_client,
    )
    monkeypatch.setattr(
        f"{__name__}.get_redis_client",
        mock_get_redis_client,
    )
    return fake_client


@pytest.mark.asyncio
async def test_ai_studio_adapter_preparer_bypass() -> None:
    """Verify AI Studio adapter bypasses caching for small prompts under 32,768 tokens."""
    adapter = GoogleAIStudioCacheAdapter()

    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Small static content under threshold."},
        ],
        dynamic_messages=[
            {"role": "assistant", "content": "Response."},
        ],
    )

    op_messages, op_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-3.7-flash")
    assert op_messages == prompt.to_flat_messages()
    assert op_kwargs == {}


@pytest.mark.asyncio
async def test_ai_studio_teardown_is_noop() -> None:
    """Verify teardown is successfully executed as No-Op."""
    adapter = GoogleAIStudioCacheAdapter()
    await adapter.teardown_cache("run_12345")


def test_ai_studio_adapter_cost_calculation() -> None:
    """Verify precision cost calculation with 75% read caching discount."""
    adapter = GoogleAIStudioCacheAdapter()
    usage = TokenUsage(
        prompt_tokens=100000,
        completion_tokens=2000,
        total_tokens=102000,
        cached_tokens=80000,
    )
    pricing = {
        "input_token_price": 0.000001,
        "output_token_price": 0.000004,
    }

    result = adapter.calculate_cost(usage, pricing)
    assert isinstance(result, GoogleAIStudioTokenUsage)
    # regular_input = 20000 * 0.000001 = 0.02
    # cached_input = 80000 * 0.000001 * 0.25 = 0.02
    # output = 2000 * 0.000004 = 0.008
    # total_cost = 0.048
    # total_savings = 80000 * 0.000001 * 0.75 = 0.06
    assert pytest.approx(result.cost_usd, rel=1e-5) == 0.048
    assert pytest.approx(result.estimated_savings_usd, rel=1e-5) == 0.06


def test_ai_studio_missing_pricing_raises_error() -> None:
    """Verify error is raised when pricing is missing required keys."""
    adapter = GoogleAIStudioCacheAdapter()
    usage = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
    with pytest.raises(AppException):
        adapter.calculate_cost(usage, {})


def test_ai_studio_token_usage_negative_savings_raises() -> None:
    """Verify negative estimated savings raises validation error."""
    with pytest.raises(ValueError, match="estimated_savings_usd must be greater than or equal to 0.0"):
        GoogleAIStudioTokenUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150,
            estimated_savings_usd=-0.05,
        )


def test_ai_studio_adapter_prepare_provider_kwargs() -> None:
    """Verify safety settings returned for LiteLLM."""
    adapter = GoogleAIStudioCacheAdapter()
    kwargs = adapter.prepare_provider_kwargs("gemini-3.7-flash")
    assert "safety_settings" in kwargs
    assert len(kwargs["safety_settings"]) == 4


def test_ai_studio_adapter_prepare_kwargs_thinking_and_cached_content() -> None:
    """Verify prepare_kwargs maps thinking budget and cached content to extra_body."""
    adapter = GoogleAIStudioCacheAdapter()

    config_mock = MagicMock()
    config_mock.additional_params = {"thinking_budget_tokens": 2048}

    call_kwargs: dict[str, Any] = {
        "cached_content": "cachedContents/ai-studio-cache-123",
        "messages": [
            {"role": "system", "content": "Stray system message"},
            {"role": "user", "content": "User prompt"},
        ],
    }

    result = adapter.prepare_kwargs(call_kwargs, config=config_mock)

    assert result["extra_body"]["cachedContent"] == "cachedContents/ai-studio-cache-123"
    assert result["extra_body"]["cached_content"] == "cachedContents/ai-studio-cache-123"
    assert result["extra_body"]["generationConfig"]["thinkingConfig"]["thinkingBudget"] == 2048
    assert len(result["messages"]) == 1
    assert result["messages"][0]["role"] == "user"


@pytest.mark.asyncio
async def test_ai_studio_thundering_herd_protection() -> None:
    """Verify that multiple concurrent workers for the same prompt create cache only once."""
    mock_genai_client.caches.create.reset_mock()

    class DummyCacheObj:
        name = "cachedContents/ai-studio-shared-cache-99"

    mock_genai_client.caches.create.return_value = DummyCacheObj()

    large_static = "A" * 150000
    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": "You are an analytical evaluator."},
            {"role": "user", "content": large_static},
        ],
        dynamic_messages=[
            {"role": "user", "content": "Query"},
        ],
    )

    adapter = GoogleAIStudioCacheAdapter()
    redis_client = await get_redis_client()
    static_hash = hashlib.sha256(json.dumps(prompt.static_messages, sort_keys=True).encode()).hexdigest()
    redis_key = f"ai_studio_cache:gemini-3.7-flash:{static_hash}"
    lock_key = f"lock:ai_studio_cache:gemini-3.7-flash:{static_hash}"
    await redis_client.delete(redis_key, lock_key)

    tasks = [adapter.prepare_caching_payload(prompt, "gemini-3.7-flash") for _ in range(5)]
    results = await asyncio.gather(*tasks)

    assert mock_genai_client.caches.create.call_count == 1

    expected_cache = "cachedContents/ai-studio-shared-cache-99"
    for _, extra_kwargs in results:
        assert extra_kwargs == {"cached_content": expected_cache}


@pytest.mark.asyncio
async def test_ai_studio_fail_soft_error() -> None:
    """Verify that when google.genai cache creation raises, it falls back cleanly to uncached."""
    mock_genai_client.caches.create.reset_mock()
    mock_genai_client.caches.create.side_effect = Exception("API Key invalid or quota reached.")

    large_static = "A" * 150000
    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": "You are an analytical evaluator."},
            {"role": "user", "content": large_static},
        ],
        dynamic_messages=[
            {"role": "user", "content": "Query"},
        ],
    )

    adapter = GoogleAIStudioCacheAdapter()
    redis_client = await get_redis_client()
    static_hash = hashlib.sha256(json.dumps(prompt.static_messages, sort_keys=True).encode()).hexdigest()
    redis_key = f"ai_studio_cache:gemini-3.7-flash:{static_hash}"
    lock_key = f"lock:ai_studio_cache:gemini-3.7-flash:{static_hash}"
    await redis_client.delete(redis_key, lock_key)

    flat_msgs, extra_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-3.7-flash")
    assert extra_kwargs == {}
    assert mock_genai_client.caches.create.call_count == 1

    status = await redis_client.get(redis_key)
    if isinstance(status, bytes):
        status = status.decode("utf-8")
    assert status == "FAILED"


@pytest.mark.asyncio
async def test_ai_studio_cache_immediate_hit_in_shared_ledger() -> None:
    """Verify that an existing cache in Redis returns immediately without lock or SDK creation."""
    adapter = GoogleAIStudioCacheAdapter()
    large_static = "A" * 150000
    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": "You are an analytical evaluator."},
            {"role": "user", "content": large_static},
        ],
        dynamic_messages=[{"role": "user", "content": "Query"}],
    )

    redis_client = await get_redis_client()
    static_hash = hashlib.sha256(json.dumps(prompt.static_messages, sort_keys=True).encode()).hexdigest()
    redis_key = f"ai_studio_cache:gemini-3.7-flash:{static_hash}"
    existing_cache_id = "cachedContents/hit-12345"
    await redis_client.set(redis_key, existing_cache_id, ex=300)

    dynamic_msgs, extra_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-3.7-flash")
    assert extra_kwargs == {"cached_content": existing_cache_id}
    assert len(dynamic_msgs) == 1


@pytest.mark.asyncio
async def test_ai_studio_instant_exit_on_failed() -> None:
    """Verify that if a sentinel FAILED is found in Redis, adapter immediately returns flat messages."""
    mock_genai_client.caches.create.reset_mock()

    large_static = "A" * 150000
    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": "You are an analytical evaluator."},
            {"role": "user", "content": large_static},
        ],
        dynamic_messages=[{"role": "user", "content": "Query"}],
    )

    adapter = GoogleAIStudioCacheAdapter()
    redis_client = await get_redis_client()
    static_hash = hashlib.sha256(json.dumps(prompt.static_messages, sort_keys=True).encode()).hexdigest()
    redis_key = f"ai_studio_cache:gemini-3.7-flash:{static_hash}"
    lock_key = f"lock:ai_studio_cache:gemini-3.7-flash:{static_hash}"
    await redis_client.delete(redis_key, lock_key)

    await redis_client.set(redis_key, "FAILED", ex=300)

    flat_msgs, extra_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-3.7-flash")
    assert extra_kwargs == {}
    assert mock_genai_client.caches.create.call_count == 0


@pytest.mark.asyncio
async def test_ai_studio_cache_wait_and_poll_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify wait-and-poll loop handles timeout when lock is held by another worker."""
    from backend_v2.settings import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "context_cache_lock_poll_interval_ms", 1)
    monkeypatch.setattr(settings, "context_cache_lock_wait_limit_seconds", 0.005)

    large_static = "A" * 150000
    prompt = CompiledPrompt(
        static_messages=[{"role": "user", "content": large_static}],
        dynamic_messages=[],
    )

    adapter = GoogleAIStudioCacheAdapter()
    redis_client = await get_redis_client()
    static_hash = hashlib.sha256(json.dumps(prompt.static_messages, sort_keys=True).encode()).hexdigest()
    redis_key = f"ai_studio_cache:gemini-3.7-flash:{static_hash}"
    lock_key = f"lock:ai_studio_cache:gemini-3.7-flash:{static_hash}"

    await redis_client.set(lock_key, "worker_0", ex=10)
    await redis_client.set(redis_key, "CREATING", ex=10)

    flat_msgs, extra_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-3.7-flash")
    assert extra_kwargs == {}
    assert len(flat_msgs) == 1


@pytest.mark.asyncio
async def test_ai_studio_adapter_static_chars_with_content_blocks() -> None:
    """Verify token estimation handles content formatted as list of text blocks and assistant role mapping."""
    mock_genai_client.caches.create.reset_mock()
    mock_genai_client.caches.create.side_effect = None

    class DummyCacheObj:
        name = "cachedContents/blocks-cache-123"

    mock_genai_client.caches.create.return_value = DummyCacheObj()

    large_block = "C" * 150000
    adapter = GoogleAIStudioCacheAdapter()

    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": "System instructions here."},
            {"role": "assistant", "content": [{"type": "text", "text": large_block}]},
        ],
        dynamic_messages=[],
    )

    returned_msgs, extra_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-3.7-flash")
    assert extra_kwargs == {"cached_content": "cachedContents/blocks-cache-123"}
    assert mock_genai_client.caches.create.call_count == 1


def test_ai_studio_adapter_prepare_structured_output() -> None:
    """Verify prepare_structured_output formats JSON schema and strips unsupported constraints."""
    from pydantic import BaseModel, Field

    class SampleSchema(BaseModel):
        name: str = Field(min_length=2)
        score: int = Field(ge=0, le=100)

    adapter = GoogleAIStudioCacheAdapter()
    result = adapter.prepare_structured_output(SampleSchema)

    assert isinstance(result, dict)
    assert result["type"] == "json_schema"
    assert result["json_schema"]["name"] == "SampleSchema"
    assert "minLength" not in result["json_schema"]["schema"].get("properties", {}).get("name", {})


@pytest.mark.asyncio
async def test_ai_studio_real_get_redis_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify get_redis_client returns patched fakeredis pool in test environments."""
    import backend_v2.llm.adapters.ai_studio_adapter as ai_module

    monkeypatch.undo()

    client = await ai_module.get_redis_client()
    assert client is not None
    client2 = await ai_module.get_redis_client()
    assert client2 is client

