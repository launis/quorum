"""Coach Agent Domain Models.

This module contains the schemas for the Coach Agent,
including coaching plans and bibliography.
"""

# Import JudgeOutput for strict type checking if possible, otherwise use Dict
# To avoid potential circular imports (though judge doesn't import coach), we can use forward refs or just imports
# But let's check if we can import JudgeOutput from backend.models.domain.judge
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.models.domain.base import ReasoningTrace, ReasoningTraceDTO

if TYPE_CHECKING:
    pass


class CoachInput(BaseModel):
    """Strict input schema for CoachAgent."""

    history_text: str = Field(..., description="Chat history.")
    product_text: str | None = Field(default=None, description="Product context.")
    reflection_text: str | None = Field(default=None, description="User reflection.")
    step_judge: dict[str, Any] | Any | None = Field(
        default=None, description="The Verdict from Judge Agent.", json_schema_extra={"x-ui-label": "Judge Verdict"}
    )
    step_judge_cognitive: dict[str, Any] | Any | None = Field(
        default=None, description="The Verdict from Cognitive Judge Agent.", json_schema_extra={"x-ui-label": "Cognitive Verdict"}
    )
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    # Allow extra fields because Coach might receive step_judge, step_judge_cognitive etc.
    # Logic in agent iterates keys.
    model_config = ConfigDict(frozen=True, extra="allow")

    @field_validator("history_text")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("History text cannot be empty.")
        return v.strip()

    @model_validator(mode="after")
    def validate_judge_presence(self) -> 'CoachInput':
        if not self.step_judge and not self.step_judge_cognitive:
            raise ValueError("CoachAgent requires at least one judge input (step_judge or step_judge_cognitive).")
        return self


class BibliographyItem(BaseModel):
    """A single bibliographic reference."""

    source_id: str = Field(..., description="Unique source ID.", json_schema_extra={"x-ui-label": "Source ID"})
    title: str = Field(..., description="Title of the source.", json_schema_extra={"x-ui-label": "Title"})
    url: str | None = Field(default=None, description="URL if available.", json_schema_extra={"x-ui-label": "URL"})
    snippet: str | None = Field(
        default=None, description="Relevant snippet.", json_schema_extra={"x-ui-label": "Snippet"}
    )

    model_config = ConfigDict(frozen=True)

    @field_validator("source_id", "title")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class BibliographyResult(BaseModel):
    """Result of the bibliography generation (Hook)."""

    references: list[BibliographyItem] = Field(
        default_factory=list, description="List of references.", json_schema_extra={"x-ui-label": "References"}
    )

    model_config = ConfigDict(frozen=True)


class CoachingPlanDTO(ReasoningTraceDTO):
    """DTO for Coaching Plan (Content Only)."""

    actionable_steps: list[str] = Field(
        ...,
        description="Concrete steps for improvement.",
        json_schema_extra={"x-ui-label": "Actionable Steps"},
    )
    bibliography: list[BibliographyItem] = Field(
        ...,
        description="Recommended reading.",
        json_schema_extra={"x-ui-label": "References"},
    )
    focus_areas: list[str] = Field(
        ...,
        description="Key areas to focus on.",
        json_schema_extra={"x-ui-label": "Focus Areas"},
    )
    model_config = ConfigDict(frozen=True)

    @field_validator("actionable_steps", "focus_areas")
    @classmethod
    def validate_list_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("List cannot be empty.")
        # Validate individual items
        cleaned = [item.strip() for item in v if item and item.strip()]
        if not cleaned:
            raise ValueError("List cannot contain only empty strings.")
        return cleaned


class CoachingPlan(CoachingPlanDTO, ReasoningTrace):
    """Output schema for the Coach Agent (Domain Model)."""

    model_config = ConfigDict(frozen=True)
