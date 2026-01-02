from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, Union
import os
import logging
import json
import asyncio
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, wait_exponential
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
    wait=wait_exponential(multiplier=_settings.llm_retry_delay, min=1, max=60),
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

# Global Cache for Models (Simplified)
_CACHED_MODELS = []

class LiteLLMProvider(LLMProvider):
    """
    Unified LLM Provider using LiteLLM to support multiple models (Gemini, OpenAI, etc.)
    with a consistent interface.
    """
    def __init__(self, model_name: str, api_key: Optional[str] = None, settings: Any = None):
        """
        Initializes the LiteLLM provider.

        Args:
            model_name (str): The model identifier.
            api_key (Optional[str]): API Key.
            settings (Any): System settings object (containing vertex_location etc).
        """
        self.model_name = model_name
        self.api_key = api_key
        self.settings = settings
        # litellm configuration if needed
        litellm.drop_params = True 

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
            
            # Prepare arguments
            call_kwargs = {
                "model": self.model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "response_format": response_format,
                "api_key": self.api_key,
                "drop_params": True
            }

            # Explicitly force Vertex Location (Fixes 403 default-to-us-central1 issue)
            # Robustly resolve location (Settings attr or Env Var)
            
            # Ensure env is loaded from project root
            from dotenv import load_dotenv
            from pathlib import Path
            
            # provider.py is at backend/llm/provider.py
            # Go up 3 levels to reach project root
            root_dir = Path(__file__).resolve().parent.parent.parent
            env_path = root_dir / ".env"
            
            load_dotenv(dotenv_path=env_path)
            
            v_loc = None
            if self.settings and hasattr(self.settings, "vertex_location"):
                v_loc = self.settings.vertex_location
            
            if not v_loc:
                v_loc = os.getenv("VERTEX_LOCATION")
                
            # STRICT MODE: No defaults. Fail if missing.
            if not v_loc:
                 logger.error(f"[LiteLLMProvider] Env load failed. Tried path: {env_path}, Exists: {env_path.exists()}")
                 raise ValueError(f"[LiteLLMProvider] Critical Error: VERTEX_LOCATION not found in settings or .env ({env_path}). Cannot proceed.")
            
            logger.info(f"[LiteLLMProvider] Using Vertex Location: {v_loc}")
            call_kwargs["vertex_location"] = v_loc

            response = await litellm.acompletion(**call_kwargs)
            
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
                      # STRICT MODE: Fail Fast if not valid JSON
                      try:
                          # Attempt standard parsing
                          # Note: Some models return Markdown ```json ... ``` even with strict mode
                          # We do minimal stripping of code blocks only, no heuristic repair.
                          clean_text = raw_content
                          if "```" in raw_content:
                                clean_text = raw_content.replace("```json", "").replace("```", "").strip()
                          
                          obj = json.loads(clean_text)
                          final_content = json.dumps(obj, ensure_ascii=False)
                      except json.JSONDecodeError as e:
                          logger.error(f"[LiteLLM] Strict JSON Parse Failed: {e}")
                          # Dump for debug
                          with open("FAILED_JSON_STRICT.txt", "w", encoding="utf-8") as f:
                               f.write(raw_content)
                          raise ValueError(f"Strict JSON parsing failed. Content dumped to FAILED_JSON_STRICT.txt")

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

        target_model = model_name
        api_key = None
        
        if provider_type.lower() == "gemini" or provider_type.lower() == "vertex_ai":
            # STRICT MODE: Model name must come fully formed from DB (e.g. gemini/gemini-1.5-pro)
            target_model = model_name
            api_key = settings.google_api_key
            
        elif provider_type.lower() == "openai":
            target_model = model_name
            api_key = settings.openai_api_key
            if not api_key:
                api_key = os.getenv("OPENAI_API_KEY")
        
        if not target_model:
             raise ValueError("[LLMFactory] Failed to resolve target_model. Check logic.") 

        msg_key = "PRESENT" if api_key else "MISSING"
        logger.info(f"[LLMFactory] Creating Provider: {target_model} (Key: {msg_key})")
        
        return LiteLLMProvider(model_name=target_model, api_key=api_key, settings=settings)
