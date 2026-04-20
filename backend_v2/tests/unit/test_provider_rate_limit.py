import asyncio
from typing import Any

import pytest

from backend_v2.llm.provider import LiteLLMProvider


@pytest.fixture
def mock_settings() -> Any:
    class Settings:
        llm_default_timeout = 60
        default_safety_settings: list[Any] = []

    return Settings()


@pytest.mark.asyncio
async def test_lite_llm_rate_limit_cooldown(mock_settings: Any, monkeypatch: Any) -> None:
    """TDD Repro: Ensure LiteLLMProvider rate limit exhaustion triggers
    a 60s cooldown instead of burning Tenacity retries instantly.
    """
    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-2.5-flash",
        api_key="fake",
        settings=mock_settings,
        limits={"tpm": 100000, "rpm": 5},
    )

    call_count = {"count": 0}

    async def mock_acompletion(*args: Any, **kwargs: Any) -> Any:
        call_count["count"] += 1
        if call_count["count"] == 1:
            raise Exception("litellm.RateLimitError: 429 Resource exhausted")

        # Second call succeeds
        class MockChoice:
            message = type("Message", (), {"content": "Success!", "tool_calls": None})()

        class MockResponse:
            choices = [MockChoice()]

            def model_dump(self) -> dict[str, Any]:
                return {}

        return MockResponse()

    monkeypatch.setattr(provider.router, "acompletion", mock_acompletion)

    # We patch asyncio.sleep to not actually sleep in the test but record it
    sleep_calls: list[int] = []

    async def mock_sleep(seconds: int) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr(asyncio, "sleep", mock_sleep)

    try:
        response = await provider.generate(prompt="Test rate limit", temperature=0.7, max_tokens=1000)
        assert response.content == "Success!"
    except Exception as e:
        pytest.fail(f"Provider crashed completely during rate limit test: {e}")

    # Verify that we slept for at least 60 seconds (to wait out RPM limit)
    assert len(sleep_calls) > 0, "No async sleep was invoked to mitigate the RateLimitError"
    assert any(s >= 60 for s in sleep_calls), "The sleep was less than 60s, quota would not reset"
