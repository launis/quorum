"""Evaluation and Validation Domain Models.

This module contains models related to evaluation matrices and structure validation.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.models.domain.base import ReasoningTrace
from backend.models.domain.judge import DimensionResultItem, JudgeScoreCard


class EvaluationCriterion(BaseModel):
    """A single criterion in an evaluation matrix."""
    id: str
    label: str
    description: str | None = None
    instruction: str | None = None
    anchors: dict[str, str] | None = None
    weight: float = 1.0

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "label")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("weight")
    @classmethod
    def validate_positive(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Weight cannot be negative.")
        return v


class EvaluationMatrixConfig(BaseModel):
    """Configuration for an Evaluation Matrix."""
    id: str
    name: str
    description: str | None = None
    criteria: list[EvaluationCriterion] = Field(default_factory=list)

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "name")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class EvaluationResult(ReasoningTrace):
    """Generic container for evaluation results."""
    matrix_id: str
    timestamp: datetime
    total_score: float = Field(..., description="Total score.")
    final_verdict: str = Field(..., description="Final verdict.")
    dimensions: list[DimensionResultItem]

    # Scale Metadata (Added for XAI/BFF Compatibility)
    scale_min: float = Field(default=0.0, description="Minimum possible score.")
    scale_max: float = Field(default=5.0, description="Maximum possible score.")

    # Container for aggregated results (if applicable)
    score_cards: list[JudgeScoreCard] | None = Field(
        default=None,
        description="List of score cards if this result aggregates multiple."
    )

    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        if isinstance(v, str):
            # Fallback for ISO strings in strict mode
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("matrix_id", "final_verdict")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("total_score", "scale_min", "scale_max")
    @classmethod
    def validate_scores(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Score cannot be negative.")
        return v


class ValidationResult(BaseModel):
    """Result of the structure verification (Hook)."""
    is_valid: bool = Field(..., description="Is the structure valid?", json_schema_extra={"x-ui-label": "Is Valid"})
    errors: list[str] = Field(
        default_factory=list,
        description="Validation errors.",
        json_schema_extra={"x-ui-label": "Errors"}
    )

    model_config = ConfigDict(frozen=True, strict=True)

    @model_validator(mode="after")
    def validate_logic(self) -> "ValidationResult":
        if not self.is_valid and not self.errors:
            raise ValueError("Invalid result must have errors.")
        return self
