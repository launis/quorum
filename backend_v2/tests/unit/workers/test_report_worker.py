"""Unit tests for report worker verifying compilation delegation and failure containment."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.workers.report_worker import generate_report_artifact_job


@pytest.mark.asyncio
async def test_generate_report_artifact_job_delegates_to_service() -> None:
    """Verify that generate_report_artifact_job delegates compilation to ReportService."""
    mock_service = MagicMock()
    mock_service.process_artifact_compilation = AsyncMock()

    with (
        patch("backend_v2.services.report_service.ReportService", return_value=mock_service),
        patch("backend_v2.workers.report_worker.get_driver", new_callable=AsyncMock),
    ):
        result = await generate_report_artifact_job(
            ctx={},
            report_id="rep_0123456789abcdef",
        )

    assert result == "Report Artifact Generated: rep_0123456789abcdef"
    mock_service.process_artifact_compilation.assert_awaited_once_with("rep_0123456789abcdef")


@pytest.mark.asyncio
async def test_generate_report_artifact_job_failure_containment() -> None:
    """Verify that when ReportService fails, execution record status is not corrupted."""
    mock_service = MagicMock()
    mock_service.process_artifact_compilation = AsyncMock(
        side_effect=AppException(
            message="PDF Render Crash",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        )
    )

    mock_repo = MagicMock()
    mock_repo.update_execution = AsyncMock()

    with (
        patch("backend_v2.services.report_service.ReportService", return_value=mock_service),
        patch("backend_v2.workers.report_worker.get_driver", new_callable=AsyncMock),
        patch("backend_v2.workers.report_worker.UnifiedWorkflowRepository", return_value=mock_repo),
    ):
        await generate_report_artifact_job(
            ctx={},
            report_id="rep_0123456789abcdef",
        )

    # Invariant: Failure in Phase 2/3 does NOT alter execution record status to FAILED
    assert not mock_repo.update_execution.called
