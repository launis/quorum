"""Service for validating evidence using strict lexical anchoring and fuzzy fallbacks."""

import logging
import re
import unicodedata
from collections.abc import Sequence

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.quote_evidence import GateMatchResultDTO, SourceDocumentContext
from backend_v2.models.enums import TargetSpeaker
from backend_v2.services.orchestrator.anchor_validation.lexical_matcher import (
    is_lexically_valid as is_lexically_valid,
)
from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import (
    MAX_CITATION_SPAN_CHARS as MAX_CITATION_SPAN_CHARS,
)
from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import (
    MIN_ENTROPY_GATE_CHARS as MIN_ENTROPY_GATE_CHARS,
)
from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import (
    MIN_MULTI_SEGMENT_FLOOR_CHARS as MIN_MULTI_SEGMENT_FLOOR_CHARS,
)
from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import (
    calculate_fuzzy_score as calculate_fuzzy_score,
)
from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import (
    normalize_text_with_mapping as normalize_text_with_mapping,
)
from backend_v2.services.orchestrator.anchor_validation.lexical_normalizer import (
    strict_match as strict_match,
)

logger = logging.getLogger(__name__)

# Phase 1, Step 2 & Phase 2, Step 2: Re-export extracted symbols using explicit redundant aliases and __all__
__all__ = [
    "MAX_CITATION_SPAN_CHARS",
    "MIN_ENTROPY_GATE_CHARS",
    "MIN_MULTI_SEGMENT_FLOOR_CHARS",
    "AnchorValidationService",
    "calculate_fuzzy_score",
    "is_lexically_valid",
    "normalize_text_with_mapping",
    "strict_match",
]


