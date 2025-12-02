from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
import importlib

router = APIRouter(prefix="/agents", tags=["Agents"])

from tinydb import TinyDB, Query
from backend.config import DB_PATH

def _load_agent_class(agent_name: str):
    """
    Dynamically loads an agent class by name using the database registry.
    """
    db = TinyDB(DB_PATH, encoding='utf-8')
    components_table = db.table('components')
    
    # 1. Try to find by class name (preferred)
    comp_record = components_table.get(Query()['class'] == agent_name)
    
    # 2. If not found by class, try by name (fallback)
    if not comp_record:
         comp_record = components_table.get(Query()['name'] == agent_name)

    if not comp_record:
        # Fallback for legacy hardcoded names if DB is not fully populated or for testing
        # This ensures we don't break immediately if DB is missing something
        legacy_mapping = {
            "GuardAgent": "backend.agents.guard",
            "AnalystAgent": "backend.agents.analyst",
            "LogicianAgent": "backend.agents.logician",
            "LogicalFalsifierAgent": "backend.agents.critics",
            "FactualOverseerAgent": "backend.agents.critics",
            "CausalAnalystAgent": "backend.agents.critics",
            "PerformativityDetectorAgent": "backend.agents.critics",
            "JudgeAgent": "backend.agents.judge",
            "XAIReporterAgent": "backend.agents.judge"
        }
        module_name = legacy_mapping.get(agent_name)
        if not module_name:
             raise ValueError(f"Unknown agent: {agent_name} (not found in DB or legacy map)")
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
        
        print(f"Executing agent {agent_name} via API...")
        result = agent.execute(system_instruction=system_instruction, **inputs)
        return {"agent": agent_name, "result": result}
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
