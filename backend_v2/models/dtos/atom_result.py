"""Data Transfer Objects for Atom Evaluation Results and DAG Telemetry.

SSOT for ErrorDetailsDTO, HydratedAtomDTO, ExtractedValueDTO, AtomResultDTO,
EvaluatedAtomDTO, EvaluationFactsDTO, ExecutionMetricsDTO, and ExtensionMetricsDTO.
"""

from __future__ import annotations

from typing import Annotated, Self

from pydantic import ConfigDict, Field, model_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import (
    ExecutionStatus,
    LaxExecutionStatus,
    LaxSDUIComponentType,
)

__all__ = [
    "AtomResultDTO",
    "ErrorDetailsDTO",
    "EvaluatedAtomDTO",
    "EvaluationFactsDTO",
    "ExecutionMetricsDTO",
    "ExtensionMetricsDTO",
    "ExtractedValueDTO",
    "HydratedAtomDTO",
]


class ErrorDetailsDTO(V2CoreBase):
    """Standardized error details for failed atom executions.

    Attributes:
        error_code: Standardized error code, e.g., LLM_TIMEOUT.
        message: Technical error message or stack trace.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    error_code: Annotated[str, Field(description="Standardized error code, e.g., LLM_TIMEOUT")]
    message: Annotated[str, Field(description="Technical error message or stack trace")]


class HydratedAtomDTO(V2CoreBase):
    """Static ontology data. Perfectly cacheable.

    Must not contain any dynamic execution-related data.

    Attributes:
        sdui_component: Server-Driven UI hint for frontend.
        resolved_claim: Cleaned claim in human language.
        source_quote: Optional verbatim original quote.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    sdui_component: Annotated[LaxSDUIComponentType, Field(description="Server-Driven UI hint for frontend.")]
    resolved_claim: Annotated[str, Field(description="Cleaned claim in human language")]
    source_quote: Annotated[str | None, Field(default=None, description="Verbatim original quote")] = None


class ExtractedValueDTO(V2CoreBase):
    """Quantitative or categorical extracted value.

    Attributes:
        value: The extracted quantitative or categorical value.
        unit: Optional unit of measurement, e.g., 'tCO2e' or 'EUR'.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    value: Annotated[str | float | int | bool, Field(description="Extracted quantitative or categorical value")]
    unit: Annotated[str | None, Field(default=None, description="Unit of measurement, e.g., 'tCO2e' or 'EUR'")] = None


class AtomResultDTO(V2CoreBase):
    """Dynamic execution data (DAG node).

    Attributes:
        tda_id: Opaque ID pointing to the hydrated_references dictionary key.
        matrix_id: Opaque ID of the matrix block that requested this evaluation.
        status: Evaluation execution status.
        extracted_data: Quantitative or isolated result.
        source_quote: Verbatim original quote from the document.
        contextual_override: Allows cognitive override without a verbatim quote.
        is_inverse_evidence: True if assertion evaluates absence of negative evidence.
        evaluation_reasoning: Strictly AI cognitive reasoning, no infra errors.
        error_details: Populated only if status is SYSTEM_ERROR.
        extensions: Requested XAI extensions mapping.
        depends_on_tda_ids: DAG adjacency list.
        short_circuit_reason_tda_ids: List of short-circuit reason TDA IDs.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    tda_id: Annotated[str, Field(description="Opaque ID pointing to the hydrated_references dictionary key")]
    matrix_id: Annotated[
        str | None, Field(default=None, description="Opaque ID of the matrix block that requested this evaluation")
    ] = None
    status: Annotated[LaxExecutionStatus, Field(description="Evaluation execution status")]
    extracted_data: Annotated[
        ExtractedValueDTO | None, Field(default=None, description="Quantitative or isolated result")
    ] = None
    source_quote: Annotated[
        str | None, Field(default=None, description="Verbatim original quote from the document")
    ] = None
    contextual_override: Annotated[
        bool, Field(default=False, description="Allows cognitive override without a verbatim quote")
    ] = False
    is_inverse_evidence: Annotated[
        bool,
        Field(
            default=False,
            description="True if assertion evaluates absence of negative evidence (null hypothesis).",
        ),
    ] = False
    evaluation_reasoning: Annotated[
        str | None, Field(default=None, description="Strictly AI cognitive reasoning, no infra errors")
    ] = None
    error_details: Annotated[
        ErrorDetailsDTO | None, Field(default=None, description="Populated only if status is SYSTEM_ERROR")
    ] = None
    extensions: Annotated[
        dict[str, str], Field(default_factory=dict, description="Requested XAI extensions mapping")
    ] = Field(default_factory=dict)

    depends_on_tda_ids: Annotated[list[str], Field(default_factory=list, description="DAG adjacency list")] = Field(
        default_factory=list
    )
    short_circuit_reason_tda_ids: Annotated[list[str], Field(default_factory=list)] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_cognitive_vs_system_state(self) -> Self:
        """Fail-Fast validation for cognitive state consistency.

        Returns:
            The validated AtomResultDTO instance.

        Raises:
            ValueError: If cognitive or system state invariants are violated.
        """
        if self.status == ExecutionStatus.FAILED:
            if not self.evaluation_reasoning or not self.evaluation_reasoning.strip():
                raise ValueError(f"Reasoning is mandatory for cognitive status {self.status.value}")
            if self.contextual_override:
                raise ValueError("contextual_override cannot be True when status is FAILED")
            if self.is_inverse_evidence:
                raise ValueError("is_inverse_evidence cannot be True when status is FAILED")
            if self.source_quote is not None:
                raise ValueError("source_quote must be None when status is FAILED")

        elif self.status == ExecutionStatus.PASSED:
            if not self.evaluation_reasoning or not self.evaluation_reasoning.strip():
                raise ValueError(f"Reasoning is mandatory for cognitive status {self.status.value}")
            if not self.contextual_override and not self.is_inverse_evidence and not self.source_quote:
                raise ValueError("source_quote is mandatory unless contextual_override or is_inverse_evidence is True")
            if (self.contextual_override or self.is_inverse_evidence) and self.source_quote is not None:
                raise ValueError("source_quote must be None when contextual_override or is_inverse_evidence is True")

        elif self.status == ExecutionStatus.SYSTEM_ERROR and not self.error_details:
            raise ValueError("Error details are mandatory when status is SYSTEM_ERROR")

        return self


