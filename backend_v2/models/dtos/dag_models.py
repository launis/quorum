"""DAG Data Transfer Objects.

This module defines the strictly typed Pydantic V2 models for the Enriched Atom Graph
architecture, including the causal edges, extracted atoms, linked graphs, and the
execution state.

Models enforce `ConfigDict(extra="forbid", strict=True, frozen=True)` to guarantee
architectural Single Source of Truth and Fail-Fast operations.
"""

from typing import Annotated, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend_v2.models.enums import ExecutionStatus


class CausalEdge(BaseModel):
    """Represents a directional causal dependency between two atoms in the DAG.

    In accordance with the Local Causal Markov Condition over a Directed Acyclic Graph
    G = (V, E), the joint verification probability factorizes strictly over causal parents:
        P(A_1, ..., A_n | D) = prod_{i=1}^n P(A_i | Parents_G(A_i), D)

    Causal dependencies enforce structural conditioning: downstream child atoms are evaluated
    conditionally upon the deterministic resolution of their causal parents. If any parent fails
    its expected_status, downstream execution is deterministically short-circuited with
    P(A_i = BLOCKED | Parent != expected) = 1.0, assigning ExecutionStatus.N_A without LLM invocation.

    Attributes:
        edge_reasoning: Chain-of-thought reasoning explaining the causal relationship.
        tda_id: The identifier of the parent atom (Topological Directed Atom ID).
        source_id: The identifier of the spatial anchor (e.g., chunk ID).
        expected_status: The expected status of the parent for this edge to be satisfied.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    edge_reasoning: Annotated[
        str,
        Field(
            description=(
                "Chain-of-thought: LLM reasoning about why this causal relationship exists (Reason-then-Format)."
            )
        ),
    ]
    tda_id: Annotated[
        str,
        Field(description="The canonical Opaque Stripe ID of the parent Topological Directed Atom."),
    ]
    source_id: Annotated[str, Field(description="The spatial anchor (Chunk ID) where this edge was identified.")]
    expected_status: Annotated[
        ExecutionStatus,
        Field(
            description="Allows for negative conditions. The dependency is met only if the parent reaches this status."
        ),
    ] = ExecutionStatus.PASSED


class ExtractedAtom(BaseModel):
    """Represents a single extracted claim with resolved anaphora and exact evidence.

    Attributes:
        reasoning: Chain-of-thought reasoning for anaphora resolution and extraction.
        resolved_claim: The standalone, contextualized claim.
        is_logical_deduction: Whether the claim is deduced logically (allowing null quote).
        source_quote: The exact verbatim quote from the source text.
        tda_id: The globally unique canonical Opaque Stripe ID of this Topological Directed Atom (tda_ prefix).
        source_id: The spatial anchor (Chunk ID) indicating where the claim originated.
        source_sequence_index: The chronological sequence index indicating extraction order.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    reasoning: Annotated[
        str, Field(description="Chain-of-thought: reasoning for anaphora resolution and claim extraction.")
    ]
    resolved_claim: Annotated[str, Field(description="The cleaned, standalone claim with all anaphora resolved.")]
    is_logical_deduction: Annotated[
        bool,
        Field(
            default=False, description="Set to True if the claim is deduced purely via logic, allowing a null quote."
        ),
    ] = False
    source_quote: Annotated[
        str | None,
        Field(default=None, description="The exact verbatim quote from the original text. Immutable evidence."),
    ] = None
    tda_id: Annotated[
        str,
        Field(
            description="The canonical Opaque Stripe ID of this Topological Directed Atom.",
            pattern=r"^tda_[a-fA-F0-9]{8,32}$",
        ),
    ]
    source_id: Annotated[str | None, Field(description="The spatial anchor (Chunk ID).")] = None
    source_sequence_index: Annotated[
        int, Field(description="The chronological sequence index indicating extraction order.")
    ]

    @model_validator(mode="after")
    def validate_logical_deduction_and_quote(self) -> Self:
        """Validate that source_quote is provided if and only if is_logical_deduction is False.

        Returns:
            Self: The validated model instance.

        Raises:
            ValueError: If source_quote is present on a logical deduction, or missing on an empirical claim.
        """
        if self.is_logical_deduction and self.source_quote is not None:
            raise ValueError("source_quote must be None if is_logical_deduction is True.")
        if not self.is_logical_deduction and not self.source_quote:
            raise ValueError("source_quote is mandatory unless is_logical_deduction is True.")
        return self


