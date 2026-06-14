"""Performativity Agent Domain Models.

This module contains the schemas for the Performativity/Detector Agent,
including linguistics analysis and heuristics.
"""

from __future__ import annotations

import logging

from fastapi import status
from pydantic import Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.enums import LaxAuthenticityLevel

logger = logging.getLogger(__name__)


class PerformativityInput(V2CoreBase):
    """Strict input schema for PerformativityDetectorAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.

    Attributes:
        chat_log: The mandatory conversation history.
        step_analyst: Analyst or Logician outputs.
        last_reasoning_trace: Previous reasoning trace.
    """

    chat_log: str = Field(
        ...,
        min_length=1,
        description="The mandatory conversation history.",
        json_schema_extra={"x-ui-label": "Chatlog"},
    )
    step_analyst: AnalystOutput | LogicianOutput | None = Field(None, description="Analyst or Logician outputs.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")


class PerformativityHeuristic(V2CoreBase):
    """Heuristic check for performativity.

    Attributes:
        heuristic_name: Heuristic name.
        flag_raised: Flag raised.
        description: Description.
    """

    heuristic_name: str = Field(
        ...,
        min_length=1,
        description="Heuristic name.",
        json_schema_extra={"x-ui-label": "Heuristic"},
    )
    flag_raised: bool = Field(
        ...,
        description="Flag raised?",
        json_schema_extra={"x-ui-label": "Flag Raised"},
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Description.",
        json_schema_extra={"x-ui-label": "Description"},
    )


class PreMortemAnalysis(V2CoreBase):
    """Pre-Mortem Analysis results.

    Attributes:
        performed: Was Pre-Mortem performed?
        weak_signals: Detected weak signals.
    """

    performed: bool = Field(
        ...,
        description="Was Pre-Mortem performed?",
        json_schema_extra={"x-ui-label": "Performed"},
    )
    weak_signals: list[str] = Field(
        ...,
        min_length=1,
        description="Detected weak signals.",
        json_schema_extra={"x-ui-label": "Weak Signals"},
    )


class PerformativityAnalysis(V2CoreBase):
    """Output from Performativity component.

    (Renamed for schema clarity vs Detector).

    Attributes:
        performativity_heuristics: Heuristics check.
        pre_mortem_analysis: Pre-Mortem analysis.
        authenticity_assessment: Authenticity assessment.
        authenticity_score: Numeric authenticity score.
        description_key: Localization key.
        description: Localized description.
    """

    performativity_heuristics: list[PerformativityHeuristic] = Field(
        ...,
        min_length=1,
        description="Heuristics check.",
        json_schema_extra={"x-ui-label": "Heuristics"},
    )
    pre_mortem_analysis: PreMortemAnalysis = Field(
        ...,
        description="Pre-Mortem analysis.",
        json_schema_extra={"x-ui-label": "Pre-Mortem"},
    )
    authenticity_assessment: LaxAuthenticityLevel = Field(
        ...,
        description="Authenticity assessment.",
        json_schema_extra={"x-ui-label": "Authenticity Assessment"},
    )
    authenticity_score: float = Field(
        ...,
        description=(
            "Numeric authenticity score (1.0 to 3.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 2.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Authenticity Score"},
    )

    @field_validator("authenticity_score")
    @classmethod
    def validate_authenticity_score(cls, v: float) -> float:
        """Enforce strict authenticity score boundaries between 1.0 and 3.0.

        Ensures that the output adheres to the configured range.

        Args:
            v: The authenticity score to validate.

        Returns:
            The validated authenticity score.

        Raises:
            AppException: If the score is outside the range [1.0, 3.0].
        """
        if not (1.0 <= v <= 3.0):
            raise AppException(
                message="authenticity_score must be between 1.0 and 3.0 inclusive",
                status_code=status.HTTP_400_BAD_REQUEST,
                details={"error_code": ErrorCodes.VALIDATION_FAILED.value},
            )
        return v

    description_key: str = Field(
        default="authenticity_desc",
        description="Localization key.",
    )
    description: str = Field(
        default="TBD",
        min_length=1,
        description="Localized description.",
        json_schema_extra={"x-ui-label": "Description"},
    )


class PerformativityDTO(ReasoningTraceDTO):
    """Performativity DTO (Content Only).

    Attributes:
        performativity_analysis: Performativity audit result.
    """

    performativity_analysis: PerformativityAnalysis = Field(
        ...,
        description="Performativity audit result.",
        json_schema_extra={"x-ui-label": "Performativity Audit"},
    )


class PerformativityOutput(PerformativityDTO, ReasoningTrace):
    """Output schema for the Performativity/Detector Agent.

    Attributes:
        No additional attributes.
    """


class PerformativePattern(V2CoreBase):
    """A single detected performative pattern.

    Attributes:
        pattern_id: ID of the pattern.
        detected_phrase: The exact phrase detected.
        category: Category of the pattern.
    """

    pattern_id: str = Field(
        ..., min_length=1, description="ID of the pattern.", json_schema_extra={"x-ui-label": "Pattern ID"}
    )
    detected_phrase: str = Field(
        ..., min_length=1, description="The exact phrase detected.", json_schema_extra={"x-ui-label": "Detected Phrase"}
    )
    category: str = Field(
        ..., min_length=1, description="Category of the pattern.", json_schema_extra={"x-ui-label": "Category"}
    )


class LinguisticsResult(V2CoreBase):
    """Result of the linguistics analysis (Hook).

    Attributes:
        performative_patterns: Detected patterns.
    """

    performative_patterns: list[PerformativePattern] = Field(
        default_factory=list,
        description="Detected patterns.",
        json_schema_extra={"x-ui-label": "Performative Patterns"},
    )
