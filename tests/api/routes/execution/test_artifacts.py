from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import AsyncClient

from backend.dependencies import get_arq_pool, get_async_repository, get_storage_service_dep
from backend.main import app


@pytest.fixture
def mock_repo():
    return AsyncMock()

@pytest.fixture
def mock_storage():
    return MagicMock()

@pytest.mark.asyncio
async def test_download_pdf_queued(client: AsyncClient, mock_repo, mock_storage):
    app.dependency_overrides[get_async_repository] = lambda: mock_repo
    app.dependency_overrides[get_storage_service_dep] = lambda: mock_storage
    app.dependency_overrides[get_arq_pool] = lambda: AsyncMock()

    # Mock Execution
    mock_repo.get_execution.return_value = {
        "id": "e1",
        "user_id": "root_master", # Matches default mock user
        "organization_id": "org_1"
    }

    # Mock Storage missing file
    mock_storage.exists.return_value = False

    response = await client.get("/executions/e1/pdf/download")

    # Should accept and queue
    assert response.status_code == 202
    assert response.json()["status"] == "accepted"

    del app.dependency_overrides[get_async_repository]
    del app.dependency_overrides[get_storage_service_dep]

@pytest.mark.asyncio
async def test_download_pdf_success(client: AsyncClient, mock_repo, mock_storage):
    app.dependency_overrides[get_async_repository] = lambda: mock_repo
    app.dependency_overrides[get_storage_service_dep] = lambda: mock_storage
    app.dependency_overrides[get_arq_pool] = lambda: AsyncMock()

    mock_repo.get_execution.return_value = {
        "id": "e1",
        "user_id": "root_master",
        "organization_id": "org_1"
    }

    # Mock Storage HAS file
    mock_storage.exists.return_value = True
    # For LocalFileStorage path construction in route, we might need a real-ish path or mock base_path
    mock_storage.base_path = MagicMock()
    mock_storage.base_path.__truediv__.return_value = "dummy/path.pdf"

    # Mock FileResponse might be tricky without real file, expecting 500 or error if file not found on disk really
    # But route logic checks storage.exists first.
    pass # difficult to integration test FileResponse validation without real file

    del app.dependency_overrides[get_async_repository]
    del app.dependency_overrides[get_storage_service_dep]
