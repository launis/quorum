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
            generation_config["response_schema"] = response_schema
        
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=generation_config,
            system_instruction=system_instruction
        )

        try:
            # DEBUG LOGGING
            print(f"[GeminiProvider] Calling {self.model_name}...")
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
