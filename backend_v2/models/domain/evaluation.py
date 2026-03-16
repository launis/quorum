"""Evaluation and Validation Domain Models.

This module contains models related to evaluation matrices and structure validation.
"""

import logging
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

from backend_v2.models.domain.base import ReasoningTrace
from backend_v2.models.domain.judge import DimensionResultItem, JudgeScoreCard


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
    def validate_non_empty(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v or not v.strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error(f"[EvaluationModel] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v.strip()

    @field_validator("weight")
    @classmethod
    def validate_positive(cls, v: float) -> float:
        if v < 0:
            msg = "Weight cannot be negative."
            logger.error(f"[EvaluationModel] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class EvaluationMatrixConfig(BaseModel):
    """Configuration for an Evaluation Matrix."""

    id: str
    name: str
    description: str | None = None
    criteria: list[EvaluationCriterion] = Field(
        default_factory=list, json_schema_extra={"x-ui-group": "Evaluation Criteria"}
    )

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "name")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v or not v.strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error(f"[EvaluationModel] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v.strip()


class EvaluationResult(ReasoningTrace):
    """Generic container for evaluation results."""

    matrix_id: str
    timestamp: datetime
    total_score: float = Field(..., description="Total score.")
    final_verdict: str = Field(..., description="Final verdict.")
    dimensions: list[DimensionResultItem]

    # Scale Metadata (Added for XAI/BFF Compatibility)
    scale_min: float = Field(..., description="Minimum possible score.")
    scale_max: float = Field(..., description="Maximum possible score.")

    # Container for aggregated results (if applicable)
    score_cards: list[JudgeScoreCard] | None = Field(
        default=None, description="List of score cards if this results aggregates multiple."
    )

    # Citation Support (Restored per User Request)
    citation_snippets: list[str] = Field(
        default_factory=list,
        description="Direct quotes from the source text supporting the verdict.",
        json_schema_extra={"x-ui-label": "Citations"},
    )

    # Penalties (Added for Scoring Hook / Multilingual Support)
    penalties: list[str] = Field(
        default_factory=list, description="List of penalty keys applied.", json_schema_extra={"x-ui-label": "Penalties"}
    )

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        if isinstance(v, str):
            # Fallback for ISO strings in strict mode
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("matrix_id", "final_verdict")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v or not v.strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error(f"[EvaluationModel] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v.strip()

    @model_validator(mode="after")
    def validate_scores_range(self) -> EvaluationResult:
        if self.scale_min >= self.scale_max:
            msg = "scale_min must be strictly less than scale_max."
            logger.error(f"[EvaluationModel] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED})

        if not (self.scale_min <= self.total_score <= self.scale_max):
            msg = f"Score {self.total_score} is out of valid range [{self.scale_min}, {self.scale_max}]."
            logger.error(f"[EvaluationModel] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED})

        return self


class ValidationResult(BaseModel):
    """Result of the structure verification (Hook)."""

    is_valid: bool = Field(..., description="Is the structure valid?", json_schema_extra={"x-ui-label": "Is Valid"})
    errors: list[str] = Field(
        default_factory=list, description="Validation errors.", json_schema_extra={"x-ui-label": "Errors"}
    )

    model_config = ConfigDict(frozen=True, strict=True)

    @model_validator(mode="after")
    def validate_logic(self) -> ValidationResult:
        if not self.is_valid and not self.errors:
            msg = "Invalid result must have errors."
            logger.error(f"[EvaluationModel] {ErrorCodes.VALIDATION_FAILED.name}: {msg}")
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return self
