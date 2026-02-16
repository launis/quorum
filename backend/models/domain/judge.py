"""Judge Agent Domain Models.

This module contains the schemas for the Judge Agent,
including scorecards and dimension results.
"""


from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.models.domain.base import ReasoningTrace


class DimensionResultItem(BaseModel):
    """Result for a single dimension."""

    dimension_id: str = Field(
        ...,
        description="ID of the dimension (e.g., 'analysis').",
        json_schema_extra={"x-ui-label": "Dimension ID"},
    )
    dimension_label: str = Field(
        default="",
        description="Human-readable label.",
        json_schema_extra={"x-ui-label": "Dimension"},
    )
    score: int | float = Field(
        ...,
        description="Numerical score.",
        json_schema_extra={"x-ui-label": "Score"},
    )
    reasoning: str = Field(
        ...,
        description="Justification for the score.",
        json_schema_extra={"x-ui-label": "Reasoning"},
    )

    model_config = ConfigDict(extra="forbid", strict=True)

    @field_validator("dimension_id", "dimension_label", "reasoning")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: int | float) -> int | float:
        if v < 0:
            raise ValueError("Score cannot be negative.")
        return v


class JudgeScoreCard(BaseModel):
    """Summary of a single judgment step."""

    agent_name: str = Field(
        ...,
        description="Name of the judge (e.g. 'Standard Judge').",
        json_schema_extra={"x-ui-label": "Judge"},
    )
    total_score: float = Field(
        ...,
        description="Total score (0-5).",
        json_schema_extra={"x-ui-label": "Total Score"},
    )
    max_score: int = Field(
        ...,
        description="Max scale.",
        json_schema_extra={"x-ui-label": "Max Score"},
    )
    verdict: str = Field(
        ...,
        description="Short verdict or summary.",
        json_schema_extra={"x-ui-label": "Verdict"},
    )
    dimensions: list[DimensionResultItem] = Field(
        default_factory=list,
        description="Radar chart data.",
        json_schema_extra={"x-ui-label": "Dimensions"},
    )
    scale_min: float = Field(
        ...,
        description="Minimum possible score.",
        json_schema_extra={"x-ui-label": "Scale Min"},
    )
    scale_max: float = Field(
        ...,
        description="Maximum possible score.",
        json_schema_extra={"x-ui-label": "Scale Max"},
    )

    @field_validator("agent_name", "verdict")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @model_validator(mode="after")
    def validate_scores(self) -> "JudgeScoreCard":
        if self.scale_min >= self.scale_max:
             raise ValueError("scale_min must be less than scale_max.")
        
        if not (self.scale_min <= self.total_score <= self.scale_max):
             # Allow small floating point epsilon if needed, but strict is better for now.
             raise ValueError(f"total_score {self.total_score} is out of range [{self.scale_min}, {self.scale_max}].")
        return self


class JudgeOutput(ReasoningTrace):
    """Output schema for the Judge Agent."""

    score_card: JudgeScoreCard = Field(
        ...,
        description="Final scorecard.",
        json_schema_extra={"x-ui-label": "Scorecard"},
    )
    scale_min: float = Field(
        ...,
        description="Minimum possible score (usually 0 or 1).",
        json_schema_extra={"x-ui-label": "Scale Min"},
    )
    scale_max: float = Field(
        ...,
        description="Maximum possible score (usually 5).",
        json_schema_extra={"x-ui-label": "Scale Max"},
    )

    model_config = ConfigDict(frozen=True, strict=True)


class ScoringResult(BaseModel):
    """Result of the scoring logic (Hook)."""
    total_score: float = Field(..., description="Total aggregated score.", json_schema_extra={"x-ui-label": "Total Score"})
    calculated_average: float = Field(..., description="Calculated average.", json_schema_extra={"x-ui-label": "Average Score"})
    score_summary: str = Field(..., description="Summary text.", json_schema_extra={"x-ui-label": "Summary"})
    penalties_applied: list[str] = Field(
        default_factory=list,
        description="List of penalties applied.",
        json_schema_extra={"x-ui-label": "Penalties"}
    )

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("score_summary")
    @classmethod
    def validate_summary(cls, v: str) -> str:
        if not v or not v.strip():
             raise ValueError("Score summary cannot be empty.")
        return v.strip()
