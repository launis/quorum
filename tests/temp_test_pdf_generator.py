import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from backend.services.pdf_generator import PdfReportService
from backend.exceptions import AppException, ErrorCodes
from backend.models.view import ReportView, UiSection, SectionType

class TestPdfReportService:
    
    @pytest.mark.asyncio
    async def test_generate_pdf_execution_not_found(self):
        """Test Fail Fast when execution is missing."""
        mock_repo = AsyncMock()
        mock_repo.get_execution.return_value = None
        
        service = PdfReportService(repository=mock_repo)
        
        with pytest.raises(AppException) as excinfo:
            await service.generate_execution_pdf("missing-id")
            
        assert excinfo.value.status_code == 404
        assert excinfo.value.details["error_code"] == ErrorCodes.EXECUTION_NOT_FOUND

    @pytest.mark.asyncio
    async def test_generate_pdf_invalid_chart_score(self):
        """Test Fail Fast when chart score is corrupted."""
        mock_repo = AsyncMock()
        # Mock execution data
        mock_execution = MagicMock()
        mock_execution.model_dump.return_value = {"id": "exec-1"}
        mock_repo.get_execution.return_value = mock_execution

        # Mock Transformer output with bad score
        with patch("backend.services.pdf_generator.ReportTransformer") as MockTransformer:
            mock_transformer_instance = MockTransformer.return_value
            mock_transformer_instance.transform.return_value = ReportView(
                view_id="exec-1",
                sections=[
                    UiSection(
                        id="section-1",
                        type=SectionType.SCORE_CARD,
                        title="Test Chart",
                        data={
                            "dimensions": [
                                {"label": "Dim1", "score": "NOT_A_NUMBER"} # <--- Corrupt Data
                            ],
                            "max_score": 4
                        }
                    )
                ]
            )
            
            service = PdfReportService(repository=mock_repo)
            
            # Should raise AppException (500) due to generic catch-all OR specific ValueError handling
            # We refactored ValueError -> AppException(CHART_GENERATION_FAILED)
            
            with pytest.raises(AppException) as excinfo:
                await service.generate_execution_pdf("exec-1")

            # The service wraps everything in a catch-all PDF_GENERATION_FAILED if not caught earlier.
            # However, our specific `except (ValueError, TypeError)` raises CHART_GENERATION_FAILED.
            # But wait, the `generate_execution_pdf` wraps the WHOLE thing in `except Exception`.
            # If we raise AppException inside, does the outer catch block re-wrap it?
            # Let's check the code.
            
            # If inner raises AppException, outer catch (Exception) catches it?
            # Yes, AppException inherits from Exception.
            # The outer block logs it and raises a NEW AppException(PDF_GENERATION_FAILED).
            # So we expect PDF_GENERATION_FAILED, and the 'cause' or details might contain the original.
            
            assert excinfo.value.status_code == 500
            assert excinfo.value.details["error_code"] == ErrorCodes.CHART_GENERATION_FAILED
            assert "Invalid score value" in str(excinfo.value.message) or "Invalid score value" in str(excinfo.value.__cause__)
            print("\n[TEST] Invalid Score: Fail Fast Successful")

if __name__ == "__main__":
    pass
