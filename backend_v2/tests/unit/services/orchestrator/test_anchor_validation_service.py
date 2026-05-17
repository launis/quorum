import pytest

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService


def test_normalization() -> None:
    """Test Phase 1 Normalization."""
    assert AnchorValidationService.normalize_text("") == ""
    assert AnchorValidationService.normalize_text("Hello World! 123") == "helloworld123"
    assert AnchorValidationService.normalize_text("Tämä on testi.") == "tämäontesti"
    assert AnchorValidationService.normalize_text("ﬃ") == "ffi"  # ligature


def test_fuzzy_match() -> None:
    """Test Phase 2 RapidFuzz O(N) anchoring."""
    pdf_text = "This is a long document about various things. The exact quote we want is here."
    assert AnchorValidationService.fuzzy_match(pdf_text, "The exact quote we want is here.") is True
    assert AnchorValidationService.fuzzy_match(pdf_text, "The ecxat quote we want is here") is True
    assert AnchorValidationService.fuzzy_match(pdf_text, "Something completely different.") is False
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
    assert exc_info.value.status_code == 400


def test_validate_evidence_trace_contradiction_ban() -> None:
    pdf_text = "This is a valid quote."
    quote = "valid quote"
    trace = "Here is my reasoning: [5. VALIDATION DECISION: Fail]"
    
    with pytest.raises(SemanticEvidenceError) as exc:
        AnchorValidationService.validate_evidence(pdf_text, quote, reasoning_trace=trace)
        
    assert "Logical contradiction: Trace concluded Fail, but exact_quote was populated" in str(exc.value)


def test_validate_evidence_empty_anchor_ban() -> None:
    pdf_text = "This is a valid quote."
    quote = "valid quote"
    trace = "We found it. [2. SYNTACTIC ANCHOR: none]"
    
    with pytest.raises(SemanticEvidenceError) as exc:
        AnchorValidationService.validate_evidence(pdf_text, quote, reasoning_trace=trace)
        
    assert "Anchorless Extraction: Cannot pass validation without a physical syntactic anchor" in str(exc.value)


def test_validate_evidence_lexical_reality_ban_hallucinated() -> None:
    pdf_text = "The quick brown fox jumps over the lazy dog."
    quote = "quick brown fox"
    trace = "[2. SYNTACTIC ANCHOR: 'slow white cat']"
    
    with pytest.raises(SemanticEvidenceError) as exc:
        AnchorValidationService.validate_evidence(pdf_text, quote, reasoning_trace=trace)
        
    assert "Hallucinated Anchor: The anchor 'slow white cat' does not exist in the source text" in str(exc.value)


def test_validate_evidence_lexical_reality_ban_success() -> None:
    pdf_text = "The quick brown fox jumps over the lazy dog."
    quote = "quick brown fox"
    trace = "[2. SYNTACTIC ANCHOR: 'quick brown fox']"
    
    final_quote = AnchorValidationService.validate_evidence(pdf_text, quote, reasoning_trace=trace)
    assert final_quote == quote
