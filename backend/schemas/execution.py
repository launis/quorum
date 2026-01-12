from typing import Any, Optional

from pydantic import BaseModel, Field


class ExecutionRequest(BaseModel):
    """Strictly typed payload for execution requests.
    
    Replaces manual form parsing with a cleaner Pydantic model.
    """
    
    project_id: str = Field(..., description="The ID of the workflow/project to execute (maps to workflow_id).")
    description: Optional[str] = Field(None, description="Optional description for this execution run.")
    settings: dict[str, Any] = Field(default_factory=dict, description="Input parameters/settings for the execution.")
