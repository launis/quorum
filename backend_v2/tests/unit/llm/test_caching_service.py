"""Unit tests for the LLMCachingService."""

import logging
from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.llm.caching_service import LLMCachingService
from backend_v2.models.llm import CachingPayloadResultDTO, LLMMessageDTO
from backend_v2.models.prompt import CompiledPrompt


@pytest.mark.asyncio
async def test_prepare_caching_payload() -> None:
    """Verify that prepare_caching_payload delegates to the correct adapter."""
    mock_adapter = AsyncMock()
    mock_adapter.prepare_caching_payload.return_value = CachingPayloadResultDTO(
        messages=[LLMMessageDTO(role="user", content="mock_messages")],
        kwargs={"mock": "kwargs"},
    )

    compiled_prompt = CompiledPrompt(static_messages=[], dynamic_messages=[])

    with patch(
        "backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter", return_value=mock_adapter
    ) as mock_get:
        result = await LLMCachingService.prepare_caching_payload(
            provider_name="vertex_ai",
            compiled_prompt=compiled_prompt,
            model_name="gemini-1.5-pro",
        )

        mock_get.assert_called_once_with("vertex_ai", model_name="gemini-1.5-pro")
        mock_adapter.prepare_caching_payload.assert_called_once_with(compiled_prompt, "gemini-1.5-pro")
        assert result.messages == [LLMMessageDTO(role="user", content="mock_messages")]
        assert result.kwargs == {"mock": "kwargs"}


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


@pytest.mark.asyncio
async def test_pre_cache_document() -> None:
    """Verify pre_cache_document forwards to prepare_caching_payload."""
    mock_adapter = AsyncMock()
    mock_adapter.prepare_caching_payload.return_value = CachingPayloadResultDTO(messages=[], kwargs={})
    compiled_prompt = CompiledPrompt(static_messages=[], dynamic_messages=[])

    with patch("backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter", return_value=mock_adapter):
        await LLMCachingService.pre_cache_document(
            provider_name="vertex_ai",
            compiled_prompt=compiled_prompt,
            model_name="gemini-1.5-pro",
        )
        mock_adapter.prepare_caching_payload.assert_called_once_with(compiled_prompt, "gemini-1.5-pro")


@pytest.mark.asyncio
async def test_purity_scanner_detects_violations(caplog: pytest.LogCaptureFixture) -> None:
    """Verify purity scanner logs warning on dynamic traces in system instructions."""
    mock_adapter = AsyncMock()
    mock_adapter.prepare_caching_payload.return_value = CachingPayloadResultDTO(messages=[], kwargs={})

    # UUID in system message
    uuid_prompt = CompiledPrompt(
        static_messages=[LLMMessageDTO(role="system", content="Trace: 12345678-1234-1234-1234-123456789abc")],
        dynamic_messages=[],
    )
    with (
        patch("backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter", return_value=mock_adapter),
        caplog.at_level(logging.WARNING),
    ):
        await LLMCachingService.prepare_caching_payload(
            provider_name="vertex_ai",
            compiled_prompt=uuid_prompt,
            model_name="gemini-1.5-pro",
        )
        assert "PROMPT_CACHING_PURITY_VIOLATION" in caplog.text

    caplog.clear()

    # Timestamp in system message
    ts_prompt = CompiledPrompt(
        static_messages=[LLMMessageDTO(role="system", content="Timestamp: 2026-08-27T18:22:00")],
        dynamic_messages=[],
    )
    with (
        patch("backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter", return_value=mock_adapter),
        caplog.at_level(logging.WARNING),
    ):
        await LLMCachingService.prepare_caching_payload(
            provider_name="vertex_ai",
            compiled_prompt=ts_prompt,
            model_name="gemini-1.5-pro",
        )
        assert "PROMPT_CACHING_PURITY_VIOLATION" in caplog.text


def test_record_cache_hit_with_recording_span() -> None:
    from unittest.mock import MagicMock

    import opentelemetry.trace as otel_trace

    mock_span = MagicMock()
    mock_span.is_recording.return_value = True

    with patch.object(otel_trace, "get_current_span", return_value=mock_span):
        LLMCachingService.record_cache_hit(True)
        mock_span.set_attribute.assert_called_once_with("gen_ai.cache.hit", True)

        mock_span.reset_mock()
        mock_span.is_recording.return_value = False
        LLMCachingService.record_cache_hit(False)
        mock_span.set_attribute.assert_not_called()


def test_caching_payload_result_dto_validation() -> None:
    """Verify CachingPayloadResultDTO validates successfully under ConfigDict(strict=True, extra='forbid')."""
    dto = CachingPayloadResultDTO(
        messages=[LLMMessageDTO(role="system", content="Hello")],
        kwargs={"cached_content": "cache_123"},
    )
    assert len(dto.messages) == 1
    assert dto.kwargs["cached_content"] == "cache_123"
