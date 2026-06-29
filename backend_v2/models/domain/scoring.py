"""Scoring Hook Domain Models.

Provides strict Pydantic V2 validation schemas to replace legacy dictionary
parsing in the scoring and passivity penalty hooks.
"""

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace
from backend_v2.models.domain.causal import CausalAnalysis
from backend_v2.models.domain.falsifier import FalsifierData
from backend_v2.models.domain.guard import SecurityCheck, TaintedDataContent
from backend_v2.models.domain.logician import LogicianData
from backend_v2.models.domain.overseer import OverseerData
from backend_v2.models.domain.performativity import PerformativityAnalysis


class StepGuardDTO(ReasoningTrace):
    """Strict schema for step_guard output within scoring hook.

    Attributes:
        security_check: Evaluated results mapping safe execution states.
        tainted_data: Optional details identifying any tainted data elements encountered.
    """

    security_check: SecurityCheck = Field(...)
    tainted_data: TaintedDataContent | None = Field(default=None)


class StepFalsifierDTO(ReasoningTrace):
    """Strict schema for step_falsifier output within scoring hook.

    Attributes:
        falsifier_data: Structure containing counter-arguments.
    """

    falsifier_data: FalsifierData | None = Field(default=None)


class StepPanelDTO(V2CoreBase):
    """Strict schema for step_panel output within scoring hook.

    Attributes:
        falsifier_data: Structure containing counter-arguments.
        overseer_data: Execution governance details.
        logician_data: Data tracking logical deduction chains.
        performativity_analysis: Analysis tracking execution fidelity.
        causal_analysis: Analysis mapping causality relationships.
    """

    falsifier_data: FalsifierData | None = Field(default=None)
    overseer_data: OverseerData | None = Field(default=None)
    logician_data: LogicianData | None = Field(default=None)
    performativity_analysis: PerformativityAnalysis | None = Field(default=None)
    causal_analysis: CausalAnalysis | None = Field(default=None)
