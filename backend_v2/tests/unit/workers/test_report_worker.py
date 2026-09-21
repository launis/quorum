"""Unit tests for report worker verifying compilation delegation and failure containment."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.workers.report_worker import (
    generate_pdf_job,
    generate_pdf_task,
    generate_report_artifact_job,
    render_profile_job,
)


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


@pytest.mark.asyncio
async def test_generate_report_artifact_job_cancelled() -> None:
    """Verify cancellation handling in generate_report_artifact_job returns DLQ status."""
    with patch(
        "backend_v2.workers.report_worker.UnifiedWorkflowRepository",
        side_effect=asyncio.CancelledError,
    ):
        res = await generate_report_artifact_job(ctx={}, report_id="rep_0123456789abcdef")
    assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_generate_pdf_job_success() -> None:
    """Verify generate_pdf_job calls task and returns success string."""
    with patch("backend_v2.workers.report_worker.generate_pdf_task", new_callable=AsyncMock) as mock_task:
        res = await generate_pdf_job({}, "exe_1234567890123456", "en-US", "prof_1111222233334444")
        assert res == "PDF Generated for exe_1234567890123456"
        mock_task.assert_called_once_with("exe_1234567890123456", "en-US", "prof_1111222233334444")


@pytest.mark.asyncio
async def test_generate_pdf_job_cancelled() -> None:
    """Negative test: verify generate_pdf_job returns DLQ dictionary on cancellation."""
    with patch("backend_v2.workers.report_worker.generate_pdf_task", side_effect=asyncio.CancelledError):
        res = await generate_pdf_job({}, "exe_1234567890123456")
        assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_generate_pdf_job_exception() -> None:
    """Negative test: verify generate_pdf_job catches generic exception and routes to DLQ."""
    with patch("backend_v2.workers.report_worker.generate_pdf_task", side_effect=RuntimeError("PDF engine crash")):
        res = await generate_pdf_job({}, "exe_1234567890123456")
        assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_render_profile_job_success() -> None:
    """Verify render_profile_job calls generate_profile_synthesis_and_pdf_task and returns success string."""
    with patch(
        "backend_v2.workers.report_worker.generate_profile_synthesis_and_pdf_task", new_callable=AsyncMock
    ) as mock_task:
        ctx = {"redis": AsyncMock()}
        res = await render_profile_job(ctx, "exe_1234567890123456", "en-US", "prof_1111222233334444")
        assert res == "Render Job Completed for exe_1234567890123456"
        mock_task.assert_called_once_with("exe_1234567890123456", "en-US", "prof_1111222233334444", ctx["redis"])


@pytest.mark.asyncio
async def test_render_profile_job_cancelled() -> None:
    """Negative test: verify render_profile_job handles cancellation gracefully with DLQ."""
    with patch(
        "backend_v2.workers.report_worker.generate_profile_synthesis_and_pdf_task", side_effect=asyncio.CancelledError
    ):
        res = await render_profile_job({}, "exe_1234567890123456")
        assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_render_profile_job_exception() -> None:
    """Negative test: verify render_profile_job routes generic exception to DLQ."""
    with patch(
        "backend_v2.workers.report_worker.generate_profile_synthesis_and_pdf_task",
        side_effect=ValueError("Invalid profile"),
    ):
        res = await render_profile_job({}, "exe_1234567890123456")
        assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_generate_pdf_task_execution_not_found() -> None:
    """Verify generate_pdf_task skips processing when execution does not exist in repo."""
    with patch("backend_v2.workers.report_worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.report_worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_execution.return_value = None

            await generate_pdf_task("exe_1234567890123456")
            mock_repo.get_execution.assert_called_once_with("exe_1234567890123456")


@pytest.mark.asyncio
async def test_generate_pdf_task_success_path() -> None:
    """Verify generate_pdf_task happy path: delegates to ReportService for default artifact compilation."""
    with patch("backend_v2.workers.report_worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.report_worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "output_profile_id": "prof_1111222233334444",
                "status": "RUNNING",
                "target_locale": "fi",
                "metadata": {},
            }
            mock_artifact = MagicMock()
            mock_artifact.id = "rep_1234567890123456"

            with patch("backend_v2.workers.report_worker.report_service_mod.ReportService") as mock_service_class:
                mock_service = AsyncMock()
                mock_service_class.return_value = mock_service
                mock_service.get_or_create_default_artifact.return_value = mock_artifact

                await generate_pdf_task("exe_1234567890123456", None, "prof_1111222233334444")

                mock_service.get_or_create_default_artifact.assert_called_once_with(
                    execution_id="exe_1234567890123456",
                    profile_id="prof_1111222233334444",
                    locale=None,
                )
                mock_service.process_artifact_compilation.assert_called_once_with(mock_artifact.id)


@pytest.mark.asyncio
async def test_generate_pdf_task_exception_handling() -> None:
    """Negative test: verify generate_pdf_task catches failure and updates execution status."""
    with patch("backend_v2.workers.report_worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.report_worker.UnifiedWorkflowRepository") as mock_repo_class:
            mock_repo = AsyncMock()
            mock_repo_class.return_value = mock_repo
            mock_repo.get_execution.return_value = {
                "id": "exe_1234567890123456",
                "workflow_id": "wf_1234567890123456",
                "output_profile_id": "prof_1111222233334444",
                "status": "RUNNING",
                "target_locale": "en",
                "metadata": {},
                "steps": [{"id": "sys_render_prof_1111222233334444", "label": "Rendering", "status": "RUNNING"}],
                "step_states": {
                    "sys_render_prof_1111222233334444": {
                        "id": "sys_render_prof_1111222233334444",
                        "label": "Rendering",
                        "status": "RUNNING",
                    }
                },
            }

            with patch("backend_v2.workers.report_worker.report_service_mod.ReportService") as mock_service_class:
                mock_service = AsyncMock()
                mock_service_class.return_value = mock_service
                mock_service.get_or_create_default_artifact.side_effect = RuntimeError("ReportService crash")

                with pytest.raises(RuntimeError):
                    await generate_pdf_task("exe_1234567890123456", "en", "prof_1111222233334444")
                assert mock_repo.update_execution.call_count >= 1
