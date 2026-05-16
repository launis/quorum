import pytest

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService


def test_normalization() -> None:
    """Test Phase 1 Normalization."""
    # Empty cases
    assert AnchorValidationService.normalize_text("") == ""

    # Lowercasing and regex cleanup
    assert AnchorValidationService.normalize_text("Hello World! 123") == "helloworld123"
    assert AnchorValidationService.normalize_text("Tämä on testi.") == "tämäontesti"
    # NFKC testing
    assert AnchorValidationService.normalize_text("ﬃ") == "ffi"  # ligature


def test_fuzzy_match() -> None:
    """Test Phase 2 RapidFuzz O(N) anchoring."""
    pdf_text = "This is a long document about various things. The exact quote we want is here."

    # Exact match
    assert AnchorValidationService.fuzzy_match(pdf_text, "The exact quote we want is here.") is True

    # Fuzzy match (minor typo)
    assert AnchorValidationService.fuzzy_match(pdf_text, "The ecxat quote we want is here") is True

    # Non-match
    assert AnchorValidationService.fuzzy_match(pdf_text, "Something completely different.") is False

    # Empty cases
    assert AnchorValidationService.fuzzy_match("", "quote") is False
    assert AnchorValidationService.fuzzy_match(pdf_text, "") is False


def test_validate_evidence_success() -> None:
    """Test the deterministic RapidFuzz path success."""
    pdf_text = "This is a long document. Very important evidence is right here. And some more."
    quote = "Very important evidence is right here"

    final_quote = AnchorValidationService.validate_evidence(pdf_text, quote)

    assert final_quote == quote


def test_validate_evidence_fails_fast() -> None:
    """Test the fail-fast mechanism when evidence is not found in the source text."""
    pdf_text = "The system is currently operational and green."
    quote = "The system has encountered a critical failure."

    with pytest.raises(SemanticEvidenceError) as exc_info:
        AnchorValidationService.validate_evidence(pdf_text, quote)

    assert "Lexical validation failed" in str(exc_info.value)
    assert quote in str(exc_info.value)
    # Status code is inherited from SemanticEvidenceError (400 Bad Request typically)
    assert exc_info.value.status_code == 400
