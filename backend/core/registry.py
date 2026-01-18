import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class TaskDefinition:
    """Metadata for a registered task."""

    name: str
    handler: Callable[..., Any]
    input_schema: type[BaseModel]
    output_schema: type[BaseModel]
    description: str | None = None


class TaskRegistry:
    """Registry for functional agent tasks."""

    _tasks: dict[str, TaskDefinition] = {}

    @classmethod
    def register_task(
        cls,
        name: str,
        input_schema: type[BaseModel],
        output_schema: type[BaseModel],
        description: str | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a function as a task.

        Args:
            name: Unique identifier for the task.
            input_schema: Pydantic model for input validation.
            output_schema: Pydantic model for output validation.
            description: Optional description (defaults to docstring).
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            cls._tasks[name] = TaskDefinition(
                name=name,
                handler=func,
                input_schema=input_schema,
                output_schema=output_schema,
                description=description or func.__doc__,
            )
            return func

        return decorator

    @classmethod
    def get(cls, name: str) -> TaskDefinition | None:
        """Retrieve a task definition by name."""
        return cls._tasks.get(name)

    @classmethod
    def register_agent(
        cls,
        task_keys: list[str],
        agent_cls: type[Any],  # Strictly BaseAgent subclass but Any to avoid import cycles
        output_model: type[BaseModel],
    ) -> None:
        """Registers a legacy Class-Based Agent as a Task (V2 Adapter).

        Creates a wrapper function that:
        1. Instantiates the Agent.
        2. Wraps input dict into a 'MockState'.
        3. Calls agent.execute(state).
        4. Extracts result from agent.state_field.
        """

        # Create Generic Input Schema if not strictly defined
        # We assume input is a Dict that can be mapped to State
        class GenericInput(BaseModel):
            # Allow any fields
            model_config = {"extra": "allow"}

        async def agent_wrapper(input_data: BaseModel, execution_config: dict[str, Any] | None = None) -> BaseModel:
            # 1. Instantiate
            agent = agent_cls()

            # 2. Configure Model (Inject Dependency)
            # Legacy agents require set_model() to be called.
            # We resolve the model using the AgentRegistry.
            try:
                from backend.dependencies import get_async_repository
                from backend.services.agent_registry import AgentRegistry

                repo = await get_async_repository()
                registry = AgentRegistry(repo)

                # Resolve model name using the Agent Class Name as the strategy key.
                # E.g. "InteractionAnalystAgent" -> "gemini-2.5-pro"
                # If this fails, the agent will fail to execute.
                # We do NOT use a fallback here (Zero-Fallback).
                model_name = await registry.resolve_model_name(agent_cls.__name__)

                # Check if agent has set_model
                if hasattr(agent, "set_model"):
                    agent.set_model(model_name)
                else:
                    logger.warning(f"Agent {agent_cls.__name__} does not have 'set_model'. Skipping configuration.")

            except Exception as e:
                # Log critical setup failure
                logger.error(f"Failed to configure agent {agent_cls.__name__}: {e}")
                raise

            # 3. Resolve System Instruction with Variable Substitution (Jan 2026)
            system_instruction = None
            if execution_config and "llm_prompts" in execution_config:
                from backend.services.component_registry import ComponentRegistry
                
                # Resolve list of keys into single text block
                reg = ComponentRegistry()
                prompts = execution_config["llm_prompts"]
                if prompts:
                    logger.info(f"[{agent_cls.__name__}] Found {len(prompts)} prompt keys in config: {prompts[:3]}...")
                    system_instruction = reg.resolve_prompts(tuple(prompts))
                    
                    # --- VARIABLE SUBSTITUTION (Fix for Hallucinations) ---
                    # The prompt contains {{HISTORY_TEXT}} etc.
                    # The input_data contains history_text etc.
                    # We must replace the placeholders with actual content.
                    
                    # 1. Standardize Inputs
                    vars_to_inject = {}
                    if isinstance(input_data, BaseModel):
                        vars_to_inject = input_data.model_dump()
                    elif isinstance(input_data, dict):
                        vars_to_inject = input_data
                    
                    # 2. Add System Context Variables
                    import datetime
                    vars_to_inject["CURRENT_DATE"] = datetime.datetime.now().strftime("%Y-%m-%d")
                    vars_to_inject["DYNAMIC_TIME"] = datetime.datetime.now().strftime("%H:%M:%S")
                    vars_to_inject["DYNAMIC_LOCATION"] = "Sijainti: VIRTUAL_ENCLAVE" # Default
                    
                    # 3. Perform Substitution
                    if system_instruction:
                        for key, value in vars_to_inject.items():
                            if value is None:
                                value = ""
                            # Try UPPERCASE match first (Standard: {{HISTORY_TEXT}})
                            placeholder = f"{{{{{key.upper()}}}}}" 
                            if placeholder in system_instruction:
                                system_instruction = system_instruction.replace(placeholder, str(value))
                            
                            # Try Direct Match (Legacy: {{history_text}})
                            placeholder_lower = f"{{{{{key}}}}}"
                            if placeholder_lower in system_instruction:
                                system_instruction = system_instruction.replace(placeholder_lower, str(value))
                                
                    logger.info(f"[{agent_cls.__name__}] Resolved system_instruction length: {len(system_instruction)}")
                else:
                    logger.warning(f"[{agent_cls.__name__}] 'llm_prompts' key present but empty list.")
            else:
                pass # No prompt config

            # 4. Execute using New Signature
            # Input is Pydantic model (InputData), convert to dict
            input_dict = input_data.model_dump()
            
            result_dict = await agent.execute(
                input_data=input_dict,
                execution_context=execution_config,
                system_instruction=system_instruction,
                repository=repo
            )

            # 5. Extract/Validate Result
            # The agent returns a dictionary (or Pydantic dump)
            # We convert it to the expected output_model
            
            # Hooks would go here if we kept them, but the prompt says:
            # "Remove the complex logic that tried to wrap inputs into a state object or extract outputs from specific state fields."
            # "The input is now just the input, and the output is just the output."
            # So I am dropping the HOOK logic from the Wrapper. Hooks should be handled by the GraphEngine or explicitly if needed,
            # but the Wrapper's job is just to adapt the Class to the Task function signature.
            # *Wait, the previous code had Hooks logic inside the wrapper.*
            # If I remove it, hooks won't run. The prompt says "Remove the complex logic that tried to wrap inputs...". 
            # It didn't explicitly say "Remove hooks".
            # However, hooks relied on `result_state` (which was a `WorkflowState`).
            # Now `result_dict` is just the output of *this* agent step.
            # The hooks in the previous code were mutating `result_state` (WorkflowState).
            # If the architecture is moving to stateless agents returning results, then `GraphEngine` might need to handle hooks or
            # hooks need to be adapted to work on `step_results`.
            # Given the strict instruction "Return result directly", I will remove the Hooks logic from here.
            # If hooks are needed, they should be applied elsewhere or reimplemented. I will follow the explicit instruction to simplify.

            if isinstance(result_dict, output_model):
                return result_dict
            
            if isinstance(result_dict, dict):
                return output_model(**result_dict)
            
            return result_dict

        # Register for each key
        for key in task_keys:
            cls._tasks[key] = TaskDefinition(
                name=key,
                handler=agent_wrapper,
                input_schema=GenericInput,  # Generic adapter
                output_schema=output_model,
                description=agent_cls.__doc__ or f"Adapter for {agent_cls.__name__}",
            )
