from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from backend.dependencies import get_arq_pool, get_async_repository
from backend.main import app


@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.mark.asyncio
async def test_create_execution_success(client: AsyncClient, mock_repo):
    # Override
    app.dependency_overrides[get_async_repository] = lambda: mock_repo
    app.dependency_overrides[get_arq_pool] = lambda: AsyncMock()

    # Mock Repo Data
    mock_repo.get_workflow.return_value = MagicMock(id="test_wf", steps=[])
    mock_repo.create_execution = AsyncMock()

    payload = {
        "workflowId": "test_wf",
        "inputs": {"foo": "bar"}
    }

    response = await client.post("/v1/execute/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"

    # Verify repo call
    mock_repo.create_execution.assert_called_once()

    # Clean up
    del app.dependency_overrides[get_async_repository]

@pytest.mark.skip(reason="Cancel endpoint not implemented in lifecycle router")
@pytest.mark.asyncio
async def test_cancel_execution(client: AsyncClient, mock_repo):
    app.dependency_overrides[get_async_repository] = lambda: mock_repo

    # Mock Repo
    mock_repo.get_execution.return_value = {
        "id": "exec_1",
        "user_id": "root_master",
        "organization_id": "org_1",
        "status": "running",
    }
    mock_repo.update_execution = AsyncMock()

    # Authenticated as Root (see conftest default)
    response = await client.delete("/v1/execute/exec_1/cancel")
    assert response.status_code == 200
    assert response.json()["status"] == "cancelling"

    del app.dependency_overrides[get_async_repository]

@pytest.mark.asyncio
async def test_delete_execution_not_found(client: AsyncClient, mock_repo):
    app.dependency_overrides[get_async_repository] = lambda: mock_repo
    mock_repo.get_execution.return_value = None
    response = await client.delete("/v1/execute/non_existent")
    assert response.status_code == 404
    del app.dependency_overrides[get_async_repository]
