"""Unit tests for adaptive Retry-After rate limit handling and strategy-scoped pacing.

Verifies that:
1. LiteLLMProvider extracts dynamic retry delay from RateLimitError (e.g. "Please try again in 10.958s" or Retry-After header)
   and sleeps at least that duration instead of blindly following static exponential jitter.
2. LLMClient and LiteLLMProvider pass deterministic strategy identifiers to apply_provider_pacing
   rather than random instance UUIDs, ensuring distributed locks are shared across client instances.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel

from backend_v2.exceptions import ServiceUnavailableError
from backend_v2.llm.client import LLMClient
from backend_v2.llm.provider import (
    LiteLLMProvider,
    _AdaptiveWaitWithRetryAfter,
    _extract_retry_after_seconds,
)
from backend_v2.models.enums import CognitiveTier, LLMProvider
from backend_v2.models.v2_core import ModelProfile, SystemConfigModelRegistry
from backend_v2.settings import get_settings
from backend_v2.tests.fakes.in_memory_repositories import InMemorySystemRepository


class DummyResponse(BaseModel):
    """Dummy schema for structured task testing."""

    content: str


class MockOpenAIRateLimitError(Exception):
    """Mock OpenAI rate limit error with 'Please try again in X.Xs' in the message."""

    status_code: int = 429

    def __init__(self, message: str, headers: dict[str, str] | None = None) -> None:
        super().__init__(message)
        self.headers = headers or {}
        self.response = type("MockResponse", (), {"headers": self.headers})()


@pytest.mark.asyncio
async def test_provider_respects_upstream_retry_after_delay(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that LiteLLMProvider extracts 'Please try again in 10.958s' and sleeps >= 10.958s."""
    mock_sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", mock_sleep)
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())

    mock_settings = get_settings().model_copy(
        update={
            "llm_max_transient_retries": 1,
            "llm_retry_jitter_initial_seconds": 2,
            "llm_retry_max_seconds": 60,
        }
    )
    monkeypatch.setattr("backend_v2.llm.provider.get_settings", lambda: mock_settings)

    provider = LiteLLMProvider(
        model_name="openai/gpt-5.1",
        api_key="sk-test",
        settings=mock_settings,
        limits={"tpm": 1000000, "rpm": 500},
    )

    # Error specifies 10.958s wait
    error_msg = (
        "Rate limit reached for gpt-5.1 on tokens per min (TPM): "
        "Limit 1000000, Used 933461, Requested 182649. Please try again in 10.958s..."
    )
    mock_acompletion = AsyncMock(side_effect=MockOpenAIRateLimitError(error_msg))
    provider.router.acompletion = mock_acompletion

    with pytest.raises(ServiceUnavailableError):
        await provider.generate(
            prompt="Test prompt",
            temperature=0.0,
            max_tokens=100,
        )

    # Check that sleep was called during the retry with duration >= 10.958
    assert mock_sleep.call_count >= 1, "Expected asyncio.sleep to be called for retry backoff"
    sleep_delay = mock_sleep.call_args[0][0]
    assert sleep_delay >= 10.958, f"Expected retry sleep >= 10.958s, but got {sleep_delay}s"


