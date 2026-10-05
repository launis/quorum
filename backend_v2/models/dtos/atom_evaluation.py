from __future__ import annotations

from typing import Annotated

from pydantic import ConfigDict, Field, JsonValue

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import LaxExecutionStatus

__all__ = [
    "EvaluatedMatrixRefDTO",
    "LightweightMatrixDTO",
    "RawXAIExtensionDTO",
    "ReasoningStepDTO",
    "ReducedAtomDTO",
]


class ReasoningStepDTO(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Structured micro-CoT reasoning step schema to prevent JSON escaping issues."""

    step_1_identify_premise: Annotated[str, Field(description="Extract the exact claim from the prompt.")]
    step_2_scan_source: Annotated[
        str, Field(description="Analyze if the source text physically contains evidence for or against the premise.")
    ]
    step_3_evaluate_anti_patterns: Annotated[
        str, Field(description="Check if any strict anti-patterns or exclusions apply.")
    ]
    step_4_final_conclusion: Annotated[str, Field(description="Synthesize steps 1-3 into a final logical conclusion.")]


class ReducedAtomDTO(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Reduced atom data for synthesis, containing only what is strictly necessary."""

    tda_id: str
    status: LaxExecutionStatus
    reasoning: str | None = None
    source_quote: str | None = None
    extracted_data: dict[str, JsonValue] | None = None


class EvaluatedMatrixRefDTO(V2CoreBase):
    """Reference to an evaluated matrix block."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    matrix_id: str
    score: float | None = None
    display_name: str | None = None


class RawXAIExtensionDTO(V2CoreBase):
    """Raw XAI extension data captured during matrix atom evaluation."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: str | None = None
    type: str | None = None
    citation: str | None = None
    justification: str | None = None
    falsification: str | None = None
    theory_link: str | None = None
    risk_flag: bool | None = None
    coaching: str | None = None
    missing_context: str | None = None
    remediation_steps: str | list[str] | None = None
    emotional_sentiment: str | None = None
    confidence: float | None = None
    source_id: str | None = None
    contextual_override: bool | None = None
    variance_validation: str | None = None
    authenticity_evaluation: str | None = None
    pedagogical_key: str | None = None
    raw_payload: dict[str, JsonValue] | None = None


class LightweightMatrixDTO(V2CoreBase):
    """Token-compressed matrix payload for Synthesis Generation."""

    model_config = ConfigDict(strict=True, extra="forbid")

    execution_id: str
    reduced_atoms: list[ReducedAtomDTO]
    global_metrics: dict[str, JsonValue]
    evaluated_matrices: Annotated[
        list[EvaluatedMatrixRefDTO],
        Field(default_factory=list, description="Evaluated matrix references"),
    ]
    raw_extensions: Annotated[
        list[RawXAIExtensionDTO],
        Field(default_factory=list, description="Raw XAI extensions from execution trace"),
    ]
