"""Unit tests for evidence_validator.py (validate_evidence provenance, syntactic anchors, and slicing)."""

import pytest

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.models.enums import TargetSpeaker
from backend_v2.services.orchestrator.anchor_validation.evidence_validator import validate_evidence
from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import strict_match


def test_anchor_validation_exact_match() -> None:
    pdf_text = "This is a simple test document. It contains some text."
    exact_quotes = ["simple test document"]

    extracted = validate_evidence(pdf_text, exact_quotes)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "simple test document"


def test_anchor_validation_encoding_resilience() -> None:
    pdf_text = "Johtoryhma paatti etta tee t\ufffdt\ufffd muistio tasta kokouksesta."
    exact_quotes = ["tee tästä muistio"]

    extracted = validate_evidence(
        pdf_text=pdf_text,
        exact_quotes=exact_quotes,
        locale="fi",
        strictness_level=50,
    )

    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "tee t\ufffdt\ufffd muistio"


def test_anchor_validation_html_tags_ignored() -> None:
    pdf_text = "Tee <b>tästä</b> muistio"
    exact_quotes = ["Tee tästä muistio"]

    extracted = validate_evidence(pdf_text, exact_quotes)

    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "Tee <b>tästä</b> muistio"


def test_anchor_validation_trace_contradiction() -> None:
    with pytest.raises(SemanticEvidenceError, match="Logical contradiction"):
        validate_evidence(pdf_text="Some text", exact_quotes=["text"], reasoning_trace="[5. validation decision: fail]")


def test_anchor_validation_hallucinated_anchor() -> None:
    with pytest.raises(SemanticEvidenceError, match="Hallucinated Anchor"):
        validate_evidence(
            pdf_text="Some text", exact_quotes=["text"], reasoning_trace="[2. SYNTACTIC ANCHOR: 'hallucination']"
        )


def test_anchor_validation_provenance_violation() -> None:
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Some AI generated text about cats"]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        validate_evidence(pdf_text, exact_quotes)


def test_anchor_validation_provenance_user_rejects_ai_text() -> None:
    """Cross-speaker rejection: USER claim quoting AI text in dialogue triggers SemanticEvidenceError."""
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Some AI generated text about cats"]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)


def test_anchor_validation_provenance_ai_rejects_user_text() -> None:
    """Cross-speaker rejection (SYMMETRIC - Amendment 3): AI claim quoting user text in dialogue triggers SemanticEvidenceError."""
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Only this text is valid."]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.AI)


def test_anchor_validation_provenance_success() -> None:
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Only this text is valid."]

    extracted = validate_evidence(pdf_text, exact_quotes)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "Only this text is valid"


def test_anchor_validation_provenance_user_accepts_user_text() -> None:
    """Valid quote acceptance: USER claim quoting user text in dialogue passes."""
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Only this text is valid."]

    extracted = validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "Only this text is valid"


def test_anchor_validation_provenance_ai_accepts_ai_text() -> None:
    """Valid quote acceptance: AI claim quoting AI text in dialogue passes."""
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Some AI generated text about cats"]

    extracted = validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.AI)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "Some AI generated text about cats"


def test_anchor_validation_non_chat_document_user_claim_passes() -> None:
    """Non-chat document: USER claim quoting full document text without dialogue tags passes."""
    pdf_text = "Tämä on yksittäisen kirjoittajan strateginen muistio ilman dialogia."
    exact_quotes = ["strateginen muistio"]

    extracted = validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "strateginen muistio"


def test_anchor_validation_provenance_user_rejects_assignment_text() -> None:
    """Provenance protection: USER claim quoting assignment brief raises PROVENANCE_VIOLATION."""
    pdf_text = (
        "<assignment_context>Analyze the financial liquidity risk under Basel III.</assignment_context> "
        "<user_payload>The liquidity coverage ratio was maintained at 120% throughout the fiscal period.</user_payload>"
    )
    exact_quotes = ["Analyze the financial liquidity risk under Basel III."]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)


def test_anchor_validation_provenance_ai_rejects_assignment_text() -> None:
    """Provenance protection: AI claim quoting assignment brief raises PROVENANCE_VIOLATION."""
    pdf_text = (
        "<assignment_context>Analyze the financial liquidity risk under Basel III.</assignment_context> "
        "<ai_draft_context>AI drafted response regarding risk metrics.</ai_draft_context>"
    )
    exact_quotes = ["Analyze the financial liquidity risk under Basel III."]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.AI)


