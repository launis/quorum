"""Performativity Agent Domain Models.

This module contains the schemas for the Performativity/Detector Agent,
including linguistics analysis and heuristics.
"""

from __future__ import annotations

import logging

from pydantic import Field, field_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.enums import LaxAuthenticityLevel

logger = logging.getLogger(__name__)


class PerformativityInput(V2CoreBase):
    """Strict input schema for PerformativityDetectorAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.
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
    """Heuristic check for performativity."""

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
    """Pre-Mortem Analysis results."""

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
    """(Renamed for schema clarity vs Detector) - Output from Performativity component."""

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
        """Enforce strict authenticity score boundaries between 1.0 and 3.0."""
        if not (1.0 <= v <= 3.0):
            raise ValueError("authenticity_score must be between 1.0 and 3.0 inclusive")
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
    """Performativity DTO (Content Only)."""

    performativity_analysis: PerformativityAnalysis = Field(
        ...,
        description="Performativity audit result.",
        json_schema_extra={"x-ui-label": "Performativity Audit"},
    )


class PerformativityOutput(PerformativityDTO, ReasoningTrace):
    """Output schema for the Performativity/Detector Agent."""


class PerformativePattern(V2CoreBase):
    """A single detected performative pattern."""

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
    """Result of the linguistics analysis (Hook)."""

    performative_patterns: list[PerformativePattern] = Field(
        default_factory=list,
        description="Detected patterns.",
        json_schema_extra={"x-ui-label": "Performative Patterns"},
    )
