"""Unit and ISTQB test suite for LLMHandler.

Covers:
- Dynamic model discovery across Vertex AI, Google AI Studio, OpenAI, Anthropic, and Mock providers.
- Vertex AI regional location validation, publisher availability checks, and caching.
- Platform routing, configuration validation, and discovery failure boundaries.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from backend_v2.exceptions import (
    ConfigurationError,
    ErrorCodes,
    ServiceUnavailableError,
)
from backend_v2.llm.handler import LLMHandler
from backend_v2.models.dtos.studio import GCPLocationDTO
from backend_v2.models.enums import LLMPlatformType
from backend_v2.settings import Settings
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository


@pytest.fixture
def mock_repo() -> InMemoryUnifiedWorkflowRepository:
    """Fixture providing an in-memory unified workflow repository."""
    return InMemoryUnifiedWorkflowRepository()


@pytest.fixture
def handler(mock_repo: InMemoryUnifiedWorkflowRepository) -> LLMHandler:
    """Fixture providing an LLMHandler instance with in-memory repository."""
    return LLMHandler(mock_repo)


# -----------------------------------------------------------------------------
# Standalone Availability Checks
# -----------------------------------------------------------------------------


def test_check_model_availability_success(handler: LLMHandler) -> None:
    """Verifies that _check_model_availability returns True when client succeeds."""
    mock_client = MagicMock()
    mock_client.models.get.return_value = MagicMock()
    with patch("google.genai.Client", return_value=mock_client):
        assert handler._check_model_availability("gemini-2.5-flash", "us-central1") is True


def test_check_model_availability_rejected_model(handler: LLMHandler) -> None:
    """Verifies that gemini-3.5-pro is blocked fail-fast."""
    assert handler._check_model_availability("models/gemini-3.5-pro", "us-central1") is False


def test_check_model_availability_exception(handler: LLMHandler) -> None:
    """Verifies that client exceptions result in False."""
    mock_client = MagicMock()
    mock_client.models.get.side_effect = RuntimeError("SDK Error")
    with patch("google.genai.Client", return_value=mock_client):
        assert handler._check_model_availability("gemini-2.5-flash", "us-central1") is False


def test_check_model_availability_genai_api_error(handler: LLMHandler) -> None:
    """Verifies that GenAI ClientError/APIError results in False."""
    from google.genai import errors as genai_errors

    mock_client = MagicMock()
    mock_client.models.get.side_effect = genai_errors.ClientError(404, {"error": {"message": "not found"}}, None)
    with patch("google.genai.Client", return_value=mock_client):
        assert handler._check_model_availability("gemini-2.5-flash", "us-central1") is False


# -----------------------------------------------------------------------------
# Mock Models Discovery
# -----------------------------------------------------------------------------


def test_fetch_mock_models_branches(handler: LLMHandler) -> None:
    """Verifies _fetch_mock_models handles all provider branches."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.use_mock_llm = True

    models: dict[str, list[str] | str] = {}
    handler._fetch_mock_models(["vertex_ai", "ai_studio", "openai", "anthropic"], mock_settings, models)

    assert "vertex_ai" in models
    assert "ai_studio" in models
    assert "openai" in models
    assert "anthropic" in models


