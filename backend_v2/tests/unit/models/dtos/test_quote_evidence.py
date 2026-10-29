import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.quote_evidence import (
    GateMatchResultDTO,
    LLMExtractedQuote,
    QuoteEvidenceDTO,
    SourceDocumentContext,
)
from backend_v2.models.prompts.common import DESC_EXACT_QUOTE_TEXT


def test_source_document_context_creation() -> None:
    """Test SourceDocumentContext creation and fields."""
    doc = SourceDocumentContext(
        opaque_id="doc_0195f3a0000070018234567890abcdef",
        text_content="Sample text content.",
        display_name="Sample Document",
    )
    assert doc.opaque_id == "doc_0195f3a0000070018234567890abcdef"
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


def test_quote_evidence_validates_raw_string() -> None:
    """Test that a raw string with multiple DOC-X is parsed into a list."""
    dto = QuoteEvidenceDTO.model_validate(
        {"source_quotes": ["This is a test quote."], "source_alias": "DOC-1, DOC-2"},
        context={"alias_registry": {"DOC-1": "opaque_1", "DOC-2": "opaque_2"}},
    )
    assert dto.source_quotes == ("This is a test quote.",)
    assert dto.verified_source_ids == ["opaque_1", "opaque_2"]
    assert dto.unverified_aliases == []
    assert dto.is_verified is True


def test_quote_evidence_validates_list_of_strings() -> None:
    """Test that a list of strings containing DOC-X is parsed correctly."""
    dto = QuoteEvidenceDTO.model_validate(
        {"source_quotes": ["Another test quote."], "source_alias": ["DOC-3", "Some other string DOC-4", 123]},
        context={"alias_registry": {"DOC-3": "opaque_3", "DOC-4": "opaque_4", "Some other string DOC-4": "opaque_5"}},
    )
    assert "opaque_3" in dto.verified_source_ids
    assert "opaque_4" in dto.verified_source_ids
    assert "123" in dto.unverified_aliases


def test_quote_evidence_fallback_to_unverified() -> None:
    """Test that missing aliases are pushed to unverified_aliases and is_verified is False."""
    dto = QuoteEvidenceDTO.model_validate(
        {"source_quotes": ["Missing alias quote."], "source_alias": "DOC-99"},
        context={"alias_registry": {"DOC-1": "opaque_1"}},
    )
    assert dto.verified_source_ids == []
    assert dto.unverified_aliases == ["DOC-99"]
    assert dto.is_verified is False


def test_quote_evidence_missing_context() -> None:
    """Test behavior when context is not provided."""
    with pytest.raises(RuntimeError, match="ValidationInfo.context is missing"):
        QuoteEvidenceDTO.model_validate({"source_quotes": ["No context quote."], "source_alias": ["DOC-1"]})

    # Allowed if verified_source_ids already in payload
    dto = QuoteEvidenceDTO.model_validate(
        {
            "source_quotes": ["Pre-verified quote."],
            "verified_source_ids": ["doc_1"],
        }
    )
    assert dto.verified_source_ids == ["doc_1"]


def test_quote_evidence_empty_or_none_alias() -> None:
    """Test QuoteEvidenceDTO with empty or None source_alias."""
    dto_none = QuoteEvidenceDTO.model_validate(
        {"source_quotes": ["None alias quote."], "source_alias": None},
        context={"alias_registry": {}},
    )
    assert dto_none.verified_source_ids == []
    assert dto_none.unverified_aliases == []

    dto_empty = QuoteEvidenceDTO.model_validate(
        {"source_quotes": ["Empty alias quote."], "source_alias": "   "},
        context={"alias_registry": {}},
    )
    assert dto_empty.verified_source_ids == []
    assert dto_empty.unverified_aliases == []


def test_quote_evidence_custom_alias_without_doc_pattern() -> None:
    """Test custom alias without DOC-X pattern."""
    dto = QuoteEvidenceDTO.model_validate(
        {"source_quotes": ["Custom alias."], "source_alias": ["custom_alias_1"]},
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
        {"source_quotes": ["Non-dict context."], "source_alias": ["DOC-1"]},
        context="invalid_context_type",
    )
    assert dto.unverified_aliases == ["DOC-1"]


def test_gate_match_result_dto_valid_instantiation() -> None:
    """Test GateMatchResultDTO valid instantiation and strict immutability."""
    res = GateMatchResultDTO(is_valid=True, start_idx=10, end_idx=45)
    assert res.is_valid is True
    assert res.start_idx == 10
    assert res.end_idx == 45

    with pytest.raises(ValidationError):
        # Frozen immutability check
        res.__setattr__("is_valid", False)


def test_gate_match_result_dto_extra_fields_raises_validation_error() -> None:
    """Test GateMatchResultDTO extra fields rejection per extra='forbid'."""
    with pytest.raises(ValidationError):
        GateMatchResultDTO.model_validate({"is_valid": True, "start_idx": 10, "end_idx": 45, "extra_field": "illegal"})


def test_quote_evidence_dto_get_quotes_with_quote() -> None:
    """Test get_quotes() returns tuple with valid quote."""
    dto = QuoteEvidenceDTO(source_quotes=("A valid evidence quote.",))
    assert dto.get_quotes() == ("A valid evidence quote.",)


def test_quote_evidence_dto_get_quotes_empty_or_none() -> None:
    """Test get_quotes() returns empty tuple when quote is empty or None."""
    dto = QuoteEvidenceDTO(source_quotes="")
    assert dto.get_quotes() == ()
    dto_none = QuoteEvidenceDTO(source_quotes=None)
    assert dto_none.get_quotes() == ()


def test_quote_evidence_dto_empty_string_resolves_none() -> None:
    """Test that empty string or whitespace resolves source_quotes to None."""
    dto = QuoteEvidenceDTO(source_quotes="   ")
    assert dto.source_quotes is None


def test_gate_match_result_dto_bool() -> None:
    """Test GateMatchResultDTO __bool__ method."""
    assert bool(GateMatchResultDTO(is_valid=True, start_idx=0, end_idx=5)) is True
    assert bool(GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)) is False


def test_quote_evidence_non_dict_and_base_model_inputs() -> None:
    """Test validation from BaseModel and rejection of non-dict inputs."""
    existing_quote = LLMExtractedQuote(text="Sample quote text", source_id="doc_id")
    validated_from_model = LLMExtractedQuote.model_validate(existing_quote)
    assert validated_from_model.text == "Sample quote text"

    with pytest.raises(ValidationError):
        LLMExtractedQuote.model_validate(12345)

    existing_dto = QuoteEvidenceDTO(source_quotes=("Evidence",))
    validated_dto_from_model = QuoteEvidenceDTO.model_validate(existing_dto)
    assert validated_dto_from_model.source_quotes == ("Evidence",)

    with pytest.raises(ValidationError):
        QuoteEvidenceDTO.model_validate("invalid_input_type")
