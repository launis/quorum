from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.llm.provider import LiteLLMProvider
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.settings import get_settings


@pytest.mark.asyncio
async def test_lite_llm_provider_tool_calls_content_extraction(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tier 4 Bug Hunting Repro:
    Ensures that if Vertex/Gemini returns structured JSON via tool_calls instead of content,
    the provider.py extracts it properly instead of returning an empty string.
    """
    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())
    import litellm

    monkeypatch.setattr(litellm, "completion_cost", lambda *args, **kwargs: 0.002)
    config = LLMProviderConfig(
        id="prv_test1234",
        provider="litellm",
        model_name="vertex_ai/gemini-2.5-flash",
        api_key="secret",
        tpm_limit=100,
        rpm_limit=10,
        temperature=0.0,
    )

    settings = get_settings()

    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-2.5-flash",
        api_key="secret",
        settings=settings,
        limits={"tpm": 100, "rpm": 10},
        config=config,
    )

    provider.router.acompletion = AsyncMock()

    class MockFunction:
        name = "test_func"
        arguments = '{"answer": "structured data from tool calls"}'

    class MockToolCall:
        id = "call_test123"
        type = "function"
        function = MockFunction()

    class MockMessage:
        content = None  # Crucial: Content is missing!
        tool_calls = [MockToolCall()]

    class MockChoice:
        message = MockMessage()
        finish_reason = "stop"

    class MockUsage:
        prompt_tokens = 10
        completion_tokens = 5
        total_tokens = 15

    class MockLiteLLMResponse:
        choices = [MockChoice()]
        model_extra: dict[str, Any] = {}
        usage = MockUsage()

        def model_dump(self) -> dict[str, Any]:
            return {}

    provider.router.acompletion.return_value = MockLiteLLMResponse()

    if True:
        # Act
        response = await provider.generate(
            prompt="Hello",
            temperature=0.0,
            max_tokens=100,
        )

    # Assert
    # If the bug is present, result.content will be "" (empty).
    # If fixed, it should extract the JSON from tool_calls.
    assert response.content == '{"answer": "structured data from tool calls"}', (
        "BUG REPRODUCED: provider.py failed to extract JSON from tool_calls when content was None. "
        "This causes client.py to throw AgentExecutionCritical (Safety Filter Triggered)."
    )
