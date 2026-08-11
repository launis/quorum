"""Scoring Hook Domain Models.

Provides strict Pydantic V2 validation schemas to replace legacy dictionary
parsing in the scoring and passivity penalty hooks.
"""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace
from backend_v2.models.domain.causal import CausalAnalysis
from backend_v2.models.domain.falsifier import FalsifierData
from backend_v2.models.domain.logician import LogicianData
from backend_v2.models.domain.overseer import OverseerData
from backend_v2.models.domain.performativity import PerformativityAnalysis


class StepFalsifierDTO(ReasoningTrace):
    """Strict schema for step_falsifier output within scoring hook.

    Attributes:
        falsifier_data: Structure containing counter-arguments.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    falsifier_data: Annotated[FalsifierData | None, Field(description="Structure containing counter-arguments.")] = None


class StepPanelDTO(V2CoreBase):
    """Strict schema for step_panel output within scoring hook.

    Attributes:
        falsifier_data: Structure containing counter-arguments.
        overseer_data: Execution governance details.
        logician_data: Data tracking logical deduction chains.
        performativity_analysis: Analysis tracking execution fidelity.
        causal_analysis: Analysis mapping causality relationships.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    falsifier_data: Annotated[FalsifierData | None, Field(description="Structure containing counter-arguments.")] = None
    overseer_data: Annotated[OverseerData | None, Field(description="Execution governance details.")] = None
    logician_data: Annotated[LogicianData | None, Field(description="Data tracking logical deduction chains.")] = None
    performativity_analysis: Annotated[
        PerformativityAnalysis | None, Field(description="Analysis tracking execution fidelity.")
    ] = None
    causal_analysis: Annotated[
        CausalAnalysis | None, Field(description="Analysis mapping causality relationships.")
    ] = None
