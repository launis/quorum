"""Unit tests for backend_v2/main.py covering lifespan, pre-flight checks, middlewares, and exception handlers."""

import logging
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import BaseModel
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


def test_validate_database_preflight_missing_file() -> None:
    """Test that pre-flight check logs a warning and returns if DB file does not exist."""
    logger = logging.getLogger("test.main")
    with patch("pathlib.Path.exists", return_value=False):
        _validate_database_preflight(logger)


def test_validate_database_preflight_success() -> None:
    """Test that pre-flight check passes with valid database records."""
    logger = logging.getLogger("test.main")
    mock_db = MagicMock()
    mock_table = MagicMock()
    mock_table.all.return_value = []
    mock_db.table.return_value = mock_table

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("tinydb.TinyDB", return_value=mock_db),
    ):
        _validate_database_preflight(logger)
        mock_db.close.assert_called_once()


def test_validate_database_preflight_corrupted_raises_runtime_error() -> None:
    """Test that pre-flight check cleanly aborts with instructions to re-seed on invalid DB schema."""
    logger = logging.getLogger("test.main")
    mock_db = MagicMock()
    mock_table = MagicMock()
    mock_table.all.return_value = [{"invalid_key": "unsupported_data"}]
    mock_db.table.return_value = mock_table

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("tinydb.TinyDB", return_value=mock_db),
        pytest.raises(RuntimeError) as excinfo,
    ):
        _validate_database_preflight(logger)

    assert "run_seed.py local" in str(excinfo.value)


@pytest.mark.asyncio
async def test_lifespan_test_environment() -> None:
    """Test lifespan startup and shutdown in test environment."""
    test_app = FastAPI()
    with patch("backend_v2.main._validate_database_preflight"):
        async with lifespan(test_app):
            assert hasattr(test_app.state, "arq_pool")


@pytest.mark.asyncio
async def test_lifespan_production_redis_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test lifespan startup fails-fast when Redis connection fails in production mode."""
    import backend_v2.main as b_main

    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setattr(b_main, "create_pool", AsyncMock(side_effect=ConnectionError("Redis down")))
    monkeypatch.setattr(b_main, "setup_logging", MagicMock())
    monkeypatch.setattr(b_main, "configure_logfire", MagicMock())
    monkeypatch.setattr(b_main, "_validate_database_preflight", MagicMock())
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

    try:
        SampleModel.model_validate({"name": 123}, strict=True)
    except Exception:
        validation_exc = RequestValidationError(
            errors=[{"loc": ("body", "name"), "msg": "str type expected", "type": "string_type"}]
        )

    response = await validation_exception_handler(mock_request, validation_exc)
    assert response.status_code == 422


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
    """Test that lifespan shutdown invokes aclose on the arq pool."""
    test_app = FastAPI()
    mock_pool = AsyncMock()
    with patch("backend_v2.main._validate_database_preflight"):
        async with lifespan(test_app):
            test_app.state.arq_pool = mock_pool
    mock_pool.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_rate_limit_exception_handler_delegation() -> None:
    """Test rate limit exception handler delegates properly."""
    from slowapi.errors import RateLimitExceeded

    from backend_v2.main import rate_limit_exception_handler

    mock_request = MagicMock(spec=Request)
    mock_request.url.path = "/api/v2/limited"
    mock_request.scope = {"type": "http", "path": "/api/v2/limited"}
    mock_exc = MagicMock(spec=RateLimitExceeded)
    mock_exc.detail = "Rate limit exceeded: 5 per minute"

    with patch("backend_v2.main.rate_limit_exceeded_handler", return_value=MagicMock(status_code=429)) as mock_handler:
        res = await rate_limit_exception_handler(mock_request, mock_exc)
        mock_handler.assert_called_once_with(mock_request, mock_exc)
        assert res.status_code == 429
