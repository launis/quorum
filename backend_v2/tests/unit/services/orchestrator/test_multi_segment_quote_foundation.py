"""Dedicated test suite for Multi-Segment Evidence and Causal Horizon foundations.

Verifies:
1. coerce_source_quotes_tuple SSOT conversion and boundary invariants.
2. GateMatchResultDTO strict Pydantic V2 validation, immutability, and boolean truthiness.
3. QuoteEvidenceDTO.get_quotes forward-compatible accessor.
4. AnchorValidationService symmetric index resolution via pdf_map.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.models.core_base import coerce_source_quotes_tuple
from backend_v2.models.dtos.quote_evidence import GateMatchResultDTO, QuoteEvidenceDTO
from backend_v2.services.orchestrator.anchor_validation import AnchorValidationService

# ============================================================================
# Contract 1: coerce_source_quotes_tuple
# ============================================================================


def test_coerce_source_quotes_tuple_single_string_returns_1tuple() -> None:
    """Positive: Single string with whitespace is stripped and wrapped into 1-tuple."""
    result = coerce_source_quotes_tuple("  Evidence sentence here.  ")
    assert result == ("Evidence sentence here.",)


def test_coerce_source_quotes_tuple_list_returns_tuple() -> None:
    """Positive: Sequence of strings is stripped and converted into an immutable tuple."""
    result = coerce_source_quotes_tuple(["Sentence one.", "Sentence two."])
    assert result == ("Sentence one.", "Sentence two.")


def test_coerce_source_quotes_tuple_empty_string_returns_none() -> None:
    """Boundary: Whitespace-only string returns None."""
    assert coerce_source_quotes_tuple("   ") is None
    assert coerce_source_quotes_tuple("") is None


def test_coerce_source_quotes_tuple_none_returns_none() -> None:
    """Boundary: None input returns None."""
    assert coerce_source_quotes_tuple(None) is None


def test_coerce_source_quotes_tuple_generator_or_set_returns_tuple() -> None:
    """Positive: Non-list iterables (sets, generators) are converted into tuples with whitespace stripped."""
    items = {"  Fact alpha  ", "  Fact beta  "}
    result = coerce_source_quotes_tuple(items)
    assert result is not None
    assert set(result) == {"Fact alpha", "Fact beta"}


def test_coerce_source_quotes_tuple_all_whitespace_items_returns_none() -> None:
    """Boundary: Sequence containing only whitespace strings returns None."""
    assert coerce_source_quotes_tuple(["", "   ", "\t\n"]) is None


def test_coerce_source_quotes_tuple_filters_empty_items() -> None:
    """Boundary: Mixed empty and non-empty items filters empty items properly."""
    result = coerce_source_quotes_tuple(["Valid 1", "", "   ", "Valid 2"])
    assert result == ("Valid 1", "Valid 2")


def test_coerce_source_quotes_tuple_prevents_string_shattering() -> None:
    """Invariant: String must not shatter into character tuple tuple('abc') -> ('a', 'b', 'c')."""
    result = coerce_source_quotes_tuple("abc")
    assert result == ("abc",)
    assert len(result) == 1


# ============================================================================
# Contract 2: GateMatchResultDTO
# ============================================================================


def test_gate_match_result_dto_valid_instantiation() -> None:
    """Positive: Instantiation with valid typed attributes succeeds."""
    result = GateMatchResultDTO(is_valid=True, start_idx=10, end_idx=45)
    assert result.is_valid is True
    assert result.start_idx == 10
    assert result.end_idx == 45


def test_gate_match_result_dto_extra_fields_raises_validation_error() -> None:
    """Error Path: Extra unexpected fields are strictly forbidden."""
    with pytest.raises(ValidationError):
        GateMatchResultDTO.model_validate({"is_valid": True, "start_idx": 10, "end_idx": 45, "extra_field": "illegal"})


def test_gate_match_result_dto_immutability() -> None:
    """Invariant: GateMatchResultDTO instances are frozen and immutable."""
    result = GateMatchResultDTO(is_valid=True, start_idx=0, end_idx=10)
    with pytest.raises(ValidationError):
        result.__setattr__("is_valid", False)


def test_gate_match_result_dto_boolean_coercion() -> None:
    """Positive: GateMatchResultDTO evaluates to its is_valid state in boolean expressions."""
    success = GateMatchResultDTO(is_valid=True, start_idx=5, end_idx=15)
    failure = GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)
    assert bool(success) is True
    assert bool(failure) is False


# ============================================================================
# Contract 3: QuoteEvidenceDTO.get_quotes()
# ============================================================================


def test_quote_evidence_dto_get_quotes_with_quote() -> None:
    """Positive: Populated quote returns 1-tuple of stripped quote."""
    dto = QuoteEvidenceDTO(source_quotes="A valid evidence quote.")
    assert dto.get_quotes() == ("A valid evidence quote.",)


def test_quote_evidence_dto_get_quotes_empty_or_none() -> None:
    """Boundary: Whitespace-only quote returns empty tuple."""
    dto_whitespace = QuoteEvidenceDTO(source_quotes="   ")
    assert dto_whitespace.get_quotes() == ()


# ============================================================================
# Contract 4: Symmetric Coordinate Extraction in AnchorValidationService
# ============================================================================


def test_anchor_validation_symmetric_index_resolution_exact() -> None:
    """Positive: Exact match resolves physical document coordinate slice symmetrically via pdf_map."""
    source_text = "Johtoryhma paatti toteuttaa projektin aikataulussa."
    exact_quotes = ["paatti toteuttaa projektin"]

    extracted = AnchorValidationService.validate_evidence(
        pdf_text=source_text,
        exact_quotes=exact_quotes,
        strictness_level=100,
    )

    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "paatti toteuttaa projektin"


def test_anchor_validation_symmetric_index_resolution_fuzzy() -> None:
    """Positive: Fuzzy match with corrupted diacritics slices physical document text symmetrically."""
    source_text = "Johtoryhma paatti etta tee t\ufffdt\ufffd muistio tasta kokouksesta."
    exact_quotes = ["tee t\xe4st\xe4 muistio"]

    extracted = AnchorValidationService.validate_evidence(
        pdf_text=source_text,
        exact_quotes=exact_quotes,
        locale="fi",
        strictness_level=50,
    )

    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "tee t\ufffdt\ufffd muistio"