def test_anchor_validation_provenance_only_assignment_rejects_all_quotes() -> None:
    """Provenance protection: Document with solely assignment_context rejects extraction attempts."""
    pdf_text = "<assignment_context>General instructions and rubric for candidate evaluation.</assignment_context>"
    exact_quotes = ["General instructions and rubric"]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)


def test_anchor_validation_provenance_user_accepts_user_text_with_assignment() -> None:
    """Provenance protection: Valid quote from user_payload passes when assignment_context is present."""
    pdf_text = (
        "<assignment_context>Analyze the financial liquidity risk under Basel III.</assignment_context> "
        "<user_payload>The liquidity coverage ratio was maintained at 120 throughout the fiscal period.</user_payload>"
    )
    exact_quotes = ["The liquidity coverage ratio was maintained at 120"]

    extracted = validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "The liquidity coverage ratio was maintained at 120"


def test_anchor_validation_contextual_override() -> None:
    assert validate_evidence("text", [], contextual_override=True) is None


def test_anchor_validation_too_long_quote(monkeypatch: pytest.MonkeyPatch) -> None:
    from backend_v2.settings import Settings

    monkeypatch.setattr(
        "backend_v2.services.orchestrator.anchor_validation.evidence_validator.get_settings",
        lambda: Settings(max_citation_span_chars=1000),
    )
    with pytest.raises(SemanticEvidenceError, match="Quote length exceeds safety limit"):
        validate_evidence("text", ["A" * 1001])


def test_anchor_validation_empty_anchor_ban() -> None:
    with pytest.raises(SemanticEvidenceError, match="Cannot pass validation without a physical syntactic anchor"):
        validate_evidence("text", ["text"], reasoning_trace="[2. syntactic anchor: none]")


def test_anchor_validation_entropy_gate_failure() -> None:
    with pytest.raises(SemanticEvidenceError, match="Lexical validation failed: exact_quote"):
        validate_evidence("some other text", ["short"])


def test_anchor_validation_absolute_strictness() -> None:
    with pytest.raises(SemanticEvidenceError, match="Lexical validation failed: exact_quote"):
        validate_evidence("almost perfect text", ["almost perfect texxxt"], lexical_strictness_level=100)


def test_anchor_validation_coverage_fallback() -> None:
    extracted = validate_evidence("the quick brown fox", ["the quick brown fox jumps"], lexical_strictness_level=0)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "the quick brown fox"


def test_anchor_validation_strictness_multiplier() -> None:
    source_text = "Työryhmä sitoutui johtajuudessaan selkeisiin tavoitteisiin."
    inflected_quote = ["johtajuus ja selkeät tavoitteet"]

    extracted = validate_evidence(source_text, inflected_quote, lexical_strictness_level=50, locale="fi")
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "johtajuudessaan selkeisiin tavoitteisiin"

    with pytest.raises(SemanticEvidenceError):
        validate_evidence(source_text, ["talousarvio ja budjetti"], lexical_strictness_level=50, locale="fi")

    with pytest.raises(SemanticEvidenceError, match="Lexical validation failed: exact_quote"):
        validate_evidence(source_text, inflected_quote, lexical_strictness_level=100, locale="fi")

    with pytest.raises(SemanticEvidenceError):
        validate_evidence("some text", ["completely different text"], lexical_strictness_level=85)

    with pytest.raises(SemanticEvidenceError):
        validate_evidence("some text", ["completely different text"], lexical_strictness_level=30)


def test_anchor_validation_no_tags_fallback() -> None:
    pdf_text = "This is a normal document without XML tags."
    exact_quotes = ["normal document"]

    extracted = validate_evidence(pdf_text, exact_quotes)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "normal document"


def test_anchor_validation_quote_normalized_to_empty_string_fails() -> None:
    pdf_text = "Standard valid document text."
    with pytest.raises(SemanticEvidenceError, match="normalized to empty string"):
        validate_evidence(pdf_text, ["???"])


def test_anchor_validation_provenance_empty_allowed_stream_fails() -> None:
    pdf_text = "<ai_draft_context>Model output here.</ai_draft_context>"
    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        validate_evidence(pdf_text, ["Model output"], target_speaker=TargetSpeaker.USER)


def test_anchor_validation_inverted_segment_order_raises_semantic_error() -> None:
    """Error-path ISTQB test: tuple of 2 segments where segment 2 precedes segment 1 in source text."""
    pdf_text = "Ensimmäinen lause esitetään tässä järjestyksessä. Toinen lause tulee vasta tämän jälkeen tekstissä."
    seg1 = "Ensimmäinen lause esitetään tässä järjestyksessä."
    seg2 = "Toinen lause tulee vasta tämän jälkeen tekstissä."

    with pytest.raises(SemanticEvidenceError, match="Inverted segment order"):
        validate_evidence(pdf_text, (seg2, seg1))

    match_res = strict_match(pdf_text, (seg2, seg1))
    assert match_res.is_valid is False


