from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, UploadFile, File, Depends, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging
import json
from tinydb import Query

from backend.dependencies import get_engine, get_agent_registry_dep, get_db_client_dep
from backend.core.engine import WorkflowEngine
from backend.services.agent_registry import AgentRegistry
from backend.database.wrapper import AbstractDatabase

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Orchestration"])

# --- Request Models ---

class WorkflowCreateRequest(BaseModel):
    name: str
    steps: List[Dict[str, Any]]

class WorkflowExecutionRequest(BaseModel):
    workflow_id: str
    inputs: Dict[str, Any] = {}

# --- Workflows & Executions ---

@router.post("/workflows")
def create_workflow(request: WorkflowCreateRequest, engine: WorkflowEngine = Depends(get_engine)):
    """Creates a new workflow definition."""
    workflow_id = engine.create_workflow(request.name, request.steps)
    return {"status": "created", "workflow_id": workflow_id}

@router.post("/executions")
async def execute_workflow(request: Request, background_tasks: BackgroundTasks, engine: WorkflowEngine = Depends(get_engine)):
    """Starts a workflow execution asynchronously (Multipart)."""
    form = await request.form()
    
    workflow_id = form.get("workflow_id")
    if not workflow_id:
        raise HTTPException(status_code=422, detail="Missing workflow_id")
        
    inputs = json.loads(form.get("inputs") or "{}")
    
    files_map = {}
    for key, value in form.items():
        if hasattr(value, "filename") and value.filename:
            content = await value.read()
            files_map[key] = (value.filename, content)

    execution_id = await engine.create_execution(workflow_id, inputs, files=files_map)
    
    # Fetch actual text inputs from DB for the runner
    rec = engine.repository.get_execution(execution_id)
    cleaned_inputs = rec['inputs']
    
    background_tasks.add_task(engine.run_execution, execution_id, cleaned_inputs)
    
    return {"status": "started", "execution_id": execution_id}

@router.get("/executions/recent")
async def get_recent_executions(limit: int = 5, status: Optional[str] = None, engine: WorkflowEngine = Depends(get_engine)):
    """Returns the most recent executions."""
    all_execs = engine.repository.get_all_executions()
    if not all_execs: return []
    
    if status:
        all_execs = [ex for ex in all_execs if ex.get('status', '').lower() == status.lower()]

    sorted_execs = sorted(all_execs, key=lambda x: x.get('start_time', ''), reverse=True)
    return sorted_execs[:limit]

@router.get("/executions/latest")
async def get_latest_execution(engine: WorkflowEngine = Depends(get_engine)):
    """Returns the most recent execution."""
    all_execs = engine.repository.get_all_executions()
    if not all_execs: raise HTTPException(status_code=404, detail="No executions found")
    
    return sorted(all_execs, key=lambda x: x.get('start_time', ''), reverse=True)[0]

@router.get("/executions/{execution_id}")
async def get_execution_status(execution_id: str, engine: WorkflowEngine = Depends(get_engine)):
    """Gets the status of a workflow execution."""
    status = engine.get_execution_status(execution_id)
    if not status: raise HTTPException(status_code=404, detail="Execution not found")
    return status

@router.post("/executions/{execution_id}/retry")
async def retry_execution(execution_id: str, background_tasks: BackgroundTasks, engine: WorkflowEngine = Depends(get_engine)):
    """Retries a failed or interrupted execution."""
    status = engine.get_execution_status(execution_id)
    if not status: raise HTTPException(status_code=404, detail="Execution not found")
    
    current_status = status.get('status')
    if current_status not in ['failed', 'rejected', 'interrupted']:
         raise HTTPException(status_code=400, detail=f"Cannot retry execution in status '{current_status}'.")

    background_tasks.add_task(engine.resume_execution, execution_id)
    return {"status": "resuming", "execution_id": execution_id}

# --- Agents Definitions ---

