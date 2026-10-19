import pytest

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.quote_evidence import GateMatchResultDTO, SourceDocumentContext
from backend_v2.models.enums import ExecutionStatus, TargetSpeaker
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
    assert extracted[0] == "tee t\ufffdt\ufffd muistio"  # Symmetric extraction slices exact string from physical source


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


def test_anchor_validation_provenance_user_rejects_ai_text() -> None:
    """Cross-speaker rejection: USER claim quoting AI text in dialogue triggers SemanticEvidenceError."""
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Some AI generated text about cats"]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)


def test_anchor_validation_provenance_ai_rejects_user_text() -> None:
    """Cross-speaker rejection (SYMMETRIC - Amendment 3): AI claim quoting user text in dialogue triggers SemanticEvidenceError."""
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Only this text is valid."]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.AI)


def test_anchor_validation_provenance_success() -> None:
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Only this text is valid."]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "Only this text is valid"


def test_anchor_validation_provenance_user_accepts_user_text() -> None:
    """Valid quote acceptance: USER claim quoting user text in dialogue passes."""
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Only this text is valid."]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "Only this text is valid"


def test_anchor_validation_provenance_ai_accepts_ai_text() -> None:
    """Valid quote acceptance: AI claim quoting AI text in dialogue passes."""
    pdf_text = "<ai_draft_context>Some AI generated text about cats</ai_draft_context> <user_payload>Only this text is valid.</user_payload>"
    exact_quotes = ["Some AI generated text about cats"]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.AI)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "Some AI generated text about cats"


def test_anchor_validation_non_chat_document_user_claim_passes() -> None:
    """Non-chat document: USER claim quoting full document text without dialogue tags passes."""
    pdf_text = "Tämä on yksittäisen kirjoittajan strateginen muistio ilman dialogia."
    exact_quotes = ["strateginen muistio"]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)
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
        AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)


def test_anchor_validation_provenance_ai_rejects_assignment_text() -> None:
    """Provenance protection: AI claim quoting assignment brief raises PROVENANCE_VIOLATION."""
    pdf_text = (
        "<assignment_context>Analyze the financial liquidity risk under Basel III.</assignment_context> "
        "<ai_draft_context>AI drafted response regarding risk metrics.</ai_draft_context>"
    )
    exact_quotes = ["Analyze the financial liquidity risk under Basel III."]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.AI)


def test_anchor_validation_provenance_only_assignment_rejects_all_quotes() -> None:
    """Provenance protection: Document with solely assignment_context rejects extraction attempts."""
    pdf_text = "<assignment_context>General instructions and rubric for candidate evaluation.</assignment_context>"
    exact_quotes = ["General instructions and rubric"]

    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)


def test_anchor_validation_provenance_user_accepts_user_text_with_assignment() -> None:
    """Provenance protection: Valid quote from user_payload passes when assignment_context is present."""
    pdf_text = (
        "<assignment_context>Analyze the financial liquidity risk under Basel III.</assignment_context> "
        "<user_payload>The liquidity coverage ratio was maintained at 120 throughout the fiscal period.</user_payload>"
    )
    exact_quotes = ["The liquidity coverage ratio was maintained at 120"]

    extracted = AnchorValidationService.validate_evidence(pdf_text, exact_quotes, target_speaker=TargetSpeaker.USER)
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "The liquidity coverage ratio was maintained at 120"


def test_anchor_validation_empty_inputs() -> None:
    assert AnchorValidationService.normalize_text_with_mapping("") == ("", [])
    assert AnchorValidationService.strict_match("", ["quote"]).is_valid is False
    assert AnchorValidationService.strict_match("text", []).is_valid is False
    assert AnchorValidationService.strict_match("text", [""]).is_valid is False

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
    with pytest.raises(SemanticEvidenceError, match="Lexical validation failed: exact_quote"):
        # strictness 100 forces threshold >= 100 and requires 100% exact match
        AnchorValidationService.validate_evidence(
            "almost perfect text", ["almost perfect texxxt"], strictness_level=100
        )


def test_anchor_validation_coverage_fallback() -> None:
    # Fuzzy score < 80% but coverage > 50%
    # norm_quote = "the quick brown fox jumps"
    # norm_text = "the quick brown fox"
    # Symmetric slice extraction extracts the matched portion from the physical source text
    extracted = AnchorValidationService.validate_evidence(
        "the quick brown fox", ["the quick brown fox jumps"], strictness_level=0
    )
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "the quick brown fox"


