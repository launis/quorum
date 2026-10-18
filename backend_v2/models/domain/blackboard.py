"""Domain models for the RAG Pre-Flight Global Atom Blackboard."""

from typing import Annotated, Self

from pydantic import BeforeValidator, ConfigDict, Field, model_validator

from backend_v2.models.core_base import V2CoreBase, coerce_source_quotes_tuple


class LLMDraftAtom(V2CoreBase):
    """Schema for LLM to extract atoms using Anchor Hydration."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    reasoning: Annotated[str, Field(description="Chain-of-thought logic.")]
    resolved_claim: Annotated[str, Field(description="The cleaned claim.")]
    is_logical_deduction: Annotated[
        bool,
        Field(
            default=False, description="Set to True if the claim is deduced purely via logic, allowing a null quote."
        ),
    ] = False
    source_block_id: Annotated[
        str | None,
        Field(
            default=None,
            description="The block ID (e.g. B1, B2) where the quote resides. Must be None if is_logical_deduction is True.",
        ),
    ] = None
    draft_id: Annotated[str, Field(description="A short temporary ID assigned by LLM, e.g. a0, a1.")]

    @model_validator(mode="after")
    def validate_logical_deduction_and_source(self) -> Self:
        if self.is_logical_deduction and self.source_block_id is not None:
            raise ValueError("source_block_id must be None if is_logical_deduction is True.")
        if not self.is_logical_deduction and not self.source_block_id:
            raise ValueError("source_block_id is mandatory unless is_logical_deduction is True.")
        return self


class LLMDraftAtomList(V2CoreBase):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)
    atoms: Annotated[list[LLMDraftAtom], Field(description="List of extracted draft atoms.")]


class DraftExtractedAtom(V2CoreBase):
    """Draft representation of an atom after AliasEngine hydration."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    reasoning: Annotated[str, Field(description="Chain-of-thought logic.")]
    resolved_claim: Annotated[str, Field(description="The cleaned claim.")]
    is_logical_deduction: Annotated[
        bool,
        Field(
            default=False, description="Set to True if the claim is deduced purely via logic, allowing a null quote."
        ),
    ] = False
    source_quotes: Annotated[
        tuple[str, ...] | None,
        BeforeValidator(coerce_source_quotes_tuple),
        Field(default=None, description="The exact verbatim quotes. Must be None if is_logical_deduction is True."),
    ] = None
    draft_id: Annotated[str, Field(description="A short temporary ID assigned by LLM, e.g. a0, a1.")]
    source_sequence_index: Annotated[
        int, Field(description="Injected programmatically by the Python worker for chronological sorting.")
    ]

    @model_validator(mode="after")
    def validate_logical_deduction_and_source(self) -> Self:
        if self.is_logical_deduction and self.source_quotes is not None:
            raise ValueError("source_quotes must be None if is_logical_deduction is True.")
        if not self.is_logical_deduction and not self.source_quotes:
            raise ValueError("source_quotes is mandatory unless is_logical_deduction is True.")
        return self


class DraftAtomList(V2CoreBase):
    """Wrapper for a list of draft atoms returned by structured task execution."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    atoms: Annotated[list[DraftExtractedAtom], Field(description="List of extracted draft atoms.")]
    dlq_status: Annotated[
        str | None,
        Field(default=None, description="DLQ sentinel marker. Set to 'FAILED/DLQ' on structural failures."),
    ] = None


class GlobalAtomBlackboard(V2CoreBase):
    """Immutable blackboard aggregating extracted atoms grouped by source input file.

    Attributes:
        atoms_by_input: Mapping of input file keys to their extracted atom lists.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", strict=True)

    atoms_by_input: Annotated[
        dict[str, DraftAtomList],
        Field(description="Extracted atoms keyed by their source input file key (e.g. 'product_text')."),
    ]
    is_data_starved: Annotated[
        bool,
        Field(default=False, description="Set to True when RAG preflight skips extraction due to data starvation."),
    ] = False

    def get_all_atom_ids(self) -> list[str]:
        """Returns a flat list of all draft_id strings across all inputs."""
        ids = []
        for v in self.atoms_by_input.values():
            for atom in v.atoms:
                ids.append(atom.draft_id)
        return list(set(ids))

    def to_markdown_synthesis_injection(self) -> str:
        """Serializes the blackboard into a structured Markdown payload for LLM injection."""
        lines = []
        for input_key, atom_list in self.atoms_by_input.items():
            lines.append(f"## SOURCE: {input_key}")
            for atom in atom_list.atoms:
                lines.append(f"### ATOM: {atom.draft_id}")
                lines.append(f"**Claim**: {atom.resolved_claim}")
                if atom.is_logical_deduction:
                    lines.append("**Quote**: [Logical Deduction]")
                elif atom.source_quotes:
                    lines.append(f"**Quote**: {' [...] '.join(atom.source_quotes)}")
                else:
                    lines.append("**Quote**: [None]")
                lines.append(f"**Reasoning**: {atom.reasoning}")
                lines.append("")
        return "\n".join(lines)
