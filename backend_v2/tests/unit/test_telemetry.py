from unittest.mock import AsyncMock
import pytest

from backend_v2.api.routers.system.telemetry import report_client_error
from backend_v2.models.dtos.system import ClientErrorPayload


@pytest.mark.asyncio
async def test_report_client_error() -> None:
    payload = ClientErrorPayload(error_message="Test error", severity="error", context_data={})
    await report_client_error(payload=payload)