def test_anchor_validation_strictness_multiplier() -> None:
    source_text = "Työryhmä sitoutui johtajuudessaan selkeisiin tavoitteisiin."
    inflected_quote = ["johtajuus ja selkeät tavoitteet"]

    # 1. Under strictness level 50, Finnish inflected quote matches via Stage 3 morphological stemming
    # and symmetric extraction slices the physical source text
    extracted = AnchorValidationService.validate_evidence(
        source_text, inflected_quote, strictness_level=50, locale="fi"
    )
    assert extracted is not None
    assert len(extracted) == 1
    assert extracted[0] == "johtajuudessaan selkeisiin tavoitteisiin"

    # 2. Negative test: completely different words fail fail-fast with SemanticEvidenceError
    with pytest.raises(SemanticEvidenceError):
        AnchorValidationService.validate_evidence(
            source_text, ["talousarvio ja budjetti"], strictness_level=50, locale="fi"
        )

    # 3. Absolute strictness boundary test: under strictness level 100, inflected quote fails
    with pytest.raises(SemanticEvidenceError, match="Lexical validation failed: exact_quote"):
        AnchorValidationService.validate_evidence(source_text, inflected_quote, strictness_level=100, locale="fi")

    # 4. Strictness 85 and 30 paths
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


def test_anchor_validation_strict_match() -> None:
    assert AnchorValidationService.strict_match("hello world document text", ["hello world"]).is_valid is True
    assert AnchorValidationService.strict_match("hello world document text", ["absent quote"]).is_valid is False
    assert AnchorValidationService.strict_match("hello world document text", [""]).is_valid is False


def test_anchor_validation_calculate_fuzzy_score_long_quote() -> None:
    long_quote = "this is a very long normalized quote with more than thirty chars"
    source = "this is a very long normalized quote with more than thirty characters in it"
    score = AnchorValidationService.calculate_fuzzy_score(long_quote, source)
    assert score > 80.0


def test_anchor_validation_quote_normalized_to_empty_string_fails() -> None:
    pdf_text = "Standard valid document text."
    with pytest.raises(SemanticEvidenceError, match="normalized to empty string"):
        AnchorValidationService.validate_evidence(pdf_text, ["???"])


def test_anchor_validation_is_lexically_valid_negative_partitions() -> None:
    """ISTQB Negative Partitions: Assert empty, whitespace, and punctuation-only quotes fail lexical validation."""
    source_text = "Standard valid document text for lexical validation testing."
    norm_source, _ = AnchorValidationService.normalize_text_with_mapping(source_text)

    # Empty normalized quotes must fail immediately without entering find("") == 0
    for invalid_quote in ["", "   ", ".", "-", "...", " ? ! "]:
        norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(invalid_quote)
        assert (
            AnchorValidationService._is_lexically_valid(
                quote=invalid_quote,
                norm_quote=norm_quote,
                norm_text=norm_source,
                strictness_level=70,
            ).is_valid
            is False
        )

    # Valid quote must match Tier 1 literal find without regression
    valid_quote = "Standard valid document"
    norm_valid, _ = AnchorValidationService.normalize_text_with_mapping(valid_quote)
    assert (
        AnchorValidationService._is_lexically_valid(
            quote=valid_quote,
            norm_quote=norm_valid,
            norm_text=norm_source,
            strictness_level=70,
        ).is_valid
        is True
    )


def test_anchor_validation_provenance_empty_allowed_stream_fails() -> None:
    # Only <ai_draft_context> present, but claim targets USER
    pdf_text = "<ai_draft_context>Model output here.</ai_draft_context>"
    with pytest.raises(SemanticEvidenceError, match="PROVENANCE_VIOLATION"):
        AnchorValidationService.validate_evidence(pdf_text, ["Model output"], target_speaker=TargetSpeaker.USER)


