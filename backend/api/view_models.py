from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AssessmentViewModel(BaseModel):
    """Server-Driven UI View Model for the Execution Monitor.

    Strictly typed for Server-Driven UI rendering.
    """

    session_id: str = Field(..., description="Unique Session/Execution ID")
    status_label: str = Field(..., json_schema_extra={"x-ui-label": "Status"}, description="Human readable status.")
    ui_variant: Literal["success", "warning", "error", "info", "neutral"] = Field(
        ..., description="UI styling variant key."
    )
    final_score: int | None = Field(None, json_schema_extra={"x-ui-label": "Score"}, description="0-100 Score.")
    status_message: str = Field(
        ..., json_schema_extra={"x-ui-label": "Message"}, description="Detailed status message."
    )
    show_warning_banner: bool = Field(False, description="Whether to show a warning banner.")

    model_config = ConfigDict(extra="forbid")
