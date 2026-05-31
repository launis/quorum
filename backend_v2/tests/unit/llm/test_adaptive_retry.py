import asyncio
from unittest.mock import AsyncMock

import pytest

from backend_v2.exceptions import ServiceUnavailableError
from backend_v2.llm.provider import LiteLLMProvider
from backend_v2.models.enums import SystemConcurrency
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

    # Mock apply_provider_pacing to prevent Fakeredis lock infinite loops
    import backend_v2.llm.adapters.base_adapter

    monkeypatch.setattr(backend_v2.llm.adapters.base_adapter, "apply_provider_pacing", AsyncMock())

    settings = get_settings()
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

    monkeypatch.setattr(litellm, "acompletion", mock_acompletion)

    # LiteLLMProvider.generate should deplete retries and raise ServiceUnavailableError
    with pytest.raises(ServiceUnavailableError) as exc_info:
        await provider.generate(
            prompt="Hello",
            temperature=0.7,
            max_tokens=100,
        )

    # Verify the error details
    assert "rate limit exceeded" in str(exc_info.value).lower()

    # Verify the number of attempts: 1 initial call + 2 retries = 3 attempts total
    assert mock_acompletion.call_count == SystemConcurrency.LLM_MAX_RETRIES.value + 1

    # Verify that sleep was called 2 times (during the retries)
    assert mock_sleep.call_count == SystemConcurrency.LLM_MAX_RETRIES.value


@pytest.mark.asyncio
async def test_lite_llm_provider_adaptive_retry_success_on_retry(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test LiteLLMProvider retry loop succeeds on a retry attempt."""
    import litellm

    mock_sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", mock_sleep)
    monkeypatch.setattr(litellm, "completion_cost", lambda *args, **kwargs: 0.002)

    import backend_v2.llm.adapters.base_adapter

    monkeypatch.setattr(backend_v2.llm.adapters.base_adapter, "apply_provider_pacing", AsyncMock())

    settings = get_settings()
    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-1.5-pro",
        api_key="secret",
        settings=settings,
        limits={"tpm": 100, "rpm": 10},
    )

    # Mock responses
    class MockMessage:
        content: str = "successful retry response"
        tool_calls: list[object] = []

    class MockChoice:
        message: MockMessage = MockMessage()
        finish_reason: str = "stop"

    class MockLiteLLMResponse:
        choices: list[MockChoice] = [MockChoice()]
        model_extra: dict[str, object] = {}

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
