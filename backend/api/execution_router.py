from fastapi import APIRouter, HTTPException, BackgroundTasks, Request, UploadFile, File, Depends, Body, Path, Query as APIQuery
from typing import List, Dict, Any, Optional, Annotated
from pydantic import BaseModel, Field
import logging
import json

from backend.dependencies import get_engine, EngineDep
from backend.core.engine import WorkflowEngine
from backend.models.state import WorkflowState  # Required for migration/hydration logic

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Orchestration"])

# --- Request Models ---

class WorkflowCreateRequest(BaseModel):
    name: Annotated[str, Field(
        description="The unique, human-readable name for the new workflow."
    )]
    steps: Annotated[List[Dict[str, Any]], Field(
        description="A sequential list of step configurations defining the workflow logic."
    )]

class WorkflowExecutionRequest(BaseModel):
    workflow_id: Annotated[str, Field(
        description="The UUID of the workflow definition to instantiate."
    )]
    inputs: Annotated[Dict[str, Any], Field(
        description="Key-value pairs representing the initial input state (e.g., source text, user intent)."
    )] = {}

# --- Workflows ---

@router.post(
    "/workflows", 
    summary="Create Workflow",
    response_description="A confirmation object with the new Workflow ID."
)
async def create_workflow(
    request: WorkflowCreateRequest, 
    engine: EngineDep
):
    """
    Creates a new workflow definition in the database.

    Args:
        request (WorkflowCreateRequest): The workflow payload containing name and steps.
        engine (WorkflowEngine): The workflow engine dependency.

    Returns:
        dict: The status and generated workflow_id.
    """
    workflow_id = await engine.create_workflow(request.name, request.steps)
    return {"status": "created", "workflow_id": workflow_id}

# --- Executions ---

@router.post(
    "/executions", 
    summary="Start Execution",
    response_description="The ID of the newly started execution background job."
)
async def execute_workflow(
    request: Request, 
    background_tasks: BackgroundTasks, 
    engine: EngineDep
):
    """
    Initiates a new workflow execution asynchronously. 
    Supports Multipart/Form-Data for optional file uploads alongside JSON inputs.

    Args:
        request (Request): The raw FastAPI request (for parsing form data).
        background_tasks (BackgroundTasks): Logic for handling async operations.
        engine (WorkflowEngine): The workflow engine dependency.

    Returns:
        dict: The status and execution_id.

    Raises:
        HTTPException: If workflow_id is missing from the form data.
    """
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
    rec = await engine.repository.get_execution(execution_id)
    cleaned_inputs = rec.get('inputs', {})
    
    # DEBUG: Verify inputs made it
    input_summary = {k: len(str(v)) for k, v in cleaned_inputs.items()}
    logger.info(f"[Router] Triggering execution {execution_id}. Input sizes: {input_summary}")
    
    background_tasks.add_task(engine.run_execution, execution_id, cleaned_inputs)
    
    return {"status": "started", "execution_id": execution_id}

@router.get(
    "/executions/recent", 
    summary="List Recent Executions",
    response_description="A list of recent execution records, sorted by time (descending)."
)
async def get_recent_executions(
    engine: EngineDep,
    limit: int = APIQuery(5, description="Maximum number of executions to return."), 
    status: Optional[str] = APIQuery(None, description="Filter by execution status (e.g., 'completed', 'failed').")
):
    """
    Retrieves a list of the most recent workflow executions.
    """
    all_execs = await engine.repository.get_all_executions()
    if not all_execs: return []
    
    if status:
        all_execs = [ex for ex in all_execs if ex.get('status', '').lower() == status.lower()]

    sorted_execs = sorted(all_execs, key=lambda x: x.get('start_time', ''), reverse=True)
    return sorted_execs[:limit]

@router.get(
    "/executions/latest", 
    summary="Get Latest Execution",
    response_description="The single most recent execution record."
)
async def get_latest_execution(
    engine: EngineDep
):
    """
    Retrieves the absolutely most recent execution record.
    """
    all_execs = await engine.repository.get_all_executions()
    if not all_execs: raise HTTPException(status_code=404, detail="No executions found")
    
    return sorted(all_execs, key=lambda x: x.get('start_time', ''), reverse=True)[0]

@router.get(
    "/executions/{execution_id}", 
    summary="Get Execution Status",
    response_description="The detailed status, result, and state of a specific execution."
)
async def get_execution_status(
    engine: EngineDep,
    execution_id: str = Path(..., description="The UUID of the execution to retrieve.")
):
    """
    Retrieves the full status and result data for a specific execution ID.
    Performs on-the-fly hydration of legacy result structures if necessary.
    """
    status = await engine.get_execution_status(execution_id)
    if not status: raise HTTPException(status_code=404, detail="Execution not found")
    
    # If the workflow is complete and we have a final result state, flatten it for the UI
    if status.get('status') == 'completed' and 'result' in status:
        res = status['result']
        
        if hasattr(res, 'to_flat_dict'):
             status['result'] = res.to_flat_dict()
        
        elif isinstance(res, dict):
             # CHECK IF ALREADY FLAT (V2 Structure)
             if "Report" in res or "Raw_Steps" in res:
                 pass # Already processed, return as is.
             else:
                 # MIGRATION LOGIC:
                 # Even if it's already a dict, it might be the OLD structure (nested steps).
                 # We want to force it through the new 'to_flat_dict' logic to get the 2-layer structure.
                 try:
                     # INJECT MISSING REQUIRED FIELDS for hydration
                     hydration_data = res.copy()
                     if 'execution_id' not in hydration_data:
                         hydration_data['execution_id'] = status.get('execution_id', 'unknown')
                     if 'inputs' not in hydration_data:
                         hydration_data['inputs'] = status.get('inputs', {})
                     
                     # Attempt to hydrate the dict back into a State Object
                     hydrated_state = WorkflowState(**hydration_data)
                     status['result'] = hydrated_state.to_flat_dict()
    
                 except Exception as e:
                     logger.warning(f"Failed to migrate legacy execution result {execution_id}: {e}")
                     # Fallback: leave it as is, legacy UI might handle parts of it
                     pass

    return status

@router.post(
    "/executions/{execution_id}/retry", 
    summary="Retry Execution",
    response_description="Confirmation that the execution is resuming."
)
async def retry_execution(
    background_tasks: BackgroundTasks, 
    engine: EngineDep,
    execution_id: str = Path(..., description="The UUID of the execution to retry.")
):
    """
    Resumes a failed, rejected, or interrupted execution from its last successful state.
    """
    status = await engine.get_execution_status(execution_id)
    if not status: raise HTTPException(status_code=404, detail="Execution not found")
    
    current_status = status.get('status')
    if current_status not in ['failed', 'rejected', 'interrupted']:
         raise HTTPException(status_code=400, detail=f"Cannot retry execution in status '{current_status}'.")

    background_tasks.add_task(engine.resume_execution, execution_id)
    return {"status": "resuming", "execution_id": execution_id}
