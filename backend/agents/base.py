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
        """
        Initializes the agent with an optional specific model strategy.

        Args:
            model (Optional[str]): The model identifier (e.g. 'gemini-1.5-pro').
            provider (Optional[str]): The provider (e.g. 'google').
        """
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

        Args:
            model_name (str): The new model name.
            provider (Optional[str]): The provider type.
        """
        self.model = model_name
        if provider:
            self.provider_type = provider
            
        current_provider_type = self.provider_type or "google" # Default fallback
        
        if self.llm_provider:
             # Update existing provider
             self.llm_provider.model_name = model_name
        else:
             # Create new provider
             if current_provider_type:
                 self.llm_provider = LLMFactory.create_provider(current_provider_type, model_name)
             else:
                 logger.error(f"[BaseAgent] Cannot create LLMProvider: Provider type missing for model {model_name}")

    def _update_state(self, state: WorkflowState, response_data: Any, output_key: Optional[str] = None, **kwargs) -> WorkflowState:
        """
        Updates the WorkflowState with the LLM response.
        Generic implementation: Uses self.state_field and self.get_response_schema().

        Args:
            state (WorkflowState): Current state.
            response_data (Any): Raw data dictionary from LLM.
            output_key (Optional[str]): Override for self.state_field.

        Returns:
            WorkflowState: The updated state object.

        Raises:
            Exception: If schema validation fails.
        """
        target_field = output_key or self.state_field
        
        if target_field and self.get_response_schema():
            try:
                SchemaClass = self.get_response_schema()
                # Validate and create Pydantic model
                validated_data = SchemaClass(**response_data)
                
                # Check if state has this field
                if hasattr(state, target_field):
                    logger.debug(f"_update_state [id={id(state)}] Setting {target_field}")
                    setattr(state, target_field, validated_data)
                    logger.info(f"[{self.__class__.__name__}] Updated state.{target_field}")
                else:
                    logger.warning(f"[{self.__class__.__name__}] State model missing field '{target_field}'. Assigning to aux_data.")
                    state.aux_data[target_field] = validated_data.model_dump()
                    
                return state
            except Exception as e:
                logger.error(f"[{self.__class__.__name__}] Generic state update failed: {e}")
                raise e
        
        raise NotImplementedError(f"[{self.__class__.__name__}] must define 'state_field' or override '_update_state'.")

    async def execute(self, state: WorkflowState, system_instruction: Optional[str] = None, **kwargs) -> WorkflowState:
        """
        Standard execution entry point.
        Takes the entire WorkflowState, processes it, and returns the updated state.

        Args:
            state (WorkflowState): The current workflow context.
            system_instruction (Optional[str]): Prompt override.
            **kwargs: Additional parameters for LLM (e.g. max_tokens, temperature, output_key).

        Returns:
            WorkflowState: Updated state after execution.

        Raises:
            Exception: If execution fails.
        """
        logger.info(f"[{self.__class__.__name__}] Starting execution...")
        try:
            # 1. Use Generic User Prompt (The System Instruction carries the context)
            user_prompt = "Proceed with your task according to the system instructions."
            
            # 2. Get System Instruction
            if not system_instruction:
                system_instruction = "You are a helpful AI assistant."

            # 3. Determine Output Schema (Subclasses must define this!)
            response_schema = self.get_response_schema()

            # 3.5 Lifecycle Hook: Prepare Context
            logger.info(f"[{self.__class__.__name__}] Lifecycle Hook: prepare_context")
            additional_context = await self.prepare_context(state, **kwargs)
            if additional_context:
                system_instruction = (system_instruction or "") + "\n\n" + additional_context
                logger.debug(f"[{self.__class__.__name__}] Appended dynamic context.")
            
            # 3.6 Context Continuity Check (Stateless Reasoning)
            try:
                latest_meta = state.get_latest_reasoning_metadata()
                if latest_meta and latest_meta.get('token'):
                    prev_provider = latest_meta.get('provider')
                    curr_provider = self.provider_type or "google" # Default
                    
                    # Compatibility Check (Simple Exact Match for now)
                    if prev_provider and curr_provider and prev_provider.lower() == curr_provider.lower():
                        logger.info(f"[{self.__class__.__name__}] Chain of Thought: Injecting token from {latest_meta.get('model')} (Provider match: {curr_provider})")
                        kwargs['pass_reasoning_token'] = latest_meta['token']
                    else:
                        logger.info(f"[{self.__class__.__name__}] Chain of Thought: Skipping token (Provider mismatch: {prev_provider} != {curr_provider})")
            except Exception as e:
                logger.warning(f"Error in context continuity check: {e}")

            # --- LOGGING EXECUTION CONFIG ---
            conf_model = self.model
            conf_temp = kwargs.get('temperature', 'Default')
            conf_tokens = kwargs.get('max_tokens', 'Default')
            
            logger.info(f"[{self.__class__.__name__}] >>> EXECUTION START <<<")
            logger.info(f"[{self.__class__.__name__}] MODEL: {conf_model} | TEMP: {conf_temp} | TOKENS: {conf_tokens}")
            # --------------------------------
            
            # 4. Call LLM (The "Mask" handles the details) — ASYNC WAIT
            kwargs['mock_identity'] = self.__class__.__name__
            
            response_obj = await self.llm_provider.generate(
                prompt=user_prompt,
                system_instruction=system_instruction,
                response_schema=response_schema,
                **kwargs
            )

            # Handle Response Content
            if response_schema:
                 # Provider ensures content is valid JSON string if schema was used
                import json
                try:
                    response_data = json.loads(response_obj.content)
                except:
                    # Fallback if provider failed to ensure robust JSON (should generally be handled in provider)
                    response_data = response_obj.content 
            else:
                response_data = response_obj.content

            # Store reasoning_token if captured
            if response_obj.reasoning_token:
                logger.info(f"[{self.__class__.__name__}] Reasoning Token captured (Size: {len(response_obj.reasoning_token)})")
                target_key = kwargs.get('output_key') or self.state_field or self.__class__.__name__
                state.reasoning_context[target_key] = {
                    "token": response_obj.reasoning_token,
                    "model": self.model or "unknown",
                    "provider": self.provider_type or "google"
                }

            # 5. Update State
            output_key = kwargs.get('output_key')
            # Remove output_key from kwargs to avoid "multiple values" error when passing both explicit arg and **kwargs
            update_kwargs = {k: v for k, v in kwargs.items() if k != 'output_key'}
            updated_state = self._update_state(state, response_data, output_key=output_key, **update_kwargs)
            
            # 6. Lifecycle Hook: Post Process
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
        Override to inject dynamic context.

        Args:
            state (WorkflowState): Current state.
            **kwargs: execution arguments.

        Returns:
            Optional[str]: Text to append to system instruction.
        """
        return None

    def post_process(self, state: WorkflowState) -> WorkflowState:
        """
        Lifecycle Hook: Post-Execution.
        Override to refine state or perform calculations.

        Args:
            state (WorkflowState): Current state.

        Returns:
            WorkflowState: Processed state.
        """
        return state

    def construct_user_prompt(self, state: WorkflowState) -> str:
        """
        Deprecated: User prompts are now generic.
        
        Args:
            state (WorkflowState): Context.

        Returns:
            str: Prompt text.
        """
        return "Proceed with your task."

    def get_response_schema(self) -> Optional[Type[BaseModel]]:
        """
        Returns the Pydantic model that this agent expects as output.

        Returns:
            Optional[Type[BaseModel]]: The Pydantic output schema class.
        """
        return None

    def get_system_instruction(self) -> str:
        """
        Retrieves the default system instruction.

        Returns:
            str: Default instruction text.
        """
        return "You are a helpful AI assistant."

    def get_user_prompt_template(self) -> str:
        """
        Returns a string representation of the user prompt template for UI preview.

        Returns:
            str: Template preview.
        """
        return "Proceed with your task according to the system instructions."
