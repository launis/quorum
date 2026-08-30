from unittest.mock import AsyncMock, patch

import pytest

from backend_v2.exceptions import ServiceUnavailableError
from backend_v2.worker import render_profile_job


@pytest.mark.asyncio
async def test_render_profile_job_catches_service_unavailable_error() -> None:
    """Test that render_profile_job catches ServiceUnavailableError (e.g. from 429 RateLimitError)
    and returns a DLQ dictionary as mandated by dlq_arq_fallback_routing,
    instead of bubbling the exception up and crashing the Arq worker.
    """
    ctx = {"redis": AsyncMock()}
    execution_id = "exe_123"
    accept_language = "fi"
    profile_id = "prof_456"

    with patch("backend_v2.worker.generate_profile_synthesis_and_pdf_task", new_callable=AsyncMock) as mock_generate:
        # Simulate the TaskGroup crash from Vertex AI rate limits
        mock_generate.side_effect = ServiceUnavailableError("Model provider rate limit exceeded")

        # Call the Arq job
        result = await render_profile_job(ctx, execution_id, accept_language, profile_id)

        # According to rule dlq_arq_fallback_routing, it MUST yield/return {"_dlq_status": "FAILED/DLQ"}
        assert isinstance(result, dict)
        assert result.get("_dlq_status") == "FAILED/DLQ"
