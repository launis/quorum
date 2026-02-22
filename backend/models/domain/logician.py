"""Logician Agent Domain Models.

This module contains the schemas for the Logician Agent,
including Toulmin argumentation analysis and Walton schemes.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.models.domain.analyst import AnalystOutput
from backend.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend.models.enums import BloomLevel, StrategicDepth
from backend.services.localization import LocalizationService


class LogicianInput(BaseModel):
    """Strict input schema for LogicianAgent."""

    history_text: str = Field(..., description="Chat history to analyze.")
    step_analyst: AnalystOutput | None = Field(None, description="Analyst hypotheses/timeline.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    model_config = ConfigDict(frozen=True, extra="ignore")


class ToulminComponent(BaseModel):
    """Component of the Toulmin Argumentation Model."""

    id: str = Field(
        ...,
        description="Reference ID.",
        json_schema_extra={"x-ui-label": "ID"},
    )
    claim: str = Field(
        ...,
        description="The conclusion.",
        json_schema_extra={"x-ui-label": "Claim"},
    )
    data: str = Field(
        ...,
        description="The evidence.",
        json_schema_extra={"x-ui-label": "Data"},
    )
    warrant: str = Field(
        ...,
        description="The logical bridge.",
        json_schema_extra={"x-ui-label": "Warrant"},
    )
    backing: str | None = Field(
        default=None,
        description="Support for the warrant.",
        json_schema_extra={"x-ui-label": "Backing"},
    )
    rebuttal: str | None = Field(
        default=None,
        description="Counter-arguments.",
        json_schema_extra={"x-ui-label": "Rebuttal"},
    )
    qualifier: str | None = Field(
        default=None,
        description="Degree of certainty.",
        json_schema_extra={"x-ui-label": "Qualifier"},
    )
    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "claim", "data", "warrant")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class CognitiveLevel(BaseModel):
    """Assessment of cognitive depth."""

    bloom_level: BloomLevel = Field(
        ...,
        description="Bloom's Taxonomy Level.",
        json_schema_extra={"x-ui-label": "Bloom Level"},
    )
    strategic_depth: StrategicDepth = Field(
        ...,
        description="Strategic depth analysis.",
        json_schema_extra={"x-ui-label": "Strategic Depth"},
    )
    bloom_score: float = Field(
        ...,
        description="Numeric Bloom score (1-6).",
        json_schema_extra={"x-ui-label": "Bloom Score"},
    )
    strategic_score: float = Field(
        ...,
        description="Numeric Strategic score (1-4).",
        json_schema_extra={"x-ui-label": "Strategic Score"},
    )
    description_key: str = Field(
        default="bloom_desc",
        description="Localization key for help text.",
    )
    description: str = Field(
        default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"}
    )

    @field_validator("bloom_score")
    @classmethod
    def validate_bloom_score(cls, v: float) -> float:
        if not (1.0 <= v <= 6.0):
            raise ValueError("Bloom score must be between 1.0 and 6.0.")
        return v

    @field_validator("strategic_score")
    @classmethod
    def validate_strategic_score(cls, v: float) -> float:
        if not (1.0 <= v <= 4.0):
            raise ValueError("Strategic score must be between 1.0 and 4.0.")
        return v

    @model_validator(mode="before")
    @classmethod
    def calculate_scores(cls, data: Any) -> Any:
        """Calculate numeric scores and populate descriptions."""
        if isinstance(data, dict):
            # Populate Description (Context-Aware)
            key = data.get("description_key", "bloom_desc")
            if not data.get("description"):
                data["description"] = LocalizationService.translate(key)

            # Bloom Mapping (Enum-Based)
            bloom_map = {
                BloomLevel.REMEMBERING: 1.0,
                BloomLevel.UNDERSTANDING: 2.0,
                BloomLevel.APPLYING: 3.0,
                BloomLevel.ANALYZING: 4.0,
                BloomLevel.EVALUATING: 5.0,
                BloomLevel.CREATING: 6.0,
            }

            # Bloom Conversion (String -> Enum)
            # This is critical for strict=True models consuming JSON/DB data.
            bloom_val = data.get("bloom_level")
            if bloom_val and isinstance(bloom_val, str):
                # 1. Try direct lookup (e.g. "BLOOM_CREATING")
                try:
                    data["bloom_level"] = BloomLevel(bloom_val)
                except ValueError:
                    # 2. Try prefix matching (e.g. "creating" -> BloomLevel.CREATING)
                    val_upper = bloom_val.upper()
                    if not val_upper.startswith("BLOOM_"):
                        for member in BloomLevel:
                            if member.value.replace("BLOOM_", "") == val_upper:
                                data["bloom_level"] = member
                                break

            # Score Calculation (Bloom)
            current_bloom_score = data.get("bloom_score")
            if current_bloom_score is None and data.get("bloom_level"):
                # Calculate score from the now-resolved Enum
                b_enum = data["bloom_level"]
                if isinstance(b_enum, BloomLevel) and b_enum in bloom_map:
                    data["bloom_score"] = bloom_map[b_enum]

            # Strategic Conversion (String -> Enum)
            strat_val = data.get("strategic_depth")
            if strat_val and isinstance(strat_val, str):
                try:
                    data["strategic_depth"] = StrategicDepth(strat_val)
                except ValueError:
                    val_upper = strat_val.upper()
                    if not val_upper.startswith("STRAT_"):
                        for strat_member in StrategicDepth:
                            if strat_member.value.replace("STRAT_", "") == val_upper:
                                data["strategic_depth"] = strat_member
                                break

            # Score Calculation (Strategic)
            current_strat_score = data.get("strategic_score")
            if current_strat_score is None and data.get("strategic_depth"):
                strat_map = {
                    StrategicDepth.LOW: 1.0,
                    StrategicDepth.MEDIUM: 2.0,
                    StrategicDepth.HIGH: 3.0,
                    StrategicDepth.VISIONARY: 4.0,
                }
                s_enum = data["strategic_depth"]
                if isinstance(s_enum, StrategicDepth) and s_enum in strat_map:
                    data["strategic_score"] = strat_map[s_enum]

        return data

    model_config = ConfigDict(frozen=True, strict=True)


class WaltonScheme(BaseModel):
    """Walton's Argumentation Scheme."""

    identified_scheme: str = Field(
        ...,
        description="Identified Argumentation Scheme.",
        json_schema_extra={"x-ui-label": "Identified Scheme"},
    )
    critical_questions: list[str] = Field(
        ...,
        description="Critical Questions posed.",
        json_schema_extra={"x-ui-label": "Critical Questions"},
    )

    @field_validator("identified_scheme")
    @classmethod
    def validate_scheme(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Identified scheme cannot be empty.")
        return v.strip()

    @field_validator("critical_questions")
    @classmethod
    def validate_questions(cls, v: list[str]) -> list[str]:
        for q in v:
            if not q or not q.strip():
                raise ValueError("Critical questions cannot be empty strings.")
        return v

    model_config = ConfigDict(frozen=True, strict=True)


class LogicianData(BaseModel):
    """The core data payload of Logician analysis."""

    toulmin_analysis: list[ToulminComponent] = Field(
        ...,
        description="Toulmin analysis breakdown.",
        json_schema_extra={"x-ui-label": "Toulmin Analysis"},
    )
    cognitive_level: CognitiveLevel = Field(
        ...,
        description="Cognitive level assessment.",
        json_schema_extra={"x-ui-label": "Cognitive Level"},
    )
    walton_scheme: WaltonScheme = Field(
        ...,
        description="Argumentation scheme analysis.",
        json_schema_extra={"x-ui-label": "Argumentation Scheme"},
    )
    toulmin_score: float = Field(
        ...,
        ge=0.0,
        le=6.0,
        description="Calculated score based on components.",
        json_schema_extra={"x-ui-label": "Toulmin Score"},
    )
    description_key: str = Field(
        default="toulmin_desc",
        description="Localization key for help text.",
    )
    description: str = Field(
        default="", description="Localized description.", json_schema_extra={"x-ui-label": "Description"}
    )

    @field_validator("toulmin_analysis")
    @classmethod
    def validate_analysis(cls, v: list[ToulminComponent]) -> list[ToulminComponent]:
        if not v:
            raise ValueError("Toulmin analysis cannot be empty.")
        return v

    @model_validator(mode="before")
    @classmethod
    def pop_desc(cls, data: Any) -> Any:
        if isinstance(data, dict):
            key = data.get("description_key", "toulmin_desc")
            if not data.get("description"):
                data["description"] = LocalizationService.translate(key)
        return data

    model_config = ConfigDict(frozen=True, strict=True)


class LogicianOutputDTO(ReasoningTraceDTO):
    """Logician Output DTO (Content Only)."""

    logician_data: LogicianData = Field(
        ...,
        description="Logic analysis results.",
        json_schema_extra={"x-ui-label": "Logic Analysis"},
    )
    model_config = ConfigDict(frozen=True)


class LogicianOutput(LogicianOutputDTO, ReasoningTrace):
    """Output schema for the Logician Agent (Domain Authority)."""

    model_config = ConfigDict(frozen=True, strict=True)