def test_fetch_mock_models_early_return_when_mock_only(handler: LLMHandler) -> None:
    """Verifies early return when only 'mock' is requested."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.use_mock_llm = False

    models: dict[str, list[str] | str] = {}
    handler._fetch_mock_models(["mock"], mock_settings, models)
    assert "vertex_ai" in models


# -----------------------------------------------------------------------------
# Vertex Models Discovery
# -----------------------------------------------------------------------------


def test_fetch_vertex_models_missing_discovery_location(handler: LLMHandler) -> None:
    """Verifies ConfigurationError when discovery_location is missing from settings."""
    mock_settings = MagicMock()
    mock_settings.discovery_location = None
    with pytest.raises(ConfigurationError) as exc_info:
        handler._fetch_vertex_models("europe-north1", mock_settings)
    assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR


def test_fetch_vertex_models_missing_dependencies(handler: LLMHandler) -> None:
    """Verifies ConfigurationError when Google dependencies are missing."""
    mock_settings = MagicMock()
    mock_settings.discovery_location = "us-central1"
    with patch("backend_v2.llm.handler.GOOGLE_DEPS_AVAILABLE", False):
        with pytest.raises(ConfigurationError) as exc_info:
            handler._fetch_vertex_models("europe-north1", mock_settings)
        assert exc_info.value.error_code == ErrorCodes.SERVICE_DEPENDENCY_MISSING


def test_fetch_vertex_models_auth_error(handler: LLMHandler) -> None:
    """Verifies ConfigurationError when GCP auth fails."""
    mock_settings = MagicMock()
    mock_settings.discovery_location = "us-central1"
    with patch("google.auth.default", side_effect=RuntimeError("Auth failed")):
        with pytest.raises(ConfigurationError) as exc_info:
            handler._fetch_vertex_models("europe-north1", mock_settings)
        assert exc_info.value.error_code == ErrorCodes.AUTHENTICATION_FAILED


def test_fetch_vertex_models_success(handler: LLMHandler) -> None:
    """Verifies discovery and validation of Vertex models."""
    mock_settings = MagicMock()
    mock_settings.discovery_location = "us-central1"
    mock_client = MagicMock()
    mock_client.models.get.return_value = MagicMock()

    with (
        patch("google.auth.default", return_value=(MagicMock(), "proj-123")),
        patch("litellm.model_list", ["vertex_ai/gemini-2.5-pro", "vertex_ai/gemini-2.5-flash"]),
        patch("google.genai.Client", return_value=mock_client),
    ):
        result = handler._fetch_vertex_models("europe-north1", mock_settings)
        assert "vertex_ai/gemini-2.5-pro" in result
        assert "vertex_ai/gemini-2.5-flash" in result


def test_fetch_vertex_models_skips_unsupported_models_with_genai_api_error(handler: LLMHandler) -> None:
    """Verifies that unsupported or missing models raising GenAI ClientError/APIError are skipped rather than crashing discovery."""
    from google.genai import errors as genai_errors

    mock_settings = MagicMock()
    mock_settings.discovery_location = "us-central1"
    mock_client = MagicMock()

    def mock_get(model: str) -> MagicMock:
        if model == "gemini-2.5-flash-preview-tts":
            raise genai_errors.ClientError(
                404,
                {
                    "error": {
                        "code": 404,
                        "message": f"Publisher Model publishers/google/models/{model} is not found.",
                        "status": "NOT_FOUND",
                    }
                },
                None,
            )
        return MagicMock()

    mock_client.models.get.side_effect = mock_get

    with (
        patch("google.auth.default", return_value=(MagicMock(), "proj-123")),
        patch("litellm.model_list", ["vertex_ai/gemini-2.5-flash", "vertex_ai/gemini-2.5-flash-preview-tts"]),
        patch("google.genai.Client", return_value=mock_client),
    ):
        result = handler._fetch_vertex_models("europe-north1", mock_settings)
        assert result == ["vertex_ai/gemini-2.5-flash"]


def test_fetch_vertex_models_dynamic_two_stage_discovery(handler: LLMHandler) -> None:
    """Verifies that Stage 1 fetches candidates dynamically from discovery_location (us-central1), and Stage 2 validates in target_location."""
    mock_settings = MagicMock()
    mock_settings.discovery_location = "us-central1"

    m1 = MagicMock()
    m1.name = "publishers/google/models/gemini-2.5-pro"
    m2 = MagicMock()
    m2.name = "publishers/google/models/gemini-2.5-flash"

    mock_client = MagicMock()
    mock_client.models.list.return_value = [m1, m2]
    mock_client.models.get.return_value = MagicMock()

    with (
        patch("google.auth.default", return_value=(MagicMock(), "proj-123")),
        patch("litellm.model_list", ["vertex_ai/claude-3-5-sonnet"]),
        patch("google.genai.Client", return_value=mock_client),
        patch("requests.get", return_value=MagicMock(status_code=200)),
    ):
        result = handler._fetch_vertex_models("europe-north1", mock_settings)
        assert "vertex_ai/gemini-2.5-pro" in result
        assert "vertex_ai/gemini-2.5-flash" in result
        assert "vertex_ai/claude-3-5-sonnet" in result
        mock_client.models.list.assert_called_once_with(config={"query_base": True})


# -----------------------------------------------------------------------------
# Vertex Locations Discovery
# -----------------------------------------------------------------------------


def test_fetch_vertex_locations_cached(handler: LLMHandler) -> None:
    """Verifies cached vertex locations are returned immediately."""
    cached = [GCPLocationDTO(id="europe-north1", label="Hamina", description="Region")]
    handler._cached_vertex_locations = cached
    mock_settings = MagicMock()
    assert handler.fetch_vertex_locations(mock_settings) is cached


def test_fetch_vertex_locations_mock_mode(handler: LLMHandler) -> None:
    """Verifies mock locations returned when use_mock_llm is True."""
    mock_settings = MagicMock()
    mock_settings.use_mock_llm = True
    locations = handler.fetch_vertex_locations(mock_settings)
    assert len(locations) >= 6
    loc_ids = [loc.id for loc in locations]
    assert "europe-north1" in loc_ids
    assert "us-central1" in loc_ids


def test_fetch_vertex_locations_auth_error(handler: LLMHandler) -> None:
    """Verifies ConfigurationError when GCP auth fails for locations."""
    mock_settings = MagicMock()
    mock_settings.use_mock_llm = False
    with patch("google.auth.default", side_effect=RuntimeError("Auth error")):
        with pytest.raises(ConfigurationError) as exc_info:
            handler.fetch_vertex_locations(mock_settings)
        assert exc_info.value.error_code == ErrorCodes.AUTHENTICATION_FAILED


def test_fetch_vertex_locations_api_error(handler: LLMHandler) -> None:
    """Verifies ServiceUnavailableError when GCP API returns non-200."""
    mock_settings = MagicMock()
    mock_settings.use_mock_llm = False
    mock_settings.llm_default_timeout_seconds = 5
    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.text = "Internal Server Error"

    with (
        patch("google.auth.default", return_value=(MagicMock(), "mock-proj")),
        patch("requests.get", return_value=mock_resp),
    ):
        with pytest.raises(ServiceUnavailableError) as exc_info:
            handler.fetch_vertex_locations(mock_settings)
        assert exc_info.value.error_code == ErrorCodes.SERVICE_UNAVAILABLE


def test_fetch_vertex_locations_timeout(handler: LLMHandler) -> None:
    """Verifies ServiceUnavailableError on HTTP request timeout."""
    mock_settings = MagicMock()
    mock_settings.use_mock_llm = False
    mock_settings.llm_default_timeout_seconds = 5

    with (
        patch("google.auth.default", return_value=(MagicMock(), "mock-proj")),
        patch("requests.get", side_effect=requests.exceptions.Timeout("Timed out")),
    ):
        with pytest.raises(ServiceUnavailableError) as exc_info:
            handler.fetch_vertex_locations(mock_settings)
        assert exc_info.value.error_code == ErrorCodes.SERVICE_UNAVAILABLE


def test_fetch_vertex_locations_success_and_caching(handler: LLMHandler) -> None:
    """Verifies live query and caching for vertex locations."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.use_mock_llm = False
    mock_settings.llm_default_timeout_seconds = 5

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "locations": [
            {"locationId": "europe-north1", "displayName": "Hamina"},
            {"locationId": "us-central1", "displayName": "Iowa"},
        ]
    }

    with (
        patch("google.auth.default", return_value=(MagicMock(), "mock-proj")),
        patch("requests.get", return_value=mock_resp) as mock_get,
    ):
        locations = handler.fetch_vertex_locations(mock_settings)
        assert len(locations) == 2
        assert locations[0].id == "europe-north1"
        assert locations[1].id == "us-central1"
        assert mock_get.call_count == 1

        # Second call hits cache
        cached = handler.fetch_vertex_locations(mock_settings)
        assert cached is locations
        assert mock_get.call_count == 1