@router.get("/agents")
def list_agents(workflow_id: Optional[str] = None, registry: AgentRegistry = Depends(get_agent_registry_dep), db: AbstractDatabase = Depends(get_db_client_dep)):
    """Lists all available agents and their metadata, with Model Mapping."""
    try:
        if not registry.agents_map:
            registry.discover_and_register_agents()
    except Exception as e:
        logger.error(f"AGENT DISCOVERY ERROR: {e}")

    # 1. Get Workflow Mapping if ID provided
    workflow_mapping = {}
    try:
        if workflow_id:
            # DB lookup via repository
            wf = registry.repository.get_workflow_by_id(workflow_id)
            if wf:
                workflow_mapping = wf.get('default_model_mapping', {})
    except Exception as e:
        logger.error(f"WORKFLOW FETCH ERROR: {e}")

    # 2. Get Steps for Mapping
    agent_to_step_id = {}
    try:
        steps = registry.repository.get_all_steps()
        if steps:
            for s in steps:
                # 'component' is the field used in seed_data.json/db.json for the Agent Class Name
                agent_identifier = s.get('agent_id') or s.get('component')
                if agent_identifier and 'id' in s:
                    agent_to_step_id[agent_identifier] = s['id']
    except Exception as e:
        logger.error(f"STEP FETCH ERROR: {e}")
        
    agents_list = []
    for name, agent_instance in registry.agents_map.items():
        input_schema = None
        response_schema = None
        if hasattr(agent_instance, 'get_input_schema'):
             try:
                 schema_cls = agent_instance.get_input_schema()
                 if schema_cls: input_schema = schema_cls.model_json_schema()
             except Exception: pass

        output_schema = None
        if hasattr(agent_instance, 'get_response_schema'):
             try:
                 schema_cls = agent_instance.get_response_schema()
                 if schema_cls: output_schema = schema_cls.model_json_schema()
             except Exception: pass
        
        # Determine Model Name (Workflow > Global Default)
        current_model = agent_instance.model 
        
        # Override with Workflow Mapping (Strict DB Lookup)
        if name in agent_to_step_id:
            step_id = agent_to_step_id[name]
            if step_id in workflow_mapping:
                strategy_key = workflow_mapping[step_id]
                
                # Direct DB Fetch using get_db_client as requested
                try:
                    table = db.table('system_config')
                    Config = Query()
                    res = table.search(Config.type == 'model_registry')
                    
                    db_strategies = {}
                    if res and 'models' in res[0]:
                        db_strategies = res[0]['models'].get('google', {})
                    
                    if strategy_key in db_strategies:
                        val = db_strategies[strategy_key]
                        if isinstance(val, dict):
                             current_model = val.get('model_name', current_model)
                        else:
                             current_model = str(val)
                    else:
                        current_model = f"ERROR: Strategy '{strategy_key}' not found in DB"
                        
                except Exception as e:
                    current_model = f"ERROR: DB Query Failed: {str(e)}"
                    logger.error(f"DIAGNOSTIC FAULT: {e}")

        # Formatting Suffix
        fast_model = "gemini-3-flash-preview" 
        deep_model = "gemini-3-pro-preview"
        # Ideally fetch defaults from settings, but keeping simple for now logic
        
        model_display = current_model
        if "flash" in str(model_display).lower():
             model_display = f"{model_display} (Fast)"
        elif "pro" in str(model_display).lower():
             model_display = f"{model_display} (Deep)"

        agents_list.append({
            "name": name,
            "description": agent_instance.__doc__.strip() if agent_instance.__doc__ else "No description.",
            "model": model_display,
            "input_schema": input_schema,
            "output_schema": output_schema,
        })
        
    return agents_list

@router.post("/agents/{agent_name}/run")
async def run_agent_direct(
    agent_name: str, 
    inputs: Dict[str, Any] = Body(...),
    system_instruction: Optional[str] = Body(None),
    model: Optional[str] = Body(None),
    registry: AgentRegistry = Depends(get_agent_registry_dep)
):
    """Executes a specific agent directly (Bypassing Workflow Engine)."""
    try:
        agent = registry.get_agent(agent_name)
        if not agent:
             raise ValueError(f"Unknown agent: {agent_name}")
        
        # Determine model override if needed
        # For direct run, we might want to clone the agent to avoiding thread safety issues?
        # Agents are stateless per request if designed correctly (except self.model), 
        # but self.model mutation is dangerous in singleton.
        # Ideally we should pass model to execute(), not set on self.
        
        # Warning: This updates the singleton agent's model! 
        # Only safe if Agents are transient or we accept global change.
        # Better: Pass model to execute.
        
        # NOTE: execute() signature in BaseAgent doesn't accept model override yet, 
        # but our runners do injected kwargs.
        
        logger.info(f"Executing agent {agent_name} direct...")
        # We need to construct a minimal State?
        # BaseAgent.execute signature matches: (self, state: WorkflowState, ...)
        # So we cannot just pass dict. 
        # The previous agents_router.py implementation was calling agent.execute(**inputs), 
        # which implies the agent wasn't inheriting BaseAgent OR BaseAgent had different signature?
        # Let's check BaseAgent...
        
        # Checked BaseAgent: execute(self, state: WorkflowState, ...)
        # So previous agents_router code: `result = await agent.execute(system_instruction=system_instruction, **inputs)`
        # MUST have been broken for BaseAgents unless they overrode execute to take kwargs.
        # But BaseAgent definition is `async def execute(self, state: WorkflowState, ...)`.
        
        # Thus, the old agents_router endpoint was likely broken or for testing only.
        # We will disable this endpoint for now or wrap it properly.
        
        raise HTTPException(status_code=501, detail="Direct agent execution via API is temporarily disabled pending State refactor.")
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
