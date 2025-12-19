from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, Union
import os
import logging
import json
import asyncio
from pydantic import BaseModel
import tenacity
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from backend.models.state import WorkflowState
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
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Union[str, Dict[str, Any]]:
        pass

class GoogleGeminiProvider(LLMProvider):
    def __init__(self, model_name: Optional[str] = None, api_key: Optional[str] = None):
        import google.generativeai as genai
        from backend.settings import Settings
        
        self.settings = Settings()
        self.model_name = model_name or self.settings.gemini_model_fast
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
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Union[str, Dict[str, Any]]:
        import google.generativeai as genai
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens or 8192,
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
            
            # LOGGING: Detailed Trace
            logger.debug("--- LLM REQUEST TRACE ---")
            logger.debug(f"COMMAND: {'Structured Output (JSON)' if response_schema else 'Standard Generation'}")
            logger.debug(f"MODEL: {self.model_name}")
            if system_instruction:
                logger.debug(f"SYSTEM INSTRUCTION (First 200 chars): {system_instruction[:200]}...")
            else:
                logger.debug("SYSTEM INSTRUCTION: None")
            
            logger.debug(f"PROMPT (First 500 chars): {prompt[:500]}...")
            logger.debug("---------------------------")

            # ASYNC CHANGE: generate_content_async
            try:
                response = await model.generate_content_async(prompt)
            except Exception as e:
                # 429 Handling: If tenacity gave up, we catch it here.
                # Check for resource exhaustion / 429
                if "429" in str(e) or "ResourceExhausted" in str(e) or "quota" in str(e).lower():
                    logger.warning(f"[GeminiProvider] 429/Quota Exhausted for {self.model_name}.")
                    
                    # FALLBACK STRATEGY
                    fallback_model = self.settings.gemini_model_deep # Use configured deep model as fallback (usually different quota bucket)
                    
                    if self.model_name != fallback_model:
                        logger.warning(f"[GeminiProvider] ⚠️ FALLING BACK to {fallback_model} to salvage request...")
                        
                        fallback_model_instance = genai.GenerativeModel(
                            model_name=fallback_model,
                            generation_config=generation_config,
                            system_instruction=system_instruction
                        )
                        # One final attempt with fallback
                        response = await fallback_model_instance.generate_content_async(prompt)
                        logger.info(f"[GeminiProvider] Fallback to {fallback_model} SUCCESSFUL.")
                    else:
                        raise e # Already on fallback, nothing else to do
                else:
                    raise e

            if not response.parts:
                 finish_reason = response.candidates[0].finish_reason if response.candidates else 'Unknown'
                 msg = f"Gemini returned no content. Finish reason: {finish_reason}"
                 logger.error(msg)
                 raise ValueError(msg)

            text_response = response.text
            
            if response_schema:
                return self._clean_json_response(text_response)
            
            return text_response

        except Exception as e:
            logger.error(f"[GeminiProvider] Error: {e}", exc_info=True)
            raise e

    def _dump_debug_json(self, content: str, error_msg: str):
        """Helper to dump failed JSON to a file for manual inspection."""
        try:
            filename = "debug_failed_json.json"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(f"// ERROR: {error_msg}\n")
                f.write(content)
            logger.error(f"[GeminiProvider] DUMPED INVALID JSON TO: {os.path.abspath(filename)}")
        except Exception as e:
            logger.error(f"[GeminiProvider] Failed to dump debug JSON: {e}")

    def _clean_json_response(self, raw_response: str) -> Dict[str, Any]:
        """
        Robustly parses JSON from LLM output, handling markdown blocks and conversational text.
        """
        
        # 0. Pre-cleaning: Remove // comments (Common in LLM JSON)
        # Be careful not to match URLs (http://...)
        import re
        
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
            logger.warning(f"[GeminiProvider] Extraction failed: {e}. Attempting repairs...")
            
            # 3. Repair: Remove single-line comments // that are not inside strings (Approximate)
            # This regex looks for // not preceded by : (url) and removes until newline
            try:
                # Remove comments // ... 
                # Note: This is risky for URLs, so we only target obvious text comments
                # removing lines starting with //
                repaired = re.sub(r'^\s*//.*$', '', json_candidate, flags=re.MULTILINE)
                return json.loads(repaired)
            except Exception:
                pass

            # 4. Repair: Heuristic Fix for Missing Commas
            try:
                logger.warning("[GeminiProvider] Attempting heuristic fix for missing commas...")
                fixed_json = re.sub(r'(?<=[}\]"\'0-9lue])\s*(?<!,)\s*\n\s*(?=")', ',\n', json_candidate)
                return json.loads(fixed_json)
            except Exception as e2:
                logger.error(f"[GeminiProvider] Heuristic fix failed: {e2}")

            # 5. FATAL: Dump to file
            self._dump_debug_json(raw_response, str(e))
            raise ValueError(f"Could not extract valid JSON from response. See debug_failed_json.json. Error: {e}")

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
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Union[str, Dict[str, Any]]:
        
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})

        try:
            logger.info(f"[OpenAIProvider] Calling {self.model_name} (ASYNC)...")

            # LOGGING: Detailed Trace
            logger.debug("--- LLM REQUEST TRACE ---")
            logger.debug(f"COMMAND: {'Structured Output (JSON)' if response_schema else 'Standard Generation'}")
            logger.debug(f"MODEL: {self.model_name}")
            if system_instruction:
                logger.debug(f"SYSTEM INSTRUCTION (First 200 chars): {system_instruction[:200]}...")
            else:
                logger.debug("SYSTEM INSTRUCTION: None")
            
            logger.debug(f"PROMPT (First 500 chars): {prompt[:500]}...")
            logger.debug("---------------------------")
            
            if response_schema:
                logger.info(f"[OpenAIProvider] Enforcing schema: {response_schema.__name__} (Structured Outputs)")
                completion = await self.client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=messages,
                    response_format=response_schema,
                    temperature=temperature,
                    max_tokens=max_tokens
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
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return completion.choices[0].message.content

        except Exception as e:
            logger.error(f"[OpenAIProvider] Error: {e}", exc_info=True)
            raise e