class LinkedAtomGraph(BaseModel):
    """Wraps an ExtractedAtom with its topological dependencies (the DAG).

    Enforces the Local Causal Markov Condition: within Kahn's topological evaluation waves,
    an atom is conditionally isolated given its resolved parents Parents_G(A_i). Evaluation occurs
    if and only if all causal parents satisfy their expected_status. If any dependency fails,
    the node is deterministically short-circuited with P(A_i = N_A | Parent != expected) = 1.0.

    Attributes:
        atom: The extracted claim and its metadata.
        depends_on: Implicit AND-list of causal dependencies that must be met before evaluating this atom.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    atom: Annotated[ExtractedAtom, Field(description="The extracted claim.")]
    depends_on: Annotated[
        list[CausalEdge],
        Field(
            description=(
                "Implicit AND-list. Atom is evaluated conditionally on parents: "
                "proceeds only if all parents reach their expected_status, otherwise short-circuits to N_A."
            ),
            default_factory=list,
        ),
    ] = Field(default_factory=list)


class AtomEvaluationResultDTO(BaseModel):
    """Evaluation payload emitted by sensor or pre-flight engine for a single atom."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    status: Annotated[ExecutionStatus, Field(description="Evaluated cognitive or execution status.")]
    reasoning: Annotated[str | None, Field(default=None, description="Cognitive chain-of-thought justification.")] = (
        None
    )
    source_quote: Annotated[
        str | None,
        Field(
            default=None,
            max_length=500,
            description="Exact verbatim quote in original source language.",
        ),
    ] = None
    extensions: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Extracted XAI extensions."),
    ] = Field(default_factory=dict)


class AtomExecutionState(BaseModel):
    """Runtime state for a single Atom in the DAG.

    Attributes:
        tda_id: The Opaque Stripe ID of the atom.
        status: The current evaluation status.
        short_circuit_reason_tda_ids: The list of parent IDs that caused a short-circuit (N/A) or block.
        evaluation_reasoning: Detailed reasoning for the assigned status.
        source_quote: Exact verbatim quote extracted by the sensor during evaluation in original language.
        extensions: Extracted XAI extensions mapped from BooleanEvaluationResult.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    tda_id: Annotated[str, Field(description="The Opaque Stripe ID of the atom.")]
    status: Annotated[ExecutionStatus, Field(description="The current runtime execution status.")] = (
        ExecutionStatus.PENDING
    )
    short_circuit_reason_tda_ids: Annotated[
        list[str],
        Field(
            description="List of tda_id values that caused this atom to short-circuit (Blame determinism).",
            default_factory=list,
        ),
    ] = Field(default_factory=list)
    evaluation_reasoning: Annotated[
        str | None,
        Field(description="Reasoning generated by the evaluation engine or system error traces."),
    ] = None
    source_quote: Annotated[
        str | None,
        Field(
            default=None,
            max_length=500,
            description="Exact verbatim quote extracted by the sensor during evaluation in original language.",
        ),
    ] = None
    extensions: Annotated[
        dict[str, str],
        Field(description="Extracted XAI extensions mapped from BooleanEvaluationResult.", default_factory=dict),
    ] = Field(default_factory=dict)


class OntologyEntity(BaseModel):
    """Represents a global entity or concept extracted from the document."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    name: Annotated[str, Field(description="The name of the entity or concept.")]
    description: Annotated[str, Field(description="A brief description of what this entity represents in context.")]


class GlobalOntologyMap(BaseModel):
    """A map of all global entities, concepts, and macro-rules in the document.

    Used to resolve cross-chunk anaphora and conditional logic (GECL).
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    entities: Annotated[
        list[OntologyEntity],
        Field(description="A list of distinct entities, actors, and concepts.", default_factory=list),
    ] = Field(default_factory=list)
    macro_rules: Annotated[
        list[str],
        Field(description="A list of global rules or conditions that apply across the document.", default_factory=list),
    ] = Field(default_factory=list)
