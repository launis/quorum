"""Telemetry API router for client dual-reporting."""

import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend_v2.exceptions import ErrorCodes

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Telemetry"])


class ClientErrorPayload(BaseModel):
    """Payload sent by the Flutter client when an unhandled or caught error occurs."""

    session_id: str | None = Field(None, description="Client session or user ID if available")
    app_version: str | None = Field(None, description="Client application version")
    platform: str | None = Field(None, description="Client platform OS (e.g. android, ios, web)")
    locale: str | None = Field(None, description="Client UI language")
    error_message: str = Field(..., description="The main error message or exception toString()")
    stack_trace: str | None = Field(None, description="The Dart stack trace lines")
    severity: str = Field("error", description="Severity level, usually 'error' or 'fatal'")
    context_data: dict[str, Any] | None = Field(default_factory=dict, description="Additional context or state dump")


@router.post("/telemetry/client-error", status_code=204)
async def report_client_error(payload: ClientErrorPayload) -> None:
    """Ingest an error report from the client and log it into the backend's logging system.

    This fulfills the Dual-Reporting Telemetry Mandate. Errors logged here will be
    forwarded to Logfire/Sentry automatically via the backend's logging configuration.
    """
    # We log it with the specific ErrorCodes.CLIENT_ERROR tag so it stands out in logs
    log_msg = (
        f"[{ErrorCodes.CLIENT_ERROR.name}] "
        f"Platform: {payload.platform} | Version: {payload.app_version} | Session: {payload.session_id}\n"
        f"Message: {payload.error_message}\n"
        f"Stack trace:\n{payload.stack_trace}"
    )

    if payload.severity.lower() == "fatal":
        logger.critical(log_msg, extra={"client_payload": payload.model_dump(mode="json")})
    else:
        logger.error(log_msg, extra={"client_payload": payload.model_dump(mode="json")})
