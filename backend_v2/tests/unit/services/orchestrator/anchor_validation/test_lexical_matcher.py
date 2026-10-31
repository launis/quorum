"""Unit tests for lexical_matcher.py (is_lexically_valid across Gates 0, 1, 2, and 3)."""

import pytest
from pydantic import ValidationError

from backend_v2.models.domain.workflow import Workflow
from backend_v2.models.dtos.studio import WorkflowCreateDTO, WorkflowUpdateDTO
from backend_v2.services.orchestrator.anchor_validation.lexical_matcher import is_lexically_valid
from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import (
    normalize_text_with_mapping,
)
from backend_v2.settings import get_lexical_fuzz_threshold


def test_anchor_validation_is_lexically_valid_negative_partitions() -> None:
    """ISTQB Negative Partitions: Assert empty, whitespace, and punctuation-only quotes fail lexical validation."""
    source_text = "Standard valid document text for lexical validation testing."
    norm_source, _ = normalize_text_with_mapping(source_text)

    for invalid_quote in ["", "   ", ".", "-", "...", " ? ! "]:
        norm_quote, _ = normalize_text_with_mapping(invalid_quote)
        assert (
            is_lexically_valid(
                quote=invalid_quote,
                norm_quote=norm_quote,
                norm_text=norm_source,
                strictness_level=70,
            ).is_valid
            is False
        )

    valid_quote = "Standard valid document"
    norm_valid, _ = normalize_text_with_mapping(valid_quote)
    assert (
        is_lexically_valid(
            quote=valid_quote,
            norm_quote=norm_valid,
            norm_text=norm_source,
            strictness_level=70,
        ).is_valid
        is True
    )


def test_anchor_validation_empty_and_punctuation_quotes_fail_lexical_validation() -> None:
    """Negative ISTQB tests verifying empty, whitespace, and punctuation-only quotes fail is_lexically_valid."""
    norm_text, _ = normalize_text_with_mapping("Any valid document text context here.")

    assert is_lexically_valid("", "", norm_text, strictness_level=50).is_valid is False
    assert is_lexically_valid("   ", "", norm_text, strictness_level=50).is_valid is False
    assert is_lexically_valid(".", "", norm_text, strictness_level=50).is_valid is False
    assert is_lexically_valid("---", "", norm_text, strictness_level=50).is_valid is False

    valid_quote = "valid document text"
    norm_quote, _ = normalize_text_with_mapping(valid_quote)
    assert is_lexically_valid(valid_quote, norm_quote, norm_text, strictness_level=50).is_valid is True


