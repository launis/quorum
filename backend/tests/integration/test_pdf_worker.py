from unittest.mock import AsyncMock, mock_open, patch

import pytest

from backend.worker import generate_pdf_job


@pytest.mark.asyncio
async def test_generate_pdf_job_success():
    # Setup Context Mock
    mock_redis = AsyncMock()
    mock_repo = AsyncMock()
    ctx = {
        "redis": mock_redis,
        "repository": mock_repo
    }

    execution_id = "exec-worker-test"

    # Mock PdfReportService to avoid actual generation and dependencies
    with patch("backend.worker.PdfReportService") as MockServiceClass, \
         patch("backend.worker.get_storage_driver") as mock_get_storage:
        
        mock_service_instance = MockServiceClass.return_value
        mock_service_instance.generate_execution_pdf = AsyncMock(return_value=b"%PDF-MOCK")
        
        mock_storage = AsyncMock()
        mock_storage.save.return_value = f"data/files/executions/{execution_id}/report.pdf"
        mock_get_storage.return_value = mock_storage

        # Execute
        result_path = await generate_pdf_job(ctx, execution_id=execution_id)

        # Verify Logic
        assert MockServiceClass.called
        mock_service_instance.generate_execution_pdf.assert_called_with(execution_id)
        mock_storage.save.assert_called_with(f"executions/{execution_id}/report.pdf", b"%PDF-MOCK")
        
        # 5. Return
        assert result_path == f"data/files/executions/{execution_id}/report.pdf"

@pytest.mark.asyncio
async def test_generate_pdf_job_failure():
    # Setup Context
    ctx = {"redis": AsyncMock(), "repository": AsyncMock()}

    # Force Exception
    with patch("backend.worker.PdfReportService") as MockServiceClass:
        mock_service_instance = MockServiceClass.return_value
        mock_service_instance.generate_execution_pdf.side_effect = Exception("Generation Failed")

        # Execute & Expect Error
        with pytest.raises(Exception, match="Generation Failed"):
            await generate_pdf_job(ctx, execution_id="fail-exec")

