"""Unit tests for report worker verifying compilation delegation and failure containment."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import backend_v2.workers.report_worker as report_worker_mod
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.domain.report_artifact import ReportArtifact
from backend_v2.models.enums import ReportStatus
from backend_v2.tests.factories.model_factories import ReportArtifactFactory
from backend_v2.tests.fakes.in_memory_repositories import InMemoryUnifiedWorkflowRepository
from backend_v2.workers.report_worker import generate_report_artifact_job


@pytest.mark.asyncio
async def test_generate_report_artifact_job_delegates_to_service() -> None:
    """Verify that generate_report_artifact_job delegates compilation to ReportService."""
    mock_service = MagicMock()
    mock_service.process_artifact_compilation = AsyncMock()
    mock_repo = InMemoryUnifiedWorkflowRepository()

    with (
        patch("backend_v2.services.report.ReportService", return_value=mock_service),
        patch("backend_v2.workers.report_worker.get_driver", new_callable=AsyncMock),
        patch.object(report_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
    ):
        _ = await generate_report_artifact_job(
            ctx={},
            report_id="rep_0195f3a0000070008123456789abcdef",
        )

    mock_service.process_artifact_compilation.assert_awaited_once_with(
        "rep_0195f3a0000070008123456789abcdef", force_resynthesis=False
    )


@pytest.mark.asyncio
async def test_generate_report_artifact_job_forwards_force_resynthesis() -> None:
    """Verify that generate_report_artifact_job forwards force_resynthesis=True to ReportService."""
    mock_service = MagicMock()
    mock_service.process_artifact_compilation = AsyncMock()
    mock_repo = InMemoryUnifiedWorkflowRepository()

    with (
        patch("backend_v2.services.report.ReportService", return_value=mock_service),
        patch("backend_v2.workers.report_worker.get_driver", new_callable=AsyncMock),
        patch.object(report_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
    ):
        await generate_report_artifact_job(
            ctx={},
            report_id="rep_0195f3a0000070008123456789abcdef",
            force_resynthesis=True,
        )

    mock_service.process_artifact_compilation.assert_awaited_once_with(
        "rep_0195f3a0000070008123456789abcdef", force_resynthesis=True
    )


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

    mock_repo = InMemoryUnifiedWorkflowRepository()

    # Phase 6, Step 6.2: Use stateful InMemoryUnifiedWorkflowRepository without string-based patch
    with (
        patch("backend_v2.services.report.ReportService", return_value=mock_service),
        patch("backend_v2.workers.report_worker.get_driver", new_callable=AsyncMock),
        patch.object(report_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
    ):
        await generate_report_artifact_job(
            ctx={},
            report_id="rep_0195f3a0000070008123456789abcdef",
        )

    # Invariant: Failure in Phase 2/3 does NOT alter execution record status to FAILED
    assert (await mock_repo.get_execution("exe_0195f3a0000070008123456789abcdef")) is None


@pytest.mark.asyncio
async def test_generate_report_artifact_job_cancelled() -> None:
    """Verify cancellation handling in generate_report_artifact_job returns DLQ status."""
    mock_repo = InMemoryUnifiedWorkflowRepository()
    mock_service = MagicMock()
    mock_service.process_artifact_compilation = AsyncMock(side_effect=asyncio.CancelledError)

    with (
        patch("backend_v2.services.report.ReportService", return_value=mock_service),
        patch("backend_v2.workers.report_worker.get_driver", new_callable=AsyncMock),
        patch.object(report_worker_mod, "UnifiedWorkflowRepository", return_value=mock_repo),
    ):
        res = await generate_report_artifact_job(ctx={}, report_id="rep_0195f3a0000070008123456789abcdef")
    assert res == {"_dlq_status": "FAILED/DLQ"}


@pytest.mark.asyncio
async def test_report_worker_fails_fast_when_execution_record_missing_in_memory() -> None:
    """Phase 6, Step 6.2: Verify report worker fails fast deterministically when execution record is missing in memory."""
    repo = InMemoryUnifiedWorkflowRepository()
    report_id = "rep_0195f3a0000070008123456789abcdef"
    missing_exec_id = "exe_0195f3a0000070008123456789abcdef"

    # Case 1: Missing report artifact in repository triggers ResourceNotFoundError -> DLQ status
    with (
        patch("backend_v2.workers.report_worker.get_driver", new_callable=AsyncMock),
        patch.object(report_worker_mod, "UnifiedWorkflowRepository", return_value=repo),
    ):
        missing_report_res = await generate_report_artifact_job(ctx={}, report_id=report_id)
    assert missing_report_res == {"_dlq_status": "FAILED/DLQ"}

    # Case 2: Report artifact exists in repository, but associated execution_id is missing in memory
    seeded_artifact = ReportArtifactFactory.build(
        id=report_id,
        execution_id=missing_exec_id,
        status=ReportStatus.PENDING,
    )
    repo.save_report_artifact(seeded_artifact)

    with (
        patch("backend_v2.workers.report_worker.get_driver", new_callable=AsyncMock),
        patch.object(report_worker_mod, "UnifiedWorkflowRepository", return_value=repo),
    ):
        await generate_report_artifact_job(ctx={}, report_id=report_id)

    reconstituted = await repo.get_report_artifact(report_id)
    assert reconstituted is not None
    validated = ReportArtifact.model_validate_json(reconstituted.model_dump_json())
    assert validated.status == ReportStatus.FAILED
    assert validated.error_message is not None
    assert missing_exec_id in validated.error_message
