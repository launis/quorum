"""Unit tests for the LLMCachingService."""

from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.llm.caching_service import LLMCachingService
from backend_v2.models.prompt import CompiledPrompt


@pytest.mark.asyncio
async def test_prepare_caching_payload() -> None:
    """Verify that prepare_caching_payload delegates to the correct adapter."""
    mock_adapter = AsyncMock()
    mock_adapter.prepare_caching_payload.return_value = (
        [{"role": "user", "content": "mock_messages"}],
        {"mock": "kwargs"},
    )

    compiled_prompt = CompiledPrompt(static_messages=[], dynamic_messages=[])

    with patch(
        "backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter", return_value=mock_adapter
    ) as mock_get:
        messages, kwargs = await LLMCachingService.prepare_caching_payload(
            provider_name="vertex_ai",
            compiled_prompt=compiled_prompt,
            model_name="gemini-1.5-pro",
        )

        mock_get.assert_called_once_with("vertex_ai")
        mock_adapter.prepare_caching_payload.assert_called_once_with(compiled_prompt, "gemini-1.5-pro")
        assert messages == [{"role": "user", "content": "mock_messages"}]
        assert kwargs == {"mock": "kwargs"}


@pytest.mark.asyncio
async def test_teardown_workflow_caches() -> None:
    """Verify that teardown_workflow_caches delegates to the correct adapter."""
    mock_adapter = AsyncMock()

    with patch(
        "backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter", return_value=mock_adapter
    ) as mock_get:
        await LLMCachingService.teardown_workflow_caches(
            provider_name="anthropic",
            workflow_run_id="run_123",
        )

        mock_get.assert_called_once_with("anthropic")
        mock_adapter.teardown_cache.assert_called_once_with("run_123")


@pytest.mark.asyncio
async def test_teardown_workflow_caches_exception() -> None:
    """Verify that exceptions during teardown are properly raised."""
    mock_adapter = AsyncMock()
    mock_adapter.teardown_cache.side_effect = Exception("Teardown failed")

    with patch("backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter", return_value=mock_adapter):
        with pytest.raises(Exception, match="Teardown failed"):
            await LLMCachingService.teardown_workflow_caches(
                provider_name="anthropic",
                workflow_run_id="run_123",
            )
