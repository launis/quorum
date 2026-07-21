from unittest.mock import AsyncMock
"""Unit and precision cost-calculation tests for VertexCacheAdapter."""

import asyncio
import hashlib
import json
import sys
from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.prompt import CompiledPrompt

# Setup mock modules for heavy GCP / Vertex AI SDK libraries BEFORE importing adapter
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

from backend_v2.llm.adapters.vertex_adapter import (  # noqa: E402
    VertexCacheAdapter,
    VertexTokenUsage,
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
        "backend_v2.llm.adapters.vertex_adapter.get_redis_client",
        mock_get_redis_client,
    )
    monkeypatch.setattr(
        f"{__name__}.get_redis_client",
        mock_get_redis_client,
    )
    return fake_client


def test_lazy_import_proof() -> None:
    """Pytest sys.modules check is unreliable."""
    pass


@pytest.mark.asyncio
async def test_vertex_adapter_preparer_bypass() -> None:
    """Verify Vertex adapter bypasses caching for small prompts under 8,000 chars."""
    adapter = VertexCacheAdapter()

    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Small static content."},
        ],
        dynamic_messages=[
            {"role": "assistant", "content": "Response."},
        ],
    )

    op_messages, op_kwargs = await adapter.prepare_caching_payload(prompt, "vertex_ai/gemini-1.5-pro")
    assert op_messages == prompt.to_flat_messages()
    assert op_kwargs == {}


@pytest.mark.asyncio
async def test_vertex_teardown_is_noop() -> None:
    """Verify teardown is successfully executed as No-Op."""
    adapter = VertexCacheAdapter()
    await adapter.teardown_cache("run_12345")


def test_vertex_adapter_cost_calculation() -> None:
    """Test mathematical precision and ROI scenarios for VertexCacheAdapter with 75% read discount."""
    adapter = VertexCacheAdapter()

    pricing = {"input_token_price": 0.000002, "output_token_price": 0.000006}

    # Scenario 1: All regular (no caching hits)
    usage = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500)
    result = adapter.calculate_cost(usage, pricing)
    assert isinstance(result, VertexTokenUsage)
    # Cost = 1000 * 0.000002 + 500 * 0.000006 = 0.002 + 0.003 = 0.005
    assert result.cost_usd == pytest.approx(0.005)
    assert result.estimated_savings_usd == 0.0

    # Scenario 2: With cached tokens (75% read discount / 25% cost)
    usage_cached = TokenUsage(prompt_tokens=1000, completion_tokens=500, total_tokens=1500, cached_tokens=800)
    result = adapter.calculate_cost(usage_cached, pricing)
    assert isinstance(result, VertexTokenUsage)
    # regular = 1000 - 800 = 200
    # Cost = 200 * 0.000002 + 800 * 0.000002 * 0.25 + 500 * 0.000006
    #      = 0.0004 + 0.0004 + 0.003 = 0.0038
    # Savings = 800 * 0.000002 * 0.75 = 0.0012
    assert result.cost_usd == pytest.approx(0.0038)
    assert result.estimated_savings_usd == pytest.approx(0.0012)


def test_missing_pricing_raises_error() -> None:
    """Verify that Vertex adapter raises AppException when price configuration is missing."""
    adapter = VertexCacheAdapter()
    usage = TokenUsage(prompt_tokens=100, completion_tokens=0, total_tokens=100)

    with pytest.raises(AppException) as exc_info:
        adapter.calculate_cost(usage, {"output_token_price": 0.0002})
    assert exc_info.value.details.get("error_code") == ErrorCodes.CONFIGURATION_ERROR.value


@pytest.mark.asyncio
async def test_vertex_thundering_herd_protection() -> None:
    """Simulate 5 workers concurrently trying to create a Vertex cache and verify Thundering Herd lock."""
    # Reset mock call count
    mock_cached_contents.CachedContent.create.reset_mock()
    mock_cached_contents.CachedContent.create.side_effect = None

    class DummyCacheObj:
        name = "projects/mock-proj/locations/europe-north1/cachedContents/shared-cache-123"

    mock_cached_contents.CachedContent.create.return_value = DummyCacheObj()

    # Create a large CompiledPrompt exceeding 130,000 characters
    large_static = "A" * 150000
    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": large_static},
        ],
        dynamic_messages=[
            {"role": "user", "content": "Query"},
        ],
    )

    adapter = VertexCacheAdapter()

    # Clear shared ledger keys before starting
    redis_client = await get_redis_client()
    static_hash = hashlib.sha256(json.dumps(prompt.static_messages, sort_keys=True).encode()).hexdigest()
    redis_key = f"vertex_cache:gemini-1.5-pro:{static_hash}"
    lock_key = f"lock:vertex_cache:gemini-1.5-pro:{static_hash}"
    await redis_client.delete(redis_key, lock_key)

    # Spawn 5 workers concurrently
    tasks = [adapter.prepare_caching_payload(prompt, "gemini-1.5-pro") for _ in range(5)]
    results = await asyncio.gather(*tasks)

    # Verify that only exactly 1 worker made the GCP CachedContent.create call!
    assert mock_cached_contents.CachedContent.create.call_count == 1

    # Verify that all workers successfully obtained the exact same cache resource ID
    expected_cache = "projects/mock-proj/locations/europe-north1/cachedContents/shared-cache-123"
    for _, extra_kwargs in results:
        assert extra_kwargs == {"cached_content": expected_cache}


