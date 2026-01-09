import os

import pytest

# 1. FORCE ENV VARS BEFORE IMPORTS
os.environ["USE_MOCK_LLM"] = "true"
os.environ["USE_MOCK_DB"] = "true"  # Ensure we default to safe mock DB
os.environ["STORAGE_BACKEND"] = "LOCAL"
os.environ["TESTING"] = "true"

# 2. PATCH ARQ TO PREVENT FAKEREDIS CRASH
# Fakeredis + Arq = Crash on startup because Arq tries to run 'INFO' command
# inside a pipeline and parse it manually, which Fakeredis fails on.
try:
    import arq.connections

    async def _no_op_log(*args, **kwargs):
        pass

    arq.connections.log_redis_info = _no_op_log

    # Also patch the imported reference in worker.py!
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
    return "asyncio"


from httpx import ASGITransport, AsyncClient

from backend.dependencies import get_current_user_from_header
from backend.main import app
from backend.models.auth import User, UserRole


@pytest.fixture
async def client():
    """Async Client with Auth overrides."""
    # Override Auth to return ROOT user always
    from datetime import datetime

    root_user = User(
        uid="root_master",
        email="root@example.com",
        role=UserRole.ROOT,
        organization_id="system",
        display_name="Root User",
        created_at=datetime.utcnow().isoformat(),
    )

    app.dependency_overrides[get_current_user_from_header] = lambda: root_user

    # Override Database to use Temp File (Isolated Tests)
    import os
    import tempfile

    # Create temp DB file
    fd, temp_db_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)

    # Initialize with schema if needed, or rely on code to create tables.
    # We need to make sure 'settings' says we are using LOCAL storage.
    from backend.settings import Settings

    def override_settings():
        return Settings(
            storage_backend="LOCAL",
            start_db_path=temp_db_path,
            use_mock_db=False,
            use_mock_llm=True,  # Use Mock LLM for speed/safety
        )

    # Reset singleton to ensure fresh init if it was already created (though dependencies usually create new if function called, but we have global singleton in dependencies.py)
    # We can't easily reset the global variable in dependencies.py from here without accessing it.
    # But overriding the dependency avoids calling the original function.
    # We construct a fresh DB client
    from backend.database.wrapper import TinyDBClient
    from backend.dependencies import get_db_client_dep, get_settings_dep

    test_db = TinyDBClient(temp_db_path)

    app.dependency_overrides[get_settings_dep] = override_settings
    app.dependency_overrides[get_db_client_dep] = lambda: test_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c

    app.dependency_overrides = {}

    # Cleanup
    try:
        os.remove(temp_db_path)
    except:
        pass


@pytest.fixture
def admin_token_headers():
    """Mock headers (Auth is overridden, so this is dummy)."""
    return {"Authorization": "Bearer mock_token"}
