"""Unit tests for LiteLLM response parsing, telemetry recording, and RFC 7807 error stage."""

from __future__ import annotations

import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import litellm
import litellm.exceptions as litellm_exc
import opentelemetry.trace as otel_trace
import pytest
from pydantic import BaseModel, ConfigDict

import backend_v2.llm.provider as provider_facade
import backend_v2.llm.provider.litellm_response_stage as response_stage_mod
from backend_v2.exceptions import (
    AgentExecutionError,
    AppException,
    ConfigurationError,
    ErrorCodes,
    SecurityViolationError,
    ServiceUnavailableError,
)
from backend_v2.llm.provider.litellm_response_stage import (
    _truncate_for_debug,
    classify_and_raise_litellm_error,
    extract_litellm_content_and_usage,
)
from backend_v2.models.domain.mcp import OpenAIFunctionCallDTO, OpenAIToolCallDTO
from backend_v2.models.llm import LLMMessageDTO


class _DummyStructuredSchema(BaseModel):
    """Strict Pydantic schema for testing structured output response handling."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    answer: str


class _FakeFunctionObj:
    """Stub function call object without model_dump."""

    def __init__(self, name: str, arguments: str) -> None:
        """Initialize function stub."""
        self.name = name
        self.arguments = arguments


class _FakeToolCallObj:
    """Stub tool call object without model_dump."""

    def __init__(self, call_id: str | None, name: str, arguments: str) -> None:
        """Initialize tool call stub."""
        if call_id is not None:
            self.id = call_id
        self.function = _FakeFunctionObj(name=name, arguments=arguments)


class _DumpableToolCallObj:
    """Stub tool call object exposing model_dump."""

    def __init__(self, call_id: str, name: str, arguments: str) -> None:
        """Initialize dumpable tool call stub."""
        self._id = call_id
        self._name = name
        self._arguments = arguments

    def model_dump(self) -> Any:
        """Return OpenAI tool call dictionary representation."""
        return {
            "id": self._id,
            "type": "function",
            "function": {"name": self._name, "arguments": self._arguments},
        }


class _TokenDetailsStub:
    """Stub for prompt_tokens_details and completion_tokens_details."""

    def __init__(self, cached_tokens: int | None = None, reasoning_tokens: int | None = None) -> None:
        """Initialize token detail counts."""
        self.cached_tokens = cached_tokens
        self.reasoning_tokens = reasoning_tokens


class _UsageStub:
    """Stub for LiteLLM response usage object."""

    def __init__(
        self,
        prompt_tokens: int | None = 12,
        completion_tokens: int | None = 8,
        total_tokens: int | None = 20,
        cached_tokens: int | None = None,
        reasoning_tokens: int | None = None,
    ) -> None:
        """Initialize token usage stub."""
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
        self.prompt_tokens_details = _TokenDetailsStub(cached_tokens=cached_tokens)
        self.completion_tokens_details = _TokenDetailsStub(reasoning_tokens=reasoning_tokens)


class _MessageStub:
    """Stub for LiteLLM choice message."""

    def __init__(
        self,
        content: str | None = "ok",
        tool_calls: Any = None,
        provider_specific_fields: Any = None,
    ) -> None:
        """Initialize message stub."""
        self.content = content
        self.tool_calls = tool_calls
        self.provider_specific_fields = provider_specific_fields


class _ChoiceStub:
    """Stub for LiteLLM response choice."""

    def __init__(self, message: _MessageStub, finish_reason: str | None = "stop") -> None:
        """Initialize choice stub."""
        self.message = message
        self.finish_reason = finish_reason


class _ResponseStub:
    """Stub for LiteLLM ModelResponse."""

    def __init__(
        self,
        message: _MessageStub,
        model: str = "openai/gpt-4o",
        finish_reason: str | None = "stop",
        usage: _UsageStub | None = None,
        system_fingerprint: str | None = "fp_test",
        hidden_params: Any = None,
        model_extra: Any = None,
    ) -> None:
        """Initialize response stub."""
        self.choices = [_ChoiceStub(message=message, finish_reason=finish_reason)]
        self.model = model
        self.usage = usage if usage is not None else _UsageStub()
        self.system_fingerprint = system_fingerprint
        self._hidden_params = hidden_params
        self.model_extra = model_extra

    def model_dump(self) -> Any:
        """Return metadata dictionary."""
        return {"provider_echo": self.model}

    def model_dump_json(self) -> str:
        """Return diagnostic JSON string."""
        return f'{{"model": "{self.model}"}}'


def test_truncate_for_debug_handles_empty_and_populated_strings(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verifies that _truncate_for_debug logs redacted length or <empty> without leaking content."""
    with caplog.at_level("INFO"):
        _truncate_for_debug("", "EMPTY_TEST")
        _truncate_for_debug("secret-user-prompt", "PROMPT_TEST")

    assert "[EMPTY_TEST]: <empty>" in caplog.text
    assert "[PROMPT_TEST]: Length=18 chars | Content=[REDACTED_FOR_SECURITY]" in caplog.text
    assert "secret-user-prompt" not in caplog.text


