"""Unit tests for backend_v2/main.py covering lifespan, pre-flight checks, middlewares, and exception handlers."""

import logging
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import BaseModel, JsonValue, ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.main import (
    LocalizationMiddleware,
    RequestIdMiddleware,
    _validate_database_preflight,
    app,
    app_exception_handler,
    global_exception_handler,
    http_exception_handler,
    lifespan,
    validation_exception_handler,
)
from backend_v2.tests.fakes.in_memory_uow import InMemoryUnitOfWork

client = TestClient(app)


def test_docs_endpoint() -> None:
    """Test that the OpenAPI docs endpoint is accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text


def test_openapi_schema() -> None:
    """Test that the OpenAPI schema is available."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "Cognitive Quorum API"


@pytest.mark.asyncio
async def test_validate_database_preflight_skips_in_pytest_when_uow_not_passed() -> None:
    """Test that pre-flight check skips live check in pytest when uow is None."""
    logger = MagicMock(spec=logging.Logger)
    await _validate_database_preflight(logger)
    logger.info.assert_called_once()
    assert "skipping" in logger.info.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_validate_database_preflight_success() -> None:
    """Test that pre-flight check passes when core PostgreSQL seed tables are populated."""
    logger = MagicMock(spec=logging.Logger)
    uow = InMemoryUnitOfWork()
    for table in (
        "model_registries",
        "mcp_gateways",
        "workflows",
        "prompt_blocks",
        "task_briefs",
        "steps",
        "output_profiles",
    ):
        uow.store.seed_tables[table][f"{table[:3]}_1234567890abcdef"] = (f"{table[:3]}_1234567890abcdef",)

    await _validate_database_preflight(logger, uow=uow)
    logger.info.assert_called_once()
    assert "PASSED" in logger.info.call_args[0][0]


@pytest.mark.asyncio
async def test_validate_database_preflight_empty_table_raises_runtime_error() -> None:
    """Test that pre-flight check cleanly aborts with instructions to re-seed when a seed table is empty."""
    logger = logging.getLogger("test.main")
    uow = InMemoryUnitOfWork()

    with pytest.raises(RuntimeError) as excinfo:
        await _validate_database_preflight(logger, uow=uow)

    assert "run_seed.py" in str(excinfo.value)


@pytest.mark.asyncio
async def test_lifespan_test_environment() -> None:
    """Test lifespan startup and shutdown in test environment."""
    from backend_v2.database.postgres.pool import PostgresPoolManager

    test_app = FastAPI()
    with patch("backend_v2.main._validate_database_preflight", new_callable=AsyncMock):
        async with lifespan(test_app):
            assert test_app.state.arq_pool is not None
            assert isinstance(test_app.state.pool_manager, PostgresPoolManager)


@pytest.mark.asyncio
async def test_lifespan_shutdown_drains_shared_pool_manager() -> None:
    """Test lifespan shutdown calls close_shared_pool_manager in finally block."""
    from backend_v2.tests.fakes.in_memory_uow import InMemoryAsyncPgPool

    test_app = FastAPI()
    fake_pool = InMemoryAsyncPgPool()
    with patch("backend_v2.main._validate_database_preflight", new_callable=AsyncMock):
        async with lifespan(test_app):
            test_app.state.pool_manager._pool = fake_pool
            assert test_app.state.pool_manager.is_initialized is True
    assert fake_pool.closed is True


@pytest.mark.asyncio
async def test_lifespan_production_redis_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test lifespan startup fails-fast when Redis connection fails in production mode."""
    import backend_v2.main as b_main

    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(b_main, "create_pool", AsyncMock(side_effect=ConnectionError("Redis down")))
    monkeypatch.setattr(b_main, "setup_logging", MagicMock())
    monkeypatch.setattr(b_main, "configure_telemetry", MagicMock())
    monkeypatch.setattr(b_main, "_validate_database_preflight", AsyncMock())
    test_app = FastAPI()
    with pytest.raises(ConnectionError):
        async with b_main.lifespan(test_app):
            pass


@pytest.mark.asyncio
async def test_request_id_middleware() -> None:
    """Test RequestIdMiddleware sets X-Request-ID header."""
    middleware = RequestIdMiddleware(app=FastAPI())
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {}
    mock_response = MagicMock()
    mock_response.headers = {}

    async def mock_call_next(req: Request) -> Any:
        return mock_response

    result = await middleware.dispatch(mock_request, mock_call_next)
    assert "X-Request-ID" in result.headers


@pytest.mark.asyncio
async def test_localization_middleware() -> None:
    """Test LocalizationMiddleware parses Accept-Language header."""
    middleware = LocalizationMiddleware(app=FastAPI())
    mock_request = MagicMock(spec=Request)
    mock_request.headers = {"Accept-Language": "fi-FI,fi;q=0.9,en;q=0.8"}
    mock_response = MagicMock()

    async def mock_call_next(req: Request) -> Any:
        return mock_response

    result = await middleware.dispatch(mock_request, mock_call_next)
    assert result == mock_response


@pytest.mark.asyncio
async def test_app_exception_handler_400() -> None:
    """Test AppException handler with 4xx client errors."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v2/test"
    exc = AppException(
        message="Invalid input",
        status_code=400,
        details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
    )
    response = await app_exception_handler(mock_request, exc)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_app_exception_handler_500() -> None:
    """Test AppException handler with 5xx server errors."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v2/test"
    exc = AppException(
        message="Internal failure",
        status_code=500,
        details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
    )
    response = await app_exception_handler(mock_request, exc)
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_validation_exception_handler() -> None:
    """Test validation exception handler converts Pydantic errors to RFC 7807 problem details."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v2/test"

    class SampleModel(BaseModel):
        name: str

    with pytest.raises(ValidationError) as exc_info:
        SampleModel.model_validate({"name": 123}, strict=True)
    validation_exc = RequestValidationError(errors=exc_info.value.errors())

    response = await validation_exception_handler(mock_request, validation_exc)
    assert response.status_code == 422
    import json

    payload = json.loads(bytes(response.body).decode("utf-8"))
    assert payload["type"] == "https://api.qrum.ai/errors/validation-failed"
    assert "//" not in payload["type"].removeprefix("https://")


