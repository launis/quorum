import os
import shutil
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from tinydb import TinyDB, Query

from backend.processor import PDFProcessor
from backend.engine import WorkflowEngine
from backend.api.hooks_router import router as hooks_router
from backend.api.tools_router import router as tools_router
from backend.api.agents_router import router as agents_router
from backend.api.templates_router import router as templates_router
from backend.api.admin_router import router as admin_router
from backend.api.llm_router import router as llm_router
from backend.api.config_router import router as config_router
from dotenv import load_dotenv
from backend.config import DB_PATH, DATA_DIR

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Cognitive Quorum API",
    description="Backend for Cognitive Quorum application.",
    version="0.2.0"
)

app.include_router(hooks_router)
app.include_router(tools_router)
app.include_router(agents_router)
app.include_router(templates_router)
app.include_router(admin_router)
app.include_router(config_router)
app.include_router(llm_router, prefix="/llm", tags=["LLM"])

@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Database setup
# Robust path resolution for DB
print(f"DEBUG: ACTIVE DATABASE PATH: {os.path.abspath(DB_PATH)}")

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

db = TinyDB(DB_PATH, encoding='utf-8')
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
def create_workflow(request: WorkflowCreateRequest):
    """
    Creates a new workflow definition.
    """
    workflow_id = engine.create_workflow(request.name, request.steps)
    return {"status": "created", "workflow_id": workflow_id}

@app.post("/executions")
def execute_workflow(request: WorkflowExecutionRequest, background_tasks: BackgroundTasks):
    """
    Starts a workflow execution asynchronously.
    """
    try:
        # 1. Create Execution Record (Sync, Fast)
        execution_id = engine.create_execution(request.workflow_id, request.inputs)
        
        # 2. Schedule Execution in Background
        background_tasks.add_task(engine.run_execution, execution_id)
        
        return {"status": "started", "execution_id": execution_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/executions/{execution_id}")
def get_execution_status(execution_id: int):
    """
    Gets the status of a workflow execution.
    """
    status = engine.get_execution_status(execution_id)
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")
    return status

@app.get("/db/seed_data")
@app.get("/db/seed_data")
def get_seed_data():
    """
    Returns the content of seed data from the database.
    """
    try:
        components = engine.components_table.all()
        steps = engine.steps_table.all()
        workflows = engine.workflows_table.all()
        
        return {
            "components": components,
            "steps": steps,
            "workflows": workflows
        }
    except Exception as e:
        print(f"DEBUG: Error reading seed data from DB: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/workflows")
def get_workflows():
    """
    Returns all workflows from the database.
    """
    try:
        workflows = engine.workflows_table.all()
        return workflows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/preview_prompt/{step_id}")
def preview_prompt(step_id: str):
    """
    Returns a preview of the prompt for a given step.
    """
    try:
        preview = engine.preview_step_prompt(step_id)
        if "error" in preview:
            raise HTTPException(status_code=400, detail=preview["error"])
        return preview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/preview_full_chain/{workflow_id}")
def preview_full_chain(workflow_id: str):
    """
    Returns a full chain prompt preview for a given workflow.
    """
    try:
        preview_text = engine.preview_full_chain_prompts(workflow_id)
        if preview_text.startswith("Error"):
            raise HTTPException(status_code=404, detail=preview_text)
        return {"full_chain_text": preview_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Legacy / Helper Endpoints ---

@app.post("/orchestrator/run")
def run_orchestrator(
    workflow_id: str,
    background_tasks: BackgroundTasks,
    history_file: UploadFile = File(...),
    product_file: UploadFile = File(...),
    reflection_file: UploadFile = File(...)
):
    """
    Uploads files, extracts text using DataHandler, and starts the workflow asynchronously.
    """
    from backend.data_handler import DataHandler
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

        # 1. Create Execution Record (Sync, Fast)
        execution_id = engine.create_execution(workflow_id, inputs)
        
        # 2. Schedule Execution in Background
        background_tasks.add_task(engine.run_execution, execution_id)
        
        return {
            "status": "started",
            "execution_id": execution_id,
            "message": "Workflow started successfully (Async)"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Orchestration failed: {str(e)}")

@app.get("/orchestrator/status/{execution_id}")
def get_orchestrator_status(execution_id: int):
    """
    Gets the status of a workflow execution.
    """
    status = engine.get_execution_status(execution_id)
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")
    return status

@app.get("/config/introspection")
def introspect_codebase():
    """
    Returns available Schemas and Hooks by inspecting the codebase.
    """
    import inspect
    from backend import schemas, hooks
    
    # 1. Inspect Schemas
    available_schemas = []
    for name, obj in inspect.getmembers(schemas):
        if inspect.isclass(obj) and issubclass(obj, schemas.BaseModel) and obj is not schemas.BaseModel:
            available_schemas.append(name)
            
    # 2. Inspect Hooks
    available_hooks = []
    for name, obj in inspect.getmembers(hooks):
        if inspect.isfunction(obj) and not name.startswith("_"):
            available_hooks.append(name)

    # 3. Inspect Agents
    available_agents = []
    from backend.agents import base, guard, analyst, logician, critics, judge, panel
    
    agent_modules = [base, guard, analyst, logician, critics, judge, panel]
    
    for module in agent_modules:
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and name.endswith("Agent") and name != "BaseAgent":
                available_agents.append(name)
            
    return {
        "schemas": sorted(available_schemas),
        "hooks": sorted(available_hooks),
        "agents": sorted(list(set(available_agents)))
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
