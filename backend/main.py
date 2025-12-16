import os
import shutil
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request, Depends
from pydantic import BaseModel
# from tinydb import Query # Removed

from backend.services.document_processor import DocumentProcessor
from backend.core.engine import WorkflowEngine
from backend.dependencies import get_engine, get_db_client_dep

from backend.api.tools_router import router as tools_router

from backend.api.agents_router import router as agents_router
from backend.api.admin_router import router as admin_router
from backend.api.llm_router import router as llm_router
from backend.api.config_router import router as config_router
from backend.api.workflows_router import router as workflows_router
from backend.exceptions import AppException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from backend.config import DB_PATH, DATA_DIR

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Cognitive Quorum API",
    description="Backend for Cognitive Quorum application.",
    version="0.2.0"
)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message, "details": exc.details, "status": "error"}
    )


app.include_router(tools_router)
app.include_router(agents_router)
app.include_router(admin_router)
app.include_router(config_router)
app.include_router(workflows_router)
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
    
    # Warmup Engine Singleton
    try:
        logger.info("   [INFO] Warming up Engine Singleton...")
        from backend.dependencies import get_db_client_dep, get_repository_dep, get_agent_registry_dep, get_prompt_builder_dep
        from backend.exceptions import FatalInterruption # Import locally
        
        # Manually resolve dependencies to avoid Depends() objects leaking in
        db = get_db_client_dep()
        repo = get_repository_dep(db)
        registry = get_agent_registry_dep(repo)
        pb = get_prompt_builder_dep(repo, registry)
        
        # Initialize Engine with resolved deps
        get_engine(repository=repo, registry=registry, prompt_builder=pb)
        logger.info("   [INFO] Engine Ready.")
        
    except FatalInterruption as fi:
        logger.critical("!"*60)
        logger.critical(f"   [CRITICAL STARTUP FAILURE] {fi.step_name}")
        logger.critical(f"   Reason: {fi.reason}")
        logger.critical(f"   Details: {json.dumps(fi.details, indent=2)}")
        logger.critical("!"*60)
        # We don't exit(1) because Uvicorn manages the process, but we log loud.
        # Ideally we might raise to crash the pod/service.
        # Re-raise to let exception handler or Uvicorn see it? 
        # Actually raising here during startup cancels startup.
        raise fi
        
    except Exception as e:
        logger.error(f"   [CRITICAL] Engine Warmup Failed: {e}", exc_info=True)
        # Raise to abort startup
        raise RuntimeError(f"Startup Failed: {e}")


# Database setup
# Robust path resolution for DB
print(f"DEBUG: ACTIVE DATABASE PATH: {os.path.abspath(DB_PATH)}")

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

# Ensure data and database dirs exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Database setup
# Robust path resolution for DB
print(f"DEBUG: ACTIVE DATABASE PATH: {os.path.abspath(DB_PATH)}")

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

# Ensure data and database dirs exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Global Engine REMOVED in favor of DI (backend.dependencies.get_engine)

# Ensure upload directory exists
# Ensure upload directory exists
UPLOAD_DIR = os.path.join(DATA_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)





@app.get("/db/seed_data")
async def get_seed_data(engine: WorkflowEngine = Depends(get_engine)):
    """
    Returns the content of seed data from the database.
    """
    try:
        components = engine.repository.get_all_components()
        steps = engine.repository.get_all_steps()
        workflows = engine.repository.get_all_workflows()
        
        return {
            "components": components,
            "steps": steps,
            "workflows": workflows
        }
    except Exception as e:
        print(f"DEBUG: Error reading seed data from DB: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/workflows")
async def get_workflows(engine: WorkflowEngine = Depends(get_engine)):
    """
    Returns all workflows from the database.
    """
    try:
        workflows = engine.repository.get_all_workflows()
        return workflows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/preview_prompt/{step_id}")
async def preview_prompt(step_id: str, engine: WorkflowEngine = Depends(get_engine)):
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
async def preview_full_chain(workflow_id: str, engine: WorkflowEngine = Depends(get_engine)):
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





@app.get("/config/introspection")
def introspect_codebase():
    """
    Returns available Schemas and Hooks by inspecting the codebase.
    """
    import inspect
    from backend.models import domain

    
    # 1. Inspect Schemas
    available_schemas = []
    for name, obj in inspect.getmembers(domain):
        if inspect.isclass(obj) and issubclass(obj, domain.BaseModel) and obj is not domain.BaseModel:
            available_schemas.append(name)
            
    # 2. Inspect Hooks (Legacy - Deprecated/Removed)
    available_hooks = []


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
        "hooks": [],
        "agents": sorted(list(set(available_agents)))
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
