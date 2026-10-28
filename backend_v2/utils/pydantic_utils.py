"""Pydantic utility functions for data inflation and validation."""

import logging

from pydantic import BaseModel, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes

__all__ = ["inflate"]

logger = logging.getLogger(__name__)


def inflate[T: BaseModel](data: object, model_class: type[T]) -> T | None:
    """Safely inflate a dictionary or object into a strict Pydantic model.

    Args:
        data: The input payload to validate into the target model.
        model_class: The target Pydantic model class.

    Returns:
        The inflated Pydantic model instance, or None if the input data is empty.

    Raises:
        AppException: If data is present but fails schema validation (INVALID_OUTPUT_SCHEMA).
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
