"""Performativity Agent Domain Models.

This module contains the schemas for the Performativity/Detector Agent,
including linguistics analysis and heuristics.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.enums import AuthenticityLevel
from backend_v2.services.localization import LocalizationService


class PerformativityInput(BaseModel):
    """Strict input schema for PerformativityDetectorAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.
    """

    chat_log: str = Field(
        ..., description="The mandatory conversation history.", json_schema_extra={"x-ui-label": "Chatlog"}
    )
    step_analyst: AnalystOutput | LogicianOutput | None = Field(None, description="Analyst or Logician outputs.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    model_config = ConfigDict(frozen=True, extra="allow")


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
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @field_validator("heuristic_name", "description")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str:
        if not v or not str(v).strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[PerformativityModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return str(v).strip()


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
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @field_validator("weak_signals")
    @classmethod
    def validate_list_items(cls, v: list[str]) -> list[str]:
        if not v:
            msg = "weak_signals cannot be empty. Zero-Compromise Fail-Fast enforced."
            logger.error("[PerformativityModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        for item in v:
            if not item or not item.strip():
                msg = "weak_signals items cannot be empty."
                logger.error("[PerformativityModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
                raise AppException(
                    message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value}
                )
        return v


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
        ge=1.0,
        le=3.0,
        description=(
            "Numeric authenticity score (1.0 to 3.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 2.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Authenticity Score"},
    )
    description_key: str = Field(
        default="authenticity_desc",
        description="Localization key.",
    )
    description: str = Field(
        default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"}
    )

    @field_validator("performativity_heuristics")
    @classmethod
    def validate_heuristics_not_empty(cls, v: list[PerformativityHeuristic]) -> list[PerformativityHeuristic]:
        if not v:
            msg = "performativity_heuristics cannot be empty. Zero-Compromise Fail-Fast enforced."
            logger.error("[PerformativityModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v

    @model_validator(mode="before")
    @classmethod
    def calc_authenticity(cls, data: Any) -> Any:
        if isinstance(data, dict):
            key = data.get("description_key", "authenticity_desc")
            if not data.get("description"):
                data["description"] = LocalizationService.translate(key)

            # Strict mapping
            mapping = {AuthenticityLevel.PERFORMATIVE: 2.0, AuthenticityLevel.ORGANIC: 3.0}
            val = data.get("authenticity_assessment")

            # Cast raw string from LLM to the Enum instance to satisfy strict=True validation
            if val is not None and not isinstance(val, AuthenticityLevel):
                try:
                    val = AuthenticityLevel(val)
                    data["authenticity_assessment"] = val
                except ValueError as e:
                    msg = f"Performativity parsing failed: Invalid AuthenticityLevel '{val}'."
                    logger.error("[PerformativityModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
                    err_details = {"error_code": ErrorCodes.VALIDATION_FAILED.value}
                    raise AppException(message=msg, status_code=422, details=err_details) from e

            if data.get("authenticity_score") is None:
                if isinstance(val, AuthenticityLevel) and val in mapping:
                    data["authenticity_score"] = mapping[val]
        return data

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @field_validator("description")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str:
        if not v or not str(v).strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[PerformativityModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            from backend_v2.exceptions import AppException

            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return str(v).strip()

    @field_validator("authenticity_score")
    @classmethod
    def validate_score(cls, v: float) -> float:
        if not (1.0 <= v <= 3.0):
            msg = "Authenticity score must be between 1.0 and 3.0."
            logger.error("[PerformativityModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v


class PerformativityDTO(ReasoningTraceDTO):
    """Performativity DTO (Content Only)."""

    performativity_analysis: PerformativityAnalysis = Field(
        ...,
        description="Performativity audit result.",
        json_schema_extra={"x-ui-label": "Performativity Audit"},
    )
    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class PerformativityOutput(PerformativityDTO, ReasoningTrace):
    """Output schema for the Performativity/Detector Agent."""

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class PerformativePattern(BaseModel):
    """A single detected performative pattern."""

    pattern_id: str = Field(..., description="ID of the pattern.", json_schema_extra={"x-ui-label": "Pattern ID"})
    detected_phrase: str = Field(
        ..., description="The exact phrase detected.", json_schema_extra={"x-ui-label": "Detected Phrase"}
    )
    category: str = Field(..., description="Category of the pattern.", json_schema_extra={"x-ui-label": "Category"})

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    @field_validator("pattern_id", "detected_phrase", "category")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str:
        if not v or not str(v).strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[PerformativityModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return str(v).strip()


class LinguisticsResult(BaseModel):
    """Result of the linguistics analysis (Hook)."""

    performative_patterns: list[PerformativePattern] = Field(
        default_factory=list,
        description="Detected patterns.",
        json_schema_extra={"x-ui-label": "Performative Patterns"},
    )

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")
