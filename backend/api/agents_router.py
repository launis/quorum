from fastapi import APIRouter, HTTPException, Body, Depends
from typing import Dict, Any, Optional
import importlib

from backend.database.wrapper import AbstractDatabase, get_db_client
from backend.dependencies import get_db_client_dep, get_agent_registry_dep
from backend.services.agent_registry import AgentRegistry
from tinydb import Query
# from backend.config import DB_PATH # Removed unused import
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["Agents"])

def _load_agent_class(agent_name: str, db: AbstractDatabase):
    """
    Dynamically loads an agent class by name using the database registry.
    """
    # db = get_db_client() # Removed
    components_table = db.table('components')
    
    # 1. Try to find by class name (preferred)
    comp_record = components_table.get(Query()['class'] == agent_name)
    
    # 2. If not found by class, try by name (fallback)
    if not comp_record:
         comp_record = components_table.get(Query()['name'] == agent_name)

    if not comp_record:
         raise ValueError(f"Unknown agent: {agent_name} (not found in registry)")
    else:
        module_name = comp_record.get('module')
        
    try:
        module = importlib.import_module(module_name)
        return getattr(module, agent_name)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Failed to load agent {agent_name} from {module_name}: {e}")

@router.post("/{agent_name}/run")
async def run_agent(
    agent_name: str, 
    inputs: Dict[str, Any] = Body(...),
    system_instruction: Optional[str] = Body(None),
    model: Optional[str] = Body(None),
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """
    Executes a specific agent with provided inputs.
    """
    try:
        AgentClass = _load_agent_class(agent_name, db)
        agent = AgentClass(model=model)
        
        logger.info(f"Executing agent {agent_name} via API...")
        # Fixed: Added await since execute is async
        result = await agent.execute(system_instruction=system_instruction, **inputs)
        return {"agent": agent_name, "result": result}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
def list_agents(registry: AgentRegistry = Depends(get_agent_registry_dep)):
    """
    Lists all available agents and their metadata.
    """
    agents_list = []
    
    # Force discovery if empty (though dep should handle it)
    if not registry.agents_map:
        registry.discover_and_register_agents()
        
    for name, agent_instance in registry.agents_map.items():
        # Clean up name (remove module path if present, though registry keys are usually class names)
        # Inspect input schema if possible
        input_schema = None
        if hasattr(agent_instance, 'get_input_schema'):
             try:
                 # It's a method on BaseAgent
                 # However, get_input_schema might return a Pydantic model class
                 schema_cls = agent_instance.get_input_schema()
                 if schema_cls:
                     input_schema = schema_cls.model_json_schema()
             except Exception:
                 pass

        agents_list.append({
            "name": name,
            "class": name,
            "description": agent_instance.__doc__.strip() if agent_instance.__doc__ else "No description.",
            "model": agent_instance.model,
            "input_schema": input_schema
        })
        
    return agents_list
