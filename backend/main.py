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

@app.post("/upload")
async def upload_files(
    prompt_file: UploadFile = File(...),
    history_file: UploadFile = File(...),
    product_file: UploadFile = File(...),
    reflection_file: UploadFile = File(...)
):
    """
    Uploads files and returns their paths. 
    Does NOT trigger processing automatically anymore (use Workflows for that).
    """
    files = [prompt_file, history_file, product_file, reflection_file]
    saved_filenames = {}

    try:
        for file in files:
            file_location = f"{UPLOAD_DIR}/{file.filename}"
            with open(file_location, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)
            # Map the field name to the saved path
            if file == prompt_file: saved_filenames['prompt_path'] = file_location
            if file == history_file: saved_filenames['history_path'] = file_location
            if file == product_file: saved_filenames['product_path'] = file_location
            if file == reflection_file: saved_filenames['reflection_path'] = file_location

        return {
            "status": "success",
            "message": "Files uploaded successfully",
            "file_paths": saved_filenames
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "ok"}
