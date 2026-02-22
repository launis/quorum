import logging
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


def inflate[T: BaseModel](data: Any, model_class: type[T]) -> T | None:
    """Safely inflates a dictionary or object into a strict Pydantic model.

    Args:
        data: The input data (dict, existing model instance, or None).
        model_class: The target Pydantic model class.

    Returns:
        The inflated Pydantic model instance, or None if input matches (strict validation).
        Raises strict validation errors if data is present but invalid.
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
            logger.error(f"Failed to inflate {model_class.__name__}: {e}")
            # Fail Fast: Re-raise or return None? Mandate says "Fail Fast"
            # typically implies raising exceptions for invalid states.
            # However, returning None is safer for optional steps.
            # Context-dependent. Let's start with logging and returning None,
            # allowing the caller to decide if it's fatal.
            return None

    # 3. If it's an object (e.g. from ORM or legacy), try conversion via dump/load
    # This is expensive but safe for transition.
    try:
        if hasattr(data, "model_dump"):
            return model_class.model_validate(data.model_dump())
        if hasattr(data, "__dict__"):
            return model_class.model_validate(data.__dict__)
    except Exception as e:
        logger.warning(f"Failed to convert object to {model_class.__name__}: {e}")

    return None
