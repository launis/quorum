"""Forensic evidence validator enforcing reasoning trace, provenance, and quote slicing."""

import logging
import re
import unicodedata
from collections.abc import Sequence

from backend_v2.exceptions import ErrorCodes, SemanticEvidenceError
from backend_v2.models.dtos.quote_evidence import GateMatchResultDTO
from backend_v2.models.enums import TargetSpeaker
from backend_v2.services.orchestrator.anchor_validation.lexical_matcher import is_lexically_valid
from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import (
    normalize_text_with_mapping,
    strict_match,
)
from backend_v2.settings import get_settings

logger = logging.getLogger(__name__)

__all__ = ["validate_evidence"]


def _validate_quote_segment_bounds(quotes: tuple[str, ...]) -> None:
    """Validate individual quote segment non-emptiness, span ceiling, and multi-segment floor.

    Args:
        quotes: Non-empty tuple of extracted quote segments.

    Raises:
        SemanticEvidenceError: If any segment is empty/whitespace, exceeds max_citation_span_chars,
            or falls below min_multi_segment_floor_chars when multiple segments are provided.
    """
    settings = get_settings()
    max_span_chars = settings.max_citation_span_chars
    min_floor_chars = settings.min_multi_segment_floor_chars
    for quote in quotes:
        if not quote or not quote.strip():
            raise SemanticEvidenceError(message="Lexical validation failed: a quote normalized to empty string.")
        if max_span_chars > 0 and len(quote) > max_span_chars:
            raise SemanticEvidenceError(
                message=f"Quote length exceeds safety limit ({len(quote)} > {max_span_chars} chars)."
            )

    if len(quotes) > 1:
        for quote in quotes:
            if len(quote) < min_floor_chars:
                raise SemanticEvidenceError(
                    message=(
                        f"Multi-segment quote segment under floor: segment length {len(quote)} "
                        f"< {min_floor_chars} chars."
                    )
                )


def _validate_directive_boundaries(
    pdf_text: str,
    quotes: tuple[str, ...],
    strictness_level: int,
    locale: str | None,
    lexical_strictness_level: int,
) -> None:
    """Enforce single-document buffer boundary isolation across <ai_context_directive> blocks.

    Args:
        pdf_text: Full source text context potentially containing directive tags.
        quotes: Tuple of extracted quote segments.
        strictness_level: Scoring strictness tolerance boundary percentage.
        locale: Optional locale string for morphological matching.
        lexical_strictness_level: Sovereign workflow lexical strictness level (0-100).

    Raises:
        SemanticEvidenceError: If quote segments span across discrete <ai_context_directive> blocks.
    """
    directive_matches = list(
        re.finditer(r"<ai_context_directive[^>]*>(.*?)</ai_context_directive>", pdf_text, re.DOTALL | re.IGNORECASE)
    )
    if not directive_matches:
        return

    matched_in_any_directive = False
    for d_match in directive_matches:
        d_text = d_match.group(1)
        if strict_match(d_text, quotes).is_valid:
            matched_in_any_directive = True
            break
        if lexical_strictness_level < 100:
            norm_d, _ = normalize_text_with_mapping(d_text)
            all_segs_valid = True
            for q in quotes:
                norm_q, _ = normalize_text_with_mapping(q)
                if not is_lexically_valid(
                    q,
                    norm_q,
                    norm_d,
                    strictness_level=strictness_level,
                    locale=locale,
                    source_text=d_text,
                    lexical_strictness_level=lexical_strictness_level,
                ).is_valid:
                    all_segs_valid = False
                    break
            if all_segs_valid:
                matched_in_any_directive = True
                break

    if not matched_in_any_directive:
        found_in_blocks: set[int] = set()
        for idx, d_match in enumerate(directive_matches):
            d_text = d_match.group(1)
            norm_d, _ = normalize_text_with_mapping(d_text)
            for q in quotes:
                norm_q, _ = normalize_text_with_mapping(q)
                if norm_d.find(norm_q) != -1:
                    found_in_blocks.add(idx)
        if len(found_in_blocks) > 1:
            raise SemanticEvidenceError(
                message=(
                    "Cross-document chimera: quote segments span across discrete "
                    "<ai_context_directive> document boundaries."
                )
            )


