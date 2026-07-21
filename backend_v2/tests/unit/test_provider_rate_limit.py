import asyncio
from typing import Any

import pytest

from backend_v2.llm.provider import LiteLLMProvider


@pytest.fixture
def mock_settings() -> Any:
    class Settings:
        llm_default_timeout = 60
        default_safety_settings: list[Any] = []
        vertex_location = "europe-north1"

    return Settings()


@pytest.mark.asyncio
@pytest.mark.skip("Legacy architecture obsolete")
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

            class MockRateLimit(Exception):
                status_code = 429

            raise MockRateLimit("litellm.RateLimitError: 429 Resource exhausted")

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


    # apply_provider_pacing removed from module

    try:
        response = await provider.generate(prompt="Test rate limit", temperature=0.7, max_tokens=1000)
        assert response.content == "Success!"
    except Exception as e:
        pytest.fail(f"Provider crashed completely during rate limit test: {e}")

    # Verify that we slept (to wait out RPM limit using exponential backoff with jitter)
    assert len(sleep_calls) > 0, "No async sleep was invoked to mitigate the RateLimitError"
    assert any(3 <= s <= 7 for s in sleep_calls), f"The sleep was {sleep_calls}, expected between 3s and 7s"


@pytest.mark.asyncio
@pytest.mark.skip("Legacy architecture obsolete")
async def test_lite_llm_fail_soft_fallback(mock_settings: Any, monkeypatch: Any) -> None:
    """Ensure LiteLLMProvider rate limit exhaustion on a heavy model
    triggers a dynamic fail-soft downgrade to gemini-2.5-flash on the final attempt.
    """
    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-2.5-pro",
        api_key="fake",
        settings=mock_settings,
        limits={"tpm": 100000, "rpm": 5},
    )

    calls = []

    # Mock router.acompletion for first two failed attempts
    async def mock_router_acompletion(*args: Any, **kwargs: Any) -> Any:
        calls.append(("router", kwargs.get("model")))

        class MockRateLimit(Exception):
            status_code = 429

        raise MockRateLimit("litellm.RateLimitError: 429 Resource exhausted")

    # Mock litellm.acompletion for the third fallback attempt
    async def mock_litellm_acompletion(*args: Any, **kwargs: Any) -> Any:
        calls.append(("litellm", kwargs.get("model")))

        class MockChoice:
            message = type(
                "Message", (), {"content": "Fallback Success!", "tool_calls": None, "provider_specific_fields": None}
            )()

        class MockResponse:
            choices = [MockChoice()]
            system_fingerprint = "fake_fingerprint"
            usage = type(
                "Usage",
                (),
                {
                    "prompt_tokens": 100,
                    "completion_tokens": 50,
                    "total_tokens": 150,
                    "prompt_tokens_details": None,
                    "completion_tokens_details": None,
                },
            )()

            def model_dump(self) -> dict[str, Any]:
                return {}

        return MockResponse()

    monkeypatch.setattr(provider.router, "acompletion", mock_router_acompletion)

    import litellm

    monkeypatch.setattr(litellm, "acompletion", mock_litellm_acompletion)
    monkeypatch.setattr(litellm, "completion_cost", lambda **k: 0.0005)

    # Disable sleeping to keep the test ultra fast and avoid infinite recursion
    async def mock_sleep(seconds: Any) -> None:
        pass

    monkeypatch.setattr(asyncio, "sleep", mock_sleep)


    # apply_provider_pacing removed from module

    response = await provider.generate(
        prompt="Test fallback",
        temperature=0.7,
        max_tokens=1000,
    )

    # Assertions
    assert response.content == "Fallback Success!"
    assert response.override_reason is not None
    assert "Downgraded to vertex_ai/gemini-2.5-flash" in response.override_reason
    assert response.token_usage.cost_usd == 0.0005

    # Verify order and models used in attempts
    assert len(calls) == 3
    # Attempt 1: Router with Pro
    assert calls[0] == ("router", "vertex_ai/gemini-2.5-pro")
    # Attempt 2: Router with Pro
    assert calls[1] == ("router", "vertex_ai/gemini-2.5-pro")
    # Attempt 3: Direct LiteLLM with Flash (due to fallback)
    assert calls[2] == ("litellm", "vertex_ai/gemini-2.5-flash")
