"""Telemetry API router for client dual-reporting."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Telemetry"])


class ClientErrorPayload(BaseModel):
    """Payload sent by the Flutter client when an unhandled or caught error occurs."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    session_id: Annotated[str | None, Field(description="Client session or user ID if available")] = None
    app_version: Annotated[str | None, Field(description="Client application version")] = None
    platform: Annotated[str | None, Field(description="Client platform OS (e.g. android, ios, web)")] = None
    locale: Annotated[str | None, Field(description="Client UI language")] = None
    error_message: Annotated[str, Field(description="The main error message or exception toString()")]
    stack_trace: Annotated[str | None, Field(description="The Dart stack trace lines")] = None
    severity: Annotated[str, Field(description="Severity level, usually 'error' or 'fatal'")] = "error"
    context_data: Annotated[dict[str, Any], Field(default_factory=dict, description="Additional context or state dump")]


@router.post("/telemetry/client-error", status_code=204)
async def report_client_error(payload: ClientErrorPayload) -> None:
    """Ingest an error report from the client and log it into the backend's logging system.

    This fulfills the Dual-Reporting Telemetry Mandate. Errors logged here will be
    forwarded to Logfire/Sentry automatically via the backend's logging configuration.
    """
    try:
        log_fmt = "[%s] Platform: %s | Version: %s | Session: %s\nMessage: %s\nStack trace:\n%s"

        log_args = (
            ErrorCodes.CLIENT_ERROR.name,
            payload.platform,
            payload.app_version,
            payload.session_id,
            payload.error_message,
            payload.stack_trace,
        )

        if payload.severity.lower() == "fatal":
            logger.critical(log_fmt, *log_args, extra={"client_payload": payload.model_dump(mode="json")})
        else:
            logger.error(log_fmt, *log_args, extra={"client_payload": payload.model_dump(mode="json")})
    except Exception as e:
        if isinstance(e, AppException):
            raise
        logger.error(
            "[TelemetryRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "error": str(e)},
        )
        raise AppException(
            message="Internal telemetry failure",
            status_code=500,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e
