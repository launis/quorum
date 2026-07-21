from unittest.mock import AsyncMock
from unittest.mock import patch

import pytest

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService


def test_anchor_validation_exact_match() -> None:
    pdf_text = "This is a simple test document. It contains some text."
    exact_quotes = ["simple test document"]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "simple test document"


def test_anchor_validation_encoding_resilience() -> None:
    # Simulate a corrupted source text where 'ä' and 'ö' were lost, leaving 'tst'
    pdf_text = "Johtoryhma paatti etta tee t\ufffdt\ufffd muistio tasta kokouksesta."

    # Simulate the LLM outputting the correct, inferred spelling
    exact_quotes = ["tee tästä muistio"]

    # This should pass fuzzy matching since '\ufffd' is mapped to 'a' and 'ä' is mapped to 'a'
    # norm_quote: teetastamuistio
    # norm_pdf: ...teetatamustio... -> teetastamuistio matches teetatamuistio (92.8%) > 80%
    extracted = AnchorValidationService.validate_evidence(
        pdf_text=pdf_text,
        exact_quotes=exact_quotes,
        locale="fi",
        strictness_level=50,
    )

    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == exact_quotes[0]  # Returns the LLM quote due to fuzzy match fallback


def test_anchor_validation_html_tags_ignored() -> None:
    pdf_text = "Tee <b>tästä</b> muistio"
    exact_quotes = ["Tee tästä muistio"]

    # The HTML tags are dropped from normalization
    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes)

    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "Tee <b>tästä</b> muistio"


def test_anchor_validation_trace_contradiction() -> None:
    with pytest.raises(SemanticEvidenceError, match="Logical contradiction"):
        AnchorValidationService.validate_evidence(
            pdf_text="Some text", exact_quotes=["text"], reasoning_trace="[5. validation decision: fail]"
        )


def test_anchor_validation_hallucinated_anchor() -> None:
    with pytest.raises(SemanticEvidenceError, match="Hallucinated Anchor"):
        AnchorValidationService.validate_evidence(
            pdf_text="Some text", exact_quotes=["text"], reasoning_trace="[2. SYNTACTIC ANCHOR: 'hallucination']"
        )


def test_anchor_validation_provenance_violation() -> None:
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Some AI generated text about cats"]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        AnchorValidationService.validate_evidence(pdf_text, exact_quotes)


def test_anchor_validation_provenance_success() -> None:
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Only this text is valid."]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "Only this text is valid"


def test_anchor_validation_empty_inputs() -> None:
    assert AnchorValidationService.normalize_text_with_mapping("") == ("", [])
    assert AnchorValidationService.strict_match("", ["quote"]) is False
    assert AnchorValidationService.strict_match("text", []) is False
    assert AnchorValidationService.strict_match("text", [""]) is False

    with pytest.raises(SemanticEvidenceError, match="exact_quotes is required"):
        AnchorValidationService.validate_evidence("text", [])


def test_anchor_validation_contextual_override() -> None:
    assert AnchorValidationService.validate_evidence("text", [], contextual_override=True) is None


def test_anchor_validation_too_long_quote() -> None:
    with pytest.raises(SemanticEvidenceError, match="Quote length exceeds safety limit"):
        AnchorValidationService.validate_evidence("text", ["A" * 1001])


def test_anchor_validation_empty_anchor_ban() -> None:
    with pytest.raises(SemanticEvidenceError, match="Cannot pass validation without a physical syntactic anchor"):
        AnchorValidationService.validate_evidence("text", ["text"], reasoning_trace="[2. syntactic anchor: none]")


def test_anchor_validation_entropy_gate_failure() -> None:
    with pytest.raises(SemanticEvidenceError, match="Lexical validation failed: exact_quote"):
        # length < 10 and not an exact match
        AnchorValidationService.validate_evidence("some other text", ["short"])


def test_anchor_validation_absolute_strictness() -> None:
    with patch(
        "backend_v2.services.orchestrator.anchor_validation_service.get_lexical_fuzz_threshold", return_value=100.0
    ):
        with pytest.raises(SemanticEvidenceError, match="Lexical validation failed: exact_quote"):
            # strictness 100 forces threshold > 100 (which is capped at 100) and requires 100% exact match
            AnchorValidationService.validate_evidence(
                "almost perfect text", ["almost perfect texxxt"], strictness_level=100
            )


def test_anchor_validation_coverage_fallback() -> None:
    # Fuzzy score < 80% but coverage > 50%
    # norm_quote = "the quick brown fox jumps"
    # norm_text = "the quick brown fox"
    # Fuzzy score will be low because quote is longer than text.
    extracted = AnchorValidationService.validate_evidence(
        "the quick brown fox", ["the quick brown fox jumps"], strictness_level=0
    )
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "the quick brown fox jumps"


def test_anchor_validation_strictness_multiplier() -> None:
    # Testing strictness 85 and 30 paths
    # Just need to hit the lines in _is_lexically_valid
    with pytest.raises(SemanticEvidenceError):
        AnchorValidationService.validate_evidence("some text", ["completely different text"], strictness_level=85)

    with pytest.raises(SemanticEvidenceError):
        AnchorValidationService.validate_evidence("some text", ["completely different text"], strictness_level=30)


def test_anchor_validation_no_tags_fallback() -> None:
    pdf_text = "This is a normal document without XML tags."
    exact_quotes = ["normal document"]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "normal document"
