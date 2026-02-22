"""Strict DTO for State Presenter output."""

from typing import Any

from pydantic import BaseModel, ConfigDict


class SystemStatus(BaseModel):
    """System status and audit metadata."""

    execution_id: str
    workflow_id: str
    workflow_name: str
    timestamp: str | None
    version: str = "2.0"
    reasoning_chain_active: bool
    database_source: str
    environment: str

    # Optional Security context
    uhka_havaittu: bool | None = None
    riski_taso: str | None = None
    logiikka_validi: bool | None = None

    # Identity
    organization_id: str | None = None
    user_id: str | None = None

    model_config = ConfigDict(frozen=True, strict=True)


class StatePresentation(BaseModel):
    """Refined state presentation for UI consumption."""

    System_Status: SystemStatus
    Report: dict[str, Any]  # Keeping Report as dict for now as it's highly dynamic, but contained
    Raw_Steps: dict[str, Any]  # Keeping Raw Steps as dict (debug data)

    model_config = ConfigDict(frozen=True, strict=True)
