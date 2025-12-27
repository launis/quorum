import os
import logging
from typing import List, Dict, Any, Optional
from tinydb import Query
from backend.database.wrapper import get_db_client
from backend.settings import get_settings
from backend.llm.provider import LLMFactory
import google.generativeai as genai
import openai

logger = logging.getLogger(__name__)

class LLMHandler:
    """
    Handles higher-level LLM operations including model discovery via APIs,
    fetching configuration from the database, and delegating execution to the LLMFactory.
    """
    def __init__(self, db_client: Any):
        """
        Initializes the handler.

        Args:
            db_client (Any): Database client for accessing system config.
        """
        self.db_client = db_client

    def fetch_all_available_models(self) -> Dict[str, List[str]]:
        """
        Queries External APIs (Google GenAI, OpenAI) for available models.
        Respects 'use_mock_llm' setting by returning mock data if enabled.

        Returns:
            Dict[str, List[str]]: Dictionary containing lists of models for 'google' and 'openai'.
        """
        settings = get_settings()
        models = {
            "google": [],
            "openai": []
        }
        
        if settings.use_mock_llm:
            models["google"] = ["mock-model-a", "mock-model-b"]
            models["openai"] = ["mock-gpt-a"]
            return models
        
        # 1. Fetch Google Models
        try:
             # Use the Provider's caching mechanism (initialized at bootstrap)
             from backend.llm.provider import GoogleAIProvider
             
             logger.info(f"Fetching cached Google models from Provider...")
             # Since it's a static method that checks cache, we can just call it safely.
             cached_google_models = GoogleAIProvider.fetch_available_models(api_key=settings.google_api_key)
             models["google"] = cached_google_models
             
        except Exception as e:
            logger.error(f"Error fetching Google models: {e}", exc_info=True)
            models["google_error"] = str(e)
            
        # 2. Fetch OpenAI Models (Cached)
        try:
             # Simple global cache for OpenAI similar to Google
             if not hasattr(self, '_cached_openai_models'):
                 self._cached_openai_models = []
             
             if self._cached_openai_models:
                 models["openai"] = self._cached_openai_models
             else:
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    client = openai.OpenAI(api_key=api_key)
                    # List models
                    for m in client.models.list():
                        # Filter for likely chat models
                        if "gpt" in m.id:
                            self._cached_openai_models.append(m.id)
                    models["openai"] = self._cached_openai_models
                else:
                     # Not an error per se if user only wants Gemini
                     models["openai_warning"] = "OPENAI_API_KEY not found"
        except Exception as e:
            models["openai_error"] = str(e)
            
        return models

    def get_active_model_registry(self) -> Dict[str, str]:
        """
        Fetches the 'global_model_registry' from the 'system_config' table in the database.
        
        Returns:
            Dict[str, str]: configuration mapping (e.g. {'fast': 'gemini-1.5-flash'}).
        """
        try:
            table = self.db_client.table('system_config')
            
            Result = Query()
            results = table.search(Result.type == 'model_registry') 
            
            if results:
                return results[0].get('models', {})
            return {}
        except Exception as e:
            print(f"[LLMHandler] Failed to get model registry: {e}")
            return {}

    def get_model_config(self, provider: str, mode: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific model configuration for a provider/mode.

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

    async def call_llm(self, provider: str, mode: str, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        High-level helper to call an LLM (Ad-hoc usage).
        Resolves configuration from DB based on provider/mode and delegates to LLMFactory.

        Args:
            provider (str): 'gemini' or 'openai' or 'mock'.
            mode (str): 'fast', 'smart', etc.
            prompt (str): Text prompt.
            system_instruction (Optional[str]): System context.

        Returns:
            str: Generated text response.
        """
        config = self.get_model_config(provider, mode)
        
        # Defaults
        settings = get_settings()
        model_name = settings.initial_model
        temperature = 0.7
        max_tokens = None
        
        if config:
            # Handle if config is Pydantic model or dict
            if hasattr(config, "dict"):
                cd = config.model_dump()
            elif hasattr(config, "model_dump"):
                cd = config.model_dump()
            else:
                cd = config
                
            model_name = cd.get("model_name", model_name)
            temperature = cd.get("temperature", temperature)
            max_tokens = cd.get("max_tokens", max_tokens)
        else:
             # Minimal default if config completely missing
             # if provider == "openai": model_name = "gpt-4o" # Removed to enforce centralized config
             pass
        
        # Create Provider via Factory (Unified Logic)
        try:
            logger.info(f"[LLM Execution] Strategy: {provider}/{mode} -> Model: {model_name} (Temp: {temperature}, MaxTokens: {max_tokens})")
            llm_provider = LLMFactory.create_provider(provider, model_name)
            
            response = await llm_provider.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=temperature,
                max_tokens=max_tokens # Now validating this argument exists in provider
            )
            
            # Helper handles return type (str or dict) -> We expect Str for pure text generation endpoints
            if isinstance(response, dict):
                import json
                return json.dumps(response, ensure_ascii=False)
            return str(response)
            
        except Exception as e:
            logger.error(f"[LLMHandler] Unified Call Failed: {e}", exc_info=True)
            return f"Error calling LLM: {str(e)}"
