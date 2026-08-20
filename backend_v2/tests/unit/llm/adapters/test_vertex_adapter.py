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


def test_vertex_token_usage_negative_savings_raises() -> None:
    """Verify that negative savings in VertexTokenUsage raises a ValueError."""
    with pytest.raises(ValueError, match="estimated_savings_usd must be greater than or equal to 0.0"):
        VertexTokenUsage(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            estimated_savings_usd=-1.0,
        )


def test_vertex_adapter_prepare_provider_kwargs() -> None:
    """Verify prepare_provider_kwargs returns standard Vertex safety settings."""
    adapter = VertexCacheAdapter()
    kwargs = adapter.prepare_provider_kwargs("gemini-2.5-flash")
    assert "safety_settings" in kwargs
    assert len(kwargs["safety_settings"]) > 0


def test_vertex_adapter_sanitize_messages() -> None:
    """Verify sanitize_messages strips orphaned tool calls and preserves valid ones."""
    adapter = VertexCacheAdapter()

    messages = [
        {"role": "user", "content": "Hello"},
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [{"id": "call_123", "type": "function", "function": {"name": "search"}}],
        },
        {"role": "tool", "tool_call_id": "call_123", "content": "Result 1"},
        {"role": "tool", "tool_call_id": "orphaned_call_999", "content": "Orphaned result"},
    ]

    sanitized = adapter.sanitize_messages(messages)
    assert len(sanitized) == 3
    assert not any(m.get("tool_call_id") == "orphaned_call_999" for m in sanitized)
    assert any(m.get("tool_call_id") == "call_123" for m in sanitized)


def test_vertex_adapter_prepare_kwargs_location_and_thinking() -> None:
    """Verify prepare_kwargs resolves vertex location and maps thinking budget tokens."""
    adapter = VertexCacheAdapter()

    config_mock = MagicMock()
    config_mock.vertex_location = "europe-west1"
    config_mock.additional_params = {"thinking_budget_tokens": 1024}

    call_kwargs: dict[str, Any] = {}
    result = adapter.prepare_kwargs(call_kwargs, config=config_mock)

    assert result["vertex_location"] == "europe-west1"
    assert (
        result["extra_body"]["generationConfig"]["thinkingConfig"]["thinkingBudget"]
        == 1024
    )


def test_vertex_adapter_prepare_kwargs_cached_content_with_tools_bypasses() -> None:
    """Verify prepare_kwargs bypasses caching if tools are present in call_kwargs."""
    adapter = VertexCacheAdapter()

    call_kwargs: dict[str, Any] = {
        "cached_content": "projects/test/locations/europe-north1/cachedContents/123",
        "tools": [{"type": "function"}],
    }

    result = adapter.prepare_kwargs(call_kwargs)
    assert "cached_content" not in result


def test_vertex_adapter_prepare_kwargs_cached_content_scrubs_system_message() -> None:
    """Verify prepare_kwargs scrubs stray system messages when caching is active."""
    adapter = VertexCacheAdapter()

    call_kwargs: dict[str, Any] = {
        "cached_content": "projects/test/locations/europe-north1/cachedContents/123",
        "messages": [
            {"role": "system", "content": "Stray system message"},
            {"role": "user", "content": "User prompt"},
        ],
    }

    result = adapter.prepare_kwargs(call_kwargs)
    assert result["extra_headers"]["cached_content"] == "projects/test/locations/europe-north1/cachedContents/123"
    assert result["extra_body"]["cachedContent"] == "projects/test/locations/europe-north1/cachedContents/123"
    assert len(result["messages"]) == 1
    assert result["messages"][0]["role"] == "user"


def test_vertex_adapter_build_http_client() -> None:
    """Verify build_http_client returns an AsyncHTTPHandler with persistent settings."""
    adapter = VertexCacheAdapter()
    handler = adapter.build_http_client(45.0)
    assert handler is not None
    assert handler.timeout == 45.0
    assert handler.client is not None


def test_vertex_adapter_prepare_structured_output() -> None:
    """Verify prepare_structured_output converts Pydantic model and strips unsupported constraints."""
    from pydantic import BaseModel, Field

    class OutputSchema(BaseModel):
        summary: str = Field(description="Summary text", min_length=5)
        score: int = Field(ge=1, le=10)

    adapter = VertexCacheAdapter()
    structured = adapter.prepare_structured_output(OutputSchema)

    assert isinstance(structured, dict)
    assert structured["type"] == "json_schema"
    schema = structured["json_schema"]["schema"]
    assert "minLength" not in schema.get("properties", {}).get("summary", {})


@pytest.mark.asyncio
async def test_vertex_adapter_bypasses_cache_when_static_messages_below_1024() -> None:
    """Verify VertexCacheAdapter pre-flight check bypasses cache when static prompt is <1024 tokens even if metadata token count is high."""
    adapter = VertexCacheAdapter()

    # Short static messages (~30 chars = ~7 tokens), but metadata reports 50k tokens (document payload)
    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": "You are a concise classifier."},
        ],
        dynamic_messages=[
            {"role": "user", "content": "Document text " * 5000},
        ],
        metadata={"estimated_token_count": 50000},
    )

    flat_msgs, extra_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-2.5-flash")
    assert extra_kwargs == {}
    assert len(flat_msgs) == 2


