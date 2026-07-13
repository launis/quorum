"""Scoring and penalty evaluation DTOs."""

from typing import Any

from pydantic import ConfigDict

from backend_v2.models.dtos.base import BaseDTO
from backend_v2.models.dtos.report.matrix import MatrixFieldsMixin


class PenaltyData(BaseDTO):
    """Scoring penalty application metrics details."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    penalty_type: str
    impact: float


class ScoreSummaryData(BaseDTO):
    """Consolidated summary metrics schema."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    total_score: float = 0.0
    normalized_score: float = 0.0


class ScoringReportData(MatrixFieldsMixin):
    """Scoring engine step output payload model."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    penalties_applied: list[PenaltyData] | None = None
    score_summary: ScoreSummaryData | None = None


class TraceScoringPayloadDTO(BaseDTO):
    """Strict hydration schema for extracting scoring results in BlueprintTransformer."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    total_score: float | None = None
    final_score: float | None = None
    normalized_score: float | None = None
    penalties_applied: list[Any] | None = None
    aggregation_status: str | None = None


class ScoreItem(BaseDTO):
    """A normalized dimension score evaluation object."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    score: float
    reasoning: str
    label: str