def test_anchor_validation_is_lexically_valid_multi_segment_direct() -> None:
    """Tests is_lexically_valid directly with multi-segment tuples, fuzzy alignment, and stemming."""
    seg1 = "Tämä on ensimmäinen riittävän pitkä lause testissä."
    seg2 = "Tämä on toinen riittävän pitkä lause testissä."
    text = f"{seg1} Väliosa tähän. {seg2}"
    norm_text, _ = normalize_text_with_mapping(text)
    norm_q1, _ = normalize_text_with_mapping(seg1)
    norm_q2, _ = normalize_text_with_mapping(seg2)

    # Valid monotonic match
    res = is_lexically_valid(
        quote=(seg1, seg2),
        norm_quote=(norm_q1, norm_q2),
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
        source_text=text,
    )
    assert res.is_valid is True

    # Multi-segment with norm_quote passed as string or raw
    res_raw = is_lexically_valid(
        quote=(seg1, seg2),
        norm_quote="raw",
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
        source_text=text,
    )
    assert res_raw.is_valid is True

    # Empty tuple
    res_empty = is_lexically_valid(
        quote=(),
        norm_quote=(),
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
    )
    assert res_empty.is_valid is False

    # Single tuple delegates to single quote
    res_single = is_lexically_valid(
        quote=(seg1,),
        norm_quote=(norm_q1,),
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
    )
    assert res_single.is_valid is True

    # Segment under floor (< 30)
    short_seg = "Lyhyt lause."
    norm_short, _ = normalize_text_with_mapping(short_seg)
    res_short = is_lexically_valid(
        quote=(seg1, short_seg),
        norm_quote=(norm_q1, norm_short),
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
    )
    assert res_short.is_valid is False

    # Empty normalized quote in tuple
    res_empty_nq = is_lexically_valid(
        quote=(seg1, seg2),
        norm_quote=(norm_q1, ""),
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
    )
    assert res_empty_nq.is_valid is False

    # Not found in text
    res_not_found = is_lexically_valid(
        quote=(seg1, "Tämä lause ei koskaan esiinny kohdetekstissä lainkaan."),
        norm_quote=(norm_q1, "tama lause ei koskaan esiinny kohdetekstissa lainkaan"),
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
    )
    assert res_not_found.is_valid is False

    # Span > 1000 chars: passes under default unbounded (0), fails when max_citation_span_chars=1000
    from unittest.mock import patch

    from backend_v2.settings import Settings

    filler = "Täytetekstiä analyyttisessä testissä. " * 35
    text_long = f"{seg1} {filler} {seg2}"
    norm_long, _ = normalize_text_with_mapping(text_long)
    res_unbounded = is_lexically_valid(
        quote=(seg1, seg2),
        norm_quote=(norm_q1, norm_q2),
        norm_text=norm_long,
        strictness_level=100,
        locale="fi",
    )
    assert res_unbounded.is_valid is True

    with patch(
        "backend_v2.services.orchestrator.anchor_validation.lexical_matcher.get_settings",
        return_value=Settings(max_citation_span_chars=1000),
    ):
        res_long = is_lexically_valid(
            quote=(seg1, seg2),
            norm_quote=(norm_q1, norm_q2),
            norm_text=norm_long,
            strictness_level=100,
            locale="fi",
        )
        assert res_long.is_valid is False

    # Gate 2: Fuzzy alignment branch (encoding resilience) and Gate 3: Morphological stemming branch
    corrupted_text = "Johtoryhma paatti etta tee t\ufffdt\ufffd muistio tasta kokouksesta."
    norm_corrupted, _ = normalize_text_with_mapping(corrupted_text)
    fuz_q = "tee tästä muistio"
    norm_fuz_q, _ = normalize_text_with_mapping(fuz_q)
    assert (
        is_lexically_valid(
            quote=fuz_q,
            norm_quote=norm_fuz_q,
            norm_text=norm_corrupted,
            strictness_level=50,
            locale="fi",
            source_text=corrupted_text,
            lexical_strictness_level=50,
        ).is_valid
        is True
    )

    morph_text = "Työryhmä sitoutui johtajuudessaan selkeisiin tavoitteisiin."
    norm_morph, _ = normalize_text_with_mapping(morph_text)
    morph_q = "johtajuus ja selkeät tavoitteet"
    norm_morph_q, _ = normalize_text_with_mapping(morph_q)
    assert (
        is_lexically_valid(
            quote=morph_q,
            norm_quote=norm_morph_q,
            norm_text=norm_morph,
            strictness_level=50,
            locale="fi",
            source_text=morph_text,
            lexical_strictness_level=50,
        ).is_valid
        is True
    )

    # Entropy gate (< 10 chars) and lexical_strictness_level=100 rejection
    assert is_lexically_valid("short", "short", norm_text, strictness_level=50).is_valid is False
    assert (
        is_lexically_valid(
            quote=morph_q,
            norm_quote=norm_morph_q,
            norm_text=norm_morph,
            strictness_level=50,
            locale="fi",
            source_text=morph_text,
            lexical_strictness_level=100,
        ).is_valid
        is False
    )


def test_anchor_validation_coverage_safety_net_branch() -> None:
    """Tests coverage safety net branch, stemmer SequenceMatcher fallback, and Tier 2 clean_norm_quote."""
    # 1. Coverage safety net branch: score (75%) < threshold (93.84%), stem (0%) < 80%, coverage (75%) >= 70%
    short_source = "abcdefghijklyyyyyyyy"
    norm_short_source, _ = normalize_text_with_mapping(short_source)
    quote_safety = "abcdefghijklxxxx"
    norm_quote_safety, _ = normalize_text_with_mapping(quote_safety)
    res_safety = is_lexically_valid(
        quote=quote_safety,
        norm_quote=norm_quote_safety,
        norm_text=norm_short_source,
        strictness_level=85,
        locale="en",
        source_text=short_source,
        lexical_strictness_level=85,
    )
    assert res_safety.is_valid is True

    # 2. Stemmer fallback when matched_source_span is not in norm_text
    morph_text = "Työryhmä sitoutui johtajuudessaan selkeisiin tavoitteisiin."
    morph_q = "johtajuus ja selkeät tavoitteet"
    norm_morph_q, _ = normalize_text_with_mapping(morph_q)
    res_stem_fallback = is_lexically_valid(
        quote=morph_q,
        norm_quote=norm_morph_q,
        norm_text="johtajuuszzzzzzzzzzzzzzzzzzzzzzzzzz",
        strictness_level=50,
        locale="fi",
        source_text=morph_text,
        lexical_strictness_level=50,
    )
    assert res_stem_fallback.is_valid is True

    # 2b. Stemmer fallback when norm_text shares zero characters with norm_quote (empty matching blocks -> 0, 0)
    res_stem_zero_blocks = is_lexically_valid(
        quote=morph_q,
        norm_quote=norm_morph_q,
        norm_text="1234567890",
        strictness_level=50,
        locale="fi",
        source_text=morph_text,
        lexical_strictness_level=50,
    )
    assert res_stem_zero_blocks.is_valid is True
    assert res_stem_zero_blocks.start_idx == 0
    assert res_stem_zero_blocks.end_idx == 0

    # 3. Tier 2 clean_norm_quote fallback when caller passes un-normalized norm_quote
    text = "Dokumentti sisältää tämän täsmällisen lauseen täällä."
    norm_text, _ = normalize_text_with_mapping(text)
    quote_zw = "Dokumentti\u200b sisältää\u200c tämän\ufeff täsmällisen"
    res_tier2 = is_lexically_valid(
        quote=quote_zw,
        norm_quote="unnormalized_placeholder",
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
        source_text=text,
        lexical_strictness_level=100,
    )
    assert res_tier2.is_valid is True

    # 4. Multi-segment with raw norm_quote and punctuation-only second segment
    seg1 = "Dokumentti sisältää tämän täsmällisen lauseen täällä."
    seg_punct = "?" * 35
    res_raw_empty = is_lexically_valid(
        quote=(seg1, seg_punct),
        norm_quote="raw",
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
    )
    assert res_raw_empty.is_valid is False

    # 5. Complete lexical failure reaching final return False
    res_fail = is_lexically_valid(
        quote="completely unrelated long quote that never matches",
        norm_quote="completelyunrelatedlongquotethatnevermatches",
        norm_text=norm_short_source,
        strictness_level=85,
        locale="en",
        source_text=short_source,
        lexical_strictness_level=85,
    )
    assert res_fail.is_valid is False


