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
            from fastapi import status

            from backend_v2.exceptions import AppException, ErrorCodes

            logger.error(
                "[TaskRegistry] %s: Agent %s instantiation failed: %s",
                ErrorCodes.INTERNAL_SERVER_ERROR.name,
                agent_cls.__name__,
                str(e),
                exc_info=True,
            )

            raise AppException(
                message="An unexpected system error occurred during AI agent initialization.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
            ) from e

        input_model = getattr(agent_cls, "INPUT_SCHEMA", None)
        if not input_model:
            from backend_v2.exceptions import ConfigurationError

            raise ConfigurationError(
                message=f"Strict Mode: Agent {agent_cls.__name__} has no INPUT_SCHEMA defined.",
                details={"error_code": "CONFIGURATION_ERROR"},
            )

        async def agent_wrapper(input_data: BaseModel, execution_config: dict[str, Any] | None = None) -> BaseModel:
            logger.debug("agent_wrapper CALLED. Config: %s", execution_config)
            # 1. Instantiate
            agent = agent_cls()

            # 2. Configure Model (Inject Dependency)
            try:
                from backend_v2.services.agent_registry import AgentRegistry

                from backend_v2.database.factory import get_driver
                from backend_v2.database.repository import UnifiedWorkflowRepository
                from backend_v2.services.usage_service import UsageService
                from backend_v2.settings import get_settings

                driver = await get_driver(get_settings())
                repo = UnifiedWorkflowRepository(driver)
                registry = AgentRegistry(repo)
                usage_service = UsageService(identity_repo=repo, audit_repo=repo)
                model_config = await registry.resolve_model_config(agent_cls.__name__)

                if hasattr(agent, "set_model"):
                    agent.set_model(
                        model_name=model_config.model_name,
                        provider=model_config.provider,
                        usage_service=usage_service,
                        config=model_config,
                    )
            except Exception as e:
                logger.error(
                    "[TaskRegistry] %s: Agent configuration failed: %s",
                    ErrorCodes.AGENT_NOT_CONFIGURED.name,
                    str(e),
                    exc_info=True,
                )
                from fastapi import status

                from backend_v2.exceptions import AppException, ErrorCodes

                if isinstance(e, AppException):
                    raise e
                raise AppException(
                    message="An unexpected error occurred during AI agent configuration.",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    details={
                        "error_code": ErrorCodes.AGENT_NOT_CONFIGURED.value,
                    },
                ) from e

            # 3. Resolve System Instruction
            system_instruction = None
            if execution_config and "llm_prompts" in execution_config:
                from backend_v2.services.component_registry import ComponentRegistry

                prompts = execution_config["llm_prompts"]
                if prompts:
                    prompt_map = await ComponentRegistry.resolve_prompts_map(repo, tuple(prompts))

                    # MANDATE: Strict Unique Concatenation (Feb 2026 Bug Fix)
                    # Do not use prompt_map.values() as aliases/slugs create duplicated dictionary values
                    # resulting in 2x/4x prompt bloat. Iterate in strict array order.
                    resolved_parts = []
                    for pid in prompts:
                        if pid in prompt_map:
                            resolved_parts.append(prompt_map[pid])

                    system_instruction = "\n\n".join(resolved_parts)

                    if execution_config is None:
                        execution_config = {}
                    execution_config.update(prompt_map)

                    # --- VARIABLE SUBSTITUTION ---
                    # Use model_dump to get dict for substitution logic
                    vars_to_inject = input_data.model_dump()

                    # Dynamic Input Handling for V2 (Courtroom SDUI)
                    if "inputs" in vars_to_inject and "expected_inputs" in execution_config:
                        import json

                        expected_inputs = execution_config["expected_inputs"]
                        dynamic_inputs = vars_to_inject["inputs"]
                        structured_inputs = []

                        # If inputs is a dict mapping expected_input keys to content
                        if isinstance(dynamic_inputs, dict) and isinstance(expected_inputs, list):
                            for expected in expected_inputs:
                                key = expected.get("id")
                                if key and key in dynamic_inputs:
                                    # Fallback descriptions if missing
                                    ai_desc = expected.get("ai_description", {})
                                    translations = ai_desc.get("translations", {})
                                    desc = translations.get("fi", f"Input data for {key}")
                                    structured_inputs.append({"role_description": desc, "content": dynamic_inputs[key]})
                        # Set to vars_to_inject so it replaces {{INPUTS_JSON}}
                        if structured_inputs:
                            vars_to_inject["INPUTS_JSON"] = structured_inputs

                    # System Context
                    from datetime import datetime

                    vars_to_inject["CURRENT_DATE"] = datetime.now().astimezone().strftime("%Y-%m-%d")
                    vars_to_inject["DYNAMIC_TIME"] = datetime.now().astimezone().strftime("%H:%M:%S")
                    vars_to_inject["DYNAMIC_LOCATION"] = "Sijainti: VIRTUAL_ENCLAVE"

                    if system_instruction:
                        logger.info("[DEBUG-INJECTION] System instruction Base Length: %d", len(system_instruction))
                        for key, value in vars_to_inject.items():
                            if value is None:
                                value = ""
                            if hasattr(value, "model_dump_json"):
                                replacement = value.model_dump_json()
                            elif hasattr(value, "model_dump"):
                                import json

                                replacement = json.dumps(value.model_dump(), default=str)
                            elif hasattr(value, "dict"):
                                import json

                                replacement = json.dumps(value.dict(), default=str)
                            else:
                                replacement = str(value)

                            placeholder = f"{{{{{key.upper()}}}}}"
                            placeholder_lower = f"{{{{{key}}}}}"

                            old_len = len(system_instruction)
                            replaced = False

                            if placeholder in system_instruction:
                                system_instruction = system_instruction.replace(placeholder, replacement)
                                replaced = True
                            if placeholder_lower in system_instruction:
                                system_instruction = system_instruction.replace(placeholder_lower, replacement)
                                replaced = True

                            if replaced:
                                logger.info(
                                    "[DEBUG-INJECTION] Replaced %s: %d -> %d chars",
                                    key,
                                    old_len,
                                    len(system_instruction),
                                )

            # 4. Execute using New Signature (Strict Model Pass-Through)
            final_input: Any = input_data

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
                    except Exception as e:
                        # Business Error (400) - No stacktrace needed, fast fail without dataleak
                        from fastapi import status

                        from backend_v2.exceptions import AppException, ErrorCodes

                        raise AppException(
                            message="Invalid AI Model override mapping provided in the request.",
                            status_code=status.HTTP_400_BAD_REQUEST,
                            details={"error_code": ErrorCodes.INVALID_JSON_PAYLOAD.value},
                        ) from e
                exec_kwargs.update(execution_config)

            # CALL EXECUTE
            # logic to handle missing kwargs if strict signature
            # But BaseAgent allows **kwargs.

            # Prevent duplicate repository arg if injected into execution_kwargs
            exec_kwargs.pop("repository", None)

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
                return output_model.model_validate(result_dict)

            # STRICT MODE: If it's not a dict or expected model, fail immediately.
            raise ValueError(f"Agent {agent_cls.__name__} returned an invalid response type: {type(result_dict)}")

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
