from typing import Any

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    """Structured Audit Log Event."""

    id: str
    timestamp: str
    actor_uid: str
    action: str
    organization_id: str | None = None
    target_uid: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
