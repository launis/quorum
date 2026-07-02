"""Evaluation and Validation Domain Models.

This module contains models related to evaluation matrices and structure validation.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Self

from pydantic import Field, field_validator, model_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace
from backend_v2.models.domain.integrity import CitationAudit
from backend_v2.models.domain.judge import DimensionResultItem, JudgeScoreCard

logger = logging.getLogger(__name__)


class EvaluationCriterion(V2CoreBase):
    """A single criterion in an evaluation matrix.

    Attributes:
        id: Unique identifier.
        label: Human-readable label.
        description: Description of the criterion.
        instruction: Specific instructions for evaluation.
        anchors: Scoring anchors mapping.
        weight: Importance weight.
    """

    id: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    description: str | None = None
    instruction: str | None = None
    anchors: dict[str, str] | None = None
    weight: float = Field(default=1.0, ge=0.0)


class EvaluationMatrixConfig(V2CoreBase):
    """Configuration for an Evaluation Matrix.

    Attributes:
        id: Unique identifier for the matrix.
        name: Human-readable name.
        description: Optional description.
        criteria: List of evaluation criteria.
    """

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    description: str | None = None
    criteria: list[EvaluationCriterion] = Field(
        ..., min_length=1, json_schema_extra={"x-ui-group": "Evaluation Criteria"}
    )


class EvaluationResult(ReasoningTrace):
    """Generic container for evaluation results.

    Attributes:
        matrix_id: ID of the evaluated matrix.
        timestamp: Evaluation timestamp.
        total_score: Total score.
        final_verdict: Final verdict.
        dimensions: Evaluation dimensions.
        scale_min: Minimum possible score.
        scale_max: Maximum possible score.
        score_cards: List of score cards if this results aggregates multiple.
        citation_snippets: Direct quotes from the source text supporting the verdict.
        penalties: List of penalty keys applied.
        integrity_audit: Integrity audit results for citations.
    """

    matrix_id: str = Field(..., min_length=1)
    timestamp: datetime
    total_score: float = Field(..., description="Total score.")
    final_verdict: str = Field(..., min_length=1, description="Final verdict.")
    dimensions: list[DimensionResultItem] = Field(..., min_length=1, description="Evaluation dimensions.")

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

    integrity_audit: CitationAudit | None = Field(
        default=None,
        description="Integrity audit results for citations.",
        json_schema_extra={"x-ui-label": "Integrity Audit"},
    )

    @field_validator("timestamp", mode="before")
    @classmethod
    def parse_datetime(cls, v: Any) -> Any:
        """Parse datetime string to object.

        Args:
            v: Input value.

        Returns:
            Parsed datetime or original value.
        """
        if isinstance(v, str):
            # Parse explicit ISO strings in strict mode
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        return v

    @model_validator(mode="after")
    def validate_scores_range(self) -> Self:
        """Validate that scale_min is less than scale_max.

        Returns:
            The validated instance.

        Raises:
            AppException: If scale_min is greater than or equal to scale_max.
        """
        if self.scale_min >= self.scale_max:
            msg = "scale_min must be strictly less than scale_max."
            logger.error("[EvaluationModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return self


class ValidationResult(V2CoreBase):
    """Result of the structure verification (Hook).

    Attributes:
        is_valid: Is the structure valid?
        errors: Validation errors.
    """

    is_valid: bool = Field(..., description="Is the structure valid?", json_schema_extra={"x-ui-label": "Is Valid"})
    errors: list[str] = Field(
        default_factory=list, description="Validation errors.", json_schema_extra={"x-ui-label": "Errors"}
    )

    @model_validator(mode="after")
    def validate_logic(self) -> Self:
        """Validate that invalid results contain errors.

        Returns:
            The validated instance.

        Raises:
            AppException: If is_valid is False but no errors are provided.
        """
        if not self.is_valid and not self.errors:
            msg = "Invalid result must have errors."
            logger.error("[EvaluationModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return self
