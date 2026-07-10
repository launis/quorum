"""Shared DTOs for the reporting engine."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetailsDTO(BaseModel):
    """Details of a system error during execution."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    error_code: Annotated[str, Field(description="Standardized error code, e.g., LLM_TIMEOUT")]
    message: Annotated[str, Field(description="Technical error message or stack trace")]
