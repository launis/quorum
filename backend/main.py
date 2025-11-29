import os
import shutil
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from tinydb import TinyDB, Query

from processor import PDFProcessor
from engine import WorkflowEngine

app = FastAPI(
    title="Cognitive Quorum API",
    description="Backend for Cognitive Quorum application.",
    version="0.2.0"
)

# Database setup
DB_PATH = '/app/data/db.json'
db = TinyDB(DB_PATH)
engine = WorkflowEngine(DB_PATH)

# Initialize/Seed Components
engine.register_component("PDFExtractor", "processor", "PDFProcessor")
engine.register_component("GuardAgent", "backend.agents.guard", "GuardAgent")
engine.register_component("AnalystAgent", "backend.agents.analyst", "AnalystAgent")
engine.register_component("LogicianAgent", "backend.agents.logician", "LogicianAgent")
engine.register_component("LogicalFalsifierAgent", "backend.agents.critics", "LogicalFalsifierAgent")
engine.register_component("FactualOverseerAgent", "backend.agents.critics", "FactualOverseerAgent")
engine.register_component("CausalAnalystAgent", "backend.agents.critics", "CausalAnalystAgent")
engine.register_component("PerformativityDetectorAgent", "backend.agents.critics", "PerformativityDetectorAgent")
engine.register_component("JudgeAgent", "backend.agents.judge", "JudgeAgent")
engine.register_component("XAIReporterAgent", "backend.agents.judge", "XAIReporterAgent")

# Ensure upload directory exists
UPLOAD_DIR = "/app/data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Generic Workflow Endpoints ---

class WorkflowCreateRequest(BaseModel):
    name: str
    steps: List[Dict[str, Any]]

class WorkflowExecutionRequest(BaseModel):
    workflow_id: int
    inputs: Dict[str, Any] = {}

@app.post("/workflows")
async def create_workflow(request: WorkflowCreateRequest):
    """
    Creates a new workflow definition.
    """
    workflow_id = engine.create_workflow(request.name, request.steps)
    return {"status": "created", "workflow_id": workflow_id}

@app.post("/executions")
async def execute_workflow(request: WorkflowExecutionRequest):
    """
    Starts a workflow execution.
    """
    try:
        execution_id = engine.execute_workflow(request.workflow_id, request.inputs)
        return {"status": "started", "execution_id": execution_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/executions/{execution_id}")
async def get_execution_status(execution_id: int):
    """
    Gets the status of a workflow execution.
    """
    status = engine.get_execution_status(execution_id)
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")
    return status

# --- Legacy / Helper Endpoints ---

@app.post("/orchestrator/run")
async def run_orchestrator(
    workflow_id: str,
    history_file: UploadFile = File(...),
    product_file: UploadFile = File(...),
    reflection_file: UploadFile = File(...)
):
    """
    Uploads files, extracts text using DataHandler, and starts the workflow.
    """
    from data_handler import DataHandler
    handler = DataHandler()

    try:
        # Extract text from uploaded files
        history_text = handler.read_file_content(history_file)
        product_text = handler.read_file_content(product_file)
        reflection_text = handler.read_file_content(reflection_file)

        # Prepare inputs for the workflow
        inputs = {
            "history_text": history_text,
            "product_text": product_text,
            "reflection_text": reflection_text
        }

        # Execute workflow
        # Note: workflow_id is passed as a query parameter
        execution_id = engine.execute_workflow(workflow_id, inputs)
        
        return {
            "status": "started",
            "execution_id": execution_id,
            "message": "Workflow started successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")

@app.get("/orchestrator/status/{execution_id}")
async def get_orchestrator_status(execution_id: int):
    """
    Gets the status of a workflow execution.
    """
    status = engine.get_execution_status(execution_id)
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")
    return status

@app.get("/health")
def health_check():
    return {"status": "ok"}