@pytest.mark.asyncio
async def test_client_strategy_scoping_in_provider_pacing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that LLMClient passes the deterministic strategy name to apply_provider_pacing."""
    repo = InMemorySystemRepository()

    def _make_profile() -> ModelProfile:
        return ModelProfile(
            model_name="openai/gpt-5.1",
            temperature=0.0,
            max_tokens=4096,
            tpm_limit=1000000,
            rpm_limit=500,
            provider="openai",
            caching_strategy="none",
        )

    registry_config = SystemConfigModelRegistry(
        id="sys_1234567890abcdef",
        name="Test Registry",
        type="model_registry",
        default_provider=LLMProvider.OPENAI,
        tier_definitions={
            CognitiveTier.FAST: _make_profile(),
            CognitiveTier.BALANCED: _make_profile(),
            CognitiveTier.DEEP: _make_profile(),
            CognitiveTier.REASONING: _make_profile(),
        },
    )
    await repo.update_model_registry(registry_config)

    client = await LLMClient.from_strategy("fast", repository=repo, registry_id=registry_config.id)

    captured_pacing_kwargs: dict[str, Any] = {}

    async def fake_apply_provider_pacing(**kwargs: Any) -> None:
        nonlocal captured_pacing_kwargs
        captured_pacing_kwargs = kwargs

    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", fake_apply_provider_pacing)

    from litellm.router import Router

    mock_choice = type(
        "MockChoice",
        (),
        {"message": type("MockMessage", (), {"content": '{"content": "ok"}', "tool_calls": []})()},
    )()
    mock_usage = type(
        "MockUsage",
        (),
        {"prompt_tokens": 10, "completion_tokens": 10, "total_tokens": 20},
    )()
    mock_response = type(
        "MockResponse",
        (),
        {"choices": [mock_choice], "model": "openai/gpt-5.1", "usage": mock_usage},
    )()
    monkeypatch.setattr(Router, "acompletion", AsyncMock(return_value=mock_response))

    await client.run_structured_task(
        messages=[{"role": "user", "content": "hello"}],
        response_model=DummyResponse,
    )

    assert "strategy_id" in captured_pacing_kwargs
    assert captured_pacing_kwargs["strategy_id"] == "openai/gpt-5.1", (
        f"Expected pacing strategy_id='openai/gpt-5.1', but got '{captured_pacing_kwargs.get('strategy_id')}'"
    )


def test_extract_retry_after_from_header_numeric() -> None:
    """Verify numeric Retry-After header extraction."""
    err = MockOpenAIRateLimitError("Rate limit exceeded", headers={"Retry-After": "15.5"})
    assert _extract_retry_after_seconds(err) == 15.5


def test_extract_retry_after_from_header_non_numeric() -> None:
    """Verify non-numeric Retry-After header gracefully returns None."""
    err = MockOpenAIRateLimitError("Rate limit exceeded", headers={"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"})
    assert _extract_retry_after_seconds(err) is None


def test_extract_retry_after_negative_and_zero_values() -> None:
    """Verify negative and zero Retry-After values are safely ignored."""
    err_neg = MockOpenAIRateLimitError("Rate limit exceeded", headers={"Retry-After": "-5.0"})
    assert _extract_retry_after_seconds(err_neg) is None

    err_zero = MockOpenAIRateLimitError("Rate limit exceeded", headers={"Retry-After": "0"})
    assert _extract_retry_after_seconds(err_zero) is None


def test_extract_retry_after_from_nested_exception_group() -> None:
    """Verify recursive extraction from ExceptionGroup."""
    err1 = ValueError("Unrelated error")
    err2 = MockOpenAIRateLimitError("Please try again in 8.2s...")
    group = ExceptionGroup("nested", [err1, err2])
    assert _extract_retry_after_seconds(group) == 8.2


def test_extract_retry_after_circular_reference_safety() -> None:
    """Verify cycle detection prevents infinite recursion on chained exceptions."""
    err1 = MockOpenAIRateLimitError("Please try again in 12.0s...")
    err2 = RuntimeError("Wrapper error")
    err1.__cause__ = err2
    err2.__cause__ = err1
    assert _extract_retry_after_seconds(err1) == 12.0


def test_adaptive_wait_clamping_to_max_seconds() -> None:
    """Verify adaptive waiter clamps upstream delay to configured max_seconds."""
    from tenacity import Future, RetryCallState
    from tenacity.wait import wait_fixed

    waiter = _AdaptiveWaitWithRetryAfter(
        base_wait=wait_fixed(1.0),
        max_seconds=60.0,
    )
    # Simulate a failed attempt with a 120s retry-after delay
    err = MockOpenAIRateLimitError("Please try again in 120.0s...")
    outcome = Future(1)
    outcome.set_exception(err)
    retry_state = RetryCallState(
        retry_object=None,  # type: ignore[arg-type]
        fn=None,
        args=(),
        kwargs={},
    )
    retry_state.outcome = outcome

    delay = waiter(retry_state)
    assert delay == 60.0, f"Expected wait to be clamped to 60.0s max, but got {delay}s"