def _validate_speaker_provenance(
    pdf_text: str,
    quotes: tuple[str, ...],
    target_speaker: TargetSpeaker,
    strictness_level: int,
    locale: str | None,
    lexical_strictness_level: int,
) -> None:
    """Enforce speaker stream provenance isolation and assignment context quarantine.

    Args:
        pdf_text: Source text context.
        quotes: Tuple of extracted quote segments.
        target_speaker: Target speaker stream (USER or AI) for conversational dialogue.
        strictness_level: Scoring strictness tolerance boundary percentage.
        locale: Optional locale string for morphological matching.
        lexical_strictness_level: Sovereign workflow lexical strictness level (0-100).

    Raises:
        SemanticEvidenceError: If a quote breaches structured speaker or assignment provenance boundaries.
    """
    user_payload_matches = re.findall(r"<user_payload>(.*?)</user_payload>", pdf_text, re.IGNORECASE | re.DOTALL)
    ai_draft_matches = re.findall(r"<ai_draft_context>(.*?)</ai_draft_context>", pdf_text, re.IGNORECASE | re.DOTALL)
    assignment_matches = re.findall(
        r"<assignment_context>(.*?)</assignment_context>", pdf_text, re.IGNORECASE | re.DOTALL
    )
    if not (user_payload_matches or ai_draft_matches or assignment_matches):
        return

    allowed_source_text = (
        "\n\n".join(user_payload_matches) if target_speaker == TargetSpeaker.USER else "\n\n".join(ai_draft_matches)
    )
    if not allowed_source_text:
        raise SemanticEvidenceError(message="PROVENANCE_VIOLATION: Quote breached structured provenance boundary")

    norm_allowed_source, _ = normalize_text_with_mapping(allowed_source_text)
    for quote in quotes:
        norm_quote, _ = normalize_text_with_mapping(quote)
        if not is_lexically_valid(
            quote,
            norm_quote,
            norm_allowed_source,
            strictness_level=strictness_level,
            locale=locale,
            source_text=allowed_source_text,
            lexical_strictness_level=lexical_strictness_level,
        ).is_valid:
            raise SemanticEvidenceError(message="PROVENANCE_VIOLATION: Quote breached structured provenance boundary")


def _validate_reasoning_trace(pdf_text: str, reasoning_trace: str, quotes_count: int) -> None:
    """Verify reasoning trace consistency, non-empty syntactic anchor, and physical anchor presence.

    Args:
        pdf_text: Source text context.
        reasoning_trace: LLM reasoning trace string.
        quotes_count: Number of quote segments being validated.

    Raises:
        SemanticEvidenceError: If the trace contradicts positive extraction, declares an empty anchor,
            or references a hallucinated syntactic anchor absent from pdf_text.
    """
    trace_lower = reasoning_trace.lower()

    if "[5. validation decision: fail]" in trace_lower or "condition not met" in trace_lower:
        logger.error(
            "Lexical Verifier failed: Trace Contradiction.",
            extra={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.value, "quote_count": quotes_count},
        )
        raise SemanticEvidenceError(
            message="Logical contradiction: Trace concluded Fail, but exact_quotes was populated."
        )

    if "[2. syntactic anchor: none]" in trace_lower or "[2. syntactic anchor: n/a]" in trace_lower:
        logger.error(
            "Lexical Verifier failed: Empty Anchor.",
            extra={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.value, "quote_count": quotes_count},
        )
        raise SemanticEvidenceError(
            message="Anchorless Extraction: Cannot pass validation without a physical syntactic anchor."
        )

    regex_pattern = r"\[2\.\s*SYNTACTIC\s*ANCHOR:\s*['\"]([^'\"]+)['\"]\]"
    anchor_match = re.search(regex_pattern, reasoning_trace, re.IGNORECASE)
    if anchor_match:
        parsed_anchor = anchor_match.group(1)
        if parsed_anchor.lower() not in ("none", "n/a") and not strict_match(pdf_text, [parsed_anchor]).is_valid:
            logger.error(
                "Lexical Verifier failed: Hallucinated Anchor.",
                extra={
                    "error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.value,
                    "anchor_length": len(parsed_anchor),
                },
            )
            raise SemanticEvidenceError(
                message=f"Hallucinated Anchor: The anchor '{parsed_anchor}' does not exist in the source text."
            )


