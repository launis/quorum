import os
from typing import List, Dict, Any
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

    def call_llm(self, prompts: List[Dict[str, str]], model: str = "gemini-1.5-flash") -> str:
        """
        Calls the specified LLM model.
        """
        print(f"[LLM] Calling {model}...")
        
        # Combine prompts into a single context
        full_prompt = "\n\n".join([p['content'] for p in prompts])

        try:
            if "gemini" in model:
                return self._call_gemini(full_prompt, model)
            elif "gpt" in model:
                return self._call_openai(full_prompt, model)
            else:
                return f"[Mock Response] Unknown model: {model}"
        except Exception as e:
            print(f"[LLM] Error calling {model}: {e}")
            return f"[Error] Failed to call LLM: {e}"

    def _call_gemini(self, prompt: str, model_name: str) -> str:
        if not config.GOOGLE_API_KEY:
            return "[Error] GOOGLE_API_KEY missing."
        
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text

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
