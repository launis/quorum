from typing import Any, Optional, Type
import os
from backend.component import BaseComponent
from backend.state import WorkflowState
from backend.llm_provider import LLMFactory, LLMProvider
from pydantic import BaseModel

class BaseAgent(BaseComponent):
    """
    Abstract base class for all Cognitive Quorum agents.
    Handles LLM interaction via the Provider Pattern and manages WorkflowState.
    """
    
    def __init__(self, model: str = "gemini-1.5-flash", provider: str = "gemini"):
        self.model = model
        self.provider_type = provider
        # Initialize the provider lazily or here
        self.llm_provider: LLMProvider = LLMFactory.create_provider(provider, model)

    def execute(self, state: WorkflowState) -> WorkflowState:
        """
        Standard execution entry point.
        Takes the entire WorkflowState, processes it, and returns the updated state.
        """
        print(f"[{self.__class__.__name__}] Starting execution...")
        try:
            # 1. Construct Prompt (using state)
            user_prompt = self.construct_user_prompt(state)
            
            # 2. Get System Instruction (usually from kwargs/config, but here we might need a better way)
            # For now, we assume subclasses might have a way to get it, or we pass it in constructor.
            # In the V1 code, it was passed in kwargs. In V2, we might fetch it from DB based on agent name.
            # For this refactor, we'll assume a method `get_system_instruction()` exists or return None.
            system_instruction = self.get_system_instruction()

            # 3. Determine Output Schema (Subclasses must define this!)
            response_schema = self.get_response_schema()

            # 4. Call LLM (The "Mask" handles the details)
            response_data = self.llm_provider.generate(
                prompt=user_prompt,
                system_instruction=system_instruction,
                response_schema=response_schema
            )

            # 5. Update State
            updated_state = self._update_state(state, response_data)
            
            print(f"[{self.__class__.__name__}] Execution completed.")
            return updated_state

        except Exception as e:
            print(f"[{self.__class__.__name__}] Execution failed: {e}")
            raise e

    def construct_user_prompt(self, state: WorkflowState) -> str:
        """
        Constructs the prompt based on the current state.
        """
        raise NotImplementedError("Subclasses must implement construct_user_prompt(state)")

    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        """
        Updates the WorkflowState with the LLM response.
        """
        raise NotImplementedError("Subclasses must implement _update_state")

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        """
        Returns the Pydantic model that this agent expects as output.
        Used for Structured Outputs.
        """
        return None

    def get_system_instruction(self) -> str:
        """
        Retrieves the system instruction. 
        In a real app, this might query the DB. For now, we can return a default or override in subclasses.
        """
        # Placeholder: In the real app, this comes from the 'Step' configuration.
        # We might need to inject it or fetch it.
        return "You are a helpful AI assistant."

    def get_schema_example(self, schema: Type[BaseModel]) -> str:
        """
        Helper to extract examples from Pydantic schema for prompting (if needed).
        With Structured Outputs, this is less critical but still useful for 'style'.
        """
        try:
            config = schema.model_config
            examples = config.get('json_schema_extra', {}).get('examples')
            if examples and len(examples) > 0:
                import json
                example_json = json.dumps(examples[0], indent=2, ensure_ascii=False)
                return f"""=== MALLIVASTAUS (Seuraa tätä tyyliä) ===\n{example_json}\n======================================="""
        except Exception:
            pass
        return ""
