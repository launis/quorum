"""API Router for Agent Execution and Discovery.

This module provides endpoints for listing available agents, running specific agents
in isolation, and resolving agent capabilities dynamically.
"""

import importlib
import logging
from typing import Annotated, Any

from fastapi import (
    APIRouter,
    Body,
    status,
)
from fastapi import (
    Query as APIQuery,
)
from tinydb import Query

from backend.database.wrapper import AbstractDatabase
from backend.dependencies import DatabaseDep, RegistryDep
from backend.services.localization import localize_schema

from backend.schemas.agent import AgentDefinition, AgentRunResponse

# --- Local Imports ---
# Rule 6: APIError must be the FIRST local import
from backend.exceptions import AppException, ResourceNotFoundError


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["Agents"])


def _load_agent_class(agent_name: str, db: AbstractDatabase):
    """Dynamically loads an agent class by name using the database registry.

    Args:
        agent_name (str): The name of the agent class or component.
        db (AbstractDatabase): The database connection.

    Returns:
        Type: The loaded Agent class.

    Raises:
        ValueError: If the agent is not found or cannot be imported.

    """
    components_table = db.table("components")

    # 1. Try to find by class name (preferred)
    comp_record = components_table.get(Query()["class"] == agent_name)

    # 2. If not found by class, try by name (fallback)
    if not comp_record:
        comp_record = components_table.get(Query()["name"] == agent_name)

    if not comp_record:
        raise ValueError(f"Unknown agent: {agent_name} (not found in registry)")
    else:
        module_name = str(comp_record.get("module"))

    try:
        module = importlib.import_module(module_name)
        return getattr(module, agent_name)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Failed to load agent {agent_name} from {module_name}: {e}") from e


@router.post(
    "/{agent_name}/run",
    summary="Run Specific Agent",
    response_model=AgentRunResponse,
    response_description="The result of the agent execution."
)
async def run_agent(
    agent_name: str,
    inputs: Annotated[dict[str, Any], Body(description="Key-value pairs representing the input state for the agent.")],
    db: DatabaseDep,
    registry: RegistryDep,
    system_instruction: Annotated[str | None, Body(description="Optional system instruction override.")] = None,
    model: Annotated[str | None, Body(description="Optional model strategy override.")] = None,
):
    """Executes a specific agent in isolation with provided inputs.

    Args:
        agent_name (str): The class name of the agent to run.
        inputs (Dict[str, Any]): Input data for the agent's context.
        system_instruction (Optional[str]): optional prompt override.
        model (Optional[str]): optional model override (strategy key or model name).
        db (DatabaseDep): Database dependency.
        registry (RegistryDep): Registry dependency for strategy resolution.

    Returns:
        AgentRunResponse: A DTO containing the execution result.

    Raises:
        ResourceNotFoundError: If the agent class cannot be loaded.
        AppException: If execution fails (400 for validation, 500 for runtime).

    """
    # 1. Resolve Strategy (Strict Mode: Database Only)
    # Mandate: "Ensure that default doesn't come from anywhere [code]... give error if not from database"
    if not model:
        error_code = "AGENT_MISSING_MODEL"
        raise AppException(
            message="Model strategy is required. No default strategy is applied.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code},
        )
    
    target_strategy = model

    try:
        resolved_model = await registry.resolve_model_name(target_strategy)
    except ValueError as e:
        # Strategy not found in DB -> Fail Fast (400)
        error_code = "INVALID_MODEL_STRATEGY"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=f"Model strategy '{target_strategy}' not configured in database.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code, "strategy": target_strategy},
        ) from e
    except Exception as e:
         # Configuration Error -> 500
         error_code = "MODEL_RESOLUTION_FAILED"
         logger.error(f"{error_code}: {e}", exc_info=True)
         raise AppException(
             message="Failed to resolve model strategy.",
             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
             details={"error_code": error_code},
         ) from e

    # 2. Load Agent Class (Strict)
    try:
        AgentClass = _load_agent_class(agent_name, db)
    except ValueError as e:
        # Load Error -> 404
        error_code = "AGENT_NOT_FOUND"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise ResourceNotFoundError(
            "Agent", agent_name, details={"error_code": error_code, "original_error": str(e)}
        ) from e

    # 3. Instantiate and Execute (Isolated Try-Catch)
    try:
        agent = AgentClass(model=resolved_model)
        logger.info(f"Executing agent {agent_name} via API... Model: {resolved_model}")

        result = await agent.execute(system_instruction=system_instruction, **inputs)
        return AgentRunResponse(agent=agent_name, result=result)

    except ValueError as e:
        # Execution Validation Error -> 400 Bad Request
        # Mandate: Fail Fast on invalid inputs
        error_code = "AGENT_INPUT_INVALID"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": error_code},
        ) from e

    except Exception as e:
        # Unexpected Runtime Error -> 500 Internal Server Error
        error_code = "AGENT_EXECUTION_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code},
        ) from e


