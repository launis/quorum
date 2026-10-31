"""Leaf lexical normalization, exact substring matching, and fuzzy scoring functions."""

import re
import unicodedata
from collections.abc import Sequence

from rapidfuzz import fuzz

from backend_v2.models.dtos.quote_evidence import GateMatchResultDTO
from backend_v2.settings import get_settings

# Phase 1, Step 1.3: Resolve leaf forensic citation thresholds from settings SSOT
MAX_CITATION_SPAN_CHARS: int = get_settings().max_citation_span_chars
MIN_MULTI_SEGMENT_FLOOR_CHARS: int = get_settings().min_multi_segment_floor_chars
MIN_ENTROPY_GATE_CHARS: int = get_settings().min_entropy_gate_chars

__all__ = [
    "MAX_CITATION_SPAN_CHARS",
    "MIN_ENTROPY_GATE_CHARS",
    "MIN_MULTI_SEGMENT_FLOOR_CHARS",
    "calculate_fuzzy_score",
    "normalize_text_with_mapping",
    "strict_match",
]


# Phase 1, Step 1: Relocate normalize_text_with_mapping leaf function
def normalize_text_with_mapping(text: str) -> tuple[str, list[int]]:
    """Normalizes text and returns a mapping from normalized index to original index.

    Args:
        text: The text to normalize.

    Returns:
        A tuple containing the normalized string and a list mapping
        each character's index in the normalized string to its index in the original string.
    """
    if not text:
        return "", []

    # FAST-PATH: Find indices of HTML tags and ignore them during normalization.
    # This prevents characters from tags like <br> from ending up in the normalized text.
    html_tag_indices: set[int] = set()
    for match in re.finditer(r"<[^>]+>", text):
        html_tag_indices.update(range(match.start(), match.end()))

    norm_chars: list[str] = []
    index_map: list[int] = []
    for i, char in enumerate(text):
        if i in html_tag_indices:
            continue

        # Skip zero-width format characters so they don't affect normalization index map
        if char in "\u200b\u200c\u200d\ufeff":
            continue

        # Fallback for unicode replacement characters to maximize fuzzy matches
        # since most broken characters in this context are 'ä' -> 'a'
        if char == "\ufffd":
            char = "a"

        # NFKC normalizes typographic spaces (\u2002, \u00a0) to standard ASCII whitespace
        # and NFD normalization splits diacritics from base characters
        nfkc_char = unicodedata.normalize("NFKC", char)
        nfd_chars = unicodedata.normalize("NFD", nfkc_char)

        # Filter out the combining characters (category 'Mn') to drop accents
        base_chars = "".join(c for c in nfd_chars if unicodedata.category(c) != "Mn")

        norm_char = base_chars.lower()
        norm_char = re.sub(r"[\W_]+", "", norm_char)
        if norm_char:
            for nc in norm_char:
                norm_chars.append(nc)
                index_map.append(i)

    return "".join(norm_chars), index_map


# Phase 1, Step 1: Relocate strict_match leaf function
def strict_match(
    pdf_text: str,
    exact_quotes: Sequence[str] | tuple[str, ...] | list[str],
) -> GateMatchResultDTO:
    """Phase 2 & Phase 3: O(N) Anchoring using strict substring matching.

    Enforces forward-scan monotonic ordering (s_k < e_k < s_{k+1}), candidate s_1 anchor
    iteration, individual segment floor of 30 characters when m > 1, and bounding
    span ceiling (e_m - s_1 <= 1000 characters).

    Args:
        pdf_text: The source text context.
        exact_quotes: Ordered sequence of extracted quote segments.

    Returns:
        GateMatchResultDTO indicating match validity and normalized coordinate bounds.
    """
    if not exact_quotes or not pdf_text:
        return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

    quotes = tuple(exact_quotes)
    m = len(quotes)
    settings = get_settings()
    min_floor_chars = settings.min_multi_segment_floor_chars
    max_span_chars = settings.max_citation_span_chars
    # Phase 1, Step 1.3: Enforce individual segment floor from settings when m > 1
    if m > 1:
        for q in quotes:
            if len(q) < min_floor_chars:
                return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

    clean_pdf = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", pdf_text))
    norm_pdf, _ = normalize_text_with_mapping(clean_pdf)
    if not norm_pdf:
        return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

    norm_quotes: list[str] = []
    for q in quotes:
        clean_q = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", q))
        norm_q, _ = normalize_text_with_mapping(clean_q)
        if not norm_q:
            return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)
        norm_quotes.append(norm_q)

    # Candidate s_1 anchor iteration with forward-scan search:
    q0 = norm_quotes[0]
    search_offset = 0
    while True:
        pos_0 = norm_pdf.find(q0, search_offset)
        if pos_0 == -1:
            return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

        s1 = pos_0
        prev_end = pos_0 + len(q0) - 1
        chain_valid = True

        for k in range(1, m):
            qk = norm_quotes[k]
            next_pos = norm_pdf.find(qk, prev_end + 1)
            if next_pos == -1:
                chain_valid = False
                break
            end_k = next_pos + len(qk) - 1
            if max_span_chars > 0 and end_k - s1 > max_span_chars:
                chain_valid = False
                break
            prev_end = end_k

        if chain_valid:
            return GateMatchResultDTO(is_valid=True, start_idx=s1, end_idx=prev_end)

        search_offset = pos_0 + 1


# Phase 1, Step 1: Relocate calculate_fuzzy_score leaf function
def calculate_fuzzy_score(norm_quote: str, norm_text: str) -> float:
    """Choose fuzzy algorithm based on length of the normalized quote.

    Args:
        norm_quote: The normalized quote string.
        norm_text: The normalized source text context.

    Returns:
        The fuzzy similarity score (0.0 to 100.0).
    """
    # Phase 1, Step 1.3: Resolve multi-segment floor from settings SSOT
    if len(norm_quote) < get_settings().min_multi_segment_floor_chars:
        # Short quotes: enforce strict partial_ratio for contiguous matches (contiguity-guard)
        return float(fuzz.partial_ratio(norm_quote, norm_text))
    else:
        # Long quotes: allow token_set_ratio to accommodate word ordering / Finnish morphological conjugations
        return float(fuzz.token_set_ratio(norm_quote, norm_text))
