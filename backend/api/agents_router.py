from fastapi import APIRouter, HTTPException, Body, Depends, Query as APIQuery
from typing import Dict, Any, Optional, List
import importlib

from backend.database.wrapper import AbstractDatabase
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

@router.get("/", response_model=List[Dict])
def list_agents(
    workflow_id: Optional[str] = APIQuery(None), 
    db: AbstractDatabase = Depends(get_db_client_dep)
):
    """
    List all available agents with their metadata, models, and schemas.
    Dynamically resolves model strategy based on the selected workflow configuration.
    """
    registry = AgentRegistry.get_instance()
    agents_list = []
    
    # Force discovery if empty
    if not registry.agents_map:
        registry.discover_and_register_agents()
        
    # 1. Resolve Global Strategies (for display suffixes)
    try:
        fast_model = registry.resolve_model_name("fast")
        deep_model = registry.resolve_model_name("deep")
    except Exception:
        fast_model = "unknown"
        deep_model = "unknown"

    # 2. Fetch Workflow Context to override defaults
    # Use the repository directly to find how agents are configured in the active workflow
    workflow_mapping = {}
    agent_to_step_id = {}
    
    try:
        # Get active workflow mapping
        wfs = registry.repository.get_all_workflows()
        if wfs:
        if wfs:
            target_wf = None
            if workflow_id:
                target_wf = next((w for w in wfs if w.get('id') == workflow_id), None)
            
            if not target_wf:
                # Fallback to first if explicit ID not found or not provided
                target_wf = wfs[0]

            if target_wf:
                workflow_mapping = target_wf.get('default_model_mapping', {})
            
        # Map Agent Class Name -> Step ID
        steps = registry.repository.get_all_steps()
        for s in steps:
            comp = s.get('component') # e.g. "GuardAgent"
            sid = s.get('id')         # e.g. "step_guard"
            if comp and sid:
                agent_to_step_id[comp] = sid
                
    except Exception as e:
        logger.warning(f"Failed to resolve workflow mapping for agent list: {e}")

    # 3. Build List
    for name, agent_instance in registry.agents_map.items():
        # Schema Extraction
        input_schema = None
        if hasattr(agent_instance, 'get_input_schema'):
             try:
                 schema_cls = agent_instance.get_input_schema()
                 if schema_cls and hasattr(schema_cls, 'model_json_schema'):
                     input_schema = schema_cls.model_json_schema()
             except Exception: pass

        response_schema = None
        if hasattr(agent_instance, 'get_response_schema'):
             try:
                 schema_cls = agent_instance.get_response_schema()
                 if schema_cls:
                     if hasattr(schema_cls, 'model_json_schema'):
                         response_schema = schema_cls.model_json_schema()
                     elif hasattr(schema_cls, 'schema'):
                         response_schema = schema_cls.schema()
             except Exception: pass

        # Determine Model Name (Workflow > Global Default)
        # Start with the agent's internal default (initially set to Global Fast)
        current_model = agent_instance.model 
        
        # Override with Workflow Mapping
        # Override with Workflow Mapping (Strict DB Lookup)
        if name in agent_to_step_id:
            step_id = agent_to_step_id[name]
            if step_id in workflow_mapping:
                strategy_key = workflow_mapping[step_id]
                
                # Direct DB Fetch using get_db_client as requested
                try:
                    # Logic: Use injected DB client -> Query system_config -> Build local strategies -> Lookup
                    table = db.table('system_config')
                    Config = Query()
                    res = table.search(Config.type == 'model_registry')
                    
                    db_strategies = {}
                    if res and 'models' in res[0]:
                        # Prioritize google
                        db_strategies = res[0]['models'].get('google', {})
                    
                    logger.warning(f"DIAGNOSTIC: Agent={name}, Step={step_id}, StratKey={strategy_key}, StrategiesFound={list(db_strategies.keys())}")

                    if strategy_key in db_strategies:
                        val = db_strategies[strategy_key]
                        if isinstance(val, dict):
                             current_model = val.get('model_name', current_model)
                        else:
                             current_model = str(val)
                    else:
                        # User requirement: If NOT found -> error
                        current_model = f"ERROR: Strategy '{strategy_key}' not found in DB"
                        
                except Exception as e:
                    current_model = f"ERROR: DB Query Failed: {str(e)}"
                    logger.error(f"DIAGNOSTIC FAULT: {e}")

        # Formatting Suffix
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
                
                # Check if update happened
                if current_model == agent_instance.model and "deep" in d_sk:
                     d_dbg += "[FAIL:NoUpd]"
                else:
                     if "deep" in d_sk: d_dbg += "[UPDATED]"
                     else: d_dbg += "[OK]"
            else:
                d_dbg += "[NoMap]"
        else:
            d_dbg += "[NoStep]"

        desc_base = agent_instance.__doc__.strip() if agent_instance.__doc__ else "No description."

        agents_list.append({
            "name": name,
            "class": name,
            "description": f"{d_dbg} {desc_base}",
            "model": model_display,
            "input_schema": input_schema,
            "output_schema": response_schema
        })
        
    return agents_list
