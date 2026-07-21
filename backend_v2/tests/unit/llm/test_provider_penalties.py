"""Tests for LLMProvider penalty parameter handling."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend_v2.llm.provider import LiteLLMProvider
from backend_v2.models.llm import LLMProviderConfig

pytestmark = pytest.mark.asyncio


async def test_litellm_provider_injects_penalties() -> None:
    """Test that frequency and presence penalties are injected into Litellm kwargs."""
    # 1. This will FAIL because LLMProviderConfig doesn't have these fields yet (Red phase).
    config = LLMProviderConfig(
        id="conf_12345678",
        provider="openai",
        model_name="gpt-4o",
        tpm_limit=1000,
        rpm_limit=10,
        frequency_penalty=0.5,
        presence_penalty=0.1,
    )

    mock_settings = MagicMock()
    mock_settings.llm_default_timeout = 30
    mock_settings.llm_max_retries = 0
    mock_settings.llm_retry_jitter_initial_seconds = 0
    mock_settings.llm_retry_max_seconds = 0
    mock_settings.llm_retry_jitter_exp_base = 1

    limits = {"tpm": 1000, "rpm": 10}

    provider = LiteLLMProvider(model_name="gpt-4o", settings=mock_settings, limits=limits, config=config)

    class MockUsage:
        prompt_tokens = 10
        completion_tokens = 20
        total_tokens = 30

    class MockMsg:
        content: str = "test response"
        tool_calls: list[Any] = []

    class MockChoice:
        message = MockMsg()
        finish_reason = "stop"

    class MockResponse:
        choices: list[Any] = [MockChoice()]
        usage: MockUsage = MockUsage()

        def model_dump(self) -> dict[str, Any]:
            return {}

    mock_response = MockResponse()

    provider.router.acompletion = AsyncMock(return_value=mock_response)

    # Mock apply_provider_pacing so it doesn't try to access Redis/Locks
    if True:
        # 2. This will FAIL because provider.generate() doesn't accept these arguments yet.
        await provider.generate(
            prompt="Test prompt", temperature=0.0, max_tokens=100, frequency_penalty=0.5, presence_penalty=0.1
        )

    # 3. Verify they were injected into the Litellm acompletion call kwargs.
    provider.router.acompletion.assert_called_once()
    kwargs = provider.router.acompletion.call_args.kwargs
    assert "frequency_penalty" in kwargs
    assert kwargs["frequency_penalty"] == 0.5
    assert "presence_penalty" in kwargs
    assert kwargs["presence_penalty"] == 0.1
