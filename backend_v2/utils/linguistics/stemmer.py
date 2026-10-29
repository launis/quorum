"""Multilingual rule-based stemming service for anchor validation and quote grounding."""

from __future__ import annotations

import re
import unicodedata
from typing import Annotated, ClassVar, Protocol

from pydantic import BaseModel, ConfigDict, Field

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

__all__ = [
    "DEFAULT_MIN_COVERAGE",
    "MAX_WINDOW_TOKEN_PADDING",
    "MIN_STEMMABLE_WORD_LENGTH",
    "SUPPORTED_STEMMER_LANGUAGES",
    "BaseStemmer",
    "PassthroughStemmer",
    "SnowballLanguageStemmer",
    "StemmedMatchResultDTO",
    "StemmerService",
]


class StemmedMatchResultDTO(BaseModel):
    """Result of order-preserving stemmed sequence matching.

    Attributes:
        is_match: True if content stem coverage meets or exceeds the minimum threshold.
        similarity_score: Percentage similarity score scaled to 0.0 - 100.0.
        matched_content_stems: Ordered list of matched content stems within the best window.
        total_content_stems: Total number of evaluated content stems in the quote.
        content_coverage_ratio: Ratio of matched content stems to total content stems (0.0 - 1.0).
        matched_source_span: Reconstructed substring span from the source text if matched.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    is_match: Annotated[bool, Field(description="Whether the stemmed quote subsequence satisfies minimum coverage.")]
    similarity_score: Annotated[
        float, Field(description="Percentage coverage score rounded to two decimal places (0.0 - 100.0).")
    ]
    matched_content_stems: Annotated[
        list[str], Field(description="Ordered sequence of quote stems matched monotonically in the source window.")
    ]
    total_content_stems: Annotated[
        int, Field(description="Total count of content word stems extracted from the quote.")
    ]
    content_coverage_ratio: Annotated[
        float, Field(description="Ratio of matched content stems to total quote content stems (0.0 - 1.0).")
    ]
    matched_source_span: Annotated[
        str | None,
        Field(default=None, description="Matched source span string corresponding to the aligned stem window."),
    ] = None


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

        # Apply second-pass stemming for Finnish compound suffixes (plural nominative -t and oblique stems)
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
            locale: Optional ISO 639-1 or BCP 47 locale string.

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
    def normalize_for_continuous(text: str) -> str:
        """Normalize text to lowercase base-ASCII without non-alphanumeric characters.

        Args:
            text: Input string to normalize.

        Returns:
            Normalized lowercase ASCII string.
        """
        nfkc = unicodedata.normalize("NFKC", text)
        nfd = unicodedata.normalize("NFD", nfkc)
        base = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
        return re.sub(r"[\W_]+", "", base.lower())

    @staticmethod
    def _find_best_token_window_match(
        quote_stems: list[str],
        source_words: list[str],
        source_stems: list[str],
        max_window_span: int,
        min_coverage: float,
    ) -> StemmedMatchResultDTO:
        """Scan token windows in source text for best monotonic order-preserving stem alignment.

        Args:
            quote_stems: Stemmed content tokens from the quote.
            source_words: Lowercase word tokens from the source text.
            source_stems: Stemmed word tokens from the source text.
            max_window_span: Maximum token window length to inspect per candidate anchor.
            min_coverage: Minimum required content stem coverage ratio (0.0 - 1.0).

        Returns:
            StemmedMatchResultDTO representing the best token-window match found.
        """
        total_content_stems = len(quote_stems)
        quote_stems_set = set(quote_stems)
        best_matched_stems: list[str] = []
        best_coverage: float = 0.0
        best_span: str | None = None

        for start_idx in range(len(source_stems)):
            if source_stems[start_idx] not in quote_stems_set:
                continue

            window_end = min(len(source_stems), start_idx + max_window_span)
            window_stems = source_stems[start_idx:window_end]

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
                span_start = start_idx + first_offset
                span_end = start_idx + last_offset + 1
                best_span = " ".join(source_words[span_start:span_end])
                if best_coverage >= 1.0:
                    break

        return StemmedMatchResultDTO(
            is_match=best_coverage >= min_coverage,
            similarity_score=round(best_coverage * 100.0, 2),
            matched_content_stems=best_matched_stems,
            total_content_stems=total_content_stems,
            content_coverage_ratio=best_coverage,
            matched_source_span=best_span,
        )

    @staticmethod
    def _scan_continuous_candidate(
        norm_source: str,
        orig_stems: list[str],
        norm_stems: list[str],
        start_idx: int,
        found_pos: int,
        max_char_span: int,
        total_content_stems: int,
        min_coverage: float,
    ) -> StemmedMatchResultDTO:
        """Evaluate monotonic stem alignment in continuous normalized text from a starting anchor.

        Args:
            norm_source: Continuous normalized lowercase ASCII source string.
            orig_stems: Original stemmed quote tokens with non-empty normalized representations.
            norm_stems: Normalized continuous representations corresponding 1:1 to orig_stems.
            start_idx: Starting index in orig_stems and norm_stems.
            found_pos: Character index in norm_source where norm_stems[start_idx] was found.
            max_char_span: Maximum allowed character span from first_offset to candidate_end.
            total_content_stems: Total content stems in the quote.
            min_coverage: Minimum required content stem coverage ratio (0.0 - 1.0).

        Returns:
            StemmedMatchResultDTO for the candidate anchor position.
        """
        norm_start = norm_stems[start_idx]
        curr_pos = found_pos + len(norm_start)
        matched_stems = [orig_stems[start_idx]]
        first_offset = found_pos
        last_offset = curr_pos

        for next_idx in range(start_idx + 1, len(orig_stems)):
            norm_next = norm_stems[next_idx]
            next_pos = norm_source.find(norm_next, curr_pos)
            if next_pos != -1:
                candidate_end = next_pos + len(norm_next)
                if (candidate_end - first_offset) <= max_char_span:
                    matched_stems.append(orig_stems[next_idx])
                    curr_pos = candidate_end
                    last_offset = candidate_end

        coverage = len(matched_stems) / total_content_stems
        return StemmedMatchResultDTO(
            is_match=coverage >= min_coverage,
            similarity_score=round(coverage * 100.0, 2),
            matched_content_stems=matched_stems,
            total_content_stems=total_content_stems,
            content_coverage_ratio=coverage,
            matched_source_span=norm_source[first_offset:last_offset],
        )

    @staticmethod
    def _find_best_continuous_match(
        quote_words: list[str],
        quote_stems: list[str],
        source_text: str,
        initial_best: StemmedMatchResultDTO,
        min_coverage: float,
    ) -> StemmedMatchResultDTO:
        """Fallback continuous normalized text matching for whitespace-stripped source strings.

        Args:
            quote_words: Content word tokens extracted from the quote.
            quote_stems: Stemmed content tokens from the quote.
            source_text: The authoritative source text.
            initial_best: Best StemmedMatchResultDTO from token-window matching.
            min_coverage: Minimum required content stem coverage ratio (0.0 - 1.0).

        Returns:
            Updated StemmedMatchResultDTO if continuous matching improves coverage, else initial_best.
        """
        best_result = initial_best
        norm_source = StemmerService.normalize_for_continuous(source_text)
        if norm_source:
            orig_stems: list[str] = []
            norm_stems: list[str] = []
            for stem in quote_stems:
                norm_stem = StemmerService.normalize_for_continuous(stem)
                if norm_stem:
                    orig_stems.append(stem)
                    norm_stems.append(norm_stem)

            if orig_stems:
                quote_char_len = sum(len(w) for w in quote_words)
                max_char_span = quote_char_len + (MAX_WINDOW_TOKEN_PADDING * 10)

                for start_idx, norm_start in enumerate(norm_stems):
                    search_pos = 0
                    candidate_count = 0
                    while candidate_count < 50:
                        found_pos = norm_source.find(norm_start, search_pos)
                        if found_pos == -1:
                            break
                        candidate_count += 1

                        candidate = StemmerService._scan_continuous_candidate(
                            norm_source=norm_source,
                            orig_stems=orig_stems,
                            norm_stems=norm_stems,
                            start_idx=start_idx,
                            found_pos=found_pos,
                            max_char_span=max_char_span,
                            total_content_stems=initial_best.total_content_stems,
                            min_coverage=min_coverage,
                        )
                        if candidate.content_coverage_ratio > best_result.content_coverage_ratio:
                            best_result = candidate
                            if best_result.content_coverage_ratio >= 1.0:
                                break

                        search_pos = found_pos + 1

        return best_result

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
        max_window_span = len(quote_words) + MAX_WINDOW_TOKEN_PADDING

        best_result = StemmerService._find_best_token_window_match(
            quote_stems=quote_stems,
            source_words=source_words,
            source_stems=source_stems,
            max_window_span=max_window_span,
            min_coverage=min_coverage,
        )

        if best_result.content_coverage_ratio < min_coverage:
            best_result = StemmerService._find_best_continuous_match(
                quote_words=quote_words,
                quote_stems=quote_stems,
                source_text=source_text,
                initial_best=best_result,
                min_coverage=min_coverage,
            )

        return best_result
