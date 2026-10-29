"""Unit tests for LiteLLMProvider initialization, request orchestration, and retry pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import httpx
import litellm
import litellm.exceptions as litellm_exc
import pytest
from pydantic import BaseModel, ConfigDict, Field

import backend_v2.llm.provider as provider_facade
import backend_v2.llm.provider.litellm_provider as litellm_provider_mod
from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes, ServiceUnavailableError
from backend_v2.llm.adapters.adapter_factory import LLMCacheAdapterFactory
from backend_v2.llm.adapters.base_adapter import apply_provider_pacing
from backend_v2.llm.provider.base_and_mock_provider import LogfireShieldedClient
from backend_v2.llm.provider.litellm_provider import (
    LiteLLMProvider,
    _resolve_apply_provider_pacing,
    _resolve_get_settings,
)
from backend_v2.models.domain.system_config import ProviderExtraParamsDTO
from backend_v2.models.llm import (
    LLMMessageDTO,
    LLMProviderConfig,
)
from backend_v2.settings import Settings, get_settings


class _ToolParamModel(BaseModel):
    """Pydantic model representing an MCP tool declaration with inputSchema alias."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, populate_by_name=True)

    name: str
    description: str
    input_schema: Any = Field(alias="inputSchema")


class _SimpleChoiceMsg:
    """Minimal message stub for router.acompletion response."""

    def __init__(self, content: str, tool_calls: Any = None) -> None:
        """Initialize choice message."""
        self.content = content
        self.tool_calls = tool_calls


class _SimpleChoice:
    """Minimal choice stub."""

    def __init__(self, content: str, tool_calls: Any = None) -> None:
        """Initialize choice."""
        self.message = _SimpleChoiceMsg(content=content, tool_calls=tool_calls)
        self.finish_reason = "stop"


class _SimpleUsage:
    """Minimal usage stub."""

    def __init__(self, prompt_tokens: int = 10, completion_tokens: int = 5) -> None:
        """Initialize usage counts."""
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = prompt_tokens + completion_tokens


class _SimpleResponse:
    """Minimal completion response stub."""

    def __init__(self, content: str = "generated-answer", tool_calls: Any = None) -> None:
        """Initialize completion response."""
        self.choices = [_SimpleChoice(content=content, tool_calls=tool_calls)]
        self.model = "openai/gpt-4o"
        self.usage = _SimpleUsage()
        self.system_fingerprint = "fp_123"


