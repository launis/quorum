from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, Union
import os
import logging
import json
import asyncio
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.models.state import WorkflowState
from backend.models.state import WorkflowState
from backend.models.llm import LLMResponse
from backend.settings import get_settings
import litellm

# Configure logging
logger = logging.getLogger(__name__)

# Define retry strategy
_settings = get_settings()

retry_strategy = retry(
    stop=stop_after_attempt(_settings.llm_max_retries),
    wait=wait_exponential(multiplier=_settings.llm_retry_delay, min=1, max=10),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(f"Retrying LLM call... (Attempt {retry_state.attempt_number}/{_settings.llm_max_retries})")
)

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    Defines the contract for text generation and structured data extraction.
    """
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        pass_reasoning_token: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generates content from the LLM.

        Args:
            prompt (str): The user prompt.
            system_instruction (Optional[str]): System prompt/context.
            response_schema (Optional[Type[BaseModel]]): Pydantic model for structured output validation.
            temperature (float): Sampling temperature.
            max_tokens (Optional[int]): Max tokens to generate.
            pass_reasoning_token (Optional[str]): Encrypted state blob from previous turn.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse: The generated response object.
        """
        pass

# Global Cache for Models
_CACHED_MODELS = []

class GoogleAIProvider(LLMProvider):
    """
    Legacy class kept primarily for fetch_available_models used by LLMHandler.
    Actual generation logic is now handled by LiteLLMProvider via LLMFactory.
    """
    
    @staticmethod
    def fetch_available_models(api_key: Optional[str] = None) -> list:
        """
        Fetches available models from Google API using the new google.genai V2 SDK.
        Updates the global cache.
        """
        global _CACHED_MODELS
        if _CACHED_MODELS:
             return _CACHED_MODELS

        # V2 SDK Import
        try:
            from google import genai
        except ImportError:
            logger.error("[GoogleAIProvider] google-genai package not found.")
            return []

        from backend.settings import get_settings
        
        settings = get_settings()
        key = api_key or settings.google_api_key
        
        if not key:
            return []

        try:
            client = genai.Client(api_key=key)
            models = []
            # Use V2 API to list models
            pager = client.models.list()
            for m in pager:
                # Basic filtering for Gemini models
                # In V2, most models listed are usable. We focus on gemini versions.
                if "gemini" in m.name.lower():
                    name_clean = m.name.replace("models/", "")
                    models.append(name_clean)
            
            logger.info(f"[GoogleAIProvider] Fetched {len(models)} models from API (v2).")
            _CACHED_MODELS = sorted(models)
            return _CACHED_MODELS
        except Exception as e:
            logger.error(f"[GoogleAIProvider] Failed to list models: {e}")
            return []

    async def generate(self, *args, **kwargs):
        raise NotImplementedError("Use LiteLLMProvider via LLMFactory instead.")

class LiteLLMProvider(LLMProvider):
    """
    Unified LLM Provider using LiteLLM to support multiple models (Gemini, OpenAI, etc.)
    with a consistent interface.
    """
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        """
        Initializes the LiteLLM provider.

        Args:
            model_name (str): The model identifier (e.g. 'gemini/gemini-1.5-pro').
            api_key (Optional[str]): API Key for the specific provider.
        """
        self.model_name = model_name
        self.api_key = api_key
        # litellm configuration if needed
        litellm.drop_params = True 

    def _clean_json_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Robustly parses JSON from LLM output, handling markdown blocks and conversational text.
        
        Strategies:
        1. Parse directly.
        2. Strip markdown blocks.
        3. Regex extract JSON object.
        4. Heuristic repairs (trailing commas, comments).

        Args:
            raw_response (str): The raw output string from the LLM.

        Returns:
            Dict[str, Any]: Parsed JSON object.

        Raises:
            ValueError: If JSON cannot be extracted.
        """
        import re
        
        # 0. Pre-cleaning: Remove // comments (Common in LLM JSON)
        # Be careful not to match URLs (http://...)
        
        # Simple attempt to parse directly first
        json_candidate = raw_response
        
        try:
            # 1. Try stripping markdown code blocks
            clean_text = raw_response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except json.JSONDecodeError:
            pass

        # 2. Try regex extraction of the main JSON object
        try:
            start_index = raw_response.find('{')
            end_index = raw_response.rfind('}')
            
            if start_index != -1 and end_index != -1 and end_index > start_index:
                json_candidate = raw_response[start_index : end_index + 1]
                return json.loads(json_candidate)
        except json.JSONDecodeError as e:
            logger.warning(f"[LiteLLM] Extraction failed: {e}. Attempting repairs...")
            
            # 3. Repair: Remove single-line comments // that are not inside strings (Approximate)
            try:
                repaired = re.sub(r'^\s*//.*$', '', json_candidate, flags=re.MULTILINE)
                return json.loads(repaired)
            except Exception:
                pass

            # 4. Repair: Heuristic Fix for Missing Commas
            try:
                fixed_json = re.sub(r'(?<=[}\]"\'0-9lue])\s*(?<!,)\s*\n\s*(?=")', ',\n', json_candidate)
                return json.loads(fixed_json)
            except Exception as e2:
                logger.error(f"[LiteLLM] Heuristic fix failed: {e2}")

            raise ValueError(f"Could not extract valid JSON from response. Content: {raw_response[:200]}...")

    @retry_strategy
    async def generate(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        pass_reasoning_token: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generates content using LiteLLM.
        Returns unified LLMResponse with content and reasoning state.
        """
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
            
        # Context Continuity (Stateless Reasoning Blob)
        if pass_reasoning_token:
            # Abstraction: We pass it as a developer hint for now.
            # Real implementation would use provider-specific params in `litellm.acompletion`
            messages.append({"role": "system", "content": f"[SYSTEM: RESUME_THOUGHT_PROCESS] PREVIOUS_STATE_BLOB: {pass_reasoning_token}"})

        messages.append({"role": "user", "content": prompt})
        
        response_format = None
        if response_schema:
            try:
                logger.info(f"[LiteLLM] Enabling Structured Output for schema: {response_schema.__name__}")
                response_format = response_schema
            except Exception:
                pass
        
        try:
            logger.info(f"[LiteLLM] Calling {self.model_name}...")
            
            response = await litellm.acompletion(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
                api_key=self.api_key,
                drop_params=True
            )
            
            # Extract basic content
            choice = response.choices[0]
            message = choice.message
            raw_content = message.content or ""
            
            # Extract Reasoning Token (Gemini 3 / GPT-5.1)
            reasoning_token = None
            
            # Check standard LiteLLM extra fields
            if hasattr(message, "provider_specific_fields") and message.provider_specific_fields:
                 reasoning_token = message.provider_specific_fields.get("thought_signature") or \
                                   message.provider_specific_fields.get("reasoning_blob")
                                   
            # Fallback: Check top level attributes
            if not reasoning_token and hasattr(response, "model_extra"):
                 reasoning_token = response.model_extra.get("thought_signature")

            # Extract Usage
            usage = {}
            if hasattr(response, "usage"):
                 usage = {
                     "prompt_tokens": response.usage.prompt_tokens,
                     "completion_tokens": response.usage.completion_tokens,
                     "total_tokens": response.usage.total_tokens
                 }

            # Handle Schema Parsing (Validation)
            # If schema was requested, we return the JSON string in 'content' 
            # OR we populate 'tool_calls' if that mechanism was used.
            # For simplicity in this unified response, we ensure 'content' is the stringent result.
            
            final_content = raw_content
            if response_schema:
                 if hasattr(message, "parsed") and message.parsed:
                      # If LiteLLM parsed it, dump back to JSON string for consistency
                      obj = message.parsed.dict() if hasattr(message.parsed, "dict") else message.parsed
                      final_content = json.dumps(obj, ensure_ascii=False)
                 else:
                      # Clean manually
                      obj = self._clean_json_response(raw_content)
                      final_content = json.dumps(obj, ensure_ascii=False)

            return LLMResponse(
                content=final_content,
                reasoning_token=reasoning_token,
                token_usage=usage,
                provider_metadata=response.model_dump() if hasattr(response, "model_dump") else {}
            )
            
        except Exception as e:
            logger.error(f"[LiteLLM] Error: {e}", exc_info=True)
            raise e

