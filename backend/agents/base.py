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
    
    state_field: Optional[str] = None

    def __init__(self, model: str = "gemini-1.5-flash", provider: str = "gemini"):
        self.model = model
        self.provider_type = provider
        # Initialize the provider lazily or here
        self.llm_provider: LLMProvider = LLMFactory.create_provider(provider, model)

    def set_model(self, model_name: str):
        """
        Dynamically updates the agent's model preference.
        """
        self.model = model_name
        if self.llm_provider:
            self.llm_provider.model_name = model_name
            # Re-configure provider if necessary (some providers might need re-init)
            # For GeminiProvider, model_name is public attribute, used in generate()


    def _update_state(self, state: WorkflowState, response_data: Any) -> WorkflowState:
        """
        Updates the WorkflowState with the LLM response.
        Generic implementation: Uses self.state_field and self.get_response_schema().
        """
        if self.state_field and self.get_response_schema():
            try:
                SchemaClass = self.get_response_schema()
                # Validate and create Pydantic model
                validated_data = SchemaClass(**response_data)
                
                # Check if state has this field
                if hasattr(state, self.state_field):
                    setattr(state, self.state_field, validated_data)
                    logger.info(f"[{self.__class__.__name__}] Updated state.{self.state_field}")
                else:
                    # Fallback or Error? 
                    # If field missing in State model, we can't assign.
                    # Maybe allow dynamic aux_data fallback?
                    logger.warning(f"[{self.__class__.__name__}] State model missing field '{self.state_field}'. Assigning to aux_data.")
                    state.aux_data[self.state_field] = validated_data.model_dump()
                    
                return state
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] Generic state update failed: {e}")
                raise e
        
        # If no state_field defined, raise error (Subclasses must implement or define field)
        raise NotImplementedError(f"[{self.__class__.__name__}] must define 'state_field' or override '_update_state'.")
    def _generate_examples_from_schema(self, schema_class: Type[BaseModel]) -> str:
        """
        Retrieves the example from the Pydantic model's json_schema_extra.
        Used to teach the LLM the expected output format and style.
        IF no example is found, IT FETCHES MOCK DATA from `mock_data.py` as a fallback.
        """
        if not schema_class:
            return ""
            
        import json
        
        # 1. Try explicit schema examples (Legacy/Override)
        try:
            config = schema_class.model_config
            examples = config.get('json_schema_extra', {}).get('examples')
            
            if examples and len(examples) > 0:
                example_json = json.dumps(examples[0], indent=2, ensure_ascii=False)
                return f"\n\n=== RESPONSE EXAMPLE (Follow this format and style) ===\n{example_json}\n=====================================================\n"
        except Exception as e:
            logger.warning(f"[{self.__class__.__name__}] Failed to get example from schema config: {e}")

        # 2. Smart Fallback: Fetch from Mock Data (Automated)
        try:
            from backend.llm.mock_data import get_fallback_data
            
            # Map ClassName -> MockKey
            # Simple heuristic: convert "GuardAgent" -> "guard_agent"
            # Or use a map if names diverge significantly
            class_name = self.__class__.__name__
            mock_key = None
            
            mapping = {
                "GuardAgent": "guard_agent",
                "AnalystAgent": "analyst_agent",
                "ProfilerAgent": "profiler_agent",
                "LogicianAgent": "logician_agent",
                "FalsifierAgent": "falsifier_agent",
                "FactualOverseerAgent": "fact_checker_agent",  # Divergent name
                "CausalAnalystAgent": "causal_agent",
                "PerformativityDetectorAgent": "performativity_agent",
                "JudgeAgent": "judge_agent",
                "XAIReporterAgent": "xai_agent",
                "ArchivistAgent": "archivist_agent",
                "CoachAgent": "coach_agent"
            }
            
            mock_key = mapping.get(class_name)
            
            if mock_key:
                fallback_data = get_fallback_data(mock_key)
                if fallback_data and "error" not in fallback_data:
                     example_json = json.dumps(fallback_data, indent=2, ensure_ascii=False)
                     logger.info(f"[{self.__class__.__name__}] Using AUTOMATED MOCK DATA as example.")
                     return f"\n\n=== RESPONSE EXAMPLE (Follow this format and style) ===\n{example_json}\n=====================================================\n"
            
        except Exception as e:
            logger.warning(f"[{self.__class__.__name__}] Failed to fetch automated mock example: {e}")

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
            
            # 3.5. Enrich System Instruction with Examples (Few-Shot)
            if response_schema:
                examples_text = self._generate_examples_from_schema(response_schema)
                if examples_text:
                    system_instruction += examples_text
                    logger.info(f"[{self.__class__.__name__}] Injected schema examples into system instruction.")

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
            # Inject identity for MockLLM robustness
            kwargs['mock_identity'] = self.__class__.__name__
            
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