def test_anchor_validation_span_exceeding_1000_chars_raises_semantic_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Boundary ISTQB test: tuple of 2 segments where (e2 - s1) exceeds 1 000 characters when max_citation_span_chars=1000."""
    from backend_v2.settings import Settings

    bounded_settings = Settings(max_citation_span_chars=1000)
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.anchor_validation.evidence_validator.get_settings",
        lambda: bounded_settings,
    )
    monkeypatch.setattr(
        "backend_v2.services.orchestrator.anchor_validation.lexical_normalizer.get_settings",
        lambda: bounded_settings,
    )
    seg1 = "Tämä on ensimmäinen riittävän pitkä lause alussa."
    intervening = "a" * 1005
    seg2 = "Tämä on toinen riittävän pitkä lause lopussa."
    pdf_text = f"{seg1} {intervening} {seg2}"

    with pytest.raises(SemanticEvidenceError, match="Bounding span exceeds limit"):
        validate_evidence(pdf_text, (seg1, seg2))

    match_res = strict_match(pdf_text, (seg1, seg2))
    assert match_res.is_valid is False


def test_anchor_validation_cross_document_chimera_raises_semantic_error() -> None:
    """Error-path ISTQB test: segment 1 from document A and segment 2 from document B across directives."""
    doc_text = (
        '<ai_context_directive document="doc_1">\n'
        "Ensimmäinen dokumentti sisältää tämän täsmällisen lauseen.\n"
        "</ai_context_directive>\n"
        '<ai_context_directive document="doc_2">\n'
        "Toinen dokumentti esittelee tämän toisen lauseen erikseen.\n"
        "</ai_context_directive>"
    )
    seg1 = "Ensimmäinen dokumentti sisältää tämän täsmällisen lauseen."
    seg2 = "Toinen dokumentti esittelee tämän toisen lauseen erikseen."

    with pytest.raises(SemanticEvidenceError, match="Cross-document chimera"):
        validate_evidence(doc_text, (seg1, seg2))


def test_anchor_validation_multi_segment_floor_under_30_chars_raises_semantic_error() -> None:
    """Boundary ISTQB test: multi-segment citation with one segment under 30 characters raises SemanticEvidenceError."""
    pdf_text = "Tämä on ensimmäinen riittävän pitkä lause dokumentissa. Lyhyt lause täällä."
    seg1 = "Tämä on ensimmäinen riittävän pitkä lause dokumentissa."
    seg2 = "Lyhyt lause täällä."

    with pytest.raises(SemanticEvidenceError, match="under floor"):
        validate_evidence(pdf_text, (seg1, seg2))

    match_res = strict_match(pdf_text, (seg1, seg2))
    assert match_res.is_valid is False


def test_anchor_validation_validate_evidence_edge_cases() -> None:
    """Tests validate_evidence edge cases: empty quotes, empty norm_pdf, directives."""
    with pytest.raises(SemanticEvidenceError, match="exact_quotes is required"):
        validate_evidence("pdf text", ())

    with pytest.raises(SemanticEvidenceError, match="normalized to empty string"):
        validate_evidence("pdf text", ("   ",))

    with pytest.raises(SemanticEvidenceError, match="source text normalized to empty string"):
        validate_evidence("   ", ("valid quote text at least ten chars",))

    directive_text = (
        "<ai_context_directive id='doc1'>\n"
        "Tämä on ensimmäinen lause direktiivissä riittävän pitkänä.\n"
        "Tämä on toinen lause direktiivissä riittävän pitkänä.\n"
        "</ai_context_directive>"
    )
    seg1 = "Tämä on ensimmäinen lause direktiivissä riittävän pitkänä."
    seg2 = "Tämä on toinen lause direktiivissä riittävän pitkänä."
    res = validate_evidence(directive_text, (seg1, seg2))
    assert res is not None
    assert len(res) == 2

    fuzzy_directive = (
        "<ai_context_directive id='doc1'>\n"
        "Tämä on ensimmäinen lause direktiivissä riittävän pitkänä tekstinä.\n"
        "</ai_context_directive>"
    )
    seg_fuzzy = "Tämä on ensimmäinen lause direktiivissä riittävän pitkänä tekstina."
    res_fuzzy = validate_evidence(fuzzy_directive, (seg_fuzzy,), strictness_level=50)
    assert res_fuzzy is not None

    pdf_occ = f"{seg2} {seg1} Lyhyt väli. {seg1} Sen jälkeen {seg2}"
    res_occ = validate_evidence(pdf_occ, (seg1, seg2))
    assert res_occ is not None
    assert len(res_occ) == 2


def test_anchor_validation_candidate_s1_missing_subsequent_occurrence() -> None:
    """Tests candidate s1 where seg1 occurs again at the end with no subsequent seg2."""
    seg1 = "Ensimmäinen lause esiintyy tekstissä useampaan kertaan."
    seg2 = "Toinen lause seuraa vain ensimmäistä esiintymää heti."
    pdf_text = f"{seg1} {seg2} Loppuosa tekstiä. {seg1}"
    res = validate_evidence(pdf_text, (seg1, seg2))
    assert res is not None
    assert len(res) == 2


def test_strictness_decoupling_high_scoring_allows_morphology() -> None:
    """Verify high scoring strictness (85) with normal lexical strictness (50) allows morphology."""
    source_text = "Työryhmä sitoutui johtajuudessaan selkeisiin tavoitteisiin ja strategiaan."
    inflected_quote = ["johtajuus ja selkeät tavoitteet"]

    extracted = validate_evidence(
        pdf_text=source_text,
        exact_quotes=inflected_quote,
        locale="fi",
        strictness_level=85,
        lexical_strictness_level=50,
    )

    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "johtajuudessaan selkeisiin tavoitteisiin"


def test_strictness_decoupling_absolute_lexical_rejects_morphology() -> None:
    """Verify absolute lexical strictness (100) rejects morphology even when scoring strictness is normal."""
    source_text = "Työryhmä sitoutui johtajuudessaan selkeisiin tavoitteisiin ja strategiaan."
    inflected_quote = ["johtajuus ja selkeät tavoitteet"]

    with pytest.raises(SemanticEvidenceError) as exc_info:
        validate_evidence(
            pdf_text=source_text,
            exact_quotes=inflected_quote,
            locale="fi",
            strictness_level=85,
            lexical_strictness_level=100,
        )

    assert "not found" in str(exc_info.value)


def test_anchor_validation_directive_morphological_fallback_and_s1_retries() -> None:
    """Tests directive morphological match (non-strict_match) and candidate s_1 retry paths."""
    # 1. Directive where strict_match is False (inflection) and is_lexically_valid succeeds
    directive_morph = (
        "<ai_context_directive id='doc1'>\n"
        "Työryhmä sitoutui johtajuudessaan selkeisiin tavoitteisiin ja strategiaan.\n"
        "</ai_context_directive>"
    )
    res_morph = validate_evidence(
        pdf_text=directive_morph,
        exact_quotes=("johtajuus ja selkeät tavoitteet",),
        locale="fi",
        strictness_level=50,
        lexical_strictness_level=50,
    )
    assert res_morph is not None
    assert len(res_morph) == 1

    # 2. Candidate s_1 where first s_1 exceeds MAX_CITATION_SPAN_CHARS (1000) and second s_1 succeeds
    from unittest.mock import patch

    from backend_v2.settings import Settings

    seg1 = "Ensimmäinen lause esiintyy sekä kaukana alussa että lopussa."
    seg2 = "Toinen lause seuraa vasta toista esiintymää lähellä lopussa."
    long_gap = "x" * 1050
    pdf_s1_span = f"{seg1} {long_gap} {seg1} {seg2}"
    bounded = Settings(max_citation_span_chars=1000)
    with (
        patch("backend_v2.services.orchestrator.anchor_validation.evidence_validator.get_settings", return_value=bounded),
        patch("backend_v2.services.orchestrator.anchor_validation.lexical_normalizer.get_settings", return_value=bounded),
        patch("backend_v2.services.orchestrator.anchor_validation.lexical_matcher.get_settings", return_value=bounded),
    ):
        res_span_retry = validate_evidence(pdf_s1_span, (seg1, seg2))
    assert res_span_retry is not None
    assert len(res_span_retry) == 2

    # 3. Candidate s_1 with 3 segments where pairwise forward order holds (seg2->seg3 at start, seg1->seg2 at end)
    #    so _match_candidate_s1_chain hits next_pos == -1 for seg3 after the trailing seg2
    seg3 = "Kolmas lause esiintyy vain dokumentin alkupuolella heti toisen perässä."
    pdf_broken_3 = f"{seg2} {seg3} Väliosa tekstiä. {seg1} {seg2}"
    res_broken_3 = validate_evidence(pdf_broken_3, (seg1, seg2, seg3))
    assert res_broken_3 is not None
    assert len(res_broken_3) == 3