# -----------------------------------------------------------------------------
# Google AI Studio Discovery
# -----------------------------------------------------------------------------


def test_fetch_ai_studio_models_cached(handler: LLMHandler) -> None:
    """Verifies cached AI Studio models are returned immediately."""
    handler._cached_ai_studio_models = ["gemini/gemini-2.5-flash"]
    mock_settings = MagicMock(spec=Settings)
    assert handler._fetch_ai_studio_models(mock_settings) == ["gemini/gemini-2.5-flash"]


def test_fetch_ai_studio_models_missing_key(handler: LLMHandler) -> None:
    """Verifies ConfigurationError when google_api_key is missing."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.google_api_key = None
    with pytest.raises(ConfigurationError) as exc_info:
        handler._fetch_ai_studio_models(mock_settings)
    assert exc_info.value.error_code == ErrorCodes.SERVICE_DEPENDENCY_MISSING


def test_fetch_ai_studio_models_success(handler: LLMHandler) -> None:
    """Verifies successful discovery of AI Studio models."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.google_api_key = "test-key"

    m1 = MagicMock()
    m1.name = "models/gemini-2.5-flash"
    m2 = MagicMock()
    m2.name = "models/gemini-2.5-pro"

    mock_client = MagicMock()
    mock_client.models.list.return_value = [m1, m2]

    with patch("google.genai.Client", return_value=mock_client):
        res = handler._fetch_ai_studio_models(mock_settings)
        assert "gemini/gemini-2.5-flash" in res
        assert "gemini/gemini-2.5-pro" in res


