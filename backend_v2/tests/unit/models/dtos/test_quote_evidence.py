from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO


def test_quote_evidence_validates_raw_string():
    """Test that a raw string with multiple DOC-X is parsed into a list."""
    dto = QuoteEvidenceDTO.model_validate(
        {"quote": "This is a test quote.", "source_alias": "DOC-1, DOC-2"},
        context={"alias_registry": {"DOC-1": "opaque_1", "DOC-2": "opaque_2"}},
    )
    assert dto.quote == "This is a test quote."
    assert dto.source_alias == ["opaque_1", "opaque_2"]


def test_quote_evidence_validates_list_of_strings():
    """Test that a list of strings containing DOC-X is parsed correctly."""
    dto = QuoteEvidenceDTO.model_validate(
        {"quote": "Another test quote.", "source_alias": ["DOC-3", "Some other string DOC-4"]},
        context={"alias_registry": {"DOC-3": "opaque_3", "DOC-4": "opaque_4", "Some other string DOC-4": "opaque_5"}},
    )
    # The 'DOC-4' is extracted from the complex string, but wait, the logic:
    # if it's a string, it extracts DOC-\d+. So "Some other string DOC-4" yields "DOC-4".
    # DOC-3 yields DOC-3.
    assert "opaque_3" in dto.source_alias
    assert "opaque_4" in dto.source_alias


def test_quote_evidence_fallback_to_unverified():
    """Test that missing aliases map strictly to OpaqueID.UNVERIFIED."""
    dto = QuoteEvidenceDTO.model_validate(
        {"quote": "Missing alias quote.", "source_alias": "DOC-99"}, context={"alias_registry": {"DOC-1": "opaque_1"}}
    )
    assert dto.source_alias == ["OpaqueID.UNVERIFIED"]


def test_quote_evidence_missing_context():
    """Test behavior when context is not provided."""
    import pytest

    with pytest.raises(RuntimeError, match="ValidationInfo.context is missing"):
        QuoteEvidenceDTO.model_validate({"quote": "No context quote.", "source_alias": ["DOC-1"]})
