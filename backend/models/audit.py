from typing import Any, Optional
from pydantic import BaseModel, Field

class AuditEvent(BaseModel):
    """Structured Audit Log Event."""
    id: str
    timestamp: str
    actor_uid: str
    action: str
    organization_id: Optional[str] = None
    target_uid: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