def test_fetch_ai_studio_models_exception(handler: LLMHandler) -> None:
    """Verifies ServiceUnavailableError when listing AI Studio models fails."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.google_api_key = "test-key"

    mock_client = MagicMock()
    mock_client.models.list.side_effect = RuntimeError("List failed")

    with patch("google.genai.Client", return_value=mock_client):
        with pytest.raises(ServiceUnavailableError) as exc_info:
            handler._fetch_ai_studio_models(mock_settings)
        assert exc_info.value.error_code == ErrorCodes.MODEL_LIST_FAILED


# -----------------------------------------------------------------------------
# OpenAI Discovery
# -----------------------------------------------------------------------------


def test_fetch_openai_models_cached(handler: LLMHandler) -> None:
    """Verifies cached OpenAI models are returned immediately."""
    handler._cached_openai_models = ["openai/gpt-4o"]
    mock_settings = MagicMock(spec=Settings)
    models: dict[str, list[str] | str] = {}
    handler._fetch_openai_models(["openai"], mock_settings, models)
    assert models["openai"] == ["openai/gpt-4o"]


def test_fetch_openai_models_missing_key(handler: LLMHandler) -> None:
    """Verifies ConfigurationError when openai_api_key is missing."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.openai_api_key = None
    with pytest.raises(ConfigurationError) as exc_info:
        handler._fetch_openai_models(["openai"], mock_settings, {})
    assert exc_info.value.error_code == ErrorCodes.SERVICE_DEPENDENCY_MISSING


def test_fetch_openai_models_exception(handler: LLMHandler) -> None:
    """Verifies ServiceUnavailableError when listing OpenAI models fails."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.openai_api_key = "test-key"
    mock_client = MagicMock()
    mock_client.models.list.side_effect = RuntimeError("API down")

    with patch("openai.OpenAI", return_value=mock_client):
        with pytest.raises(ServiceUnavailableError) as exc_info:
            handler._fetch_openai_models(["openai"], mock_settings, {})
        assert exc_info.value.error_code == ErrorCodes.MODEL_LIST_FAILED


# -----------------------------------------------------------------------------
# Anthropic Discovery
# -----------------------------------------------------------------------------


def test_fetch_anthropic_models_missing_key(handler: LLMHandler) -> None:
    """Verifies ConfigurationError when anthropic_api_key is missing."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.anthropic_api_key = None
    with pytest.raises(ConfigurationError) as exc_info:
        handler._fetch_anthropic_models(["anthropic"], mock_settings, {})
    assert exc_info.value.error_code == ErrorCodes.SERVICE_DEPENDENCY_MISSING


def test_fetch_anthropic_models_success(handler: LLMHandler) -> None:
    """Verifies static discovery when anthropic_api_key is provided."""
    mock_settings = MagicMock(spec=Settings)
    mock_settings.anthropic_api_key = "test-key"
    models: dict[str, list[str] | str] = {}
    handler._fetch_anthropic_models(["anthropic"], mock_settings, models)
    assert "anthropic" in models
    assert "anthropic/claude-3-5-sonnet-20241022" in models["anthropic"]


# -----------------------------------------------------------------------------
# Multi-Provider and Platform-Specific Routing
# -----------------------------------------------------------------------------


