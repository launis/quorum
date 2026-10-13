"""Multilingual rule-based stemming service for anchor validation and quote grounding."""

from __future__ import annotations

import re
from typing import ClassVar, Protocol

from pydantic import BaseModel, ConfigDict

DEFAULT_MIN_COVERAGE: float = 0.80
MAX_WINDOW_TOKEN_PADDING: int = 15
MIN_STEMMABLE_WORD_LENGTH: int = 4

SUPPORTED_STEMMER_LANGUAGES: dict[str, str] = {
    "fi": "finnish",
    "sv": "swedish",
    "en": "english",
    "de": "german",
    "hu": "hungarian",
    "tr": "turkish",
    "fr": "french",
    "es": "spanish",
    "it": "italian",
    "nl": "dutch",
    "da": "danish",
    "no": "norwegian",
    "ru": "russian",
}


class StemmedMatchResultDTO(BaseModel):
    """Result of order-preserving stemmed sequence matching."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    is_match: bool
    similarity_score: float
    matched_content_stems: list[str]
    total_content_stems: int
    content_coverage_ratio: float
    matched_source_span: str | None = None


class BaseStemmer(Protocol):
    """Protocol defining the interface for language stemmers."""

    def stem_word(self, word: str) -> str:
        """Stem a single word.

        Args:
            word: The input word string.

        Returns:
            The stemmed word string.
        """
        ...

    def stem_tokens(self, tokens: list[str]) -> list[str]:
        """Stem a list of tokens.

        Args:
            tokens: List of token strings.

        Returns:
            List of stemmed token strings.
        """
        ...


class SnowballLanguageStemmer:
    """Stemmer implementation wrapping Snowball algorithmic stemmers with entropy gating.

    Attributes:
        lang: Snowball language name.
    """

    _stemmer_cache: ClassVar[dict[str, BaseStemmer]] = {}

    def __init__(self, lang: str) -> None:
        """Initialize Snowball language stemmer with lazy SDK loading.

        Args:
            lang: Language name recognized by snowballstemmer.
        """
        import snowballstemmer

        self.lang = lang
        self._stemmer = snowballstemmer.stemmer(lang)

    @classmethod
    def get_stemmer(cls, lang: str) -> BaseStemmer:
        """Get or initialize a cached stemmer instance for the given language.

        Args:
            lang: The language name.

        Returns:
            A cached BaseStemmer instance.
        """
        if lang in cls._stemmer_cache:
            return cls._stemmer_cache[lang]
        instance = cls(lang)
        cls._stemmer_cache[lang] = instance
        return instance

    def stem_word(self, word: str) -> str:
        """Stem a word using Snowball algorithm with entropy gate for short words.

        Args:
            word: The word to stem.

        Returns:
            The stemmed word or the original word if under MIN_STEMMABLE_WORD_LENGTH.
        """
        if len(word) < MIN_STEMMABLE_WORD_LENGTH:
            return word

        norm_word = word.lower()
        stemmed: str = str(self._stemmer.stemWord(norm_word))

        # Multi-pass stemming for languages with compound suffixes (e.g. Finnish plural nominative -t)
        if self.lang == "finnish":
            second_pass = str(self._stemmer.stemWord(stemmed))
            if len(second_pass) >= MIN_STEMMABLE_WORD_LENGTH:
                stemmed = second_pass
            # Harmonize Finnish nominal suffix alternation (-uus/-yys vs oblique -uud/-yyd/-uut/-yyt)
            if len(stemmed) > 4 and stemmed.endswith(("uus", "uud", "uut", "yys", "yyd", "yyt")):
                stemmed = stemmed[:-1]

        return stemmed

    def stem_tokens(self, tokens: list[str]) -> list[str]:
        """Stem a sequence of tokens.

        Args:
            tokens: The tokens to stem.

        Returns:
            List of stemmed tokens.
        """
        return [self.stem_word(t) for t in tokens]


class PassthroughStemmer:
    """Passthrough stemmer returning tokens unchanged for non-inflected or unsupported languages."""

    def stem_word(self, word: str) -> str:
        """Return the lowercase word without morphological mutation.

        Args:
            word: The word.

        Returns:
            The normalized word.
        """
        return word.lower()

    def stem_tokens(self, tokens: list[str]) -> list[str]:
        """Return the lowercase tokens without morphological mutation.

        Args:
            tokens: The tokens.

        Returns:
            The normalized tokens.
        """
        return [self.stem_word(t) for t in tokens]


class StemmerService:
    """Service providing multilingual stemming and sequence alignment for citation verification."""

    @staticmethod
    def get_stemmer_for_locale(locale: str | None = None) -> BaseStemmer:
        """Resolve the appropriate stemmer for an ISO locale code.

        Args:
            locale: Optional locale string (e.g. 'fi', 'en-US', 'zh').

        Returns:
            A BaseStemmer instance for the locale.
        """
        if not locale:
            return PassthroughStemmer()

        clean_code = locale.lower().split("-")[0].split("_")[0]
        if clean_code in ("zh", "ja", "ko"):
            return PassthroughStemmer()

        if clean_code in SUPPORTED_STEMMER_LANGUAGES:
            snowball_lang = SUPPORTED_STEMMER_LANGUAGES[clean_code]
            return SnowballLanguageStemmer.get_stemmer(snowball_lang)

        return PassthroughStemmer()

    @staticmethod
    def tokenize_content_words(text: str) -> list[str]:
        """Extract content words from text, applying entropy gate and zero-division guard.

        Args:
            text: Input string.

        Returns:
            List of extracted lowercase content word tokens.
        """
        all_tokens = [tok.lower() for tok in re.findall(r"\w+", text, flags=re.UNICODE)]
        if not all_tokens:
            return []

        content_tokens = [tok for tok in all_tokens if len(tok) >= MIN_STEMMABLE_WORD_LENGTH]
        # Zero-division fallback: if all words are under MIN_STEMMABLE_WORD_LENGTH, evaluate all words
        if not content_tokens:
            return all_tokens
        return content_tokens

    @staticmethod
    def stem_text(text: str, locale: str | None = None) -> list[str]:
        """Tokenize and stem text according to locale rules.

        Args:
            text: Input text string.
            locale: Optional locale code.

        Returns:
            List of stemmed tokens.
        """
        tokens = StemmerService.tokenize_content_words(text)
        stemmer = StemmerService.get_stemmer_for_locale(locale)
        return stemmer.stem_tokens(tokens)

    @staticmethod
    def match_stemmed_subsequence(
        quote: str,
        source_text: str,
        locale: str | None = None,
        min_coverage: float = DEFAULT_MIN_COVERAGE,
    ) -> StemmedMatchResultDTO:
        """Verify if quote content words appear in source text in monotonic order within a bounded window.

        Args:
            quote: The citation quote to verify.
            source_text: The authoritative source text.
            locale: Optional locale code.
            min_coverage: Minimum required content stem coverage ratio (0.0 - 1.0).

        Returns:
            StemmedMatchResultDTO with match outcome and coverage statistics.
        """
        # Fail-Fast boundary validation on empty or whitespace inputs
        if not quote or not quote.strip() or not source_text or not source_text.strip():
            return StemmedMatchResultDTO(
                is_match=False,
                similarity_score=0.0,
                matched_content_stems=[],
                total_content_stems=0,
                content_coverage_ratio=0.0,
                matched_source_span=None,
            )

        quote_words = StemmerService.tokenize_content_words(quote)
        if not quote_words:
            return StemmedMatchResultDTO(
                is_match=False,
                similarity_score=0.0,
                matched_content_stems=[],
                total_content_stems=0,
                content_coverage_ratio=0.0,
                matched_source_span=None,
            )

        stemmer = StemmerService.get_stemmer_for_locale(locale)
        quote_stems = stemmer.stem_tokens(quote_words)
        total_content_stems = len(quote_stems)

        source_words = [tok.lower() for tok in re.findall(r"\w+", source_text, flags=re.UNICODE)]
        if not source_words:
            return StemmedMatchResultDTO(
                is_match=False,
                similarity_score=0.0,
                matched_content_stems=[],
                total_content_stems=total_content_stems,
                content_coverage_ratio=0.0,
                matched_source_span=None,
            )

        source_stems = stemmer.stem_tokens(source_words)
        quote_stems_set = set(quote_stems)
        max_window_span = len(quote_words) + MAX_WINDOW_TOKEN_PADDING

        best_matched_stems: list[str] = []
        best_coverage: float = 0.0
        best_span: str | None = None

        # Candidate Window Discovery: scan source text for window starting at any matching stem
        for start_idx in range(len(source_stems)):
            if source_stems[start_idx] not in quote_stems_set:
                continue

            window_end = min(len(source_stems), start_idx + max_window_span)
            window_stems = source_stems[start_idx:window_end]

            # Monotonic order-preserving alignment within the contiguous window
            curr_pos = 0
            matched_in_window: list[str] = []
            first_offset = -1
            last_offset = -1

            for q_stem in quote_stems:
                if q_stem in window_stems[curr_pos:]:
                    found_offset = window_stems.index(q_stem, curr_pos)
                    matched_in_window.append(q_stem)
                    curr_pos = found_offset + 1
                    if first_offset == -1:
                        first_offset = found_offset
                    last_offset = found_offset

            coverage = len(matched_in_window) / total_content_stems
            if coverage > best_coverage:
                best_coverage = coverage
                best_matched_stems = matched_in_window
                if first_offset != -1 and last_offset != -1:
                    span_start = start_idx + first_offset
                    span_end = start_idx + last_offset + 1
                    best_span = " ".join(source_words[span_start:span_end])
                if best_coverage >= 1.0:
                    break

        is_match = best_coverage >= min_coverage
        similarity_score = round(best_coverage * 100.0, 2)

        return StemmedMatchResultDTO(
            is_match=is_match,
            similarity_score=similarity_score,
            matched_content_stems=best_matched_stems,
            total_content_stems=total_content_stems,
            content_coverage_ratio=best_coverage,
            matched_source_span=best_span,
        )
