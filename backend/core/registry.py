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
                    # If it's not a BaseAgent or doesn't have set_model, we assume it's self-configured?
                    # Or maybe it's a functional agent wrapped in a class?
                    # We log warning but proceed.
                    logger.warning(f"Agent {agent_cls.__name__} does not have 'set_model'. Skipping configuration.")

            except Exception as e:
                # Log critical setup failure
                logger.error(f"Failed to configure agent {agent_cls.__name__}: {e}")
                raise

            # 3. Mock State
            class MockState:
                def __init__(self, data):
                    self._data = data
                    # Enable dot notation for inputs (like Pydantic models)
                    self.inputs = type("Inputs", (), data)()
                    self.aux_data = {"search_results": []}
                    self.reasoning_context = {}
                    self.last_reasoning_trace = None
                    self.usage = {}
                    self.audit_results = {}

                def __getattr__(self, name):
                    return self._data.get(name)

                def __setattr__(self, name, value):
                    if name in ["inputs", "aux_data", "_data"]:
                        super().__setattr__(name, value)
                    else:
                        self._data[name] = value

                def model_dump(self):
                    return self._data

            # Convert Pydantic input to dict
            data_dict = input_data.model_dump()
            state = MockState(data_dict)

            # 4. Prompt Resolution (Strict Observability - Jan 2026)
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
                logger.warning(f"[{agent_cls.__name__}] No 'llm_prompts' in execution_config.")

            # 5. Execute
            # Inject repository if available (resolved above)
            # We pass it in kwargs so agents like JudgeAgent can check it in prepare_context
            result_state = await agent.execute(
                state, 
                system_instruction=system_instruction,
                execution_config=execution_config, 
                repository=repo
            )

            # 4.5 HOOK EXECUTION (Centralized Registry - Jan 2026)
            # Define supported hooks (available for both pre_hooks and post_hooks)
            # Note: Some hooks use _hook suffix wrappers for WorkflowState compatibility
            HOOK_MAPPING = {
                # Reporting & Output
                "generate_report": ("backend.hooks.reporting", "generate_report"),
                # Validation & Structure
                "verify_structure": ("backend.hooks.validation", "verify_structure"),
                # Search & External
                "execute_google_search": ("backend.hooks.search", "execute_google_search"),
                # Security & PII (use wrapper functions)
                "sanitize_text": ("backend.hooks.security", "sanitize_text_hook"),
                "check_banned_phrases": ("backend.hooks.security", "check_banned_phrases_hook"),
                # Metrics & Analysis (use wrapper functions)
                "calculate_text_metrics": ("backend.hooks.metrics", "calculate_text_metrics_hook"),
                "calculate_control_ratio": ("backend.hooks.metrics", "calculate_control_ratio_hook"),
                # Linguistics
                "detect_performative_patterns": ("backend.hooks.linguistics", "detect_performative_patterns"),
                # Scoring
                "apply_scoring_logic": ("backend.hooks.scoring", "apply_scoring_logic"),
                # Archival
                "retrieve_precedent": ("backend.hooks.archival", "retrieve_precedent"),
                # References (use wrapper function)
                "generate_bibliography": ("backend.hooks.references", "generate_bibliography_hook"),
            }

            # Helper function to execute hooks
            async def _execute_hooks(hook_list, hook_type):
                nonlocal result_state
                for hook_name in hook_list:
                    if hook_name in HOOK_MAPPING:
                        module_path, func_name = HOOK_MAPPING[hook_name]
                        try:
                            import asyncio
                            import importlib

                            module = importlib.import_module(module_path)
                            if hasattr(module, func_name):
                                hook_func = getattr(module, func_name)
                                # Support both sync and async hooks
                                if asyncio.iscoroutinefunction(hook_func):
                                    result_state = await hook_func(result_state)
                                else:
                                    result_state = hook_func(result_state)
                                logger.info(f"Executed {hook_type} '{hook_name}' successfully.")
                        except Exception as e:
                            logger.error(f"Failed to execute {hook_type} '{hook_name}': {e}")
                    else:
                        logger.warning(f"Hook '{hook_name}' not found in HOOK_MAPPING.")

            # Execute pre_hooks (before result extraction, but after agent execution)
            if execution_config and "pre_hooks" in execution_config:
                hooks = execution_config.get("pre_hooks") or []
                if hooks:
                    await _execute_hooks(hooks, "pre_hook")

            # Execute post_hooks (after agent output, for scoring/validation)
            if execution_config and "post_hooks" in execution_config:
                post_hooks = execution_config.get("post_hooks") or []
                if post_hooks:
                    await _execute_hooks(post_hooks, "post_hook")

            # 5. Extract Result
            field = getattr(agent, "state_field", None)
            if not field:
                field = task_keys[0]

            output_val = getattr(result_state, field, None)
            if output_val is None and hasattr(result_state, "_data"):
                output_val = result_state._data.get(field)

            # Check audit_results (specifically for Judge/Critic agents)
            if output_val is None and getattr(result_state, "audit_results", None):
                output_val = result_state.audit_results.get(field)

            if output_val is None:
                raise ValueError(f"Agent {agent_cls.__name__} did not produce output in field '{field}'.")

            # CRITICAL FIX: Propagate xai_report_formatted if present in State (from hooks)
            # This ensures GraphEngine hoisting logic works
            if hasattr(result_state, "xai_report_formatted") and result_state.xai_report_formatted:
                if isinstance(output_val, dict):
                    output_val["xai_report_formatted"] = result_state.xai_report_formatted
                elif hasattr(output_val, "xai_report_formatted"):  # Pydantic Model
                    try:
                        output_val.xai_report_formatted = result_state.xai_report_formatted
                    except Exception:
                        pass

            if isinstance(output_val, dict):
                return output_model(**output_val)
            return output_val

        # Register for each key
        for key in task_keys:
            cls._tasks[key] = TaskDefinition(
                name=key,
                handler=agent_wrapper,
                input_schema=GenericInput,  # Generic adapter
                output_schema=output_model,
                description=agent_cls.__doc__ or f"Adapter for {agent_cls.__name__}",
            )
