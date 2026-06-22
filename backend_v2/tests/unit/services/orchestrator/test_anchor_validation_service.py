import pytest

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService


def test_normalization() -> None:
    """Test Phase 1 Normalization."""
    norm, index = AnchorValidationService.normalize_text_with_mapping("")
    assert norm == ""
    assert index == []
    norm, index = AnchorValidationService.normalize_text_with_mapping("Hello World! 123")
    assert norm == "helloworld123"
    norm, index = AnchorValidationService.normalize_text_with_mapping("Tämä on testi.")
    assert norm == "tämäontesti"
    norm, index = AnchorValidationService.normalize_text_with_mapping("ﬃ")
    assert norm == "ffi"  # ligature


def test_lcs_normalization_retains_raw_pdf_mapping() -> None:
    chunk = "Tämä  on\n\t tär\xadkeä \u00adsopimus."
    quote = "Tämä on tärkeä sopimus."
    extracted = AnchorValidationService.validate_evidence(chunk, [quote])
    assert extracted == ["Tämä  on\n\t tär\xadkeä \u00adsopimus"]


def test_strict_match() -> None:
    """Test Phase 2 Strict O(N) anchoring."""
    pdf_text = "This is a long document about various things. The exact quote we want is here."
    assert AnchorValidationService.strict_match(pdf_text, ["The exact quote we want is here."]) is True
    assert AnchorValidationService.strict_match(pdf_text, ["Something completely different."]) is False
    assert AnchorValidationService.strict_match("", ["quote"]) is False
    assert AnchorValidationService.strict_match(pdf_text, []) is False


def test_validate_evidence_success() -> None:
    """Test the deterministic strict path success."""
    pdf_text = "This is a long document. Very important evidence is right here. And some more."
    quote = "Very important evidence is right here"
    final_quotes = AnchorValidationService.validate_evidence(pdf_text, [quote])
    assert final_quotes == [quote]


def test_validate_evidence_fails_fast() -> None:
    """Test the fail-fast mechanism when evidence is not found in the source text."""
    pdf_text = "The system is currently operational and green."
    quote = "The system has encountered a critical failure."

    with pytest.raises(SemanticEvidenceError) as exc_info:
        AnchorValidationService.validate_evidence(pdf_text, [quote])

    assert "Lexical validation failed" in str(exc_info.value)
    assert quote[:50] in str(exc_info.value)
    assert exc_info.value.status_code == 400


def test_validate_evidence_trace_contradiction_ban() -> None:
    pdf_text = "This is a valid quote."
    quote = "valid quote"
    trace = "Here is my reasoning: [5. VALIDATION DECISION: Fail]"

    with pytest.raises(SemanticEvidenceError) as exc:
        AnchorValidationService.validate_evidence(pdf_text, [quote], reasoning_trace=trace)

    assert "Logical contradiction: Trace concluded Fail, but exact_quotes was populated" in str(exc.value)

    # Test "condition not met" triggers contradiction as well
    trace_cnm = "Here is my reasoning: [5. VALIDATION DECISION: CONDITION NOT MET]"
    with pytest.raises(SemanticEvidenceError) as exc_cnm:
        AnchorValidationService.validate_evidence(pdf_text, [quote], reasoning_trace=trace_cnm)

    assert "Logical contradiction: Trace concluded Fail, but exact_quotes was populated" in str(exc_cnm.value)


def test_validate_evidence_empty_anchor_ban() -> None:
    pdf_text = "This is a valid quote."
    quote = "valid quote"
    trace = "We found it. [2. SYNTACTIC ANCHOR: none]"

    with pytest.raises(SemanticEvidenceError) as exc:
        AnchorValidationService.validate_evidence(pdf_text, [quote], reasoning_trace=trace)

    assert "Anchorless Extraction: Cannot pass validation without a physical syntactic anchor" in str(exc.value)


def test_validate_evidence_lexical_reality_ban_hallucinated() -> None:
    pdf_text = "The quick brown fox jumps over the lazy dog."
    quote = "quick brown fox"
    trace = "[2. SYNTACTIC ANCHOR: 'slow white cat']"

    with pytest.raises(SemanticEvidenceError) as exc:
        AnchorValidationService.validate_evidence(pdf_text, [quote], reasoning_trace=trace)

    assert "Hallucinated Anchor: The anchor 'slow white cat' does not exist in the source text" in str(exc.value)


