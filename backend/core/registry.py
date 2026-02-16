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

        # Create Generic Input Schema if not strictly defined
        # We assume input is a Dict that can be mapped to State
        class GenericInput(BaseModel):
            # Allow any fields
            model_config = {"extra": "allow"}

        async def agent_wrapper(input_data: BaseModel, execution_config: dict[str, Any] | None = None) -> BaseModel:
            logger.debug(f"agent_wrapper CALLED. Config: {execution_config}")
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

                # Resolve model config using the Agent Class Name as the strategy key.
                # E.g. "InteractionAnalystAgent" -> {"model_name": "gemini-2.5-pro", "temperature": 0.0, ...}
                model_config = await registry.resolve_model_config(agent_cls.__name__)
                model_name = model_config.get("model_name")
                provider_type = model_config.get("provider")

                # Check if agent has set_model
                if hasattr(agent, "set_model"):
                    agent.set_model(model_name, provider=provider_type)
                else:
                    logger.warning(f"Agent {agent_cls.__name__} does not have 'set_model'. Skipping configuration.")

            except Exception as e:
                # Log critical setup failure
                logger.error(f"Failed to configure agent {agent_cls.__name__}: {e}")
                from backend.exceptions import AppException, ErrorCodes, status
                if isinstance(e, AppException):
                    raise e
                raise AppException(
                    message=f"Agent configuration failed: {e}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={"error_code": ErrorCodes.AGENT_NOT_CONFIGURED, "agent": agent_cls.__name__, "original_error": str(e)}
                ) from e

            # 3. Resolve System Instruction with Variable Substitution (Jan 2026)
            system_instruction = None
            if execution_config and "llm_prompts" in execution_config:
                from backend.services.component_registry import ComponentRegistry

                # Resolve list of keys into single text block
                # Resolve list of keys into single text block
                # Refactored Feb 2026: Use static async method with repository
                prompts = execution_config["llm_prompts"]
                if prompts:
                    logger.info(f"[{agent_cls.__name__}] Found {len(prompts)} prompt keys in config: {prompts[:3]}...")
                    system_instruction = await ComponentRegistry.resolve_prompts(repo, tuple(prompts))

                    # --- VARIABLE SUBSTITUTION (Fix for Hallucinations) ---
                    # The prompt contains {{HISTORY_TEXT}} etc.
                    # The input_data contains history_text etc.
                    # We must replace the placeholders with actual content.

                    # 1. Standardize Inputs
                    # 1. Standardize Inputs (Pure Object Flow)
                    # Do NOT use model_dump() here as it recursively flattens nested objects into dicts.
                    # We want to keep nested objects (e.g. TextMetrics) as objects so we can call
                    # .model_dump_json() on them.
                    if hasattr(input_data, "model_dump"):
                        # Iterating over the model yields (key, value) pairs where value keeps its type
                        # (Object)
                        vars_to_inject = dict(input_data)
                    elif isinstance(input_data, dict):
                        vars_to_inject = input_data
                    else:
                        vars_to_inject = {}

                    # 2. Add System Context Variables
                    from datetime import datetime

                    vars_to_inject["CURRENT_DATE"] = datetime.now().strftime("%Y-%m-%d")
                    vars_to_inject["DYNAMIC_TIME"] = datetime.now().strftime("%H:%M:%S")
                    vars_to_inject["DYNAMIC_LOCATION"] = "Sijainti: VIRTUAL_ENCLAVE"  # Default

                    # 3. Perform Substitution
                    if system_instruction:
                        for key, value in vars_to_inject.items():
                            if value is None:
                                value = ""
                            # SERIALIZATION FIX: Handle Pydantic models gracefully
                            if hasattr(value, "model_dump_json"):
                                replacement = value.model_dump_json()
                            elif hasattr(value, "dict"):
                                import json

                                replacement = json.dumps(value.dict(), default=str)
                            else:
                                replacement = str(value)

                            # Try UPPERCASE match first (Standard: {{HISTORY_TEXT}})
                            placeholder = f"{{{{{key.upper()}}}}}"
                            if placeholder in system_instruction:
                                system_instruction = system_instruction.replace(placeholder, replacement)

                            # Try Direct Match (Legacy: {{history_text}})
                            placeholder_lower = f"{{{{{key}}}}}"
                            if placeholder_lower in system_instruction:
                                system_instruction = system_instruction.replace(placeholder_lower, replacement)

                    logger.info(f"[{agent_cls.__name__}] Resolved system_instruction length: {len(system_instruction)}")
                else:
                    logger.warning(f"[{agent_cls.__name__}] 'llm_prompts' key present but empty list.")
            else:
                pass  # No prompt config

            # 4. Execute using New Signature
            # Input is Pydantic model (InputData), convert to dict
            input_dict = input_data.model_dump() if hasattr(input_data, "model_dump") else input_data

            # Prepare kwargs from Registry Config first (Base Truth)
            # Filter for known LLM parameters to avoid polluting kwargs with metadata
            registry_kwargs = {}
            for k, v in model_config.items():
                if k in ["temperature", "max_tokens", "top_p", "top_k", "frequency_penalty", "presence_penalty"]:
                    registry_kwargs[k] = v

            logger.debug(
                f"[{agent_cls.__name__}] Registry Kwargs: {registry_kwargs} (from config: {model_config.keys()})"
            )

            # Apply Execution Config/Step Config on top (Overrides)
            exec_kwargs = registry_kwargs.copy()
            if execution_config:
                # Resolve Model Strategy Override if present
                if "model" in execution_config:
                    override_model = execution_config["model"]
                    try:
                        resolved_override = await registry.resolve_model_name(override_model)
                        execution_config["model"] = resolved_override
                        logger.debug(f"[{agent_cls.__name__}] Resolved execution_config model '{override_model}' -> '{resolved_override}'")
                    except Exception as e:
                        logger.error(f"[{agent_cls.__name__}] Model override '{override_model}' failed resolution: {e}")
                        from backend.exceptions import AppException, ErrorCodes, status
                        raise AppException(
                            message=f"Model override resolution failed: {e}",
                            status_code=status.HTTP_400_BAD_REQUEST,
                            details={"error_code": ErrorCodes.INVALID_JSON_PAYLOAD, "original_error": str(e)}
                        ) from e

                # Sanity: If execution_config has keys like 'temperature' that are None/Default,
                # we might need to be careful? But strict mode says we cleaned them from steps.
                exec_kwargs.update(execution_config)

            logger.debug(f"[{agent_cls.__name__}] Final Exec Kwargs keys: {list(exec_kwargs.keys())}")
            result_dict = await agent.execute(
                input_data=input_dict,
                execution_context=execution_config,
                system_instruction=system_instruction,
                repository=repo,
                **exec_kwargs,
            )

            # 5. Extract/Validate Result
            # The agent returns a dictionary (or Pydantic dump)
            # We convert it to the expected output_model

            # Hooks would go here...
            # ...
            # Given the strict instruction "Return result directly", I will remove the Hooks logic from here.

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
                input_schema=GenericInput,  # Generic adapter
                output_schema=output_model,
                description=agent_cls.__doc__ or f"Adapter for {agent_cls.__name__}",
                metadata={"agent_class": agent_cls.__name__, "module": agent_cls.__module__, "type": agent_type},
            )
