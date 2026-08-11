"""Judge Agent Domain Models.

This module contains the schemas for the Judge Agent,
including scorecards and dimension results.
"""

import logging
from typing import Annotated, Any

from pydantic import ConfigDict, Field, field_validator, model_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.archivist import ArchivistOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.causal import CausalOutput
from backend_v2.models.domain.falsifier import FalsifierOutput
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.domain.overseer import OverseerOutput
from backend_v2.models.domain.performativity import PerformativityOutput
from backend_v2.models.domain.profiler import ProfilerOutput
from backend_v2.models.domain.security import InputProcessingOutputDTO

logger = logging.getLogger(__name__)


class JudgeInput(V2CoreBase):
    """Strict Input Schema for Judge Agent (Phase 8).

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are encapsulated dynamically.

    Attributes:
        chat_log: The mandatory conversation history to evaluate.
        step_analyst: Analyst or Logician outputs.
        step_profiler: Profiler Output.
        step_archivist: Archivist Output.
        step_logician: Logician Output.
        step_falsifier: Falsifier Output.
        step_causal: Causal Output.
        step_detector: Detector Output.
        step_overseer: Overseer Output.
        step_input_processing: Input Processing Output.
        last_reasoning_trace: Previous reasoning trace.
        dynamic_inputs: Structured dictionary for dynamic inputs.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    # Context / inputs
    chat_log: Annotated[
        str,
        Field(
            min_length=1,
            description="The mandatory conversation history to evaluate.",
            json_schema_extra={"x-ui-label": "Chatlog"},
        ),
    ]

    # Preceding Agents (Critics) - Strictly Typed via Forward Refs
    step_analyst: Annotated[
        AnalystOutput | LogicianOutput | None, Field(description="Analyst or Logician outputs.")
    ] = None
    step_profiler: Annotated[ProfilerOutput | None, Field(description="Profiler Output.")] = None
    step_archivist: Annotated[ArchivistOutput | None, Field(description="Archivist Output.")] = None
    step_logician: Annotated[LogicianOutput | None, Field(description="Logician Output.")] = None
    step_falsifier: Annotated[FalsifierOutput | None, Field(description="Falsifier Output.")] = None
    step_causal: Annotated[CausalOutput | None, Field(description="Causal Output.")] = None
    step_detector: Annotated[PerformativityOutput | None, Field(description="Detector Output.")] = None
    step_overseer: Annotated[OverseerOutput | None, Field(description="Overseer Output.")] = None

    step_input_processing: Annotated[InputProcessingOutputDTO | None, Field(description="Input Processing Output.")] = (
        None
    )
    last_reasoning_trace: Annotated[str | None, Field(description="Previous reasoning trace.")] = None

    dynamic_inputs: Annotated[
        dict[str, Any], Field(default_factory=dict, description="Structured dictionary for dynamic inputs.")
    ]


class DimensionResultItem(V2CoreBase):
    """Result for a single dimension.

    Attributes:
        dimension_id: ID of the dimension (e.g., 'analysis').
        dimension_label: Human-readable label.
        score: Numerical score.
        reasoning: Justification for the score.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    dimension_id: Annotated[
        str,
        Field(
            min_length=1,
            description="ID of the dimension (e.g., 'analysis').",
            json_schema_extra={"x-ui-label": "Dimension ID"},
        ),
    ]
    dimension_label: Annotated[
        str,
        Field(
            description="Human-readable label.",
            json_schema_extra={"x-ui-label": "Dimension"},
        ),
    ] = ""
    score: Annotated[
        int | float,
        Field(
            description="Numerical score.",
            json_schema_extra={"x-ui-label": "Score"},
        ),
    ]

    @field_validator("score")
    @classmethod
    def validate_score(cls, v: int | float) -> int | float:
        """Validate score >= 0.

        Args:
            v: The score to validate.

        Returns:
            The validated score.

        Raises:
            AppException: If score is less than 0 (VALIDATION_FAILED).
        """
        if v < 0:
            msg = f"score must be >= 0, got {v}"
            logger.error("[JudgeModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v

    reasoning: Annotated[
        str,
        Field(
            min_length=1,
            description="Justification for the score.",
            json_schema_extra={"x-ui-label": "Reasoning"},
        ),
    ]


class JudgeScoreCard(V2CoreBase):
    """Summary of a single judgment step.

    Attributes:
        agent_name: Name of the judge (e.g. 'Standard Judge').
        total_score: Total score (0-5).
        max_score: Max scale.
        verdict: Short verdict or summary.
        dimensions: Radar chart data.
        scale_min: Minimum possible score.
        scale_max: Maximum possible score.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    agent_name: Annotated[
        str,
        Field(
            min_length=1,
            description="Name of the judge (e.g. 'Standard Judge').",
            json_schema_extra={"x-ui-label": "Judge"},
        ),
    ]
    total_score: Annotated[
        float,
        Field(
            description="Total score (0-5).",
            json_schema_extra={"x-ui-label": "Total Score"},
        ),
    ]
    max_score: Annotated[
        int,
        Field(
            description="Max scale.",
            json_schema_extra={"x-ui-label": "Max Score"},
        ),
    ]
    verdict: Annotated[
        str,
        Field(
            min_length=1,
            description="Short verdict or summary.",
            json_schema_extra={"x-ui-label": "Verdict"},
        ),
    ]
    dimensions: Annotated[
        list[DimensionResultItem],
        Field(
            min_length=1,
            description="Radar chart data.",
            json_schema_extra={"x-ui-label": "Dimensions"},
        ),
    ]
    scale_min: Annotated[
        float,
        Field(
            description="Minimum possible score.",
            json_schema_extra={"x-ui-label": "Scale Min"},
        ),
    ]
    scale_max: Annotated[
        float,
        Field(
            description="Maximum possible score.",
            json_schema_extra={"x-ui-label": "Scale Max"},
        ),
    ]

    @model_validator(mode="after")
    def validate_scores(self) -> JudgeScoreCard:
        """Validate the score bounds.

        Returns:
            The validated scorecard instance.

        Raises:
            AppException: If scale_min >= scale_max or total_score is out of bounds (VALIDATION_FAILED).
        """
        if self.scale_min >= self.scale_max:
            msg = "scale_min must be less than scale_max."
            logger.error("[JudgeModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})

        if not (self.scale_min <= self.total_score <= self.scale_max):
            msg = f"total_score {self.total_score} is out of range [{self.scale_min}, {self.scale_max}]."
            logger.error("[JudgeModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return self


class JudgeDTO(ReasoningTraceDTO):
    """Judge DTO (Content Only).

    Attributes:
        matrix_id: ID of the evaluation matrix used.
        score_card: Final scorecard.
        scale_min: Minimum possible score.
        scale_max: Maximum possible score.
        critical_findings: Critical issues identified.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    matrix_id: Annotated[
        str,
        Field(
            description="ID of the evaluation matrix used.",
            json_schema_extra={"x-ui-label": "Matrix ID"},
        ),
    ]
    score_card: Annotated[
        JudgeScoreCard,
        Field(
            description="Final scorecard.",
            json_schema_extra={"x-ui-label": "Scorecard"},
        ),
    ]
    scale_min: Annotated[
        float,
        Field(
            description="Minimum possible score (usually 0 or 1).",
            json_schema_extra={"x-ui-label": "Scale Min"},
        ),
    ]
    scale_max: Annotated[
        float,
        Field(
            description="Maximum possible score (usually 5).",
            json_schema_extra={"x-ui-label": "Scale Max"},
        ),
    ]
    critical_findings: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Critical issues identified.",
            json_schema_extra={"x-ui-label": "Critical Findings"},
        ),
    ]


class JudgeOutput(JudgeDTO, ReasoningTrace):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Output schema for the Judge Agent."""


class ScoringResult(V2CoreBase):
    """Result of the scoring logic (Hook).

    Attributes:
        total_score: Total aggregated score.
        calculated_average: Calculated average.
        score_summary: Summary text.
        penalties_applied: List of penalties applied.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    total_score: Annotated[
        float, Field(description="Total aggregated score.", json_schema_extra={"x-ui-label": "Total Score"})
    ]
    calculated_average: Annotated[
        float, Field(description="Calculated average.", json_schema_extra={"x-ui-label": "Average Score"})
    ]
    score_summary: Annotated[
        str, Field(min_length=1, description="Summary text.", json_schema_extra={"x-ui-label": "Summary"})
    ]
    penalties_applied: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="List of penalties applied.",
            json_schema_extra={"x-ui-label": "Penalties"},
        ),
    ]
