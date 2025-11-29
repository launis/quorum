from typing import Any
import os
from backend.component import BaseComponent

class BaseAgent(BaseComponent):
    """
    Abstract base class for all Cognitive Quorum agents.
    Handles LLM interaction and common agent behaviors.
    """
    
    def __init__(self, model: str = "gemini-1.5-flash"):
        self.model = model
        # TODO: Initialize LLM client here (e.g., Gemini, OpenAI)
        # self.client = ...

    def execute(self, **kwargs) -> dict[str, Any]:
        """
        Standard execution entry point.
        Subclasses should implement _process to handle specific logic.
        """
        print(f"[{self.__class__.__name__}] Starting execution...")
        try:
            result = self._process(**kwargs)
            print(f"[{self.__class__.__name__}] Execution completed.")
            return result
        except Exception as e:
            print(f"[{self.__class__.__name__}] Execution failed: {e}")
            raise e

    def _process(self, **kwargs) -> dict[str, Any]:
        """
        Internal processing logic to be implemented by subclasses.
        """
        raise NotImplementedError

    def _call_llm(self, prompt: str, system_instruction: str | None = None, json_mode: bool = False) -> str:
        """
        Helper to call the LLM using Google Gemini API.
        """
        import google.generativeai as genai
        import os

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set.")

        genai.configure(api_key=api_key)
        
        # Use the model specified in the agent, default to gemini-1.5-flash if not set
        model_name = self.model if self.model else "gemini-1.5-flash"
        
        # Configure generation config
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json" if json_mode else "text/plain",
        }

        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config,
            system_instruction=system_instruction
        )

        try:
            print(f"[{self.__class__.__name__}] Calling LLM ({model_name})...")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"[{self.__class__.__name__}] LLM Call Failed: {e}")
            raise e

    def get_json_response(self, prompt: str, system_instruction: str | None = None, max_retries: int = 3) -> dict[str, Any]:
        """
        Calls the LLM and attempts to parse the response as JSON.
        Retries if parsing fails.
        """
        import json
        import re
        
        current_prompt = prompt
        
        for attempt in range(max_retries):
            # Enable JSON mode for Gemini
            response_text = self._call_llm(current_prompt, system_instruction, json_mode=True)
            
            try:
                # Try to find JSON block
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    return json.loads(json_str)
                else:
                    raise ValueError("No JSON block found in response.")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"[{self.__class__.__name__}] JSON Parse Error (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    # Append error message to prompt for next attempt
                    current_prompt += f"\n\nERROR: Your previous response was not valid JSON. Error: {str(e)}. Please try again and ensure you output ONLY valid JSON."
                else:
                    print(f"[{self.__class__.__name__}] Failed to get valid JSON after {max_retries} attempts.")
                    # Return raw text in a wrapper to avoid crashing, or raise error
                    # For robustness, let's return a special error dict
                    return {"error": "Failed to parse JSON", "raw_output": response_text}
        
        return {"error": "Unknown error"}
