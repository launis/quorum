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
from typing import Any, override

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

import backend_v2.hooks as _hooks

_ = _hooks
from backend_v2.api.routers.execution import (
    external_reports_router,
    reports_router,
)
from backend_v2.api.routers.execution import (
    router as execution_router,
)
from backend_v2.api.routers.iam import router as iam_router
from backend_v2.api.routers.output_profiles import router as output_profiles_router
from backend_v2.api.routers.studio import router as studio_router
from backend_v2.api.routers.system import router as system_router
from backend_v2.context import set_request_context
from backend_v2.core.rate_limit import rate_limit_exceeded_handler
from backend_v2.core.telemetry import configure_telemetry
from backend_v2.database.driver import StorageDriver
from backend_v2.database.factory import create_unit_of_work
from backend_v2.database.interfaces import QuorumUnitOfWork
from backend_v2.exceptions import AppException, ErrorCodes, format_validation_error
from backend_v2.logging_config import log_startup_system_parameters, setup_logging
from backend_v2.services.localization import set_language
from backend_v2.settings import get_settings
from backend_v2.utils.redis_patcher import get_patched_fakeredis_pool

__all__ = [
    "LocalizationMiddleware",
    "PathNormalizationMiddleware",
    "RequestIdMiddleware",
    "app",
    "app_exception_handler",
    "global_exception_handler",
    "http_exception_handler",
    "lifespan",
    "rate_limit_exception_handler",
    "validation_exception_handler",
]

# --- 1. Lifespan Management ---


async def _audit_storage_and_database_sync(
    driver: StorageDriver,
    logger: logging.Logger,
    storage_dir: Path | None = None,
) -> None:
    """Audits synchronization between executions in PostgreSQL 19 and execution artifacts on disk.

    Performs a strictly read-only check. Emits a structured warning with remediation instructions
    if orphaned database records or unindexed disk executions are discovered.

    Args:
        driver: Active StorageDriver for querying execution records.
        logger: Application logger for emitting audit telemetry.
        storage_dir: Optional override for the root execution artifacts directory
            (defaults to Path("data/files/executions")).
    """
    resolved_storage_dir = storage_dir if storage_dir is not None else Path("data/files/executions")
    db_records = await driver.query("executions")

    db_execution_ids: set[str] = set()
    orphaned_db_ids: list[str] = []

    for rec in db_records:
        if "id" not in rec or not rec["id"]:
            continue
        rec_id = str(rec["id"])
        db_execution_ids.add(rec_id)

        trace_path_raw = None
        if "execution_trace_storage_path" in rec and rec["execution_trace_storage_path"] is not None:
            trace_path_raw = str(rec["execution_trace_storage_path"])
        trace_exists = False
        if trace_path_raw and Path(trace_path_raw).exists():
            trace_exists = True
        elif trace_path_raw and (resolved_storage_dir.parent / trace_path_raw).exists():
            trace_exists = True
        elif (resolved_storage_dir / str(rec_id) / "execution_trace.json").exists():
            trace_exists = True

        if not trace_exists:
            orphaned_db_ids.append(str(rec_id))

    unindexed_disk_ids: list[str] = []
    if resolved_storage_dir.exists() and resolved_storage_dir.is_dir():
        for child in resolved_storage_dir.iterdir():
            if child.is_dir() and (child / "execution_trace.json").exists():
                disk_id = child.name
                if disk_id not in db_execution_ids:
                    unindexed_disk_ids.append(disk_id)

    if orphaned_db_ids or unindexed_disk_ids:
        logger.warning(
            f"[StorageAudit] WARNING: Storage/Database desync detected. "
            f"DB has {len(orphaned_db_ids)} orphaned records ({orphaned_db_ids}); "
            f"Disk has {len(unindexed_disk_ids)} unindexed runs ({unindexed_disk_ids}). "
            f"Run 'uv run python scripts/reconcile_storage.py --fix' to reconcile."
        )
    else:
        logger.info("[StorageAudit] Execution storage and database synchronization PASSED.")


