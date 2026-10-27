"""Unit tests for backend_v2.llm.provider package facade and migrated LiteLLMProvider test cases."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import litellm
import pytest
from opentelemetry.trace import SpanContext, TraceFlags
from pydantic import BaseModel, ConfigDict

import backend_v2.llm.provider as provider_facade
from backend_v2.exceptions import (
    AgentExecutionError,
    AppException,
    ConfigurationError,
    SecurityViolationError,
    ServiceUnavailableError,
)
from backend_v2.llm.provider import (
    LiteLLMProvider,
    LLMFactory,
    LLMProvider,
    LogfireShieldedClient,
    MockProvider,
    _AdaptiveWaitWithRetryAfter,
    _extract_retry_after_seconds,
    _format_attempt_error,
    _INTERNAL_NON_API_KEYS,
    _is_transient_llm_error,
    _normalize_mcp_tool_schema_for_llm,
    _RETRY_AFTER_REGEX,
    _safe_static_getattr,
    _safe_static_hasattr,
    _sync_diagnostic_dump,
    _truncate_for_debug,
    apply_provider_pacing,
    classify_and_raise_litellm_error,
    extract_litellm_content_and_usage,
    get_settings,
    otel_trace,
    resolve_env_variables,
)
from backend_v2.models.domain.mcp import OpenAIToolCallDTO
from backend_v2.models.domain.system_config import ProviderExtraParamsDTO
from backend_v2.models.llm import LLMMessageDTO, LLMProviderConfig


class _DummyPydanticSchema(BaseModel):
    """Strict Pydantic schema for structured output resolution tests."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    response_value: str


class _StatusError(Exception):
    """Typed helper exception carrying an optional HTTP status_code."""

    def __init__(self, msg: str, status_code: int | None = None) -> None:
        """Initialize helper exception with message and optional status_code.

        Args:
            msg: Error message string.
            status_code: Optional HTTP status code.
        """
        super().__init__(msg)
        self.status_code = status_code


class _MockMessage:
    content = "test response"
    tool_calls: list[Any] = []


class _MockChoice:
    message = _MockMessage()
    finish_reason = "stop"


class _MockUsage:
    prompt_tokens = 10
    completion_tokens = 5
    total_tokens = 15


class _MockLiteLLMResponse:
    choices = [_MockChoice()]
    model_extra: Any = {}
    usage = _MockUsage()

    def model_dump(self) -> Any:
        return {}


# Phase 4, Step 1: Test Contract 1 — Verify package facade re-exports all public and internal symbols
def test_provider_package_facade_reexports_all_symbols() -> None:
    """Verifies that importing symbols from backend_v2.llm.provider works identically via the package facade."""
    expected_symbols = (
        LiteLLMProvider,
        MockProvider,
        LLMFactory,
        LLMProvider,
        LogfireShieldedClient,
        _AdaptiveWaitWithRetryAfter,
        _INTERNAL_NON_API_KEYS,
        _RETRY_AFTER_REGEX,
        _extract_retry_after_seconds,
        _format_attempt_error,
        _is_transient_llm_error,
        _normalize_mcp_tool_schema_for_llm,
        _safe_static_getattr,
        _safe_static_hasattr,
        _sync_diagnostic_dump,
        _truncate_for_debug,
        apply_provider_pacing,
        classify_and_raise_litellm_error,
        extract_litellm_content_and_usage,
        get_settings,
        otel_trace,
        resolve_env_variables,
    )
    for sym in expected_symbols:
        assert sym is not None
    assert len(provider_facade.__all__) == 23


@pytest.mark.asyncio
async def test_lite_llm_provider_top_k_top_p() -> None:
    """Test LiteLLMProvider receives top_k and top_p in generate call."""
    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-pro",
        api_key="secret",
        limits={"tpm": 100, "rpm": 10},
    )
    provider.router.acompletion = AsyncMock(return_value=_MockLiteLLMResponse())
    assert provider.model_name == "vertex_ai/gemini-pro"


