"""Main entrypoint for the Cognitive Quorum Backend API.

Adheres to V2.9 Architecture:
- Lifespan State Management
- One Truth Error Protocol
- V2 Execution Router
- Task Registry Initialization
"""

import logging
import os
import secrets
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

try:
    import logfire

    _logfire: Any = logfire
except ImportError:
    _logfire = None

from arq.connections import ArqRedis, RedisSettings, create_pool
from fakeredis.aioredis import FakeRedis
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

import backend_v2.hooks  # noqa: F401
from backend_v2.api.routers.execution import router as execution_router
from backend_v2.api.routers.iam import router as iam_router
from backend_v2.api.routers.output_profiles import router as output_profiles_router
from backend_v2.api.routers.studio import router as studio_router
from backend_v2.api.routers.system import router as system_router
from backend_v2.context import set_request_context
from backend_v2.core.rate_limit import rate_limit_exceeded_handler
from backend_v2.exceptions import AppException, ErrorCodes, format_validation_error
from backend_v2.logging_config import configure_logfire, setup_logging
from backend_v2.seed.seed_registry import STANDARD_REGISTRY
from backend_v2.services.localization import set_language
from backend_v2.settings import get_settings
from backend_v2.utils.redis_patcher import get_patched_fakeredis_pool

# --- 1. Lifespan Management ---


