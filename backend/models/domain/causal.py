"""Causal Agent Domain Models.

This module contains the schemas for the Causal Agent,
including counterfactual testing and abductive reasoning.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend.models.domain.analyst import AnalystOutput
from backend.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend.models.domain.logician import LogicianOutput
from backend.models.enums import AbductiveConclusion, PlausibilityLevel


class CausalInput(BaseModel):
    """Strict input schema for CausalAnalystAgent."""

    history_text: str = Field(..., description="Chat history to analyze.")
    step_analyst: AnalystOutput | LogicianOutput | None = Field(None, description="Analyst or Logician outputs.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    model_config = ConfigDict(frozen=True, extra="ignore")


class CausalAnalysisData(BaseModel):
    """Data from Causal Audit."""

    timeline_valid: bool = Field(
        ...,
        description="Is the timeline valid?",
        json_schema_extra={"x-ui-label": "Timeline Valid"},
    )
    observation: str = Field(
        ...,
        description="General observations.",
        json_schema_extra={"x-ui-label": "Observations"},
    )
    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("observation")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class CounterfactualTest(BaseModel):
    """Counterfactual test result."""

    plausibility_score: PlausibilityLevel = Field(
        ...,
        description="Plausibility score.",
        json_schema_extra={"x-ui-label": "Plausibility Score"},
    )
    plausibility_numeric: float = Field(
        ...,
        description="Numeric plausibility (1-3).",
        json_schema_extra={"x-ui-label": "Plausibility Numeric"},
    )
    actual_scenario: str = Field(
        ..., description="Actual outcome.", json_schema_extra={"x-ui-label": "Actual Scenario"}
    )
    simulation_result: str = Field(
        ..., description="Simulation outcome.", json_schema_extra={"x-ui-label": "Simulation Result"}
    )

    @field_validator("actual_scenario", "simulation_result")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @model_validator(mode="before")
    @classmethod
    def calc_plausibility(cls, data: Any) -> Any:
        if isinstance(data, dict):
            mapping = {PlausibilityLevel.IMPOSSIBLE: 1.0, PlausibilityLevel.PLAUSIBLE: 2.0, PlausibilityLevel.HIGH: 3.0}
            val = data.get("plausibility_score")
            if val:
                try:
                    enum_val = val if isinstance(val, PlausibilityLevel) else PlausibilityLevel(val)
                    data["plausibility_score"] = enum_val

                    if data.get("plausibility_numeric") is None and enum_val in mapping:
                        data["plausibility_numeric"] = mapping[enum_val]
                except ValueError as e:
                    from backend.exceptions import AppException
                    raise AppException(
                        message=f"Invalid Plausibility Score: {val}. Allowed: IMPOSSIBLE, PLAUSIBLE, HIGH.",
                        status_code=400,
                        details={"error_code": "INVALID_ENUM_VALUE", "original_error": str(e)}
                    )
        return data

    model_config = ConfigDict(frozen=True)


class CausalAnalysis(BaseModel):
    """Causal analysis result."""

    abductive_conclusion: AbductiveConclusion = Field(
        ...,
        description="Abductive conclusion type.",
        json_schema_extra={"x-ui-label": "Abductive Conclusion"},
    )
    abductive_score: float = Field(
        ...,
        description="Numeric abductive score (1-3).",
        json_schema_extra={"x-ui-label": "Abductive Score"},
    )
    counterfactual_test: CounterfactualTest = Field(
        ...,
        description="Counterfactual analysis.",
        json_schema_extra={"x-ui-label": "Counterfactual Test"},
    )
    observation: str = Field(..., description="Observation.", json_schema_extra={"x-ui-label": "Observation"})
    hypothesis: str = Field(..., description="Hypothesis.", json_schema_extra={"x-ui-label": "Hypothesis"})

    @field_validator("observation", "hypothesis")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @model_validator(mode="before")
    @classmethod
    def calc_abductive(cls, data: Any) -> Any:
        if isinstance(data, dict):
            mapping = {
                AbductiveConclusion.POST_HOC: 1.0,
                AbductiveConclusion.UNCERTAIN: 2.0,
                AbductiveConclusion.GENUINE: 3.0,
            }
            val = data.get("abductive_conclusion")
            if val:
                try:
                    enum_val = val if isinstance(val, AbductiveConclusion) else AbductiveConclusion(val)
                    data["abductive_conclusion"] = enum_val

                    if data.get("abductive_score") is None and enum_val in mapping:
                        data["abductive_score"] = mapping[enum_val]
                except ValueError as e:
                    from backend.exceptions import AppException
                    raise AppException(
                        message=f"Invalid Abductive Conclusion: {val}. Allowed: POST_HOC, UNCERTAIN, GENUINE.",
                        status_code=400,
                        details={"error_code": "INVALID_ENUM_VALUE", "original_error": str(e)}
                    )
        return data

    model_config = ConfigDict(frozen=True)


class CausalDTO(ReasoningTraceDTO):
    """Causal DTO (Content Only)."""

    causal_analysis: CausalAnalysis = Field(
        ...,
        description="Causal audit result.",
        json_schema_extra={"x-ui-label": "Causal Audit"},
    )
    model_config = ConfigDict(frozen=True, strict=False)


class CausalOutput(CausalDTO, ReasoningTrace):
    """Output schema for the Causal Agent."""

    model_config = ConfigDict(frozen=True, strict=False)
