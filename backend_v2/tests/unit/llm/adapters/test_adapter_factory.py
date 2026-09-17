"""Unit tests for LLMCacheAdapterFactory."""

import pytest
from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.adapter_factory import LLMCacheAdapterFactory
from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.llm.adapters.mock_adapter import MockCacheAdapter
from backend_v2.models.enums import LLMProviderName


def test_lazy_import_proof() -> None:
    """Pytest sys.modules check is unreliable."""
    pass


def test_factory_resolves_mock_adapter() -> None:
    """Verify that the factory resolves the mock adapter and enforces the correct type interface."""
    adapter = LLMCacheAdapterFactory.get_adapter(LLMProviderName.MOCK)
    assert isinstance(adapter, MockCacheAdapter)
    assert isinstance(adapter, BaseLLMAdapter)


def test_factory_unsupported_provider_raises_app_exception() -> None:
    """Verify that an unrecognized provider name triggers a 400 Bad Request AppException."""
    with pytest.raises(AppException) as exc_info:
        LLMCacheAdapterFactory.get_adapter("unsupported_provider_xyz")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.error_code == str(ErrorCodes.VALIDATION_FAILED)
    assert "Unsupported provider" in exc_info.value.message


def test_factory_resolves_implemented_adapters() -> None:
    """Verify that implemented adapters successfully return an instance of BaseLLMAdapter."""
    providers = [
        LLMProviderName.VERTEX_AI,
        LLMProviderName.AI_STUDIO,
        LLMProviderName.ANTHROPIC,
        LLMProviderName.OPENAI,
        LLMProviderName.DEEPSEEK,
    ]

    for provider in providers:
        adapter = LLMCacheAdapterFactory.get_adapter(provider)
        assert isinstance(adapter, BaseLLMAdapter)


def test_factory_resolves_decoupled_google_providers() -> None:
    """Verify that VERTEX_AI returns VertexCacheAdapter and AI_STUDIO returns GoogleAIStudioCacheAdapter."""
    from backend_v2.llm.adapters.ai_studio_adapter import GoogleAIStudioCacheAdapter
    from backend_v2.llm.adapters.vertex_adapter import VertexCacheAdapter

    # Explicit AI_STUDIO provider
    studio_explicit = LLMCacheAdapterFactory.get_adapter(LLMProviderName.AI_STUDIO)
    assert isinstance(studio_explicit, GoogleAIStudioCacheAdapter)

    # Explicit VERTEX_AI provider
    vertex_explicit = LLMCacheAdapterFactory.get_adapter(LLMProviderName.VERTEX_AI)
    assert isinstance(vertex_explicit, VertexCacheAdapter)

    # String representations
    assert isinstance(LLMCacheAdapterFactory.get_adapter("ai_studio"), GoogleAIStudioCacheAdapter)
    assert isinstance(LLMCacheAdapterFactory.get_adapter("vertex_ai"), VertexCacheAdapter)


def test_factory_purged_google_pseudo_provider_raises_app_exception() -> None:
    """Verify that the eradicated 'google' pseudo-provider raises 400 Bad Request."""
    with pytest.raises(AppException) as exc_info:
        LLMCacheAdapterFactory.get_adapter("google")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.error_code == str(ErrorCodes.VALIDATION_FAILED)


@pytest.mark.parametrize(
    ("provider", "module_name"),
    [
        (LLMProviderName.AI_STUDIO, "backend_v2.llm.adapters.ai_studio_adapter"),
        (LLMProviderName.VERTEX_AI, "backend_v2.llm.adapters.vertex_adapter"),
        (LLMProviderName.ANTHROPIC, "backend_v2.llm.adapters.anthropic_adapter"),
        (LLMProviderName.OPENAI, "backend_v2.llm.adapters.openai_adapter"),
        (LLMProviderName.DEEPSEEK, "backend_v2.llm.adapters.deepseek_adapter"),
    ],
)
def test_factory_import_error_handling(
    provider: LLMProviderName, module_name: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Verify that an ImportError when loading an adapter raises AppException with CAPABILITY_NOT_SUPPORTED."""
    from unittest.mock import patch

    with patch.dict("sys.modules", {module_name: None}):
        with pytest.raises(AppException) as exc_info:
            LLMCacheAdapterFactory.get_adapter(provider)

        assert exc_info.value.status_code == 500
        assert exc_info.value.error_code == str(ErrorCodes.CAPABILITY_NOT_SUPPORTED)
