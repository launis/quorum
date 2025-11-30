from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
import importlib

router = APIRouter(prefix="/agents", tags=["Agents"])

def _load_agent_class(agent_name: str):
    """
    Dynamically loads an agent class by name.
    """
    # Mapping of common agent names to modules
    # This could be improved by using the database registry, but hardcoding for simplicity/robustness here
    mapping = {
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
    
    module_name = mapping.get(agent_name)
    if not module_name:
        raise ValueError(f"Unknown agent: {agent_name}")
        
    try:
        module = importlib.import_module(module_name)
        return getattr(module, agent_name)
    except (ImportError, AttributeError) as e:
        raise ValueError(f"Failed to load agent {agent_name}: {e}")

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
