"""Judge Agent Domain Models.

This module contains the schemas for the Judge Agent,
including scorecards and dimension results.
"""

import logging
from typing import Any

from pydantic import Field, model_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.archivist import ArchivistOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.causal import CausalOutput
from backend_v2.models.domain.falsifier import FalsifierOutput
from backend_v2.models.domain.guard import GuardOutput
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.domain.overseer import OverseerOutput
from backend_v2.models.domain.performativity import PerformativityOutput
from backend_v2.models.domain.profiler import ProfilerOutput

logger = logging.getLogger(__name__)


class JudgeInput(V2CoreBase):
    """Strict Input Schema for Judge Agent (Phase 8).

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are encapsulated dynamically.
    """

    # Context / inputs
    chat_log: str = Field(
        ...,
        min_length=1,
        description="The mandatory conversation history to evaluate.",
        json_schema_extra={"x-ui-label": "Chatlog"},
    )

    # Preceding Agents (Critics) - Strictly Typed via Forward Refs
    step_analyst: AnalystOutput | LogicianOutput | None = Field(None, description="Analyst or Logician outputs.")
    step_profiler: ProfilerOutput | None = Field(None, description="Profiler Output.")
    step_archivist: ArchivistOutput | None = Field(None, description="Archivist Output.")
    step_logician: LogicianOutput | None = Field(None, description="Logician Output.")
    step_falsifier: FalsifierOutput | None = Field(None, description="Falsifier Output.")
    step_causal: CausalOutput | None = Field(None, description="Causal Output.")
    step_detector: PerformativityOutput | None = Field(None, description="Detector Output.")
    step_overseer: OverseerOutput | None = Field(None, description="Overseer Output.")

    step_guard: GuardOutput | None = Field(None, description="Guard Output.")
    last_reasoning_trace: str | None = Field(None, description="Previous reasoning trace.")

    dynamic_inputs: dict[str, Any] = Field(
        default_factory=dict, description="Structured dictionary for dynamic inputs."
    )


class DimensionResultItem(V2CoreBase):
    """Result for a single dimension."""

    dimension_id: str = Field(
        ...,
        min_length=1,
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
        ge=0,
        description="Numerical score.",
        json_schema_extra={"x-ui-label": "Score"},
    )
    reasoning: str = Field(
        ...,
        min_length=1,
        description="Justification for the score.",
        json_schema_extra={"x-ui-label": "Reasoning"},
    )


class JudgeScoreCard(V2CoreBase):
    """Summary of a single judgment step."""

    agent_name: str = Field(
        ...,
        min_length=1,
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
        min_length=1,
        description="Short verdict or summary.",
        json_schema_extra={"x-ui-label": "Verdict"},
    )
    dimensions: list[DimensionResultItem] = Field(
        ...,
        min_length=1,
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

    @model_validator(mode="after")
    def validate_scores(self) -> JudgeScoreCard:
        if self.scale_min >= self.scale_max:
            msg = "scale_min must be less than scale_max."
            logger.error("[JudgeModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ValueError(msg)

        if not (self.scale_min <= self.total_score <= self.scale_max):
            msg = f"total_score {self.total_score} is out of range [{self.scale_min}, {self.scale_max}]."
            logger.error("[JudgeModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ValueError(msg)
        return self


class JudgeDTO(ReasoningTraceDTO):
    """Judge DTO (Content Only)."""

    matrix_id: str = Field(
        ...,
        description="ID of the evaluation matrix used.",
        json_schema_extra={"x-ui-label": "Matrix ID"},
    )
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
    critical_findings: list[str] = Field(
        default_factory=list,
        description="Critical issues identified.",
        json_schema_extra={"x-ui-label": "Critical Findings"},
    )


class JudgeOutput(JudgeDTO, ReasoningTrace):
    """Output schema for the Judge Agent."""


class ScoringResult(V2CoreBase):
    """Result of the scoring logic (Hook)."""

    total_score: float = Field(
        ..., description="Total aggregated score.", json_schema_extra={"x-ui-label": "Total Score"}
    )
    calculated_average: float = Field(
        ..., description="Calculated average.", json_schema_extra={"x-ui-label": "Average Score"}
    )
    score_summary: str = Field(
        ..., min_length=1, description="Summary text.", json_schema_extra={"x-ui-label": "Summary"}
    )
    penalties_applied: list[str] = Field(
        default_factory=list, description="List of penalties applied.", json_schema_extra={"x-ui-label": "Penalties"}
    )