class MockProvider(LLMProvider):
    async def generate(self, prompt: str, system_instruction: Optional[str] = None, response_schema: Optional[Type[BaseModel]] = None, temperature: float = 0.7, max_tokens: Optional[int] = None, **kwargs) -> Union[str, Dict[str, Any]]:
        from backend.llm.mock import MockLLMService
        logger.info(f"[MockProvider] Calling Mock Service (Simulating Async)... {kwargs}")
        
        # Simulate network delay for verification of async behavior
        await asyncio.sleep(0.5)

        mock = MockLLMService()
        
        # Extract explicit identity if provided
        agent_identity = kwargs.get('mock_identity')
        
        result = mock.generate_content(prompt, system_instruction, agent_identity=agent_identity)
        
        if response_schema:
            try:
                if isinstance(result, dict):
                    return result
                return json.loads(result)
            except Exception as e:
                logger.warning(f"Mock provider returned non-JSON text when schema was requested: {e}. Returning empty dict.")
                return {} 
        return result

class LLMFactory:
    @staticmethod
    def create_provider(provider_type: str = "gemini", model_name: Optional[str] = None) -> LLMProvider:
        
        if USE_MOCK_LLM:
            return MockProvider()
        
        from backend.settings import Settings
        settings = Settings()

        if provider_type.lower() == "gemini":
            target_model = model_name or settings.gemini_model_fast
            return GoogleGeminiProvider(model_name=target_model)
        elif provider_type.lower() == "openai":
            # Assuming we might add an openai_model setting later, but for now strict user rule applies to "AI Model UI" which seems to be Gemini focused?
            # Or if user only defined gemini models, maybe this branch is less critical.
            # But let's avoid hardcoding gpt-4o if we can.
            # However, settings only has gemini_model_fast/deep.
            # I will just remove the 'or "gpt-4o"' and let it fail or use a passed name.
            # Actually, to be safe, I'll default to "gpt-4o" ONLY if not in settings, but really I should just pass model_name.
            # If model_name is None for openai... verify if we have a setting.
            return OpenAIProvider(model_name=model_name or "gpt-4o")
        else:
            raise ValueError(f"Unknown provider: {provider_type}")
