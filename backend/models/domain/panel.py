"""Panel Agent Domain Models.

This module contains the schemas for the Panel Agent (Consolidated Audit),
aggregating results from other specialist agents.
"""

from pydantic import ConfigDict, Field, field_validator

from backend.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend.models.domain.causal import CausalAnalysis
from backend.models.domain.falsifier import FalsifierData
from backend.models.domain.logician import LogicianData
from backend.models.domain.overseer import OverseerData
from backend.models.domain.performativity import PerformativityAnalysis


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