def test_anchor_validation_unicode_typographical_and_zero_width_spaces() -> None:
    r"""Positive: Test exact quote extraction when corpus contains Unicode En Space (\u2002) and Zero Width Space (\u200b)."""
    # Corpus contains typographical spaces and zero-width artifacts injected by watermarks or rich text
    corpus_text = "Johtajuus\u2002on\u200bselkeää\u00a0ja\ufeffvastuullista."
    # Extracted quote uses standard ASCII spaces without zero-width artifacts
    exact_quotes = ["Johtajuus on selkeää ja vastuullista"]

    # 1. Test validate_evidence extracts the physical quote from the corpus
    extracted = AnchorValidationService.validate_evidence(
        pdf_text=corpus_text,
        exact_quotes=exact_quotes,
        strictness_level=100,
    )
    assert extracted is not None
    assert len(extracted) == 1
    # Verify the extracted string is grounded in the physical text
    assert "Johtajuus" in extracted[0]
    assert "vastuullista" in extracted[0]

    # 2. Test strict_match directly with both typographical spaces and zero-width chars
    assert AnchorValidationService.strict_match(corpus_text, exact_quotes).is_valid is True

    # 3. Test reverse: corpus has clean text, extracted quote has typographical space or zero-width char
    clean_corpus = "Strateginen suunta on määritelty kirkkaasti tuleville vuosille."
    dirty_quote = ["Strateginen\u2002suunta\u200bon määritelty"]
    assert AnchorValidationService.strict_match(clean_corpus, dirty_quote).is_valid is True

    extracted_rev = AnchorValidationService.validate_evidence(
        pdf_text=clean_corpus,
        exact_quotes=dirty_quote,
        strictness_level=100,
    )
    assert extracted_rev is not None
    assert len(extracted_rev) == 1
    assert extracted_rev[0] == "Strateginen suunta on määritelty"


def test_anchor_validation_empty_and_punctuation_quotes_fail_lexical_validation() -> None:
    """Negative ISTQB tests verifying empty, whitespace, and punctuation-only quotes fail _is_lexically_valid."""
    norm_text, _ = AnchorValidationService.normalize_text_with_mapping("Any valid document text context here.")

    # 1. Empty string quote
    assert AnchorValidationService._is_lexically_valid("", "", norm_text, strictness_level=50).is_valid is False

    # 2. Whitespace-only normalized quote
    assert AnchorValidationService._is_lexically_valid("   ", "", norm_text, strictness_level=50).is_valid is False

    # 3. Punctuation-only quote normalizing to empty string
    assert AnchorValidationService._is_lexically_valid(".", "", norm_text, strictness_level=50).is_valid is False
    assert AnchorValidationService._is_lexically_valid("---", "", norm_text, strictness_level=50).is_valid is False

    # 4. Valid quote still succeeds
    valid_quote = "valid document text"
    norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(valid_quote)
    assert (
        AnchorValidationService._is_lexically_valid(valid_quote, norm_quote, norm_text, strictness_level=50).is_valid
        is True
    )


def test_anchor_validation_process_atom_evaluation_suite() -> None:
    """Verifies that AnchorValidationService.process_atom_evaluation executes fully."""
    from backend_v2.tests.unit.services.orchestrator.test_anchor_validation_atom_result import (
        test_process_atom_evaluation_contextual_override_clears_quote,
        test_process_atom_evaluation_mcp_source_match,
        test_process_atom_evaluation_no_match_preserves_quote,
        test_process_atom_evaluation_none_source_quote_skips_matching,
        test_process_atom_evaluation_with_atom_result_dto,
        test_process_atom_evaluation_with_inflected_quote_matching,
    )

    test_process_atom_evaluation_with_atom_result_dto()
    test_process_atom_evaluation_with_inflected_quote_matching()
    test_process_atom_evaluation_contextual_override_clears_quote()
    test_process_atom_evaluation_no_match_preserves_quote()
    test_process_atom_evaluation_mcp_source_match()
    test_process_atom_evaluation_none_source_quote_skips_matching()


# ---------------------------------------------------------------------------
# Phase 3 Multi-Segment Citation & Distance Verification ISTQB Test Contracts
# ---------------------------------------------------------------------------


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

    result = AnchorValidationService.strict_match(pdf_text, (seg1, seg2))
    assert isinstance(result, GateMatchResultDTO)
    assert result.is_valid is True
    assert result.start_idx >= 0
    assert result.end_idx > result.start_idx
    assert result.end_idx - result.start_idx <= 1000

    extracted = AnchorValidationService.validate_evidence(pdf_text, (seg1, seg2))
    assert extracted is not None
    assert isinstance(extracted, tuple)
    assert len(extracted) == 2
    # Normalization maps to word characters, symmetrical physical slice trims trailing punctuation
    assert extracted[0] == "Strateginen johtaminen edellyttää selkeitä tavoitteita"
    assert extracted[1] == "Toiminnan tuloksellisuus varmistetaan säännöllisellä seurannalla"


