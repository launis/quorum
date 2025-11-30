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

    def construct_user_prompt(self, **kwargs) -> str:
        """
        Constructs the user content part of the prompt.
        Subclasses should implement this to separate prompt construction from execution.
        """
        raise NotImplementedError("Subclasses must implement construct_user_prompt")

    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    import google.api_core.exceptions

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((
            google.api_core.exceptions.ServiceUnavailable,
            google.api_core.exceptions.DeadlineExceeded,
            ConnectionError,
            TimeoutError
        )),
        reraise=True
    )
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
            
            # Robustly handle response
            if response.parts:
                return response.text
            
            # Handle cases where finish_reason is MAX_TOKENS but no parts (rare but possible in some API versions)
            # or SAFETY blocks
            if response.candidates:
                candidate = response.candidates[0]
                if candidate.finish_reason == 2: # MAX_TOKENS
                     # Try to get text from parts if they exist, otherwise return empty or error
                     if candidate.content and candidate.content.parts:
                         return candidate.content.parts[0].text
                     else:
                         print(f"[{self.__class__.__name__}] Warning: MAX_TOKENS reached but no content returned.")
                         return "" # Return empty string to allow retry or partial processing
                elif candidate.finish_reason == 3: # SAFETY
                     raise ValueError(f"Response blocked by safety filters. Ratings: {candidate.safety_ratings}")
            
            raise ValueError(f"No content returned. Finish reason: {response.candidates[0].finish_reason if response.candidates else 'Unknown'}")

        except Exception as e:
            print(f"[{self.__class__.__name__}] LLM Call Failed: {e}")
            raise e

    def get_json_response(self, prompt: str, system_instruction: str | None = None, max_retries: int = 3) -> dict[str, Any]:
        """
        Calls the LLM and attempts to parse the response as JSON.
        Retries if parsing fails.
        """
        from backend.hooks import _clean_and_parse_json
        
        current_prompt = prompt
        
        for attempt in range(max_retries):
            # Enable JSON mode for Gemini
            response_text = self._call_llm(current_prompt, system_instruction, json_mode=True)
            
            # Use robust parsing from hooks
            parsed_json = _clean_and_parse_json(response_text)
            
            if parsed_json and "raw_output" not in parsed_json:
                 return parsed_json
            
            # If parsing failed (returned dict with raw_output only) or returned empty
            if not parsed_json or "raw_output" in parsed_json:
                print(f"[{self.__class__.__name__}] JSON Parse Error (Attempt {attempt+1}/{max_retries}): Failed to parse.")
                if attempt < max_retries - 1:
                    # Append error message to prompt for next attempt
                    current_prompt += f"\n\nERROR: Your previous response was not valid JSON. Please try again and ensure you output ONLY valid JSON."
                else:
                    print(f"[{self.__class__.__name__}] Failed to get valid JSON after {max_retries} attempts.")
                    return {"error": "Failed to parse JSON", "raw_output": response_text}
        
        return {"error": "Unknown error"}
