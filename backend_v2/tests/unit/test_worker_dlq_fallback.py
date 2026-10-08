from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend_v2.exceptions import ServiceUnavailableError
from backend_v2.workers import generate_report_artifact_job


@pytest.mark.asyncio
async def test_generate_report_artifact_job_catches_service_unavailable_error() -> None:
    """Test that generate_report_artifact_job catches ServiceUnavailableError (e.g. from 429 RateLimitError)
    and returns a DLQ dictionary as mandated by dlq_arq_fallback_routing,
    instead of bubbling the exception up and crashing the Arq worker.
    """
    ctx = {"redis": AsyncMock()}
    report_id = "rep_1234567890abcdef"

    mock_service = MagicMock()
    mock_service.process_artifact_compilation = AsyncMock(
        side_effect=ServiceUnavailableError("Model provider rate limit exceeded")
    )

    with (
        patch("backend_v2.workers.report_worker.get_driver", new_callable=AsyncMock),
        patch("backend_v2.workers.report_worker.report_service_mod.ReportService", return_value=mock_service),
    ):
        result = await generate_report_artifact_job(ctx, report_id)

        assert type(result) is dict
        assert result["_dlq_status"] == "FAILED/DLQ"
