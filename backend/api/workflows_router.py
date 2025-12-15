from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, UploadFile, File
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from tinydb import Query
import json
import os
import logging
from backend.core.engine import WorkflowEngine
from backend.config import DB_PATH, DATA_DIR

router = APIRouter(tags=["Workflows"])
logger = logging.getLogger(__name__)

# Initialize Engine (Module Scoped)
# This shares the same DB file, so it's safe to have multiple instances accessing TinyDB.
engine = WorkflowEngine(DB_PATH)

# --- Request Models ---

class WorkflowCreateRequest(BaseModel):
    name: str
    steps: List[Dict[str, Any]]

class WorkflowExecutionRequest(BaseModel):
    workflow_id: str
    inputs: Dict[str, Any] = {}

# --- Endpoints ---

@router.post("/workflows")
def create_workflow(request: WorkflowCreateRequest):
    """
    Creates a new workflow definition.
    """
    workflow_id = engine.create_workflow(request.name, request.steps)
    return {"status": "created", "workflow_id": workflow_id}

@router.post("/executions")
async def execute_workflow(request: Request, background_tasks: BackgroundTasks):
    """
    Starts a workflow execution asynchronously (Multipart).
    """
    try:
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

        execution_id = engine.create_execution(workflow_id, inputs, files=files_map)
        
        # Fetch actual text inputs from DB for the runner
        Execution = Query()
        rec = engine.executions_table.search(Execution.execution_id == execution_id)[0]
        cleaned_inputs = rec['inputs']
        
        background_tasks.add_task(engine.run_execution, execution_id, cleaned_inputs)
        
        return {"status": "started", "execution_id": execution_id}
    except Exception as e:
        logger.error(f"Execution Start Failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions/recent")
async def get_recent_executions(limit: int = 5, status: Optional[str] = None):
    """
    Returns the most recent executions (by start_time).
    Supports filtering by status (e.g. 'completed', 'failed').
    """
    try:
        all_execs = engine.executions_table.all()
        if not all_execs:
             return []
        
        # Filter by status if provided
        if status:
            all_execs = [ex for ex in all_execs if ex.get('status', '').lower() == status.lower()]

        # Sort by start_time descending
        # Assuming start_time is ISO string
        sorted_execs = sorted(all_execs, key=lambda x: x.get('start_time', ''), reverse=True)
        return sorted_execs[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions/latest")
async def get_latest_execution():
    """
    Returns the most recent execution (by start_time).
    Useful for 'Resume' functionality.
    """
    try:
        all_execs = engine.executions_table.all()
        if not all_execs:
             raise HTTPException(status_code=404, detail="No executions found")
        
        # Sort by start_time descending
        latest = sorted(all_execs, key=lambda x: x.get('start_time', ''), reverse=True)[0]
        return latest
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/executions/{execution_id}")
async def get_execution_status(execution_id: str):
    """
    Gets the status of a workflow execution.
    """
    status = engine.get_execution_status(execution_id)
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")
    return status

@router.get("/orchestrator/status/{execution_id}")
def get_orchestrator_status(execution_id: str):
    """
    Gets the status of a workflow execution (Legacy Alias).
    """
    status = engine.get_execution_status(execution_id)
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")
    return status