def test_anchor_validation_zero_width_quote_matching() -> None:
    """Tests zero-width and NFKC normalization matching."""
    text = "Dokumentti sisältää tämän täsmällisen lauseen täällä."
    norm_text, _ = normalize_text_with_mapping(text)
    quote_zw = "Dokumentti\u200b sisältää\u200c tämän\ufeff täsmällisen\u200d lauseen täällä."
    norm_quote, _ = normalize_text_with_mapping(quote_zw)
    res = is_lexically_valid(
        quote=quote_zw,
        norm_quote=norm_quote,
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
        source_text=text,
        lexical_strictness_level=100,
    )
    assert res.is_valid is True


def test_lexical_strictness_bounds_validation_negative() -> None:
    """Verify Pydantic ValidationError on out-of-bounds lexical strictness level (<0 or >100)."""
    with pytest.raises(ValidationError):
        Workflow(
            id="wor_0195f3a0000070008123456789abcdef",
            slug="test-wf",
            name="Test Workflow",
            description="Test",
            status="active",
            version=1,
            default_strictness_level=50,
            default_lexical_strictness_level=-1,
        )

    with pytest.raises(ValidationError):
        Workflow(
            id="wor_0195f3a0000070008123456789abcdef",
            slug="test-wf",
            name="Test Workflow",
            description="Test",
            status="active",
            version=1,
            default_strictness_level=50,
            default_lexical_strictness_level=101,
        )

    with pytest.raises(ValidationError):
        WorkflowCreateDTO(
            slug="test-wf",
            name="Test Workflow",
            description="Test",
            model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
            steps=[],
            default_lexical_strictness_level=-5,
        )

    with pytest.raises(ValidationError):
        WorkflowCreateDTO(
            slug="test-wf",
            name="Test Workflow",
            description="Test",
            model_registry_id="sys_0195f3a00000700e826807f3bfa3454d",
            steps=[],
            default_lexical_strictness_level=150,
        )

    with pytest.raises(ValidationError):
        WorkflowUpdateDTO(default_lexical_strictness_level=-1)

    with pytest.raises(ValidationError):
        WorkflowUpdateDTO(default_lexical_strictness_level=105)


def test_get_lexical_fuzz_threshold_strictness_tiers() -> None:
    """Verify that get_lexical_fuzz_threshold scales with calibrated strictness multipliers."""
    assert get_lexical_fuzz_threshold("fi", lexical_strictness_level=0) == pytest.approx(68.0, rel=1e-3)
    assert get_lexical_fuzz_threshold("fi", lexical_strictness_level=30) == pytest.approx(76.5, rel=1e-3)
    assert get_lexical_fuzz_threshold("fi", lexical_strictness_level=50) == pytest.approx(85.0, rel=1e-3)
    assert get_lexical_fuzz_threshold("fi", lexical_strictness_level=85) == pytest.approx(86.7, rel=1e-3)
    assert get_lexical_fuzz_threshold("fi", lexical_strictness_level=100) == 100.0

    assert get_lexical_fuzz_threshold("en", lexical_strictness_level=0) == pytest.approx(73.6, rel=1e-3)
    assert get_lexical_fuzz_threshold("en", lexical_strictness_level=30) == pytest.approx(82.8, rel=1e-3)
    assert get_lexical_fuzz_threshold("en", lexical_strictness_level=50) == pytest.approx(92.0, rel=1e-3)
    assert get_lexical_fuzz_threshold("en", lexical_strictness_level=85) == pytest.approx(93.84, rel=1e-3)
    assert get_lexical_fuzz_threshold("en", lexical_strictness_level=100) == 100.0
