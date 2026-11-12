"""Unit tests for Arq report worker Dead Letter Queue fallback routing."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import ServiceUnavailableError
from backend_v2.workers import generate_report_artifact_job


@pytest.mark.asyncio
async def test_generate_report_artifact_job_catches_service_unavailable_error() -> None:
    """Verify generate_report_artifact_job routes ServiceUnavailableError to the Dead Letter Queue."""
    ctx = {"redis": AsyncMock()}
    report_id = "rep_0195f3a0000070018234567890abcdef"

    mock_service = MagicMock()
    mock_service.process_artifact_compilation = AsyncMock(
        side_effect=ServiceUnavailableError("Model provider rate limit exceeded")
    )

    with patch("backend_v2.workers.report_worker.report_service_mod.ReportService", return_value=mock_service):
        result = await generate_report_artifact_job(ctx, report_id)

        assert type(result) is dict
        assert result["_dlq_status"] == "FAILED/DLQ"


@pytest.mark.asyncio
async def test_generate_report_artifact_job_catches_unexpected_runtime_error() -> None:
    """Verify generate_report_artifact_job routes unexpected RuntimeError failures to the Dead Letter Queue."""
    ctx = {"redis": AsyncMock()}
    report_id = "rep_0195f3a0000070018234567890abcdef"

    mock_service = MagicMock()
    mock_service.process_artifact_compilation = AsyncMock(side_effect=RuntimeError("Unexpected compilation crash"))

    with patch("backend_v2.workers.report_worker.report_service_mod.ReportService", return_value=mock_service):
        result = await generate_report_artifact_job(ctx, report_id)

        assert type(result) is dict
        assert result["_dlq_status"] == "FAILED/DLQ"
