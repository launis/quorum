from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, RootModel

from backend.models.dtos.reflection import GuidedReflectionDTO


class PDFDownloadCheckResponse(BaseModel):
    """Response when checking for local PDF existence."""

    status: str
    exists: bool
    local_path: str | None = None


class PDFQueuedResponse(BaseModel):
    """Response when PDF generation is queued."""

    status: str
    message: str


class PDFCancelResponse(BaseModel):
    """Response when cancelling PDF generation."""

    status: str
    message: str


class Base64FileDTO(BaseModel):
    """Represents a file uploaded as Base64."""

    filename: str
    mime_type: str = "application/octet-stream"
    content_base64: str


class ExecutionRequestDTO(BaseModel):
    """Request payload for creating an execution (Strict Pydantic JSON)."""

    workflow_id: str
    organization_id: str | None = None
    inputs: dict[str, Base64FileDTO | str] = {}
    guided_reflection: GuidedReflectionDTO | None = None


class ExecutionResponse(BaseModel):
    """Response for execution creation/status."""

    id: str
    workflow_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    results: dict[str, Any] = {}
    inputs: dict[str, Any] = {}
    user_id: str
    organization_id: str | None = None
    workflow_name: str | None = None
    # Extra fields for response convenience
    start_time: datetime | None = None

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class ExecutionRawResponse(BaseModel):
    """Response for raw execution data dump."""

    id: str
    workflow_id: str | None
    status: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: float | None = None
    inputs: dict[str, Any] = {}
    results: dict[str, Any] = {}
    state: dict[str, Any] = {}
    user_id: str | None
    agent_outputs: dict[str, Any] = {}
    hook_outputs: dict[str, Any] = {}
    xai_report: str | None = None


class ExecutionCancelResponse(BaseModel):
    """Response when cancelling an execution."""

    id: str
    status: str
    message: str


class ExecutionDeleteResponse(BaseModel):
    """Response when deleting an execution."""

    status: str
    id: str


class DirectExecutionResponse(RootModel):
    """Response for direct workflow execution (Legacy)."""

    root: dict[str, Any]
