import pytest
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
import os
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
    with patch("backend.worker.PdfReportService") as MockServiceClass:
        mock_service_instance = MockServiceClass.return_value
        mock_service_instance.generate_execution_pdf = AsyncMock(return_value=b"%PDF-MOCK")
        
        # Mock File Operations
        with patch("builtins.open", mock_open()) as mock_file:
            with patch("os.makedirs") as mock_makedirs:
                
                # Execute
                result_path = await generate_pdf_job(ctx, execution_id=execution_id)
                
                # Verify Logic
                
                # 1. ProgressService Init
                # We can't easily check internal variable 'progress' but we can check PdfReportService init args
                # MockServiceClass.call_args[0][1] should be the progress service
                assert MockServiceClass.called
                
                # 2. Service Call
                mock_service_instance.generate_execution_pdf.assert_called_with(execution_id)
                
                # 3. Directories
                mock_makedirs.assert_called_with(f"data/files/executions/{execution_id}", exist_ok=True)
                
                # 4. File Write
                mock_file.assert_called_with(f"data/files/executions/{execution_id}/report.pdf", "wb")
                mock_file().write.assert_called_with(b"%PDF-MOCK")
                
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

