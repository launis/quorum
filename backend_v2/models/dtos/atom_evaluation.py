from typing import Annotated, Any

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import LaxExecutionStatus


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
    extracted_data: dict[str, Any] | None = None


class LightweightMatrixDTO(V2CoreBase):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Token-compressed matrix payload for Synthesis Generation."""

    execution_id: str
    reduced_atoms: list[ReducedAtomDTO]
    global_metrics: dict[str, Any]
    raw_extensions: list[dict[str, Any]] = Field(default_factory=list)
