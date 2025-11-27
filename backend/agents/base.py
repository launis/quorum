from typing import Dict, Any, Optional
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

    def execute(self, **kwargs) -> Dict[str, Any]:
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

    def _process(self, **kwargs) -> Dict[str, Any]:
        """
        Internal processing logic to be implemented by subclasses.
        """
        raise NotImplementedError

    def _call_llm(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
        Helper to call the LLM.
        Currently a MOCK implementation for prototyping.
        """
        # TODO: Replace with actual API call
        print(f"[{self.__class__.__name__}] Calling LLM with prompt length: {len(prompt)}")
        if system_instruction:
            print(f"[{self.__class__.__name__}] System Instruction: {system_instruction[:50]}...")
        return f"[MOCK LLM RESPONSE from {self.model}]"
