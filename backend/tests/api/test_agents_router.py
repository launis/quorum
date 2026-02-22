from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_user_root():
    """Returns headers mimicking a Root user."""
    # Assuming auth middleware reads these or we mock the dependency override
    return {"Authorization": "Bearer mock-root-token"}


from unittest.mock import patch

from backend.dependencies import get_agent_registry_dep


@pytest.mark.asyncio
async def test_run_agent_not_found(async_client: AsyncClient, mock_user_root):
    """Verify that requesting an unknown agent returns 404."""
    # Mock Registry using Dependency Override
    mock_registry = MagicMock()
    mock_registry.resolve_model_name = AsyncMock(return_value="mock-resolved-model")

    app.dependency_overrides[get_agent_registry_dep] = lambda: mock_registry

    try:
        # We mock _load_agent_class to raise ValueError as it would in production
        # Note: _load_agent_class is a local function in agents_router, so we patch it there.
        # But for "UnknownAgent", the real function would check DB and fail.
        # Since we use a real DB dependency (or might not be mocked), we might need to patch it too.
        # Actually, let's patch _load_agent_class to be sure we control the 404.
        with patch("backend.api.agents_router._load_agent_class", side_effect=ValueError("Unknown agent")):
            response = await async_client.post(
                "/agents/UnknownAgent/run", json={"inputs": {"text": "hello"}, "model": "fast"}, headers=mock_user_root
            )

        # The router catches ValueError from _load_agent_class and raises ResourceNotFoundError (404)
        assert response.status_code == 404
        data = response.json()
        # RFC 7807: "type" contains the error code as a slug
        assert data["title"] == "Agent Not Found"
        assert data["type"].endswith("/agent-not-found")
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_run_agent_success(async_client: AsyncClient, mock_user_root):
    """Verify that agent execution returns strict DTO."""
    mock_agent_instance = MagicMock()
    mock_agent_instance.execute = AsyncMock(return_value={"output": "success"})
    mock_agent_class = MagicMock(return_value=mock_agent_instance)

    mock_registry = MagicMock()
    mock_registry.resolve_model_name = AsyncMock(return_value="mock-resolved-model")
    app.dependency_overrides[get_agent_registry_dep] = lambda: mock_registry

    try:
        with patch("backend.api.agents_router._load_agent_class", return_value=mock_agent_class):
            response = await async_client.post(
                "/agents/TestAgent/run",
                json={"inputs": {"text": "hello"}, "model": "fast"},  # Valid model provided
                headers=mock_user_root,
            )

            assert response.status_code == 200
            data = response.json()
            assert "agent" in data
            assert "result" in data
            assert data["agent"] == "TestAgent"
            assert data["result"] == {"output": "success"}
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_run_agent_validation_error(async_client: AsyncClient, mock_user_root):
    """Verify that validation errors return 400 (Fail Fast)."""
    mock_agent_instance = MagicMock()
    # ValueError during execution -> 400
    mock_agent_instance.execute = AsyncMock(side_effect=ValueError("Invalid Input"))
    mock_agent_class = MagicMock(return_value=mock_agent_instance)

    mock_registry = MagicMock()
    mock_registry.resolve_model_name = AsyncMock(return_value="mock-resolved-model")
    app.dependency_overrides[get_agent_registry_dep] = lambda: mock_registry

    try:
        with patch("backend.api.agents_router._load_agent_class", return_value=mock_agent_class):
            # Must provide model to pass initial checks
            response = await async_client.post(
                "/agents/TestAgent/run", json={"inputs": {"text": "bad"}, "model": "fast"}, headers=mock_user_root
            )

            assert response.status_code == 400
            data = response.json()
            # RFC 7807: AGENT_INPUT_INVALID -> Agent Input Invalid
            assert data["title"] == "Agent Input Invalid"
            assert data["type"].endswith("/agent-input-invalid")
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_run_agent_runtime_error(async_client: AsyncClient, mock_user_root):
    """Verify that runtime errors return 500."""
    mock_agent_instance = MagicMock()
    # Generic Exception during execution -> 500
    mock_agent_instance.execute = AsyncMock(side_effect=RuntimeError("Crash"))
    mock_agent_class = MagicMock(return_value=mock_agent_instance)

    mock_registry = MagicMock()
    mock_registry.resolve_model_name = AsyncMock(return_value="mock-resolved-model")
    app.dependency_overrides[get_agent_registry_dep] = lambda: mock_registry

    try:
        with patch("backend.api.agents_router._load_agent_class", return_value=mock_agent_class):
            # Must provide model to pass initial checks
            response = await async_client.post(
                "/agents/TestAgent/run", json={"inputs": {"text": "hello"}, "model": "fast"}, headers=mock_user_root
            )

            assert response.status_code == 500
            data = response.json()
            # RFC 7807: AGENT_EXECUTION_FAILED -> Agent Execution Failed
            assert data["title"] == "Agent Execution Failed"
            assert data["type"].endswith("/agent-execution-failed")
    finally:
        app.dependency_overrides = {}


@pytest.mark.asyncio
async def test_run_agent_missing_model(async_client: AsyncClient, mock_user_root):
    """Verify that missing model returns 400 (Fail Fast)."""
    # No registry mock needed as it fails before resolution

    response = await async_client.post(
        "/agents/TestAgent/run",
        json={"inputs": {"text": "hello"}},  # Missing model
        headers=mock_user_root,
    )

    assert response.status_code == 400
    data = response.json()
    # RFC 7807: AGENT_MISSING_MODEL -> Agent Missing Model
    # Since AGENT_MISSING_MODEL is not in the Enum (yet?), it defaults to Generic 400 or dynamically generated
    # I should add it to Enum or check dynamic behavior.
    # Dynamic title from code: "AGENT_MISSING_MODEL" -> "Agent Missing Model"
    assert data["title"] == "Agent Missing Model"
    assert data["type"].endswith("/agent-missing-model")


@pytest.mark.asyncio
async def test_run_agent_invalid_strategy(async_client: AsyncClient, mock_user_root):
    """Verify that invalid model strategy returns 400 (Fail Fast)."""
    mock_registry = MagicMock()
    # Simulate DB lookup failure
    mock_registry.resolve_model_name = AsyncMock(side_effect=ValueError("Strategy not found"))
    app.dependency_overrides[get_agent_registry_dep] = lambda: mock_registry

    try:
        response = await async_client.post(
            "/agents/TestAgent/run",
            json={"inputs": {"text": "hello"}, "model": "nonexistent_strategy"},
            headers=mock_user_root,
        )

        assert response.status_code == 400
        data = response.json()
        # RFC 7807: INVALID_MODEL_STRATEGY -> Invalid Model Strategy
        assert data["title"] == "Invalid Model Strategy"
        assert data["type"].endswith("/invalid-model-strategy")

    finally:
        app.dependency_overrides = {}
