from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from backend.dependencies import get_async_repository
from backend.main import app


@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.mark.asyncio
async def test_get_recent_executions(client: AsyncClient, mock_repo):
    app.dependency_overrides[get_async_repository] = lambda: mock_repo
    mock_repo.get_all_executions.return_value = [
        {"id": "e1", "started_at": "2024-01-01T12:00:00Z", "status": "completed"},
        {"id": "e2", "started_at": "2024-01-02T12:00:00Z", "status": "failed"}
    ]

    response = await client.get("/executions/recent")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # Verify ordering (reverse chronological)
    assert data[0]["id"] == "e2"
    assert data[1]["id"] == "e1"
    del app.dependency_overrides[get_async_repository]

@pytest.mark.asyncio
async def test_get_execution_details(client: AsyncClient, mock_repo):
    app.dependency_overrides[get_async_repository] = lambda: mock_repo
    mock_repo.get_execution.return_value = {"id": "e1", "status": "completed"}

    response = await client.get("/executions/e1")
    assert response.status_code == 200
    assert response.json()["id"] == "e1"
    del app.dependency_overrides[get_async_repository]
