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
from typing import Any

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# from backend_v2.api.auth_router import router as auth_router
# from backend_v2.api.v2.core_router import router as core_router
# from backend_v2.api.v2.system_router import router as system_router
from backend_v2.context import set_request_context
from backend_v2.logging_config import configure_logfire, setup_logging
from backend_v2.settings import get_settings

# --- 1. Lifespan Management ---


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Manages application startup and shutdown lifecycle."""
    # STARTUP
    setup_logging()
    configure_logfire()
    logger = logging.getLogger("backend.main")

    # 1. LOG TO FILE (Detailed Audit)
    logger.info("======================================================================")
    logger.info("   COGNITIVE QUORUM BACKEND (V2.9) - STARTING UP")
    logger.info("======================================================================")

    # Output is handled by loggers to backend_debug.log

    try:
        # A. Initialize Task Registry / Hook Registry (Trigger Decorators)
        import backend_v2.hooks  # noqa: F401

        # B. Load Workflows (Mock/File-based seeding for now)
        # In a real app, this might sync to DB.
        # Here we just verify the file exists.
        workflow_dir = "data/workflows"
        if os.path.exists(workflow_dir):
            files = [f for f in os.listdir(workflow_dir) if f.endswith(".json")]
            logger.info(f"[StartupAudit] Workflows Detected: {len(files)} files in {workflow_dir}.")

        # C. Initialize Arq Redis Pool
        # We attempt to connect to the configured Redis instance, otherwise fallback to in-memory fake redis.
        from arq.connections import RedisSettings, create_pool

        try:
            settings = get_settings()
            app.state.arq_pool = await create_pool(RedisSettings(host=settings.redis_host, port=settings.redis_port))
            logger.info(f"Connected to Arq Redis at {settings.redis_host}:{settings.redis_port}")
        except Exception as redis_err:
            logger.warning(f"Failed to connect to real Redis: {redis_err}. Falling back to FakeRedis.")
            from backend_v2.utils.redis_patcher import get_patched_fakeredis_pool

            app.state.arq_pool = get_patched_fakeredis_pool()

        yield

    except Exception as e:
        logger.critical(f"Startup failed: {e}", exc_info=True)
        raise

    finally:
        # SHUTDOWN
        logger.info("Shutting down...")
        if hasattr(app.state, "arq_pool") and app.state.arq_pool:
            try:
                # Modern redis-py: use aclose() or close(), wait_closed() is removed
                if hasattr(app.state.arq_pool, "aclose"):
                    await app.state.arq_pool.aclose()
                elif hasattr(app.state.arq_pool, "close"):
                    await app.state.arq_pool.close()
            except Exception as close_err:
                logger.error(f"Error closing Arq pool: {close_err}")


# --- 2. Application Setup ---

settings = get_settings()

app = FastAPI(
    title="Cognitive Quorum API",
    version="2.9.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

try:
    import logfire

    logfire.instrument_fastapi(app)
except ImportError:
    pass
except Exception:
    logging.getLogger("backend.main").error("Failed to instrument FastAPI with Logfire.", exc_info=True)
    raise

# (duplicate validation handler removed)

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

    async def dispatch(self, request: Request, call_next):  # type: ignore
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

    async def dispatch(self, request: Request, call_next):  # type: ignore
        from backend_v2.services.localization import set_language

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

from backend_v2.exceptions import AppException, ErrorCodes, format_validation_error


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Catches domain-specific AppExceptions and returns RFC 7807 Problem Details."""
    logger = logging.getLogger("backend.main")

    # Extract the Enum Name if it's an ErrorCode, otherwise use the string.
    err_name = exc.error_code.name if hasattr(exc.error_code, "name") else str(exc.error_code)
    logger.error(f"[FastAPI] {err_name}: {exc.message} (Status: {exc.status_code})")

    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_problem_detail(instance=str(request.url.path)),
        media_type="application/problem+json",
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Catches Pydantic validation errors and returns RFC 7807 Problem Details."""
    logger = logging.getLogger("backend.main")

    # 1. Format readable detail first
    readable_detail = format_validation_error(exc)

    # 2. Log: Summary first (easy to read), then details
    error_code = ErrorCodes.VALIDATION_FAILED
    logger.error(f"[FastAPI] {error_code.name}: VALIDATION ERROR: {readable_detail}")
    logger.debug(f"[FastAPI] Raw Schema Errors: {exc.errors()}")

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

from backend_v2.core.rate_limit import rate_limit_exceeded_handler


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded) -> Any:
    """Catches RateLimitExceeded and delegates to the strict handler."""
    return rate_limit_exceeded_handler(request, exc)


from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    # Map HTTP status to approximate error code for L10n
    error_code_enum = None
    if exc.status_code == 404:
        error_code_enum = ErrorCodes.RESOURCE_NOT_FOUND
    elif exc.status_code == 401:
        error_code_enum = ErrorCodes.AUTHENTICATION_FAILED
    elif exc.status_code == 403:
        error_code_enum = ErrorCodes.PERMISSION_DENIED
    else:
        error_code_enum = ErrorCodes.UNKNOWN_ERROR

    logger = logging.getLogger("backend.main")
    logger.warning(
        f"[FastAPI] {error_code_enum.name}: HTTP_ERROR: {exc.detail} (Status: {exc.status_code})",
        exc_info=True,
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(
            {
                "type": "about:blank",
                "title": "HTTP Error",
                "status": exc.status_code,
                "detail": exc.detail,
                "instance": str(request.url.path),
                "extensions": {"error_code": error_code_enum.value},
            }
        ),
        media_type="application/problem+json",
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches all unhandled exceptions and returns RFC 7807 Problem Details."""
    logger = logging.getLogger("backend.main")
    logger.error(f"[FastAPI] {ErrorCodes.INTERNAL_SERVER_ERROR.name}: Unhandled Exception: {exc}", exc_info=True)

    # Create a generic AppException for RFC 7807 formatting
    error = AppException(
        message="An unexpected system error occurred.",
        status_code=500,
        details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "original_error": str(exc)},
    )

    return JSONResponse(
        status_code=500,
        content=error.to_problem_detail(instance=str(request.url.path)),
        media_type="application/problem+json",
    )


# --- 5. Routers ---

# ...
from backend_v2.api.routers.execution import router as execution_router
from backend_v2.api.routers.iam import router as iam_router
from backend_v2.api.routers.output_profiles import router as output_profiles_router
from backend_v2.api.routers.studio import router as studio_router
from backend_v2.api.routers.system import router as system_router

app.include_router(iam_router, prefix="/api/v2")
app.include_router(system_router, prefix="/api/v2")
app.include_router(execution_router, prefix="/api/v2")
app.include_router(studio_router, prefix="/api/v2")
app.include_router(output_profiles_router, prefix="/api/v2")