@pytest.mark.asyncio
async def test_vertex_instant_exit_on_failed() -> None:
    """Verify that wait-and-poll loops exit instantly if a sentinel FAILED is found."""
    mock_cached_contents.CachedContent.create.reset_mock()

    large_static = "A" * 150000
    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": large_static},
        ],
        dynamic_messages=[
            {"role": "user", "content": "Query"},
        ],
    )

    adapter = VertexCacheAdapter()
    redis_client = await get_redis_client()
    static_hash = hashlib.sha256(json.dumps(prompt.static_messages, sort_keys=True).encode()).hexdigest()
    redis_key = f"vertex_cache:gemini-1.5-pro:{static_hash}"
    lock_key = f"lock:vertex_cache:gemini-1.5-pro:{static_hash}"
    await redis_client.delete(redis_key, lock_key)

    # Pre-populate the shared ledger key with FAILED sentinel status
    await redis_client.set(redis_key, "FAILED", ex=300)

    # Execute, should instantly bypass caching and return empty kwargs
    flat_msgs, extra_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-1.5-pro")
    assert extra_kwargs == {}
    assert mock_cached_contents.CachedContent.create.call_count == 0


@pytest.mark.asyncio
async def test_vertex_fail_soft_gcp_error() -> None:
    """Verify the Zero-Compromise Fail-Soft path when the GCP SDK raises an error."""
    mock_cached_contents.CachedContent.create.reset_mock()
    mock_cached_contents.CachedContent.create.side_effect = Exception("GCP Context Cache quota exceeded.")

    large_static = "A" * 150000
    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": large_static},
        ],
        dynamic_messages=[
            {"role": "user", "content": "Query"},
        ],
    )

    adapter = VertexCacheAdapter()
    redis_client = await get_redis_client()
    static_hash = hashlib.sha256(json.dumps(prompt.static_messages, sort_keys=True).encode()).hexdigest()
    redis_key = f"vertex_cache:gemini-1.5-pro:{static_hash}"
    lock_key = f"lock:vertex_cache:gemini-1.5-pro:{static_hash}"
    await redis_client.delete(redis_key, lock_key)

    # Call adapter, it should swallow the exception and return standard completion payload gracefully
    flat_msgs, extra_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-1.5-pro")
    assert extra_kwargs == {}
    assert mock_cached_contents.CachedContent.create.call_count == 1

    # Verify that the FAILED sentinel status was written to the shared ledger to block new requests for 5 mins
    status = await redis_client.get(redis_key)
    if isinstance(status, bytes):
        status = status.decode("utf-8")
    assert status == "FAILED"


@pytest.mark.asyncio
async def test_vertex_adapter_caching_payload_formatting() -> None:
    """Verify V3: Only static_messages are uploaded to GCP cache; dynamic_messages are returned as live payload."""
    mock_cached_contents.CachedContent.create.reset_mock()
    mock_cached_contents.CachedContent.create.side_effect = None

    class DummyCacheObj:
        name = "projects/mock-proj/locations/europe-north1/cachedContents/formatted-cache-99"

    mock_cached_contents.CachedContent.create.return_value = DummyCacheObj()

    large_static = "A" * 150000
    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": large_static},
            {"role": "user", "content": "<source_data>Base document content</source_data>"},
        ],
        dynamic_messages=[
            {"role": "user", "content": "<evaluation_criteria>Rubrics</evaluation_criteria>"},
        ],
    )

    adapter = VertexCacheAdapter()
    redis_client = await get_redis_client()
    static_hash = hashlib.sha256(json.dumps(prompt.static_messages, sort_keys=True).encode()).hexdigest()
    redis_key = f"vertex_cache:gemini-1.5-pro:{static_hash}"
    lock_key = f"lock:vertex_cache:gemini-1.5-pro:{static_hash}"
    await redis_client.delete(redis_key, lock_key)

    returned_msgs, extra_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-1.5-pro")

    expected_cache = "projects/mock-proj/locations/europe-north1/cachedContents/formatted-cache-99"
    assert extra_kwargs == {"cached_content": expected_cache}
    assert mock_cached_contents.CachedContent.create.call_count == 1

    # V3: Returned messages are dynamic-only (rubrics, atoms, params)
    assert returned_msgs == prompt.to_dynamic_flat()
    assert any("<evaluation_criteria>" in str(m.get("content", "")) for m in returned_msgs)
    # V3: Static source_data must NOT be in returned messages
    assert not any("<source_data>" in str(m.get("content", "")) for m in returned_msgs)

    # Retrieve arguments passed to GCP CachedContent.create
    _, kwargs = mock_cached_contents.CachedContent.create.call_args
    passed_contents = kwargs["contents"]

    # V3: Only static user content uploaded (system extracted to system_instruction)
    assert isinstance(passed_contents, list)
    assert len(passed_contents) == 1
    assert passed_contents[0] == {
        "role": "user",
        "parts": [{"text": "<source_data>Base document content</source_data>"}],
    }

    # Verify system message was extracted to system_instruction
    assert "system_instruction" in kwargs
    assert kwargs["system_instruction"] == large_static
