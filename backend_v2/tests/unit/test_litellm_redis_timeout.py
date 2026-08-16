import asyncio
from typing import Any
from unittest.mock import AsyncMock

import litellm
import pytest
from pydantic import BaseModel, ConfigDict

from backend_v2.llm.provider import LiteLLMProvider
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.settings import Settings


class DummySchema(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid")
    test_field: str


@pytest.mark.asyncio
async def test_litellm_router_in_memory_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify LiteLLMProvider initializes Router with in-memory caching and redis_cache is None."""
    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()

    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())
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

    settings = Settings(redis_host="192.0.2.1", redis_port=9999, llm_default_timeout=5, llm_max_retries=0)

    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-2.5-flash",
        api_key="fake",
        settings=settings,
        organization_id="test_org",
        limits={"tpm": 1000, "rpm": 10},
        config=config,
    )

    assert hasattr(provider.router, "cache")
    # Verify redis_cache is None (in-memory DualCache mode)
    assert getattr(provider.router.cache, "redis_cache", None) is None

    # Mock the actual LLM call
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
    assert response.content == '{"test_field": "val"}'


@pytest.mark.asyncio
async def test_litellm_router_generation_with_unreachable_redis_config(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that even with non-existent Redis configuration in settings, Router executes in-memory with zero network errors."""
    LiteLLMProvider._router_cache.clear()
    LiteLLMProvider._semaphores.clear()

    monkeypatch.setattr("backend_v2.llm.provider.apply_provider_pacing", AsyncMock())
    monkeypatch.setattr(litellm, "completion_cost", lambda *args, **kwargs: 0.002)

    config = LLMProviderConfig(
        id="prv_87654321",
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

    settings = Settings(
        redis_host="invalid-unreachable-redis-host", redis_port=9999, llm_default_timeout=5, llm_max_retries=0
    )

    provider = LiteLLMProvider(
        model_name="vertex_ai/gemini-2.5-flash",
        api_key="fake",
        settings=settings,
        organization_id="test_org_unreachable",
        limits={"tpm": 1000, "rpm": 10},
        config=config,
    )

    async def mock_acompletion(*args: Any, **kwargs: Any) -> Any:
        from litellm import Choices, Message, ModelResponse, Usage

        return ModelResponse(
            id="chatcmpl-456",
            choices=[
                Choices(
                    finish_reason="stop",
                    index=0,
                    message=Message(content='{"test_field": "in_memory_ok"}', role="assistant"),
                )
            ],
            model="vertex_ai/gemini-2.5-flash",
            usage=Usage(prompt_tokens=5, completion_tokens=5, total_tokens=10),
        )

    monkeypatch.setattr(provider.router, "acompletion", mock_acompletion)

    response = await provider.generate(
        prompt="hello", temperature=0.0, max_tokens=50, timeout=1.0, response_schema=DummySchema
    )

    assert response is not None
    assert response.content == '{"test_field": "in_memory_ok"}'
    # Ensure no background socket errors occur
    await asyncio.sleep(0.1)