@pytest.mark.asyncio
async def test_lite_llm_provider_additional_params(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test LiteLLMProvider correctly resolves and uses additional_params in call_kwargs."""
    monkeypatch.setenv("TEST_REGION_VAR", "europe-west3")
    monkeypatch.setattr(litellm, "completion_cost", lambda *args, **kwargs: 0.002)
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())

    config = LLMProviderConfig(
        id="prv_test1234",
        provider="litellm",
        model_name="vertex_ai/gemini-1.5-pro",
        api_key="secret",
        tpm_limit=100,
        rpm_limit=10,
        temperature=0.7,
        additional_params=ProviderExtraParamsDTO(top_p=0.85),
    )

    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-1.5-pro",
        api_key="secret",
        settings=get_settings(),
        limits={"tpm": 100, "rpm": 10},
        config=config,
    )
    assert provider._config == config
    provider.router.acompletion = AsyncMock(return_value=_MockLiteLLMResponse())

    await provider.generate(prompt="Hello", temperature=0.7, max_tokens=100)
    called_kwargs = provider.router.acompletion.call_args[1]
    assert called_kwargs["top_p"] == 0.85


@pytest.mark.asyncio
async def test_lite_llm_provider_model_info_id_registration(caplog: pytest.LogCaptureFixture) -> None:
    """Verify that LiteLLMProvider populates model_info.id and generate() does not trigger register_model warnings."""
    LiteLLMProvider._router_cache.clear()
    mock_usage_service = MagicMock()
    mock_usage_service.track_usage = AsyncMock()

    with caplog.at_level(logging.WARNING):
        provider = LiteLLMProvider(
            model_name="vertex_ai/gemini-2.5-flash",
            api_key=None,
            limits={"tpm": 100, "rpm": 10},
            settings=get_settings(),
            usage_service=mock_usage_service,
        )
        deployment = provider.router.model_list[0]
        assert "model_info" in deployment
        assert deployment["model_info"]["id"] == "vertex_ai/gemini-2.5-flash"
        assert "not in built-in cost map" not in caplog.text

        mock_usage = MagicMock(
            prompt_tokens=10,
            completion_tokens=5,
            total_tokens=15,
            prompt_tokens_details=MagicMock(cached_tokens=0),
            completion_tokens_details=MagicMock(reasoning_tokens=0),
        )
        mock_response = MagicMock(
            choices=[
                MagicMock(message=MagicMock(content="Hello response", tool_calls=None, provider_specific_fields=None))
            ],
            usage=mock_usage,
            system_fingerprint="fp_123",
            _hidden_params={},
            model_extra={},
        )
        mock_response.model_dump.return_value = {}
        provider.router.acompletion = AsyncMock(return_value=mock_response)
        await provider.generate(
            prompt="Hello",
            temperature=0.0,
            max_tokens=100,
            top_p=0.0,
            top_k=1,
            frequency_penalty=0.0,
            presence_penalty=0.0,
        )
    assert "not in built-in cost map" not in caplog.text


@pytest.mark.asyncio
async def test_fallback_snapshot_normalization(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that date-pinned snapshots from the same family do NOT trigger fallback logging, while real fallbacks do."""
    monkeypatch.setattr(litellm, "completion_cost", lambda *args, **kwargs: 0.002)
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())

    provider = LiteLLMProvider(
        model_name="openai/gpt-5.4",
        api_key="secret",
        settings=get_settings(),
        limits={"tpm": 100, "rpm": 10},
    )

    class _SnapResponse:
        choices = [_MockChoice()]
        usage = _MockUsage()
        model = "gpt-5.4-2026-03-05"

    provider.router.acompletion = AsyncMock(return_value=_SnapResponse())
    with caplog.at_level(logging.INFO):
        await provider.generate("hello", temperature=0.0, max_tokens=10)
    assert "LLM Fallback utilized" not in caplog.text

    caplog.clear()
    _SnapResponse.model = "gpt-3.5-turbo"
    with caplog.at_level(logging.INFO):
        await provider.generate("hello", temperature=0.0, max_tokens=10)
    assert "LLM Fallback utilized" in caplog.text