def test_anchor_validation_inverted_segment_order_raises_semantic_error() -> None:
    """Error-path ISTQB test: tuple of 2 segments where segment 2 precedes segment 1 in source text."""
    pdf_text = "Ensimmäinen lause esitetään tässä järjestyksessä. Toinen lause tulee vasta tämän jälkeen tekstissä."
    seg1 = "Ensimmäinen lause esitetään tässä järjestyksessä."
    seg2 = "Toinen lause tulee vasta tämän jälkeen tekstissä."

    # Inverted order: seg2 passed as first segment, seg1 passed as second segment
    with pytest.raises(SemanticEvidenceError, match="Inverted segment order"):
        AnchorValidationService.validate_evidence(pdf_text, (seg2, seg1))

    # strict_match also returns is_valid=False
    match_res = AnchorValidationService.strict_match(pdf_text, (seg2, seg1))
    assert match_res.is_valid is False


def test_anchor_validation_span_exceeding_1000_chars_raises_semantic_error() -> None:
    """Boundary ISTQB test: tuple of 2 segments where (e2 - s1) exceeds 1 000 characters."""
    seg1 = "Tämä on ensimmäinen riittävän pitkä lause alussa."
    intervening = "a" * 1005
    seg2 = "Tämä on toinen riittävän pitkä lause lopussa."
    pdf_text = f"{seg1} {intervening} {seg2}"

    with pytest.raises(SemanticEvidenceError, match="Bounding span exceeds limit"):
        AnchorValidationService.validate_evidence(pdf_text, (seg1, seg2))

    match_res = AnchorValidationService.strict_match(pdf_text, (seg1, seg2))
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
        AnchorValidationService.validate_evidence(doc_text, (seg1, seg2))


def test_anchor_validation_multi_segment_floor_under_30_chars_raises_semantic_error() -> None:
    """Boundary ISTQB test: multi-segment citation with one segment under 30 characters raises SemanticEvidenceError."""
    pdf_text = "Tämä on ensimmäinen riittävän pitkä lause dokumentissa. Lyhyt lause täällä."
    seg1 = "Tämä on ensimmäinen riittävän pitkä lause dokumentissa."  # 55 chars (>= 30)
    seg2 = "Lyhyt lause täällä."  # 19 chars (< 30)
    assert len(seg1) >= 30
    assert len(seg2) < 30

    with pytest.raises(SemanticEvidenceError, match="under floor"):
        AnchorValidationService.validate_evidence(pdf_text, (seg1, seg2))

    match_res = AnchorValidationService.strict_match(pdf_text, (seg1, seg2))
    assert match_res.is_valid is False


def test_anchor_validation_candidate_s1_iteration_repeated_phrase_success() -> None:
    """Positive ISTQB test: segment 1 repeats in preamble; first occurrence span exceeds 1000 chars, second succeeds."""
    seg1 = "Toistuva johdantolause esiintyy tässä dokumentin alussa useasti."
    seg2 = "Vasta toisen esiintymän jälkeen saavutetaan toinen tärkeä lause."
    intervening_filler = "Pitkää analyyttistä väliosaa tekstiä. " * 35  # ~1330 characters
    pdf_text = f"{seg1} {intervening_filler} {seg1} Lyhyt väliosa tähän. {seg2}"
    assert len(seg1) >= 30
    assert len(seg2) >= 30

    result = AnchorValidationService.strict_match(pdf_text, (seg1, seg2))
    assert result.is_valid is True
    # First occurrence fails due to span > 1000; second occurrence succeeds with start_idx > 1000
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
    seg = "lyhyen täsmällisen ilmauksen"  # 28 chars (< 30, >= 10)
    assert 10 <= len(seg) < 30

    result = AnchorValidationService.strict_match(pdf_text, (seg,))
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

    result = AnchorValidationService.strict_match(pdf_text, (seg1, seg2, seg3))
    assert result.is_valid is True

    extracted = AnchorValidationService.validate_evidence(pdf_text, (seg1, seg2, seg3))
    assert extracted is not None
    assert len(extracted) == 3
    assert extracted[0] == "Ensimmäinen vaihe määrittelee perusteellisesti koko projektin laajuuden"
    assert extracted[1] == "Toinen vaihe toteuttaa suunnitellut toimenpiteet systemaattisesti ja tarkasti"
    assert extracted[2] == "Kolmas vaihe arvioi saavutetut tulokset ja laatii kattavan loppuraportin"


