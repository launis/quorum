"""Data Transfer Objects for Atom Evaluation Results and DAG Telemetry.

SSOT for ErrorDetailsDTO, HydratedAtomDTO, ExtractedValueDTO, AtomResultDTO,
EvaluatedAtomDTO, EvaluationFactsDTO, ExecutionMetricsDTO, and ExtensionMetricsDTO.
"""

from __future__ import annotations

from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

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


class ErrorDetailsDTO(BaseModel):
    """Standardized error details for failed atom executions."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    error_code: Annotated[str, Field(description="Standardized error code, e.g., LLM_TIMEOUT")]
    message: Annotated[str, Field(description="Technical error message or stack trace")]


class HydratedAtomDTO(BaseModel):
    """Static ontology data. Perfectly cacheable.

    Must not contain any dynamic execution-related data.
    """

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    sdui_component: Annotated[LaxSDUIComponentType, Field(description="Server-Driven UI hint for frontend.")]
    resolved_claim: Annotated[str, Field(description="Cleaned claim in human language")]
    source_quote: Annotated[str | None, Field(default=None, description="Verbatim original quote")]


class ExtractedValueDTO(BaseModel):
    """Quantitative or categorical extracted value."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    value: str | float | int | bool
    unit: Annotated[str | None, Field(default=None, description="Unit of measurement, e.g., 'tCO2e' or 'EUR'")]


class AtomResultDTO(BaseModel):
    """Dynamic execution data (DAG node)."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    tda_id: Annotated[str, Field(description="Opaque ID pointing to the hydrated_references dictionary key")]
    matrix_id: Annotated[
        str | None, Field(default=None, description="Opaque ID of the matrix block that requested this evaluation")
    ] = None
    status: LaxExecutionStatus
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
        """Fail-Fast validation for cognitive state consistency."""
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


class ExecutionMetricsDTO(BaseModel):
    """Aggregate atom-level metrics for DAG execution."""

    model_config = ConfigDict(strict=True, frozen=True, extra="forbid")

    total_atoms: int
    evaluated: int
    short_circuited_na: int
    duration_ms: Annotated[int, Field(default=0, description="Execution duration in milliseconds for observability")]


class ExtensionMetricsDTO(V2CoreBase):
    """Pre-calculated numeric or boolean metrics for UI adapters."""

    model_config = ConfigDict(strict=True, extra="forbid")

    authenticity_score: float | None = None
    performative_phrases_count: float | None = None
    variance_score: float | None = None
    alignment_verdict: str | None = None
    jargon_density: float | None = None
    total_word_count: int | None = None
