import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import LLMExtractedQuote


def test_llm_extracted_quote_parses_valid_data():
    """Test that LLMExtractedQuote parses correctly with valid fields."""
    data = {"source_id": "DOC-1", "text": "This is an exact quote."}
    quote = LLMExtractedQuote.model_validate(data, context={"mcp_source_texts": {"DOC-1": ""}})
    assert quote.source_id == "DOC-1"
    assert quote.text == "This is an exact quote."


def test_llm_extracted_quote_ignores_extra_keys():
    """Test that extra keys in the payload are ignored (extra='ignore')."""
    data = {
        "source_id": "DOC-2",
        "text": "Another exact quote.",
        "hallucinated_key": "some value",
        "reasoning": "because I said so",
    }
    quote = LLMExtractedQuote.model_validate(data, context={"mcp_source_texts": {"DOC-2": ""}})
    assert quote.source_id == "DOC-2"
    assert quote.text == "Another exact quote."
    assert not hasattr(quote, "hallucinated_key")
    assert not hasattr(quote, "reasoning")


def test_llm_extracted_quote_fails_on_missing_fields():
    """Test that missing required fields raise ValidationError."""
    with pytest.raises(ValidationError):
        LLMExtractedQuote.model_validate({"source_id": "DOC-3"}, context={"mcp_source_texts": {}})
