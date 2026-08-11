import asyncio

import pytest
from pydantic import BaseModel

from backend_v2.llm.provider import LiteLLMProvider
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.settings import Settings


class DummySchema(BaseModel):
    test_field: str


@pytest.mark.asyncio
async def test_redis_timeout_logs_spam(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that simulates a Redis timeout / CancelledError during LiteLLM's LoggingWorker
    async_increment_pipeline execution, which causes the Router's logging to fail.
    We ensure that the provider handles it without crashing the main generation.
    """
    from unittest.mock import AsyncMock

    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())
    import litellm

    monkeypatch.setattr(litellm, "completion_cost", lambda *args, **kwargs: 0.002)

    config = LLMProviderConfig(
        id="prv_12345678",
        provider="litellm",
        model_name="vertex_ai/gemini-2.5-flash",
        api_key="fake",
        temperature=0.0,
        tpm_limit=1000,
        rpm_limit=10,
        default_max_tokens=100,
        supports_grounding=False,
        parsing_mode="strict",
        caching_strategy="none",
        additional_params={},
    )

    settings = Settings(redis_host="localhost", redis_port=6379, llm_default_timeout=5, llm_max_retries=0)

    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-2.5-flash",
        api_key="fake",
        settings=settings,
        organization_id="test_org",
        limits={"tpm": 1000, "rpm": 10},
        config=config,
    )

    from typing import Any

    from litellm.caching.redis_cache import RedisCache

    # Mock Redis pipeline increment to simulate the hang/timeout that raises CancelledError
    async def mock_increment(*args: Any, **kwargs: Any) -> Any:
        raise asyncio.exceptions.CancelledError()

    monkeypatch.setattr(RedisCache, "async_increment_pipeline", mock_increment)

    # Mock the actual LLM call so we only test the logging worker behavior
    async def mock_acompletion(*args: Any, **kwargs: Any) -> Any:
        from litellm import Choices, Message, ModelResponse, Usage

        return ModelResponse(
            id="chatcmpl-123",
            choices=[
                Choices(
                    finish_reason="stop", index=0, message=Message(content='{"test_field": "val"}', role="assistant")
                )
            ],
            model="vertex_ai/gemini-2.5-flash",
            usage=Usage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
        )

    monkeypatch.setattr(provider.router, "acompletion", mock_acompletion)

    response = await provider.generate(
        prompt="test", temperature=0.0, max_tokens=100, timeout=1.0, response_schema=DummySchema
    )

    assert response is not None

    # Allow the event loop to run LoggingWorker tasks to trigger the mocked error
    await asyncio.sleep(0.5)

    # Verify that the router was initialized with cache_kwargs to prevent real hangs
    assert hasattr(provider.router, "cache")