def _validate_database_preflight(logger: logging.Logger) -> None:
    """Validates root database collections against strict Pydantic models at startup.

    Args:
        logger: Active application logger.

    Raises:
        RuntimeError: If database records fail strict Pydantic validation.
    """
    settings = get_settings()
    db_path = Path(settings.prod_db_path)
    if not db_path.exists():
        logger.warning(
            "[StartupAudit] Database file '%s' not found. Re-seed via 'uv run python backend_v2/seed/run_seed.py local'.",
            db_path,
        )
        return

    try:
        from tinydb import TinyDB

        db = TinyDB(str(db_path), encoding="utf-8")
        collections_to_validate = ["system_config", "workflows", "output_profiles"]
        for col_name in collections_to_validate:
            if col_name in STANDARD_REGISTRY:
                config = STANDARD_REGISTRY[col_name]
                table_name = str(config["table"])
                adapter: Any = config["model"]
                table = db.table(table_name)
                for item in table.all():
                    adapter.validate_python(item)
        db.close()
        logger.info("[StartupAudit] Pre-flight database schema validation PASSED.")
    except Exception as exc:
        logger.critical(
            "[StartupAudit] Database schema validation FAILED for %s: %s. Please re-seed via 'uv run python backend_v2/seed/run_seed.py local'.",
            db_path,
            exc,
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
        raise RuntimeError(
            f"Pre-flight schema validation failed on '{db_path}': {exc}. "
            "Please run 'uv run python backend_v2/seed/run_seed.py local' to rebuild clean database state."
        ) from exc


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manages application startup and shutdown lifecycle.

    Args:
        app: The current FastAPI application context.

    Yields:
        None: Proceeds with the yield flow while application runs.

    Raises:
        Exception: Propagates initialization failures to the application host.
    """
    setup_logging()
    configure_logfire()
    logger = logging.getLogger("backend.main")

    logger.info("======================================================================")
    logger.info("   COGNITIVE QUORUM BACKEND (V2.9) - STARTING UP")
    logger.info("======================================================================")

    try:
        workflow_dir = "data/workflows"
        if os.path.exists(workflow_dir):
            files = [f for f in os.listdir(workflow_dir) if f.endswith(".json")]
            logger.info(f"[StartupAudit] Workflows Detected: {len(files)} files in {workflow_dir}.")

        _validate_database_preflight(logger)

        if "PYTEST_CURRENT_TEST" in os.environ:
            logger.info("Test environment detected. Forcing FakeRedis.")
            app.state.arq_pool = get_patched_fakeredis_pool()
        else:
            try:
                settings_ctx = get_settings()
                app.state.arq_pool = await create_pool(
                    RedisSettings(host=settings_ctx.redis_host, port=settings_ctx.redis_port)
                )
                logger.info(f"Connected to Arq Redis at {settings_ctx.redis_host}:{settings_ctx.redis_port}")
            except Exception as redis_err:
                logger.critical(f"Failed to connect to real Redis: {redis_err}. Crashing system (Fail-Fast).")
                raise

        yield

    except Exception as e:
        logger.critical(
            "Startup failed: %s", str(e), exc_info=True, extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
        )
        raise

    finally:
        logger.info("Shutting down...")
        try:
            pool = app.state.arq_pool
        except AttributeError:
            pool = None

        if pool is not None:
            try:
                if isinstance(pool, (ArqRedis, FakeRedis)):
                    await pool.aclose()
            except (OSError, RuntimeError) as close_err:
                logger.error(
                    "Error closing Arq pool: %s",
                    str(close_err),
                    extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
                )


# --- 2. Application Setup ---

app = FastAPI(
    title="Cognitive Quorum API",
    version="2.9.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

if _logfire:
    try:
        _logfire.instrument_fastapi(app)
    except Exception as logfire_err:
        logging.getLogger("backend.main").error("Failed to instrument FastAPI with Logfire.", exc_info=True)
        raise logfire_err
else:
    logging.getLogger("backend.main").info("Logfire not installed. Skipping FastAPI telemetry instrumentation.")

# --- 3. Middleware ---

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to inject Request ID into context."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        """Process the request and assign secure request trace IDs.

        Args:
            request: The current incoming FastAPI Request.
            call_next: Next request processing middleware function in line.

        Returns:
            Any: The completed downstream execution response.
        """
        request_id = request.headers.get("X-Request-ID") or secrets.token_hex(16)
        set_request_context(request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class LocalizationMiddleware(BaseHTTPMiddleware):
    """Middleware to inject Accept-Language into context."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        """Process the request and determine client localization.

        Args:
            request: The current incoming FastAPI Request.
            call_next: Next request processing middleware function in line.

        Returns:
            Any: The completed downstream execution response.
        """
        accept_language = request.headers.get("Accept-Language", "en")
        preferred_lang = accept_language.split(",")[0].split(";")[0].strip()
        set_language(preferred_lang)
        response = await call_next(request)
        return response


app.add_middleware(RequestIdMiddleware)
app.add_middleware(LocalizationMiddleware)


# --- 4. Global Error Handlers (RFC 7807 Problem Details) ---


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Catches domain-specific AppExceptions and returns RFC 7807 Problem Details.

    Args:
        request: The current HTTP Request boundary context.
        exc: The raised domain model exception to catch.

    Returns:
        JSONResponse: Standardized RFC 7807 JSON response.
    """
    logger = logging.getLogger("backend.main")
    err_name = str(exc.error_code)

    if exc.status_code >= 500:
        logger.error(
            "[FastAPI] %s (Status: %s)",
            exc.message,
            exc.status_code,
            exc_info=exc,
            extra={"error_code": err_name},
        )
    else:
        logger.warning("[FastAPI] %s (Status: %s)", exc.message, exc.status_code, extra={"error_code": err_name})
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_problem_detail(instance=str(request.url.path)),
        media_type="application/problem+json",
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Catches Pydantic validation errors and returns RFC 7807 Problem Details.

    Args:
        request: The current HTTP Request boundary context.
        exc: Pydantic internal structure failure trace.

    Returns:
        JSONResponse: Standardized RFC 7807 JSON response mapping schema issues.
    """
    logger = logging.getLogger("backend.main")
    readable_detail = format_validation_error(exc)
    error_code = ErrorCodes.VALIDATION_FAILED
    logger.error("[FastAPI] VALIDATION ERROR: %s", readable_detail, extra={"error_code": error_code.value})
    logger.debug("[FastAPI] Raw Schema Errors: %s", exc.errors(), extra={"error_code": error_code.value})

    return JSONResponse(
        status_code=422,
        content=jsonable_encoder(
            {
                "type": "https://api.quorum.fi/errors/validation-failed",
                "title": "Validation Failed",
                "status": 422,
                "detail": readable_detail,
                "instance": str(request.url.path),
                "extensions": {
                    "error_code": error_code.value,
                    "errors": exc.errors(),
                },
            }
        ),
        media_type="application/problem+json",
    )


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exception_handler(request: Request, exc: RateLimitExceeded) -> Any:
    """Catches RateLimitExceeded and delegates to the strict handler.

    Args:
        request: The current HTTP Request boundary context.
        exc: SlowAPI threshold rate restriction.

    Returns:
        Any: Delegated JSON response indicating client rate lockout.
    """
    return rate_limit_exceeded_handler(request, exc)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Catches standard starlette exceptions to preserve JSON API structure.

    Args:
        request: The current HTTP Request boundary context.
        exc: Core HTTP standard exception model.

    Returns:
        JSONResponse: Standardized RFC 7807 JSON response.
    """
    error_code_enum = ErrorCodes.UNKNOWN_ERROR
    if exc.status_code == 404:
        error_code_enum = ErrorCodes.RESOURCE_NOT_FOUND
    elif exc.status_code == 401:
        error_code_enum = ErrorCodes.AUTHENTICATION_FAILED
    elif exc.status_code == 403:
        error_code_enum = ErrorCodes.PERMISSION_DENIED

    logger = logging.getLogger("backend.main")
    logger.warning(
        "[FastAPI] HTTP_ERROR: %s (Status: %s)",
        exc.detail,
        exc.status_code,
        exc_info=True,
        extra={"error_code": error_code_enum.value},
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
                "extensions": {
                    "error_code": error_code_enum.value,
                },
            }
        ),
        media_type="application/problem+json",
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches all unhandled exceptions and returns RFC 7807 Problem Details.

    Args:
        request: The current HTTP Request boundary context.
        exc: Caught arbitrary exception thrown downstream.

    Returns:
        JSONResponse: Standardized RFC 7807 JSON response mapping a 500 error.
    """
    logger = logging.getLogger("backend.main")
    logger.error(
        "[FastAPI] Unhandled Exception: %s",
        str(exc),
        exc_info=True,
        extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
    )

    error = AppException(
        message="An unexpected system error occurred.",
        status_code=500,
        details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
    )

    return JSONResponse(
        status_code=500,
        content=error.to_problem_detail(instance=str(request.url.path)),
        media_type="application/problem+json",
    )


# --- 5. Routers ---

app.include_router(iam_router, prefix="/api/v2")
app.include_router(system_router, prefix="/api/v2")
app.include_router(execution_router, prefix="/api/v2")
app.include_router(studio_router, prefix="/api/v2")
app.include_router(output_profiles_router, prefix="/api/v2")