@pytest.mark.asyncio
async def test_litellm_provider_error_handling_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    """ISTQB Negative Tests: Verify error mapping for all upstream exceptions in LiteLLMProvider."""
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())
    provider = LiteLLMProvider(
        model_name="openai/gpt-5.4",
        api_key="secret",
        settings=get_settings(),
        limits={"tpm": 100, "rpm": 10},
    )

    class MockInstructorRetryException(Exception):
        pass

    provider.router.acompletion = AsyncMock(side_effect=MockInstructorRetryException("parsing failed"))
    with pytest.raises(AppException) as exc_info:
        await provider.generate("hello", temperature=0.0, max_tokens=10)
    assert exc_info.value.status_code == 500

    for status_code, msg, expected_exc in (
        (401, "invalid_api_key", ConfigurationError),
        (400, "context_length_exceeded token limit", AgentExecutionError),
        (400, "bad format", AgentExecutionError),
        (503, "gateway timeout", ServiceUnavailableError),
        (None, "ContentPolicyViolation: text blocked", SecurityViolationError),
        (None, "Something completely unexpected", ServiceUnavailableError),
    ):
        err = _StatusError(msg, status_code=status_code)
        provider.router.acompletion = AsyncMock(side_effect=err)
        with pytest.raises(expected_exc):
            await provider.generate("hello", temperature=0.0, max_tokens=10)


def test_litellm_provider_init_and_cache() -> None:
    """Test LiteLLMProvider initialization limit checks and router caching."""
    with pytest.raises(ConfigurationError):
        LiteLLMProvider(model_name="openai/gpt-4o", limits=None)
    with pytest.raises(ConfigurationError):
        LiteLLMProvider(model_name="openai/gpt-4o", limits={"rpm": 100})
    with pytest.raises(ConfigurationError):
        LiteLLMProvider(model_name="openai/gpt-4o", limits={"tpm": 100})

    p1 = LiteLLMProvider(model_name="openai/gpt-4o", organization_id="org_test123", limits={"tpm": 500, "rpm": 50})
    p2 = LiteLLMProvider(model_name="openai/gpt-4o", organization_id="org_test123", limits={"tpm": 500, "rpm": 50})
    assert p1.router is p2.router


