import os
import shutil
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from tinydb import Query

from backend.services.document_processor import DocumentProcessor
from backend.core.engine import WorkflowEngine
from backend.api.hooks_router import router as hooks_router
from backend.api.tools_router import router as tools_router
from backend.api.agents_router import router as agents_router
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

@app.on_event("startup")
async def startup_event():
    from datetime import datetime
    from backend.logging_config import setup_logging
    import logging
    
    # Initialize Logging
    setup_logging(log_level=logging.DEBUG) # Set to DEBUG for detailed traces
    logger = logging.getLogger("backend.main")
    
    logger.info("="*50)
    logger.info(f"   Cognitive Quorum Backend v0.2.0")
    logger.info(f"   Startup Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*50)
    
    # DB Path
    logger.info(f"   [CONFIG] Database Path: {os.path.abspath(DB_PATH)}")
    
    # LLM Config
    llm_model = os.getenv("GEMINI_MODEL", "Not Set (Using Default)")
    from backend.config import USE_MOCK_LLM
    logger.info(f"   [CONFIG] LLM Model: {llm_model}")
    
    if USE_MOCK_LLM:
        logger.warning("!"*50)
        logger.warning("   [INFO] OPERATING IN MOCK LLM MODE")
        logger.warning("   [INFO] No external API calls will be made.")
        logger.warning("!"*50)
    else:
        logger.info("="*50)
        logger.info("   [INFO] OPERATING IN REAL LLM MODE")
        logger.info("   [INFO] External API calls WILL be made.")
        logger.info("="*50)
    
    # Google Search Config
    search_key = os.getenv("GOOGLE_SEARCH_API_KEY")
    search_cx = os.getenv("GOOGLE_SEARCH_CX")
    if search_key and search_cx:
        logger.info(f"   [CONFIG] Google Search: ENABLED (Key: ...{search_key[-4:]})")
    else:
        logger.info(f"   [CONFIG] Google Search: DISABLED (Missing Key or CX)")
        
    logger.info("="*50)

# Database setup
# Robust path resolution for DB
print(f"DEBUG: ACTIVE DATABASE PATH: {os.path.abspath(DB_PATH)}")

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

# Ensure data and database dirs exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

from backend.database.wrapper import get_db_client
db_client = get_db_client()
engine = WorkflowEngine(DB_PATH)

# Initialize/Seed Components
engine.register_component("DocumentProcessor", "processor", "DocumentProcessor")
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
# Ensure upload directory exists
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- Generic Workflow Endpoints ---

class WorkflowCreateRequest(BaseModel):
    name: str
    steps: List[Dict[str, Any]]

class WorkflowExecutionRequest(BaseModel):
    workflow_id: str
    inputs: Dict[str, Any] = {}

@app.post("/workflows")
def create_workflow(request: WorkflowCreateRequest):
    """
    Creates a new workflow definition.
    """
    workflow_id = engine.create_workflow(request.name, request.steps)
    return {"status": "created", "workflow_id": workflow_id}

@app.post("/executions")
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/executions/recent")
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
        sorted_execs = sorted(all_execs, key=lambda x: x.get('start_time', ''), reverse=True)
        return sorted_execs[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/executions/latest")
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
        # Assuming start_time is ISO string, which sorts correctly lexicographically
        latest = sorted(all_execs, key=lambda x: x.get('start_time', ''), reverse=True)[0]
        return latest
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/executions/{execution_id}")
async def get_execution_status(execution_id: str):
    """
    Gets the status of a workflow execution.
    """
    status = engine.get_execution_status(execution_id)
    if not status:
        raise HTTPException(status_code=404, detail="Execution not found")
    return status



@app.get("/db/seed_data")
@app.get("/db/seed_data")
async def get_seed_data():
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
async def get_workflows():
    """
    Returns all workflows from the database.
    """
    try:
        workflows = engine.workflows_table.all()
        return workflows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/preview_prompt/{step_id}")
async def preview_prompt(step_id: str):
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
async def preview_full_chain(workflow_id: str):
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



@app.get("/orchestrator/status/{execution_id}")
def get_orchestrator_status(execution_id: str):
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
    from backend.models import domain
    from backend.services import hooks
    
    # 1. Inspect Schemas
    available_schemas = []
    for name, obj in inspect.getmembers(domain):
        if inspect.isclass(obj) and issubclass(obj, domain.BaseModel) and obj is not domain.BaseModel:
            available_schemas.append(name)
            
    # 2. Inspect Hooks
    available_hooks = []
    for name, obj in inspect.getmembers(hooks):
        if inspect.isfunction(obj) and not name.startswith("_"):
            available_hooks.append(name)

    # 3. Inspect Agents
    available_agents = []
    from backend.agents import base, guard, analyst, logician, critics, judge, panel, xai
    
    agent_modules = [base, guard, analyst, logician, critics, judge, panel, xai]
    
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
