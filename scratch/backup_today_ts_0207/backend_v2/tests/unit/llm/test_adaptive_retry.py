import asyncio
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import ServiceUnavailableError
from backend_v2.llm.provider import LiteLLMProvider
from backend_v2.settings import get_settings


class MockRateLimitError(Exception):
    """Mock rate limit exception to trigger transient error recovery."""

    status_code = 429


@pytest.mark.asyncio
async def test_lite_llm_provider_adaptive_retry_depleted(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test LiteLLMProvider retry loop is triggered and depleted after 2 retries (3 attempts total)."""
    # Mock asyncio.sleep to avoid waiting during test execution
    mock_sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", mock_sleep)
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())

    settings = get_settings()
    settings.llm_retry_jitter_initial_seconds = 0.001
    settings.llm_retry_max_seconds = 0.001
    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-1.5-pro",
        api_key="secret",
        settings=settings,
        limits={"tpm": 100, "rpm": 10},
    )

    # Mock the acompletion function to always raise MockRateLimitError
    mock_acompletion = AsyncMock(side_effect=MockRateLimitError("Rate limit exceeded"))
    provider.router.acompletion = mock_acompletion

    import litellm

    mock_litellm_acompletion = AsyncMock(side_effect=MockRateLimitError("Rate limit exceeded"))
    monkeypatch.setattr(litellm, "acompletion", mock_litellm_acompletion)

    # LiteLLMProvider.generate should deplete retries and raise ServiceUnavailableError
    with pytest.raises(ServiceUnavailableError) as exc_info:
        await provider.generate(
            prompt="Hello",
            temperature=0.7,
            max_tokens=100,
        )

    # Verify the error details
    assert "rate limit exceeded" in str(exc_info.value).lower()

    # Verify primary model calls (attempts 1, 2, & 3)
    assert mock_acompletion.call_count == get_settings().llm_max_retries + 1
    assert mock_litellm_acompletion.call_count == 0

    # Verify that sleep was called 2 times (during the retries)
    assert mock_sleep.call_count == get_settings().llm_max_retries


@pytest.mark.asyncio
async def test_lite_llm_provider_adaptive_retry_success_on_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test LiteLLMProvider retry loop succeeds on a retry attempt."""
    import litellm

    mock_sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", mock_sleep)
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())
    monkeypatch.setattr(litellm, "completion_cost", lambda *args, **kwargs: 0.002)

    settings = get_settings()
    settings.llm_retry_jitter_initial_seconds = 0.001
    settings.llm_retry_max_seconds = 0.001
    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-1.5-pro",
        api_key="secret",
        settings=settings,
        limits={"tpm": 100, "rpm": 10},
    )

    # Mock responses
    class MockMessage:
        content = "successful retry response"
        tool_calls: list[object] = []

    class MockChoice:
        message = MockMessage()
        finish_reason = "stop"

    class MockUsage:
        prompt_tokens = 10
        completion_tokens = 5
        total_tokens = 15

    class MockLiteLLMResponse:
        choices = [MockChoice()]
        model_extra: dict[str, object] = {}
        usage = MockUsage()

        def model_dump(self) -> dict[str, object]:
            return {}

    # Mock acompletion to fail once, then succeed
    mock_acompletion = AsyncMock(
        side_effect=[
            MockRateLimitError("First attempt rate limited"),
            MockLiteLLMResponse(),
        ]
    )
    provider.router.acompletion = mock_acompletion

    response = await provider.generate(
        prompt="Hello",
        temperature=0.7,
        max_tokens=100,
    )

    assert response.content == "successful retry response"
    assert mock_acompletion.call_count == 2
    assert mock_sleep.call_count == 1
