from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
import importlib

from backend.database.wrapper import get_db_client
from tinydb import Query
from backend.config import DB_PATH
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["Agents"])

def _load_agent_class(agent_name: str):
    """
    Dynamically loads an agent class by name using the database registry.
    """
    db = get_db_client()
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
    model: Optional[str] = Body("gemini-2.5-flash")
):
    """
    Executes a specific agent with provided inputs.
    """
    try:
        AgentClass = _load_agent_class(agent_name)
        agent = AgentClass(model=model)
        
        logger.info(f"Executing agent {agent_name} via API...")
        # Fixed: Added await since execute is async
        result = await agent.execute(system_instruction=system_instruction, **inputs)
        return {"agent": agent_name, "result": result}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
