import json
import logging
from datetime import date, datetime
from typing import Any

logger = logging.getLogger(__name__)


def json_serial(obj: Any) -> Any:
    """JSON serializer for objects not serializable by default json code.

    Handles:
    - datetime/date -> ISO format string
    - Pydantic models -> dict (via model_dump)
    - Objects with model_dump method -> dict
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return obj.__dict__

    # Fail Fast: Strict serialization
    raise TypeError(f"Type '{type(obj).__name__}' is not JSON serializable")


def flexible_json_dump(data: Any, indent: int = 2, ensure_ascii: bool = False) -> str:
    """Dumps data to JSON string with strict error handling.

    Raises:
        AppException: If serialization fails (INTERNAL_SERVER_ERROR).
    """
    try:
        return json.dumps(data, indent=indent, ensure_ascii=ensure_ascii, default=json_serial)
    except (TypeError, ValueError) as e:
        from fastapi import status

        from backend.exceptions import AppException, ErrorCodes

        logger.error(f"JSON Serialization Failed: {e}")
        raise AppException(
            message=f"JSON Serialization Failed: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details={"error_code": ErrorCodes.INTERNAL_SERVER_ERROR},  # Could add SERIALIZATION_FAILED if needed
        )
