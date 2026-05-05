from typing import Any
from pydantic import Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import LaxXaiExtensionType


class OutputProfileConfig(V2CoreBase):
    """Configuration for Output Profile extensions."""

    visible_extensions: list[LaxXaiExtensionType]


class LightweightMatrixOutput(V2CoreBase):
    """Strict schema for the Lightweight Matrix Output."""

    raw_score: float
    normalized_score: float = Field(ge=0.0, le=100.0)
    level_breakdown: dict[str, dict[str, int]] | None = None
    justification: str = ""
    evaluated_atoms: dict[str, bool] = Field(default_factory=dict)
    extensions: dict[LaxXaiExtensionType, str] = Field(default_factory=dict)

class AtomEvaluationItemDTO(V2CoreBase):
    """Strict schema for individual atom evaluations in the waterfall pipeline."""

    atom_id: str
    step_1_evidence_type: str | None = None
    step_2_quote: str | None = None
    step_3_implicit_justification: str | None = None
    step_4_reasoning: str = ""
    step_5_boolean: bool = False
