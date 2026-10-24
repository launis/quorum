"""Multi-tier lexical verifier for single and multi-segment quote anchoring."""

import difflib
import logging
import re
import unicodedata
from collections.abc import Sequence

from backend_v2.models.dtos.quote_evidence import GateMatchResultDTO
from backend_v2.models.enums import ValidationThresholdRatio
from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import (
    MAX_CITATION_SPAN_CHARS,
    MIN_ENTROPY_GATE_CHARS,
    MIN_MULTI_SEGMENT_FLOOR_CHARS,
    calculate_fuzzy_score,
    normalize_text_with_mapping,
)
from backend_v2.settings import get_lexical_fuzz_threshold
from backend_v2.utils.linguistics.stemmer import StemmerService

logger = logging.getLogger(__name__)

__all__ = ["is_lexically_valid"]


# Phase 2, Step 1: Relocate multi-tier lexical matcher is_lexically_valid
def is_lexically_valid(
    quote: str | Sequence[str] | tuple[str, ...] | list[str],
    norm_quote: str | Sequence[str] | tuple[str, ...] | list[str],
    norm_text: str,
    strictness_level: int = 50,
    locale: str | None = None,
    source_text: str | None = None,
    lexical_strictness_level: int = 50,
) -> GateMatchResultDTO:
    """Determine if a quote or multi-segment quote is lexically valid against normalized text.

    Enforces candidate s_1 anchor iteration, forward-scan search, monotonic ordering
    (s_k < e_k < s_{k+1}), individual segment floor of 30 characters when m > 1,
    and global span limit (<= 1000 characters).

    Args:
        quote: The exact quote string or ordered sequence of quote segments.
        norm_quote: The normalized quote string or sequence of normalized quote segments.
        norm_text: The normalized source text context.
        strictness_level: Validation strictness level constraint.
        locale: Optional locale definition.
        source_text: Optional original source text prior to normalization for word-boundary stemming.
        lexical_strictness_level: Sovereign workflow lexical strictness level (0-100 continuous).

    Returns:
        GateMatchResultDTO indicating match validity and normalized coordinate bounds.
    """
    if isinstance(quote, (list, tuple, Sequence)) and not isinstance(quote, str):
        quotes = tuple(q for q in quote if q is not None)
        if len(quotes) == 0:
            return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)
        if len(quotes) == 1:
            single_q = quotes[0]
            single_nq = (
                norm_quote[0]
                if isinstance(norm_quote, (list, tuple, Sequence)) and not isinstance(norm_quote, str)
                else norm_quote
            )
            return is_lexically_valid(
                quote=single_q,
                norm_quote=single_nq,
                norm_text=norm_text,
                strictness_level=strictness_level,
                locale=locale,
                source_text=source_text,
                lexical_strictness_level=lexical_strictness_level,
            )

        # Multi-segment citation (m > 1):
        m = len(quotes)
        for q in quotes:
            if len(q) < MIN_MULTI_SEGMENT_FLOOR_CHARS:
                return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

        norm_quotes_list: list[str] = []
        if isinstance(norm_quote, (list, tuple, Sequence)) and not isinstance(norm_quote, str):
            for nq in norm_quote:
                if not nq:
                    return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)
                norm_quotes_list.append(nq)
        else:
            for q in quotes:
                clean_q = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", q))
                nq, _ = normalize_text_with_mapping(clean_q)
                if not nq:
                    return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)
                norm_quotes_list.append(nq)

        # Candidate s_1 anchor iteration with forward-scan search:
        q0 = norm_quotes_list[0]
        search_offset = 0
        while True:
            pos_0 = norm_text.find(q0, search_offset)
            if pos_0 == -1:
                return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

            s1 = pos_0
            prev_end = pos_0 + len(q0) - 1
            chain_valid = True

            for k in range(1, m):
                qk = norm_quotes_list[k]
                next_pos = norm_text.find(qk, prev_end + 1)
                if next_pos == -1:
                    chain_valid = False
                    break
                end_k = next_pos + len(qk) - 1
                if end_k - s1 > MAX_CITATION_SPAN_CHARS:
                    chain_valid = False
                    break
                prev_end = end_k

            if chain_valid:
                return GateMatchResultDTO(is_valid=True, start_idx=s1, end_idx=prev_end)

            search_offset = pos_0 + 1

    # Single segment quote validation
    single_quote_str = quote if isinstance(quote, str) else str(quote)
    single_norm_quote_str = norm_quote if isinstance(norm_quote, str) else str(norm_quote)

    if not single_norm_quote_str:
        logger.warning("Lexical Verifier rejected quote: normalized quote is empty.")
        return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

    start_norm_idx = norm_text.find(single_norm_quote_str)
    if start_norm_idx != -1:
        return GateMatchResultDTO(
            is_valid=True,
            start_idx=start_norm_idx,
            end_idx=start_norm_idx + len(single_norm_quote_str) - 1,
        )

    # Tier 2 Unicode NFKC & Zero-Width normalization check
    clean_quote = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", single_quote_str))
    clean_norm_quote, _ = normalize_text_with_mapping(clean_quote)
    if clean_norm_quote:
        clean_norm_idx = norm_text.find(clean_norm_quote)
        if clean_norm_idx != -1:
            return GateMatchResultDTO(
                is_valid=True,
                start_idx=clean_norm_idx,
                end_idx=clean_norm_idx + len(clean_norm_quote) - 1,
            )

    if len(single_quote_str) < MIN_ENTROPY_GATE_CHARS:
        logger.warning(
            f"Entropy Gate Failure: Quote '{single_quote_str}' is under {MIN_ENTROPY_GATE_CHARS} chars. "
            "Fuzzy match is forbidden. 100% exact match required."
        )
        return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

    tier_threshold = get_lexical_fuzz_threshold(locale, lexical_strictness_level=lexical_strictness_level)

    if tier_threshold >= 100.0:
        logger.warning(
            f"Lexical validation failed: strictness is ABSOLUTE. "
            f"100% exact match required for '{single_quote_str[:50]}...'."
        )
        return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

    score = calculate_fuzzy_score(single_norm_quote_str, norm_text)
    if score >= tier_threshold:
        logger.warning(
            f"Lexical Verifier used Fuzzy Fallback for '{single_quote_str[:50]}...'. "
            f"Score {score:.1f}% >= threshold {tier_threshold}%",
            extra={
                "exact_quote_snippet": single_quote_str[:50],
                "rapidfuzz_score": score,
                "strictness_level": strictness_level,
                "lexical_strictness_level": lexical_strictness_level,
            },
        )
        matcher = difflib.SequenceMatcher(None, single_norm_quote_str, norm_text)
        blocks = [b for b in matcher.get_matching_blocks() if b.size > 0]
        if blocks:
            start_coord = blocks[0].b
            end_coord = blocks[-1].b + blocks[-1].size - 1
        else:
            start_coord = 0
            end_coord = 0
        return GateMatchResultDTO(is_valid=True, start_idx=start_coord, end_idx=end_coord)

    # Stage 3: Morphological Stemmed Sequence Verification (executed strictly when lexical_strictness_level < 100)
    if lexical_strictness_level < 100:
        stem_min_coverage = min(0.80, tier_threshold / 100.0)
        stem_result = StemmerService.match_stemmed_subsequence(
            quote=single_quote_str,
            source_text=source_text if source_text else norm_text,
            locale=locale,
            min_coverage=stem_min_coverage,
        )
        if stem_result.is_match:
            logger.warning(
                f"Lexical Verifier used Morphological Stemming for '{single_quote_str[:50]}...'. "
                f"Similarity {stem_result.similarity_score:.1f}% >= threshold {stem_min_coverage * 100.0:.1f}%",
                extra={
                    "exact_quote_snippet": single_quote_str[:50],
                    "rapidfuzz_score": score,
                    "stem_similarity_score": stem_result.similarity_score,
                    "matched_content_stems": stem_result.matched_content_stems,
                    "strictness_level": strictness_level,
                    "lexical_strictness_level": lexical_strictness_level,
                },
            )
            start_coord = -1
            end_coord = -1
            if stem_result.matched_source_span:
                norm_span, _ = normalize_text_with_mapping(stem_result.matched_source_span)
                if norm_span:
                    span_idx = norm_text.find(norm_span)
                    if span_idx != -1:
                        start_coord = span_idx
                        end_coord = span_idx + len(norm_span) - 1
            if start_coord == -1:
                matcher = difflib.SequenceMatcher(None, single_norm_quote_str, norm_text)
                blocks = [b for b in matcher.get_matching_blocks() if b.size > 0]
                if blocks:
                    start_coord = blocks[0].b
                    end_coord = blocks[-1].b + blocks[-1].size - 1
                else:
                    start_coord = 0
                    end_coord = 0
            return GateMatchResultDTO(is_valid=True, start_idx=start_coord, end_idx=end_coord)

    safety_net = ValidationThresholdRatio.COVERAGE_SAFETY_NET.value
    matcher = difflib.SequenceMatcher(None, single_norm_quote_str, norm_text)
    match = matcher.find_longest_match(0, len(single_norm_quote_str), 0, len(norm_text))
    coverage_pct = match.size / len(single_norm_quote_str)

    if coverage_pct >= safety_net:
        logger.warning(
            f"[AnchorValidation] Coverage-based match: {coverage_pct:.0%} of quote anchored",
            extra={
                "exact_quote_snippet": single_quote_str[:50],
                "coverage_pct": coverage_pct,
                "matched_fragment": single_norm_quote_str[match.a : match.a + match.size],
            },
        )
        blocks = [b for b in matcher.get_matching_blocks() if b.size > 0]
        if blocks:
            start_coord = blocks[0].b
            end_coord = blocks[-1].b + blocks[-1].size - 1
        else:
            if match.size > 0:
                start_coord = match.b
                end_coord = match.b + match.size - 1
            else:
                start_coord = 0
                end_coord = 0
        return GateMatchResultDTO(is_valid=True, start_idx=start_coord, end_idx=end_coord)

    logger.warning(
        f"Backend Lexical Verifier failed: exact_quote '{single_quote_str[:50]}...' not found in source text. "
        f"RapidFuzz best match: {score:.1f}% < threshold {tier_threshold}%. "
        f"Coverage match: {coverage_pct:.0%} < safety net {safety_net * 100:.0%}%",
        extra={
            "exact_quote_snippet": single_quote_str[:50],
            "rapidfuzz_score": score,
            "tier_threshold": tier_threshold,
            "coverage_pct": coverage_pct,
        },
    )
    return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)