@router.get(
    "/",
    response_model=list[AgentDefinition],
    summary="List All Agents",
    response_description="A list of available agents containing metadata and schemas.",
)
async def list_agents(
    db: DatabaseDep,
    registry: RegistryDep,
    workflow_id: str | None = APIQuery(
        None, description="Optional Workflow ID to resolve model strategies contextually."
    ),
):
    """List all available agents with their metadata, models, and schemas.

    Dynamically resolves model strategy based on the selected workflow configuration.

    Args:
        workflow_id (Optional[str]): Context for model resolution.
        db (DatabaseDep): Database dependency.
        registry (RegistryDep): Injected registry service.

    Returns:
        List[AgentDefinition]: A list of agent definition objects.
    """
    try:
        agents_list: list[AgentDefinition] = []

        # Force discovery if empty
        if not registry.agents_map:
            await registry.discover_and_register_agents()

        # 1. Resolve Global Strategies (for display suffixes)
        # Fetch all strategies to support dynamic suffixes (Fast, Deep, Pro, Strict, etc.)
        all_strategies = await registry.get_all_strategies()
        # Filter for display: use only lowercase keys (strategies) to avoid Component Names (CamelCase)
        display_strategies = {k: v for k, v in all_strategies.items() if k.islower()}

        # 2. Fetch Workflow Context to override defaults
        workflow_mapping = {}
        agent_to_step_id = {}

        try:
            wfs = await registry.repository.get_all_workflows()
            if wfs:
                target_wf = None
                if workflow_id:
                    target_wf = next((w for w in wfs if w.get("id") == workflow_id), None)

                if not target_wf:
                    # Fallback to first if explicit ID not found or not provided
                    target_wf = wfs[0]

                if target_wf:
                    workflow_mapping = target_wf.get("default_model_mapping", {})

            # Map Agent Class Name -> Step ID
            steps = await registry.repository.get_all_steps()
            for s in steps:
                comp = s.get("component")  # e.g. "GuardAgent"
                sid = s.get("id")  # e.g. "step_guard"
                if comp and sid:
                    agent_to_step_id[comp] = sid

        except Exception as e:
            logger.warning(f"Failed to resolve workflow mapping for agent list: {e}")

        # 3. Build List
        for name, agent_instance in registry.agents_map.items():
            # Schema Extraction (Simplified with helpers)
            input_schema = _extract_schema(agent_instance, "get_input_schema")
            output_schema = _extract_schema(agent_instance, "get_response_schema")

            # Determine Model Name (Workflow > Global Default)
            current_model = agent_instance.model

            # Override with Workflow Mapping
            if name in agent_to_step_id:
                step_id = agent_to_step_id[name]
                if step_id in workflow_mapping:
                    strategy_key = workflow_mapping[step_id]

                    # Use Registry for Resolution (SSOT)
                    try:
                        current_model = await registry.resolve_model_name(strategy_key)
                    except Exception as e:
                        current_model = f"ERROR: Strategy '{strategy_key}' Failed: {str(e)}"
                        logger.error(f"DIAGNOSTIC FAULT: {e}")

            # Formatting Suffix - Dynamic
            model_display = current_model

            # Find matching strategy key
            for s_key in sorted(display_strategies.keys()):
                s_resolved = display_strategies[s_key]
                if model_display == s_resolved:
                    model_display = f"{model_display} ({s_key.capitalize()})"
                    break

            # Simplified Description
            desc_base = agent_instance.__doc__.strip() if agent_instance.__doc__ else "No description."

            agents_list.append(
                AgentDefinition(
                    name=name,
                    class_name=name,
                    description=desc_base,
                    model=model_display,
                    input_schema=localize_schema(input_schema) if input_schema else None,
                    output_schema=localize_schema(output_schema) if output_schema else None,
                )
            )

        return agents_list

    except Exception as e:
        error_code = "AGENT_DISCOVERY_FAILED"
        logger.error(f"{error_code}: {e}", exc_info=True)
        raise AppException(
            message=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": error_code},
        ) from e


def _extract_schema(instance: Any, method_name: str) -> dict[str, Any] | None:
    """Helper to extract Pydantic schema safely."""
    if hasattr(instance, method_name):
        try:
            schema_cls = getattr(instance, method_name)()
            if schema_cls:
                if hasattr(schema_cls, "model_json_schema"):
                    return schema_cls.model_json_schema()
                elif hasattr(schema_cls, "schema"):
                    return schema_cls.schema()
        except Exception as e:
            logger.debug(f"Failed to extract schema {method_name} for instance: {e}")
    return None
