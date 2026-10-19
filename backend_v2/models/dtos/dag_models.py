"""DAG Data Transfer Objects.

This module defines the strictly typed Pydantic V2 models for the Enriched Atom Graph
architecture, including the causal edges, extracted atoms, linked graphs, and the
execution state.

Models enforce `ConfigDict(extra="forbid", strict=True, frozen=True)` to guarantee
architectural Single Source of Truth and Fail-Fast operations.
"""

from typing import Annotated, Self

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator

from backend_v2.models.core_base import coerce_source_quotes_tuple
from backend_v2.models.enums import ExecutionStatus

__all__ = [
    "AtomEvaluationResultDTO",
    "AtomExecutionState",
    "CausalEdge",
    "ChunkPacketDTO",
    "ExtractedAtom",
    "GlobalOntologyMap",
    "LinkedAtomGraph",
    "OntologyEntity",
]


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
        warrant_quotes: Verbatim source quotes grounding the Toulmin inferential warrant.
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
    warrant_quotes: Annotated[
        tuple[str, ...] | None,
        BeforeValidator(coerce_source_quotes_tuple),
        Field(
            default=None,
            description="Verbatim source quotes grounding the Toulmin inferential warrant.",
        ),
    ] = None


class ExtractedAtom(BaseModel):
    """Represents a single extracted claim with resolved anaphora and exact evidence.

    Attributes:
        reasoning: Chain-of-thought reasoning for anaphora resolution and extraction.
        resolved_claim: The standalone, contextualized claim.
        is_logical_deduction: Whether the claim is deduced logically (allowing null quote).
        is_inverse: Whether this is an inverse assertion.
        source_quotes: The exact verbatim quotes from the source text.
        tda_id: The globally unique canonical Opaque Stripe ID of this Topological Directed Atom (tda_ prefix).
        source_id: The spatial anchor (Chunk ID) indicating where the claim originated.
        source_sequence_index: The chronological sequence index indicating extraction order.
        source_input_key: Dynamic input key indicating source document provenance.
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
    is_inverse: Annotated[bool, Field(default=False, description="Set to True if this is an inverse assertion.")] = (
        False
    )
    source_quotes: Annotated[
        tuple[str, ...] | None,
        BeforeValidator(coerce_source_quotes_tuple),
        Field(default=None, description="The exact verbatim quotes from the original text. Immutable evidence."),
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
    source_input_key: Annotated[
        str | None,
        Field(default=None, description="Dynamic input key indicating source document provenance."),
    ] = None

    @model_validator(mode="after")
    def validate_logical_deduction_and_quote(self) -> Self:
        """Validate that source_quotes is provided if and only if is_logical_deduction or is_inverse is False.

        Returns:
            Self: The validated model instance.

        Raises:
            ValueError: If source_quotes is present on a logical deduction or inverse claim,
                or missing on an empirical claim, or contains segments under 30 characters
                when m > 1, or exceeds 3 segments, or segment > 500 chars.
        """
        if (self.is_logical_deduction or self.is_inverse) and self.source_quotes is not None:
            raise ValueError("source_quotes must be None if is_logical_deduction or is_inverse is True.")
        if not self.is_logical_deduction and not self.is_inverse and not self.source_quotes:
            raise ValueError("source_quotes is mandatory unless is_logical_deduction or is_inverse is True.")
        if self.source_quotes is not None:
            if len(self.source_quotes) > 3:
                raise ValueError("source_quotes cannot contain more than 3 segments.")
            if len(self.source_quotes) > 1:
                for seg in self.source_quotes:
                    if len(seg.strip()) < 30:
                        raise ValueError("source_quotes segment floor is at least 30 characters when m > 1.")
            for seg in self.source_quotes:
                if len(seg) > 500:
                    raise ValueError("source_quotes segment exceeds maximum allowed length of 500 characters.")
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
            default_factory=list,
            description=(
                "Implicit AND-list. Atom is evaluated conditionally on parents: "
                "proceeds only if all parents reach their expected_status, otherwise short-circuits to N_A."
            ),
        ),
    ]


class AtomEvaluationResultDTO(BaseModel):
    """Evaluation payload emitted by sensor or pre-flight engine for a single atom.

    Attributes:
        status: Evaluated cognitive or execution status.
        reasoning: Cognitive chain-of-thought justification.
        source_quotes: Exact verbatim quotes in original source language.
        extensions: Extracted XAI extensions.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    status: Annotated[ExecutionStatus, Field(description="Evaluated cognitive or execution status.")]
    reasoning: Annotated[str | None, Field(default=None, description="Cognitive chain-of-thought justification.")] = (
        None
    )
    source_quotes: Annotated[
        tuple[str, ...] | None,
        BeforeValidator(coerce_source_quotes_tuple),
        Field(
            default=None,
            description="Exact verbatim quotes in original source language.",
        ),
    ] = None
    extensions: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Extracted XAI extensions."),
    ]


class AtomExecutionState(BaseModel):
    """Runtime state for a single Atom in the DAG.

    Attributes:
        tda_id: The Opaque Stripe ID of the atom.
        status: The current evaluation status.
        short_circuit_reason_tda_ids: The list of parent IDs that caused a short-circuit (N/A) or block.
        evaluation_reasoning: Detailed reasoning for the assigned status.
        source_quotes: Exact verbatim quotes extracted by the sensor during evaluation in original language.
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
            default_factory=list,
            description="List of tda_id values that caused this atom to short-circuit (Blame determinism).",
        ),
    ]
    evaluation_reasoning: Annotated[
        str | None,
        Field(description="Reasoning generated by the evaluation engine or system error traces."),
    ] = None
    source_quotes: Annotated[
        tuple[str, ...] | None,
        BeforeValidator(coerce_source_quotes_tuple),
        Field(
            default=None,
            description="Exact verbatim quotes extracted by the sensor during evaluation in original language.",
        ),
    ] = None
    extensions: Annotated[
        dict[str, str],
        Field(
            default_factory=dict,
            description="Extracted XAI extensions mapped from BooleanEvaluationResult.",
        ),
    ]


class OntologyEntity(BaseModel):
    """Represents a global entity or concept extracted from the document.

    Attributes:
        name: The name of the entity or concept.
        description: A brief description of what this entity represents in context.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    name: Annotated[str, Field(description="The name of the entity or concept.")]
    description: Annotated[str, Field(description="A brief description of what this entity represents in context.")]


class GlobalOntologyMap(BaseModel):
    """A map of all global entities, concepts, and macro-rules in the document.

    Used to resolve cross-chunk anaphora and conditional logic (GECL).

    Attributes:
        entities: A list of distinct entities, actors, and concepts.
        macro_rules: A list of global rules or conditions that apply across the document.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    entities: Annotated[
        list[OntologyEntity],
        Field(default_factory=list, description="A list of distinct entities, actors, and concepts."),
    ]
    macro_rules: Annotated[
        list[str],
        Field(default_factory=list, description="A list of global rules or conditions that apply across the document."),
    ]


class ChunkPacketDTO(BaseModel):
    """Encapsulates logical document chunk packet boundaries.

    Attributes:
        start_block: Starting block marker ID.
        end_block: Ending block marker ID.
        packet_keys: List of block keys in packet.
    """

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    start_block: Annotated[str, Field(description="Starting block marker ID.")]
    end_block: Annotated[str, Field(description="Ending block marker ID.")]
    packet_keys: Annotated[list[str], Field(description="List of block keys in packet.")]
