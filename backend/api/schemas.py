from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict, AliasChoices

class ExecutionResponse(BaseModel):
    """API DTO for Workflow Execution Details.
    
    Standardizes the output format regardless of the underlying database schema.
    """
    
    execution_id: str = Field(..., validation_alias=AliasChoices("id", "execution_id"))
    start_time: datetime | None = Field(None, validation_alias=AliasChoices("started_at", "timestamp", "start_time"))
    status: str = Field(default="unknown")
    
    # Workflow Context
    workflow_id: Optional[str] = None
    workflow_name: Optional[str] = None
    
    # Data
    inputs: Dict[str, Any] = Field(default_factory=dict)
    result: Dict[str, Any] = Field(default_factory=dict, validation_alias=AliasChoices("results", "result"))
    
    # Expanded Visibility
    audit_results: Dict[str, Any] = Field(default_factory=dict)
    usage: Dict[str, Any] = Field(default_factory=dict)
    execution_trace: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Metadata
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        extra="allow",  # Include any other fields from DB automatically
        json_encoders={datetime: lambda v: v.isoformat()}
    )
