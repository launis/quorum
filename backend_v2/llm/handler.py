"""LLM Handler module for managing model discovery and configuration."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import openai

from backend_v2.exceptions import AppException, ConfigurationError, ErrorCodes, ServiceUnavailableError
from backend_v2.llm.provider import LLMFactory
from backend_v2.models.llm import LLMProviderConfig
from backend_v2.models.v2_core import SystemConfigModelRegistry
from backend_v2.settings import get_settings
from backend_v2.utils.pydantic_utils import inflate

try:
    import google.auth
    import requests
    import vertexai
    from google.api_core import client_options as g_client_options
    from google.auth.transport.requests import Request as GRequest
    from google.cloud import aiplatform_v1
    from vertexai.generative_models import GenerativeModel

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

        Attempts to fetch its metadata in the target location.
        """
        if not GOOGLE_DEPS_AVAILABLE:
            return False

        try:
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

    def __init__(self, repo: Any):
        """Initializes the handler.

        Args:
            repo (Any): The IWorkflowRepository instance (injected via dependencies.py).
        """
        self.repo = repo
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
                source_region = settings.discovery_location
                if not source_region:
                    raise ConfigurationError(
                        message="Strict Fail-Fast: 'discovery_location' is required in settings.",
                        details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value},
                    )
                logger.debug("[LLMHandler] Initiating Model Discovery (Source: %s)...", source_region)

                if not GOOGLE_DEPS_AVAILABLE:
                    raise ConfigurationError(
                        message="Missing required dependencies for Google discovery.",
                        details={"error_code": ErrorCodes.SERVICE_DEPENDENCY_MISSING.value},
                    )

                import litellm

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
                    credentials, project = google.auth.default(  # type: ignore[no-untyped-call]
                        scopes=["https://www.googleapis.com/auth/cloud-platform"]
                    )
                    credentials.refresh(GRequest())  # type: ignore[no-untyped-call]
                    token = credentials.token
                except Exception as auth_err:
                    # Fail Fast: If we can't authenticate, we can't discover or use models.
                    raise ConfigurationError(
                        message="Google Authentication failed during discovery.",
                        details={"error_code": ErrorCodes.AUTHENTICATION_FAILED.value, "original_error": str(auth_err)},
                    ) from auth_err

                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

                def check_model(model_id: str) -> str | None:
                    # Clean model ID for API call
                    clean_id = model_id
                    for prefix in ["vertex_ai/", "gemini/", "models/"]:
                        if clean_id.startswith(prefix):
                            clean_id = clean_id[len(prefix) :]

                    # 1. SPECIAL CASE: For Gemini 3.x models, use the modern google-genai Client
                    # to check their global availability.
                    if "gemini-3." in clean_id:
                        try:
                            from google import genai
                            # Initialize modern GenAI client with global endpoint
                            modern_client = genai.Client(
                                vertexai=True,
                                project=project,
                                location="global"
                            )
                            # Get model metadata to verify availability
                            _ = modern_client.models.get(model=clean_id)
                            # Explicitly exclude gemini-3.5-pro as empirical tests prove
                            # it does not support content generation yet (404).
                            if clean_id == "gemini-3.5-pro":
                                return None
                            return f"vertex_ai/{clean_id}"
                        except Exception:
                            return None

                    # 2. STANDARD CASE: For traditional models (1.5, 2.0, 2.5), use region checks in Hamina (target_location)
                    try:
                        # Initialize Vertex AI strictly in the target location
                        vertexai.init(project=project, location=target_location, credentials=credentials)

                        # Just initializing the model objects acts as a validation that the string
                        # name is somewhat valid. To be absolutely sure, we'd need to call it, but
                        # that costs money and time. For now we just verify we can instantiate it
                        # using the Vertex AI SDK which does some basic validation.
                        try:
                            _ = GenerativeModel(clean_id)
                            # Also verify it via the publisher models API to be doubly safe
                            url = f"https://{target_location}-aiplatform.googleapis.com/v1/publishers/google/models/{clean_id}"
                            resp = requests.get(url, headers=headers, timeout=5)
                            if resp.status_code == 200:
                                return f"vertex_ai/{clean_id}"
                            return None
                        except Exception:
                            return None
                    except Exception:
                        return None

                # Parallel Validation
                logger.info("[LLMHandler] discovering %d models; validating in %s...", len(candidates), target_location)

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
                    logger.error("[LLMHandler] Regional validation in %s returned 0 models.", target_location)
                    final_list = []

                models["google"] = final_list
                self._cached_google_models = final_list

                logger.info(
                    "[LLMHandler] Discovered & Validated %d Gemini models in %s.", len(final_list), target_location
                )

            except Exception as e:
                # If it's already an AppException, re-raise
                if isinstance(e, AppException):
                    raise e

                # Otherwise wrap in ServiceUnavailable (upstream failure)
                logger.error(
                    "[LLMHandler] %s: Error fetching/validating Google models: %s",
                    ErrorCodes.MODEL_LIST_FAILED.name,
                    e,
                    exc_info=True,
                )

                # STRICT: Do not return error strings. Raise.
                raise ServiceUnavailableError(
                    message=f"Google Model Discovery Failed: {e}",
                    details={"error_code": ErrorCodes.MODEL_LIST_FAILED.value, "original_error": str(e)},
                ) from e

        # --- OPENAI ---
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

        return models

    async def get_active_model_registry(self) -> dict[str, Any]:
        """Fetches the 'global_model_registry' from the 'system_config' table in the database.

        Returns:
            Dict[str, Any]: configuration mapping (flat map of ModelProfiles).
        """
        try:
            res = await self.repo.get_model_registry()

            parsed = inflate(res, SystemConfigModelRegistry)
            if not isinstance(parsed, SystemConfigModelRegistry):
                raise ValueError("Parsed registry is not a valid SystemConfigModelRegistry")
            dump = parsed.model_dump()
            models: dict[str, Any] = dump["models"]
            return models
        except Exception as e:
            logger.error(
                "[LLMHandler] %s: Failed to parse active model registry: %s",
                ErrorCodes.CONFIGURATION_ERROR.name,
                e,
                exc_info=True,
            )
            raise ConfigurationError(
                message=f"Model Registry is corrupt: {e}", details={"error_code": ErrorCodes.CONFIGURATION_ERROR.value}
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

        # V2 schema uses 'mode' (strategy) as the top-level keys
        config = registry.get(mode)

        if config:
            return dict(config)
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
        config = await self.get_model_config(provider, mode)

        if not config:
            raise ValueError(f"STRICT CONFIG ERROR: No configuration found for strategy '{provider}/{mode}' ")

        cd = config

        # Pydantic has already validated these via SystemConfigModelRegistry in get_active_model_registry
        model_name = cd["model_name"]
        temperature = cd["temperature"]
        max_tokens = cd["max_tokens"]
        api_key = cd.get("api_key")

        # STRICT VALIDATION (Jan 2026 Decree):
        # Ensure the configured model name actually exists in the target region.
        # This prevents "blind" 404s from the provider.
        if provider == "google" and mode != "mock":
            import asyncio

            available_models_map = await asyncio.to_thread(self.fetch_all_available_models, providers=[provider])
            valid_models = available_models_map[provider] if provider in available_models_map else []

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

            response = await llm_provider.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Response is now LLMResponse object
            if response.reasoning_token:
                logger.info("[LLMHandler] Captured Reasoning Token: %s...", response.reasoning_token[:20])

            # Return content string to maintain backward compatibility for this ad-hoc method
            return response.content

        except Exception as e:
            if isinstance(e, (AppException, ServiceUnavailableError, ConfigurationError)):
                raise e
            logger.error("[LLMHandler] %s: Unified Call Failed: %s", ErrorCodes.UNKNOWN_ERROR.name, e, exc_info=True)
            raise ServiceUnavailableError(
                message=f"LLM Handler Unified Call Failed: {e}", details={"error_code": ErrorCodes.UNKNOWN_ERROR.value}
            ) from e
