import os
import shutil
import json
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Request, Depends, Query as APIQuery, Path
from pydantic import BaseModel, Field

from backend.core.engine import WorkflowEngine
from backend.dependencies import get_engine, get_db_client_dep

from backend.api.tools_router import router as tools_router
from backend.api.agents_router import router as agents_router
from backend.api.admin_router import router as admin_router
from backend.api.llm_router import router as llm_router
from backend.api.config_router import router as config_router
from backend.api.execution_router import router as execution_router
# from backend.api.workflows_router import router as workflows_router # Deprecated/Merged into execution_router

from backend.exceptions import AppException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from backend.settings import get_settings

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
app.include_router(execution_router)
app.include_router(agents_router)
app.include_router(admin_router)
app.include_router(config_router)
app.include_router(llm_router, prefix="/llm", tags=["LLM"])

from backend.api.builder_router import router as builder_router
app.include_router(builder_router)

@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.on_event("startup")
async def startup_event():
    from backend.bootstrap import bootstrap_application
    await bootstrap_application()

# Database setup
settings = get_settings()
print(f"DEBUG: ACTIVE DATABASE PATH: {os.path.abspath(settings.start_db_path)}")

# Ensure data dirs exist
os.makedirs(settings.data_dir, exist_ok=True)
os.makedirs(os.path.dirname(settings.start_db_path), exist_ok=True)
UPLOAD_DIR = os.path.join(settings.data_dir, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# --- Root / DB Endpoints ---

@app.get(
    "/db/seed_data", 
    summary="Get Seed Data", 
    response_description="Returns the full components, steps, and workflows from the database."
)
async def get_seed_data(engine: WorkflowEngine = Depends(get_engine)):
    """
    Retrieves the raw seed data configuration (components, steps, workflows).

    Args:
        engine (WorkflowEngine): Dependency.

    Returns:
        dict: Object containing lists of components, steps, and workflows.
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

@app.get(
    "/db/workflows", 
    summary="List Workflows (DB)", 
    response_description="A list of all workflow definitions."
)
async def get_workflows(engine: WorkflowEngine = Depends(get_engine)):
    """
    Retrieves all workflow definitions from the repository.

    Args:
        engine (WorkflowEngine): Dependency.

    Returns:
        List[dict]: List of workflow objects.
    """
    try:
        workflows = engine.repository.get_all_workflows()
        return workflows
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/db/preview_prompt/{step_id}", 
    summary="Preview Step Prompt", 
    response_description="The constructed prompt segments for a specific step."
)
async def preview_prompt(
    step_id: str = Path(..., description="The ID of the step to preview."), 
    engine: WorkflowEngine = Depends(get_engine)
):
    """
    Previews the prompt that would be generated for a specific step ID.

    Args:
        step_id (str): Step Identifier.
        engine (WorkflowEngine): Dependency.

    Returns:
        dict: Prompt structure (user, system, parts).

    Raises:
        HTTPException: If prompt generation fails.
    """
    try:
        preview = engine.preview_step_prompt(step_id)
        if "error" in preview:
            raise HTTPException(status_code=400, detail=preview["error"])
        return preview
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/db/preview_full_chain/{workflow_id}", 
    summary="Preview Full Chain", 
    response_description="The concatenated full prompt chain for deep auditing."
)
async def preview_full_chain(
    workflow_id: str = Path(..., description="The ID of the workflow."), 
    engine: WorkflowEngine = Depends(get_engine)
):
    """
    Generates a full textual preview of the entire sequential audit chain.

    Args:
        workflow_id (str): Workflow Identifier.
        engine (WorkflowEngine): Dependency.

    Returns:
        dict: Object containing 'full_chain_text'.
    """
    try:
        preview_text = engine.preview_full_chain_prompts(workflow_id)
        if preview_text.startswith("Error"):
            raise HTTPException(status_code=404, detail=preview_text)
        return {"full_chain_text": preview_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/config/introspection", 
    summary="Introspect Codebase", 
    response_description="Lists available schemas, hooks, and agents found in code."
)
def introspect_codebase():
    """
    Performs runtime introspection of the backend codebase to discover available resources.

    Returns:
        dict: Lists of schemas, hooks, and agents.
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

@app.get(
    "/health", 
    summary="Health Check", 
    response_description="Simple status indicator."
)
def health_check():
    """
    Basic liveness probe.
    """
    return {"status": "ok"}
