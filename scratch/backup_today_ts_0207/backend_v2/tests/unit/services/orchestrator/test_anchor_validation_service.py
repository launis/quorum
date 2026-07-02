import pytest

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService


def test_anchor_validation_exact_match():
    pdf_text = "This is a simple test document. It contains some text."
    exact_quotes = ["simple test document"]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes)
    assert len(extracted) == 1
    assert extracted[0] == "simple test document"


def test_anchor_validation_encoding_resilience():
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

    assert len(extracted) == 1
    assert extracted[0] == exact_quotes[0]  # Returns the LLM quote due to fuzzy match fallback


def test_anchor_validation_html_tags_ignored():
    pdf_text = "Tee <b>tästä</b> muistio"
    exact_quotes = ["Tee tästä muistio"]

    # The HTML tags are dropped from normalization
    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes)

    assert len(extracted) == 1
    assert extracted[0] == "Tee <b>tästä</b> muistio"


def test_anchor_validation_trace_contradiction():
    with pytest.raises(SemanticEvidenceError, match="Logical contradiction"):
        AnchorValidationService.validate_evidence(
            pdf_text="Some text", exact_quotes=["text"], reasoning_trace="[5. validation decision: fail]"
        )


def test_anchor_validation_hallucinated_anchor():
    with pytest.raises(SemanticEvidenceError, match="Hallucinated Anchor"):
        AnchorValidationService.validate_evidence(
            pdf_text="Some text", exact_quotes=["text"], reasoning_trace="[2. SYNTACTIC ANCHOR: 'hallucination']"
        )
