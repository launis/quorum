"""Unit tests for the RAG Pre-Flight Global Atom Blackboard."""

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.blackboard import DraftExtractedAtom, LLMDraftAtom


def test_llm_draft_atom_missing_quote_not_logical():
    """Test LLMDraftAtom fails if quote is missing and not logical deduction."""
    with pytest.raises(ValidationError, match="source_block_id is mandatory unless is_logical_deduction is True"):
        LLMDraftAtom(
            reasoning="Reasoning",
            resolved_claim="Claim",
            is_logical_deduction=False,
            source_block_id=None,
            draft_id="a0",
        )


def test_llm_draft_atom_quote_with_logical_deduction():
    """Test LLMDraftAtom fails if quote is present when logical deduction."""
    with pytest.raises(ValidationError, match="source_block_id must be None if is_logical_deduction is True"):
        LLMDraftAtom(
            reasoning="Reasoning",
            resolved_claim="Claim",
            is_logical_deduction=True,
            source_block_id="B1",
            draft_id="a0",
        )


def test_draft_extracted_atom_missing_quote_not_logical():
    """Test DraftExtractedAtom fails if quote is missing and not logical deduction."""
    with pytest.raises(ValidationError, match="source_quotes is mandatory unless is_logical_deduction is True"):
        DraftExtractedAtom(
            reasoning="Reasoning",
            resolved_claim="Claim",
            is_logical_deduction=False,
            source_quotes=None,
            draft_id="a0",
            source_sequence_index=0,
        )


def test_draft_extracted_atom_quote_with_logical_deduction():
    """Test DraftExtractedAtom fails if quote is present when logical deduction."""
    with pytest.raises(ValidationError, match="source_quotes must be None if is_logical_deduction is True"):
        DraftExtractedAtom(
            reasoning="Reasoning",
            resolved_claim="Claim",
            is_logical_deduction=True,
            source_quotes=("Should be None",),
            draft_id="a0",
            source_sequence_index=0,
        )


def test_draft_extracted_atom_multi_segment_quotes_valid():
    """Test DraftExtractedAtom valid with multi-segment quotes tuple."""
    atom = DraftExtractedAtom(
        reasoning="Valid analytical reasoning premise.",
        resolved_claim="Verifiable claim statement.",
        is_logical_deduction=False,
        source_quotes=("Premise quote with sufficient length.", "Conclusion quote with sufficient length."),
        draft_id="a0",
        source_sequence_index=0,
    )
    assert atom.source_quotes == ("Premise quote with sufficient length.", "Conclusion quote with sufficient length.")


def test_llm_draft_atom_list_and_draft_atom_list() -> None:
    """Test LLMDraftAtomList and DraftAtomList instantiation and validation."""
    from backend_v2.models.domain.blackboard import DraftAtomList, LLMDraftAtomList

    llm_atom = LLMDraftAtom(
        reasoning="CoT deduction",
        resolved_claim="Logical deduction claim",
        is_logical_deduction=True,
        source_block_id=None,
        draft_id="a0",
    )
    atom_list = LLMDraftAtomList(atoms=[llm_atom])
    assert len(atom_list.atoms) == 1
    assert atom_list.atoms[0].draft_id == "a0"

    draft_atom = DraftExtractedAtom(
        reasoning="Deduction reasoning",
        resolved_claim="Logical claim",
        is_logical_deduction=True,
        source_quotes=None,
        draft_id="a0",
        source_sequence_index=1,
    )
    draft_list = DraftAtomList(atoms=[draft_atom], dlq_status="FAILED/DLQ")
    assert draft_list.dlq_status == "FAILED/DLQ"
    assert len(draft_list.atoms) == 1


def test_global_atom_blackboard_operations() -> None:
    """Test GlobalAtomBlackboard aggregation, IDs extraction, and Markdown serialization."""
    from backend_v2.models.domain.blackboard import DraftAtomList, GlobalAtomBlackboard

    atom_with_quote = DraftExtractedAtom(
        reasoning="Direct empirical evidence.",
        resolved_claim="Product launch confirmed.",
        is_logical_deduction=False,
        source_quotes=("Confirmed launch date.", "Next quarter target."),
        draft_id="a1",
        source_sequence_index=0,
    )
    atom_deduced = DraftExtractedAtom(
        reasoning="Derived proposition from earlier context.",
        resolved_claim="Implicit market positioning.",
        is_logical_deduction=True,
        source_quotes=None,
        draft_id="a2",
        source_sequence_index=1,
    )
    atom_list = DraftAtomList(atoms=[atom_with_quote, atom_deduced])

    bb = GlobalAtomBlackboard(
        atoms_by_input={"product_doc": atom_list},
        is_data_starved=False,
    )

    ids = bb.get_all_atom_ids()
    assert ids == ["a1", "a2"]

    md = bb.to_markdown_synthesis_injection()
    assert "## SOURCE: product_doc" in md
    assert "### ATOM: a1" in md
    assert "**Quote**: Confirmed launch date. [...] Next quarter target." in md
    assert "### ATOM: a2" in md
    assert "**Quote**: [Logical Deduction]" in md
