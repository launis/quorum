"""Telemetry API router for client dual-reporting."""

import logging

from fastapi import APIRouter, status

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.dtos.system import ClientErrorPayload

logger = logging.getLogger(__name__)

__all__ = [
    "report_client_error",
    "router",
]

router = APIRouter(tags=["Telemetry"])


@router.post("/telemetry/client-error", status_code=status.HTTP_204_NO_CONTENT)
async def report_client_error(payload: ClientErrorPayload) -> None:
    """Ingest an error report from the client and log it into the backend's logging system.

    This fulfills the Dual-Reporting Telemetry Mandate. Errors logged here will be
    forwarded to Logfire/Sentry automatically via the backend's logging configuration.

    Args:
        payload: The telemetry payload from the client containing the error details.

    Returns:
        None.

    Raises:
        AppException: With error code `INTERNAL_SERVER_ERROR` if logging the client
            error fails internally, or re-raises any upstream `AppException`.
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
        serialized_payload = payload.model_dump(mode="json", exclude_none=True)

        if payload.severity.lower() == "fatal":
            logger.critical(log_fmt, *log_args, extra={"client_payload": serialized_payload})
        else:
            logger.error(log_fmt, *log_args, extra={"client_payload": serialized_payload})
    except AppException:
        raise
    except Exception as e:
        logger.error(
            "[TelemetryRouter] %s: %s",
            ErrorCodes.INTERNAL_SERVER_ERROR.name,
            str(e),
            exc_info=True,
            extra={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value, "error": str(e)},
        )
        raise AppException(
            message="Internal telemetry failure",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR.value},
        ) from e