def test_fetch_all_available_models_explicit_platforms(handler: LLMHandler) -> None:
    """Verifies routing by explicit platform parameter."""
    with (
        patch.object(handler, "_fetch_vertex_models", return_value=["vertex_ai/gemini-2.5-pro"]),
        patch.object(handler, "_fetch_ai_studio_models", return_value=["gemini/gemini-2.5-flash"]),
        patch.object(handler, "_fetch_openai_models") as mock_openai,
        patch.object(handler, "_fetch_anthropic_models") as mock_anthropic,
    ):
        # Vertex AI
        res_v = handler.fetch_all_available_models(platform=LLMPlatformType.VERTEX_AI.value, location="europe-north1")
        assert res_v[LLMPlatformType.VERTEX_AI.value] == ["vertex_ai/gemini-2.5-pro"]

        # AI Studio
        res_s = handler.fetch_all_available_models(platform=LLMPlatformType.AI_STUDIO.value)
        assert res_s[LLMPlatformType.AI_STUDIO.value] == ["gemini/gemini-2.5-flash"]

        # OpenAI
        handler.fetch_all_available_models(platform=LLMPlatformType.OPENAI.value)
        mock_openai.assert_called_once()

        # Anthropic
        handler.fetch_all_available_models(platform=LLMPlatformType.ANTHROPIC.value)
        mock_anthropic.assert_called_once()


def test_fetch_all_available_models_vertex_missing_location(handler: LLMHandler) -> None:
    """Verifies ConfigurationError when vertex platform requested without location."""
    with patch("backend_v2.llm.handler.get_settings") as mock_settings_fn:
        mock_settings = MagicMock()
        mock_settings.vertex_location = None
        mock_settings.use_mock_llm = False
        mock_settings_fn.return_value = mock_settings

        with pytest.raises(ConfigurationError) as exc_info:
            handler.fetch_all_available_models(platform=LLMPlatformType.VERTEX_AI.value, location=None)
        assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR


def test_fetch_all_available_models_empty_providers(handler: LLMHandler) -> None:
    """Verifies empty dict returned when active_providers resolves to empty."""
    with patch("backend_v2.llm.handler.get_settings") as mock_settings_fn:
        mock_settings = MagicMock()
        mock_settings.enabled_providers = []
        mock_settings.use_mock_llm = False
        mock_settings.vertex_location = "us-central1"
        mock_settings_fn.return_value = mock_settings

        assert handler.fetch_all_available_models(providers=[]) == {}


def test_fetch_all_available_models_multi_aggregation(handler: LLMHandler) -> None:
    """Verifies multi-provider aggregation invokes all requested providers."""
    with (
        patch.object(handler, "_fetch_vertex_models", return_value=["vertex_ai/model-a"]),
        patch.object(handler, "_fetch_ai_studio_models", return_value=["gemini/model-b"]),
        patch.object(handler, "_fetch_openai_models") as mock_openai,
        patch.object(handler, "_fetch_anthropic_models") as mock_anthropic,
    ):
        res = handler.fetch_all_available_models(
            providers=["vertex_ai", "ai_studio", "openai", "anthropic"], location="europe-north1"
        )
        assert "vertex_ai" in res
        assert "ai_studio" in res
        mock_openai.assert_called_once()
        mock_anthropic.assert_called_once()


# -----------------------------------------------------------------------------
# Expanded Coverage & Edge-Case Partitions
# -----------------------------------------------------------------------------


def test_fetch_vertex_models_publishers_and_non_strings(handler: LLMHandler) -> None:
    """Verifies candidate filtering across publishers and ignores non-string model elements."""
    mock_settings = MagicMock()
    mock_settings.discovery_location = "us-central1"
    mock_settings.llm_default_timeout_seconds = 5

    mock_resp = MagicMock()
    mock_resp.status_code = 200

    with (
        patch("google.auth.default", return_value=(MagicMock(), "proj-123")),
        patch(
            "litellm.model_list",
            [
                12345,  # non-string
                "vertex_ai/claude-3-5-sonnet",
                "vertex_ai/llama-3.1-70b",
                "vertex_ai/mistral-large",
            ],
        ),
        patch("requests.get", return_value=mock_resp),
    ):
        result = handler._fetch_vertex_models("europe-north1", mock_settings)
        assert len(result) == 3
        assert "vertex_ai/claude-3-5-sonnet" in result


