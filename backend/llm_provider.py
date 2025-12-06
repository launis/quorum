from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Type, Union
import os
from pydantic import BaseModel
from backend.state import WorkflowState

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers (Google, OpenAI, Mock, etc.).
    This defines the 'mask' interface.
    """
    
    @abstractmethod
    def generate(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7
    ) -> Union[str, Dict[str, Any]]:
        """
        Generates content from the LLM.
        
        Args:
            prompt: The user prompt.
            system_instruction: Optional system instruction.
            response_schema: Optional Pydantic model to enforce structured output.
            temperature: Generation temperature.
            
        Returns:
            Either a string (if no schema) or a dict (if schema provided).
        """
        pass

class GoogleGeminiProvider(LLMProvider):
    def __init__(self, model_name: str = "gemini-1.5-flash", api_key: Optional[str] = None):
        import google.generativeai as genai
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found.")
        genai.configure(api_key=self.api_key)

    def _sanitize_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitizes Pydantic JSON schema for Gemini:
        1. Removes 'examples', 'title'.
        2. Inlines '$defs' references because Gemini might not support top-level $defs.
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
                        # Replace ref with the definition (recursively resolved)
                        definition = copy.deepcopy(defs[ref_name])
                        return resolve_refs(definition)
                
                # Handle anyOf (usually for Optional fields)
                if 'anyOf' in node:
                    any_of = node.pop('anyOf')
                    # Check if it's a nullable field (one of the types is 'null')
                    non_null_types = [t for t in any_of if t.get('type') != 'null']
                    
                    if len(non_null_types) == 1:
                        # It's a simple nullable field
                        # Merge the non-null type into the node
                        node.update(resolve_refs(non_null_types[0]))
                        node['nullable'] = True
                    elif non_null_types:
                        # Complex union. Gemini doesn't support anyOf.
                        # Fallback: Use the first type.
                        node.update(resolve_refs(non_null_types[0]))

                # Clean fields
                node.pop('examples', None)
                node.pop('title', None)
                node.pop('default', None) # Gemini doesn't support 'default' in schema
                node.pop('additionalProperties', None) # Gemini doesn't support 'additionalProperties'
                node.pop('maximum', None) # Gemini doesn't support 'maximum'
                node.pop('minimum', None) # Gemini doesn't support 'minimum'
                
                # Fix for "should be non-empty for OBJECT type"
                if node.get('type') == 'object' and not node.get('properties'):
                    # Gemini requires at least one property for OBJECT.
                    # We inject a dummy optional property.
                    node['properties'] = {'_dynamic_content': {'type': 'string', 'nullable': True}}

                # Recursively clean children
                new_node = {}
                for k, v in node.items():
                    if k == 'properties' and isinstance(v, dict):
                        # Special handling for properties map: recurse on values (schemas), 
                        # but DO NOT call resolve_refs on the map itself (which would strip keys like 'title')
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

    def generate(
        self, 
        prompt: str, 
        system_instruction: Optional[str] = None,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.7
    ) -> Union[str, Dict[str, Any]]:
        import google.generativeai as genai
        import json
        
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": 8192,
        }

        # 1. Structured Output (The "Magic")
        if response_schema:
            generation_config["response_mime_type"] = "application/json"
            
            # SANITIZATION: Get JSON schema and remove 'examples' + inline '$defs'
            try:
                raw_schema = response_schema.model_json_schema()
                sanitized_schema = self._sanitize_schema(raw_schema)
                generation_config["response_schema"] = sanitized_schema
            except Exception as e:
                print(f"[GeminiProvider] Schema sanitization failed: {e}. Using raw schema.")
                generation_config["response_schema"] = response_schema
        
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            system_instruction=system_instruction
        )

        try:
            # DEBUG LOGGING
            print(f"[GeminiProvider] Calling {self.model_name}...")
            if system_instruction:
                print(f"--- SYSTEM INSTRUCTION ---\n{system_instruction}\n--------------------------")
            print(f"--- PROMPT ---\n{prompt}\n--------------")

            if response_schema:
                print(f"[GeminiProvider] Enforcing schema: {response_schema.__name__}")

            response = model.generate_content(prompt)
            
            if not response.parts:
                 # Fallback for safety blocks or empty responses
                 raise ValueError(f"Gemini returned no content. Finish reason: {response.candidates[0].finish_reason if response.candidates else 'Unknown'}")

            text_response = response.text
            
            # If schema was requested, Gemini returns JSON text. We parse it here.
            if response_schema:
                try:
                    return json.loads(text_response)
                except json.JSONDecodeError:
                    # Fallback: Try to clean markdown code blocks if Gemini messed up
                    clean_text = text_response.replace("```json", "").replace("```", "").strip()
                    return json.loads(clean_text)
            
            return text_response

        except Exception as e:
            print(f"[GeminiProvider] Error: {e}")
            raise e

class OpenAIProvider(LLMProvider):
    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None):
        from openai import OpenAI
        self.model_name = model_name
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def generate(
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
            print(f"[OpenAIProvider] Calling {self.model_name}...")
            if system_instruction:
                print(f"--- SYSTEM INSTRUCTION ---\n{system_instruction}\n--------------------------")
            print(f"--- PROMPT ---\n{prompt}\n--------------")
            
            if response_schema:
                print(f"[OpenAIProvider] Enforcing schema: {response_schema.__name__} (Structured Outputs)")
                completion = self.client.beta.chat.completions.parse(
                    model=self.model_name,
                    messages=messages,
                    response_format=response_schema,
                    temperature=temperature
                )
                # OpenAI returns a parsed Pydantic object directly!
                # We convert it to dict to match the interface
                return completion.choices[0].message.parsed.model_dump()
            else:
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature
                )
                return completion.choices[0].message.content

        except Exception as e:
            print(f"[OpenAIProvider] Error: {e}")
            raise e

class MockProvider(LLMProvider):
    def generate(self, prompt: str, system_instruction: Optional[str] = None, response_schema: Optional[Type[BaseModel]] = None, temperature: float = 0.7) -> Union[str, Dict[str, Any]]:
        from backend.mock_llm import MockLLMService
        print(f"[MockProvider] Calling Mock Service...")
        if system_instruction:
            print(f"--- SYSTEM INSTRUCTION ---\n{system_instruction}\n--------------------------")
        print(f"--- PROMPT ---\n{prompt}\n--------------")

        mock = MockLLMService()
        # Mock currently returns string JSON. We might need to parse it if schema is requested.
        result = mock.generate_content(prompt, system_instruction)
        if response_schema:
            import json
            # Try to find a mock response that matches the schema or just return generic
            try:
                return json.loads(result)
            except:
                # If mock returns plain text but we wanted JSON, return empty dict or error
                return {} 
        return result

class LLMFactory:
    @staticmethod
    def create_provider(provider_type: str = "gemini", model_name: Optional[str] = None) -> LLMProvider:
        from backend.config import USE_MOCK_LLM
        
        if USE_MOCK_LLM:
            return MockProvider()
            
        if provider_type.lower() == "gemini":
            return GoogleGeminiProvider(model_name=model_name or "gemini-1.5-flash")
        elif provider_type.lower() == "openai":
            return OpenAIProvider(model_name=model_name or "gpt-4o")
        else:
            raise ValueError(f"Unknown provider: {provider_type}")
