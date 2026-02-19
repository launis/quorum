"""Performativity Agent Domain Models.

This module contains the schemas for the Performativity/Detector Agent,
including linguistics analysis and heuristics.
"""


from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator

from backend.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend.models.enums import AuthenticityLevel
from backend.services.localization import LocalizationService


from typing import TYPE_CHECKING
from backend.models.domain.analyst import AnalystOutput


class PerformativityInput(BaseModel):
    """Strict input schema for PerformativityDetectorAgent."""
    history_text: str = Field(..., description="Chat history to analyze.")
    step_analyst: Optional[AnalystOutput] = Field(None, description="Analyst hypotheses/timeline.")
    last_reasoning_trace: Optional[str] = Field(default=None, description="Previous reasoning trace.")
    
    model_config = ConfigDict(frozen=True, extra="ignore")


class PerformativityHeuristic(BaseModel):
    """Heuristic check for performativity."""

    heuristic_name: str = Field(
        ...,
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
        description="Description.",
        json_schema_extra={"x-ui-label": "Description"},
    )
    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("heuristic_name", "description")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()




class PreMortemAnalysis(BaseModel):
    """Pre-Mortem Analysis results."""

    performed: bool = Field(
        ...,
        description="Was Pre-Mortem performed?",
        json_schema_extra={"x-ui-label": "Performed"},
    )
    weak_signals: list[str] = Field(
        ...,
        description="Detected weak signals.",
        json_schema_extra={"x-ui-label": "Weak Signals"},
    )
    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("weak_signals")
    @classmethod
    def validate_list_items(cls, v: list[str]) -> list[str]:
         return [item.strip() for item in v if item and item.strip()]


class PerformativityAnalysis(BaseModel):
    """(Renamed for schema clarity vs Detector) - Output from Performativity component."""

    performativity_heuristics: list[PerformativityHeuristic] = Field(
        ...,
        description="Heuristics check.",
        json_schema_extra={"x-ui-label": "Heuristics"},
    )
    pre_mortem_analysis: PreMortemAnalysis = Field(
        ...,
        description="Pre-Mortem analysis.",
        json_schema_extra={"x-ui-label": "Pre-Mortem"},
    )
    authenticity_assessment: AuthenticityLevel = Field(
        ...,
        description="Authenticity assessment.",
        json_schema_extra={"x-ui-label": "Authenticity Assessment"},
    )
    authenticity_score: float = Field(
        ...,
        description="Numeric authenticity score (1-3).",
        json_schema_extra={"x-ui-label": "Authenticity Score"},
    )
    description_key: str = Field(
        default="authenticity_desc",
        description="Localization key.",
    )
    description: str = Field(default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"})

    @model_validator(mode="before")
    @classmethod
    def calc_authenticity(cls, data: Any) -> Any:
        if isinstance(data, dict):
            key = data.get("description_key", "authenticity_desc")
            if not data.get("description"):
                data["description"] = LocalizationService.translate(key)

            # Strict mapping
            mapping = {
                AuthenticityLevel.PERFORMATIVE: 2.0,
                AuthenticityLevel.ORGANIC: 3.0
            }
            val = data.get("authenticity_assessment")
            if data.get("authenticity_score") is None:
                if val:
                    try:
                        enum_val = val if isinstance(val, AuthenticityLevel) else AuthenticityLevel(val)
                        if enum_val in mapping:
                             data["authenticity_score"] = mapping[enum_val]
                    except ValueError:
                        pass
        return data

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("description")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        return v.strip() if v else v

    @field_validator("authenticity_score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        if not (1.0 <= v <= 3.0):
            raise ValueError("Authenticity score must be between 1.0 and 3.0.")
        return v


class PerformativityDTO(ReasoningTraceDTO):
    """Performativity DTO (Content Only)."""
    performativity_analysis: PerformativityAnalysis = Field(
        ...,
        description="Performativity audit result.",
        json_schema_extra={"x-ui-label": "Performativity Audit"},
    )
    model_config = ConfigDict(frozen=True, strict=False)


class PerformativityOutput(PerformativityDTO, ReasoningTrace):
    """Output schema for the Performativity/Detector Agent."""
    model_config = ConfigDict(frozen=True, strict=False)


class PerformativePattern(BaseModel):
    """A single detected performative pattern."""
    pattern_id: str = Field(..., description="ID of the pattern.", json_schema_extra={"x-ui-label": "Pattern ID"})
    detected_phrase: str = Field(..., description="The exact phrase detected.", json_schema_extra={"x-ui-label": "Detected Phrase"})
    category: str = Field(..., description="Category of the pattern.", json_schema_extra={"x-ui-label": "Category"})

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("pattern_id", "detected_phrase", "category")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class LinguisticsResult(BaseModel):
    """Result of the linguistics analysis (Hook)."""
    performative_patterns: list[PerformativePattern] = Field(
        default_factory=list,
        description="Detected patterns.",
        json_schema_extra={"x-ui-label": "Performative Patterns"}
    )

    model_config = ConfigDict(frozen=True, strict=True)
