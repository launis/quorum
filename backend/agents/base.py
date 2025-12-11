from typing import Any, Optional, Type
import os
from backend.core.component import BaseComponent
from backend.models.state import WorkflowState
from backend.llm.provider import LLMFactory, LLMProvider
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

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

    def get_schema_example(self, schema_class: Type[BaseModel]) -> str:
        """
        Retrieves the example from the Pydantic model's json_schema_extra.
        Used to teach the LLM the expected output format and style.
        """
        try:
            # Pydantic v2 way to access config
            config = schema_class.model_config
            examples = config.get('json_schema_extra', {}).get('examples')
            
            if examples and len(examples) > 0:
                import json
                example_json = json.dumps(examples[0], indent=2, ensure_ascii=False)
                return f"""
=== MODEL RESPONSE (Follow this format and style) ===
{example_json}
=====================================================
"""
        except Exception as e:
            logger.warning(f"[{self.__class__.__name__}] Failed to get example from schema {schema_class.__name__}: {e}")
        return ""

    async def execute(self, state: WorkflowState, system_instruction: Optional[str] = None, **kwargs) -> WorkflowState:
        """
        Standard execution entry point.
        Takes the entire WorkflowState, processes it, and returns the updated state.
        Now accepts an optional system_instruction override (for data-driven prompts).
        Key Change: Accepts **kwargs to pass parameters like max_tokens to generate.
        """
        logger.info(f"[{self.__class__.__name__}] Starting execution...")
        try:
            # 1. Use Generic User Prompt (The System Instruction carries the context)
            user_prompt = "Proceed with your task according to the system instructions."
            
            # 2. Get System Instruction
            if not system_instruction:
                # Fallback if engine didn't provide it (should not happen in new flow)
                system_instruction = "You are a helpful AI assistant."

            # 3. Determine Output Schema (Subclasses must define this!)
            response_schema = self.get_response_schema()

            # --- LOGGING EXECUTION CONFIG ---
            # Extract config to show user exactly what is running
            conf_model = self.model
            conf_temp = kwargs.get('temperature', 'Default')
            conf_tokens = kwargs.get('max_tokens', 'Default')
            
            logger.info(f"[{self.__class__.__name__}] >>> EXECUTION START <<<")
            logger.info(f"[{self.__class__.__name__}] MODEL: {conf_model} | TEMP: {conf_temp} | TOKENS: {conf_tokens}")
            # --------------------------------

            # 4. Call LLM (The "Mask" handles the details) — ASYNC WAIT
            # Pass kwargs (e.g. max_tokens) here
            response_data = await self.llm_provider.generate(
                prompt=user_prompt,
                system_instruction=system_instruction,
                response_schema=response_schema,
                **kwargs
            )

            # 5. Update State
            updated_state = self._update_state(state, response_data)
            
            logger.info(f"[{self.__class__.__name__}] Execution completed.")
            return updated_state

        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Execution failed: {e}", exc_info=True)
            raise e

    def construct_user_prompt(self, state: WorkflowState) -> str:
        """
        Deprecated: User prompts are now generic.
        """
        return "Proceed with your task."

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

    def get_user_prompt_template(self) -> str:
        """
        Returns a string representation of the user prompt template for UI preview.
        Subclasses should override this to show their specific template structure.
        """
        return "Proceed with your task according to the system instructions."


