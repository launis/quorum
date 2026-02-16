"""Unique identifier utilities."""

import re
import uuid


def generate_unique_id(base_name: str | None = None) -> str:
    """Generates a unique, slugified identifier.

    Format: {slug}-{short_uuid}
    Example: "acme-corp-a1b2c3d4"

    If no base_name is provided, returns a full UUID.
    """
    suffix = str(uuid.uuid4())[:8]

    if not base_name:
        return str(uuid.uuid4())

    # Slugify: lowercase, replace non-alphanumeric with hyphen
    slug = re.sub(r"[^a-z0-9]+", "-", base_name.lower()).strip("-")

    if not slug:
        return str(uuid.uuid4())

    return f"{slug}-{suffix}"


def validate_identifier_format(identifier: str) -> None:
    """Validates that the identifier follows the system's strict format (slug-like).

    Format: Lowercase alphanumeric, hyphens allowed. No spaces, no special chars.

    Fail Fast: Raises AppException if format is invalid.

    Args:
        identifier (str): The ID to check.

    Raises:
        AppException: If format is invalid (INVALID_INPUT).
    """
    if not identifier:
        from backend.exceptions import AppException, ErrorCodes
        from fastapi import status
        raise AppException(
            message="Identifier cannot be empty.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"error_code": ErrorCodes.EMPTY_INPUT}
        )

    # Regex: Start/End with alphanumeric, dashes/alphanumeric in between.
    # Typically: ^[a-z0-9]+(?:-[a-z0-9]+)*$
    if not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", identifier):
         from backend.exceptions import AppException, ErrorCodes
         from fastapi import status
         raise AppException(
            message=f"Invalid identifier format: '{identifier}'. Must be lowercase alphanumeric with hyphens.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={
                "error_code": ErrorCodes.VALIDATION_FAILED,
                "invalid_identifier": identifier
            }
        )
