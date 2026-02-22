"""LLM Handler module for managing model discovery and configuration."""

import logging
import os
from typing import Any

import openai
from tinydb import Query

from backend.exceptions import ConfigurationError, ErrorCodes, ServiceUnavailableError
from backend.llm.provider import LLMFactory
from backend.models.llm import LLMProviderConfig
from backend.settings import get_settings

logger = logging.getLogger(__name__)


class LLMHandler:
    """Handles higher-level LLM operations including model discovery via APIs.

    Fetching configuration from the database, and delegating execution to the LLMFactory.
    """

    def _check_model_availability(self, model_id: str, location: str) -> bool:
        """Validates if a specific model_id (e.g., 'vertex_ai/gemini-1.5-pro') is available.

        Attempts to fetch its metadata in the target location.
        """
        try:
            # Dynamic import to avoid top-level crash if library missing
            from google.api_core import client_options as g_client_options
            from google.cloud import aiplatform_v1

            api_endpoint = f"{location}-aiplatform.googleapis.com"
            client = aiplatform_v1.ModelGardenServiceClient(
                client_options=g_client_options.ClientOptions(api_endpoint=api_endpoint)
            )

            # The name format for retrieving is "publishers/google/models/{model_name}"
            # model_id input is usually "vertex_ai/{model_name}" or just "{model_name}" logic
            clean_name = model_id.split("/")[-1]
            resource_name = f"publishers/google/models/{clean_name}"

            # We use get_publisher_model to check existence
            client.get_publisher_model(name=resource_name)
            return True
        except Exception:
            # If it fails (404 or other error), we assume unavailable
            return False

    def __init__(self, db_client: Any):
        """Initializes the handler.

        Args:
            db_client (Any): Database client for accessing system config.

        """
        self.db_client = db_client
        self._cached_google_models: list[str] = []
        self._cached_openai_models: list[str] = []

    def fetch_all_available_models(
        self, providers: list[str] | None = None, location: str | None = None
    ) -> dict[str, list[str] | str]:
        """Queries External APIs (Vertex AI, OpenAI) for available models.

        Respects 'use_mock_llm' setting by returning mock data if enabled.

        Args:
            providers (List[str]): List of providers to query ('google', 'openai', 'mock'). Defaults to all.
            location (str | None): Optional target location to validate against. Defaults to settings value.

        Logic for Google:
        1. Fetch Master List from 'us-central1' (Model Garden root).
        2. Iterate and Validate against Target Location (if different from us-central1).

        """
        settings = get_settings()
        models: dict[str, list[str] | str] = {}

        # Resolve Target Location from Settings (Robust .env loading)
        target_location = location if location else settings.vertex_location
        if not target_location:
            raise ValueError(
                "CRITICAL: VERTEX_LOCATION not set in environment or settings. Cannot proceed with Model Discovery."
            )

        # Normalize providers list
        if not providers:
            # Zero-Fallback: We do not assume default providers.
            # Use configured providers from settings.
            providers = settings.enabled_providers
            if not providers:
                # If strictly nothing executed, we return empty.
                return {}

        providers = [p.lower() for p in providers]
        # Strict checking: Only add mock if explicitly requested
        if "mock" in providers or settings.use_mock_llm:
            # Only then we consider mock logic
            pass

        # --- MOCK ---
        if settings.use_mock_llm or "mock" in providers:
            if "google" in providers or "mock" in providers:
                models["google"] = ["mock-model-a", "mock-model-b"]
            if "openai" in providers or "mock" in providers:
                models["openai"] = ["mock-gpt-a"]

            # Return early logic
            if settings.use_mock_llm and "mock" not in providers:
                return models  # Should matching mock logic, but simplifying

            if len(providers) == 1 and "mock" in providers:
                return models

        # --- GOOGLE (Vertex AI) ---
        if "google" in providers:
            try:
                # 1. Discovery (Source of Truth: LiteLLM / "West" equivalent)
                # We log the source region for auditability.
                source_region = settings.discovery_location or "us-west1"
                logger.debug(f"[LLMHandler] Initiating Model Discovery (Source: {source_region})...")

                try:
                    from concurrent.futures import ThreadPoolExecutor, as_completed

                    import google.auth
                    import litellm
                    import requests
                    from google.auth.transport.requests import Request as GRequest
                except ImportError as ie:
                    from backend.exceptions import ConfigurationError, ErrorCodes

                    raise ConfigurationError(
                        message="Missing required dependencies for Google discovery.",
                        details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING, "original_error": str(ie)},
                    ) from ie

                # Get all candidates
                all_models = litellm.model_list
                candidates = []
                for m in all_models:
                    if not isinstance(m, str):
                        continue
                    m_lower = m.lower()
                    if "gemini" in m_lower:
                        # We prefer vertex_ai prefix, but keep raw 'gemini' if valid
                        if m_lower.startswith("vertex_ai/") or m_lower.startswith("gemini"):
                            candidates.append(m)

                candidates = sorted(list(set(candidates)))

                # 2. Validation (Target Region: Finland / europe-north1)
                final_list = []

                # Setup Auth (once)
                try:
                    credentials, project = google.auth.default(
                        scopes=["https://www.googleapis.com/auth/cloud-platform"]
                    )
                    credentials.refresh(GRequest())
                    token = credentials.token
                except Exception as auth_err:
                    from backend.exceptions import ConfigurationError, ErrorCodes

                    # Fail Fast: If we can't authenticate, we can't discover or use models.
                    raise ConfigurationError(
                        message="Google Authentication failed during discovery.",
                        details={"error_code": ErrorCodes.AUTHENTICATION_FAILED, "original_error": str(auth_err)},
                    ) from auth_err

                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

                def check_model(model_id: str) -> str | None:
                    # Clean model ID for API call (strip prefixes)
                    # We want the distinct model ID, e.g. "gemini-1.5-pro"
                    # Input could be "vertex_ai/gemini-1.5-pro", "gemini/gemini-1.5-pro", or just "gemini-1.5-pro"

                    clean_id = model_id
                    for prefix in ["vertex_ai/", "gemini/", "models/"]:
                        if clean_id.startswith(prefix):
                            clean_id = clean_id[len(prefix) :]

                    # Endpoint: https://{location}-aiplatform.googleapis.com/v1/publishers/google/models/{model}
                    url = f"https://{target_location}-aiplatform.googleapis.com/v1/publishers/google/models/{clean_id}"

                    try:
                        resp = requests.get(url, headers=headers, timeout=5)
                        if resp.status_code == 200:
                            # Normalize return value to "vertex_ai/" prefix which is what our "google" provider implies
                            return f"vertex_ai/{clean_id}"
                        return None
                    except Exception:
                        return None

                # Parallel Validation
                logger.info(f"[LLMHandler] discovering {len(candidates)} models; validating in {target_location}...")

                with ThreadPoolExecutor(max_workers=20) as executor:
                    future_to_model = {executor.submit(check_model, m): m for m in candidates}
                    for future in as_completed(future_to_model):
                        result = future.result()
                        if result:
                            final_list.append(result)

                final_list = sorted(final_list)

                # Fallback if validation fails hard (empty list)
                if not final_list:
                    # STRICT: We do not fallback. We return empty.
                    # Caller (frontend) decides if empty is an error (it probably is).
                    # But if we genuinely found nothing, we shouldn't lie.
                    logger.error(f"[LLMHandler] Regional validation in {target_location} returned 0 models.")
                    final_list = []

                models["google"] = final_list
                self._cached_google_models = final_list

                logger.info(
                    f"[LLMHandler] Discovered & Validated {len(final_list)} Gemini models in {target_location}."
                )

            except Exception as e:
                # If it's already an AppException, re-raise
                from backend.exceptions import AppException, ErrorCodes, ServiceUnavailableError

                if isinstance(e, AppException):
                    raise e

                # Otherwise wrap in ServiceUnavailable (upstream failure)
                logger.error(f"Error fetching/validating Google models: {e}")

                # STRICT: Do not return error strings. Raise.
                raise ServiceUnavailableError(
                    message=f"Google Model Discovery Failed: {e}",
                    details={"error_code": ErrorCodes.MODEL_LIST_FAILED, "original_error": str(e)},
                ) from e

        # --- OPENAI ---
        if "openai" in providers:
            try:
                if self._cached_openai_models:
                    models["openai"] = self._cached_openai_models
                else:
                    api_key = os.getenv("OPENAI_API_KEY") or settings.openai_api_key
                    if api_key:
                        openai_client = openai.OpenAI(api_key=api_key)
                        for m in openai_client.models.list():
                            if "gpt" in m.id:
                                self._cached_openai_models.append(m.id)
                        models["openai"] = self._cached_openai_models
                    else:
                        raise ConfigurationError(
                            message="OPENAI_API_KEY not found in environment or settings.",
                            details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING},
                        )
            except Exception as e:
                # STRICT TYPE SAFETY: Do not assign string error messages to a Dict[str, List[str]]
                logger.error(f"Error fetching OpenAI models: {e}")
                # We return empty list for OpenAI if it fails, or we could raise.
                # Given 'Fail Fast' for keys, if we are here it might be a network error or other.
                # But we must satisfy the return type.
                models["openai"] = []
                # If we want to communicate error, we can't do it via this typed dict field.
                # The caller should handle emptiness or we relies on logs.

        return models

    def get_active_model_registry(self) -> dict[str, Any]:
        """Fetches the 'global_model_registry' from the 'system_config' table in the database.

        Returns:
            Dict[str, Any]: configuration mapping.
        """
        try:
            table = self.db_client.table("system_config")

            Result = Query()
            results = table.search(Result.type == "model_registry")

            if results:
                return results[0].get("models", {})
            return {}
        except Exception as e:
            logger.error(f"Failed to get registry: {e}")
            return {}

    def get_model_config(self, provider: str, mode: str) -> dict[str, Any] | None:
        """Retrieves a specific model configuration for a provider/mode.

        Args:
            provider (str): Provider name (e.g., 'openai').
            mode (str): Mode name (e.g., 'smart').

        Returns:
            Optional[Dict[str, Any]]: Configuration dictionary if found, else None.

        """
        registry = self.get_active_model_registry()

        # Try nested structure first (new schema)
        config = None
        if isinstance(registry.get(provider), dict):
            provider_config = registry[provider]
            if isinstance(provider_config, dict):
                config = provider_config.get(mode)

        if config:
            return config
        return None

    async def call_llm(self, provider: str, mode: str, prompt: str, system_instruction: str | None = None) -> str:
        """High-level helper to call an LLM (Ad-hoc usage).

        Resolves configuration from DB based on provider/mode and delegates to LLMFactory.

        Args:
            provider (str): 'gemini' or 'openai' or 'mock'.
            mode (str): 'fast', 'smart', etc.
            prompt (str): Text prompt.
            system_instruction (Optional[str]): System context.

        Returns:
            str: Generated text response.

        """
        settings = get_settings()
        config = self.get_model_config(provider, mode)

        if not config:
            raise ValueError(f"STRICT CONFIG ERROR: No configuration found for strategy '{provider}/{mode}' ")

        # Handle if config is Pydantic model or dict
        cd: dict[str, Any]
        if hasattr(config, "model_dump"):
            # Cast Any to something with model_dump? Mypy hates ambiguous "hasattr".
            # Assume it's a dict unless proven otherwise, but get_model_config returns dict.
            # If it returns BaseModel, annotation should say so.
            # For now, coerce.
            cd = config.model_dump()
        elif isinstance(config, dict):
            cd = config
        else:
            # Fallback
            cd = dict(config)  # type: ignore

        model_name = cd.get("model_name")
        if not model_name:
            raise ValueError(f"STRICT CONFIG ERROR: Strategy '{provider}/{mode}' exists but describes no 'model_name'.")

        temperature = cd.get("temperature")
        if temperature is None:
            raise ConfigurationError(
                message=f"STRICT CONFIG ERROR: Strategy '{provider}/{mode}' is missing required 'temperature'.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )

        max_tokens = cd.get("max_tokens")
        if max_tokens is None:
            raise ConfigurationError(
                message=f"STRICT CONFIG ERROR: Strategy '{provider}/{mode}' is missing required 'max_tokens'.",
                details={"error_code": ErrorCodes.CONFIGURATION_ERROR},
            )

        # Extract API Key from DB Config
        api_key = cd.get("api_key")

        # STRICT VALIDATION (Jan 2026 Decree):
        # Ensure the configured model name actually exists in the target region.
        # This prevents "blind" 404s from the provider.
        if provider == "google" and mode != "mock":
            available_models_map = self.fetch_all_available_models(providers=[provider])
            valid_models = available_models_map.get(provider, [])

            # DB stores "vertex_ai/foo", discovery returns "vertex_ai/foo"
            if model_name not in valid_models:
                # Force refresh once if not found, just in case cache is stale?
                # No, "Strict Strictness" implies we trust our validator.
                # But maybe we should warn logic.
                # Actually, checking if it is a "mock" environment or not.
                if "mock" not in model_name.lower():
                    error_msg = (
                        f"STRICT VALIDATION ERROR: Model '{model_name}' configured for strategy '{mode}' "
                        f"is NOT available in the current region ('{settings.vertex_location}'). "
                        f"Available models: {valid_models[:5]}..."
                    )
                    logger.error(error_msg)
                    raise ValueError(error_msg)

        # Create Provider via Factory (Unified Logic)
        try:
            logger.info(
                f"[LLM Execution] Strategy: {provider}/{mode} -> Model: {model_name} "
                f"(Temp: {temperature}, MaxTokens: {max_tokens})"
            )

            # Construct strict config object
            # We map dict fields to LLMProviderConfig
            # Note: 'cd' is the raw dict from DB
            provider_config = LLMProviderConfig(
                id=f"{provider}/{mode}",
                provider=provider,
                model_name=model_name,
                api_key=api_key,
                base_url=cd.get("base_url"),
                temperature=temperature,
                tpm_limit=cd.get("tpm_limit", 0),
                rpm_limit=cd.get("rpm_limit", 0),
                default_max_tokens=max_tokens,
                vertex_location=cd.get("vertex_location"),
                supports_grounding=cd.get("supports_grounding", False),
                is_active=cd.get("is_active", True),
                additional_params=cd.get("additional_params", {}),
            )

            # FAIL FAST: Check Active Status
            if not provider_config.is_active:
                raise ServiceUnavailableError(
                    message=f"Model Strategy '{provider}/{mode}' is deactivated.",
                    details={"error_code": ErrorCodes.SERVICE_DISABLED},
                )

            # Pass config object to factory
            llm_provider = LLMFactory.create_provider(
                provider_type=provider,  # Redundant but kept for signature
                model_name=model_name,  # Redundant but kept for signature
                config=provider_config,
                api_key=api_key,  # Pass explicit key if needed, but config has it
            )

            response = await llm_provider.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Response is now LLMResponse object
            if response.reasoning_token:
                logger.info(f"[LLMHandler] Captured Reasoning Token: {response.reasoning_token[:20]}...")

            # Return content string to maintain backward compatibility for this ad-hoc method
            return response.content

        except ValueError as ve:
            raise ve  # Re-raise strict validation errors
        except Exception as e:
            if isinstance(e, (ServiceUnavailableError, ConfigurationError)):
                raise e
            logger.error(f"[LLMHandler] Unified Call Failed: {e}", exc_info=True)
            raise e  # Strict raising instead of returning string error