@pytest.mark.asyncio
async def test_litellm_provider_generate_full_telemetry_and_toolcalls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifies content/tool_calls extraction, TokenUsage, cost_usd, and OpenTelemetry GenAI attributes."""
    monkeypatch.setattr(litellm, "completion_cost", lambda **_: 0.0042)

    mock_span = MagicMock()
    mock_span.is_recording.return_value = True
    mock_otel = MagicMock()
    mock_otel.get_current_span.return_value = mock_span
    monkeypatch.setattr(provider_facade, "otel_trace", mock_otel)

    dto_tc = OpenAIToolCallDTO(
        id="call_dto_1",
        function=OpenAIFunctionCallDTO(name="search_docs", arguments='{"q": "quorum"}'),
    )
    dumpable_tc = _DumpableToolCallObj("call_dump_2", "fetch_url", '{"url": "https://example.com"}')
    raw_tc = _FakeToolCallObj(None, "calc_metric", '{"x": 1}')

    msg = _MessageStub(
        content=None,
        tool_calls=[dto_tc, dumpable_tc, raw_tc],
        provider_specific_fields={"thought_signature": "sig_abc"},
    )
    usage = _UsageStub(
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=None,
        cached_tokens=40,
        reasoning_tokens=15,
    )
    resp = _ResponseStub(
        message=msg,
        model="vertex_ai/gemini-2.5-pro",
        finish_reason="tool_calls",
        usage=usage,
        hidden_params={"headers": {"x-ratelimit-remaining-requests": "5"}},
        model_extra={
            "safety_ratings": [{"category": "HARM_CATEGORY_HATE_SPEECH", "probability": "NEGLIGIBLE"}],
            "grounding_metadata": {
                "grounding_chunks": [{"web": {"uri": "https://grounded.example.com/doc"}}],
            },
        },
    )

    mock_usage_service = MagicMock()
    mock_usage_service.track_usage = AsyncMock()

    result = await extract_litellm_content_and_usage(
        response=resp,
        model_name="openai/gpt-4o",
        start_time=time.perf_counter() - 0.05,
        final_messages=[LLMMessageDTO(role="user", content="hello")],
        response_schema=None,
        usage_service=mock_usage_service,
        organization_id="org_default12345678",
        kwargs={"organization_id": "org_override12345678", "user_id": "usr_test12345678"},
    )

    assert '{"q": "quorum"}' in result.content
    assert "https://grounded.example.com/doc" in result.content
    assert result.reasoning_token == "sig_abc"
    assert result.token_usage.prompt_tokens == 100
    assert result.token_usage.completion_tokens == 50
    assert result.token_usage.total_tokens == 150
    assert result.token_usage.cached_tokens == 40
    assert result.token_usage.reasoning_tokens == 15
    assert result.token_usage.cost_usd == pytest.approx(0.0042)
    assert result.provider_metadata is not None
    assert result.provider_metadata.finish_reason == "tool_calls"
    assert result.tool_calls is not None
    assert len(result.tool_calls) == 3
    assert result.tool_calls[0].id == "call_dto_1"
    assert result.tool_calls[1].id == "call_dump_2"
    assert result.tool_calls[2].id.startswith("call_")

    mock_span.set_attribute.assert_any_call("gen_ai.response.model", "vertex_ai/gemini-2.5-pro")
    mock_span.set_attribute.assert_any_call("gen_ai.usage.input_tokens", 100)
    mock_span.set_attribute.assert_any_call("gen_ai.usage.output_tokens", 50)
    mock_usage_service.track_usage.assert_awaited_once()


@pytest.mark.asyncio
async def test_extract_litellm_content_and_usage_variants_and_error_paths(
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Verifies dict tool_calls, reasoning_blob/model_extra fallbacks, and error handling paths."""
    with caplog.at_level("ERROR"), pytest.raises(ServiceUnavailableError, match="Failed to get a response"):
        await extract_litellm_content_and_usage(
            response=None,
            model_name="openai/gpt-4o",
            start_time=time.perf_counter(),
            final_messages=[],
        )
    assert "SERVICE_UNAVAILABLE" in caplog.text

    monkeypatch.delitem(response_stage_mod.sys.modules, "backend_v2.llm.provider", raising=False)
    assert response_stage_mod._resolve_otel_trace() is otel_trace

    monkeypatch.setattr(litellm, "completion_cost", lambda **_: 0.001)
    dict_tc = {"id": "call_dict_1", "type": "function", "function": {"name": "fn_a", "arguments": ""}}
    msg_blob = _MessageStub(
        content="",
        tool_calls=[dict_tc],
        provider_specific_fields={"reasoning_blob": "blob_xyz"},
    )
    resp_blob = _ResponseStub(
        message=msg_blob,
        model="openai/gpt-4o",
        finish_reason="eos",
        usage=_UsageStub(prompt_tokens=5, completion_tokens=5, total_tokens=10),
        model_extra={"grounding_metadata": {"grounding_chunks": [{"web": {"uri": "https://ex.com"}}]}},
    )
    res_schema = await extract_litellm_content_and_usage(
        response=resp_blob,
        model_name="openai/gpt-4o",
        start_time=time.perf_counter(),
        final_messages=[{"role": "user", "content": "hi"}],
        response_schema=_DummyStructuredSchema,
    )
    assert res_schema.reasoning_token == "blob_xyz"
    assert res_schema.provider_metadata is not None
    assert res_schema.provider_metadata.finish_reason is None
    assert "https://ex.com" not in res_schema.content

    msg_extra = _MessageStub(content="direct text")
    resp_extra = _ResponseStub(
        message=msg_extra,
        model_extra={"thought_signature": "extra_sig"},
    )
    res_extra = await extract_litellm_content_and_usage(
        response=resp_extra,
        model_name="openai/gpt-4o",
        start_time=time.perf_counter(),
        final_messages=[],
    )
    assert res_extra.reasoning_token == "extra_sig"

    failing_usage = MagicMock()
    failing_usage.track_usage = AsyncMock(side_effect=RuntimeError("db down"))
    with pytest.raises(AppException, match="Usage Tracking Failed"):
        await extract_litellm_content_and_usage(
            response=resp_extra,
            model_name="openai/gpt-4o",
            start_time=time.perf_counter(),
            final_messages=[],
            usage_service=failing_usage,
        )

    def _raise_cost_error(**_: Any) -> float:
        raise ValueError("unmapped model pricing")

    monkeypatch.setattr(litellm, "completion_cost", _raise_cost_error)
    with pytest.raises(AgentExecutionError):
        await extract_litellm_content_and_usage(
            response=resp_extra,
            model_name="openai/gpt-4o",
            start_time=time.perf_counter(),
            final_messages=[],
        )


