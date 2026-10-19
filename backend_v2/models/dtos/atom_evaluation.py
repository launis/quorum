"""Data Transfer Objects for atom evaluation results and synthesis reduction."""

from __future__ import annotations

from typing import Annotated

from pydantic import BeforeValidator, ConfigDict, Field, JsonValue

from backend_v2.models.core_base import V2CoreBase, coerce_source_quotes_tuple
from backend_v2.models.enums import LaxExecutionStatus

__all__ = [
    "EvaluatedMatrixRefDTO",
    "LightweightMatrixDTO",
    "RawXAIExtensionDTO",
    "ReasoningStepDTO",
    "ReducedAtomDTO",
]


class ReasoningStepDTO(V2CoreBase):
    """Structured micro-CoT reasoning step schema to prevent JSON escaping issues.

    Attributes:
        step_1_identify_premise: Extract the exact claim from the prompt.
        step_2_scan_source: Analyze if the source text physically contains evidence.
        step_3_evaluate_anti_patterns: Check if any strict anti-patterns or exclusions apply.
        step_4_final_conclusion: Synthesize steps 1-3 into a final logical conclusion.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    step_1_identify_premise: Annotated[str, Field(description="Extract the exact claim from the prompt.")]
    step_2_scan_source: Annotated[
        str, Field(description="Analyze if the source text physically contains evidence for or against the premise.")
    ]
    step_3_evaluate_anti_patterns: Annotated[
        str, Field(description="Check if any strict anti-patterns or exclusions apply.")
    ]
    step_4_final_conclusion: Annotated[str, Field(description="Synthesize steps 1-3 into a final logical conclusion.")]


class ReducedAtomDTO(V2CoreBase):
    """Reduced atom data for synthesis, containing only what is strictly necessary.

    Attributes:
        tda_id: Authoritative atom identifier.
        status: Execution status of the evaluated atom.
        reasoning: Optional textual rationale for the atom outcome.
        source_quotes: Verbatim source quote segments as a validated tuple.
        extracted_data: Optional structured extraction key-value payload.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tda_id: Annotated[str, Field(description="Authoritative atom identifier.")]
    status: Annotated[LaxExecutionStatus, Field(description="Lax execution status.")]
    reasoning: Annotated[str | None, Field(default=None, description="Optional evaluation reasoning text.")] = None
    source_quotes: Annotated[
        tuple[str, ...] | None,
        BeforeValidator(coerce_source_quotes_tuple),
        Field(default=None, description="Verbatim source quote segments."),
    ] = None
    extracted_data: Annotated[
        dict[str, JsonValue] | None,
        Field(default=None, description="Optional extracted key-value pairs."),
    ] = None


class EvaluatedMatrixRefDTO(V2CoreBase):
    """Reference to an evaluated matrix block.

    Attributes:
        matrix_id: Authoritative matrix identifier.
        score: Evaluated numerical score for the matrix.
        display_name: Localized or human-readable display name.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    matrix_id: Annotated[str, Field(description="Authoritative matrix identifier.")]
    score: Annotated[float | None, Field(default=None, description="Evaluated numerical score.")] = None
    display_name: Annotated[str | None, Field(default=None, description="Display name.")] = None


class RawXAIExtensionDTO(V2CoreBase):
    """Raw XAI extension data captured during matrix atom evaluation.

    Attributes:
        id: Optional extension identifier.
        type: Category or classification type of the extension.
        citation: Verbatim source citation or text anchor.
        justification: Argumentative justification.
        falsification: Falsification explanation.
        theory_link: Academic or ontological framework reference.
        risk_flag: High-severity risk boolean indicator.
        coaching: Prescriptive coaching feedback.
        missing_context: Description of missing contextual data.
        remediation_steps: Actionable remediation steps.
        emotional_sentiment: Detected emotional tone.
        confidence: Numerical confidence score.
        source_id: Originating source input identifier.
        contextual_override: Whether contextual override was applied.
        variance_validation: Variance validation outcome.
        authenticity_evaluation: Assessment of source authenticity.
        pedagogical_key: Pedagogical taxonomy key.
        raw_payload: Untyped or raw JSON dictionary payload.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    id: Annotated[str | None, Field(default=None, description="Extension identifier.")] = None
    type: Annotated[str | None, Field(default=None, description="Extension type.")] = None
    citation: Annotated[str | None, Field(default=None, description="Source citation text.")] = None
    justification: Annotated[str | None, Field(default=None, description="Justification argument.")] = None
    falsification: Annotated[str | None, Field(default=None, description="Falsification rationale.")] = None
    theory_link: Annotated[str | None, Field(default=None, description="Theory or framework link.")] = None
    risk_flag: Annotated[bool | None, Field(default=None, description="Risk indicator flag.")] = None
    coaching: Annotated[str | None, Field(default=None, description="Coaching feedback text.")] = None
    missing_context: Annotated[str | None, Field(default=None, description="Missing context description.")] = None
    remediation_steps: Annotated[
        str | list[str] | None, Field(default=None, description="Actionable remediation steps.")
    ] = None
    emotional_sentiment: Annotated[str | None, Field(default=None, description="Emotional sentiment rating.")] = None
    confidence: Annotated[float | None, Field(default=None, description="Confidence score.")] = None
    source_id: Annotated[str | None, Field(default=None, description="Source identifier.")] = None
    contextual_override: Annotated[bool | None, Field(default=None, description="Contextual override flag.")] = None
    variance_validation: Annotated[str | None, Field(default=None, description="Variance validation result.")] = None
    authenticity_evaluation: Annotated[str | None, Field(default=None, description="Authenticity evaluation.")] = None
    pedagogical_key: Annotated[str | None, Field(default=None, description="Pedagogical taxonomy key.")] = None
    raw_payload: Annotated[dict[str, JsonValue] | None, Field(default=None, description="Raw extension payload.")] = (
        None
    )


class LightweightMatrixDTO(V2CoreBase):
    """Token-compressed matrix payload for Synthesis Generation.

    Attributes:
        execution_id: Unique execution identifier.
        reduced_atoms: Sequence of token-reduced atoms.
        global_metrics: High-level numerical and categorical metrics dictionary.
        evaluated_matrices: Evaluated matrix references for cross-block reasoning.
        raw_extensions: Raw XAI extensions captured during matrix evaluation.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    execution_id: Annotated[str, Field(description="Unique execution identifier.")]
    reduced_atoms: Annotated[list[ReducedAtomDTO], Field(description="List of token-reduced atoms.")]
    global_metrics: Annotated[dict[str, JsonValue], Field(description="Global execution metrics dictionary.")]
    evaluated_matrices: Annotated[
        list[EvaluatedMatrixRefDTO],
        Field(default_factory=list, description="Evaluated matrix references."),
    ]
    raw_extensions: Annotated[
        list[RawXAIExtensionDTO],
        Field(default_factory=list, description="Raw XAI extensions from execution trace."),
    ]
