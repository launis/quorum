from unittest.mock import AsyncMock
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO


def test_quote_evidence_validates_raw_string():
    """Test that a raw string with multiple DOC-X is parsed into a list."""
    dto = QuoteEvidenceDTO.model_validate(
        {"quote": "This is a test quote.", "source_alias": "DOC-1, DOC-2"},
        context={"alias_registry": {"DOC-1": "opaque_1", "DOC-2": "opaque_2"}},
    )
    assert dto.quote == "This is a test quote."
    assert dto.verified_source_ids == ["opaque_1", "opaque_2"]
    assert dto.unverified_aliases == []
    assert dto.is_verified is True


def test_quote_evidence_validates_list_of_strings():
    """Test that a list of strings containing DOC-X is parsed correctly."""
    dto = QuoteEvidenceDTO.model_validate(
        {"quote": "Another test quote.", "source_alias": ["DOC-3", "Some other string DOC-4"]},
        context={"alias_registry": {"DOC-3": "opaque_3", "DOC-4": "opaque_4", "Some other string DOC-4": "opaque_5"}},
    )
    assert "opaque_3" in dto.verified_source_ids
    assert "opaque_4" in dto.verified_source_ids
    assert dto.unverified_aliases == []
    assert dto.is_verified is True


def test_quote_evidence_fallback_to_unverified():
    """Test that missing aliases are pushed to unverified_aliases and is_verified is False."""
    dto = QuoteEvidenceDTO.model_validate(
        {"quote": "Missing alias quote.", "source_alias": "DOC-99"}, context={"alias_registry": {"DOC-1": "opaque_1"}}
    )
    assert dto.verified_source_ids == []
    assert dto.unverified_aliases == ["DOC-99"]
    assert dto.is_verified is False


def test_quote_evidence_missing_context():
    """Test behavior when context is not provided."""
    import pytest

    with pytest.raises(RuntimeError, match="ValidationInfo.context is missing"):
        QuoteEvidenceDTO.model_validate({"quote": "No context quote.", "source_alias": ["DOC-1"]})
