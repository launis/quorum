"""Domain models for the RAG Pre-Flight Global Atom Blackboard."""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase


class DraftExtractedAtom(V2CoreBase):
    """Draft representation of an atom before AliasEngine hydration."""

    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)

    reasoning: Annotated[str, Field(description="Chain-of-thought logic.")]
    resolved_claim: Annotated[str, Field(description="The cleaned claim.")]
    is_logical_deduction: Annotated[
        bool,
        Field(
            default=False, description="Set to True if the claim is deduced purely via logic, allowing a null quote."
        ),
    ] = False
    source_quote: Annotated[
        str | None,
        Field(default=None, description="The exact verbatim quote. Must be None if is_logical_deduction is True."),
    ] = None
    draft_id: Annotated[str, Field(description="A short temporary ID assigned by LLM, e.g. a0, a1.")]


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
