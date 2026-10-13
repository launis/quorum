"""Unit tests for StemmerService, SnowballLanguageStemmer, and PassthroughStemmer."""

from backend_v2.utils.linguistics.stemmer import (
    DEFAULT_MIN_COVERAGE,
    MIN_STEMMABLE_WORD_LENGTH,
    PassthroughStemmer,
    SnowballLanguageStemmer,
    StemmerService,
)


def test_stemmer_finnish_inflections() -> None:
    """ISTQB-P1: Finnish stemming parity for inflected noun cases."""
    stemmer = StemmerService.get_stemmer_for_locale("fi")

    # 1. Nominal vs inflected possessive case
    stem_nom = stemmer.stem_word("johtajuus")
    stem_inf = stemmer.stem_word("johtajuudessaan")
    assert stem_nom == "johtajuu"
    assert stem_inf == "johtajuu"
    assert stem_nom == stem_inf

    # 2. Plural illative vs nominative
    stem_tav_ill = stemmer.stem_word("tavoitteisiin")
    stem_tav_nom = stemmer.stem_word("tavoitteet")
    assert stem_tav_ill == stem_tav_nom

    # 3. Adjectival inflection
    stem_sel_ill = stemmer.stem_word("selkeisiin")
    stem_sel_nom = stemmer.stem_word("selkeät")
    assert stem_sel_ill == stem_sel_nom

    # 4. Full sentence subsequence matching
    source_text = "Työryhmä sitoutui johtajuudessaan selkeisiin tavoitteisiin ja strategiaan."
    quote = "johtajuus ja selkeät tavoitteet"
    result = StemmerService.match_stemmed_subsequence(quote, source_text, locale="fi")

    assert result.is_match is True
    assert result.similarity_score >= DEFAULT_MIN_COVERAGE * 100.0
    assert result.total_content_stems == 3  # johtajuus, selkeät, tavoitteet (ja < 4 chars)
    assert len(result.matched_content_stems) == 3
    assert result.matched_source_span is not None
    assert "johtajuudessaan" in result.matched_source_span


def test_stemmer_swedish_inflections() -> None:
    """Swedish stemming parity for definite articles and noun declensions."""
    stemmer = StemmerService.get_stemmer_for_locale("sv")

    stem_def = stemmer.stem_word("ledarskapet")
    stem_indef = stemmer.stem_word("ledarskap")
    assert stem_def == "ledarskap"
    assert stem_indef == "ledarskap"
    assert stem_def == stem_indef

    source_text = "Organisationen utmärks av ett starkt ledarskap och tydliga mål."
    quote = "starkt ledarskap och mål"
    result = StemmerService.match_stemmed_subsequence(quote, source_text, locale="sv")
    assert result.is_match is True


def test_stemmer_english_inflections() -> None:
    """English stemming parity for verbal conjugations and plurals."""
    stemmer = StemmerService.get_stemmer_for_locale("en")

    stem_noun = stemmer.stem_word("leadership")
    stem_plural = stemmer.stem_word("leaders")
    stem_gerund = stemmer.stem_word("leading")

    assert stem_noun == "leadership"
    assert stem_plural == "leader"
    assert stem_gerund == "lead"

    source_text = "Effective leaders are actively leading their organizations toward excellence."
    quote = "effective leaders leading organizations"
    result = StemmerService.match_stemmed_subsequence(quote, source_text, locale="en")
    assert result.is_match is True
    assert result.content_coverage_ratio == 1.0


def test_stemmer_german_and_hungarian_parity() -> None:
    """German and Hungarian stemming parity across agglutinations and endings."""
    stemmer_de = StemmerService.get_stemmer_for_locale("de")
    assert stemmer_de.stem_word("führungskräfte") == stemmer_de.stem_word("führungskraft")

    stemmer_hu = StemmerService.get_stemmer_for_locale("hu")
    assert stemmer_hu.stem_word("célok") == stemmer_hu.stem_word("célokhoz")


def test_stemmer_cjk_passthrough() -> None:
    """ISTQB-P7: CJK isolating languages pass through without token modification."""
    for locale in ("zh", "ja", "ko"):
        stemmer = StemmerService.get_stemmer_for_locale(locale)
        assert isinstance(stemmer, PassthroughStemmer)

    chinese_text = "组织领导与战略目标"
    assert stemmer.stem_word(chinese_text) == chinese_text.lower()

    japanese_text = "リーダーシップと戦略的目標"
    assert stemmer.stem_word(japanese_text) == japanese_text.lower()


def test_stemmer_entropy_gate_short_words() -> None:
    """ISTQB-P6: Short words strictly under MIN_STEMMABLE_WORD_LENGTH (4 chars) remain unmutated."""
    stemmer_fi = StemmerService.get_stemmer_for_locale("fi")
    short_words = ["tie", "on", "ei", "puu", "se", "ja", "ne"]

    for word in short_words:
        assert len(word) < MIN_STEMMABLE_WORD_LENGTH
        assert stemmer_fi.stem_word(word) == word