class AnchorValidationService:
    """TDD-testable service for deterministic evidence anchoring using strict substring matching.

    Enforces a strict Fail-Fast architecture. If lexical validation fails,
    a SemanticEvidenceError is raised immediately to eliminate fabricated quote hallucinations and enforce physical citation provenance.
    """

    MAX_CITATION_SPAN_CHARS: int = MAX_CITATION_SPAN_CHARS
    MIN_MULTI_SEGMENT_FLOOR_CHARS: int = MIN_MULTI_SEGMENT_FLOOR_CHARS
    MIN_ENTROPY_GATE_CHARS: int = MIN_ENTROPY_GATE_CHARS

    @staticmethod
    def normalize_text_with_mapping(text: str) -> tuple[str, list[int]]:
        """Normalizes text and returns a mapping from normalized index to original index.

        Args:
            text: The text to normalize.

        Returns:
            A tuple containing the normalized string and a list mapping
            each character's index in the normalized string to its index in the original string.
        """
        # Phase 1, Step 2: Delegate to extracted leaf normalizer
        return normalize_text_with_mapping(text)

    @staticmethod
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
        # Phase 1, Step 2: Delegate to extracted leaf strict_match
        return strict_match(pdf_text, exact_quotes)

    @staticmethod
    def calculate_fuzzy_score(norm_quote: str, norm_text: str) -> float:
        """Choose fuzzy algorithm based on length of the normalized quote.

        Args:
            norm_quote: The normalized quote string.
            norm_text: The normalized source text context.

        Returns:
            The fuzzy similarity score (0.0 to 100.0).
        """
        # Phase 1, Step 2: Delegate to extracted leaf calculate_fuzzy_score
        return calculate_fuzzy_score(norm_quote, norm_text)

    @staticmethod
    def _is_lexically_valid(
        quote: str | Sequence[str] | tuple[str, ...] | list[str],
        norm_quote: str | Sequence[str] | tuple[str, ...] | list[str],
        norm_text: str,
        strictness_level: int = 50,
        locale: str | None = None,
        source_text: str | None = None,
        lexical_strictness_level: int = 50,
    ) -> GateMatchResultDTO:
        """Helper to determine if a quote (or multi-segment quote) is lexically valid against normalized text.

        Enforces candidate s_1 anchor iteration, forward-scan search, monotonic ordering (s_k < e_k < s_{k+1}),
        individual segment floor of 30 characters when m > 1, and global span limit (<= 1000 characters).

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
        # Phase 2, Step 2: Delegate to extracted multi-tier lexical matcher
        return is_lexically_valid(
            quote=quote,
            norm_quote=norm_quote,
            norm_text=norm_text,
            strictness_level=strictness_level,
            locale=locale,
            source_text=source_text,
            lexical_strictness_level=lexical_strictness_level,
        )

    @staticmethod
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
        """Validates evidence strictly and extracts the exact physical string segments.

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
        if contextual_override:
            logger.info("Lexical Verifier skipped: cognitive override (contextual_override) is active.")
            return None

        if not exact_quotes:
            raise SemanticEvidenceError(
                message="Lexical validation failed: exact_quotes is required when contextual_override is False."
            )

        quotes = tuple(exact_quotes)
        m = len(quotes)

        for quote in quotes:
            if not quote or not quote.strip():
                raise SemanticEvidenceError(message="Lexical validation failed: a quote normalized to empty string.")
            if len(quote) > MAX_CITATION_SPAN_CHARS:
                raise SemanticEvidenceError(
                    message=f"Quote length exceeds safety limit ({len(quote)} > {MAX_CITATION_SPAN_CHARS} chars)."
                )

        if m > 1:
            for quote in quotes:
                if len(quote) < MIN_MULTI_SEGMENT_FLOOR_CHARS:
                    raise SemanticEvidenceError(
                        message=(
                            f"Multi-segment quote segment under floor: segment length {len(quote)} "
                            f"< {MIN_MULTI_SEGMENT_FLOOR_CHARS} chars."
                        )
                    )

        # Single-Document Buffer Boundary Isolation: Check for <ai_context_directive> document wrappers
        directive_matches = list(
            re.finditer(r"<ai_context_directive[^>]*>(.*?)</ai_context_directive>", pdf_text, re.DOTALL | re.IGNORECASE)
        )
        if directive_matches:
            matched_in_any_directive = False
            for d_match in directive_matches:
                d_text = d_match.group(1)
                if AnchorValidationService.strict_match(d_text, quotes).is_valid:
                    matched_in_any_directive = True
                    break
                if lexical_strictness_level < 100:
                    norm_d, _ = AnchorValidationService.normalize_text_with_mapping(d_text)
                    all_segs_valid = True
                    for q in quotes:
                        norm_q, _ = AnchorValidationService.normalize_text_with_mapping(q)
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
                # Check for cross-document chimera where segments span across different directive blocks
                found_in_blocks: set[int] = set()
                for idx, d_match in enumerate(directive_matches):
                    d_text = d_match.group(1)
                    norm_d, _ = AnchorValidationService.normalize_text_with_mapping(d_text)
                    for q in quotes:
                        norm_q, _ = AnchorValidationService.normalize_text_with_mapping(q)
                        if norm_d.find(norm_q) != -1:
                            found_in_blocks.add(idx)
                if len(found_in_blocks) > 1:
                    raise SemanticEvidenceError(
                        message="Cross-document chimera: quote segments span across discrete <ai_context_directive> document boundaries."
                    )

        # Pre-Flight Provenance Check with assignment_context boundary defense
        user_payload_matches = re.findall(r"<user_payload>(.*?)</user_payload>", pdf_text, re.IGNORECASE | re.DOTALL)
        ai_draft_matches = re.findall(
            r"<ai_draft_context>(.*?)</ai_draft_context>", pdf_text, re.IGNORECASE | re.DOTALL
        )
        assignment_matches = re.findall(
            r"<assignment_context>(.*?)</assignment_context>", pdf_text, re.IGNORECASE | re.DOTALL
        )
        if user_payload_matches or ai_draft_matches or assignment_matches:
            if target_speaker == TargetSpeaker.USER:
                allowed_source_text = "\n\n".join(user_payload_matches)
            else:
                allowed_source_text = "\n\n".join(ai_draft_matches)

            if not allowed_source_text:
                raise SemanticEvidenceError(
                    message="PROVENANCE_VIOLATION: Quote breached structured provenance boundary"
                )

            norm_allowed_source, _ = AnchorValidationService.normalize_text_with_mapping(allowed_source_text)
            for quote in quotes:
                norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(quote)
                if not is_lexically_valid(
                    quote,
                    norm_quote,
                    norm_allowed_source,
                    strictness_level=strictness_level,
                    locale=locale,
                    source_text=allowed_source_text,
                    lexical_strictness_level=lexical_strictness_level,
                ).is_valid:
                    raise SemanticEvidenceError(
                        message="PROVENANCE_VIOLATION: Quote breached structured provenance boundary"
                    )

        if reasoning_trace:
            trace_lower = reasoning_trace.lower()

            # 1. Trace Contradiction Ban
            if "[5. validation decision: fail]" in trace_lower or "condition not met" in trace_lower:
                logger.error("Lexical Verifier failed: Trace Contradiction.", extra={"exact_quotes": quotes})
                raise SemanticEvidenceError(
                    message="Logical contradiction: Trace concluded Fail, but exact_quotes was populated."
                )

            # 2. Empty Anchor Ban
            if "[2. syntactic anchor: none]" in trace_lower or "[2. syntactic anchor: n/a]" in trace_lower:
                logger.error("Lexical Verifier failed: Empty Anchor.", extra={"exact_quotes": quotes})
                raise SemanticEvidenceError(
                    message="Anchorless Extraction: Cannot pass validation without a physical syntactic anchor."
                )

            # 3. Lexical Reality Ban
            regex_pattern = r"\[2\.\s*SYNTACTIC\s*ANCHOR:\s*['\"]([^'\"]+)['\"]\]"
            anchor_match = re.search(regex_pattern, reasoning_trace, re.IGNORECASE)
            if anchor_match:
                parsed_anchor = anchor_match.group(1)
                if parsed_anchor.lower() not in ["none", "n/a"]:
                    if not AnchorValidationService.strict_match(pdf_text, [parsed_anchor]).is_valid:
                        logger.error(
                            "Lexical Verifier failed: Hallucinated Anchor.",
                            extra={"parsed_anchor": parsed_anchor},
                        )
                        raise SemanticEvidenceError(
                            message=(
                                f"Hallucinated Anchor: The anchor '{parsed_anchor}' does not exist in the source text."
                            )
                        )

        norm_pdf, pdf_map = AnchorValidationService.normalize_text_with_mapping(pdf_text)
        if not norm_pdf:
            raise SemanticEvidenceError(message="Lexical validation failed: source text normalized to empty string.")

        norm_quotes: list[str] = []
        for quote in quotes:
            clean_q = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", quote))
            norm_q, _ = AnchorValidationService.normalize_text_with_mapping(clean_q)
            if not norm_q:
                raise SemanticEvidenceError(message="Lexical validation failed: a quote normalized to empty string.")
            norm_quotes.append(norm_q)

        # Monotonic Ordering & Span Limit Pre-Flight Check for Multi-Segment Quotes
        if m > 1:
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

            if all(len(occ) > 0 for occ in occurrences):
                for k in range(m - 1):
                    occ_k = occurrences[k]
                    occ_next = occurrences[k + 1]
                    len_k = len(norm_quotes[k])
                    valid_forward_pair = any(o_next > o_k + len_k - 1 for o_k in occ_k for o_next in occ_next)
                    if not valid_forward_pair:
                        raise SemanticEvidenceError(
                            message=f"Inverted segment order: segment {k + 2} precedes segment {k + 1} in source text."
                        )

                min_chain_span = None
                for s1 in occurrences[0]:
                    prev_end = s1 + len(norm_quotes[0]) - 1
                    chain_ok = True
                    for seg_idx in range(1, m):
                        nxt = norm_pdf.find(norm_quotes[seg_idx], prev_end + 1)
                        if nxt == -1:
                            chain_ok = False
                            break
                        end_seg = nxt + len(norm_quotes[seg_idx]) - 1
                        prev_end = end_seg
                    if chain_ok:
                        span_len = prev_end - s1
                        if min_chain_span is None or span_len < min_chain_span:
                            min_chain_span = span_len

                if min_chain_span is not None and min_chain_span > MAX_CITATION_SPAN_CHARS:
                    raise SemanticEvidenceError(
                        message=(
                            f"Bounding span exceeds limit: span distance ({min_chain_span} chars) "
                            f"> {MAX_CITATION_SPAN_CHARS} chars."
                        )
                    )

        # Symmetrical Extraction via Candidate s_1 Iteration
        matched_segments: list[GateMatchResultDTO] | None = None
        q0 = norm_quotes[0]
        search_offset = 0
        while True:
            pos_0 = norm_pdf.find(q0, search_offset)
            if pos_0 == -1:
                break
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
                if end_k - s1 > MAX_CITATION_SPAN_CHARS:
                    chain_valid = False
                    break
                segments.append(GateMatchResultDTO(is_valid=True, start_idx=next_pos, end_idx=end_k))
                prev_end = end_k

            if chain_valid:
                matched_segments = segments
                break

            search_offset = pos_0 + 1

        extracted_quotes: list[str] = []
        if matched_segments is not None:
            for seg in matched_segments:
                s_k = seg.start_idx
                e_k = seg.end_idx
                if 0 <= s_k <= e_k < len(pdf_map):
                    start_idx = pdf_map[s_k]
                    end_idx = pdf_map[e_k]
                    extracted_quotes.append(pdf_text[start_idx : end_idx + 1])
                else:
                    extracted_quotes.append(quotes[len(extracted_quotes)])
        else:
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
                start_norm_idx = match_result.start_idx
                end_norm_idx = match_result.end_idx
                if 0 <= start_norm_idx <= end_norm_idx < len(pdf_map):
                    start_idx = pdf_map[start_norm_idx]
                    end_idx = pdf_map[end_norm_idx]
                    extracted_quotes.append(pdf_text[start_idx : end_idx + 1])
                else:
                    extracted_quotes.append(quote)

        return tuple(extracted_quotes)

    @staticmethod
    def process_atom_evaluation(
        atom: AtomResultDTO,
        alias_map: dict[str, str],
        source_documents: list[SourceDocumentContext] | None = None,
        mcp_source_texts: dict[str, str] | None = None,
        locale: str | None = None,
        strictness_level: int = 50,
        lexical_strictness_level: int = 50,
    ) -> AtomResultDTO:
        """Process an atom evaluation item, resolving aliases and matching quotes cohesively.

        Validates multi-segment citations as a cohesive tuple against each candidate source
        document, enforcing that all segments resolve monotonically within the same single
        source document buffer and eliminating cross-document chimera matches.

        Args:
            atom: The AtomResultDTO instance to process.
            alias_map: Mapping of short aliases to real document IDs.
            source_documents: List of static source documents.
            mcp_source_texts: Dictionary of MCP provided source texts.
            locale: Optional locale definition.
            strictness_level: Strictness tier (0-100).
            lexical_strictness_level: Sovereign workflow lexical strictness level (0-100 continuous).

        Returns:
            A new mutated AtomResultDTO instance with hydrated source_quote and evaluation_reasoning.
        """
        from backend_v2.utils.alias_engine import AliasEngine

        engine = AliasEngine(alias_map=alias_map)

        hydrated_reasoning = None
        if atom.evaluation_reasoning:
            hydrated_reasoning = engine.hydrate_reasoning_text(atom.evaluation_reasoning)

        # Phase 1, Step 1.1: Shallow C-level update via model_copy(update={...})
        if atom.contextual_override:
            return atom.model_copy(update={"source_quotes": None, "evaluation_reasoning": hydrated_reasoning})

        validated_quotes = atom.source_quotes
        if atom.source_quotes is not None:
            matched = False
            # 1. Match as a cohesive tuple against static source documents
            if source_documents:
                for doc in source_documents:
                    if doc.text_content and doc.opaque_id:
                        if AnchorValidationService.strict_match(doc.text_content, atom.source_quotes).is_valid:
                            matched = True
                            break
                        if lexical_strictness_level < 100:
                            norm_doc, _ = AnchorValidationService.normalize_text_with_mapping(doc.text_content)
                            if is_lexically_valid(
                                quote=atom.source_quotes,
                                norm_quote=tuple(
                                    AnchorValidationService.normalize_text_with_mapping(q)[0]
                                    for q in atom.source_quotes
                                ),
                                norm_text=norm_doc,
                                strictness_level=strictness_level,
                                locale=locale,
                                source_text=doc.text_content,
                                lexical_strictness_level=lexical_strictness_level,
                            ).is_valid:
                                matched = True
                                break
                            # Also check per-segment in this single isolated document buffer
                            all_segs = True
                            for q in atom.source_quotes:
                                nq, _ = AnchorValidationService.normalize_text_with_mapping(q)
                                if not is_lexically_valid(
                                    quote=q,
                                    norm_quote=nq,
                                    norm_text=norm_doc,
                                    strictness_level=strictness_level,
                                    locale=locale,
                                    source_text=doc.text_content,
                                    lexical_strictness_level=lexical_strictness_level,
                                ).is_valid:
                                    all_segs = False
                                    break
                            if all_segs:
                                matched = True
                                break

            # 2. Match as a cohesive tuple against dynamic MCP source texts
            if not matched and mcp_source_texts:
                for mcp_text in mcp_source_texts.values():
                    if mcp_text:
                        if AnchorValidationService.strict_match(mcp_text, atom.source_quotes).is_valid:
                            matched = True
                            break
                        if lexical_strictness_level < 100:
                            norm_mcp, _ = AnchorValidationService.normalize_text_with_mapping(mcp_text)
                            all_segs = True
                            for q in atom.source_quotes:
                                nq, _ = AnchorValidationService.normalize_text_with_mapping(q)
                                if not is_lexically_valid(
                                    quote=q,
                                    norm_quote=nq,
                                    norm_text=norm_mcp,
                                    strictness_level=strictness_level,
                                    locale=locale,
                                    source_text=mcp_text,
                                    lexical_strictness_level=lexical_strictness_level,
                                ).is_valid:
                                    all_segs = False
                                    break
                            if all_segs:
                                matched = True
                                break

        # Phase 1, Step 1.1: Shallow C-level update via model_copy(update={...})
        return atom.model_copy(update={"source_quotes": validated_quotes, "evaluation_reasoning": hydrated_reasoning})
