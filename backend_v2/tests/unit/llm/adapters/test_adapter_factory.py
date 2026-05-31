"""Unit tests for LLMCacheAdapterFactory."""

import sys

import pytest
from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.llm.adapters.adapter_factory import LLMCacheAdapterFactory
from backend_v2.llm.adapters.base_adapter import BaseLLMAdapter
from backend_v2.llm.adapters.mock_adapter import MockCacheAdapter
from backend_v2.models.enums import LLMProviderName


def test_lazy_import_proof() -> None:
    """Prove that importing the factory does not load heavy ML libraries globally."""
    heavy_libs = ["vertexai", "anthropic", "openai", "litellm", "google.genai"]
    for lib in heavy_libs:
        assert lib not in sys.modules, f"Heavy ML library '{lib}' was unexpectedly loaded globally!"


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
        LLMProviderName.GOOGLE,
        LLMProviderName.ANTHROPIC,
        LLMProviderName.OPENAI,
        LLMProviderName.DEEPSEEK,
    ]

    for provider in providers:
        adapter = LLMCacheAdapterFactory.get_adapter(provider)
        assert isinstance(adapter, BaseLLMAdapter)
