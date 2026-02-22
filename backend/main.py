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
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.api import (
    admin_router,
    agents_router,
    api_router,
    audit_router,
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

    # 1. LOG TO FILE (Detailed Audit)
    logger.info("======================================================================")
    logger.info("   COGNITIVE QUORUM BACKEND (V2.9) - STARTING UP")
    logger.info("======================================================================")

    # 2. PRINT TO CONSOLE (Minimal)
    print("===================================================")
    print("  CQ BACKEND (V2.9) STARTED")
    print("  -> Log: backend_debug.log (CHECK FOR DETAILS)")
    print("  -> Doc: http://localhost:8000/docs")
    print("===================================================")

    try:
        # A. Initialize Task Registry (Trigger Decorators)
        # Import task modules to ensure @TaskRegistry.register_task runs
        import backend.tasks.security  # noqa
        import backend.tasks.retrieval  # noqa
        import backend.tasks.analysis  # noqa
        import backend.tasks.critique  # noqa
        import backend.tasks.interaction  # noqa
        import backend.tasks.judgment  # noqa
        import backend.tasks.coaching  # noqa
        import backend.tasks.panel  # noqa
        import backend.tasks.reporting  # noqa

        # Log Task Count to File
        task_count = len(TaskRegistry._tasks)
        logger.info(f"[StartupAudit] Task Registry: {task_count} tasks loaded.")
        logger.info(f"[StartupAudit] Auth Mode: {'FIREBASE' if settings.use_firebase_auth else 'MOCK'}")
        logger.info(f"[StartupAudit] DB Mode: {settings.storage_backend}")
        logger.info(f"[StartupAudit] LLM Provider: {'VERTEX' if settings.use_vertex_llm else 'OPENAI'}")

        # B. Load Workflows (Mock/File-based seeding for now)
        # In a real app, this might sync to DB.
        # Here we just verify the file exists.
        workflow_dir = "data/workflows"
        if os.path.exists(workflow_dir):
            files = [f for f in os.listdir(workflow_dir) if f.endswith(".json")]
            logger.info(f"[StartupAudit] Workflows Detected: {len(files)} files in {workflow_dir}.")

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


class LocalizationMiddleware(BaseHTTPMiddleware):
    """Middleware to inject Accept-Language into context."""

    async def dispatch(self, request: Request, call_next):
        from backend.services.localization import set_language

        # Extract Accept-Language header (e.g., "fi,en;q=0.9")
        # For simplicity, we take the first preferred language.
        accept_language = request.headers.get("Accept-Language", "en")

        # Parse logic could be more robust (q-factor), but splitting by comma/semi-colon is a good start
        # "fi,en;q=0.9" -> "fi"
        preferred_lang = accept_language.split(",")[0].split(";")[0].strip()

        # Set Context
        set_language(preferred_lang)

        response = await call_next(request)
        return response


app.add_middleware(LocalizationMiddleware)


# --- 4. Global Error Handlers (RFC 7807 Problem Details) ---

from backend.exceptions import AppException, ErrorCodes, format_validation_error


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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Catches Pydantic validation errors and returns RFC 7807 Problem Details."""
    logger = logging.getLogger("backend.main")

    # 1. Format readable detail first
    readable_detail = format_validation_error(exc)

    # 2. Log: Summary first (easy to read), then details
    logger.error(f"VALIDATION ERROR: {readable_detail}")
    logger.debug(f"Raw Schema Errors: {exc.errors()}")

    # 3. Return RFC 7807 with Error Code for Client Localization
    error_code = ErrorCodes.VALIDATION_FAILED

    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(
            {
                "type": "https://api.quorum.fi/errors/validation-failed",  # Machine readable URI
                "title": "Validation Failed",  # Fallback title
                "status": 422,
                "detail": readable_detail,
                "instance": str(request.url.path),
                "extensions": {
                    "error_code": error_code.value,  # Client uses this for L10n key
                    "errors": exc.errors(),
                },
            }
        ),
        media_type="application/problem+json",
    )


from slowapi.errors import RateLimitExceeded

from backend.core.rate_limit import rate_limit_exceeded_handler


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded):
    """Catches RateLimitExceeded and delegates to the strict handler."""
    return rate_limit_exceeded_handler(request, exc)


from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Catches standard HTTP errors (404, 405) and returns RFC 7807."""
    logger = logging.getLogger("backend.main")
    logger.warning(f"HTTP_ERROR: {exc.detail} (Status: {exc.status_code})")

    # Map HTTP status to approximate error code for L10n
    if exc.status_code == 404:
        error_code = ErrorCodes.RESOURCE_NOT_FOUND.value
    elif exc.status_code == 401:
        error_code = ErrorCodes.AUTHENTICATION_FAILED.value
    elif exc.status_code == 403:
        error_code = ErrorCodes.PERMISSION_DENIED.value
    else:
        error_code = "HTTP_ERROR"

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {
                "type": "about:blank",
                "title": "HTTP Error",
                "status": exc.status_code,
                "detail": exc.detail,
                "instance": str(request.url.path),
                "extensions": {"error_code": error_code.value if hasattr(error_code, "value") else error_code},
            }
        ),
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
app.include_router(agents_router.router)
app.include_router(builder_router)
app.include_router(settings_router.router)
app.include_router(llm_router.router)
app.include_router(organization_router.router)
app.include_router(tools_router.router)
app.include_router(tools_router.router)
app.include_router(audit_router.router)


print("Updated backend/main.py with Lifespan and V2 Router.")