def test_anchor_validation_process_atom_evaluation_cross_document_chimera_fails() -> None:
    """Negative ISTQB test: cross-document chimera across separate SourceDocumentContext instances fails matching."""
    doc1 = SourceDocumentContext(
        opaque_id="doc_1",
        text_content="Dokumentti yksi sisältää tämän ensimmäisen lauseen tässä.",
        display_name="Doc 1",
    )
    doc2 = SourceDocumentContext(
        opaque_id="doc_2",
        text_content="Dokumentti kaksi sisältää tämän toisen lauseen erikseen.",
        display_name="Doc 2",
    )
    seg1 = "Dokumentti yksi sisältää tämän ensimmäisen lauseen tässä."
    seg2 = "Dokumentti kaksi sisältää tämän toisen lauseen erikseen."

    atom = AtomResultDTO(
        tda_id="tda_123",
        matrix_id="mat_1",
        status=ExecutionStatus.PASSED,
        extracted_data=None,
        source_quotes=(seg1, seg2),
        contextual_override=False,
        evaluation_reasoning="a1 points to evidence across documents",
        error_details=None,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    result = AnchorValidationService.process_atom_evaluation(
        atom=atom,
        alias_map={"a1": "doc_1"},
        source_documents=[doc1, doc2],
        mcp_source_texts=None,
        locale="fi",
        strictness_level=100,
    )
    # Neither doc1 nor doc2 contains BOTH segments; cohesive matching fails and preserves raw quotes
    assert result.source_quotes == (seg1, seg2)
    assert AnchorValidationService.strict_match(doc1.text_content, (seg1, seg2)).is_valid is False
    assert AnchorValidationService.strict_match(doc2.text_content, (seg1, seg2)).is_valid is False


def test_anchor_validation_is_lexically_valid_multi_segment_direct() -> None:
    """Tests _is_lexically_valid directly with multi-segment tuples."""
    seg1 = "Tämä on ensimmäinen riittävän pitkä lause testissä."
    seg2 = "Tämä on toinen riittävän pitkä lause testissä."
    text = f"{seg1} Väliosa tähän. {seg2}"
    norm_text, _ = AnchorValidationService.normalize_text_with_mapping(text)
    norm_q1, _ = AnchorValidationService.normalize_text_with_mapping(seg1)
    norm_q2, _ = AnchorValidationService.normalize_text_with_mapping(seg2)

    # Valid monotonic match
    res = AnchorValidationService._is_lexically_valid(
        quote=(seg1, seg2),
        norm_quote=(norm_q1, norm_q2),
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
        source_text=text,
    )
    assert res.is_valid is True

    # Multi-segment with norm_quote passed as string or raw
    res_raw = AnchorValidationService._is_lexically_valid(
        quote=(seg1, seg2),
        norm_quote="raw",
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
        source_text=text,
    )
    assert res_raw.is_valid is True

    # Empty tuple
    res_empty = AnchorValidationService._is_lexically_valid(
        quote=(),
        norm_quote=(),
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
    )
    assert res_empty.is_valid is False

    # Single tuple delegates to single quote
    res_single = AnchorValidationService._is_lexically_valid(
        quote=(seg1,),
        norm_quote=(norm_q1,),
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
    )
    assert res_single.is_valid is True

    # Segment under floor (< 30)
    short_seg = "Lyhyt lause."
    norm_short, _ = AnchorValidationService.normalize_text_with_mapping(short_seg)
    res_short = AnchorValidationService._is_lexically_valid(
        quote=(seg1, short_seg),
        norm_quote=(norm_q1, norm_short),
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
    )
    assert res_short.is_valid is False

    # Empty normalized quote in tuple
    res_empty_nq = AnchorValidationService._is_lexically_valid(
        quote=(seg1, seg2),
        norm_quote=(norm_q1, ""),
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
    )
    assert res_empty_nq.is_valid is False

    # Not found in text
    res_not_found = AnchorValidationService._is_lexically_valid(
        quote=(seg1, "Tämä lause ei koskaan esiinny kohdetekstissä lainkaan."),
        norm_quote=(norm_q1, "tama lause ei koskaan esiinny kohdetekstissa lainkaan"),
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
    )
    assert res_not_found.is_valid is False

    # Span > 1000 chars
    filler = "Täytetekstiä analyyttisessä testissä. " * 35
    text_long = f"{seg1} {filler} {seg2}"
    norm_long, _ = AnchorValidationService.normalize_text_with_mapping(text_long)
    res_long = AnchorValidationService._is_lexically_valid(
        quote=(seg1, seg2),
        norm_quote=(norm_q1, norm_q2),
        norm_text=norm_long,
        strictness_level=100,
        locale="fi",
    )
    assert res_long.is_valid is False


def test_anchor_validation_strict_match_edge_cases() -> None:
    """Tests strict_match edge cases with empty or invalid inputs."""
    assert AnchorValidationService.strict_match("", ("seg",)).is_valid is False
    assert AnchorValidationService.strict_match("pdf", ()).is_valid is False
    assert AnchorValidationService.strict_match("   ", ("seg1",)).is_valid is False
    assert AnchorValidationService.strict_match("pdf text", ("   ",)).is_valid is False


def test_anchor_validation_validate_evidence_edge_cases() -> None:
    """Tests validate_evidence edge cases: empty quotes, empty norm_pdf, directives."""
    with pytest.raises(SemanticEvidenceError, match="exact_quotes is required"):
        AnchorValidationService.validate_evidence("pdf text", ())

    with pytest.raises(SemanticEvidenceError, match="normalized to empty string"):
        AnchorValidationService.validate_evidence("pdf text", ("   ",))

    with pytest.raises(SemanticEvidenceError, match="source text normalized to empty string"):
        AnchorValidationService.validate_evidence("   ", ("valid quote text at least ten chars",))

    # Single-document directive matching (strict_match inside directive)
    directive_text = (
        "<ai_context_directive id='doc1'>\n"
        "Tämä on ensimmäinen lause direktiivissä riittävän pitkänä.\n"
        "Tämä on toinen lause direktiivissä riittävän pitkänä.\n"
        "</ai_context_directive>"
    )
    seg1 = "Tämä on ensimmäinen lause direktiivissä riittävän pitkänä."
    seg2 = "Tämä on toinen lause direktiivissä riittävän pitkänä."
    res = AnchorValidationService.validate_evidence(directive_text, (seg1, seg2))
    assert res is not None
    assert len(res) == 2

    # Single-document directive matching (fuzzy inside directive when strictness_level < 100)
    fuzzy_directive = (
        "<ai_context_directive id='doc1'>\n"
        "Tämä on ensimmäinen lause direktiivissä riittävän pitkänä tekstinä.\n"
        "</ai_context_directive>"
    )
    seg_fuzzy = "Tämä on ensimmäinen lause direktiivissä riittävän pitkänä tekstina."
    res_fuzzy = AnchorValidationService.validate_evidence(fuzzy_directive, (seg_fuzzy,), strictness_level=50)
    assert res_fuzzy is not None

    # Line 659-660: candidate s1 where subsequent segment is not found after first occurrence
    pdf_occ = (
        f"{seg2} "  # seg2 appears BEFORE first occurrence of seg1
        f"{seg1} Lyhyt väli. "
        f"{seg1} Sen jälkeen {seg2}"  # seg2 appears after second occurrence of seg1
    )
    res_occ = AnchorValidationService.validate_evidence(pdf_occ, (seg1, seg2))
    assert res_occ is not None
    assert len(res_occ) == 2


def test_anchor_validation_process_atom_evaluation_mcp_and_fuzzy_branches() -> None:
    """Tests process_atom_evaluation with MCP texts and fuzzy matching branches."""
    seg1 = "Tämä on ensimmäinen lause MCP dokumentissa riittävän pitkänä."
    seg2 = "Tämä on toinen lause MCP dokumentissa riittävän pitkänä."
    atom = AtomResultDTO(
        tda_id="tda_mcp",
        matrix_id="mat_1",
        status=ExecutionStatus.PASSED,
        extracted_data=None,
        source_quotes=(seg1, seg2),
        contextual_override=False,
        evaluation_reasoning="Evidence found in dynamic MCP tool output",
        error_details=None,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    # 1. MCP source text matching via strict_match
    mcp_text = f"Alkutekstiä. {seg1} Väliosa tähän. {seg2} Lopputekstiä."
    res_mcp = AnchorValidationService.process_atom_evaluation(
        atom=atom,
        alias_map={},
        source_documents=[],
        mcp_source_texts={"tool_1": mcp_text},
        locale="fi",
        strictness_level=100,
    )
    assert res_mcp.source_quotes is not None
    assert len(res_mcp.source_quotes) == 2

    # 2. Static document matching via per-segment fuzzy matching (strictness_level=50)
    # Use real character substitution ('kehityssuunnidelma' vs 'kehityssuunnitelma') that does not normalize away
    fuzzy_seg1 = "Organisaation strateginen kehityssuunnitelma määrittelee tulevat tavoitteet selkeästi."
    fuzzy_seg2 = "Toiminnan tuloksellisuutta seurataan säännöllisesti ja systemaattisesti koko organisaatiossa."
    doc = SourceDocumentContext(
        opaque_id="doc_fuzzy",
        text_content=f"{fuzzy_seg1} Väliosa. {fuzzy_seg2}",
        display_name="Fuzzy Doc",
    )
    atom_fuzzy = AtomResultDTO(
        tda_id="tda_fuz",
        matrix_id="mat_1",
        status=ExecutionStatus.PASSED,
        extracted_data=None,
        source_quotes=(
            "Organisaation strateginen kehityssuunnidelma määrittelee tulevat tavoitteet selkeästi.",  # typo: d instead of t
            "Toiminnan tuloksellisuutta seurataan säännollisesti ja systemaattisesti koko organisaatiossa.",  # typo: o instead of ö
        ),
        contextual_override=False,
        evaluation_reasoning="Fuzzy evidence matching",
        error_details=None,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )
    res_fuzzy = AnchorValidationService.process_atom_evaluation(
        atom=atom_fuzzy,
        alias_map={},
        source_documents=[doc],
        mcp_source_texts=None,
        locale="fi",
        strictness_level=50,
    )
    assert res_fuzzy.source_quotes is not None

    # 3. Dynamic MCP source text matching via per-segment fuzzy matching (strictness_level=50)
    res_mcp_fuzzy = AnchorValidationService.process_atom_evaluation(
        atom=atom_fuzzy,
        alias_map={},
        source_documents=[],
        mcp_source_texts={"mcp_tool": doc.text_content},
        locale="fi",
        strictness_level=50,
    )
    assert res_mcp_fuzzy.source_quotes is not None


def test_anchor_validation_coverage_safety_net_branch() -> None:
    """Tests coverage safety net branch in _is_lexically_valid (lines 407-426)."""
    text = "Organisaation strateginen kehityssuunnitelma määrittelee tulevat tavoitteet ja toimenpiteet selkeästi."
    norm_text, _ = AnchorValidationService.normalize_text_with_mapping(text)
    # Quote contains extra characters at beginning and end, but shares > 70% sequence match
    quote = "Extra preamble... Organisaation strateginen kehityssuunnitelma määrittelee tulevat tavoitteet ja toimenpiteet selkeästi ...extra suffix"
    norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(quote)

    res = AnchorValidationService._is_lexically_valid(
        quote=quote,
        norm_quote=norm_quote,
        norm_text=norm_text,
        strictness_level=0,  # Free mode allows coverage safety net
        locale="fi",
        source_text=text,
    )
    assert res.is_valid is True


def test_anchor_validation_zero_width_quote_matching() -> None:
    """Tests zero-width and NFKC normalization matching (line 297)."""
    text = "Dokumentti sisältää tämän täsmällisen lauseen täällä."
    norm_text, _ = AnchorValidationService.normalize_text_with_mapping(text)
    quote_zw = "Dokumentti\u200b sisältää\u200c tämän\ufeff täsmällisen\u200d lauseen täällä."
    norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(quote_zw)
    res = AnchorValidationService._is_lexically_valid(
        quote=quote_zw,
        norm_quote=norm_quote,
        norm_text=norm_text,
        strictness_level=100,
        locale="fi",
        source_text=text,
    )
    assert res.is_valid is True


def test_anchor_validation_candidate_s1_missing_subsequent_occurrence() -> None:
    """Tests candidate s1 where seg1 occurs again at the end with no subsequent seg2 (lines 647-648)."""
    seg1 = "Ensimmäinen lause esiintyy tekstissä useampaan kertaan."
    seg2 = "Toinen lause seuraa vain ensimmäistä esiintymää heti."
    pdf_text = f"{seg1} {seg2} Loppuosa tekstiä. {seg1}"
    res = AnchorValidationService.validate_evidence(pdf_text, (seg1, seg2))
    assert res is not None
    assert len(res) == 2