async def _validate_database_preflight(
    logger: logging.Logger,
    uow: QuorumUnitOfWork | None = None,
) -> None:
    """Validates PostgreSQL 19 connectivity and core seed table counts at startup.

    Args:
        logger: Active application logger.
        uow: Optional QuorumUnitOfWork override for testing.

    Raises:
        RuntimeError: If PostgreSQL 19 is unreachable or core seed tables are empty.
    """
    if "PYTEST_CURRENT_TEST" in os.environ and uow is None:
        logger.info("[StartupAudit] Test environment detected; skipping live PostgreSQL pre-flight check.")
        return

    settings = get_settings()
    resolved_uow = uow if uow is not None else create_unit_of_work(settings)
    try:
        async with resolved_uow as active_uow:
            await active_uow.entities.verify_seed_table_counts(
                {
                    "system_configs": 1,
                    "workflows": 1,
                    "prompt_blocks": 1,
                    "steps": 1,
                    "output_profiles": 1,
                }
            )
        logger.info("[StartupAudit] Pre-flight PostgreSQL 19 database validation PASSED.")
    except Exception as exc:
        logger.critical(
            "[StartupAudit] PostgreSQL 19 pre-flight validation FAILED: %s. "
            "Please seed via 'uv run python backend_v2/seed/run_seed.py'.",
            exc,
            exc_info=True,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )
        raise RuntimeError(
            f"Pre-flight PostgreSQL 19 validation failed: {exc}. "
            "Please run 'uv run python backend_v2/seed/run_seed.py' to populate clean database state."
        ) from exc


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manages application startup and shutdown lifecycle.

    Args:
        app: The current FastAPI application context.

    Yields:
        Proceeds with the yield flow while application runs.

    Raises:
        Exception: Propagates initialization failures to the application host.
    """
    setup_logging()
    settings = get_settings()
    configure_telemetry(settings, app=app)
    logger = logging.getLogger("backend.main")
    log_startup_system_parameters(logger, "FASTAPI API SERVER")

    app.state.arq_pool = None

    try:
        workflow_dir = Path("data/workflows")
        if workflow_dir.exists() and workflow_dir.is_dir():
            files = [f.name for f in workflow_dir.iterdir() if f.name.endswith(".json")]
            logger.info(f"[StartupAudit] Workflows Detected: {len(files)} files in {workflow_dir.as_posix()}.")

        await _validate_database_preflight(logger)

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
        pool = app.state.arq_pool
        if pool is not None and isinstance(pool, (ArqRedis, FakeRedis)):
            await pool.aclose()


# --- 2. Application Setup ---

app = FastAPI(
    title="Cognitive Quorum API",
    version="2.9.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- 3. Middleware ---

cors_origins = get_settings().cors_origins
if not cors_origins:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to inject Request ID into context."""

    @override
    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        """Process the request and assign secure request trace IDs.

        Args:
            request: The current incoming FastAPI Request.
            call_next: Next request processing middleware function in line.

        Returns:
            The completed downstream execution response.
        """
        raw_request_id = request.headers.get("X-Request-ID")
        request_id = raw_request_id if raw_request_id else secrets.token_hex(16)
        set_request_context(request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class LocalizationMiddleware(BaseHTTPMiddleware):
    """Middleware to inject Accept-Language into context."""

    @override
    async def dispatch(self, request: Request, call_next: Callable[[Request], Any]) -> Any:
        """Process the request and determine client localization.

        Args:
            request: The current incoming FastAPI Request.
            call_next: Next request processing middleware function in line.

        Returns:
            The completed downstream execution response.
        """
        accept_language = request.headers.get("Accept-Language", "en")
        preferred_lang = accept_language.split(",")[0].split(";")[0].strip()
        set_language(preferred_lang)
        response = await call_next(request)
        return response


class PathNormalizationMiddleware:
    """Normalizes redundant slashes in ASGI URL scope to prevent Starlette 404 routing mismatches."""

    def __init__(self, app_instance: Any) -> None:
        """Initialize path normalization middleware.

        Args:
            app_instance: ASGI application instance.
        """
        self.app_instance = app_instance

    async def __call__(self, scope: Any, receive: Any, send: Any) -> Any:
        """Intercepts and normalizes ASGI HTTP paths by collapsing double slashes.

        Args:
            scope: ASGI connection scope mapping.
            receive: ASGI receive awaitable channel.
            send: ASGI send awaitable channel.

        Returns:
            None after delegating to the downstream ASGI application.
        """
        if "type" in scope and scope["type"] == "http":
            if "path" in scope and "//" in scope["path"]:
                path: str = scope["path"]
                while "//" in path:
                    path = path.replace("//", "/")
                scope["path"] = path
        await self.app_instance(scope, receive, send)


app.add_middleware(PathNormalizationMiddleware)
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
        Standardized RFC 7807 JSON response.
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
        content=exc.to_problem_detail(instance=str(request.url.path)).model_dump(mode="json", exclude_none=True),
        media_type="application/problem+json",
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Catches Pydantic validation errors and returns RFC 7807 Problem Details.

    Args:
        request: The current HTTP Request boundary context.
        exc: Pydantic internal structure failure trace.

    Returns:
        Standardized RFC 7807 JSON response mapping schema issues.
    """
    logger = logging.getLogger("backend.main")
    readable_detail = format_validation_error(exc)
    error_code = ErrorCodes.VALIDATION_FAILED
    logger.warning("[FastAPI] VALIDATION ERROR: %s", readable_detail, extra={"error_code": error_code.value})
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
        Delegated JSON response indicating client rate lockout.
    """
    return rate_limit_exceeded_handler(request, exc)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Catches standard starlette exceptions to preserve JSON API structure.

    Args:
        request: The current HTTP Request boundary context.
        exc: Core HTTP standard exception model.

    Returns:
        Standardized RFC 7807 JSON response.
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
        Standardized RFC 7807 JSON response mapping a 500 error.
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
        content=error.to_problem_detail(instance=str(request.url.path)).model_dump(mode="json", exclude_none=True),
        media_type="application/problem+json",
    )


# --- 5. Routers ---

app.include_router(iam_router, prefix="/api/v2")
app.include_router(system_router, prefix="/api/v2")
app.include_router(execution_router, prefix="/api/v2")
app.include_router(reports_router, prefix="/api/v2")
app.include_router(external_reports_router, prefix="/api/v1")
app.include_router(external_reports_router, prefix="/api/v2")
app.include_router(studio_router, prefix="/api/v2")
app.include_router(output_profiles_router, prefix="/api/v2")