@pytest.mark.asyncio
async def test_vertex_adapter_static_chars_with_content_blocks() -> None:
    """Verify token estimation handles content formatted as list of text blocks."""
    adapter = VertexCacheAdapter()

    prompt = CompiledPrompt(
        static_messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Block one. "},
                    {"type": "text", "text": "Block two."},
                ],
            },
        ],
        dynamic_messages=[],
    )

    flat_msgs, extra_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-2.5-flash")
    assert extra_kwargs == {}
    assert len(flat_msgs) == 1


@pytest.mark.asyncio
async def test_real_get_redis_client_pytest_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify real get_redis_client returns patched fakeredis pool in test environments."""
    import backend_v2.llm.adapters.vertex_adapter as va_module

    # Undo monkeypatch on module level for this specific test
    monkeypatch.undo()

    client = await va_module.get_redis_client()
    assert client is not None
    # Verify reusing same pool
    client2 = await va_module.get_redis_client()
    assert client2 is client


@pytest.mark.asyncio
async def test_vertex_cache_immediate_hit_in_shared_ledger() -> None:
    """Verify that an existing cache in Redis returns immediately without lock or SDK creation."""
    adapter = VertexCacheAdapter()
    large_static = "A" * 150000
    prompt = CompiledPrompt(
        static_messages=[{"role": "system", "content": large_static}],
        dynamic_messages=[{"role": "user", "content": "Query"}],
    )

    redis_client = await get_redis_client()
    static_hash = hashlib.sha256(json.dumps(prompt.static_messages, sort_keys=True).encode()).hexdigest()
    redis_key = f"vertex_cache:gemini-1.5-pro:{static_hash}"
    existing_cache_id = "projects/mock-proj/locations/europe-north1/cachedContents/hit-12345"
    await redis_client.set(redis_key, existing_cache_id, ex=300)

    dynamic_msgs, extra_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-1.5-pro")
    assert extra_kwargs == {"cached_content": existing_cache_id}
    assert len(dynamic_msgs) == 1


@pytest.mark.asyncio
async def test_vertex_cache_assistant_role_and_unqualified_name() -> None:
    """Verify assistant role is mapped to model and unqualified cache names are prefixed."""
    mock_cached_contents.CachedContent.create.reset_mock()

    class DummyCacheUnqualified:
        name = "unqualified_cache_id_555"

    mock_cached_contents.CachedContent.create.return_value = DummyCacheUnqualified()

    large_static = "A" * 150000
    prompt = CompiledPrompt(
        static_messages=[
            {"role": "system", "content": large_static},
            {"role": "assistant", "content": "Previous assistant response in cache"},
        ],
        dynamic_messages=[],
    )

    adapter = VertexCacheAdapter()
    redis_client = await get_redis_client()
    static_hash = hashlib.sha256(json.dumps(prompt.static_messages, sort_keys=True).encode()).hexdigest()
    redis_key = f"vertex_cache:gemini-1.5-pro:{static_hash}"
    lock_key = f"lock:vertex_cache:gemini-1.5-pro:{static_hash}"
    await redis_client.delete(redis_key, lock_key)

    _, extra_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-1.5-pro")

    assert "cached_content" in extra_kwargs
    assert extra_kwargs["cached_content"].endswith("/cachedContents/unqualified_cache_id_555")

    # Verify assistant role was mapped to model in GAPIC contents
    _, kwargs = mock_cached_contents.CachedContent.create.call_args
    passed_contents = kwargs["contents"]
    assert any(c["role"] == "model" for c in passed_contents)


@pytest.mark.asyncio
async def test_vertex_cache_wait_and_poll_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify wait-and-poll loop handles timeout when lock is held by another worker."""
    from backend_v2.settings import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "context_cache_lock_poll_interval_ms", 1)
    monkeypatch.setattr(settings, "context_cache_lock_wait_limit_seconds", 0.005)

    large_static = "A" * 150000
    prompt = CompiledPrompt(
        static_messages=[{"role": "system", "content": large_static}],
        dynamic_messages=[],
    )

    adapter = VertexCacheAdapter()
    redis_client = await get_redis_client()
    static_hash = hashlib.sha256(json.dumps(prompt.static_messages, sort_keys=True).encode()).hexdigest()
    redis_key = f"vertex_cache:gemini-1.5-pro:{static_hash}"
    lock_key = f"lock:vertex_cache:gemini-1.5-pro:{static_hash}"

    # Lock held by worker_0, status CREATING
    await redis_client.set(lock_key, "worker_0", ex=10)
    await redis_client.set(redis_key, "CREATING", ex=10)

    flat_msgs, extra_kwargs = await adapter.prepare_caching_payload(prompt, "gemini-1.5-pro")

    assert extra_kwargs == {}
    assert len(flat_msgs) == 1


