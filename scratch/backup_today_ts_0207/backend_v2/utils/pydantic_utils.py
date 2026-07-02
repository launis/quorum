"""Pydantic utility functions for data inflation and validation."""

import logging
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


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

    # 1. If already the correct model instance, return it.
    if isinstance(data, model_class):
        return data

    # 2. If it's a dict, strictly validate and parse.
    if isinstance(data, dict):
        try:
            return model_class.model_validate(data)
        except ValidationError as e:
            msg = f"Failed to inflate dict into {model_class.__name__}."
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

    # 3. If it's an object (e.g. from ORM or legacy), try conversion via dump/load
    # This is expensive but safe for transition.
    try:
        if hasattr(data, "model_dump"):
            return model_class.model_validate(data.model_dump())
        if hasattr(data, "__dict__"):
            return model_class.model_validate(data.__dict__)
    except Exception as e:
        msg = f"Failed to convert object attributes to {model_class.__name__}."
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

    # If the data type is wholly unrecognized and did not trip the exception block
    msg = f"Unrecognized data type '{type(data).__name__}' passed for inflation into {model_class.__name__}."
    logger.error("[PydanticUtils] %s: %s", ErrorCodes.INVALID_OUTPUT_SCHEMA.name, msg)
    raise AppException(
        message=msg,
        status_code=500,
        details={"error_code": ErrorCodes.INVALID_OUTPUT_SCHEMA.value},
    )
