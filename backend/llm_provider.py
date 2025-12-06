from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, Union
import os
import logging
import json
import asyncio
from pydantic import BaseModel
import tenacity
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from backend.state import WorkflowState
from backend.config import (
    GOOGLE_API_KEY, 
    LLM_DEFAULT_TIMEOUT, 
    LLM_MAX_RETRIES, 
    LLM_RETRY_DELAY,
    USE_MOCK_LLM
)

# Configure logging
logger = logging.getLogger(__name__)

# Define retry strategy
# Valid for both sync and async functions in modern tenacity
retry_strategy = retry(
    stop=stop_after_attempt(LLM_MAX_RETRIES),
    wait=wait_exponential(multiplier=LLM_RETRY_DELAY, min=1, max=10),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(f"Retrying LLM call... (Attempt {retry_state.attempt_number}/{LLM_MAX_RETRIES})")
)

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers (Google, OpenAI, Mock, etc.).
    This defines the 'mask' interface.
    """
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7
    ) -> Union[str, Dict[str, Any]]:
        pass

class GoogleGeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemini-1.5-flash", api_key: Optional[str] = None):
        import google.generativeai as genai
        self.model_name = model_name
        self.api_key = api_key or GOOGLE_API_KEY
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found.")
        
        genai.configure(api_key=self.api_key)

    def _sanitize_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitizes Pydantic JSON schema for Gemini.
        """
        import copy
        schema = copy.deepcopy(schema)
        defs = schema.pop('$defs', {})
        defs.update(schema.pop('definitions', {}))
        
        def resolve_refs(node):
            if isinstance(node, dict):
                # Handle $ref
                if '$ref' in node:
                    ref_path = node['$ref']
                    ref_name = ref_path.split('/')[-1]
                    if ref_name in defs:
                        definition = copy.deepcopy(defs[ref_name])
                        return resolve_refs(definition)
                
                # Handle anyOf
                if 'anyOf' in node:
                    any_of = node.pop('anyOf')
                    non_null_types = [t for t in any_of if t.get('type') != 'null']
                    
                    if len(non_null_types) == 1:
                        node.update(resolve_refs(non_null_types[0]))
                        node['nullable'] = True
                    elif non_null_types:
                        node.update(resolve_refs(non_null_types[0]))

                # Clean fields that Gemini rejects
                node.pop('examples', None)
                node.pop('title', None)
                node.pop('default', None) 
                node.pop('additionalProperties', None)
                node.pop('maximum', None)
                node.pop('minimum', None)
                node.pop('exclusiveMaximum', None)
                node.pop('exclusiveMinimum', None)
                node.pop('maxLength', None)
                node.pop('minLength', None)
                node.pop('pattern', None)
                
                if node.get('type') == 'object' and not node.get('properties'):
                    node['properties'] = {'_dynamic_content': {'type': 'string', 'nullable': True}}

                # Recursively clean children
                new_node = {}
                for k, v in node.items():
                    if k == 'properties' and isinstance(v, dict):
                        new_props = {}
                        for pk, pv in v.items():
                            new_props[pk] = resolve_refs(pv)
                        new_node[k] = new_props
                    else:
                        new_node[k] = resolve_refs(v)
                return new_node
            elif isinstance(node, list):
                return [resolve_refs(item) for item in node]
            return node

        return resolve_refs(schema)

    @retry_strategy
    async def generate(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7
    ) -> Union[str, Dict[str, Any]]:
        import google.generativeai as genai
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": 8192,
        }

        # Native Structured Output Support
        if response_schema:
            try:
                raw_schema = response_schema.model_json_schema()
                sanitized_schema = self._sanitize_schema(raw_schema)
                
                logger.info(f"[GeminiProvider] Enabling Structured Output for schema: {response_schema.__name__}")
                generation_config["response_mime_type"] = "application/json"
                generation_config["response_schema"] = sanitized_schema
            except Exception as e:
                logger.error(f"[GeminiProvider] Schema sanitization failed: {e}. Falling back to raw schema.")
                generation_config["response_mime_type"] = "application/json"
                generation_config["response_schema"] = response_schema
        
        # ASYNC CHANGE: Using GenerativeModel instance
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            system_instruction=system_instruction
        )

        try:
            logger.info(f"[GeminiProvider] Calling {self.model_name} (ASYNC)...")

            # ASYNC CHANGE: generate_content_async
            response = await model.generate_content_async(prompt)
            
            if not response.parts:
                 finish_reason = response.candidates[0].finish_reason if response.candidates else 'Unknown'
                 msg = f"Gemini returned no content. Finish reason: {finish_reason}"
                 logger.error(msg)
                 raise ValueError(msg)

            text_response = response.text
            
            if response_schema:
                try:
                    return json.loads(text_response)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from Gemini: {e}")
                    clean_text = text_response.replace("```json", "").replace("```", "").strip()
                    try:
                        return json.loads(clean_text)
                    except:
                        raise ValueError(f"Invalid JSON received from Gemini: {text_response[:100]}...")
            
            return text_response

        except Exception as e:
            logger.error(f"[GeminiProvider] Error: {e}", exc_info=True)
            raise e

class OpenAIProvider(LLMProvider):
    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None):
        from openai import AsyncOpenAI
        self.model_name = model_name
        self.client = AsyncOpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"), timeout=LLM_DEFAULT_TIMEOUT)

    @retry_strategy
    async def generate(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7
    ) -> Union[str, Dict[str, Any]]:
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            logger.info(f"[OpenAIProvider] Calling {self.model_name} (ASYNC)...")
            
            if response_schema:
                logger.info(f"[OpenAIProvider] Enforcing schema: {response_schema.__name__} (Structured Outputs)")
                completion = await self.client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=messages,
                    response_format=response_schema,
                    temperature=temperature
                )
                parsed_obj = completion.choices[0].message.parsed
                if not parsed_obj:
                     refusal = completion.choices[0].message.refusal
                     msg = f"OpenAI refused to generate structured output: {refusal}"
                     logger.error(msg)
                     raise ValueError(msg)
                
                return parsed_obj.model_dump()
            else:
                completion = await self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature
                )
                return completion.choices[0].message.content

        except Exception as e:
            logger.error(f"[OpenAIProvider] Error: {e}", exc_info=True)
            raise e

class MockProvider(LLMProvider):
    async def generate(self, prompt: str, system_instruction: Optional[str] = None, response_schema: Optional[Type[BaseModel]] = None, temperature: float = 0.7) -> Union[str, Dict[str, Any]]:
        from backend.mock_llm import MockLLMService
        logger.info(f"[MockProvider] Calling Mock Service (Simulating Async)...")
        
        # Simulate network delay for verification of async behavior
        await asyncio.sleep(0.5)

        mock = MockLLMService()
        result = mock.generate_content(prompt, system_instruction)
        
        if response_schema:
            try:
                return json.loads(result)
            except:
                logger.warning("Mock provider returned non-JSON text when schema was requested. Returning empty dict.")
                return {} 
        return result

class LLMFactory:
    @staticmethod
    def create_provider(provider_type: str = "gemini", model_name: Optional[str] = None) -> LLMProvider:
        
        if USE_MOCK_LLM:
            return MockProvider()
            
        if provider_type.lower() == "gemini":
            return GoogleGeminiProvider(model_name=model_name or "gemini-1.5-flash")
        elif provider_type.lower() == "openai":
            return OpenAIProvider(model_name=model_name or "gpt-4o")
        else:
            raise ValueError(f"Unknown provider: {provider_type}")
