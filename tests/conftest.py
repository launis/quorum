"""Global Pytest Configuration."""

import os
import tempfile
from collections.abc import AsyncGenerator
from datetime import UTC

import pytest
from httpx import ASGITransport, AsyncClient

import backend.dependencies
from backend.main import app

# 1. FORCE ENV VARS BEFORE IMPORTS
os.environ["USE_MOCK_LLM"] = "true"
os.environ["USE_MOCK_DB"] = "true"  # Ensure we default to safe mock DB
os.environ["STORAGE_BACKEND"] = "LOCAL"
os.environ["TESTING"] = "true"

# 2. PATCH ARQ TO PREVENT FAKEREDIS CRASH
try:
    import arq.connections

    async def _no_op_log(*args, **kwargs):
        pass

    arq.connections.log_redis_info = _no_op_log

    import arq.worker

    arq.worker.log_redis_info = _no_op_log
except ImportError:
    pass


@pytest.fixture(scope="session", autouse=True)
def global_setup():
    """Global setup for all tests."""
    pass


@pytest.fixture
def anyio_backend():
    """Configure AnyIO backend to use asyncio."""
    return "asyncio"




from backend.dependencies import get_current_user_from_header  # noqa: E402


class MockAuthService:
    """Mock service for authentication overrides."""

    def __init__(self):
        """Initialize mock auth service."""
        self.current_user = None


@pytest.fixture
def mock_auth_service():
    """Fixture to provide access to the mock auth service instance."""
    return MockAuthService()


@pytest.fixture
async def client_authenticated(mock_auth_service) -> AsyncGenerator[AsyncClient]:
    """Async Client with Dynamic Auth overrides."""
    # Default to Root if not set
    if not mock_auth_service.current_user:
        from datetime import datetime

        from backend.models.auth import User, UserRole

        mock_auth_service.current_user = User(
            uid="root_master",
            email="root@example.com",
            role=UserRole.ROOT,
            organization_id="system",
            display_name="Root User",
            created_at=datetime.now(UTC).isoformat(),
        )

    app.dependency_overrides[get_current_user_from_header] = lambda: mock_auth_service.current_user

    # Override Database to use Temp File (Isolated Tests)

    # RESET GLOBALS to avoid stale DB references
    backend.dependencies._db_client_instance = None
    backend.dependencies._repository_instance = None
    backend.dependencies._auth_service_instance = None
    backend.dependencies._audit_service_instance = None
    backend.dependencies._engine_instance = None
    backend.dependencies._storage_service_instance = None

    fd, temp_db_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)

    from backend.settings import Settings

    def override_settings():
        return Settings(
            storage_backend="LOCAL",
            start_db_path=temp_db_path,
            use_mock_db=False,  # We use real TinyDB on temp file
            use_mock_llm=True,
            use_firebase=False,
        )

    from backend.database.wrapper import TinyDBClient
    from backend.dependencies import get_db_client_dep, get_settings_dep

    test_db = TinyDBClient(temp_db_path)

    # Align Global Helper for direct usage (e.g. in test fixtures)
    backend.dependencies._db_client_instance = test_db

    app.dependency_overrides[get_settings_dep] = override_settings
    app.dependency_overrides[get_db_client_dep] = lambda: test_db

    # SEED MOCK USER so repos can find it (e.g. for Creator checks)
    if mock_auth_service.current_user:
        from tinydb import Query

        UserQ = Query()
        # Ensure we dump properly (model_dump used in Pydantic v2)
        u_data = mock_auth_service.current_user.model_dump(mode="json")
        test_db.table("users").upsert(u_data, UserQ.uid == mock_auth_service.current_user.uid)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides = {}

    try:
        os.remove(temp_db_path)
    except Exception:
        pass

    # TEARDOWN RESET
    backend.dependencies._db_client_instance = None
    backend.dependencies._repository_instance = None
    backend.dependencies._auth_service_instance = None
    backend.dependencies._audit_service_instance = None
    backend.dependencies._engine_instance = None
    backend.dependencies._storage_service_instance = None


@pytest.fixture
async def client(client_authenticated) -> AsyncGenerator[AsyncClient]:
    """Alias for client_authenticated for compatibility with tests expecting 'client'."""
    yield client_authenticated


@pytest.fixture
def admin_token_headers():
    """Fixture providing valid admin authentication headers."""
    return {"Authorization": "Bearer mock_token"}
