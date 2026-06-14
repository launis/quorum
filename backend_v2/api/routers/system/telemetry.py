"""Telemetry API router for client dual-reporting."""

import logging

from fastapi import APIRouter

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.system import ClientErrorPayload

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Telemetry"])


@router.post("/telemetry/client-error", status_code=204)
async def report_client_error(payload: ClientErrorPayload) -> None:
    """Ingest an error report from the client and log it into the backend's logging system.

    This fulfills the Dual-Reporting Telemetry Mandate. Errors logged here will be
    forwarded to Logfire/Sentry automatically via the backend's logging configuration.

    Args:
        payload: The telemetry payload from the client containing the error details.

    Returns:
        None.

    Raises:
        AppException: If logging the client error fails internally.
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
