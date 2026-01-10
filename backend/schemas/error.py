from typing import Any, Optional
from pydantic import BaseModel

class APIError(BaseModel):
    """
    Standardized API Error response model.
    Enforces the 'API & Error Contract' defined in flutterpromptohje.md.
    """
    error_code: str
    message: str
    details: Optional[Any] = None