def test_stemmer_alien_words_rejected() -> None:
    """ISTQB-P2: Negative partition - ungrounded alien words yield 0% match and fail."""
    source_text = "Organisaation kehitys ja strategiatyö etenevät suunnitelman mukaan."
    alien_quote = "taloudellinen tuottavuus ja kulusäästöt"

    result = StemmerService.match_stemmed_subsequence(alien_quote, source_text, locale="fi")
    assert result.is_match is False
    assert result.similarity_score == 0.0
    assert result.matched_content_stems == []


def test_stemmer_scrambled_order_rejected() -> None:
    """ISTQB-P3: Negative partition - scrambled non-monotonic word order fails sequence alignment."""
    source_text = "Ensimmäinen toinen kolmas neljäs viides vaihe."
    scrambled_quote = "viides kolmas ensimmäinen"

    result = StemmerService.match_stemmed_subsequence(scrambled_quote, source_text, locale="fi")
    assert result.is_match is False
    # Only 1 word can be matched monotonically out of 3, yielding 33.3% < 80%
    assert result.content_coverage_ratio < DEFAULT_MIN_COVERAGE


def test_stemmer_window_contiguity_guard() -> None:
    """ISTQB-P4: Negative partition - words scattered across distant paragraphs exceed max window span."""
    paragraph_1 = "Johtajuus on organisaation tärkein voimavara. "
    padding_sentences = "Tämä on täytelausetta. " * 30  # ~120 tokens of distance
    paragraph_2 = "Lopuksi määritellään selkeät tavoitteet tulevaisuudelle."
    distant_source = paragraph_1 + padding_sentences + paragraph_2

    scattered_quote = "johtajuus ja tavoitteet"
    result = StemmerService.match_stemmed_subsequence(scattered_quote, distant_source, locale="fi")
    assert result.is_match is False
    # Only 1 content word matches per window span, coverage is 50% < 80%
    assert result.content_coverage_ratio < DEFAULT_MIN_COVERAGE


def test_stemmer_zero_division_guard_all_short_words() -> None:
    """Zero-division protection when quote contains only short words under 4 characters."""
    quote_short = "on se ei"
    source_text = "Tämä on se ei juttu."

    result = StemmerService.match_stemmed_subsequence(quote_short, source_text, locale="fi")
    assert result.total_content_stems == 3
    assert result.is_match is True
    assert result.content_coverage_ratio == 1.0


def test_stemmer_empty_and_whitespace_inputs() -> None:
    """Boundary test asserting empty or whitespace inputs safely return is_match=False."""
    res_empty_quote = StemmerService.match_stemmed_subsequence("", "Valid source text", locale="fi")
    assert res_empty_quote.is_match is False
    assert res_empty_quote.total_content_stems == 0

    res_empty_src = StemmerService.match_stemmed_subsequence("Valid quote", "", locale="fi")
    assert res_empty_src.is_match is False

    res_whitespace = StemmerService.match_stemmed_subsequence("   ", "   ", locale="fi")
    assert res_whitespace.is_match is False


def test_stemmer_cache_singleton() -> None:
    """Assert class-level stemmer cache returns the same instance for repeated language lookups."""
    stemmer_1 = SnowballLanguageStemmer.get_stemmer("finnish")
    stemmer_2 = SnowballLanguageStemmer.get_stemmer("finnish")
    assert stemmer_1 is stemmer_2


def test_stemmer_unmapped_and_empty_locale() -> None:
    """Assert unmapped or empty locales resolve to PassthroughStemmer."""
    stemmer_none = StemmerService.get_stemmer_for_locale(None)
    assert isinstance(stemmer_none, PassthroughStemmer)

    stemmer_unknown = StemmerService.get_stemmer_for_locale("unknown_lang")
    assert isinstance(stemmer_unknown, PassthroughStemmer)
    assert stemmer_unknown.stem_tokens(["hello", "world"]) == ["hello", "world"]


def test_stemmer_tokenize_and_stem_helpers() -> None:
    """Test tokenize_content_words and stem_text helpers."""
    assert StemmerService.tokenize_content_words("") == []

    stems = StemmerService.stem_text("Johtajuus ja selkeät tavoitteet", locale="fi")
    assert "johtajuu" in stems
    assert "tavoi" in stems



def test_stemmer_punctuation_only_inputs() -> None:
    """Assert quotes or sources with only punctuation return is_match=False."""
    res_punct_quote = StemmerService.match_stemmed_subsequence("---", "Valid source", locale="fi")
    assert res_punct_quote.is_match is False

    res_punct_src = StemmerService.match_stemmed_subsequence("Valid quote", "---", locale="fi")
    assert res_punct_src.is_match is False


def test_stemmer_continuous_normalized_source_matching() -> None:
    """Assert continuous normalized source text (spaces and diacritics stripped) matches inflected quotes."""
    continuous_norm_source = "tyoryhmasitoutuijohtajuudessaanselkeisiintavoitteisiin"
    quote = "johtajuus ja selkeät tavoitteet"

    result = StemmerService.match_stemmed_subsequence(quote, continuous_norm_source, locale="fi")
    assert result.is_match is True
    assert result.similarity_score == 100.0
    assert result.total_content_stems == 3
    assert len(result.matched_content_stems) == 3
    assert result.matched_source_span is not None


