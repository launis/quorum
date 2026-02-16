from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import UploadFile

from backend.api.routes.config.knowledge import get_ingestion_status, ingest_knowledge_base, ingestion_jobs
from backend.exceptions import AppException


@pytest.mark.asyncio
async def test_ingest_knowledge_base_success():
    # Arrange
    mock_background_tasks = MagicMock()
    mock_file = MagicMock(spec=UploadFile)
    mock_file.filename = "test.docx"
    mock_file.read = AsyncMock(return_value=b"test content")

    mock_service = AsyncMock()
    mock_service.ingest_from_bytes = AsyncMock()

    # Act
    response = await ingest_knowledge_base(
        background_tasks=mock_background_tasks,
        file=mock_file,
        service=mock_service,
        language="en"
    )

    # Assert
    assert "job_id" in response
    job_id = response["job_id"]
    assert job_id in ingestion_jobs
    assert ingestion_jobs[job_id]["status"] == "processing"

    # Verify background task was added
    mock_background_tasks.add_task.assert_called_once()

@pytest.mark.asyncio
async def test_get_ingestion_status_found():
    # Arrange
    job_id = "test-job-123"
    ingestion_jobs[job_id] = {
        "status": "completed",
        "progress": 100,
        "stage": "Finished",
        "result": {"summary": "done"}
    }

    # Act
    result = await get_ingestion_status(job_id)

    # Assert
    assert result["status"] == "completed"
    assert result["progress"] == 100

@pytest.mark.asyncio
async def test_get_ingestion_status_not_found():
    # Act & Assert
    with pytest.raises(AppException) as exc_info:
        await get_ingestion_status("non-existent-job")

    assert exc_info.value.status_code == 404
    assert exc_info.value.error_code == "JOB_NOT_FOUND"