class MockProvider(LLMProvider):
    """
    Mock LLM Provider for offline testing and development.
    Uses cached/simulated responses from MockLLMService.
    """
    def __init__(self, model_name: str = "mock"):
        self.model_name = model_name

    async def generate(self, prompt: str, system_instruction: Optional[str] = None, response_schema: Optional[Type[BaseModel]] = None, temperature: float = 0.7, max_tokens: Optional[int] = None, pass_reasoning_token: Optional[str] = None, **kwargs) -> LLMResponse:
        """
        Simulates generation by invoking the MockLLMService.
        """
        from backend.llm.mock import MockLLMService
        logger.info(f"[MockProvider] Calling Mock Service (Simulating Async)... {kwargs}")
        
        # Simulate network delay for verification of async behavior
        await asyncio.sleep(0.5)

        mock = MockLLMService()
        
        # Extract explicit identity if provided
        agent_identity = kwargs.get('mock_identity')
        
        result = mock.generate_content(prompt, system_instruction, agent_identity=agent_identity)
        
        # Determine content string
        content_str = ""
        if isinstance(result, dict):
            content_str = json.dumps(result, ensure_ascii=False)
        else:
            content_str = str(result)
            
        return LLMResponse(
            content=content_str,
            reasoning_token="mock_thought_signature_123456",
            token_usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150}
        )

class LLMFactory:
    """
    Factory class to instantiate the appropriate LLMProvider based on configuration.
    """
    @staticmethod
    def create_provider(provider_type: str, model_name: str) -> LLMProvider:
        """
        Creates an LLM provider instance.

        Args:
            provider_type (str): Type of provider (e.g., 'gemini', 'openai').
            model_name (str): Specific model name.

        Returns:
            LLMProvider: Configured provider instance.

        Raises:
            ValueError: If configuration is invalid.
        """
        settings = get_settings()
        
        if settings.use_mock_llm:
            return MockProvider(model_name=model_name or "mock-default")

        if not provider_type or not model_name:
             raise ValueError("[LLMFactory] provider_type and model_name MUST be provided from DB config. No defaults allowed.")

        # Simplify logic using LiteLLM
        # Map provider to model naming convention
        
        target_model = model_name
        api_key = None
        
        if provider_type.lower() == "gemini":
            # STRICT MODE: Model name must come fully formed from DB (e.g. gemini/gemini-1.5-pro)
            target_model = model_name
            api_key = settings.google_api_key
            
        elif provider_type.lower() == "openai":
            target_model = model_name
            api_key = settings.openai_api_key
            api_key = os.getenv("OPENAI_API_KEY")
        
        # Default fallback or pass-through
        if not target_model:
             # Should not happen given logic above usually, but safe default
             # Strict mode: raise error if we somehow got here without a model
             raise ValueError("[LLMFactory] Failed to resolve target_model. Check logic.") 

        msg_key = "PRESENT" if api_key else "MISSING"
        logger.info(f"[LLMFactory] Creating Provider: {target_model} (Key: {msg_key})")
        
        return LiteLLMProvider(model_name=target_model, api_key=api_key)
