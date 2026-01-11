"""API Error schema definition."""
from typing import Any

from pydantic import BaseModel


class APIError(BaseModel):
    """Standardized API Error response model.

    Enforces the 'API & Error Contract' defined in flutterpromptohje.md.
    """

    error_code: str
    message: str
    details: Any | None = None
