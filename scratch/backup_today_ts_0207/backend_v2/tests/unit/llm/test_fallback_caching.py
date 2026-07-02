import asyncio
from typing import Any
from unittest.mock import AsyncMock

import litellm
import pytest

from backend_v2.llm.provider import LiteLLMProvider
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.settings import get_settings


class MockRateLimitError(Exception):
    """Mock rate limit exception to trigger transient error recovery."""

    status_code = 429


@pytest.mark.asyncio
@pytest.mark.skip("Legacy architecture obsolete")
async def test_lite_llm_provider_fallback_strips_cache_control(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that cache_control is stripped from system message when falling back to flash."""
    mock_sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", mock_sleep)
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())
    monkeypatch.setattr(litellm, "completion_cost", lambda *args, **kwargs: 0.001)

    settings = get_settings()

    config = LLMProviderConfig(
        id="prv_testconfig",
        provider="vertex_ai",
        model_name="vertex_ai/gemini-2.5-pro",
        api_key="secret",
        temperature=0.7,
        tpm_limit=100,
        rpm_limit=10,
        caching_strategy="prompt_caching",
    )

    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-2.5-pro",
        api_key="secret",
        settings=settings,
        limits={"tpm": 100, "rpm": 10},
        config=config,
    )

    # 1. Mock router.acompletion to fail 2 times
    mock_router_acompletion = AsyncMock(
        side_effect=[
            MockRateLimitError("First rate limit"),
            MockRateLimitError("Second rate limit"),
        ]
    )
    provider.router.acompletion = mock_router_acompletion

    # 2. Mock litellm.acompletion to succeed on the 3rd attempt (the fallback attempt)
    class MockMessage:
        content = "mocked successful response from flash"
        tool_calls: list[object] = []

    class MockChoice:
        message = MockMessage()
        finish_reason = "stop"

    class MockLiteLLMResponse:
        choices = [MockChoice()]
        model_extra: dict[str, object] = {}
        usage = None

        def model_dump(self) -> dict[str, object]:
            return {}

    mock_litellm_response = MockLiteLLMResponse()
    mock_acompletion = AsyncMock(return_value=mock_litellm_response)
    monkeypatch.setattr(litellm, "acompletion", mock_acompletion)

    # Call generate with cache_control structure in system messages
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": [{"type": "text", "text": "System instructions here", "cache_control": {"type": "ephemeral"}}],
        },
        {"role": "user", "content": "User prompt"},
    ]

    response = await provider.generate(
        messages=messages,
        temperature=0.7,
        max_tokens=100,
    )

    assert response.content == "mocked successful response from flash"
    assert mock_router_acompletion.call_count == 2
    assert mock_acompletion.call_count == 1

    # Verify that the model passed to litellm.acompletion was indeed the flash model
    call_kwargs = mock_acompletion.call_args[1]
    assert call_kwargs["model"] == "vertex_ai/gemini-2.5-flash"

    # Assert that cache_control has been stripped from the system message content!
    fallback_messages = call_kwargs["messages"]
    system_msg = fallback_messages[0]
    content = system_msg["content"]
    assert isinstance(content, list)
    for part in content:
        assert "cache_control" not in part