@pytest.mark.asyncio
async def test_http_exception_handler_status_codes() -> None:
    """Test StarletteHTTPException handler for 404, 401, and 403."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v2/notfound"

    for status_code in (404, 401, 403, 503):
        exc = StarletteHTTPException(status_code=status_code, detail="Test message")
        response = await http_exception_handler(mock_request, exc)
        assert response.status_code == status_code


@pytest.mark.asyncio
async def test_global_exception_handler() -> None:
    """Test global exception handler catches unhandled exceptions and returns 500."""
    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v2/error"
    exc = ValueError("Unexpected division by zero")
    response = await global_exception_handler(mock_request, exc)
    assert response.status_code == 500


@pytest.mark.asyncio
async def test_lifespan_shutdown_closes_arq_pool() -> None:
    """Test that lifespan shutdown invokes aclose on the arq pool and resets state to None."""
    from arq.connections import ArqRedis

    from backend_v2.main import app as main_app
    from backend_v2.settings import get_settings

    assert main_app.version == get_settings().app_version

    test_app = FastAPI()
    mock_pool = AsyncMock(spec=ArqRedis)
    with patch("backend_v2.main._validate_database_preflight", new_callable=AsyncMock):
        async with lifespan(test_app):
            test_app.state.arq_pool = mock_pool
            assert test_app.state.pool_manager is not None
    mock_pool.aclose.assert_awaited_once()
    assert test_app.state.arq_pool is None
    assert test_app.state.pool_manager is None


@pytest.mark.asyncio
async def test_app_exception_handler_429_rate_limit_exceeded() -> None:
    """Test app_exception_handler formats HTTP 429 TokenLimitExceededError as RFC 7807 problem+json."""
    from backend_v2.exceptions import ProblemDetailDTO, TokenLimitExceededError

    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v2/iam/auth/exchange"
    exc = TokenLimitExceededError(
        message="Auth edge rate limit exceeded for scope 'POST /api/v2/iam/auth/exchange' (11/10).",
        details={
            "error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value,
            "limit_type": "auth_edge_rpm",
            "current": 11,
            "limit": 10,
        },
    )
    exc.status_code = 429

    res = await app_exception_handler(mock_request, exc)
    assert res.status_code == 429
    assert res.media_type == "application/problem+json"

    problem = ProblemDetailDTO.model_validate_json(bytes(res.body))
    assert problem.status == 429
    assert problem.instance == "/api/v2/iam/auth/exchange"
    assert problem.extensions is not None
    assert problem.extensions["error_code"] == ErrorCodes.RATE_LIMIT_EXCEEDED.value
    assert problem.extensions["limit_type"] == "auth_edge_rpm"

    # Negative boundary: ProblemDetailDTO rejects unrecognized top-level keys (extra='forbid')
    with pytest.raises(ValidationError):
        ProblemDetailDTO.model_validate_json(
            b'{"type":"about:blank","title":"Too Many Requests","status":429,"detail":"err","instance":"/x","unexpected":1}'
        )


@pytest.mark.asyncio
async def test_path_normalization_middleware_collapses_double_slashes() -> None:
    """Test PathNormalizationMiddleware collapses redundant slashes in HTTP paths."""
    from backend_v2.main import PathNormalizationMiddleware

    called_scope: dict[str, JsonValue] = {}

    async def mock_app(scope: Any, receive: Any, send: Any) -> None:
        called_scope.update(scope)

    middleware = PathNormalizationMiddleware(mock_app)
    scope = {"type": "http", "path": "/api/v2//reports/rep_123///pdf"}

    async def mock_receive() -> None:
        pass

    async def mock_send(message: Any) -> None:
        pass

    await middleware(scope, mock_receive, mock_send)
    assert scope["path"] == "/api/v2/reports/rep_123/pdf"
    assert called_scope["path"] == "/api/v2/reports/rep_123/pdf"


@pytest.mark.asyncio
async def test_path_normalization_middleware_ignores_non_http() -> None:
    """Test PathNormalizationMiddleware ignores non-http scopes."""
    from backend_v2.main import PathNormalizationMiddleware

    called = False

    async def mock_app(scope: Any, receive: Any, send: Any) -> None:
        nonlocal called
        called = True

    middleware = PathNormalizationMiddleware(mock_app)
    scope = {"type": "websocket", "path": "//ws"}

    async def mock_receive() -> None:
        pass

    async def mock_send(message: Any) -> None:
        pass

    await middleware(scope, mock_receive, mock_send)
    assert called is True
    assert scope["path"] == "//ws"


@pytest.mark.asyncio
async def test_lifespan_production_redis_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test lifespan startup connects to Arq Redis pool and closes on shutdown in production mode."""
    from arq.connections import ArqRedis

    import backend_v2.main as b_main

    mock_pool = AsyncMock(spec=ArqRedis)
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(b_main, "create_pool", AsyncMock(return_value=mock_pool))
    monkeypatch.setattr(b_main, "setup_logging", MagicMock())
    monkeypatch.setattr(b_main, "configure_telemetry", MagicMock())
    monkeypatch.setattr(b_main, "_validate_database_preflight", AsyncMock())
    test_app = FastAPI()
    async with b_main.lifespan(test_app):
        assert test_app.state.arq_pool is mock_pool
    mock_pool.aclose.assert_awaited_once()