def test_fetch_vertex_models_empty_validation_result(handler: LLMHandler) -> None:
    """Verifies warning logging when validation in target region returns 0 models."""
    mock_settings = MagicMock()
    mock_settings.discovery_location = "us-central1"

    with (
        patch("google.auth.default", return_value=(MagicMock(), "proj-123")),
        patch("litellm.model_list", ["vertex_ai/gemini-unsupported"]),
        patch("google.genai.Client") as mock_client_cls,
    ):
        mock_client = MagicMock()
        mock_client.models.get.side_effect = RuntimeError("Not found")
        mock_client_cls.return_value = mock_client

        result = handler._fetch_vertex_models("europe-north1", mock_settings)
        assert result == []


def test_fetch_vertex_models_unexpected_failure(handler: LLMHandler) -> None:
    """Verifies ServiceUnavailableError on unexpected discovery failure."""
    mock_settings = MagicMock()
    mock_settings.discovery_location = "us-central1"

    with (
        patch("google.auth.default", return_value=(MagicMock(), "proj-123")),
        patch("litellm.model_list", ["vertex_ai/gemini-2.5-pro"]),
        patch("backend_v2.llm.handler.ThreadPoolExecutor", side_effect=RuntimeError("Pool failure")),
    ):
        with pytest.raises(ServiceUnavailableError) as exc_info:
            handler._fetch_vertex_models("europe-north1", mock_settings)
        assert exc_info.value.error_code == ErrorCodes.MODEL_LIST_FAILED


def test_fetch_openai_models_live_discovery(handler: LLMHandler) -> None:
    """Verifies live OpenAI model filtering and candidate collection."""
    mock_settings = MagicMock()
    mock_settings.openai_api_key = "test-openai-key"

    m1 = MagicMock(id="gpt-4o")
    m2 = MagicMock(id="o1-mini")
    m3 = MagicMock(id="chatgpt-image-latest")  # excluded
    m4 = MagicMock(id="whisper-1")  # excluded
    m5 = MagicMock(id="openai/o3-mini")  # already prefixed

    mock_client = MagicMock()
    mock_client.models.list.return_value = [m1, m2, m3, m4, m5]

    models: dict[str, list[str] | str] = {}
    with patch("openai.OpenAI", return_value=mock_client):
        handler._fetch_openai_models(["openai"], mock_settings, models)
        discovered = models["openai"]
        assert isinstance(discovered, list)
        assert "openai/gpt-4o" in discovered
        assert "openai/o1-mini" in discovered
        assert "openai/o3-mini" in discovered
        assert "openai/chatgpt-image-latest" not in discovered


def test_fetch_anthropic_models_unexpected_error(handler: LLMHandler) -> None:
    """Verifies ServiceUnavailableError when unexpected exception occurs in Anthropic discovery."""
    mock_settings = MagicMock()
    type(mock_settings).anthropic_api_key = property(lambda self: (_ for _ in ()).throw(RuntimeError("SDK crash")))

    with pytest.raises(ServiceUnavailableError) as exc_info:
        handler._fetch_anthropic_models(["anthropic"], mock_settings, {})
    assert exc_info.value.error_code == ErrorCodes.MODEL_LIST_FAILED


def test_fetch_all_available_models_mock_early_returns(handler: LLMHandler) -> None:
    """Verifies early returns when mock is enabled or sole provider."""
    mock_settings = MagicMock()
    mock_settings.use_mock_llm = True
    mock_settings.vertex_location = "us-central1"

    with patch("backend_v2.llm.handler.get_settings", return_value=mock_settings):
        # use_mock_llm without mock in providers
        res1 = handler.fetch_all_available_models(providers=["vertex_ai"])
        assert "vertex_ai" in res1

        # single mock provider
        mock_settings.use_mock_llm = False
        res2 = handler.fetch_all_available_models(providers=["mock"])
        assert "vertex_ai" in res2


def test_fetch_all_available_models_multi_vertex_missing_location(handler: LLMHandler) -> None:
    """Verifies ConfigurationError when multi-provider includes vertex but location is missing."""
    mock_settings = MagicMock()
    mock_settings.use_mock_llm = False
    mock_settings.vertex_location = None
    mock_settings.enabled_providers = ["vertex_ai"]

    with patch("backend_v2.llm.handler.get_settings", return_value=mock_settings):
        with pytest.raises(ConfigurationError) as exc_info:
            handler.fetch_all_available_models(providers=["vertex_ai"], location=None)
        assert exc_info.value.error_code == ErrorCodes.CONFIGURATION_ERROR