def test_classify_and_raise_litellm_error_maps_upstream_exceptions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verifies that classify_and_raise_litellm_error maps upstream exceptions deterministically."""
    mock_otel = MagicMock()
    mock_span = MagicMock()
    mock_span.is_recording.return_value = True
    mock_otel.get_current_span.return_value = mock_span
    mock_otel.StatusCode = otel_trace.StatusCode
    monkeypatch.setattr(response_stage_mod, "otel_trace", mock_otel)

    # 1. Pre-wrapped AppException re-raised directly
    pre_wrapped = ConfigurationError("already wrapped")
    with pytest.raises(ConfigurationError, match="already wrapped"):
        classify_and_raise_litellm_error(pre_wrapped, "openai/gpt-4o")
    mock_span.record_exception.assert_called_with(pre_wrapped)

    # 2. Network pass-through (ConnectTimeout)
    class ConnectTimeout(Exception):
        pass

    with pytest.raises(ConnectTimeout):
        classify_and_raise_litellm_error(ConnectTimeout("net timeout"), "openai/gpt-4o")

    # 3. Rate limit (429 / RateLimitError)
    rate_err = litellm_exc.RateLimitError(message="Resource exhausted", llm_provider="openai", model="gpt-4o")
    with pytest.raises(ServiceUnavailableError) as exc_rate:
        classify_and_raise_litellm_error(rate_err, "openai/gpt-4o")
    assert exc_rate.value.details["error_code"] == ErrorCodes.RATE_LIMIT_EXCEEDED.value

    # 4. Instructor / ResponseParsingError
    class InstructorRetryException(Exception):
        pass

    with pytest.raises(AppException) as exc_inst:
        classify_and_raise_litellm_error(InstructorRetryException("schema loop"), "openai/gpt-4o")
    assert exc_inst.value.details["error_code"] == ErrorCodes.AGENT_RESPONSE_PARSING_FAILED.value

    # 5. Authentication error (401/403)
    auth_err = litellm_exc.AuthenticationError(message="invalid_api_key", llm_provider="openai", model="gpt-4o")
    with pytest.raises(ConfigurationError) as exc_auth:
        classify_and_raise_litellm_error(auth_err, "openai/gpt-4o")
    assert exc_auth.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value

    # 6. Context window exceeded
    ctx_err = litellm_exc.ContextWindowExceededError(
        message="maximum context length exceeded", model="gpt-4o", llm_provider="openai"
    )
    with pytest.raises(AgentExecutionError) as exc_ctx:
        classify_and_raise_litellm_error(ctx_err, "openai/gpt-4o")
    assert exc_ctx.value.details["error_code"] == ErrorCodes.AGENT_EXECUTION_CRITICAL.value

    # 7. Generic HTTP 400 Bad Request
    class _StatusError(Exception):
        def __init__(self, msg: str, status_code: int) -> None:
            super().__init__(msg)
            self.status_code = status_code

    with pytest.raises(AgentExecutionError) as exc_400:
        classify_and_raise_litellm_error(_StatusError("malformed payload", 400), "openai/gpt-4o")
    assert exc_400.value.details["error_code"] == ErrorCodes.AGENT_RESPONSE_MALFORMED.value

    # 8. Upstream Timeout / 503
    with pytest.raises(ServiceUnavailableError) as exc_timeout:
        classify_and_raise_litellm_error(TimeoutError("timed out"), "openai/gpt-4o")
    assert exc_timeout.value.details["error_code"] == ErrorCodes.UPSTREAM_TIMEOUT.value

    # 9. Content Policy Violation
    class ContentPolicyViolationError(Exception):
        pass

    with pytest.raises(SecurityViolationError) as exc_sec:
        classify_and_raise_litellm_error(ContentPolicyViolationError("safety blocked"), "openai/gpt-4o")
    assert exc_sec.value.details["error_code"] == ErrorCodes.SECURITY_VIOLATION.value

    # 10. Unknown upstream error with >500 char message truncation
    long_err = RuntimeError("x" * 600)
    with pytest.raises(ServiceUnavailableError) as exc_unk:
        classify_and_raise_litellm_error(long_err, "openai/gpt-4o")
    assert exc_unk.value.details["error_code"] == ErrorCodes.UNKNOWN_ERROR.value
    assert "[TRUNCATED]" in str(exc_unk.value.details["original_error"])
