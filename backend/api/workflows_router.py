from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, UploadFile, File, Depends
from backend.dependencies import get_engine
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# from tinydb import Query # Removed
import logging
import json
from backend.core.engine import WorkflowEngine
# from backend.config import DB_PATH, DATA_DIR # Removed

router = APIRouter(tags=["Workflows"])
logger = logging.getLogger(__name__)

# Initialize Engine (Module Scoped) REMOVED
# Used Dependency Injection instead.


# --- Request Models ---

class WorkflowCreateRequest(BaseModel):
    name: str
    steps: List[Dict[str, Any]]

class WorkflowExecutionRequest(BaseModel):
    workflow_id: str
    inputs: Dict[str, Any] = {}

# --- Endpoints ---

@router.post("/workflows")

def create_workflow(request: WorkflowCreateRequest, engine: WorkflowEngine = Depends(get_engine)):
    """
    Creates a new workflow definition.
    """
    workflow_id = engine.create_workflow(request.name, request.steps)
    return {"status": "created", "workflow_id": workflow_id}

@router.post("/executions")

async def execute_workflow(request: Request, background_tasks: BackgroundTasks, engine: WorkflowEngine = Depends(get_engine)):
    """
    Starts a workflow execution asynchronously (Multipart).
    """
    # Note: We let exceptions bubble up to the global handler
    form = await request.form()
    
    workflow_id = form.get("workflow_id")
    if not workflow_id:
        raise HTTPException(status_code=422, detail="Missing workflow_id")
        
    inputs = {}
    inputs_str = form.get("inputs")
    if inputs_str:
        inputs = json.loads(inputs_str)
        
    files_map = {}
    for key, value in form.items():
        if hasattr(value, "filename") and value.filename:
            content = await value.read()
            files_map[key] = (value.filename, content)

    execution_id = await engine.create_execution(workflow_id, inputs, files=files_map)
    
    # Fetch actual text inputs from DB for the runner
    rec = engine.repository.get_execution(execution_id)
    # If create_execution didn't fail, rec should exist. 
    # If not, access might raise TypeError, which will be 500.
    cleaned_inputs = rec['inputs']
    
    background_tasks.add_task(engine.run_execution, execution_id, cleaned_inputs)
    
    return {"status": "started", "execution_id": execution_id}

@router.get("/executions/recent")

async def get_recent_executions(limit: int = 5, status: Optional[str] = None, engine: WorkflowEngine = Depends(get_engine)):
    """
    Returns the most recent executions (by start_time).
    Supports filtering by status (e.g. 'completed', 'failed').
    """
    all_execs = engine.repository.get_all_executions()
    if not all_execs:
            return []
    
    # Filter by status if provided
    if status:
        all_execs = [ex for ex in all_execs if ex.get('status', '').lower() == status.lower()]

    # Sort by start_time descending
    # Assuming start_time is ISO string
    sorted_execs = sorted(all_execs, key=lambda x: x.get('start_time', ''), reverse=True)
    return sorted_execs[:limit]

@router.get("/executions/latest")

async def get_latest_execution(engine: WorkflowEngine = Depends(get_engine)):
    """
    Returns the most recent execution (by start_time).
    Useful for 'Resume' functionality.
    """
    all_execs = engine.repository.get_all_executions()
    if not all_execs:
            raise HTTPException(status_code=404, detail="No executions found")
    
    # Sort by start_time descending
    latest = sorted(all_execs, key=lambda x: x.get('start_time', ''), reverse=True)[0]
    return latest

@router.get("/executions/{execution_id}")

async def get_execution_status(execution_id: str, engine: WorkflowEngine = Depends(get_engine)):
    """
    Gets the status of a workflow execution.
    """
    status = engine.get_execution_status(execution_id)
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")
    return status

@router.get("/orchestrator/status/{execution_id}")

def get_orchestrator_status(execution_id: str, engine: WorkflowEngine = Depends(get_engine)):
    """
    Gets the status of a workflow execution (Legacy Alias).
    """
    status = engine.get_execution_status(execution_id)
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")
    return status

@router.post("/executions/{execution_id}/retry")
async def retry_execution(execution_id: str, background_tasks: BackgroundTasks, engine: WorkflowEngine = Depends(get_engine)):
    """
    Retries a failed or interrupted execution.
    Resumes from the last successfully completed step.
    """
    # Verify execution exists and is in a failed state
    status = engine.get_execution_status(execution_id)
    if not status:
         raise HTTPException(status_code=404, detail="Execution not found")
    
    current_status = status.get('status')
    if current_status not in ['failed', 'rejected', 'interrupted']:
         raise HTTPException(status_code=400, detail=f"Cannot retry execution in status '{current_status}'. Only failed/rejected/interrupted executions can be retried.")

    background_tasks.add_task(engine.resume_execution, execution_id)
    return {"status": "resuming", "execution_id": execution_id}

