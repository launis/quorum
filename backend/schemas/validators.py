"""Validation Helper Module.

Reusable validators and structure checkers for Pydantic models.
Previously logic located in backend/hooks/validation.py.
"""

import logging

logger = logging.getLogger(__name__)


from typing import Any
from backend.exceptions import AppException, ErrorCodes
from fastapi import status

def validate_content_structure(
    history_text: str | None, product_text: str | None, reflection_text: str | None, min_chars: int = 100
) -> None:
    """Verifies that the core content inputs have sufficient length for analysis.

    Fail Fast: Raises AppException if validation fails.

    Args:
        history_text: The conversation history text.
        product_text: The product text.
        reflection_text: The reflection text.
        min_chars: Minimum character count required per field.

    Raises:
        AppException: If content is missing or too short (INVALID_JSON_PAYLOAD).
    """
    errors = []
    inputs = {"history_text": history_text, "product_text": product_text, "reflection_text": reflection_text}

    for key, text in inputs.items():
        if not text:
             errors.append(f"Field '{key}' is missing or empty.")
        elif len(text) < min_chars:
            errors.append(f"Input '{key}' is too short ({len(text)} < {min_chars} chars).")

    if errors:
        raise AppException(
            message="Content validation failed.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details={
                "error_code": ErrorCodes.INVALID_JSON_PAYLOAD,
                "validation_errors": errors
            }
        )
