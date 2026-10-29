"""Scoring Hook Domain Models.

Provides strict Pydantic V2 validation schemas to replace legacy dictionary
parsing in the scoring and passivity penalty hooks.
"""

from __future__ import annotations

from typing import Annotated, Self

from pydantic import ConfigDict, Field, model_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace
from backend_v2.models.domain.causal import CausalAnalysis
from backend_v2.models.domain.falsifier import FalsifierData
from backend_v2.models.domain.logician import LogicianData
from backend_v2.models.domain.overseer import OverseerData
from backend_v2.models.domain.performativity import PerformativityAnalysis

__all__ = [
    "StepFalsifierDTO",
    "StepPanelDTO",
]


class StepFalsifierDTO(ReasoningTrace):
    """Strict schema for step_falsifier output within scoring hook.

    Attributes:
        falsifier_data: Structure containing counter-arguments.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

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

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    falsifier_data: Annotated[FalsifierData | None, Field(description="Structure containing counter-arguments.")] = None
    overseer_data: Annotated[OverseerData | None, Field(description="Execution governance details.")] = None
    logician_data: Annotated[LogicianData | None, Field(description="Data tracking logical deduction chains.")] = None
    performativity_analysis: Annotated[
        PerformativityAnalysis | None, Field(description="Analysis tracking execution fidelity.")
    ] = None
    causal_analysis: Annotated[
        CausalAnalysis | None, Field(description="Analysis mapping causality relationships.")
    ] = None

    @model_validator(mode="after")
    def validate_at_least_one_payload(self) -> Self:
        """Enforce that at least one analysis payload is populated.

        Returns:
            Validated StepPanelDTO instance.

        Raises:
            ValueError: If all five analysis payloads are None.
        """
        if (
            self.falsifier_data is None
            and self.overseer_data is None
            and self.logician_data is None
            and self.performativity_analysis is None
            and self.causal_analysis is None
        ):
            raise ValueError("StepPanelDTO requires at least one analysis payload to be populated.")
        return self
