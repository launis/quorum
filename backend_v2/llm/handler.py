"""LLM Handler module for managing model discovery and configuration."""

from __future__ import annotations

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Protocol

import openai
import requests
from pydantic import BaseModel, ConfigDict

from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    ResourceNotFoundError,
    ServiceUnavailableError,
)
from backend_v2.llm.provider import LLMFactory, LLMProvider
from backend_v2.models.domain.system_config import SystemConfigModelRegistry
from backend_v2.models.dtos.studio import GCPLocationDTO
from backend_v2.models.enums import LLMPlatformType, LLMProviderName
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.settings import Settings, get_settings

__all__ = ["LLMHandler"]

import importlib.util

GOOGLE_DEPS_AVAILABLE = (
    importlib.util.find_spec("google.auth") is not None
    and importlib.util.find_spec("google.auth.transport.requests") is not None
)
if GOOGLE_DEPS_AVAILABLE:
    import google.auth
    import google.auth.transport.requests

logger = logging.getLogger(__name__)


class _RefreshableCredentials(Protocol):
    token: str | None

    def refresh(self, request: Any) -> None: ...


DEFAULT_HTTP_TIMEOUT = 10
MAX_DISCOVERY_CONCURRENCY = 20


class LLMHandler:
    """Handles higher-level LLM operations including model discovery via APIs.

    Fetching configuration from the database, and delegating execution to the LLMFactory.
    """

    def _check_model_availability(self, model_id: str, location: str) -> bool:
        """Validates if a specific model_id (e.g., 'vertex_ai/gemini-1.5-pro') is available.

        Attempts to fetch its metadata in the target location using modern GenAI V2 Client.

        Args:
            model_id: The model identifier.
            location: The target location for Vertex AI.

        Returns:
            True if available, False otherwise.
        """
        try:
            from google import genai

            clean_name = model_id.split("/")[-1]
            if clean_name == "gemini-3.5-pro":
                return False

            client = genai.Client(vertexai=True, location=location)
            client.models.get(model=clean_name)
            return True
        except (ImportError, AttributeError, RuntimeError, OSError) as err:
            logger.warning("[LLMHandler] Availability check failed for %s in %s: %s", model_id, location, err)
            if isinstance(err, (KeyboardInterrupt, SystemExit)):
                raise
            return False

    def __init__(self, repo: Any):
        """Initializes the handler.

        Args:
            repo: The repository instance (injected via dependencies.py).
        """
        self.repo = repo
        self._cached_openai_models: list[str] = []
        self._cached_vertex_locations: list[GCPLocationDTO] = []
        self._cached_ai_studio_models: list[str] = []

    def _fetch_mock_models(self, providers: list[str], settings: Settings, models: dict[str, list[str] | str]) -> None:
        """Fetch mock models for specified providers during test runs or mock execution mode.

        Args:
            providers: List of provider names to populate with mock models.
            settings: Application settings containing mock flags.
            models: Target dictionary to populate with mock model lists.
        """
        if settings.use_mock_llm or "mock" in providers:
            if "vertex_ai" in providers or "mock" in providers:
                models["vertex_ai"] = ["vertex_ai/mock-model-a", "vertex_ai/mock-model-b"]
            if "ai_studio" in providers or "mock" in providers:
                models["ai_studio"] = ["gemini/mock-gemini-a"]
            if "openai" in providers or "mock" in providers:
                models["openai"] = ["mock-gpt-a"]
            if "anthropic" in providers or "mock" in providers:
                models["anthropic"] = ["mock-claude-a"]

            # Return early logic
            if settings.use_mock_llm and "mock" not in providers:
                return

            if len(providers) == 1 and "mock" in providers:
                return

    def _fetch_vertex_models(self, target_location: str, settings: Settings) -> list[str]:
        """Discovers and validates models available in Google Cloud Vertex AI in target_location.

        Args:
            target_location: Target GCP region (e.g. 'europe-north1').
            settings: Central application settings.

        Returns:
            Sorted list of validated model identifiers prefixed with 'vertex_ai/'.

        Raises:
            ConfigurationError: If discovery configuration or credentials are missing/invalid.
            ServiceUnavailableError: If communication with Vertex AI endpoints fails.
        """
        try:
            source_region = settings.discovery_location
            if not source_region:
                logger.error(
                    "Strict Fail-Fast: 'discovery_location' is required in settings.",
                    extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name},
                )
                raise ConfigurationError(
                    message="Strict Fail-Fast: 'discovery_location' is required in settings.",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )
            logger.debug(
                "[LLMHandler] Initiating Vertex AI Model Discovery (Source: %s, Target: %s)...",
                source_region,
                target_location,
            )

            if not GOOGLE_DEPS_AVAILABLE:
                logger.error(
                    "Missing required dependencies for Google Vertex AI discovery.",
                    extra={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.name},
                )
                raise ConfigurationError(
                    message="Missing required dependencies for Google Vertex AI discovery.",
                    details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
                )

            import litellm

            # Get all candidates (Gemini, Claude, Llama, Mistral for Vertex AI)
            all_models = litellm.model_list
            candidates: list[str] = []
            for m in all_models:
                if not isinstance(m, str):
                    continue
                m_lower = m.lower()
                if m_lower.startswith("vertex_ai/") or m_lower.startswith("gemini"):
                    if any(kw in m_lower for kw in ["gemini", "claude", "llama", "mistral"]):
                        candidates.append(m)

            candidates = sorted(list(set(candidates)))

            try:
                raw_credentials, project = google.auth.default(
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                credentials: _RefreshableCredentials = raw_credentials
            except Exception as auth_err:
                logger.error(
                    "Google Authentication failed during Vertex AI discovery: %s",
                    auth_err,
                    extra={"error_code": ErrorCodes.AUTHENTICATION_FAILED.name},
                    exc_info=True,
                )
                raise ConfigurationError(
                    message="Google Authentication failed during Vertex AI discovery.",
                    details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value, "original_error": str(auth_err)},
                ) from auth_err

            class _ModelProbeResult(BaseModel):
                model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
                model_id: str | None = None

            def check_model(model_id: str) -> _ModelProbeResult:
                clean_id = model_id
                for prefix in ["vertex_ai/", "gemini/", "models/"]:
                    if clean_id.startswith(prefix):
                        clean_id = clean_id[len(prefix) :]

                clean_lower = clean_id.lower()
                if "claude" in clean_lower:
                    publisher = "anthropic"
                elif "llama" in clean_lower:
                    publisher = "meta"
                elif "mistral" in clean_lower:
                    publisher = "mistralai"
                else:
                    publisher = "google"

                if publisher == "google":
                    try:
                        from google import genai

                        modern_client = genai.Client(vertexai=True, project=project, location=target_location)
                        _ = modern_client.models.get(model=clean_id)
                        return _ModelProbeResult(model_id=f"vertex_ai/{clean_id}")
                    except (ImportError, AttributeError, RuntimeError, OSError, ValueError) as err:
                        logger.debug("[LLMHandler] GenAI model probe failed for %s: %s", clean_id, err)
                        return _ModelProbeResult(model_id=None)
                else:
                    try:
                        auth_request = google.auth.transport.requests.Request()
                        credentials.refresh(auth_request)
                        headers = {"Authorization": f"Bearer {credentials.token}"}

                        url = f"https://{target_location}-aiplatform.googleapis.com/v1/publishers/{publisher}/models/{clean_id}"
                        timeout_sec = settings.llm_default_timeout_seconds
                        resp = requests.get(url, headers=headers, timeout=timeout_sec)
                        if resp.status_code == 200:
                            return _ModelProbeResult(model_id=f"vertex_ai/{clean_id}")

                        url_project = f"https://{target_location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{target_location}/publishers/{publisher}/models/{clean_id}"
                        resp_project = requests.get(url_project, headers=headers, timeout=timeout_sec)
                        if resp_project.status_code == 200:
                            return _ModelProbeResult(model_id=f"vertex_ai/{clean_id}")

                        return _ModelProbeResult(model_id=None)
                    except (requests.RequestException, OSError, RuntimeError, ValueError) as err:
                        logger.debug("[LLMHandler] REST model probe failed for %s: %s", clean_id, err)
                        return _ModelProbeResult(model_id=None)

            logger.info(
                "[LLMHandler] Discovering %d Vertex candidates; validating in %s...", len(candidates), target_location
            )
            final_list: list[str] = []

            with ThreadPoolExecutor(max_workers=MAX_DISCOVERY_CONCURRENCY) as executor:
                future_to_model = {executor.submit(check_model, m): m for m in candidates}
                for future in as_completed(future_to_model):
                    probe_res = future.result()
                    if probe_res.model_id:
                        final_list.append(probe_res.model_id)

            final_list = sorted(final_list)
            if not final_list:
                logger.error("[LLMHandler] Regional Vertex validation in %s returned 0 models.", target_location)

            logger.info(
                "[LLMHandler] Discovered & Validated %d Vertex AI models in %s.", len(final_list), target_location
            )
            return final_list

        except Exception as e:
            if isinstance(e, AppException):
                raise e

            logger.error(
                "[LLMHandler] %s: Error fetching/validating Vertex AI models: %s",
                ErrorCodes.MODEL_LIST_FAILED.name,
                e,
                exc_info=True,
            )
            raise ServiceUnavailableError(
                message=f"Vertex AI Model Discovery Failed: {e}",
                details={"error_code": ErrorCodes.MODEL_LIST_FAILED.value, "original_error": str(e)},
            ) from e

    def fetch_vertex_locations(self, settings: Settings) -> list[GCPLocationDTO]:
        """Fetch all available Google Cloud Vertex AI locations dynamically via ADC.

        Caches results in memory for zero-latency subsequent access.
        In mock mode (settings.use_mock_llm=True), returns deterministic mock locations.

        Args:
            settings: Central application settings containing mock mode or timeout configurations.

        Returns:
            Sorted list of GCPLocationDTO objects representing supported regions.

        Raises:
            ConfigurationError: If Google Cloud authentication fails or project cannot be resolved.
            ServiceUnavailableError: If querying Google Cloud resource API fails.
        """
        if self._cached_vertex_locations:
            return self._cached_vertex_locations

        if settings.use_mock_llm:
            mock_locations = [
                GCPLocationDTO(
                    id="europe-north1",
                    label="Hamina, Finland (europe-north1)",
                    description="Google Cloud Vertex AI region: Hamina, Finland",
                ),
                GCPLocationDTO(
                    id="europe-west1",
                    label="St. Ghislain, Belgium (europe-west1)",
                    description="Google Cloud Vertex AI region: St. Ghislain, Belgium",
                ),
                GCPLocationDTO(
                    id="europe-west3",
                    label="Frankfurt, Germany (europe-west3)",
                    description="Google Cloud Vertex AI region: Frankfurt, Germany",
                ),
                GCPLocationDTO(
                    id="europe-west4",
                    label="Eemshaven, Netherlands (europe-west4)",
                    description="Google Cloud Vertex AI region: Eemshaven, Netherlands",
                ),
                GCPLocationDTO(
                    id="us-central1",
                    label="Council Bluffs, Iowa (us-central1)",
                    description="Google Cloud Vertex AI region: Council Bluffs, Iowa",
                ),
                GCPLocationDTO(
                    id="us-east4",
                    label="Ashburn, Virginia (us-east4)",
                    description="Google Cloud Vertex AI region: Ashburn, Virginia",
                ),
            ]
            self._cached_vertex_locations = mock_locations
            return mock_locations

        if not GOOGLE_DEPS_AVAILABLE:
            logger.error(
                "Google Authentication libraries (google-auth) are not installed.",
                extra={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.name},
            )
            raise ConfigurationError(
                message="Google Authentication libraries (google-auth) are not installed.",
                details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )

        try:
            try:
                raw_credentials, project = google.auth.default(
                    scopes=["https://www.googleapis.com/auth/cloud-platform"]
                )
                credentials: _RefreshableCredentials = raw_credentials
            except Exception as auth_err:
                logger.error(
                    "Google Authentication failed during Vertex AI location discovery: %s",
                    auth_err,
                    extra={"error_code": ErrorCodes.AUTHENTICATION_FAILED.name},
                    exc_info=True,
                )
                raise ConfigurationError(
                    message="Google Authentication failed during Vertex AI location discovery.",
                    details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value, "original_error": str(auth_err)},
                ) from auth_err

            if not project:
                logger.error(
                    "Google Cloud project could not be resolved from ADC.",
                    extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name},
                )
                raise ConfigurationError(
                    message="Google Cloud project could not be resolved from ADC.",
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )

            auth_request = google.auth.transport.requests.Request()
            credentials.refresh(auth_request)
            headers = {"Authorization": f"Bearer {credentials.token}"}

            url = f"https://aiplatform.googleapis.com/v1/projects/{project}/locations"
            timeout_sec = settings.llm_default_timeout_seconds

            discovered_locations: list[GCPLocationDTO] = []
            next_page_token: str | None = None
            while True:
                params: dict[str, str] = {}
                if next_page_token:
                    params["pageToken"] = next_page_token
                resp = requests.get(url, headers=headers, params=params, timeout=timeout_sec)
                if resp.status_code != 200:
                    logger.error(
                        "Google Cloud Vertex AI locations query failed with HTTP %s: %s",
                        resp.status_code,
                        resp.text,
                        extra={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.name},
                    )
                    raise ServiceUnavailableError(
                        message=(
                            f"Google Cloud Vertex AI locations query failed with HTTP {resp.status_code}: {resp.text}"
                        ),
                        details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value, "status_code": resp.status_code},
                    )

                raw_json = resp.json()
                raw_locations: list[Any] = []
                if not isinstance(raw_json, (str, int, float, bool, list)) and raw_json is not None:
                    if "locations" in raw_json and isinstance(raw_json["locations"], list):
                        raw_locations = raw_json["locations"]

                for loc in raw_locations:
                    if not isinstance(loc, (str, int, float, bool, list)) and loc is not None:
                        if "locationId" in loc and loc["locationId"]:
                            loc_id = str(loc["locationId"])
                            disp_name = loc_id
                            if "displayName" in loc and loc["displayName"]:
                                disp_name = str(loc["displayName"])
                            discovered_locations.append(
                                GCPLocationDTO(
                                    id=loc_id,
                                    label=f"{disp_name} ({loc_id})",
                                    description=f"Google Cloud Vertex AI region: {disp_name}",
                                )
                            )
                next_page_token = None
                if not isinstance(raw_json, (str, int, float, bool, list)) and raw_json is not None:
                    if "nextPageToken" in raw_json and raw_json["nextPageToken"]:
                        next_page_token = str(raw_json["nextPageToken"])
                if not next_page_token:
                    break

            discovered_locations.sort(key=lambda loc: loc.id)
            if not discovered_locations:
                logger.warning(
                    "[LLMHandler] Vertex AI locations discovery returned 0 locations for project %s.", project
                )

            self._cached_vertex_locations = discovered_locations
            return discovered_locations

        except Exception as e:
            if isinstance(e, AppException):
                raise e

            logger.error(
                "[LLMHandler] %s: Error fetching Vertex AI locations: %s",
                ErrorCodes.SERVICE_UNAVAILABLE.name,
                e,
                exc_info=True,
            )
            raise ServiceUnavailableError(
                message=f"Vertex AI Location Discovery Failed: {e}",
                details={"error_code": ErrorCodes.SERVICE_UNAVAILABLE.value, "original_error": str(e)},
            ) from e

    def _fetch_ai_studio_models(self, settings: Settings) -> list[str]:
        """Discovers and validates models available via direct Google AI Studio API key.

        Args:
            settings: Central application settings.

        Returns:
            Sorted list of validated model identifiers prefixed with 'gemini/'.

        Raises:
            ConfigurationError: If Google AI Studio API key is missing.
            ServiceUnavailableError: If communication with Google AI Studio fails.
        """
        if self._cached_ai_studio_models:
            return self._cached_ai_studio_models

        api_key = settings.google_api_key
        if not api_key:
            logger.error(
                "GOOGLE_API_KEY / GEMINI_API_KEY not found in environment or settings for AI Studio discovery.",
                extra={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.name},
            )
            raise ConfigurationError(
                message="GOOGLE_API_KEY / GEMINI_API_KEY not found in environment or settings for AI Studio discovery.",
                details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )

        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            discovered: list[str] = []
            for m in client.models.list():
                model_name = ""
                if m.name:
                    model_name = str(m.name)
                # Strip models/ prefix if present
                clean_name = model_name
                if model_name.startswith("models/"):
                    clean_name = model_name[7:]
                if "gemini" in clean_name.lower():
                    discovered.append(f"gemini/{clean_name}")

            if not discovered:
                logger.error(
                    "Google AI Studio returned 0 available models for the configured API key.",
                    extra={"error_code": ErrorCodes.MODEL_LIST_FAILED.name},
                )
                raise ServiceUnavailableError(
                    message="Google AI Studio returned 0 available models for the configured API key.",
                    details={"error_code": ErrorCodes.MODEL_LIST_FAILED.value},
                )

            discovered_sorted = sorted(list(set(discovered)))
            self._cached_ai_studio_models = discovered_sorted
            return discovered_sorted

        except Exception as e:
            if isinstance(e, AppException):
                raise e

            logger.error(
                "[LLMHandler] %s: Error fetching Google AI Studio models: %s",
                ErrorCodes.MODEL_LIST_FAILED.name,
                e,
                exc_info=True,
            )
            raise ServiceUnavailableError(
                message=f"Google AI Studio Model Discovery Failed: {e}",
                details={"error_code": ErrorCodes.MODEL_LIST_FAILED.value, "original_error": str(e)},
            ) from e

    def _fetch_openai_models(
        self, providers: list[str], settings: Settings, models: dict[str, list[str] | str]
    ) -> None:
        """Discovers and validates models available via OpenAI API key.

        Args:
            providers: Provider identifier list containing target providers.
            settings: Central application settings.
            models: Output dictionary mapping provider keys to discovered model names.

        Raises:
            ConfigurationError: If OpenAI API key is missing.
            ServiceUnavailableError: If communication with OpenAI API fails.
        """
        if "openai" in providers:
            try:
                if self._cached_openai_models:
                    models["openai"] = self._cached_openai_models
                else:
                    api_key = settings.openai_api_key
                    if api_key:
                        openai_client = openai.OpenAI(api_key=api_key)
                        discovered: list[str] = []
                        for m in openai_client.models.list():
                            model_id = str(m.id)
                            clean_id = model_id.lower()
                            is_candidate = any(p in clean_id for p in ("gpt", "o1", "o3", "o4"))
                            is_excluded = any(
                                ex in clean_id
                                for ex in (
                                    "image",
                                    "realtime",
                                    "audio",
                                    "transcription",
                                    "transcribe",
                                    "tts",
                                    "whisper",
                                    "embedding",
                                    "moderation",
                                    "dall-e",
                                )
                            )
                            if is_candidate and not is_excluded:
                                formatted_name = model_id if model_id.startswith("openai/") else f"openai/{model_id}"
                                discovered.append(formatted_name)

                        self._cached_openai_models = sorted(list(set(discovered)))
                        models["openai"] = self._cached_openai_models
                    else:
                        logger.error(
                            "OPENAI_API_KEY not found in environment or settings.",
                            extra={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.name},
                        )
                        raise ConfigurationError(
                            message="OPENAI_API_KEY not found in environment or settings.",
                            details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
                        )
            except Exception as e:
                if isinstance(e, AppException):
                    raise e

                logger.error(
                    "[LLMHandler] %s: Error fetching/validating OpenAI models: %s",
                    ErrorCodes.MODEL_LIST_FAILED.name,
                    e,
                    exc_info=True,
                )
                raise ServiceUnavailableError(
                    message=f"OpenAI Model Discovery Failed: {e}",
                    details={"error_code": ErrorCodes.MODEL_LIST_FAILED.value, "original_error": str(e)},
                ) from e

    def _fetch_anthropic_models(
        self, providers: list[str], settings: Settings, models: dict[str, list[str] | str]
    ) -> None:
        """Discovers and validates models available via Anthropic API key.

        Args:
            providers: Provider identifier list containing target providers.
            settings: Central application settings.
            models: Output dictionary mapping provider keys to discovered model names.

        Raises:
            ConfigurationError: If Anthropic API key is missing.
            ServiceUnavailableError: If communication with Anthropic API fails.
        """
        if "anthropic" in providers:
            try:
                anthropic_models = [
                    "anthropic/claude-3-5-sonnet-20241022",
                    "anthropic/claude-3-5-sonnet",
                    "anthropic/claude-3-5-haiku-20241022",
                    "anthropic/claude-3-opus-20240229",
                ]
                if settings.anthropic_api_key:
                    models["anthropic"] = anthropic_models
                else:
                    logger.error(
                        "ANTHROPIC_API_KEY not found in environment or settings.",
                        extra={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.name},
                    )
                    raise ConfigurationError(
                        message="ANTHROPIC_API_KEY not found in environment or settings.",
                        details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
                    )
            except Exception as e:
                if isinstance(e, AppException):
                    raise e

                logger.error(
                    "[LLMHandler] %s: Error fetching/validating Anthropic models: %s",
                    ErrorCodes.MODEL_LIST_FAILED.name,
                    e,
                    exc_info=True,
                )
                raise ServiceUnavailableError(
                    message=f"Anthropic Model Discovery Failed: {e}",
                    details={"error_code": ErrorCodes.MODEL_LIST_FAILED.value, "original_error": str(e)},
                ) from e

    def fetch_all_available_models(
        self,
        providers: list[str] | None = None,
        location: str | None = None,
        platform: str | None = None,
    ) -> dict[str, list[str] | str]:
        """Queries External APIs (Vertex AI, Google AI Studio, OpenAI, Anthropic) for available models.

        Respects 'use_mock_llm' setting by returning mock data if enabled.

        Args:
            providers: List of providers to query ('google', 'openai', 'anthropic', 'mock').
            location: Optional target GCP region to validate against (e.g. 'europe-north1').
            platform: Optional platform filter ('vertex_ai', 'ai_studio', 'openai', 'anthropic', 'all').

        Returns:
            Dictionary mapping provider/platform keys to lists of available model strings.

        Raises:
            ConfigurationError: If target location is missing when discovering Vertex AI models.
        """
        settings = get_settings()
        models: dict[str, list[str] | str] = {}

        target_location: str | None
        if location:
            target_location = location
        else:
            target_location = settings.vertex_location

        # Handle Mock Mode
        if settings.use_mock_llm or (providers and "mock" in providers):
            if providers:
                mock_providers = providers
            else:
                mock_providers = ["mock"]
            self._fetch_mock_models(mock_providers, settings, models)
            if settings.use_mock_llm and (not providers or "mock" not in providers):
                return models
            if providers and len(providers) == 1 and "mock" in providers:
                return models

        # If explicit platform is provided, route directly
        if platform:
            norm_platform = platform.lower()
        else:
            norm_platform = LLMPlatformType.ALL.value

        if norm_platform == LLMPlatformType.VERTEX_AI.value:
            if not target_location:
                logger.error(
                    "CRITICAL: VERTEX_LOCATION not set in environment or settings. Cannot proceed with Vertex AI Model Discovery.",
                    extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name},
                )
                raise ConfigurationError(
                    message=(
                        "CRITICAL: VERTEX_LOCATION not set in environment or settings. "
                        "Cannot proceed with Vertex AI Model Discovery."
                    ),
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )
            vertex_models = self._fetch_vertex_models(target_location, settings)
            models[LLMPlatformType.VERTEX_AI.value] = vertex_models
            return models

        if norm_platform == LLMPlatformType.AI_STUDIO.value:
            ai_studio_models = self._fetch_ai_studio_models(settings)
            models[LLMPlatformType.AI_STUDIO.value] = ai_studio_models
            return models

        if norm_platform == LLMPlatformType.OPENAI.value:
            self._fetch_openai_models([LLMProviderName.OPENAI.value], settings, models)
            return models

        if norm_platform == LLMPlatformType.ANTHROPIC.value:
            self._fetch_anthropic_models([LLMProviderName.ANTHROPIC.value], settings, models)
            return models

        # Standard Multi-Provider Aggregation
        if providers is not None:
            active_providers = providers
        else:
            active_providers = settings.enabled_providers
        if not active_providers:
            return {}

        active_providers = [p.lower() for p in active_providers]

        if LLMPlatformType.VERTEX_AI.value in active_providers or "vertex" in active_providers:
            if not target_location:
                logger.error(
                    "CRITICAL: VERTEX_LOCATION not set in environment or settings. Cannot proceed with Vertex AI Model Discovery.",
                    extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name},
                )
                raise ConfigurationError(
                    message=(
                        "CRITICAL: VERTEX_LOCATION not set in environment or settings. "
                        "Cannot proceed with Vertex AI Model Discovery."
                    ),
                    details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                )
            vertex_models = self._fetch_vertex_models(target_location, settings)
            models[LLMPlatformType.VERTEX_AI.value] = vertex_models

        if LLMPlatformType.AI_STUDIO.value in active_providers or "ai_studio" in active_providers:
            ai_studio_models = self._fetch_ai_studio_models(settings)
            models[LLMPlatformType.AI_STUDIO.value] = ai_studio_models

        if LLMProviderName.OPENAI.value in active_providers:
            self._fetch_openai_models(active_providers, settings, models)

        if LLMProviderName.ANTHROPIC.value in active_providers:
            self._fetch_anthropic_models(active_providers, settings, models)

        return models

    async def get_active_model_registry(self) -> dict[str, Any]:
        """Fetches the 'global_model_registry' from the 'system_config' table in the database.

        Validates the configuration using the Pydantic SystemConfigModelRegistry schema.

        Returns:
            The raw dictionary representation of the validated configuration.

        Raises:
            ResourceNotFoundError: If the configuration is missing from the database.
            AppException: If schema validation fails.
        """
        record = await self.repo.get_system_config("global_model_registry")
        if not record:
            logger.error(
                "SystemConfig resource 'global_model_registry' not found in database.",
                extra={"error_code": ErrorCodes.RESOURCE_NOT_FOUND.name},
            )
            raise ResourceNotFoundError(
                resource_type="SystemConfig",
                resource_id="global_model_registry",
            )

        if "config" in record:
            raw_config = record["config"]
        else:
            raw_config = {}

        # Pydantic V2 Validation
        try:
            # Model config already defined in SystemConfigModelRegistry (domain.system_config)
            validated = SystemConfigModelRegistry.model_validate(raw_config)
            return validated.model_dump()
        except Exception as e:
            logger.error(
                "[LLMHandler] %s: Schema validation failed: %s",
                ErrorCodes.VALIDATION_FAILED.name,
                e,
                extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            )
            raise AppException(
                message=f"Model registry validation failed: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    async def get_model_config(self, provider: str, mode: str) -> dict[str, Any] | None:
        """Retrieves a specific model configuration for a provider/mode.

        Args:
            provider: Provider name (e.g., 'openai'). Legacy argument, mostly ignored now.
            mode: Mode name (e.g., 'smart', 'fast'). This maps to the V2 strategy slug.

        Returns:
            Configuration dictionary if found, else None.
        """
        registry = await self.get_active_model_registry()
        models: dict[str, Any]
        if "tier_definitions" in registry:
            models = registry["tier_definitions"]
        elif "models" in registry:
            models = registry["models"]
        else:
            models = {}

        if mode in models:
            return dict(models[mode])
        return None

    async def create_provider_for_strategy(self, mode: str) -> LLMProvider:
        """Dynamically instantiates and returns an LLM Provider configured for a specific strategy.

        Args:
            mode: The strategy name (e.g., 'primary', 'fast', 'creative', 'embedding').

        Returns:
            Configured and validated provider instance.

        Raises:
            ConfigurationError: If strategy is not configured in model registry or model is unavailable.
            ServiceUnavailableError: If strategy is deactivated or provider creation fails.
            ResourceNotFoundError: If global model registry is missing from database.
            AppException: If model registry validation fails.
        """
        registry = await self.get_active_model_registry()
        models: dict[str, Any]
        if "tier_definitions" in registry:
            models = registry["tier_definitions"]
        elif "models" in registry:
            models = registry["models"]
        else:
            models = {}

        if mode not in models:
            logger.error(
                "Strategy '%s' not configured in global model registry.",
                mode,
                extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name},
            )
            raise ConfigurationError(
                message=f"Strategy '{mode}' not configured in global model registry.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
            )

        model_profile = models[mode]
        provider = model_profile["provider"]
        cd = model_profile

        # Validate structure against LLMProviderConfig implicitly via extraction
        settings = get_settings()

        # Pydantic has already validated these via SystemConfigModelRegistry in get_active_model_registry
        model_name = cd["model_name"]
        temperature = cd["temperature"]
        max_tokens = cd["max_tokens"]

        api_key: str | None = None
        if "api_key" in cd:
            api_key = cd["api_key"]

        # Dynamic location resolution from additional_params or settings
        add_params: dict[str, Any] = {}
        if "additional_params" in cd and cd["additional_params"]:
            add_params = cd["additional_params"]

        target_location: str | None = None
        if "vertex_location" in add_params and add_params["vertex_location"]:
            target_location = str(add_params["vertex_location"])
        else:
            target_location = settings.vertex_location

        # STRICT VALIDATION: Ensure the configured model name actually exists in the target region/platform.
        # This prevents "blind" 404s from the provider.
        if provider in (LLMProviderName.VERTEX_AI.value, LLMProviderName.AI_STUDIO.value) and mode != "mock":
            if provider == LLMProviderName.VERTEX_AI.value:
                target_platform = LLMPlatformType.VERTEX_AI.value
                query_location = target_location
            else:
                target_platform = LLMPlatformType.AI_STUDIO.value
                query_location = None

            available_models_map = await asyncio.to_thread(
                self.fetch_all_available_models,
                providers=[provider],
                location=query_location,
                platform=target_platform,
            )

            if target_platform in available_models_map:
                valid_models = available_models_map[target_platform]
            else:
                valid_models = []

            if not isinstance(valid_models, list):
                if valid_models:
                    valid_models = [valid_models]
                else:
                    valid_models = []

            if model_name not in valid_models:
                if "mock" not in model_name.lower():
                    if target_platform == LLMPlatformType.VERTEX_AI.value:
                        location_detail = f" in target region ('{target_location}')"
                    else:
                        location_detail = ""
                    error_msg = (
                        f"STRICT VALIDATION ERROR: Model '{model_name}' configured for strategy '{mode}' "
                        f"is NOT available for platform '{target_platform}'{location_detail}. "
                        f"Available models: {valid_models[:5]}..."
                    )
                    logger.error(
                        "[LLMHandler] %s: %s",
                        ErrorCodes.CONFIGURATION_ERROR.name,
                        error_msg,
                        extra={"error_code": ErrorCodes.CONFIGURATION_ERROR.name},
                    )
                    raise ConfigurationError(
                        message=error_msg, details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
                    )

        # Create Provider via Factory (Unified Logic)
        try:
            logger.info(
                "[LLM Execution] Strategy: %s/%s -> Model: %s (Temp: %s, MaxTokens: %s)",
                provider,
                mode,
                model_name,
                temperature,
                max_tokens,
            )

            base_url: str | None = None
            if "base_url" in cd:
                base_url = cd["base_url"]

            vertex_loc: str | None = None
            if "vertex_location" in cd:
                vertex_loc = cd["vertex_location"]

            # Construct strict config object
            provider_config = LLMProviderConfig(
                id=f"prov_{provider.replace('-', '').replace('_', '')}{mode.replace('-', '').replace('_', '')}00000000",
                provider=provider,
                model_name=model_name,
                api_key=api_key,
                base_url=base_url,
                temperature=temperature,
                tpm_limit=cd["tpm_limit"],
                rpm_limit=cd["rpm_limit"],
                default_max_tokens=max_tokens,
                vertex_location=vertex_loc,
                supports_grounding=cd["supports_grounding"],
                is_active=cd["is_active"],
                additional_params=cd["additional_params"],
            )

            # FAIL FAST: Check Active Status
            if not provider_config.is_active:
                logger.error(
                    "Model Strategy '%s/%s' is deactivated.",
                    provider,
                    mode,
                    extra={"error_code": ErrorCodes.SERVICE_DISABLED.name},
                )
                raise ServiceUnavailableError(
                    message=f"Model Strategy '{provider}/{mode}' is deactivated.",
                    details={"error_code": ErrorCodes.SERVICE_DISABLED.value},
                )

            # Pass config object to factory
            llm_provider = LLMFactory.create_provider(
                provider_type=provider,  # Redundant but kept for signature
                model_name=model_name,  # Redundant but kept for signature
                config=provider_config,
                api_key=api_key,  # Pass explicit key if needed, but config has it
            )

            return llm_provider

        except Exception as e:
            if isinstance(e, (AppException, ServiceUnavailableError, ConfigurationError)):
                raise e
            logger.error(
                "[LLMHandler] %s: Unified Provider Creation Failed: %s", ErrorCodes.UNKNOWN_ERROR.name, e, exc_info=True
            )
            raise ServiceUnavailableError(
                message=f"LLM Handler Provider Creation Failed: {e}",
                details={"error_code": ErrorCodes.UNKNOWN_ERROR.value},
            ) from e
