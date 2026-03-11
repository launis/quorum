"""Panel Agent Domain Models.

This module contains the schemas for the Panel Agent (Consolidated Audit),
aggregating results from other specialist agents.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.models.domain.analyst import AnalystOutput
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.causal import CausalAnalysis
from backend_v2.models.domain.falsifier import FalsifierData
from backend_v2.models.domain.logician import LogicianData, LogicianOutput
from backend_v2.models.domain.overseer import OverseerData
from backend_v2.models.domain.performativity import PerformativityAnalysis
from backend_v2.models.domain.profiler import ProfilerOutput
from backend_v2.models.domain.retrieval import ContextData


class PanelInput(BaseModel):
    """Strict input schema for PanelAgent."""

    # Context
    history_text: str | None = Field(None, description="Chat history.")
    product_text: str | None = Field(None, description="Product description.")
    reflection_text: str | None = Field(None, description="User reflection.")

    # Dependencies (Mandatory in Agent Logic, Optional in Schema for flexibility?)
    # No, strict typing means we should define what we expect.
    step_analyst: AnalystOutput | LogicianOutput | None = Field(None, description="Analyst or Logician outputs.")
    step_profiler: ProfilerOutput | None = Field(None, description="Profiler Analysis.")
    step_context: ContextData | None = Field(None, description="Knowledge Context from Retriever.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    # Upstream Agent Outputs (Strict Forward References)
    # These seem to be here if Panel is Aggregating?
    # But Panel PRODCUES them.
    # Maybe PanelInput is for a DIFFERENT use case?
    # If PanelAgent RUNS them, it doesn't need them as input.
    # But if PanelAgent is a "Panel" that reviews them...
    # The docstring says "Executes multiple critical roles...".
    # So it GENERATES them.
    # So PanelInput should NOT have them as mandatory.
    # But maybe it can take them if they exist?

    step_logician: LogicianData | None = Field(None, description="Logician Logic Audit.")
    step_falsifier: FalsifierData | None = Field(None, description="Falsifier Audit.")
    step_causal: CausalAnalysis | None = Field(None, description="Causal Audit.")
    step_detector: PerformativityAnalysis | None = Field(None, description="Performativity Audit.")
    step_overseer: OverseerData | None = Field(None, description="Overseer Audit.")

    model_config = ConfigDict(frozen=True, extra="ignore")


class PanelOutputDTO(ReasoningTraceDTO):
    """DTO for Panel Agent (Content Only)."""

    logician_data: LogicianData = Field(
        ...,
        description="Logic audit result (from Logician).",
        json_schema_extra={"x-ui-label": "Logic Audit"},
    )
    falsifier_data: FalsifierData = Field(
        ...,
        description="Falsification audit result.",
        json_schema_extra={"x-ui-label": "Falsification Audit"},
    )
    causal_analysis: CausalAnalysis = Field(
        ...,
        description="Causal audit result.",
        json_schema_extra={"x-ui-label": "Causal Audit"},
    )
    performativity_analysis: PerformativityAnalysis = Field(
        ...,
        description="Performativity audit result.",
        json_schema_extra={"x-ui-label": "Performativity Audit"},
    )
    overseer_data: OverseerData = Field(
        ...,
        description="Ethics audit result.",
        json_schema_extra={"x-ui-label": "Ethics Audit"},
    )

    model_config = ConfigDict(frozen=True, strict=True)


class PanelOutput(PanelOutputDTO, ReasoningTrace):
    """Consolidated Output schema for the Panel Agent (Parallel Step).

    Aggregates results from Falsifier, Causal, Detector (Performativity), and Overseer.
    """

    model_config = ConfigDict(frozen=True, strict=True)
