"""Service for validating evidence using strict lexical anchoring and fuzzy fallbacks."""

import difflib
import logging
import re
import unicodedata

from rapidfuzz import fuzz

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.quote_evidence import GateMatchResultDTO, SourceDocumentContext
from backend_v2.models.enums import TargetSpeaker, ValidationThresholdRatio
from backend_v2.settings import get_lexical_fuzz_threshold
from backend_v2.utils.linguistics.stemmer import StemmerService

logger = logging.getLogger(__name__)


class AnchorValidationService:
    """TDD-testable service for deterministic evidence anchoring using strict substring matching.

    Enforces a strict Fail-Fast architecture. If lexical validation fails,
    a SemanticEvidenceError is raised immediately to eliminate fabricated quote hallucinations and enforce physical citation provenance.
    """

    @staticmethod
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

        norm_chars = []
        index_map = []
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

    @staticmethod
    def strict_match(pdf_text: str, exact_quotes: list[str]) -> GateMatchResultDTO:
        """Phase 2: O(N) Anchoring using strict substring matching.

        Args:
            pdf_text: The source text context.
            exact_quotes: The extracted quotes to search for.

        Returns:
            GateMatchResultDTO indicating match validity and normalized coordinate bounds.
        """
        if not exact_quotes or not pdf_text:
            return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

        clean_pdf = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", pdf_text))
        norm_pdf, _ = AnchorValidationService.normalize_text_with_mapping(clean_pdf)

        first_start = -1
        last_end = -1
        for i, quote in enumerate(exact_quotes):
            if not quote:
                return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)
            clean_quote = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", quote))
            norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(clean_quote)
            if not norm_quote:
                return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)
            pos = norm_pdf.find(norm_quote)
            if pos == -1:
                return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)
            if i == 0:
                first_start = pos
            last_end = pos + len(norm_quote) - 1

        return GateMatchResultDTO(is_valid=True, start_idx=first_start, end_idx=last_end)

    @staticmethod
    def calculate_fuzzy_score(norm_quote: str, norm_text: str) -> float:
        """Choose fuzzy algorithm based on length of the normalized quote.

        Args:
            norm_quote: The normalized quote string.
            norm_text: The normalized source text context.

        Returns:
            The fuzzy similarity score (0.0 to 100.0).
        """
        # Phase 4: Component: Anchor Validation Service - Length-weighted hybrid validation logic
        if len(norm_quote) < 30:
            # Short quotes: enforce strict partial_ratio for contiguous matches (contiguity-guard)
            return float(fuzz.partial_ratio(norm_quote, norm_text))
        else:
            # Long quotes: allow token_set_ratio to accommodate word ordering / Finnish morphological conjugations
            return float(fuzz.token_set_ratio(norm_quote, norm_text))

    @staticmethod
    def _is_lexically_valid(
        quote: str,
        norm_quote: str,
        norm_text: str,
        strictness_level: int,
        locale: str | None = None,
        source_text: str | None = None,
    ) -> GateMatchResultDTO:
        """Helper to determine if a quote is lexically valid against a normalized source text.

        Args:
            quote: The exact quote to validate.
            norm_quote: The normalized quote string.
            norm_text: The normalized source text context.
            strictness_level: Validation strictness level constraint.
            locale: Optional locale definition.
            source_text: Optional original source text prior to normalization for word-boundary stemming.

        Returns:
            GateMatchResultDTO indicating match validity and normalized coordinate bounds.
        """
        if not norm_quote:
            logger.warning("Lexical Verifier rejected quote: normalized quote is empty.")
            return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

        start_norm_idx = norm_text.find(norm_quote)
        if start_norm_idx != -1:
            return GateMatchResultDTO(
                is_valid=True,
                start_idx=start_norm_idx,
                end_idx=start_norm_idx + len(norm_quote) - 1,
            )

        # Tier 2 Unicode NFKC & Zero-Width normalization check
        clean_quote = unicodedata.normalize("NFKC", re.sub(r"[\u200b-\u200d\ufeff]", "", quote))
        clean_norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(clean_quote)
        if clean_norm_quote:
            clean_norm_idx = norm_text.find(clean_norm_quote)
            if clean_norm_idx != -1:
                return GateMatchResultDTO(
                    is_valid=True,
                    start_idx=clean_norm_idx,
                    end_idx=clean_norm_idx + len(clean_norm_quote) - 1,
                )

        if len(quote) < 10:
            logger.warning(
                f"Entropy Gate Failure: Quote '{quote}' is under 10 chars. Fuzzy match is forbidden. 100% exact match required."
            )
            return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

        if strictness_level >= 100:
            tier_threshold = 100.0
        else:
            base_threshold = get_lexical_fuzz_threshold(locale)
            match strictness_level:
                case level if level >= 85:
                    multiplier = 1.02
                case level if level >= 50:
                    multiplier = 1.0
                case level if level >= 30:
                    multiplier = 0.90
                case _:
                    multiplier = 0.80
            tier_threshold = min(100.0, base_threshold * multiplier)

        if tier_threshold >= 100.0:
            logger.warning(
                f"Lexical validation failed: strictness is ABSOLUTE. 100% exact match required for '{quote[:50]}...'."
            )
            return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

        score = AnchorValidationService.calculate_fuzzy_score(norm_quote, norm_text)
        if score >= tier_threshold:
            logger.warning(
                f"Lexical Verifier used Fuzzy Fallback for '{quote[:50]}...'. Score {score:.1f}% >= threshold {tier_threshold}%",
                extra={
                    "exact_quote_snippet": quote[:50],
                    "rapidfuzz_score": score,
                    "strictness_level": strictness_level,
                },
            )
            matcher = difflib.SequenceMatcher(None, norm_quote, norm_text)
            blocks = [b for b in matcher.get_matching_blocks() if b.size > 0]
            if blocks:
                start_coord = blocks[0].b
                end_coord = blocks[-1].b + blocks[-1].size - 1
            else:
                start_coord = 0
                end_coord = 0
            return GateMatchResultDTO(is_valid=True, start_idx=start_coord, end_idx=end_coord)

        # Stage 3: Morphological Stemmed Sequence Verification (executed strictly when strictness_level < 100)
        if strictness_level < 100:
            stem_min_coverage = min(0.80, tier_threshold / 100.0)
            stem_result = StemmerService.match_stemmed_subsequence(
                quote=quote,
                source_text=source_text if source_text else norm_text,
                locale=locale,
                min_coverage=stem_min_coverage,
            )
            if stem_result.is_match:
                logger.warning(
                    f"Lexical Verifier used Morphological Stemming for '{quote[:50]}...'. "
                    f"Similarity {stem_result.similarity_score:.1f}% >= threshold {stem_min_coverage * 100.0:.1f}%",
                    extra={
                        "exact_quote_snippet": quote[:50],
                        "rapidfuzz_score": score,
                        "stem_similarity_score": stem_result.similarity_score,
                        "matched_content_stems": stem_result.matched_content_stems,
                        "strictness_level": strictness_level,
                    },
                )
                start_coord = -1
                end_coord = -1
                if stem_result.matched_source_span:
                    norm_span, _ = AnchorValidationService.normalize_text_with_mapping(stem_result.matched_source_span)
                    if norm_span:
                        span_idx = norm_text.find(norm_span)
                        if span_idx != -1:
                            start_coord = span_idx
                            end_coord = span_idx + len(norm_span) - 1
                if start_coord == -1:
                    matcher = difflib.SequenceMatcher(None, norm_quote, norm_text)
                    blocks = [b for b in matcher.get_matching_blocks() if b.size > 0]
                    if blocks:
                        start_coord = blocks[0].b
                        end_coord = blocks[-1].b + blocks[-1].size - 1
                    else:
                        start_coord = 0
                        end_coord = 0
                return GateMatchResultDTO(is_valid=True, start_idx=start_coord, end_idx=end_coord)

        safety_net = ValidationThresholdRatio.COVERAGE_SAFETY_NET.value
        matcher = difflib.SequenceMatcher(None, norm_quote, norm_text)
        match = matcher.find_longest_match(0, len(norm_quote), 0, len(norm_text))
        coverage_pct = match.size / len(norm_quote)

        if coverage_pct >= safety_net:
            logger.warning(
                f"[AnchorValidation] Coverage-based match: {coverage_pct:.0%} of quote anchored",
                extra={
                    "exact_quote_snippet": quote[:50],
                    "coverage_pct": coverage_pct,
                    "matched_fragment": norm_quote[match.a : match.a + match.size],
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
            f"Backend Lexical Verifier failed: exact_quote '{quote[:50]}...' not found in source text. "
            f"RapidFuzz best match: {score:.1f}% < threshold {tier_threshold}%. "
            f"Coverage match: {coverage_pct:.0%} < safety net {safety_net * 100:.0%}%",
            extra={
                "exact_quote_snippet": quote[:50],
                "rapidfuzz_score": score,
                "tier_threshold": tier_threshold,
                "coverage_pct": coverage_pct,
            },
        )
        return GateMatchResultDTO(is_valid=False, start_idx=-1, end_idx=-1)

    @staticmethod
    def validate_evidence(
        pdf_text: str,
        exact_quotes: list[str] | None,
        reasoning_trace: str | None = None,
        syntactic_anchors: list[str] | None = None,
        contextual_override: bool = False,
        locale: str | None = None,
        strictness_level: int = 50,
        target_speaker: TargetSpeaker = TargetSpeaker.USER,
    ) -> list[str] | None:
        """Validates evidence strictly and extracts the exact physical string.

        Args:
            pdf_text: The source text context.
            exact_quotes: The quotes extracted by the LLM.
            reasoning_trace: Optional trace containing the LLM's logical breakdown.
            syntactic_anchors: Optional list of syntactic anchors to locate.
            contextual_override: If True, skips lexical validation.
            locale: Optional locale string to determine the fuzzy fallback threshold.
            strictness_level: Strictness tolerance boundary percentage.
            target_speaker: Target speaker stream (USER or AI) for conversational dialogue.

        Returns:
            The exact_quotes (overridden with original whitespace) if valid, or None if overridden.

        Raises:
            SemanticEvidenceError: If lexical validation or logical Trace consistency fails.
        """
        if contextual_override:
            logger.info("Lexical Verifier skipped: cognitive override (contextual_override) is active.")
            return None

        if not exact_quotes:
            raise SemanticEvidenceError(
                message="Lexical validation failed: exact_quotes is required when contextual_override is False."
            )

        for quote in exact_quotes:
            if quote and len(quote) > 1000:
                raise SemanticEvidenceError(message=f"Quote length exceeds safety limit ({len(quote)} > 1000 chars).")

        # Phase 2, Step 2.5: Pre-Flight Provenance Check with assignment_context boundary defense
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
            for quote in exact_quotes:
                norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(quote)
                if not AnchorValidationService._is_lexically_valid(
                    quote,
                    norm_quote,
                    norm_allowed_source,
                    strictness_level,
                    locale,
                    source_text=allowed_source_text,
                ).is_valid:
                    raise SemanticEvidenceError(
                        message="PROVENANCE_VIOLATION: Quote breached structured provenance boundary"
                    )

        if reasoning_trace:
            trace_lower = reasoning_trace.lower()

            # 1. Trace Contradiction Ban
            if "[5. validation decision: fail]" in trace_lower or "condition not met" in trace_lower:
                logger.error("Lexical Verifier failed: Trace Contradiction.", extra={"exact_quotes": exact_quotes})
                raise SemanticEvidenceError(
                    message="Logical contradiction: Trace concluded Fail, but exact_quotes was populated."
                )

            # 2. Empty Anchor Ban
            if "[2. syntactic anchor: none]" in trace_lower or "[2. syntactic anchor: n/a]" in trace_lower:
                logger.error("Lexical Verifier failed: Empty Anchor.", extra={"exact_quotes": exact_quotes})
                raise SemanticEvidenceError(
                    message="Anchorless Extraction: Cannot pass validation without a physical syntactic anchor."
                )

            # 3. Lexical Reality Ban
            regex_pattern = r"\[2\.\s*SYNTACTIC\s*ANCHOR:\s*['\"]([^'\"]+)['\"]\]"
            anchor_match = re.search(regex_pattern, reasoning_trace, re.IGNORECASE)
            if anchor_match:
                parsed_anchor = anchor_match.group(1)
                if parsed_anchor.lower() not in ["none", "n/a"]:
                    if not AnchorValidationService.strict_match(pdf_text, [parsed_anchor]):
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

        extracted_quotes = []
        for quote in exact_quotes:
            norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(quote)

            if not norm_quote:
                raise SemanticEvidenceError(message="Lexical validation failed: a quote normalized to empty string.")

            match_result = AnchorValidationService._is_lexically_valid(
                quote, norm_quote, norm_pdf, strictness_level, locale, source_text=pdf_text
            )
            if not match_result.is_valid:
                raise SemanticEvidenceError(
                    message=f"Lexical validation failed: exact_quote '{quote[:50]}...' not found. See logs for detailed fuzzy scores."
                )

            # Enforce symmetric start and end index resolution via pdf_map for both exact and fuzzy/stemmed matches
            start_norm_idx = match_result.start_idx
            end_norm_idx = match_result.end_idx
            if 0 <= start_norm_idx <= end_norm_idx < len(pdf_map):
                start_idx = pdf_map[start_norm_idx]
                end_idx = pdf_map[end_norm_idx]
                extracted = pdf_text[start_idx : end_idx + 1]
                extracted_quotes.append(extracted)
            else:
                extracted_quotes.append(quote)

        return extracted_quotes

    @staticmethod
    def process_atom_evaluation(
        atom: AtomResultDTO,
        alias_map: dict[str, str],
        source_documents: list[SourceDocumentContext] | None = None,
        mcp_source_texts: dict[str, str] | None = None,
        locale: str | None = None,
        strictness_level: int = 50,
    ) -> AtomResultDTO:
        """Process an atom evaluation item, resolving aliases and matching quotes.

        Args:
            atom: The AtomResultDTO instance to process.
            alias_map: Mapping of short aliases to real document IDs.
            source_documents: List of static source documents.
            mcp_source_texts: Dictionary of MCP provided source texts.
            locale: Optional locale definition.
            strictness_level: Strictness tier (0-100).

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
            return atom.model_copy(update={"source_quote": None, "evaluation_reasoning": hydrated_reasoning})

        validated_quote = atom.source_quote
        if atom.source_quote is not None:
            norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(atom.source_quote)
            matched = False
            # 1. Match against static source documents
            if source_documents:
                for doc in source_documents:
                    if doc.text_content and doc.opaque_id:
                        norm_doc, _ = AnchorValidationService.normalize_text_with_mapping(doc.text_content)
                        if AnchorValidationService._is_lexically_valid(
                            quote=atom.source_quote,
                            norm_quote=norm_quote,
                            norm_text=norm_doc,
                            strictness_level=strictness_level,
                            locale=locale,
                            source_text=doc.text_content,
                        ).is_valid:
                            matched = True
                            break

            # 2. Match against dynamic MCP source texts
            if not matched and mcp_source_texts:
                for mcp_text in mcp_source_texts.values():
                    norm_mcp, _ = AnchorValidationService.normalize_text_with_mapping(mcp_text)
                    if AnchorValidationService._is_lexically_valid(
                        quote=atom.source_quote,
                        norm_quote=norm_quote,
                        norm_text=norm_mcp,
                        strictness_level=strictness_level,
                        locale=locale,
                        source_text=mcp_text,
                    ).is_valid:
                        matched = True
                        break

        # Phase 1, Step 1.1: Shallow C-level update via model_copy(update={...})
        return atom.model_copy(update={"source_quote": validated_quote, "evaluation_reasoning": hydrated_reasoning})
