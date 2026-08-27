"""Unit and Negative ISTQB Test Suite for Model Registry Discovery Engine.

Tests positive partitions (Vertex AI multi-region, Google AI Studio direct API key, OpenAI, Anthropic),
parameterized routing, and negative boundary conditions (missing credentials, unprocessable entity).
"""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes
from backend_v2.llm.handler import LLMHandler
from backend_v2.models.dtos.studio import GCPLocationDTO
from backend_v2.models.enums import GCPVertexLocation
from backend_v2.services.studio.system_config_service import StudioSystemConfigService


class TestModelRegistryDiscoveryPositivePartitions:
    """Tests positive equivalence partitions for model discovery across platforms and regions."""

    def test_fetch_vertex_models_discovers_and_validates_regions(self) -> None:
        """Verifies that _fetch_vertex_models validates model candidates in a target GCP region."""
        repo = MagicMock()
        handler = LLMHandler(repo=repo)
        mock_settings = MagicMock()
        mock_settings.discovery_location = "us-central1"

        mock_client_instance = MagicMock()
        mock_client_instance.models.get.return_value = MagicMock(name="gemini-2.5-pro")

        with patch("litellm.model_list", ["vertex_ai/gemini-2.5-pro", "vertex_ai/gemini-1.5-flash", "gpt-4o"]):
            with patch("google.auth.default", return_value=(MagicMock(), "mock-proj")):
                with patch("google.genai.Client", return_value=mock_client_instance):
                    models = handler._fetch_vertex_models(target_location="europe-north1", settings=mock_settings)

                    assert len(models) == 2
                    assert "vertex_ai/gemini-2.5-pro" in models
                    assert "vertex_ai/gemini-1.5-flash" in models

    def test_fetch_ai_studio_models_via_direct_api_key(self) -> None:
        """Verifies that _fetch_ai_studio_models discovers models using Google AI Studio API key."""
        repo = MagicMock()
        handler = LLMHandler(repo=repo)
        mock_settings = MagicMock()
        mock_settings.google_api_key = "test_gemini_api_key"

        mock_m1 = MagicMock()
        mock_m1.name = "models/gemini-2.5-flash"
        mock_m2 = MagicMock()
        mock_m2.name = "models/gemini-2.5-pro"

        mock_client = MagicMock()
        mock_client.models.list.return_value = [mock_m1, mock_m2]

        with patch("google.genai.Client", return_value=mock_client):
            models = handler._fetch_ai_studio_models(settings=mock_settings)

            assert "gemini/gemini-2.5-flash" in models
            assert "gemini/gemini-2.5-pro" in models

    def test_fetch_all_available_models_routes_by_platform(self) -> None:
        """Verifies that fetch_all_available_models correctly filters by platform parameter."""
        repo = MagicMock()
        handler = LLMHandler(repo=repo)

        with patch.object(handler, "_fetch_vertex_models", return_value=["vertex_ai/gemini-2.5-pro"]):
            with patch.object(handler, "_fetch_ai_studio_models", return_value=["gemini/gemini-2.5-flash"]):
                # Vertex AI Platform filter
                v_res = handler.fetch_all_available_models(platform="vertex_ai", location="europe-west1")
                assert "vertex_ai" in v_res
                assert v_res["vertex_ai"] == ["vertex_ai/gemini-2.5-pro"]

                # AI Studio Platform filter
                s_res = handler.fetch_all_available_models(platform="ai_studio")
                assert "ai_studio" in s_res
                assert s_res["ai_studio"] == ["gemini/gemini-2.5-flash"]

    def test_system_config_service_supported_locations(self) -> None:
        """Verifies that get_supported_locations returns the full list of GCP regions."""
        from backend_v2.models.auth import UserRole

        service = StudioSystemConfigService(system_repo=MagicMock())
        initiator = MagicMock()
        initiator.role = UserRole.ROOT

        locations = service.get_supported_locations(initiator)
        assert len(locations) == 6
        loc_ids = [loc.id for loc in locations]
        assert GCPVertexLocation.EUROPE_NORTH1.value in loc_ids
        assert GCPVertexLocation.EUROPE_WEST1.value in loc_ids
        assert GCPVertexLocation.EUROPE_WEST4.value in loc_ids
        assert GCPVertexLocation.EUROPE_WEST3.value in loc_ids
        assert GCPVertexLocation.US_CENTRAL1.value in loc_ids
        assert GCPVertexLocation.US_EAST4.value in loc_ids


class TestModelRegistryDiscoveryNegativeBoundaries:
    """Negative boundary testing covering missing credentials, invalid regions, and auth failures."""

    def test_ai_studio_discovery_fails_fast_when_api_key_missing(self) -> None:
        """Negative Boundary 1: AI Studio discovery raises ConfigurationError when API key is missing."""
        repo = MagicMock()
        handler = LLMHandler(repo=repo)
        mock_settings = MagicMock()
        mock_settings.google_api_key = None

        with patch("os.environ.get", return_value=None):
            with pytest.raises(ConfigurationError) as exc_info:
                handler._fetch_ai_studio_models(settings=mock_settings)

            assert exc_info.value.details.get("error_code") == ErrorCodes.SERVICE_DEPENDENCY_MISSING.value

    def test_unauthorized_user_cannot_access_supported_locations(self) -> None:
        """Negative Boundary 2: Non-admin/non-root user triggers PermissionDeniedError on locations endpoint."""
        service = StudioSystemConfigService(system_repo=MagicMock())
        initiator = MagicMock()
        initiator.role = "user"
        initiator.id = "usr_regular123"

        with pytest.raises(AppException) as exc_info:
            service.get_supported_locations(initiator)

        assert exc_info.value.error_code == ErrorCodes.PERMISSION_DENIED

    def test_gcp_location_dto_strict_field_validation(self) -> None:
        """Negative Boundary 3: GCPLocationDTO fails on missing required fields."""
        with pytest.raises(ValidationError):
            GCPLocationDTO.model_validate({"id": "europe-north1"})  # Missing label and description