@pytest.mark.asyncio
async def test_litellm_provider_generate_full_telemetry(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Verify LiteLLMProvider telemetry, tool extraction, reasoning, and quota warnings."""
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())
    monkeypatch.setattr(litellm, "completion_cost", lambda *args, **kwargs: 0.005)
    monkeypatch.setenv("DUMP_PROMPTS_FILE", str(tmp_path / "litellm_dump.txt"))

    usage_service = AsyncMock()
    provider = LiteLLMProvider(
        model_name="openai/gpt-5.4",
        api_key="secret",
        settings=get_settings(),
        usage_service=usage_service,
        limits={"tpm": 100, "rpm": 10},
    )

    class _FullUsage:
        prompt_tokens = 50
        completion_tokens = 25
        total_tokens = None
        prompt_tokens_details = MagicMock(cached_tokens=40)
        completion_tokens_details = MagicMock(reasoning_tokens=15)

    class _FullChoice:
        message = MagicMock(
            content="",
            tool_calls=[MagicMock(id="call_abc123", function=MagicMock(name="search_tool", arguments='{"q": "test"}'))],
            provider_specific_fields={"thought_signature": "sig_999"},
        )
        finish_reason = "length"

    class _FullResponse:
        choices = [_FullChoice()]
        usage = _FullUsage()
        system_fingerprint = "fp_123"
        model = "gpt-5.4"
        model_extra = {
            "safety_ratings": [{"category": "HARM", "probability": "LOW"}],
            "grounding_metadata": {"grounding_chunks": [{"web": {"uri": "https://grounding.example.com"}}]},
        }
        _hidden_params = {"headers": {"x-ratelimit-remaining-requests": "3"}}

        def model_dump(self) -> Any:
            return {"raw": "data"}

    provider.router.acompletion = AsyncMock(return_value=_FullResponse())
    res = await provider.generate(
        prompt="Execute task",
        system_instruction="Be precise",
        temperature=0.7,
        max_tokens=200,
        pass_reasoning_token="resume_blob_001",
        cached_content="cache_ref_token",
        mock_identity="test_id",
        validation_context={"env": "unit_test"},
        organization_id="org_override",
        user_id="user_override",
        messages=[
            LLMMessageDTO(role="system", content="System preamble"),
            LLMMessageDTO(role="user", content="Direct message"),
        ],
    )
    assert res.content is not None and "https://grounding.example.com" in res.content
    assert res.token_usage.total_tokens == 75
    assert res.token_usage.cached_tokens == 40
    assert res.token_usage.reasoning_tokens == 15
    assert res.provider_metadata is not None and res.provider_metadata.finish_reason == "length"
    assert res.tool_calls is not None and res.tool_calls[0].id == "call_abc123"
    usage_service.track_usage.assert_called_once()

    res_struct = await provider.generate(
        prompt="Execute task",
        response_schema=_DummyPydanticSchema,
        temperature=0.0,
        max_tokens=100,
    )
    assert res_struct is not None

    class _DumpObj:
        def model_dump(self) -> Any:
            return {"id": "dump_id", "type": "function", "function": {"name": "f1", "arguments": "{}"}}

    class _VariedResponse:
        choices = [
            MagicMock(
                message=MagicMock(
                    content="",
                    tool_calls=[
                        OpenAIToolCallDTO(id="call_dto", type="function", function={"name": "f0", "arguments": "{}"}),
                        _DumpObj(),
                        {"id": "call_dict", "type": "function", "function": {"name": "f2", "arguments": '{"k": "v"}'}},
                    ],
                    provider_specific_fields={"reasoning_blob": "blob_blob"},
                ),
                finish_reason="stop",
            )
        ]
        usage = _FullUsage()
        system_fingerprint = "fp_varied"
        model = "gpt-5.4"
        model_extra = {"thought_signature": "sig_extra"}
        _hidden_params: Any = {}

    provider.router.acompletion = AsyncMock(return_value=_VariedResponse())
    mock_active_span = MagicMock()
    mock_active_span.is_recording.return_value = True
    mock_active_span.get_span_context.return_value = SpanContext(
        trace_id=0x1234567890ABCDEF1234567890ABCDEF,
        span_id=0x1234567890ABCDEF,
        is_remote=False,
        trace_flags=TraceFlags(TraceFlags.SAMPLED),
    )
    mock_otel = MagicMock()
    mock_otel.get_current_span.return_value = mock_active_span
    monkeypatch.setattr(provider_facade, "otel_trace", mock_otel)
    monkeypatch.delenv("DUMP_PROMPTS_FILE", raising=False)

    res_varied = await provider.generate(
        prompt="",
        system_instruction=None,
        messages=[{"role": "user", "content": "hello"}],
        temperature=0.0,
        max_tokens=50,
    )
    assert res_varied.tool_calls is not None and len(res_varied.tool_calls) == 3
    assert res_varied.reasoning_token == "blob_blob"

    usage_service.track_usage = AsyncMock(side_effect=RuntimeError("Tracking DB down"))
    with pytest.raises(AppException):
        await provider.generate("test", temperature=0.5, max_tokens=50)

    usage_service.track_usage = AsyncMock()
    monkeypatch.setattr(litellm, "completion_cost", MagicMock(side_effect=ValueError("Cost lookup failed")))
    with pytest.raises(AgentExecutionError):
        await provider.generate("test", temperature=0.5, max_tokens=50)
