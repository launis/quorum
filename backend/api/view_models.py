
from pydantic import BaseModel, Field


class AssessmentViewModel(BaseModel):
    """Server-Driven UI View Model for the Execution Monitor."""

    session_id: str
    status_label: str = Field(..., json_schema_extra={"x-ui-label": "Status"})
    ui_variant: str  # internal UI flag (success, warning, error, info)
    final_score: int | None = Field(None, json_schema_extra={"x-ui-label": "Score"})
    status_message: str = Field(..., json_schema_extra={"x-ui-label": "Message"})
    show_warning_banner: bool = False
