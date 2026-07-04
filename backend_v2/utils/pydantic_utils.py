"""Pydantic utility functions for data inflation and validation."""

import logging
from typing import Any

from pydantic import BaseModel, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)


def inflate[T: BaseModel](data: Any, model_class: type[T]) -> T | None:
    """Safely inflates a dictionary or object into a strict Pydantic model.

    Args:
        data: The input data (dict, existing model instance, or None).
        model_class: The target Pydantic model class.

    Returns:
        The inflated Pydantic model instance.
        Returns None ONLY if the input data itself is fundamentally empty (early return).

    Raises:
        AppException: If data is present but invalid (INVALID_OUTPUT_SCHEMA).
    """
    if not data:
        return None

    try:
        return model_class.model_validate(data)
    except ValidationError as e:
        msg = f"Failed to inflate data into {model_class.__name__}."
        logger.error(
            "[PydanticUtils] %s: %s",
            ErrorCodes.INVALID_OUTPUT_SCHEMA.name,
            msg,
            exc_info=True,
        )
        raise AppException(
            message=msg,
            status_code=500,
            details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
        ) from e
