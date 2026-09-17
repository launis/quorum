"""Unit and ISTQB boundary test suite for Google Vertex AI and Google AI Studio decoupling.

Enforces:
1. Pure typed relation routing (zero startswith or substring guessing).
2. Complete eradication of the 'google' pseudo-provider.
3. Independent credential routing (ADC for Vertex AI vs google_api_key for AI Studio).
4. Live Model Garden discovery hub with regional validation.
5. Location independence for non-Vertex providers.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import status

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.adapters.adapter_factory import LLMCacheAdapterFactory
from backend_v2.llm.adapters.ai_studio_adapter import GoogleAIStudioCacheAdapter
from backend_v2.llm.adapters.vertex_adapter import VertexCacheAdapter
from backend_v2.llm.handler import LLMHandler
from backend_v2.llm.provider import LLMFactory
from backend_v2.models.enums import GCPVertexDiscoveryRegion, LLMPlatformType, LLMProviderName
from backend_v2.settings import Settings


def test_cache_adapter_factory_returns_vertex_adapter() -> None:
    """Verify that get_adapter('vertex_ai') returns VertexCacheAdapter."""
    adapter = LLMCacheAdapterFactory.get_adapter(LLMProviderName.VERTEX_AI)
    assert isinstance(adapter, VertexCacheAdapter)
    assert isinstance(LLMCacheAdapterFactory.get_adapter("vertex_ai"), VertexCacheAdapter)


def test_cache_adapter_factory_returns_ai_studio_adapter() -> None:
    """Verify that get_adapter('ai_studio') returns GoogleAIStudioCacheAdapter."""
    adapter = LLMCacheAdapterFactory.get_adapter(LLMProviderName.AI_STUDIO)
    assert isinstance(adapter, GoogleAIStudioCacheAdapter)
    assert isinstance(LLMCacheAdapterFactory.get_adapter("ai_studio"), GoogleAIStudioCacheAdapter)


def test_cache_adapter_factory_purged_google_raises_validation_failed() -> None:
    """Verify that the eradicated 'google' pseudo-provider raises AppException(VALIDATION_FAILED)."""
    with pytest.raises(AppException) as exc_info:
        LLMCacheAdapterFactory.get_adapter("google")

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.error_code == str(ErrorCodes.VALIDATION_FAILED)


def test_create_provider_strict_credential_routing() -> None:
    """Verify that LLMFactory.create_provider routes credentials strictly by typed provider_type."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.use_mock_llm = False
    mock_settings.google_api_key = "test-ai-studio-key"
    mock_settings.openai_api_key = "test-openai-key"
    mock_settings.anthropic_api_key = "test-anthropic-key"
    mock_settings.max_tokens = 4096
    mock_settings.temperature = 0.7
    mock_settings.request_timeout = 30
    mock_settings.max_retries = 3

    mock_limits = {"tpm": 10000, "rpm": 60}

    with patch("backend_v2.llm.provider.get_settings", return_value=mock_settings):
        # 1. Vertex AI must receive api_key = None (GCP ADC) regardless of model name
        with patch("backend_v2.llm.provider.LiteLLMProvider") as mock_litellm:
            LLMFactory.create_provider(
                provider_type="vertex_ai",
                model_name="gemini-2.5-pro",  # Model name contains "gemini" but must not override provider
                limits=mock_limits,
            )
            assert mock_litellm.call_count == 1
            _, kwargs = mock_litellm.call_args
            assert kwargs["api_key"] is None

        # 2. AI Studio must receive settings.google_api_key regardless of model name
        with patch("backend_v2.llm.provider.LiteLLMProvider") as mock_litellm:
            LLMFactory.create_provider(
                provider_type="ai_studio",
                model_name="vertex_ai/gemini-2.5-flash",  # Model name contains "vertex_ai" but must not override provider
                limits=mock_limits,
            )
            assert mock_litellm.call_count == 1
            _, kwargs = mock_litellm.call_args
            assert kwargs["api_key"] == "test-ai-studio-key"


def test_istqb_negative_ai_studio_missing_api_key_raises_configuration_error() -> None:
    """ISTQB Boundary Test 1: Missing google_api_key for AI Studio raises ConfigurationError."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.use_mock_llm = False
    mock_settings.google_api_key = None

    mock_limits = {"tpm": 10000, "rpm": 60}

    with patch("backend_v2.llm.provider.get_settings", return_value=mock_settings):
        with pytest.raises(ConfigurationError) as exc_info:
            LLMFactory.create_provider(
                provider_type="ai_studio",
                model_name="gemini-2.5-flash",
                limits=mock_limits,
            )

        assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR
        assert "google_api_key" in exc_info.value.message.lower() or "gemini_api_key" in exc_info.value.message.lower()


def test_istqb_negative_vertex_ai_missing_deps_raises_service_dependency_missing() -> None:
    """ISTQB Boundary Test: Missing GCP dependencies raises ConfigurationError(SERVICE_DEPENDENCY_MISSING)."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.discovery_location = "us-central1"

    with patch("backend_v2.llm.handler.GOOGLE_DEPS_AVAILABLE", False):
        with pytest.raises(ConfigurationError) as exc_info:
            handler = LLMHandler(repo=AsyncMock())
            handler._fetch_vertex_models(target_location="europe-north1", settings=mock_settings)

        assert exc_info.value.error_code == ErrorCodes.SERVICE_DEPENDENCY_MISSING