def test_litellm_provider_init_validates_limits_and_caches_router_and_semaphores(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifies that LiteLLMProvider.__init__ enforces strict TPM/RPM limits and caches semaphores."""
    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()

    # Phase 1, Step 1: Enforce hermetic Settings without legacy storage_backend override
    test_settings = Settings(
        semaphore_low_rpm_threshold=60,
        semaphore_low_rpm_limit=2,
        semaphore_max_concurrency=20,
        semaphore_rpm_divisor=10,
    )
    monkeypatch.setattr(litellm_provider_mod, "get_settings", lambda: test_settings)

    with pytest.raises(ConfigurationError, match="LLM Rate Limits"):
        LiteLLMProvider(model_name="openai/gpt-4o", limits=None)

    with pytest.raises(ConfigurationError, match="Both TPM and RPM"):
        LiteLLMProvider(model_name="openai/gpt-4o", limits={"tpm": 10000})

    low_rpm_provider = LiteLLMProvider(
        model_name="openai/gpt-4o-mini",
        api_key="test-env-injected-key",
        organization_id="org_0195f3a0000070018234567890abcdef",
        limits={"tpm": 50000, "rpm": 30},
    )
    assert low_rpm_provider.organization_id == "org_0195f3a0000070018234567890abcdef"
    assert LiteLLMProvider._semaphores[low_rpm_provider.cache_key]._value == 2

    # Second instantiation hits _router_cache and _semaphores cache
    cached_provider = LiteLLMProvider(
        model_name="openai/gpt-4o-mini",
        limits={"tpm": 50000, "rpm": 30},
    )
    assert cached_provider.router is low_rpm_provider.router
    assert cached_provider.organization_id == "UNKNOWN_ORG"

    high_rpm_provider = LiteLLMProvider(
        model_name="openai/gpt-4o",
        limits={"tpm": 500000, "rpm": 150},
    )
    assert LiteLLMProvider._semaphores[high_rpm_provider.cache_key]._value == 15


@pytest.mark.asyncio
async def test_lite_llm_provider_strips_internal_keys_and_normalizes_mcp_tools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifies that LiteLLMProvider.generate strips internal keys and normalizes MCP tool schemas."""
    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()

    monkeypatch.setattr(litellm, "completion_cost", lambda **_: 0.002)
    monkeypatch.setattr(provider_facade, "apply_provider_pacing", AsyncMock())
    monkeypatch.setenv("TEST_REGION_VAR", "europe-west1")

    cfg = LLMProviderConfig(
        id="cfg_0195f3a0000070018234567890abcdef",
        provider="openai",
        model_name="openai/gpt-4o",
        rpm_limit=120,
        tpm_limit=100000,
        additional_params=ProviderExtraParamsDTO(vertex_location="${TEST_REGION_VAR}"),
    )
    provider = LiteLLMProvider(
        model_name="openai/gpt-4o",
        api_key="test-key-from-env",
        limits={"tpm": 100000, "rpm": 120},
        config=cfg,
    )

    captured_kwargs: list[Any] = []

    async def _fake_acompletion(**call_params: Any) -> Any:
        captured_kwargs.append(call_params)
        return _SimpleResponse(content='{"answer": "normalized"}')

    monkeypatch.setattr(provider.router, "acompletion", _fake_acompletion)

    mcp_tool_dto = _ToolParamModel(
        name="query_kb",
        description="Query knowledge base",
        input_schema={
            "type": "object",
            "properties": {"q": {"type": "string", "enum_values": ["a", "b"]}},
            "additional_properties": False,
        },
    )

    res = await provider.generate(
        messages=[
            LLMMessageDTO(role="system", content="Dropped when cached_content present"),
            LLMMessageDTO(role="user", content="Find policy"),
        ],
        response_schema={"type": "json_schema", "json_schema": {"name": "PolicySchema"}},
        temperature=0.2,
        max_tokens=256,
        pass_reasoning_token="prev_thought_123",
        cached_content="projects/p/locations/l/cachedContents/c1",
        tools=[mcp_tool_dto],
        mock_identity="internal_mock_id",
        validation_context={"step_id": "stp_internal_strip"},
    )

    assert res.content == '{"answer": "normalized"}'
    assert len(captured_kwargs) == 1
    sent = captured_kwargs[0]

    # Internal keys in _INTERNAL_NON_API_KEYS stripped
    assert "mock_identity" not in sent
    assert "validation_context" not in sent

    # System message filtered due to cached_content, reasoning token appended
    sent_messages = sent["messages"]
    assert len(sent_messages) == 2
    assert sent_messages[0]["role"] == "user"
    assert "RESUME_THOUGHT_PROCESS" in sent_messages[1]["content"]

    # MCP tool normalized (enum_values -> enum, additional_properties -> additionalProperties)
    tool_schema = sent["tools"][0]["inputSchema"]
    assert tool_schema["properties"]["q"]["enum"] == ["a", "b"]
    assert "enum_values" not in tool_schema["properties"]["q"]
    assert tool_schema["additionalProperties"] is False
    assert "additional_properties" not in tool_schema
    assert sent["vertex_location"] == "europe-west1"


@pytest.mark.asyncio
async def test_litellm_provider_generate_full_telemetry_and_toolcalls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifies content/tool_calls extraction, TokenUsage, cost_usd, and OpenTelemetry GenAI attributes."""
    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()

    monkeypatch.setattr(litellm, "completion_cost", lambda **_: 0.0075)
    pacing_mock = AsyncMock()
    monkeypatch.setattr(litellm_provider_mod, "apply_provider_pacing", pacing_mock)

    mock_span = MagicMock()
    mock_span.is_recording.return_value = True
    mock_otel = MagicMock()
    mock_otel.get_current_span.return_value = mock_span
    monkeypatch.setattr(provider_facade, "otel_trace", mock_otel)

    provider = LiteLLMProvider(
        model_name="openai/gpt-4o",
        limits={"tpm": 100000, "rpm": 100},
    )

    tool_call_dict = {
        "id": "call_live_1",
        "type": "function",
        "function": {"name": "lookup_atom", "arguments": '{"atom_id": "a0"}'},
    }

    async def _fake_acompletion(**_: Any) -> Any:
        return _SimpleResponse(content="", tool_calls=[tool_call_dict])

    monkeypatch.setattr(provider.router, "acompletion", _fake_acompletion)

    result = await provider.generate(
        prompt="Evaluate atom a0",
        system_instruction="You are an auditor.",
        temperature=0.0,
        max_tokens=512,
    )

    assert result.content == '{"atom_id": "a0"}'
    assert result.tool_calls is not None
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].id == "call_live_1"
    assert result.tool_calls[0].function.name == "lookup_atom"
    assert result.token_usage.prompt_tokens == 10
    assert result.token_usage.completion_tokens == 5
    assert result.token_usage.cost_usd == pytest.approx(0.0075)
    pacing_mock.assert_awaited_once()
    mock_span.set_attribute.assert_any_call("gen_ai.response.model", "openai/gpt-4o")
    mock_span.set_attribute.assert_any_call("gen_ai.usage.input_tokens", 10)
    mock_span.set_attribute.assert_any_call("gen_ai.usage.output_tokens", 5)


@pytest.mark.asyncio
async def test_litellm_provider_generate_retries_httpx_shield_and_fail_fast_guards(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Verifies fail-fast parameter guards, DUMP_PROMPTS_FILE, HTTPX client wrapping, and retries."""
    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()
    LiteLLMProvider._httpx_clients.clear()

    # Phase 1, Step 1: Enforce hermetic Settings without legacy storage_backend override
    fast_settings = Settings(
        llm_max_transient_retries=1,
        llm_retry_jitter_initial_seconds=0,
        llm_retry_max_seconds=1,
        llm_retry_jitter_exp_base=1,
    )
    monkeypatch.setattr(provider_facade, "get_settings", lambda: fast_settings)
    monkeypatch.setattr(provider_facade, "apply_provider_pacing", AsyncMock())
    monkeypatch.setattr(litellm, "completion_cost", lambda **_: 0.001)

    cfg = LLMProviderConfig(
        id="cfg_0195f3a00000700a8bcdef1234567890",
        provider="openai",
        model_name="openai/gpt-4o",
        rpm_limit=100,
        tpm_limit=100000,
        additional_params=ProviderExtraParamsDTO(),
    )
    provider = LiteLLMProvider(
        model_name="openai/gpt-4o",
        limits={"tpm": 100000, "rpm": 100},
        config=cfg,
    )

    with pytest.raises(ConfigurationError, match="temperature"):
        await provider.generate(prompt="hi", temperature=None, max_tokens=100)

    with pytest.raises(ConfigurationError, match="max_tokens"):
        await provider.generate(prompt="hi", temperature=0.1, max_tokens=None)

    dump_target = tmp_path / "diag_prompts.txt"
    monkeypatch.setenv("DUMP_PROMPTS_FILE", str(dump_target))
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

    real_http_client = httpx.AsyncClient(timeout=30.0)
    fake_adapter = MagicMock()
    fake_adapter.sanitize_messages.side_effect = lambda msgs: msgs
    fake_adapter.prepare_kwargs.side_effect = lambda kw, *_: kw
    fake_adapter.build_http_client.return_value = real_http_client
    monkeypatch.setattr(LLMCacheAdapterFactory, "get_adapter", lambda *_, **__: fake_adapter)

    attempts = 0
    seen_clients: list[Any] = []

    async def _flaky_acompletion(**call_params: Any) -> Any:
        nonlocal attempts
        attempts += 1
        if "client" in call_params:
            seen_clients.append(call_params["client"])
        if attempts == 1:
            raise litellm_exc.RateLimitError(
                message="Rate limit Retry-After: 0.01",
                llm_provider="openai",
                model="gpt-4o",
            )
        return _SimpleResponse(content="recovered-on-retry")

    monkeypatch.setattr(provider.router, "acompletion", _flaky_acompletion)

    try:
        res = await provider.generate(
            prompt="test retry",
            temperature=0.0,
            max_tokens=64,
            timeout=30,
        )
        assert res.content == "recovered-on-retry"
        assert attempts == 2
        assert len(seen_clients) == 2
        assert isinstance(seen_clients[0], LogfireShieldedClient)
        assert dump_target.exists()
    finally:
        await real_http_client.aclose()

    # Exhausting retries routes through classify_and_raise_litellm_error
    async def _always_rate_limited(**_: Any) -> Any:
        raise litellm_exc.RateLimitError(
            message="Resource exhausted permanently",
            llm_provider="openai",
            model="gpt-4o",
        )

    monkeypatch.setattr(provider.router, "acompletion", _always_rate_limited)
    with pytest.raises(ServiceUnavailableError, match="rate limit exceeded"):
        await provider.generate(prompt="fail", temperature=0.0, max_tokens=64)


@pytest.mark.asyncio
async def test_litellm_provider_negative_boundaries_and_rfc7807_logging(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verifies negative boundaries for schema resolution, dump failures, adapter absence, and RFC 7807 logging."""
    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()

    monkeypatch.delitem(litellm_provider_mod.sys.modules, "backend_v2.llm.provider", raising=False)
    assert _resolve_get_settings() is get_settings
    assert _resolve_apply_provider_pacing() is apply_provider_pacing

    monkeypatch.setattr(litellm, "completion_cost", lambda **_: 0.001)
    monkeypatch.setattr(litellm_provider_mod, "apply_provider_pacing", AsyncMock())

    with caplog.at_level("ERROR"), pytest.raises(ConfigurationError, match="LLM Rate Limits"):
        LiteLLMProvider(model_name="openai/gpt-4o", limits=None)
    assert ErrorCodes.CONFIGURATION_ERROR.name in caplog.text

    def _raise_adapter_err(*_: Any, **__: Any) -> Any:
        raise AppException(
            message="Adapter missing",
            status_code=400,
            details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
        )

    monkeypatch.setattr(LLMCacheAdapterFactory, "get_adapter", _raise_adapter_err)

    cfg = LLMProviderConfig(
        id="cfg_0195f3a00000700a8bcdef1234567891",
        provider="openai",
        model_name="openai/gpt-4o",
        rpm_limit=100,
        tpm_limit=100000,
        additional_params=ProviderExtraParamsDTO(),
    )
    provider = LiteLLMProvider(
        model_name="openai/gpt-4o",
        limits={"tpm": 100000, "rpm": 100},
        config=cfg,
    )
    monkeypatch.setattr(provider.router, "acompletion", AsyncMock(return_value=_SimpleResponse(content="ok")))

    # Messages without cached_content + BaseModel response_schema class
    res = await provider.generate(
        messages=[LLMMessageDTO(role="user", content="Hello without cache")],
        response_schema=_ToolParamModel,
        temperature=0.0,
        max_tokens=32,
    )
    assert res.content == "ok"

    # Malformed response_schema object raising error during name resolution
    class _BadName:
        def __bool__(self) -> bool:
            return True

        def __str__(self) -> str:
            raise RuntimeError("corrupted schema name")

    broken_schema = {"json_schema": {"name": _BadName()}}
    caplog.clear()
    with caplog.at_level("ERROR"), pytest.raises(ConfigurationError, match="Schema resolution failed"):
        await provider.generate(
            prompt="test",
            response_schema=broken_schema,
            temperature=0.0,
            max_tokens=32,
        )
    assert ErrorCodes.CONFIGURATION_ERROR.name in caplog.text

    # Diagnostic dump failure raises ConfigurationError with RFC 7807 logging
    monkeypatch.setenv("DUMP_PROMPTS_FILE", "invalid_path.txt")

    def _fail_dump(*_: Any) -> None:
        raise OSError("disk full")

    monkeypatch.setattr(litellm_provider_mod, "_sync_diagnostic_dump", _fail_dump)
    caplog.clear()
    with caplog.at_level("ERROR"), pytest.raises(ConfigurationError, match="Diagnostic dump dispatch failed"):
        await provider.generate(
            prompt="test dump error",
            temperature=0.0,
            max_tokens=32,
        )
    assert ErrorCodes.CONFIGURATION_ERROR.name in caplog.text
