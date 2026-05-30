"""Unit tests for Epic 66: Unified Vertex AI Model Garden & Multi-Provider Integration."""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import ConfigurationError
from backend_v2.llm.handler import LLMHandler
from backend_v2.llm.provider import LLMFactory
from backend_v2.settings import Settings


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def handler(mock_repo: AsyncMock) -> LLMHandler:
    return LLMHandler(mock_repo)


def test_settings_enabled_providers_with_anthropic() -> None:
    """Test that settings.enabled_providers dynamically includes 'anthropic'."""
    settings = Settings(
        use_mock_llm=False,
        google_api_key="fake-google-key",
        openai_api_key="fake-openai-key",
        anthropic_api_key="fake-anthropic-key",
        vertex_location="europe-north1",
        discovery_location="us-central1",
        storage_backend="LOCAL",
    )
    providers = settings.enabled_providers
    assert "google" in providers
    assert "openai" in providers
    assert "anthropic" in providers


def test_settings_enabled_providers_without_anthropic() -> None:
    """Test that settings.enabled_providers excludes 'anthropic' when key is missing."""
    settings = Settings(
        use_mock_llm=False,
        google_api_key="fake-google-key",
        openai_api_key="fake-openai-key",
        anthropic_api_key=None,
        vertex_location="europe-north1",
        discovery_location="us-central1",
        storage_backend="LOCAL",
    )
    providers = settings.enabled_providers
    assert "google" in providers
    assert "openai" in providers
    assert "anthropic" not in providers


@patch("backend_v2.llm.handler.get_settings")
def test_fetch_all_available_models_direct_anthropic(mock_get_settings: MagicMock, handler: LLMHandler) -> None:
    """Test that LLMHandler lists direct Anthropic models correctly when key is configured."""
    mock_settings = MagicMock()
    mock_settings.use_mock_llm = False
    mock_settings.anthropic_api_key = "fake-anthropic-key"
    mock_settings.enabled_providers = ["anthropic"]
    mock_get_settings.return_value = mock_settings

    models = handler.fetch_all_available_models(providers=["anthropic"])
    assert "anthropic" in models
    assert "anthropic/claude-3-5-sonnet" in models["anthropic"]
    assert "anthropic/claude-3-opus-20240229" in models["anthropic"]


@patch("backend_v2.llm.handler.get_settings")
def test_fetch_all_available_models_direct_anthropic_missing_key(mock_get_settings: MagicMock, handler: LLMHandler) -> None:
    """Test that LLMHandler raises ConfigurationError when direct Anthropic is requested but key is missing."""
    mock_settings = MagicMock()
    mock_settings.use_mock_llm = False
    mock_settings.anthropic_api_key = None
    mock_settings.enabled_providers = ["anthropic"]
    mock_get_settings.return_value = mock_settings

    with pytest.raises(Exception) as exc_info:
        handler.fetch_all_available_models(providers=["anthropic"])
    assert "ANTHROPIC_API_KEY not found" in str(exc_info.value)


@patch("backend_v2.llm.handler.get_settings")
@patch("google.auth.default")
@patch("google.auth.transport.requests.Request")
@patch("requests.get")
def test_fetch_all_available_models_vertex_model_garden(
    mock_requests_get: MagicMock,
    mock_auth_request: MagicMock,
    mock_auth_default: MagicMock,
    mock_get_settings: MagicMock,
    handler: LLMHandler,
) -> None:
    """Test that LLMHandler discovers Vertex Model Garden and Gemini models correctly."""
    mock_settings = MagicMock()
    mock_settings.vertex_location = "europe-north1"
    mock_settings.discovery_location = "us-central1"
    mock_settings.enabled_providers = ["google"]
    mock_settings.use_mock_llm = False
    mock_get_settings.return_value = mock_settings

    # Mock Auth
    mock_creds = MagicMock()
    mock_creds.token = "mock-token"
    mock_auth_default.return_value = (mock_creds, "mock-project")

    # Mock LiteLLM model list
    with patch("litellm.model_list", ["vertex_ai/gemini-1.5-flash", "vertex_ai/claude-3-5-sonnet", "vertex_ai/llama-3.1-70b-instruct"]):
        # Mock requests.get for third-party publisher URLs
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests_get.return_value = mock_response

        # Mock GenAI client for Gemini models
        mock_client_instance = MagicMock()
        with patch("google.genai.Client", return_value=mock_client_instance):
            models = handler.fetch_all_available_models(providers=["google"])
            assert "google" in models
            google_models = models["google"]
            
            # Should validate and include all of them
            assert "vertex_ai/gemini-1.5-flash" in google_models
            assert "vertex_ai/claude-3-5-sonnet" in google_models
            assert "vertex_ai/llama-3.1-70b-instruct" in google_models


@patch("backend_v2.llm.provider.get_settings")
def test_llm_factory_api_key_resolution(mock_get_settings: MagicMock) -> None:
    """Test that LLMFactory resolves API keys correctly based on provider and model name."""
    mock_settings = MagicMock()
    mock_settings.use_mock_llm = False
    mock_settings.google_api_key = "google-key"
    mock_settings.openai_api_key = "openai-key"
    mock_settings.anthropic_api_key = "anthropic-key"
    mock_get_settings.return_value = mock_settings

    # 1. Test Anthropic provider type
    provider = LLMFactory.create_provider(
        provider_type="anthropic",
        model_name="claude-3-5-sonnet",
        limits={"tpm": 1000, "rpm": 10},
    )
    assert provider.api_key == "anthropic-key"

    # 2. Test LiteLLM with Claude model name
    provider_litellm = LLMFactory.create_provider(
        provider_type="litellm",
        model_name="anthropic/claude-3-5-sonnet",
        limits={"tpm": 1000, "rpm": 10},
    )
    assert provider_litellm.api_key == "anthropic-key"
