"""Main entrypoint for the Cognitive Quorum Backend API.

Adheres to V2.9 Architecture:
- Lifespan State Management
- One Truth Error Protocol
- V2 Execution Router
- Task Registry Initialization
"""

import logging
import os
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.api import (
    admin_router,
    agents_router,
    api_router,
    auth_router,
    builder_router,
    llm_router,
    organization_router,
    settings_router,
    tools_router,
)
from backend.context import set_request_context
from backend.core.registry import TaskRegistry
from backend.logging_config import configure_logfire, setup_logging
from backend.settings import get_settings

# --- 1. Lifespan Management ---


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages application startup and shutdown lifecycle."""
    # STARTUP
    setup_logging()
    configure_logfire()
    logger = logging.getLogger("backend.main")

    # VISUAL SEPARATOR FOR LOG READABILITY
    logger.info("======================================================================")
    logger.info("   COGNITIVE QUORUM BACKEND (V2.9) - STARTING UP")
    logger.info("======================================================================")

    try:
        # A. Initialize Task Registry (Trigger Decorators)
        # Import task modules to ensure @TaskRegistry.register_task runs
        import backend.tasks.security  # noqa
        import backend.tasks.retrieval  # noqa
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


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to inject Request ID into context."""

    async def dispatch(self, request: Request, call_next):
        """Process the request."""
        # Trust upstream ID or generate new one
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # Set context
        set_request_context(request_id)

        response = await call_next(request)

        # Add header to response for client tracing
        response.headers["X-Request-ID"] = request_id

        # Clear context (for thread safety in some async servers, though ContextVars handle this well)
        # clear_request_context() # Optional/Redundant with ContextVars but strict safety.

        return response

app.add_middleware(RequestIdMiddleware)


# --- 4. Global Error Handlers (RFC 7807 Problem Details) ---

from backend.exceptions import AppException


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Catches domain-specific AppExceptions and returns RFC 7807 Problem Details."""
    logger = logging.getLogger("backend.main")
    logger.error(f"{exc.error_code}: {exc.message} (Status: {exc.status_code})")

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_problem_detail(instance=str(request.url.path)),
        media_type="application/problem+json",
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catches all unhandled exceptions and returns RFC 7807 Problem Details."""
    logger = logging.getLogger("backend.main")
    logger.error(f"INTERNAL_SERVER_ERROR: {exc}", exc_info=True)

    # Create a generic AppException for RFC 7807 formatting
    error = AppException(
        message="An unexpected system error occurred.",
        status_code=500,
        details={"error_code": "INTERNAL_SERVER_ERROR", "original_error": str(exc)},
    )

    return JSONResponse(
        status_code=500,
        content=error.to_problem_detail(instance=str(request.url.path)),
        media_type="application/problem+json",
    )


# --- 5. Routers ---

# ...

app.include_router(auth_router.router)
app.include_router(admin_router.router)
app.include_router(api_router)  # V2.9 Aggregated Router (Config + Execution)
# app.include_router(config_router.router) - Replaced by api_router
# app.include_router(execution_router.router)  - Replaced by api_router
app.include_router(agents_router.router)
app.include_router(builder_router)
app.include_router(settings_router.router)
app.include_router(llm_router.router)
app.include_router(organization_router.router)
app.include_router(tools_router.router)

print("Updated backend/main.py with Lifespan and V2 Router.")
