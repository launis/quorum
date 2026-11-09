"""Unit tests for the LLMCachingService."""

import logging
from unittest.mock import AsyncMock, MagicMock, patch

import opentelemetry.trace as otel_trace
import pytest
from pydantic import SecretStr

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.caching_service import LLMCachingService
from backend_v2.models.auth import ResolvedCredentialDTO
from backend_v2.models.domain.system_config import ProviderExtraParamsDTO
from backend_v2.models.enums import SecretScope
from backend_v2.models.llm import CachingPayloadResultDTO, LLMMessageDTO, LLMProviderConfig
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
        mock_adapter.prepare_caching_payload.assert_called_once_with(
            compiled_prompt,
            "gemini-1.5-pro",
            config=None,
            resolved_credential=None,
        )
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
    """Verify that exceptions during teardown are wrapped in AppException."""
    mock_adapter = AsyncMock()
    mock_adapter.teardown_cache.side_effect = RuntimeError("Teardown failed")

    with patch("backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter", return_value=mock_adapter):
        with pytest.raises(AppException, match="Teardown failed") as exc_info:
            await LLMCachingService.teardown_workflow_caches(
                provider_name="anthropic",
                workflow_run_id="run_123",
            )
        assert exc_info.value.status_code == 500
        assert exc_info.value.details["error_code"] == ErrorCodes.INTERNAL_SERVER_ERROR


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
        mock_adapter.prepare_caching_payload.assert_called_once_with(
            compiled_prompt,
            "gemini-1.5-pro",
            config=None,
            resolved_credential=None,
        )


@pytest.mark.asyncio
async def test_purity_scanner_detects_violations(caplog: pytest.LogCaptureFixture) -> None:
    """Verify purity scanner raises Fail-Fast AppException on dynamic traces in system instructions."""
    mock_adapter = AsyncMock()
    mock_adapter.prepare_caching_payload.return_value = CachingPayloadResultDTO(messages=[], kwargs={})

    # UUID in system message
    uuid_prompt = CompiledPrompt(
        static_messages=[LLMMessageDTO(role="system", content="Trace: 12345678-1234-1234-1234-123456789abc")],
        dynamic_messages=[],
    )
    with (
        patch("backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter", return_value=mock_adapter),
        caplog.at_level(logging.ERROR),
        pytest.raises(AppException) as exc_info,
    ):
        await LLMCachingService.prepare_caching_payload(
            provider_name="vertex_ai",
            compiled_prompt=uuid_prompt,
            model_name="gemini-1.5-pro",
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert exc_info.value.details["violating_role"] == "system"
    assert "PROMPT_CACHING_PURITY_VIOLATION" in caplog.text

    caplog.clear()

    # Timestamp in system message (Scenario NEG-07)
    ts_prompt = CompiledPrompt(
        static_messages=[LLMMessageDTO(role="system", content="Timestamp: 2026-08-27T18:22:00")],
        dynamic_messages=[],
    )
    with (
        patch("backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter", return_value=mock_adapter),
        caplog.at_level(logging.ERROR),
        pytest.raises(AppException) as exc_info,
    ):
        await LLMCachingService.prepare_caching_payload(
            provider_name="vertex_ai",
            compiled_prompt=ts_prompt,
            model_name="gemini-1.5-pro",
        )
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
    assert exc_info.value.details["violating_role"] == "system"
    assert "PROMPT_CACHING_PURITY_VIOLATION" in caplog.text


def test_record_cache_hit_with_recording_span() -> None:
    """Verify record_cache_hit sets the gen_ai.cache.hit attribute only when span is recording."""
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


@pytest.mark.asyncio
async def test_prepare_caching_payload_and_pre_cache_forward_config_and_credential() -> None:
    """Verify prepare_caching_payload and pre_cache_document forward config and resolved_credential."""
    mock_adapter = AsyncMock()
    mock_adapter.prepare_caching_payload.return_value = CachingPayloadResultDTO(messages=[], kwargs={})
    compiled_prompt = CompiledPrompt(static_messages=[], dynamic_messages=[])
    provider_config = LLMProviderConfig(
        id="prv_0195f3a0000070008000000000000111",
        provider="vertex_ai",
        model_name="vertex_ai/gemini-2.5-flash",
        vertex_location="europe-west1",
        tpm_limit=1000,
        rpm_limit=60,
        additional_params=ProviderExtraParamsDTO(),
    )
    resolved_cred = ResolvedCredentialDTO(
        organization_id="org_0195f3a0000070008000000000000111",
        scope=SecretScope.LLM_PROVIDER,
        target_identifier="vertex_ai",
        secret_value=SecretStr("AIzaSyTestExpressKey"),
        is_tenant_byok=True,
    )

    with patch("backend_v2.llm.adapters.adapter_factory.LLMCacheAdapterFactory.get_adapter", return_value=mock_adapter):
        await LLMCachingService.prepare_caching_payload(
            provider_name="vertex_ai",
            compiled_prompt=compiled_prompt,
            model_name="vertex_ai/gemini-2.5-flash",
            config=provider_config,
            resolved_credential=resolved_cred,
        )
        mock_adapter.prepare_caching_payload.assert_called_once_with(
            compiled_prompt,
            "vertex_ai/gemini-2.5-flash",
            config=provider_config,
            resolved_credential=resolved_cred,
        )

        mock_adapter.prepare_caching_payload.reset_mock()
        await LLMCachingService.pre_cache_document(
            provider_name="vertex_ai",
            compiled_prompt=compiled_prompt,
            model_name="vertex_ai/gemini-2.5-flash",
            config=provider_config,
            resolved_credential=resolved_cred,
        )
        mock_adapter.prepare_caching_payload.assert_called_once_with(
            compiled_prompt,
            "vertex_ai/gemini-2.5-flash",
            config=provider_config,
            resolved_credential=resolved_cred,
        )


@pytest.mark.asyncio
async def test_prepare_caching_payload_invalid_service_account_json_error() -> None:
    """ISTQB Negative Test: Malformed Vertex Service Account JSON raises ConfigurationError Fail-Fast."""
    compiled_prompt = CompiledPrompt(
        static_messages=[LLMMessageDTO(role="user", content="Static text")],
        dynamic_messages=[LLMMessageDTO(role="user", content="Dynamic text")],
    )
    malformed_cred = ResolvedCredentialDTO(
        organization_id="org_0195f3a0000070008000000000000222",
        scope=SecretScope.LLM_PROVIDER,
        target_identifier="vertex_ai",
        secret_value=SecretStr("{malformed-json"),
        is_tenant_byok=True,
    )

    with pytest.raises(ConfigurationError) as exc_info:
        await LLMCachingService.prepare_caching_payload(
            provider_name="vertex_ai",
            compiled_prompt=compiled_prompt,
            model_name="vertex_ai/gemini-2.5-flash",
            resolved_credential=malformed_cred,
        )
    assert exc_info.value.details["error_code"] == ErrorCodes.CONFIGURATION_ERROR.value
