import pytest
from pydantic import ValidationError

from backend_v2.models.v2_core import LLMExtractedQuote


def test_llm_extracted_quote_parses_valid_data():
    """Test that LLMExtractedQuote parses correctly with valid fields."""
    data = {"source_alias": "DOC-1", "text": "This is an exact quote."}
    quote = LLMExtractedQuote.model_validate(data)
    assert quote.source_alias == "DOC-1"
    assert quote.text == "This is an exact quote."


def test_llm_extracted_quote_ignores_extra_keys():
    """Test that extra keys in the payload are ignored (extra='ignore')."""
    data = {
        "source_alias": "DOC-2",
        "text": "Another exact quote.",
        "hallucinated_key": "some value",
        "reasoning": "because I said so",
    }
    quote = LLMExtractedQuote.model_validate(data)
    assert quote.source_alias == "DOC-2"
    assert quote.text == "Another exact quote."
    assert not hasattr(quote, "hallucinated_key")


def test_llm_extracted_quote_fails_on_missing_fields():
    """Test that missing required fields raise ValidationError."""
    with pytest.raises(ValidationError):
        LLMExtractedQuote.model_validate({"source_alias": "DOC-3"})

    with pytest.raises(ValidationError):
        LLMExtractedQuote.model_validate({"text": "Missing alias."})
