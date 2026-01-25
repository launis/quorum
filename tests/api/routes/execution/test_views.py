from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from backend.dependencies import get_async_repository
from backend.main import app


@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.mark.asyncio
async def test_get_execution_view_bff(client: AsyncClient, mock_repo):
    app.dependency_overrides[get_async_repository] = lambda: mock_repo
    # Mock raw execution with some steps
    mock_repo.get_execution.return_value = {
        "id": "e1",
        "results": {
            "step_judge": {
                "total_score": 3.0,
                "final_verdict": "Pass",
                "scale_min": 1,
                "scale_max": 5
            }
        }
    }

    response = await client.get("/executions/e1/view")
    assert response.status_code == 200
    data = response.json()

    # Check structure
    assert data["view_id"] == "e1"
    assert len(data["sections"]) > 0
    # Judge section should exist
    assert any(s["type"] == "SCORE_CARD" for s in data["sections"])
    del app.dependency_overrides[get_async_repository]

@pytest.mark.asyncio
async def test_get_execution_raw(client: AsyncClient, mock_repo):
    app.dependency_overrides[get_async_repository] = lambda: mock_repo
    mock_repo.get_execution.return_value = {"id": "e1", "results": {"foo": "bar"}}

    response = await client.get("/executions/e1/raw")
    assert response.status_code == 200
    assert response.json()["results"]["foo"] == "bar"
    del app.dependency_overrides[get_async_repository]
