"""Main entrypoint for the Cognitive Quorum Backend API.

Adheres to V2.9 Architecture:
- Lifespan State Management
- One Truth Error Protocol
- V2 Execution Router
- Task Registry Initialization
"""

import json
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api import (
    execution_router,
    auth_router,
    admin_router,
    agents_router,
    builder_router,
    settings_router,
    llm_router,
    organization_router
)
from backend.core.registry import TaskRegistry
from backend.logging_config import configure_logfire, setup_logging
from backend.schemas.error import APIError
from backend.settings import get_settings

# --- 1. Lifespan Management ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and shutdown lifecycle."""
    # STARTUP
    setup_logging()
    configure_logfire()
    logger = logging.getLogger("backend.main")
    logger.info("Initializing Cognitive Quorum Backend (V2.9)...")

    try:
        # A. Initialize Task Registry (Trigger Decorators)
        # Import task modules to ensure @TaskRegistry.register_task runs
        import backend.tasks.security  # noqa
        import backend.tasks.retrieval # noqa
        import backend.tasks.analysis  # noqa
        import backend.tasks.critique  # noqa
        
        logger.info(f"Task Registry initialized with {len(TaskRegistry._tasks)} tasks.")

        # B. Load Workflows (Mock/File-based seeding for now)
        # In a real app, this might sync to DB.
        # Here we just verify the file exists.
        workflow_dir = "data/workflows"
        if os.path.exists(workflow_dir):
            files = [f for f in os.listdir(workflow_dir) if f.endswith(".json")]
            logger.info(f"Detected {len(files)} workflow definitions in {workflow_dir}.")
        
        yield
        
    except Exception as e:
        logger.critical(f"Startup failed: {e}", exc_info=True)
        raise
        
    finally:
        # SHUTDOWN
        logger.info("Shutting down...")

# --- 2. Application Setup ---

settings = get_settings()

app = FastAPI(
    title="Cognitive Quorum API",
    version="2.9.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- 3. Middleware ---

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],  # Allow Flutter client
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# --- 4. Global Error Handlers (One Truth Protocol) ---

from backend.exceptions import AppException

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Catches domain-specific AppExceptions and returns uniform APIError response."""
    # We log with the specific error code from the exception
    # Fallback to message if it looks like an error code (SCREAMING_SNAKE_CASE)
    error_code = exc.details.get("error_code") or exc.details.get("code")
    if not error_code and exc.message.isupper() and " " not in exc.message:
        error_code = exc.message
    
    error_code = error_code or "APP_ERROR"
    
    logging.getLogger("backend.main").error(f"{error_code}: {exc.message} (Status: {exc.status_code})")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=APIError(
            error_code=error_code,
            message=exc.message,
            details=exc.details
        ).model_dump()
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catches all unhandled exceptions and returns a uniform APIError response."""
    logging.getLogger("backend.main").error(f"Global Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=APIError(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected system error occurred.",
            details={"original_error": str(exc)}
        ).model_dump()
    )

# --- 5. Routers ---

# ...

app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(execution_router.router)          # V2 Router
app.include_router(execution_router.workflow_router) # V2 Workflow Router
app.include_router(execution_router.executions_router) # Executions Router
app.include_router(agents_router.router)
app.include_router(builder_router.router)
app.include_router(settings_router.router)
app.include_router(llm_router.router)
app.include_router(organization_router.router)

# Include legacy routers if needed, or remove them.
# app.include_router(legacy_router)
print("Updated backend/main.py with Lifespan and V2 Router.")
