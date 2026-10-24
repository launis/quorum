"""Unit tests for lexical_normalizer.py (normalize_text_with_mapping, strict_match, calculate_fuzzy_score)."""

import pytest

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.models.dtos.quote_evidence import GateMatchResultDTO
from backend_v2.services.orchestrator.anchor_validation import AnchorValidationService
from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import (
    MAX_CITATION_SPAN_CHARS,
    MIN_ENTROPY_GATE_CHARS,
    MIN_MULTI_SEGMENT_FLOOR_CHARS,
    calculate_fuzzy_score,
    normalize_text_with_mapping,
    strict_match,
)


def test_anchor_validation_empty_inputs() -> None:
    """Phase 4, Step 1: Verify empty input handling for normalizer, strict_match, and validate_evidence."""
    assert normalize_text_with_mapping("") == ("", [])
    assert strict_match("", ["quote"]).is_valid is False
    assert strict_match("text", []).is_valid is False
    assert strict_match("text", [""]).is_valid is False

    with pytest.raises(SemanticEvidenceError, match="exact_quotes is required"):
        AnchorValidationService.validate_evidence("text", [])


def test_anchor_validation_strict_match() -> None:
    """Phase 4, Step 1: Verify strict_match exact substring containment and non-matches."""
    assert strict_match("hello world document text", ["hello world"]).is_valid is True
    assert strict_match("hello world document text", ["absent quote"]).is_valid is False
    assert strict_match("hello world document text", [""]).is_valid is False


def test_anchor_validation_calculate_fuzzy_score_long_quote() -> None:
    """Phase 4, Step 1: Verify calculate_fuzzy_score for both long (>= 30) and short (< 30) normalized quotes."""
    long_quote = "this is a very long normalized quote with more than thirty chars"
    source = "this is a very long normalized quote with more than thirty characters in it"
    score = calculate_fuzzy_score(long_quote, source)
    assert score > 80.0

    short_quote = "shortquote"
    short_score = calculate_fuzzy_score(short_quote, "prefix shortquote suffix")
    assert short_score == 100.0
    assert MAX_CITATION_SPAN_CHARS == 1000
    assert MIN_MULTI_SEGMENT_FLOOR_CHARS == 30
    assert MIN_ENTROPY_GATE_CHARS == 10


def test_anchor_validation_unicode_typographical_and_zero_width_spaces() -> None:
    r"""Positive: Test exact quote extraction when corpus contains Unicode En Space (\u2002) and Zero Width Space (\u200b)."""
    corpus_text = "Johtajuus\u2002on\u200bselkeää\u00a0ja\ufeffvastuullista."
    exact_quotes = ["Johtajuus on selkeää ja vastuullista"]

    extracted = AnchorValidationService.validate_evidence(
        pdf_text=corpus_text,
        exact_quotes=exact_quotes,
        strictness_level=100,
    )
    assert extracted is not None
    assert len(extracted) == 1
    assert "Johtajuus" in extracted[0]
    assert "vastuullista" in extracted[0]

    assert strict_match(corpus_text, exact_quotes).is_valid is True

    clean_corpus = "Strateginen suunta on määritelty kirkkaasti tuleville vuosille."
    dirty_quote = ["Strateginen\u2002suunta\u200bon määritelty"]
    assert strict_match(clean_corpus, dirty_quote).is_valid is True

    extracted_rev = AnchorValidationService.validate_evidence(
        pdf_text=clean_corpus,
        exact_quotes=dirty_quote,
        strictness_level=100,
    )
    assert extracted_rev is not None
    assert len(extracted_rev) == 1
    assert extracted_rev[0] == "Strateginen suunta on määritelty"


def test_anchor_validation_multi_segment_ordered_monotonic_success() -> None:
    """Positive ISTQB test: tuple of 2 ordered segments separated by intervening text within 1 000 characters."""
    pdf_text = (
        "Strateginen johtaminen edellyttää selkeitä tavoitteita. "
        "Tässä välissä on analyyttista pohdintaa ja välivaiheita. "
        "Toiminnan tuloksellisuus varmistetaan säännöllisellä seurannalla."
    )
    seg1 = "Strateginen johtaminen edellyttää selkeitä tavoitteita."
    seg2 = "Toiminnan tuloksellisuus varmistetaan säännöllisellä seurannalla."
    assert len(seg1) >= 30
    assert len(seg2) >= 30

    result = strict_match(pdf_text, (seg1, seg2))
    assert isinstance(result, GateMatchResultDTO)
    assert result.is_valid is True
    assert result.start_idx >= 0
    assert result.end_idx > result.start_idx
    assert result.end_idx - result.start_idx <= 1000

    extracted = AnchorValidationService.validate_evidence(pdf_text, (seg1, seg2))
    assert extracted is not None
    assert isinstance(extracted, tuple)
    assert len(extracted) == 2
    assert extracted[0] == "Strateginen johtaminen edellyttää selkeitä tavoitteita"
    assert extracted[1] == "Toiminnan tuloksellisuus varmistetaan säännöllisellä seurannalla"


