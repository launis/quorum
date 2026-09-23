"""Unit tests for synthesis_worker.py covering error handling, caching, validation, and full execution."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import AppException, ResourceNotFoundError
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.enums import ExecutionStatus, TargetBlockType
from backend_v2.models.execution_core import ExecutionMetadata
from backend_v2.tests.unit.test_worker_synthesis import *  # noqa: F403
from backend_v2.workers.synthesis_worker import generate_profile_synthesis_and_pdf_task


@pytest.mark.asyncio
async def test_synthesis_worker_empty_accept_language_raises() -> None:
    """Test generate_profile_synthesis_and_pdf_task raises AppException when accept_language is empty."""
    with pytest.raises(AppException) as exc_info:
        await generate_profile_synthesis_and_pdf_task(execution_id="exe_1", accept_language="", profile_id="pro_1")
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_synthesis_worker_missing_execution_returns() -> None:
    """Test generate_profile_synthesis_and_pdf_task returns early if execution does not exist."""
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = None

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
            await generate_profile_synthesis_and_pdf_task(
                execution_id="exe_missing", accept_language="en", profile_id="pro_1"
            )
            mock_repo.get_execution.assert_called_once_with("exe_missing")


@pytest.mark.asyncio
async def test_synthesis_worker_already_synthesized_enqueues_pdf() -> None:
    """Test generate_profile_synthesis_and_pdf_task short-circuits to report artifact generation if already synthesized."""
    prof_id = "pro_0123456789abcdef01"
    cache = RenderedSynthesisCache()
    rec = ExecutionRecord(
        id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        output_profile_id=prof_id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
        profile_syntheses={prof_id: cache},
    )
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = rec.model_dump(mode="json")
    mock_redis = AsyncMock()
    mock_artifact = MagicMock()
    mock_artifact.id = "rep_0123456789abcdef01"

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
            with patch("backend_v2.workers.synthesis_worker.ReportService") as mock_report_service_cls:
                mock_svc = mock_report_service_cls.return_value
                mock_svc.get_or_create_default_artifact = AsyncMock(return_value=mock_artifact)
                mock_svc.compile_and_persist_artifact = AsyncMock()
                await generate_profile_synthesis_and_pdf_task(
                    execution_id="exe_0123456789abcdef01",
                    accept_language="en",
                    profile_id=prof_id,
                    redis=mock_redis,
                )
                mock_svc.get_or_create_default_artifact.assert_awaited_once_with(
                    execution_id="exe_0123456789abcdef01",
                    profile_id=prof_id,
                    locale="en",
                )
                mock_svc.compile_and_persist_artifact.assert_awaited_once_with(
                    "rep_0123456789abcdef01",
                    mock_redis,
                )


@pytest.mark.asyncio
async def test_synthesis_worker_profile_not_found_raises() -> None:
    """Test generate_profile_synthesis_and_pdf_task raises ResourceNotFoundError if profile missing."""
    prof_id = "pro_0123456789abcdef01"
    rec = ExecutionRecord(
        id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        output_profile_id=prof_id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
    )
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = rec.model_dump(mode="json")
    mock_repo.get_output_profile_by_id.return_value = None

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
            with pytest.raises(ResourceNotFoundError):
                await generate_profile_synthesis_and_pdf_task(
                    execution_id="exe_0123456789abcdef01",
                    accept_language="en",
                    profile_id=prof_id,
                )


@pytest.mark.asyncio
async def test_synthesis_worker_workflow_not_found_raises() -> None:
    """Test generate_profile_synthesis_and_pdf_task raises AppException if workflow missing."""
    prof_id = "pro_0123456789abcdef01"
    rec = ExecutionRecord(
        id="exe_0123456789abcdef01",
        workflow_id="wor_0123456789abcdef01",
        output_profile_id=prof_id,
        status=ExecutionStatus.PASSED,
        target_locale="en",
        metadata=ExecutionMetadata(),
    )
    prof = OutputProfile(
        id=prof_id,
        slug="prof_test",
        workflow_id="wor_0123456789abcdef01",
        name=I18nText(translations={"en": "Test Profile"}),
        target_block_order=[TargetBlockType.EXECUTIVE_SUMMARY_BLOCK],
    )
    mock_repo = AsyncMock()
    mock_repo.get_execution.return_value = rec.model_dump(mode="json")
    mock_repo.get_output_profile_by_id.return_value = prof.model_dump(mode="json")
    mock_repo.get_workflow_by_id.return_value = None

    with patch("backend_v2.workers.synthesis_worker.get_driver", new_callable=AsyncMock):
        with patch("backend_v2.workers.synthesis_worker.UnifiedWorkflowRepository", return_value=mock_repo):
            with pytest.raises(AppException) as exc_info:
                await generate_profile_synthesis_and_pdf_task(
                    execution_id="exe_0123456789abcdef01",
                    accept_language="en",
                    profile_id=prof_id,
                )
            assert exc_info.value.status_code == 400