def _validate_multi_segment_monotonic_spans(norm_pdf: str, norm_quotes: Sequence[str]) -> None:
    """Enforce monotonic forward ordering and bounding span ceiling for multi-segment quotes.

    Args:
        norm_pdf: Normalized source document string.
        norm_quotes: Sequence of normalized quote segments (len > 1).

    Raises:
        SemanticEvidenceError: If segments appear only in inverted order or exceed MAX_CITATION_SPAN_CHARS.
    """
    m = len(norm_quotes)
    occurrences: list[list[int]] = []
    for nq in norm_quotes:
        occ: list[int] = []
        idx = 0
        while True:
            pos = norm_pdf.find(nq, idx)
            if pos == -1:
                break
            occ.append(pos)
            idx = pos + 1
        occurrences.append(occ)

    if not all(len(occ) > 0 for occ in occurrences):
        return

    for k in range(m - 1):
        occ_k = occurrences[k]
        occ_next = occurrences[k + 1]
        len_k = len(norm_quotes[k])
        valid_forward_pair = any(o_next > o_k + len_k - 1 for o_k in occ_k for o_next in occ_next)
        if not valid_forward_pair:
            raise SemanticEvidenceError(
                message=f"Inverted segment order: segment {k + 2} precedes segment {k + 1} in source text."
            )

    min_chain_span: int | None = None
    for s1 in occurrences[0]:
        prev_end = s1 + len(norm_quotes[0]) - 1
        chain_ok = True
        for seg_idx in range(1, m):
            nxt = norm_pdf.find(norm_quotes[seg_idx], prev_end + 1)
            if nxt == -1:
                chain_ok = False
                break
            prev_end = nxt + len(norm_quotes[seg_idx]) - 1
        if chain_ok:
            span_len = prev_end - s1
            if min_chain_span is None or span_len < min_chain_span:
                min_chain_span = span_len

    max_span_chars = get_settings().max_citation_span_chars
    if max_span_chars > 0 and min_chain_span is not None and min_chain_span > max_span_chars:
        raise SemanticEvidenceError(
            message=(f"Bounding span exceeds limit: span distance ({min_chain_span} chars) > {max_span_chars} chars.")
        )


def _match_candidate_s1_chain(norm_pdf: str, norm_quotes: Sequence[str]) -> list[GateMatchResultDTO] | None:
    """Find a valid forward-ordered chain of normalized quote segments starting from candidate s_1 anchors.

    Args:
        norm_pdf: Normalized source document string.
        norm_quotes: Sequence of normalized quote segments.

    Returns:
        List of GateMatchResultDTO instances for the matched chain, or None if no exact chain matches.
    """
    max_span_chars = get_settings().max_citation_span_chars
    m = len(norm_quotes)
    q0 = norm_quotes[0]
    search_offset = 0
    while True:
        pos_0 = norm_pdf.find(q0, search_offset)
        if pos_0 == -1:
            return None
        s1 = pos_0
        prev_end = pos_0 + len(q0) - 1
        segments = [GateMatchResultDTO(is_valid=True, start_idx=s1, end_idx=prev_end)]
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
            segments.append(GateMatchResultDTO(is_valid=True, start_idx=next_pos, end_idx=end_k))
            prev_end = end_k

        if chain_valid:
            return segments

        search_offset = pos_0 + 1


def _slice_physical_quotes(
    pdf_text: str,
    norm_pdf: str,
    pdf_map: Sequence[int],
    quotes: tuple[str, ...],
    norm_quotes: Sequence[str],
    matched_segments: Sequence[GateMatchResultDTO] | None,
    strictness_level: int,
    locale: str | None,
    lexical_strictness_level: int,
) -> tuple[str, ...]:
    """Slice exact physical substrings from pdf_text using normalized index mapping.

    Args:
        pdf_text: Original source document string.
        norm_pdf: Normalized source document string.
        pdf_map: Index mapping from norm_pdf character positions to pdf_text indices.
        quotes: Original quote segment tuple.
        norm_quotes: Normalized quote segment sequence.
        matched_segments: Pre-matched exact segment coordinates if available.
        strictness_level: Scoring strictness tolerance boundary percentage.
        locale: Optional locale string for morphological matching.
        lexical_strictness_level: Sovereign workflow lexical strictness level (0-100).

    Returns:
        Tuple of physical quote substrings sliced from pdf_text.

    Raises:
        SemanticEvidenceError: If fallback lexical validation fails for any segment.
    """
    extracted_quotes: list[str] = []
    if matched_segments is not None:
        for seg in matched_segments:
            start_idx = pdf_map[seg.start_idx]
            end_idx = pdf_map[seg.end_idx]
            extracted_quotes.append(pdf_text[start_idx : end_idx + 1])
        return tuple(extracted_quotes)

    for idx, quote in enumerate(quotes):
        norm_quote = norm_quotes[idx]
        match_result = is_lexically_valid(
            quote=quote,
            norm_quote=norm_quote,
            norm_text=norm_pdf,
            strictness_level=strictness_level,
            locale=locale,
            source_text=pdf_text,
            lexical_strictness_level=lexical_strictness_level,
        )
        if not match_result.is_valid:
            raise SemanticEvidenceError(
                message=(
                    f"Lexical validation failed: exact_quote '{quote[:50]}...' not found. "
                    "See logs for detailed fuzzy scores."
                )
            )
        start_idx = pdf_map[match_result.start_idx]
        end_idx = pdf_map[match_result.end_idx]
        extracted_quotes.append(pdf_text[start_idx : end_idx + 1])

    return tuple(extracted_quotes)