def test_anchor_validation_candidate_s1_iteration_repeated_phrase_success() -> None:
    """Positive ISTQB test: segment 1 repeats in preamble; first occurrence span exceeds 1000 chars, second succeeds."""
    seg1 = "Toistuva johdantolause esiintyy tässä dokumentin alussa useasti."
    seg2 = "Vasta toisen esiintymän jälkeen saavutetaan toinen tärkeä lause."
    intervening_filler = "Pitkää analyyttistä väliosaa tekstiä. " * 35
    pdf_text = f"{seg1} {intervening_filler} {seg1} Lyhyt väliosa tähän. {seg2}"
    assert len(seg1) >= 30
    assert len(seg2) >= 30

    result = strict_match(pdf_text, (seg1, seg2))
    assert result.is_valid is True
    assert result.start_idx > 1000

    extracted = AnchorValidationService.validate_evidence(pdf_text, (seg1, seg2))
    assert extracted is not None
    assert isinstance(extracted, tuple)
    assert len(extracted) == 2
    assert extracted[0] == "Toistuva johdantolause esiintyy tässä dokumentin alussa useasti"
    assert extracted[1] == "Vasta toisen esiintymän jälkeen saavutetaan toinen tärkeä lause"


def test_anchor_validation_single_segment_under_30_chars_passes() -> None:
    """Boundary ISTQB test: single-segment citation (m=1) under 30 chars (>= 10 chars) passes without floor rejection."""
    pdf_text = "Dokumentti sisältää lyhyen täsmällisen ilmauksen."
    seg = "lyhyen täsmällisen ilmauksen"
    assert 10 <= len(seg) < 30

    result = strict_match(pdf_text, (seg,))
    assert result.is_valid is True

    extracted = AnchorValidationService.validate_evidence(pdf_text, (seg,))
    assert extracted is not None
    assert extracted == (seg,)


def test_anchor_validation_multi_segment_three_segments_ordered_success() -> None:
    """Positive ISTQB test: 3-segment citation ordered monotonically and sliced symmetrically."""
    pdf_text = (
        "Ensimmäinen vaihe määrittelee perusteellisesti koko projektin laajuuden. "
        "Toinen vaihe toteuttaa suunnitellut toimenpiteet systemaattisesti ja tarkasti. "
        "Kolmas vaihe arvioi saavutetut tulokset ja laatii kattavan loppuraportin."
    )
    seg1 = "Ensimmäinen vaihe määrittelee perusteellisesti koko projektin laajuuden."
    seg2 = "Toinen vaihe toteuttaa suunnitellut toimenpiteet systemaattisesti ja tarkasti."
    seg3 = "Kolmas vaihe arvioi saavutetut tulokset ja laatii kattavan loppuraportin."

    result = strict_match(pdf_text, (seg1, seg2, seg3))
    assert result.is_valid is True

    extracted = AnchorValidationService.validate_evidence(pdf_text, (seg1, seg2, seg3))
    assert extracted is not None
    assert len(extracted) == 3
    assert extracted[0] == "Ensimmäinen vaihe määrittelee perusteellisesti koko projektin laajuuden"
    assert extracted[1] == "Toinen vaihe toteuttaa suunnitellut toimenpiteet systemaattisesti ja tarkasti"
    assert extracted[2] == "Kolmas vaihe arvioi saavutetut tulokset ja laatii kattavan loppuraportin"


def test_anchor_validation_strict_match_edge_cases() -> None:
    """Tests strict_match edge cases with empty or invalid inputs, HTML tags, replacement chars, and floor bounds."""
    assert strict_match("", ("seg",)).is_valid is False
    assert strict_match("pdf", ()).is_valid is False
    assert strict_match("   ", ("seg1",)).is_valid is False
    assert strict_match("pdf text", ("   ",)).is_valid is False

    # HTML tags and replacement character (\ufffd) in normalize_text_with_mapping
    norm_str, idx_map = normalize_text_with_mapping("Tee <b>t\ufffdst\ufffd</b> muistio")
    assert norm_str == "teetastamuistio"
    assert len(idx_map) == len(norm_str)

    # Multi-segment under floor (< 30 chars) in strict_match
    seg_long = "Ensimmäinen vaihe määrittelee perusteellisesti koko projektin laajuuden."
    seg_short = "Lyhyt."
    assert strict_match(seg_long, (seg_long, seg_short)).is_valid is False

    # Multi-segment second segment not found in strict_match
    seg_missing = "Tämä toinen pitkä lause puuttuu lähdetekstistä kokonaan täältä."
    assert strict_match(seg_long, (seg_long, seg_missing)).is_valid is False
