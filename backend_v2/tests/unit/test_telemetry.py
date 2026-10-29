"""Unit tests for the system telemetry router."""

from unittest.mock import MagicMock

import pytest
from fastapi import status
from pydantic import ValidationError

from backend_v2.api.routers.system import telemetry as telemetry_module
from backend_v2.api.routers.system.telemetry import report_client_error
from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.system import ClientErrorPayload


@pytest.mark.asyncio
async def test_report_client_error_logs_standard_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify non-fatal client errors are logged at ERROR level with serialized payload."""
    mock_error = MagicMock()
    mock_critical = MagicMock()
    monkeypatch.setattr(telemetry_module.logger, "error", mock_error)
    monkeypatch.setattr(telemetry_module.logger, "critical", mock_critical)

    payload = ClientErrorPayload(
        session_id="ses_1234567890abcdef",
        app_version="2.1.0",
        platform="windows",
        error_message="Widget overflow error",
        stack_trace="main.dart:42",
        severity="error",
        context_data={"screen": "dashboard"},
    )
    await report_client_error(payload=payload)

    mock_error.assert_called_once()
    mock_critical.assert_not_called()
    _, kwargs = mock_error.call_args
    assert kwargs["extra"]["client_payload"]["error_message"] == "Widget overflow error"
    assert "locale" not in kwargs["extra"]["client_payload"]


@pytest.mark.asyncio
async def test_report_client_error_logs_fatal_critical(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify fatal client errors (case-insensitive) are logged at CRITICAL level."""
    mock_error = MagicMock()
    mock_critical = MagicMock()
    monkeypatch.setattr(telemetry_module.logger, "error", mock_error)
    monkeypatch.setattr(telemetry_module.logger, "critical", mock_critical)

    payload = ClientErrorPayload(
        error_message="Unhandled isolate crash",
        severity="FATAL",
        context_data={},
    )
    await report_client_error(payload=payload)

    mock_critical.assert_called_once()
    mock_error.assert_not_called()


@pytest.mark.asyncio
async def test_report_client_error_reraises_app_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify upstream AppExceptions are re-raised directly without wrapping."""
    upstream_exc = AppException(
        message="Upstream rate limit",
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        details={"error_code": ErrorCodes.RATE_LIMIT_EXCEEDED.value},
    )
    monkeypatch.setattr(
        telemetry_module.logger,
        "error",
        MagicMock(side_effect=upstream_exc),
    )

    payload = ClientErrorPayload(
        error_message="Test error",
        severity="error",
        context_data={},
    )
    with pytest.raises(AppException) as exc_info:
        await report_client_error(payload=payload)

    assert exc_info.value is upstream_exc
    assert exc_info.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS


@pytest.mark.asyncio
async def test_report_client_error_translates_unexpected_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Verify unexpected runtime failures log RFC 7807 error and raise 500 AppException."""
    mock_error = MagicMock(side_effect=[RuntimeError("Sink disconnected"), None])
    monkeypatch.setattr(telemetry_module.logger, "error", mock_error)

    payload = ClientErrorPayload(
        error_message="Test error",
        severity="error",
        context_data={},
    )
    with pytest.raises(AppException) as exc_info:
        await report_client_error(payload=payload)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.message == "Internal telemetry failure"
    assert exc_info.value.details == {"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value}
    assert mock_error.call_count == 2


def test_client_error_payload_rejects_invalid_boundary_inputs() -> None:
    """Verify ClientErrorPayload enforces strict types and forbids unknown fields."""
    with pytest.raises(ValidationError):
        ClientErrorPayload.model_validate(
            {
                "error_message": "Valid message",
                "unexpected_field": "forbidden",
            }
        )

    with pytest.raises(ValidationError):
        ClientErrorPayload.model_validate({"severity": "error"})
