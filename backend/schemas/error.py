"""API Error schema definition (RFC 7807 Problem Details).

Enforces the 'API & Error Contract' defined in flutterpromptohje.md.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProblemDetail(BaseModel):
    """RFC 7807 Problem Details response model.

    This is the ONLY error response format used by the API.

    Fields:
        type: URI identifying the error type (links to documentation).
        title: Human-readable error title (from error_code).
        status: HTTP status code.
        detail: Specific error message for this occurrence.
        instance: Optional URI for this specific error.
        extensions: Additional context (step_id, cause, etc.).

    Example:
        {
            "type": "https://api.quorum.fi/errors/execution-not-found",
            "title": "Execution Not Found",
            "status": 404,
            "detail": "Execution 'abc-123' not found.",
            "instance": "/executions/abc-123"
        }
    """

    type: str = Field(
        ...,
        description="URI identifying the error type",
        json_schema_extra={"example": "https://api.quorum.fi/errors/execution-not-found"},
    )
    title: str = Field(
        ...,
        description="Human-readable error title",
        json_schema_extra={"example": "Execution Not Found"},
    )
    status: int = Field(
        ...,
        description="HTTP status code",
        json_schema_extra={"example": 404},
    )
    detail: str = Field(
        ...,
        description="Specific error message for this occurrence",
        json_schema_extra={"example": "Execution 'abc-123' not found."},
    )
    instance: str | None = Field(
        default=None,
        description="URI identifying this specific error occurrence",
        json_schema_extra={"example": "/executions/abc-123"},
    )
    extensions: dict[str, Any] | None = Field(
        default=None,
        description="Additional context (step_id, cause, agent, etc.)",
    )

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("type", "title", "detail")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @property
    def error_code(self) -> str:
        """Extract error code from type URI for frontend localization.

        Example:
            "https://api.quorum.fi/errors/execution-not-found"
            -> "EXECUTION_NOT_FOUND"
        """
        slug = self.type.split("/")[-1]
        return slug.replace("-", "_").upper()


# Legacy alias for backward compatibility during migration
APIError = ProblemDetail
