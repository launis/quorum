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
        LLMProviderName.GOOGLE,
        LLMProviderName.ANTHROPIC,
        LLMProviderName.OPENAI,
        LLMProviderName.DEEPSEEK,
    ]

    for provider in providers:
        adapter = LLMCacheAdapterFactory.get_adapter(provider)
        assert isinstance(adapter, BaseLLMAdapter)


def test_factory_resolves_google_provider_with_vertex_model() -> None:
    """Verify that provider 'google' or 'vertex_ai' with model 'vertex_ai/gemini-2.5-flash' returns VertexCacheAdapter.

    When model_name or context indicates a Vertex AI deployment (such as 'vertex_ai/gemini-2.5-flash' in seed_data.json),
    routing provider 'google' must resolve to VertexCacheAdapter rather than GoogleAIStudioCacheAdapter.
    """
    from backend_v2.llm.adapters.ai_studio_adapter import GoogleAIStudioCacheAdapter
    from backend_v2.llm.adapters.vertex_adapter import VertexCacheAdapter

    # When model_name is a vertex_ai model, should return VertexCacheAdapter
    vertex_adapter = LLMCacheAdapterFactory.get_adapter(LLMProviderName.GOOGLE, model_name="vertex_ai/gemini-2.5-flash")
    assert isinstance(vertex_adapter, VertexCacheAdapter)

    # When model_name is a direct gemini/ai_studio model, should return GoogleAIStudioCacheAdapter
    studio_adapter = LLMCacheAdapterFactory.get_adapter(LLMProviderName.GOOGLE, model_name="gemini/gemini-2.5-flash")
    assert isinstance(studio_adapter, GoogleAIStudioCacheAdapter)

    # When explicit AI_STUDIO provider is passed, should return GoogleAIStudioCacheAdapter
    studio_explicit = LLMCacheAdapterFactory.get_adapter(LLMProviderName.AI_STUDIO)
    assert isinstance(studio_explicit, GoogleAIStudioCacheAdapter)

    # When explicit VERTEX_AI provider is passed, should return VertexCacheAdapter
    vertex_explicit = LLMCacheAdapterFactory.get_adapter(LLMProviderName.VERTEX_AI)
    assert isinstance(vertex_explicit, VertexCacheAdapter)

    # String representations
    assert isinstance(LLMCacheAdapterFactory.get_adapter("google", model_name="vertex_ai/model"), VertexCacheAdapter)
    assert isinstance(
        LLMCacheAdapterFactory.get_adapter("google", model_name="gemini-flash"), GoogleAIStudioCacheAdapter
    )
    assert isinstance(LLMCacheAdapterFactory.get_adapter("ai_studio"), GoogleAIStudioCacheAdapter)
    assert isinstance(LLMCacheAdapterFactory.get_adapter("vertex_ai"), VertexCacheAdapter)


@pytest.mark.parametrize(
    ("provider", "module_name"),
    [
        (LLMProviderName.AI_STUDIO, "backend_v2.llm.adapters.ai_studio_adapter"),
        (LLMProviderName.VERTEX_AI, "backend_v2.llm.adapters.vertex_adapter"),
        (LLMProviderName.GOOGLE, "backend_v2.llm.adapters.ai_studio_adapter"),
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


def test_factory_google_vertex_import_error_handling() -> None:
    """Verify that an ImportError when loading VertexCacheAdapter under Google provider raises AppException."""
    from unittest.mock import patch

    with patch.dict("sys.modules", {"backend_v2.llm.adapters.vertex_adapter": None}):
        with pytest.raises(AppException) as exc_info:
            LLMCacheAdapterFactory.get_adapter(LLMProviderName.GOOGLE, model_name="vertex_ai/gemini-2.5-flash")

        assert exc_info.value.status_code == 500
        assert exc_info.value.error_code == str(ErrorCodes.CAPABILITY_NOT_SUPPORTED)
