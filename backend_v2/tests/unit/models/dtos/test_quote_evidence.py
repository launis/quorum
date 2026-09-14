import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.quote_evidence import (
    LLMExtractedQuote,
    QuoteEvidenceDTO,
    SourceDocumentContext,
)
from backend_v2.models.prompts.common import DESC_EXACT_QUOTE_TEXT


def test_source_document_context_creation() -> None:
    """Test SourceDocumentContext creation and fields."""
    doc = SourceDocumentContext(
        opaque_id="doc_1234567890abcdef",
        text_content="Sample text content.",
        display_name="Sample Document",
    )
    assert doc.opaque_id == "doc_1234567890abcdef"
    assert doc.text_content == "Sample text content."
    assert doc.display_name == "Sample Document"


def test_llm_extracted_quote_basic_and_description() -> None:
    """Test LLMExtractedQuote schema description matches SSOT constant."""
    quote = LLMExtractedQuote(text="Verbatim quote from text.")
    assert quote.text == "Verbatim quote from text."
    assert quote.source_id is None

    schema = LLMExtractedQuote.model_json_schema()
    assert schema["properties"]["text"]["description"] == DESC_EXACT_QUOTE_TEXT


def test_llm_extracted_quote_alias_resolution() -> None:
    """Test resolving source_id alias to its opaque identifier."""
    context = {
        "alias_map": {"doc0": "doc_real_12345"},
        "allowed_dynamic_keys": ["input_prompt"],
        "allowed_mcp_prefixes": ["mcp_"],
    }
    quote = LLMExtractedQuote.model_validate(
        {"source_id": "doc0", "text": "Valid quote"},
        context=context,
    )
    assert quote.source_id == "doc_real_12345"

    quote_dyn = LLMExtractedQuote.model_validate(
        {"source_id": "input_prompt", "text": "Dynamic key quote"},
        context=context,
    )
    assert quote_dyn.source_id == "input_prompt"


def test_llm_extracted_quote_hallucinated_source_id() -> None:
    """Test that hallucinated source_id raises ValueError."""
    context = {
        "alias_map": {"doc0": "doc_real_12345"},
        "allowed_dynamic_keys": [],
        "allowed_mcp_prefixes": [],
    }
    with pytest.raises(ValidationError, match="Hallucinated source_id"):
        LLMExtractedQuote.model_validate(
            {"source_id": "doc99", "text": "Hallucinated quote"},
            context=context,
        )


def test_llm_extracted_quote_no_context_or_empty() -> None:
    """Test LLMExtractedQuote when context is missing or empty."""
    quote_no_ctx = LLMExtractedQuote.model_validate({"source_id": "doc0", "text": "Quote"})
    assert quote_no_ctx.source_id == "doc0"

    quote_empty_ctx = LLMExtractedQuote.model_validate(
        {"source_id": "doc0", "text": "Quote"},
        context={},
    )
    assert quote_empty_ctx.source_id == "doc0"


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
        {"quote": "Another test quote.", "source_alias": ["DOC-3", "Some other string DOC-4", 123]},
        context={"alias_registry": {"DOC-3": "opaque_3", "DOC-4": "opaque_4", "Some other string DOC-4": "opaque_5"}},
    )
    assert "opaque_3" in dto.verified_source_ids
    assert "opaque_4" in dto.verified_source_ids
    assert "123" in dto.unverified_aliases


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
    with pytest.raises(RuntimeError, match="ValidationInfo.context is missing"):
        QuoteEvidenceDTO.model_validate({"quote": "No context quote.", "source_alias": ["DOC-1"]})

    # Allowed if verified_source_ids already in payload
    dto = QuoteEvidenceDTO.model_validate({
        "quote": "Pre-verified quote.",
        "verified_source_ids": ["doc_1"],
    })
    assert dto.verified_source_ids == ["doc_1"]


def test_quote_evidence_empty_or_none_alias():
    """Test QuoteEvidenceDTO with empty or None source_alias."""
    dto_none = QuoteEvidenceDTO.model_validate(
        {"quote": "None alias quote.", "source_alias": None},
        context={"alias_registry": {}},
    )
    assert dto_none.verified_source_ids == []
    assert dto_none.unverified_aliases == []

    dto_empty = QuoteEvidenceDTO.model_validate(
        {"quote": "Empty alias quote.", "source_alias": "   "},
        context={"alias_registry": {}},
    )
    assert dto_empty.verified_source_ids == []
    assert dto_empty.unverified_aliases == []


def test_quote_evidence_custom_alias_without_doc_pattern() -> None:
    """Test custom alias without DOC-X pattern."""
    dto = QuoteEvidenceDTO.model_validate(
        {"quote": "Custom alias.", "source_alias": ["custom_alias_1"]},
        context={"alias_registry": {"custom_alias_1": "opaque_custom"}},
    )
    assert dto.verified_source_ids == ["opaque_custom"]


def test_quote_evidence_non_dict_context() -> None:
    """Test non-dict context handling."""
    quote = LLMExtractedQuote.model_validate(
        {"source_id": "doc0", "text": "Quote"},
        context="invalid_context_type",
    )
    assert quote.source_id == "doc0"

    dto = QuoteEvidenceDTO.model_validate(
        {"quote": "Non-dict context.", "source_alias": ["DOC-1"]},
        context="invalid_context_type",
    )
    assert dto.unverified_aliases == ["DOC-1"]