def validate_evidence(
    pdf_text: str,
    exact_quotes: Sequence[str] | tuple[str, ...] | list[str] | None,
    reasoning_trace: str | None = None,
    syntactic_anchors: list[str] | None = None,
    contextual_override: bool = False,
    locale: str | None = None,
    strictness_level: int = 50,
    target_speaker: TargetSpeaker = TargetSpeaker.USER,
    lexical_strictness_level: int = 50,
) -> tuple[str, ...] | None:
    """Validate evidence strictly and extract the exact physical string segments.

    Enforces candidate s_1 anchor iteration, monotonic ordering (s_k < e_k < s_{k+1}),
    single-document buffer boundary isolation, individual segment floor of 30 characters when m > 1,
    and global bounding span ceiling (e_m - s_1 <= 1000 characters).

    Args:
        pdf_text: The source text context.
        exact_quotes: Ordered quote segment(s) extracted by the LLM.
        reasoning_trace: Optional trace containing the LLM's logical breakdown.
        syntactic_anchors: Optional list of syntactic anchors to locate.
        contextual_override: If True, skips lexical validation.
        locale: Optional locale string to determine the fuzzy fallback threshold.
        strictness_level: Strictness tolerance boundary percentage.
        target_speaker: Target speaker stream (USER or AI) for conversational dialogue.
        lexical_strictness_level: Sovereign workflow lexical strictness level (0-100 continuous).

    Returns:
        The exact physical quotes tuple if valid, or None if overridden.

    Raises:
        SemanticEvidenceError: If lexical validation, single-document buffer boundary isolation,
            monotonic ordering, span ceiling, or logical Trace consistency fails.
    """
    _ = syntactic_anchors
    if contextual_override:
        logger.info("Lexical Verifier skipped: cognitive override (contextual_override) is active.")
        return None

    if not exact_quotes:
        raise SemanticEvidenceError(
            message="Lexical validation failed: exact_quotes is required when contextual_override is False."
        )

    quotes = tuple(exact_quotes)
    _validate_quote_segment_bounds(quotes)
    _validate_directive_boundaries(pdf_text, quotes, strictness_level, locale, lexical_strictness_level)
    _validate_speaker_provenance(pdf_text, quotes, target_speaker, strictness_level, locale, lexical_strictness_level)

    if reasoning_trace:
        _validate_reasoning_trace(pdf_text, reasoning_trace, len(quotes))

    norm_pdf, pdf_map = normalize_text_with_mapping(pdf_text)
    if not norm_pdf:
        raise SemanticEvidenceError(message="Lexical validation failed: source text normalized to empty string.")

    norm_quotes: list[str] = []
    for quote in quotes:
        clean_q = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", quote))
        norm_q, _ = normalize_text_with_mapping(clean_q)
        if not norm_q:
            raise SemanticEvidenceError(message="Lexical validation failed: a quote normalized to empty string.")
        norm_quotes.append(norm_q)

    if len(quotes) > 1:
        _validate_multi_segment_monotonic_spans(norm_pdf, norm_quotes)

    matched_segments = _match_candidate_s1_chain(norm_pdf, norm_quotes)
    return _slice_physical_quotes(
        pdf_text=pdf_text,
        norm_pdf=norm_pdf,
        pdf_map=pdf_map,
        quotes=quotes,
        norm_quotes=norm_quotes,
        matched_segments=matched_segments,
        strictness_level=strictness_level,
        locale=locale,
        lexical_strictness_level=lexical_strictness_level,
    )