def test_validate_evidence_lexical_reality_ban_success() -> None:
    pdf_text = "The quick brown fox jumps over the lazy dog."
    quote = "quick brown fox"
    trace = "[2. SYNTACTIC ANCHOR: 'quick brown fox']"

    final_quotes = AnchorValidationService.validate_evidence(pdf_text, [quote], reasoning_trace=trace)
    assert final_quotes == [quote]


def test_html_tag_stripping_retains_mapping() -> None:
    """Test that HTML tags are ignored during normalization but retained in extraction."""
    chunk = "|**Sääntelypaine:** CSRD-direktiivin ja<br>EU-taksonomian kaltaiset säädökset|"
    quote = "CSRD-direktiivin ja EU-taksonomian kaltaiset säädökset"
    extracted = AnchorValidationService.validate_evidence(chunk, [quote])
    assert extracted == ["CSRD-direktiivin ja<br>EU-taksonomian kaltaiset säädökset"]


def test_validate_evidence_hallucinated_chars_fails() -> None:
    """Test that a quote hallucinated by a few characters fails deterministic validation under STRICT level."""
    pdf_text = "Tämä on erittäin tärkeä strateginen muutos."
    # LLM hallucination: "strateginen muutos" -> "strateginen päätös"
    quote = "Tämä on erittäin tärkeä strateginen päätös."

    with pytest.raises(SemanticEvidenceError) as exc_info:
        AnchorValidationService.validate_evidence(pdf_text, [quote], strictness_level=85)

    assert "Lexical validation failed" in str(exc_info.value)


def test_entropy_gate_fails_short_quotes() -> None:
    """Test that short quotes (< 10 chars) bypass fuzzy matching and fail if not 100% exact."""
    pdf_text = "The quick brown fox"
    # 9 chars long quote, with a typo
    quote = "The quack"

    with pytest.raises(SemanticEvidenceError) as exc_info:
        # Even with RELAXED (30) which has 65% threshold, entropy gate blocks it
        AnchorValidationService.validate_evidence(pdf_text, [quote], strictness_level=30)

    assert "Entropy Gate Failure" in str(exc_info.value)


def test_discrete_tiers_fuzzy_fallback_success() -> None:
    """Test that long quotes pass using fuzzy fallback if they meet the tier threshold."""
    pdf_text = "This is a very long document with a minor typo in the source material."
    # 70 chars long, 1 typo ('material' -> 'materiel'). Should pass STANDARD (80%)
    quote = "This is a very long document with a minor typo in the source materiel."

    result = AnchorValidationService.validate_evidence(pdf_text, [quote], strictness_level=50)
    assert result == [quote]


def test_discrete_tiers_fuzzy_fallback_fails_strict() -> None:
    """Test that the same typo fails under STRICT (85) tier which requires 95%."""
    pdf_text = "This document contains a very specific statement that we want to extract completely."
    # Change "completely" to "entirely" -> ~89% match. Will fail STRICT (95%)
    quote = "This document contains a very specific statement that we want to extract entirely."

    with pytest.raises(SemanticEvidenceError) as exc_info:
        AnchorValidationService.validate_evidence(pdf_text, [quote], strictness_level=85)

    assert "Lexical validation failed" in str(exc_info.value)


def test_coverage_based_fallback_accepts_60pct() -> None:
    """Test that a quote with a 60% coverage match is accepted even if RapidFuzz fails."""
    pdf_text = "This is a long document about strategic thinking and decision making."
    # The quote is totally fabricated in the second half.
    # The first half "strategic thinking" is 18 chars.
    # Total quote is "strategic thinking is the key" (29 chars). 18/29 = 62% coverage.
    quote = "strategic thinking is the key"

    # RapidFuzz will score low (< 60%), but coverage safety net (60%) will catch it
    result = AnchorValidationService.validate_evidence(pdf_text, [quote], strictness_level=50)
    assert result == [quote]


def test_coverage_based_fallback_rejects_under_60pct() -> None:
    """Test that a quote under 60% coverage is rejected by the safety net."""
    pdf_text = "This is a long document about strategic thinking and decision making."
    # "strategic" is 9 chars. Total quote is "strategic operations are critical now" (37 chars). 9/37 = 24%
    quote = "strategic operations are critical now"

    with pytest.raises(SemanticEvidenceError) as exc_info:
        AnchorValidationService.validate_evidence(pdf_text, [quote], strictness_level=50)

    assert "Lexical validation failed" in str(exc_info.value)
