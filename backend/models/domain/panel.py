"""Panel Agent Domain Models.

This module contains the schemas for the Panel Agent (Consolidated Audit),
aggregating results from other specialist agents.
"""


from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from pydantic import ConfigDict, Field, field_validator, BaseModel

from backend.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend.models.domain.analyst import AnalystOutput
from backend.models.domain.profiler import ProfilerAnalysis
from backend.models.domain.causal import CausalAnalysis
from backend.models.domain.falsifier import FalsifierData
from backend.models.domain.logician import LogicianData
from backend.models.domain.overseer import OverseerData
from backend.models.domain.performativity import PerformativityAnalysis

if TYPE_CHECKING:
    pass


class PanelInput(BaseModel):
    """Strict input schema for PanelAgent."""
    
    # Context
    history_text: str = Field(..., description="Chat history.")
    product_text: str = Field(..., description="Product description.")
    reflection_text: Optional[str] = Field(None, description="User reflection.")
    
    # Dependencies (Mandatory in Agent Logic, Optional in Schema for flexibility?)
    # No, strict typing means we should define what we expect.
    step_analyst: Optional["AnalystOutput"] = Field(None, description="Analyst Evidence Map.")
    step_profiler: Optional["ProfilerAnalysis"] = Field(None, description="Profiler Analysis.")
    last_reasoning_trace: Optional[str] = Field(default=None, description="Previous reasoning trace.")

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
    
    step_logician: Optional["LogicianData"] = Field(None, description="Logician Logic Audit.")
    step_falsifier: Optional["FalsifierData"] = Field(None, description="Falsifier Audit.")
    step_causal: Optional["CausalAnalysis"] = Field(None, description="Causal Audit.")
    step_detector: Optional["PerformativityAnalysis"] = Field(None, description="Performativity Audit.")
    step_overseer: Optional["OverseerData"] = Field(None, description="Overseer Audit.")

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
