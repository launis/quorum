"""Audit Logging Models."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuditEvent(BaseModel):
    """Structured Audit Log Event."""

    id: str
    timestamp: datetime
    actor_id: str
    action: str
    organization_id: str | None = None
    target_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "actor_id", "action")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("organization_id", "target_id")
    @classmethod
    def validate_non_empty_optional(cls, v: str | None) -> str | None:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip() if v else v
