"""LLM Handler module for managing model discovery and configuration."""

import logging
import os
from typing import Any

import openai
from google.cloud import aiplatform_v1beta1
from tinydb import Query

from backend.llm.provider import LLMFactory
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
            api_endpoint = f"{location}-aiplatform.googleapis.com"
            client_options = {"api_endpoint": api_endpoint}
            client = aiplatform_v1beta1.ModelGardenServiceClient(client_options=client_options)

            # The name format for retrieving is "publishers/google/models/{model_name}"
            # model_id input is usually "vertex_ai/{model_name}" or just "{model_name}" logic
            # My current logic stores "vertex_ai/gemini-..."
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

        # Normalize providers list
        if not providers:
            providers = ["google", "openai"]

        providers = [p.lower() for p in providers]
        if "moc" in providers:
            providers.append("mock")

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
                # Check cache for the *Target Location* (validated list)
                if hasattr(self, "_cached_google_models") and self._cached_google_models:  # type: ignore[has-type]
                    # Simple cache assumption: Environment doesn't change runtime
                    models["google"] = self._cached_google_models
                else:
                    # 1. Master List (us-central1) - Always works for listing Catalog
                    # We inline the list call here for simplicity or could use helper if reused.
                    # Using us-central1 explicitly.
                    discovery_ep = "us-central1-aiplatform.googleapis.com"
                    client = aiplatform_v1beta1.ModelGardenServiceClient(client_options={"api_endpoint": discovery_ep})

                    # Listing
                    # logger.info("Fetching Master Catalog from us-central1...")
                    response = client.list_publisher_models(parent="publishers/google")

                    master_list = []
                    for m in response.publisher_models:
                        mid = m.name.split("/")[-1]
                        if "gemini" in mid.lower():
                            master_list.append(f"vertex_ai/{mid}")
                    master_list = sorted(list(set(master_list)))

                    final_list = []

                    # 2. Validation
                    if target_location == "us-central1":
                        final_list = master_list
                    else:
                        # VALIDATING REGIONALLY
                        logger.info(f"[LLMHandler] Validating {len(master_list)} models in '{target_location}'...")
                        for m in master_list:
                            if self._check_model_availability(m, target_location):
                                final_list.append(m)
                            else:
                                # logger.debug(f"Model {m} not available in {target_location}")
                                pass
                        logger.info(f"[LLMHandler] Validation complete. Found {len(final_list)} valid models.")

                    models["google"] = final_list
                    self._cached_google_models = final_list  # type: ignore[has-type]

            except ImportError:
                logger.error("google-cloud-aiplatform not installed.")
                models["google_error"] = "Missing google-cloud-aiplatform library"
            except Exception as e:
                logger.error(f"Error fetching Google models: {e}")
                models["google_error"] = str(e)

        # --- OPENAI ---
        if "openai" in providers:
            try:
                if not hasattr(self, "_cached_openai_models"):
                    self._cached_openai_models: list[str] = []

                if self._cached_openai_models:
                    models["openai"] = self._cached_openai_models
                else:
                    api_key = os.getenv("OPENAI_API_KEY") or settings.openai_api_key
                    if api_key:
                        client = openai.OpenAI(api_key=api_key)
                        for m in client.models.list():
                            if "gpt" in m.id:
                                self._cached_openai_models.append(m.id)
                        models["openai"] = self._cached_openai_models
                    else:
                        models["openai_warning"] = "OPENAI_API_KEY not found"
            except Exception as e:
                models["openai_error"] = str(e)

        return models

    def get_active_model_registry(self) -> dict[str, str]:
        """Fetches the 'global_model_registry' from the 'system_config' table in the database.

        Returns:
            Dict[str, str]: configuration mapping (e.g. {'fast': 'gemini-1.5-flash'}).

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
            config = registry[provider].get(mode)

        if config:
            return config

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
            raise ValueError(
                f"STRICT CONFIG ERROR: No configuration found for strategy '{provider}/{mode}' "
                "in System Registry. Fallbacks are PROHIBITED."
            )

        # Handle if config is Pydantic model or dict
        if hasattr(config, "dict"):
            cd = config.model_dump()
        elif hasattr(config, "model_dump"):
            cd = config.model_dump()
        else:
            cd = config

        model_name = cd.get("model_name")
        if not model_name:
            raise ValueError(f"STRICT CONFIG ERROR: Strategy '{provider}/{mode}' exists but describes no 'model_name'.")

        temperature = cd.get(
            "temperature", 0.7
        )  # Parameter defaults are acceptable/necessary? Assuming yes for float/int, but MODEL must be explicit.
        max_tokens = cd.get("max_tokens", None)

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
            llm_provider = LLMFactory.create_provider(provider, model_name)

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
            logger.error(f"[LLMHandler] Unified Call Failed: {e}", exc_info=True)
            return f"Error calling LLM: {str(e)}"
