"""LLM Handler module for managing model discovery and configuration."""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import openai
import requests

from backend_v2.exceptions import (
    AppException,
    ConfigurationError,
    ErrorCodes,
    ResourceNotFoundError,
    ServiceUnavailableError,
)
from backend_v2.llm.provider import LLMFactory
from backend_v2.models.enums import LLMPlatformType, LLMProviderName
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.models.v2_core import SystemConfigModelRegistry
from backend_v2.settings import get_settings

try:
    import google.auth
    import google.auth.transport.requests

    GOOGLE_DEPS_AVAILABLE = True
except ImportError:
    GOOGLE_DEPS_AVAILABLE = False

logger = logging.getLogger(__name__)


class LLMHandler:
    """Handles higher-level LLM operations including model discovery via APIs.

    Fetching configuration from the database, and delegating execution to the LLMFactory.
    """

    def _check_model_availability(self, model_id: str, location: str) -> bool:
        """Validates if a specific model_id (e.g., 'vertex_ai/gemini-1.5-pro') is available.

        Attempts to fetch its metadata in the target location using modern GenAI V2 Client.

        Args:
            model_id (str): The model identifier.
            location (str): The target location for Vertex AI.

        Returns:
            bool: True if available, False otherwise.
        """
        try:
            from google import genai

            clean_name = model_id.split("/")[-1]
            if clean_name == "gemini-3.5-pro":
                return False

            client = genai.Client(vertexai=True, location=location)
            client.models.get(model=clean_name)
            return True
        except Exception:
            return False

    def __init__(self, repo: Any):
        """Initializes the handler.

        Args:
            repo (Any): The IWorkflowRepository instance (injected via dependencies.py).
        """
        self.repo = repo
        self._cached_google_models: list[str] = []
        self._cached_openai_models: list[str] = []

    def _fetch_mock_models(self, providers: list[str], settings: Any, models: dict[str, list[str] | str]) -> None:
        if settings.use_mock_llm or "mock" in providers:
            if "google" in providers or "vertex_ai" in providers or "ai_studio" in providers or "mock" in providers:
                models["google"] = ["mock-model-a", "mock-model-b"]
            if "openai" in providers or "mock" in providers:
                models["openai"] = ["mock-gpt-a"]
            if "anthropic" in providers or "mock" in providers:
                models["anthropic"] = ["mock-claude-a"]

            # Return early logic
            if settings.use_mock_llm and "mock" not in providers:
                return

            if len(providers) == 1 and "mock" in providers:
                return

    def _fetch_vertex_models(self, target_location: str, settings: Any) -> list[str]:
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
                credentials, project = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            except Exception as auth_err:
                raise ConfigurationError(
                    message="Google Authentication failed during Vertex AI discovery.",
                    details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value, "original_error": str(auth_err)},
                ) from auth_err

            def check_model(model_id: str) -> str | None:
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
                        return f"vertex_ai/{clean_id}"
                    except Exception:
                        return None
                else:
                    try:
                        auth_request = google.auth.transport.requests.Request()
                        credentials.refresh(auth_request)  # type: ignore[no-untyped-call]
                        headers = {"Authorization": f"Bearer {credentials.token}"}

                        url = f"https://{target_location}-aiplatform.googleapis.com/v1/publishers/{publisher}/models/{clean_id}"
                        resp = requests.get(url, headers=headers, timeout=5)
                        if resp.status_code == 200:
                            return f"vertex_ai/{clean_id}"

                        url_project = f"https://{target_location}-aiplatform.googleapis.com/v1/projects/{project}/locations/{target_location}/publishers/{publisher}/models/{clean_id}"
                        resp_project = requests.get(url_project, headers=headers, timeout=5)
                        if resp_project.status_code == 200:
                            return f"vertex_ai/{clean_id}"

                        return None
                    except Exception:
                        return None

            logger.info(
                "[LLMHandler] Discovering %d Vertex candidates; validating in %s...", len(candidates), target_location
            )
            final_list: list[str] = []

            with ThreadPoolExecutor(max_workers=20) as executor:
                future_to_model = {executor.submit(check_model, m): m for m in candidates}
                for future in as_completed(future_to_model):
                    result = future.result()
                    if result:
                        final_list.append(result)

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

    def _fetch_ai_studio_models(self, settings: Any) -> list[str]:
        """Discovers and validates models available via direct Google AI Studio API key.

        Args:
            settings: Central application settings.

        Returns:
            Sorted list of validated model identifiers prefixed with 'gemini/'.

        Raises:
            ConfigurationError: If Google AI Studio API key is missing.
            ServiceUnavailableError: If communication with Google AI Studio fails.
        """
        api_key = settings.google_api_key
        if not api_key:
            import os

            api_key = os.environ.get("GEMINI_API_KEY")

        if not api_key:
            raise ConfigurationError(
                message="GOOGLE_API_KEY / GEMINI_API_KEY not found in environment or settings for AI Studio discovery.",
                details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
            )

        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            discovered: list[str] = []
            for m in client.models.list():
                model_name = getattr(m, "name", None) or ""  # noqa: QGR001 [REASON: Google GenAI Model SDK name attribute inspection]
                # Strip models/ prefix if present
                clean_name = model_name[7:] if model_name.startswith("models/") else model_name
                if "gemini" in clean_name.lower():
                    discovered.append(f"gemini/{clean_name}")

            if not discovered:
                # Fallback to standard known Gemini models in LiteLLM catalog
                import litellm

                for lm in litellm.model_list:
                    if isinstance(lm, str) and lm.startswith("gemini/") and "gemini" in lm.lower():
                        discovered.append(lm)

            return sorted(list(set(discovered)))

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

    def _fetch_google_models(
        self, providers: list[str], target_location: str, settings: Any, models: dict[str, list[str] | str]
    ) -> None:
        if "google" in providers or "vertex_ai" in providers:
            final_list = self._fetch_vertex_models(target_location, settings)
            models["google"] = final_list
            models["vertex_ai"] = final_list
            self._cached_google_models = final_list

    def _fetch_openai_models(self, providers: list[str], settings: Any, models: dict[str, list[str] | str]) -> None:
        if "openai" in providers:
            try:
                if self._cached_openai_models:
                    models["openai"] = self._cached_openai_models
                else:
                    api_key = settings.openai_api_key
                    if api_key:
                        openai_client = openai.OpenAI(api_key=api_key)
                        for m in openai_client.models.list():
                            if "gpt" in m.id:
                                self._cached_openai_models.append(m.id)
                        models["openai"] = self._cached_openai_models
                    else:
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

    def _fetch_anthropic_models(self, providers: list[str], settings: Any, models: dict[str, list[str] | str]) -> None:
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
        """
        settings = get_settings()
        models: dict[str, list[str] | str] = {}

        # Resolve Target Location from Settings or argument
        target_location = location if location else settings.vertex_location
        if not target_location:
            raise ValueError(
                "CRITICAL: VERTEX_LOCATION not set in environment or settings. Cannot proceed with Model Discovery."
            )

        # Handle Mock Mode
        if settings.use_mock_llm or (providers and "mock" in providers):
            self._fetch_mock_models(providers or ["mock"], settings, models)
            if settings.use_mock_llm and (not providers or "mock" not in providers):
                return models
            if providers and len(providers) == 1 and "mock" in providers:
                return models

        # If explicit platform is provided, route directly
        norm_platform = platform.lower() if platform else LLMPlatformType.ALL.value

        if norm_platform == LLMPlatformType.VERTEX_AI.value:
            vertex_models = self._fetch_vertex_models(target_location, settings)
            models[LLMPlatformType.VERTEX_AI.value] = vertex_models
            models[LLMProviderName.GOOGLE.value] = vertex_models
            return models

        if norm_platform == LLMPlatformType.AI_STUDIO.value:
            ai_studio_models = self._fetch_ai_studio_models(settings)
            models[LLMPlatformType.AI_STUDIO.value] = ai_studio_models
            models[LLMProviderName.GOOGLE.value] = ai_studio_models
            return models

        if norm_platform == LLMPlatformType.OPENAI.value:
            self._fetch_openai_models([LLMProviderName.OPENAI.value], settings, models)
            return models

        if norm_platform == LLMPlatformType.ANTHROPIC.value:
            self._fetch_anthropic_models([LLMProviderName.ANTHROPIC.value], settings, models)
            return models

        # Standard Multi-Provider Aggregation
        active_providers = providers or settings.enabled_providers
        if not active_providers:
            return {}

        active_providers = [p.lower() for p in active_providers]

        if LLMProviderName.GOOGLE.value in active_providers or LLMProviderName.VERTEX_AI.value in active_providers:
            self._fetch_google_models(active_providers, target_location, settings, models)

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
            ResourceNotFoundError: If the configuration is missing.
            AppException: If validation fails.
        """
        record = await self.repo.get_system_config("global_model_registry")
        if not record:
            raise ResourceNotFoundError(
                resource_type="SystemConfig",
                resource_id="global_model_registry",
            )

        raw_config = record["config"] if "config" in record else {}

        # Pydantic V2 Validation
        try:
            # Model config already defined in SystemConfigModelRegistry (v2_core.py)
            validated = SystemConfigModelRegistry.model_validate(raw_config)
            return validated.model_dump()
        except Exception as e:
            logger.error("[LLMHandler] %s: Schema validation failed: %s", ErrorCodes.VALIDATION_FAILED.name, e)
            raise AppException(
                message=f"Model registry validation failed: {e}",
                status_code=500,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            ) from e

    async def get_model_config(self, provider: str, mode: str) -> dict[str, Any] | None:
        """Retrieves a specific model configuration for a provider/mode.

        Args:
            provider (str): Provider name (e.g., 'openai'). Legacy argument, mostly ignored now.
            mode (str): Mode name (e.g., 'smart', 'fast'). This maps to the V2 strategy slug.

        Returns:
            Optional[Dict[str, Any]]: Configuration dictionary if found, else None.
        """
        registry = await self.get_active_model_registry()
        models = registry["models"] if "models" in registry else {}
        config = models[mode] if mode in models else None

        if config:
            return dict(config)
        return None

    async def create_provider_for_strategy(self, mode: str) -> Any:
        """Dynamically instantiates and returns an LLM Provider configured for a specific strategy.

        Args:
            mode (str): The strategy name (e.g., 'primary', 'fast', 'creative', 'embedding').

        Returns:
            LLMProvider: Configured and validated provider instance.

        Raises:
            AppException: If configuration is invalid, missing, or model is not available.
        """
        registry = await self.get_active_model_registry()
        models = registry["models"] if "models" in registry else {}

        if mode not in models:
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
        api_key = cd["api_key"] if "api_key" in cd else None

        # Dynamic location resolution from additional_params or settings
        add_params = cd["additional_params"] if "additional_params" in cd and cd["additional_params"] else {}
        target_location = (
            add_params["vertex_location"]
            if "vertex_location" in add_params and add_params["vertex_location"]
            else settings.vertex_location
        )

        # STRICT VALIDATION: Ensure the configured model name actually exists in the target region.
        # This prevents "blind" 404s from the provider.
        if provider in (LLMProviderName.GOOGLE.value, LLMProviderName.VERTEX_AI.value) and mode != "mock":
            available_models_map = await asyncio.to_thread(
                self.fetch_all_available_models,
                providers=[provider],
                location=target_location,
                platform=LLMPlatformType.VERTEX_AI.value
                if model_name.startswith("vertex_ai/")
                else (LLMPlatformType.AI_STUDIO.value if model_name.startswith("gemini/") else None),
            )

            valid_models = available_models_map[provider] if provider in available_models_map else []
            if not isinstance(valid_models, list):
                valid_models = [valid_models] if valid_models else []

            if model_name not in valid_models:
                if "mock" not in model_name.lower():
                    error_msg = (
                        f"STRICT VALIDATION ERROR: Model '{model_name}' configured for strategy '{mode}' "
                        f"is NOT available in the target region ('{target_location}'). "
                        f"Available models: {valid_models[:5]}..."
                    )
                    logger.error("[LLMHandler] %s: %s", ErrorCodes.CONFIGURATION_ERROR.name, error_msg)
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

            # Construct strict config object
            provider_config = LLMProviderConfig(
                id=f"prov_{provider.replace('-', '').replace('_', '')}{mode.replace('-', '').replace('_', '')}00000000",
                provider=provider,
                model_name=model_name,
                api_key=api_key,
                base_url=cd.get("base_url"),
                temperature=temperature,
                tpm_limit=cd["tpm_limit"],
                rpm_limit=cd["rpm_limit"],
                default_max_tokens=max_tokens,
                vertex_location=cd.get("vertex_location"),
                supports_grounding=cd["supports_grounding"],
                is_active=cd["is_active"],
                additional_params=cd["additional_params"],
            )

            # FAIL FAST: Check Active Status
            if not provider_config.is_active:
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
