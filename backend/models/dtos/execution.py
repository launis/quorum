from typing import Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, RootModel

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

class ExecutionRequest(BaseModel):
    """Request payload for creating an execution."""
    workflowId: str
    organizationId: str | None = None
    inputs: Dict[str, Any] = {}
    json_payload: str | None = None # For multipart/form-data parsing hint

class ExecutionResponse(BaseModel):
    """Response for execution creation/status."""
    id: str
    workflow_id: str
    status: str
    started_at: datetime
    completed_at: datetime | None = None
    results: Dict[str, Any] = {}
    inputs: Dict[str, Any] = {}
    user_id: str
    organization_id: str | None = None
    workflow_name: str | None = None
    # Extra fields for response convenience
    start_time: datetime | None = None

    class Config:
        populate_by_name = True

class ExecutionRawResponse(BaseModel):
    """Response for raw execution data dump."""
    id: str
    workflow_id: str | None
    status: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_seconds: float | None = None
    inputs: Dict[str, Any] = {}
    results: Dict[str, Any] = {}
    state: Dict[str, Any] = {}
    user_id: str | None
    agent_outputs: Dict[str, Any] = {}
    hook_outputs: Dict[str, Any] = {}
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
    root: Dict[str, Any]
