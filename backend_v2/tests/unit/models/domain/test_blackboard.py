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
    with pytest.raises(ValidationError, match="source_quote is mandatory unless is_logical_deduction is True"):
        DraftExtractedAtom(
            reasoning="Reasoning",
            resolved_claim="Claim",
            is_logical_deduction=False,
            source_quote=None,
            draft_id="a0",
            source_sequence_index=0,
        )


def test_draft_extracted_atom_quote_with_logical_deduction():
    """Test DraftExtractedAtom fails if quote is present when logical deduction."""
    with pytest.raises(ValidationError, match="source_quote must be None if is_logical_deduction is True"):
        DraftExtractedAtom(
            reasoning="Reasoning",
            resolved_claim="Claim",
            is_logical_deduction=True,
            source_quote="Should be None",
            draft_id="a0",
            source_sequence_index=0,
        )
