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
    metadata: dict[str, Any] | None = None


class TaskRegistry:
    """Registry for functional agent tasks."""
    _tasks: dict[str, TaskDefinition] = {}
    agents_map: dict[str, Any] = {}

    @classmethod
    def register_task(
        cls,
        name: str,
        input_schema: type[BaseModel],
        output_schema: type[BaseModel],
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a function as a task.

        Args:
            name: Unique identifier for the task.
            input_schema: Pydantic model for input validation.
            output_schema: Pydantic model for output validation.
            description: Optional description (defaults to docstring).
            metadata: Optional metadata for the task.
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            cls._tasks[name] = TaskDefinition(
                name=name,
                handler=func,
                input_schema=input_schema,
                output_schema=output_schema,
                description=description or func.__doc__,
                metadata=metadata or {},
            )
            return func

        return decorator

    @classmethod
    def get(cls, name: str) -> TaskDefinition | None:
        """Retrieve a task definition by name."""
        return cls._tasks.get(name)

    @classmethod
    def get_all_agents(cls) -> dict[str, Any]:
        """Retrieve all registered agents as instances."""
        return cls.agents_map

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
        # Populate Metadata Registry
        try:
            cls.agents_map[agent_cls.__name__] = agent_cls()
        except Exception as e:
            logger.error(f"Could not instantiate {agent_cls.__name__} for metadata: {e}")
            from backend.exceptions import AppException, ErrorCodes, status
            raise AppException(
                message=f"Agent {agent_cls.__name__} instantiation failed: {e}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR, "original_error": str(e)}
            ) from e

        # Resolve Input Schema from Agent Class (Refactored Feb 2026: Strict Type Propagation)
        input_model = getattr(agent_cls, "INPUT_SCHEMA", None)
        if not input_model:
             # Fallback to Generic if not defined (Legacy support only)
             logger.warning(f"Agent {agent_cls.__name__} has no INPUT_SCHEMA. Using GenericInput (Dict fallback).")
             class GenericInput(BaseModel):
                 model_config = {"extra": "allow"}
             input_model = GenericInput

        async def agent_wrapper(input_data: BaseModel, execution_config: dict[str, Any] | None = None) -> BaseModel:
            logger.debug(f"agent_wrapper CALLED. Config: {execution_config}")
            # 1. Instantiate
            agent = agent_cls()

            # 2. Configure Model (Inject Dependency)
            try:
                from backend.dependencies import get_async_repository
                from backend.services.agent_registry import AgentRegistry

                repo = await get_async_repository()
                registry = AgentRegistry(repo)
                model_config = await registry.resolve_model_config(agent_cls.__name__)
                
                if hasattr(agent, "set_model"):
                    agent.set_model(model_config.model_name, provider=model_config.provider, config=model_config)
            except Exception as e:
                logger.error(f"Failed to configure agent {agent_cls.__name__}: {e}")
                from backend.exceptions import AppException, ErrorCodes, status
                if isinstance(e, AppException):
                    raise e
                raise AppException(
                    message=f"Agent configuration failed: {e}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.AGENT_NOT_CONFIGURED, "agent": agent_cls.__name__, "original_error": str(e)}
                ) from e

            # 3. Resolve System Instruction
            system_instruction = None
            if execution_config and "llm_prompts" in execution_config:
                from backend.services.component_registry import ComponentRegistry

                prompts = execution_config["llm_prompts"]
                if prompts:
                    prompt_map = await ComponentRegistry.resolve_prompts_map(repo, tuple(prompts))
                    system_instruction = "\n\n".join(prompt_map.values())

                    if execution_config is None:
                        execution_config = {}
                    execution_config.update(prompt_map)

                    # --- VARIABLE SUBSTITUTION ---
                    # Use model_dump to get dict for substitution logic
                    vars_to_inject = input_data.model_dump() if hasattr(input_data, "model_dump") else {}
                    if isinstance(input_data, dict): # Should not happen if strictly typed
                        vars_to_inject = input_data

                    # System Context
                    from datetime import datetime, UTC
                    vars_to_inject["CURRENT_DATE"] = datetime.now(UTC).strftime("%Y-%m-%d")
                    vars_to_inject["DYNAMIC_TIME"] = datetime.now(UTC).strftime("%H:%M:%S")
                    vars_to_inject["DYNAMIC_LOCATION"] = "Sijainti: VIRTUAL_ENCLAVE"

                    if system_instruction:
                        for key, value in vars_to_inject.items():
                            if value is None: value = ""
                            if hasattr(value, "model_dump_json"): replacement = value.model_dump_json()
                            elif hasattr(value, "dict"): import json; replacement = json.dumps(value.dict(), default=str)
                            else: replacement = str(value)

                            placeholder = f"{{{{{key.upper()}}}}}"
                            if placeholder in system_instruction:
                                system_instruction = system_instruction.replace(placeholder, replacement)
                            placeholder_lower = f"{{{{{key}}}}}"
                            if placeholder_lower in system_instruction:
                                system_instruction = system_instruction.replace(placeholder_lower, replacement)

            # 4. Execute using New Signature (Strict Model Pass-Through)
            # Do NOT downcast to dict unless it's GenericInput
            final_input = input_data
            if input_model.__name__ == "GenericInput":
                 # Legacy: Convert to dict for agents expecting dict
                 final_input = input_data.model_dump()

            # Prepare kwargs from Registry Config
            registry_kwargs = {}
            model_config_dict = model_config.model_dump()
            for k, v in model_config_dict.items():
                if k in ["temperature", "max_tokens", "top_p", "top_k", "frequency_penalty", "presence_penalty"]:
                    registry_kwargs[k] = v

            # Apply Execution Config Override
            exec_kwargs = registry_kwargs.copy()
            if execution_config:
                if "model" in execution_config:
                    override_model = execution_config["model"]
                    try:
                        resolved_override = await registry.resolve_model_name(override_model)
                        execution_config["model"] = resolved_override
                    except Exception:
                         pass # Warning logged in original code
                exec_kwargs.update(execution_config)

            # CALL EXECUTE
            # logic to handle missing kwargs if strict signature
            # But BaseAgent allows **kwargs.
            result_dict = await agent.execute(
                input_data=final_input,
                execution_context=execution_config,
                system_instruction=system_instruction,
                repository=repo,
                **exec_kwargs,
            )

            # 5. Extract/Validate Result
            if isinstance(result_dict, output_model):
                return result_dict

            if isinstance(result_dict, dict):
                return output_model(**result_dict)

            return result_dict

        # Register for each key
        for key in task_keys:
            agent_type = "critic" if "critic" in agent_cls.__name__.lower() else "agent"

            cls._tasks[key] = TaskDefinition(
                name=key,
                handler=agent_wrapper,
                input_schema=input_model,  # Strict Schema from Agent
                output_schema=output_model,
                description=agent_cls.__doc__ or f"Adapter for {agent_cls.__name__}",
                metadata={"agent_class": agent_cls.__name__, "module": agent_cls.__module__, "type": agent_type},
            )
