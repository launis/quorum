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
    
    # --- CONTRACTS (Data Flow Validation) ---
    # List of keys (in state or inputs) that this agent REQUIRES to run.
    REQUIRES_KEYS: list[str] = []
    
    # List of keys (in state) that this agent PRODUCES upon success.
    PRODUCES_KEYS: list[str] = []
    
    # Optional Pydantic Models for Schema Validation
    INPUT_SCHEMA: Optional[Type[BaseModel]] = None
    OUTPUT_SCHEMA: Optional[Type[BaseModel]] = None

    def __init__(self, model: Optional[str] = None, provider: Optional[str] = None):
        if model and "gemini" in model.lower():
             logger.warning(f"[BaseAgent] Hardcoded 'gemini' detected in model init: {model}")
             
        self.model = model
        self.provider_type = provider
        
        # Initialize the provider lazily or here
        if provider and model:
            self.llm_provider: LLMProvider = LLMFactory.create_provider(provider, model)
        else:
            self.llm_provider = None # Must be set via configure() or similar

    def set_model(self, model_name: str, provider: Optional[str] = None):
        """
        Dynamically updates the agent's model preference and ensures LLMProvider is ready.
        """
        self.model = model_name
        if provider:
            self.provider_type = provider
            
        # If provider type is known (either passed now or in init), ensuring we have a provider instance
        current_provider_type = self.provider_type or "google" # Default fallback if somehow missing, though Runner should provide it
        
        if self.llm_provider:
             # Update existing provider
             self.llm_provider.model_name = model_name
             # If provider type changed, we might need to recreate? 
             # For now assuming same provider class structure or just updating name.
             # Ideally we should recreate if provider type differs.
        else:
             # Create new provider
             if current_provider_type:
                 self.llm_provider = LLMFactory.create_provider(current_provider_type, model_name)
             else:
                 logger.error(f"[BaseAgent] Cannot create LLMProvider: Provider type missing for model {model_name}")


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

            # 3.5 Lifecycle Hook: Prepare Context
            # Allow subclasses to inject dynamic context or modify state before execution.
            logger.info(f"[{self.__class__.__name__}] Lifecycle Hook: prepare_context")
            additional_context = await self.prepare_context(state, **kwargs)
            if additional_context:
                system_instruction = (system_instruction or "") + "\n\n" + additional_context
                logger.debug(f"[{self.__class__.__name__}] Appended dynamic context.")
            
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
            
            # 6. Lifecycle Hook: Post Process
            # Allow subclasses to refine the state after LLM output (e.g. calculations, enrichment)
            logger.info(f"[{self.__class__.__name__}] Lifecycle Hook: post_process")
            updated_state = self.post_process(updated_state)

            logger.info(f"[{self.__class__.__name__}] Execution completed.")
            return updated_state

        except Exception as e:
            logger.error(f"[{self.__class__.__name__}] Execution failed: {e}", exc_info=True)
            raise e

    async def prepare_context(self, state: WorkflowState, **kwargs) -> Optional[str]:
        """
        Lifecycle Hook: Pre-Execution.
        Override this to:
        - Fetch external data (DB/Web)
        - Check inputs (Guard)
        - Return a string to be appended to the System Instruction.
        """
        return None

    def post_process(self, state: WorkflowState) -> WorkflowState:
        """
        Lifecycle Hook: Post-Execution.
        Override this to:
        - Perform calculations (Judge)
        - Enrich data (Coach)
        - Verify constraints
        """
        return state

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


