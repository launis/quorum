"""Causal Agent Domain Models.

This module contains the schemas for the Causal Agent,
including counterfactual testing and abductive reasoning.
"""

from __future__ import annotations

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.logician import LogicianOutput
from backend_v2.models.enums import AbductiveConclusion, PlausibilityLevel


class CausalInput(V2CoreBase):
    """Strict input schema for CausalAnalystAgent."""

    chat_log: str = Field(..., min_length=1, description="Mandatory chatlog to analyze.")
    step_analyst: AnalystOutput | LogicianOutput | None = Field(None, description="Analyst or Logician outputs.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")


class CausalAnalysisData(V2CoreBase):
    """Data from Causal Audit."""

    timeline_valid: bool = Field(
        ...,
        description="Is the timeline valid?",
        json_schema_extra={"x-ui-label": "Timeline Valid"},
    )
    observation: str = Field(
        ...,
        min_length=1,
        description="General observations.",
        json_schema_extra={"x-ui-label": "Observations"},
    )


class CounterfactualTest(V2CoreBase):
    """Counterfactual test result."""

    plausibility_score: PlausibilityLevel = Field(
        ...,
        description="Plausibility score.",
        json_schema_extra={"x-ui-label": "Plausibility Score"},
    )
    plausibility_numeric: float = Field(
        ...,
        ge=1.0,
        le=3.0,
        description=(
            "Numeric plausibility (1.0 to 3.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 2.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Plausibility Numeric"},
    )
    actual_scenario: str = Field(
        ..., min_length=1, description="Actual outcome.", json_schema_extra={"x-ui-label": "Actual Scenario"}
    )
    simulation_result: str = Field(
        ..., min_length=1, description="Simulation outcome.", json_schema_extra={"x-ui-label": "Simulation Result"}
    )


class CausalAnalysis(V2CoreBase):
    """Causal analysis result."""

    abductive_conclusion: AbductiveConclusion = Field(
        ...,
        description="Abductive conclusion type.",
        json_schema_extra={"x-ui-label": "Abductive Conclusion"},
    )
    abductive_score: float = Field(
        ...,
        ge=1.0,
        le=3.0,
        description=(
            "Numeric abductive score (1.0 to 3.0), required 1-decimal precision. "
            "USE DECIMALS (e.g., 2.5) to reflect nuance."
        ),
        json_schema_extra={"x-ui-label": "Abductive Score"},
    )
    counterfactual_test: CounterfactualTest = Field(
        ...,
        description="Counterfactual analysis.",
        json_schema_extra={"x-ui-label": "Counterfactual Test"},
    )
    observation: str = Field(
        ..., min_length=1, description="Observation.", json_schema_extra={"x-ui-label": "Observation"}
    )
    hypothesis: str = Field(
        ..., min_length=1, description="Hypothesis.", json_schema_extra={"x-ui-label": "Hypothesis"}
    )


class CausalDTO(ReasoningTraceDTO):
    """Causal DTO (Content Only)."""

    causal_analysis: CausalAnalysis = Field(
        ...,
        description="Causal audit result.",
        json_schema_extra={"x-ui-label": "Causal Audit"},
    )


class CausalOutput(CausalDTO, ReasoningTrace):
    """Output schema for the Causal Agent."""