def test_istqb_negative_vertex_ai_missing_adc_raises_authentication_failed() -> None:
    """ISTQB Boundary Test 2: Missing GCP credentials raises ConfigurationError(AUTHENTICATION_FAILED)."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.discovery_location = "us-central1"
    mock_settings.google_application_credentials = None

    with (
        patch("backend_v2.llm.handler.GOOGLE_DEPS_AVAILABLE", True),
        patch("google.auth.default", side_effect=Exception("Could not automatically determine credentials")),
    ):
        with pytest.raises(ConfigurationError) as exc_info:
            handler = LLMHandler(repo=AsyncMock())
            handler._fetch_vertex_models(target_location="europe-north1", settings=mock_settings)

        assert exc_info.value.error_code == ErrorCodes.AUTHENTICATION_FAILED


def test_istqb_equivalence_enabled_providers_independence() -> None:
    """ISTQB Boundary Test 3: Settings.enabled_providers calculates vertex_ai and ai_studio independently."""
    # Case A: Only google_api_key present -> ai_studio enabled, vertex_ai disabled
    with (
        patch("os.path.exists", return_value=False),
        patch.dict(
            "os.environ",
            {"VERTEX_PROJECT_ID": "", "GOOGLE_APPLICATION_CREDENTIALS": ""},
            clear=False,
        ),
    ):
        settings_ai_only = Settings(
            use_mock_llm=False,
            google_api_key="valid-key",
            openai_api_key=None,
            anthropic_api_key=None,
            google_application_credentials=None,
            vertex_project_id=None,
        )
        enabled = settings_ai_only.enabled_providers
        assert "ai_studio" in enabled
        assert "vertex_ai" not in enabled
        assert "google" not in enabled

    # Case B: Only service-account.json present -> vertex_ai enabled, ai_studio disabled
    with patch("os.path.exists", side_effect=lambda p: p == "service-account.json"):
        settings_vertex_only = Settings(
            use_mock_llm=False,
            google_api_key=None,
            openai_api_key=None,
            anthropic_api_key=None,
            google_application_credentials="service-account.json",
            vertex_project_id="test-proj",
        )
        enabled = settings_vertex_only.enabled_providers
        assert "vertex_ai" in enabled
        assert "ai_studio" not in enabled
        assert "google" not in enabled


def test_istqb_isolation_non_vertex_discovery_without_location() -> None:
    """ISTQB Boundary Test 4: Querying AI Studio models does not require target_location."""
    handler = LLMHandler(repo=AsyncMock())

    with patch.object(handler, "_fetch_ai_studio_models", return_value=["gemini-2.5-flash", "gemini-2.5-pro"]):
        # location is explicitly None
        result = handler.fetch_all_available_models(
            platform=LLMPlatformType.AI_STUDIO.value,
            location=None,
        )
        ai_models = result[LLMPlatformType.AI_STUDIO.value]
        assert isinstance(ai_models, list)
        assert len(ai_models) == 2
        assert "gemini-2.5-flash" in ai_models
        assert "gemini-2.5-pro" in ai_models


@pytest.mark.asyncio
async def test_istqb_anti_heuristic_model_validation_derives_platform_from_provider() -> None:
    """ISTQB Boundary Test 5: create_provider_for_strategy derives platform from provider, not model_name."""
    handler = LLMHandler(repo=AsyncMock())

    dummy_registry = {
        "models": {
            "fast": {
                "provider": LLMProviderName.VERTEX_AI.value,
                "model_name": "gemini-custom-enterprise",
                "temperature": 0.5,
                "max_tokens": 2048,
                "tpm_limit": 10000,
                "rpm_limit": 60,
                "supports_grounding": False,
                "is_active": True,
                "additional_params": {"vertex_location": "europe-north1"},
            }
        }
    }

    mock_discovery_result = {
        LLMPlatformType.VERTEX_AI.value: ["gemini-custom-enterprise"],
    }

    with (
        patch.object(handler, "get_active_model_registry", AsyncMock(return_value=dummy_registry)),
        patch.object(handler, "fetch_all_available_models", return_value=mock_discovery_result) as mock_fetch,
        patch("backend_v2.llm.provider.LLMFactory.create_provider") as mock_create,
    ):
        mock_create.return_value = MagicMock()
        await handler.create_provider_for_strategy("fast")

        assert mock_fetch.call_count == 1
        _, kwargs = mock_fetch.call_args
        # Platform must be VERTEX_AI derived directly from provider, not from model_name
        assert kwargs["platform"] == LLMPlatformType.VERTEX_AI.value
        assert kwargs["location"] == "europe-north1"


def test_vertex_discovery_uses_us_central1_hub_constant() -> None:
    """Verify that GCPVertexDiscoveryRegion defines US_CENTRAL1 hub."""
    assert GCPVertexDiscoveryRegion.US_CENTRAL1.value == "us-central1"
