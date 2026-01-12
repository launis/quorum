"""API Router for Agent Execution and Discovery.

This module provides endpoints for listing available agents, running specific agents
in isolation, and resolving agent capabilities dynamically.
"""

import importlib
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, HTTPException
from fastapi import Query as APIQuery
from tinydb import Query

from backend.database.wrapper import AbstractDatabase
from backend.dependencies import DatabaseDep, RegistryDep

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
    "/{agent_name}/run", summary="Run Specific Agent", response_description="The result of the agent execution."
)
async def run_agent(
    agent_name: str,
    inputs: Annotated[dict[str, Any], Body(description="Key-value pairs representing the input state for the agent.")],
    db: DatabaseDep,
    system_instruction: Annotated[str | None, Body(description="Optional system instruction override.")] = None,
    model: Annotated[str | None, Body(description="Optional model strategy override.")] = None,
):
    """Executes a specific agent in isolation with provided inputs.

    Args:
        agent_name (str): The class name of the agent to run.
        inputs (Dict[str, Any]): Input data for the agent's context.
        system_instruction (Optional[str]): optional prompt override.
        model (Optional[str]): optional model override.
        db (DatabaseDep): Database dependency.

    Returns:
        dict: A dictionary containing the agent name and the execution result/state.

    Raises:
        HTTPException: If the agent cannot be loaded or execution fails.

    """
    try:
        AgentClass = _load_agent_class(agent_name, db)
        agent = AgentClass(model=model)

        logger.info(f"Executing agent {agent_name} via API...")

        # Manually construct a minimal state or pass kwargs?
        # BaseAgent.execute expects (state, **kwargs).
        # If the agent uses state attributes, we might need to wrap inputs in WorkflowState.
        # But for simple testing, `execute` arguments vary.
        # Let's assume standard **inputs passing for now as per original code.

        result = await agent.execute(system_instruction=system_instruction, **inputs)
        return {"agent": agent_name, "result": result}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get(
    "/",
    response_model=list[dict],
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
        List[Dict]: A list of agent definition objects.
    """
    # Debug wrapper removed, proper DI used.
    import traceback

    try:
        agents_list = []

        # Force discovery if empty
        if not registry.agents_map:
            await registry.discover_and_register_agents()

        # 1. Resolve Global Strategies (for display suffixes)
        try:
            fast_model = await registry.resolve_model_name("fast")
            deep_model = await registry.resolve_model_name("deep")
        except Exception:
            fast_model = "unknown"
            deep_model = "unknown"

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
            # Schema Extraction
            input_schema = None
            if hasattr(agent_instance, "get_input_schema"):
                try:
                    schema_cls = agent_instance.get_input_schema()
                    if schema_cls and hasattr(schema_cls, "model_json_schema"):
                        input_schema = schema_cls.model_json_schema()
                except Exception:
                    pass

            response_schema = None
            if hasattr(agent_instance, "get_response_schema"):
                try:
                    schema_cls = agent_instance.get_response_schema()
                    if schema_cls:
                        if hasattr(schema_cls, "model_json_schema"):
                            response_schema = schema_cls.model_json_schema()
                        elif hasattr(schema_cls, "schema"):
                            response_schema = schema_cls.schema()
                except Exception:
                    pass

            # Determine Model Name (Workflow > Global Default)
            current_model = agent_instance.model

            # Override with Workflow Mapping
            if name in agent_to_step_id:
                step_id = agent_to_step_id[name]
                if step_id in workflow_mapping:
                    strategy_key = workflow_mapping[step_id]

                    # Direct DB Fetch
                    try:
                        table = db.table("system_config")
                        ConfigQuery = Query()
                        res = table.search(ConfigQuery.type == "model_registry")

                        db_strategies = {}
                        if res and "models" in res[0]:
                            db_strategies = res[0]["models"].get("google", {})

                        if strategy_key in db_strategies:
                            val = db_strategies[strategy_key]
                            if isinstance(val, dict):
                                current_model = val.get("model_name", current_model)
                            else:
                                current_model = str(val)
                        else:
                            current_model = f"ERROR: Strategy '{strategy_key}' not found in DB"

                    except Exception as e:
                        current_model = f"ERROR: DB Query Failed: {str(e)}"
                        logger.error(f"DIAGNOSTIC FAULT: {e}")

            # Formatting Suffix
            model_display = current_model
            if model_display == fast_model:
                model_display = f"{model_display} (Fast)"
            elif model_display == deep_model:
                model_display = f"{model_display} (Deep)"

            # DEBUG DIAGNOSTICS for UI
            d_dbg = "[-]"
            if name in agent_to_step_id:
                d_sid = agent_to_step_id[name]
                d_dbg = f"[SID:{d_sid}]"
                if d_sid in workflow_mapping:
                    d_sk = workflow_mapping[d_sid]
                    d_dbg += f"[STR:{d_sk}]"

                    if current_model == agent_instance.model and "deep" in d_sk:
                        d_dbg += "[FAIL:NoUpd]"
                    else:
                        if "deep" in d_sk:
                            d_dbg += "[UPDATED]"
                        else:
                            d_dbg += "[OK]"
                else:
                    d_dbg += "[NoMap]"
            else:
                d_dbg += "[NoStep]"

            desc_base = agent_instance.__doc__.strip() if agent_instance.__doc__ else "No description."

            agents_list.append(
                {
                    "name": name,
                    "class": name,
                    "description": f"{d_dbg} {desc_base}",
                    "model": model_display,
                    "input_schema": input_schema,
                    "output_schema": response_schema,
                }
            )

        return agents_list

    except Exception as e:
        logger.error(f"List Agents Failed: {e}\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500, detail=f"Internal Error in list_agents: {str(e)} | TRACE: {traceback.format_exc()}"
        ) from e
