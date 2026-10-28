"""Storage path utilities to enforce Single Source of Truth."""

import logging

from fastapi import status

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

__all__ = ["get_forensic_input_path"]


def get_forensic_input_path(execution_id: str, input_key: str) -> str:
    """Return the deterministic storage path for a forensic input.

    Args:
        execution_id: The ID of the execution.
        input_key: The key of the input to store.

    Returns:
        The deterministic relative file path.

    Raises:
        AppException: With ErrorCodes.VALIDATION_FAILED if execution_id or input_key
            is empty, contains path traversal sequences, or sanitizes to an empty key.
    """
    cleaned_exec_id = execution_id.strip()
    if not cleaned_exec_id or any(sep in cleaned_exec_id for sep in ("/", "\\", "..")):
        msg = "Invalid execution_id for forensic input path."
        logger.error(
            "[Paths] %s: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            msg,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            exc_info=True,
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    safe_key = "".join(c for c in input_key if c.isalnum() or c in ("_", "-"))
    if not safe_key:
        msg = "Invalid input_key for forensic input path: sanitized key is empty."
        logger.error(
            "[Paths] %s: %s",
            ErrorCodes.VALIDATION_FAILED.name,
            msg,
            extra={"error_code": ErrorCodes.VALIDATION_FAILED.name},
            exc_info=True,
        )
        raise AppException(
            message=msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
        )

    return f"executions/{cleaned_exec_id}/inputs/input_{safe_key}.md"