class EvaluationFactsDTO(V2CoreBase):
    """Strongly typed facts mapping table for boolean expression AST evaluation.

    Attributes:
        facts: Mapping of identifier keys to truth states or values (bool | str).
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    facts: Annotated[
        dict[str, bool | str],
        Field(default_factory=dict, description="Mapping of variable keys to derived evaluation states"),
    ] = Field(default_factory=dict)


class EvaluatedAtomDTO(V2CoreBase):
    """Strongly typed evaluated atom representation in matrix context.

    Attributes:
        tda_id: Authoritative identifier for the atom.
        atom_id: Optional alias identifier matching tda_id.
        status: Status of the evaluated atom.
        score: Computed mathematical or categorical score.
        human_override: Optional human override status.
        exact_quotes: List of verbatim extracted source quotes.
        source_quote: Verbatim extracted source quote.
        evaluation_reasoning: Cognitive reasoning text.
        contextual_override: Whether cognitive override without quote occurred.
        is_inverse_evidence: Whether inverse evidence (null hypothesis) was evaluated.
        facts: Associated evaluation facts if present.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tda_id: Annotated[str, Field(description="Authoritative Opaque ID for the atom")]
    atom_id: Annotated[str | None, Field(default=None, description="Optional alias identifier matching tda_id")] = None
    status: Annotated[str | None, Field(default=None, description="Evaluation status string or enum")] = None
    score: Annotated[float | int | None, Field(default=None, description="Atom evaluation score")] = None
    human_override: Annotated[str | None, Field(default=None, description="Human override status")] = None
    exact_quotes: Annotated[list[str], Field(default_factory=list, description="Verbatim extracted source quotes")] = (
        Field(default_factory=list)
    )
    source_quote: Annotated[str | None, Field(default=None, description="Verbatim source quote")] = None
    evaluation_reasoning: Annotated[str | None, Field(default=None, description="Cognitive reasoning explanation")] = (
        None
    )
    contextual_override: Annotated[bool, Field(default=False, description="Cognitive override flag")] = False
    is_inverse_evidence: Annotated[bool, Field(default=False, description="Inverse evidence flag")] = False
    facts: Annotated[EvaluationFactsDTO | None, Field(default=None, description="Evaluation facts")] = None


class ExecutionMetricsDTO(V2CoreBase):
    """Aggregate atom-level metrics for DAG execution.

    Attributes:
        total_atoms: Total number of atoms in the execution graph.
        evaluated: Number of atoms that were evaluated.
        short_circuited_na: Number of atoms that were short-circuited as not applicable.
        duration_ms: Execution duration in milliseconds for observability.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    total_atoms: Annotated[int, Field(ge=0, description="Total number of atoms in DAG.")]
    evaluated: Annotated[int, Field(ge=0, description="Number of evaluated atoms.")]
    short_circuited_na: Annotated[int, Field(ge=0, description="Number of short-circuited NA atoms.")]
    duration_ms: Annotated[
        int, Field(default=0, ge=0, description="Execution duration in milliseconds for observability")
    ] = 0


class ExtensionMetricsDTO(V2CoreBase):
    """Pre-calculated numeric or boolean metrics for UI adapters.

    Attributes:
        authenticity_score: Authenticity score between 0.0 and 1.0 or None.
        performative_phrases_count: Count of detected performative phrases or None.
        variance_score: Calculated variance score or None.
        alignment_verdict: Categorical alignment verdict string or None.
        jargon_density: Calculated jargon density float or None.
        total_word_count: Total word count integer or None.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    authenticity_score: Annotated[float | None, Field(default=None, description="Authenticity score")] = None
    performative_phrases_count: Annotated[
        float | None, Field(default=None, description="Performative phrases count")
    ] = None
    variance_score: Annotated[float | None, Field(default=None, description="Variance score")] = None
    alignment_verdict: Annotated[str | None, Field(default=None, description="Alignment verdict")] = None
    jargon_density: Annotated[float | None, Field(default=None, description="Jargon density")] = None
    total_word_count: Annotated[int | None, Field(default=None, ge=0, description="Total word count")] = None
