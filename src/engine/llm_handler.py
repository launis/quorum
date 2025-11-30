import os
from typing import Any
import google.generativeai as genai
from openai import OpenAI
import config

class LLMHandler:
    def __init__(self):
        # Initialize Gemini
        if config.GOOGLE_API_KEY:
            genai.configure(api_key=config.GOOGLE_API_KEY)
        else:
            print("[LLMHandler] Warning: GOOGLE_API_KEY not found.")

        # Initialize OpenAI
        if config.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        else:
            self.openai_client = None
            print("[LLMHandler] Warning: OPENAI_API_KEY not found.")

    def _get_fallback_models(self, model_name: str) -> list[str]:
        """
        Returns a list of fallback models based on the primary model.
        """
        fallbacks = []
        if "gemini" in model_name:
            # If asking for 2.5-flash, try 2.0-flash and 2.5-flash-lite
            if "2.5-flash" in model_name:
                fallbacks = ["gemini-2.0-flash", "gemini-2.5-flash-lite"]
            # If asking for 2.5-pro, try 2.0-pro-exp or 1.5-pro
            elif "2.5-pro" in model_name:
                fallbacks = ["gemini-2.0-pro-exp", "gemini-1.5-pro"]
            # Generic fallback for any gemini model
            else:
                fallbacks = ["gemini-2.0-flash"]
        
        # Ensure we don't duplicate the primary model
        return [m for m in fallbacks if m != model_name]

    def call_llm(self, prompts: list[dict[str, str]], model: str = "gemini-1.5-flash") -> str:
        """
        Calls the specified LLM model with fallback logic.
        """
        # Combine prompts into a single context
        full_prompt = "\n\n".join([p['content'] for p in prompts])

        models_to_try = [model] + self._get_fallback_models(model)
        last_error = None

        for current_model in models_to_try:
            print(f"[LLM] Calling {current_model}...")
            print(f"--- [LLM CALL START] Model: {current_model} ---")
            print(f"{full_prompt}")
            print(f"--- [LLM CALL END] ---")
            try:
                if "gemini" in current_model:
                    return self._call_gemini(full_prompt, current_model)
                elif "gpt" in current_model:
                    return self._call_openai(full_prompt, current_model)
                else:
                    return f"[Mock Response] Unknown model: {current_model}"
            except Exception as e:
                last_error = e
                print(f"[LLM] Error calling {current_model}: {e}")
                
                # Check for Rate Limit (429) or Quota Exceeded
                is_rate_limit = "429" in str(e) or "Quota exceeded" in str(e) or "429" in str(e)
                
                if is_rate_limit:
                    print(f"[LLM] Rate limit hit for {current_model}. Switching to fallback...")
                else:
                    print(f"[LLM] Error is not strictly rate limit, but trying fallback anyway...")
                
                continue

        # If all models fail
        error_msg = f"[LLM] All models failed. Last error: {last_error}"
        print(error_msg)
        with open("llm_errors.txt", "a") as f:
            f.write(f"{error_msg}\n")
        raise last_error or Exception("All models failed")

    def _call_gemini(self, prompt: str, model_name: str) -> str:
        if not config.GOOGLE_API_KEY:
            return "[Error] GOOGLE_API_KEY missing."
        
        try:
            model = genai.GenerativeModel(model_name)
            # Use JSON mode for robustness
            generation_config = genai.types.GenerationConfig(
                response_mime_type="application/json",
                max_output_tokens=65536
            )
            response = model.generate_content(prompt, generation_config=generation_config)
            return response.text
        except Exception as e:
            error_msg = f"[LLM] Error calling {model_name}: {e}"
            print(error_msg)
            with open("llm_errors.txt", "a") as f:
                f.write(f"{error_msg}\nPrompt: {prompt[:100]}...\n\n")
            raise e

    def _call_openai(self, prompt: str, model_name: str) -> str:
        if not self.openai_client:
            return "[Error] OPENAI_API_KEY missing."

        response = self.openai_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
