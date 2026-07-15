import difflib
import logging
import re
import unicodedata

from rapidfuzz import fuzz

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.models.enums import ValidationThresholdRatio, get_lexical_fuzz_threshold

logger = logging.getLogger(__name__)


class AnchorValidationService:
    """TDD-testable service for deterministic evidence anchoring using strict substring matching.

    Enforces a strict Fail-Fast architecture. If lexical validation fails,
    a SemanticEvidenceError is raised immediately to eliminate LLM hallucinations.
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

            # Fallback for unicode replacement characters to maximize fuzzy matches
            # since most broken characters in this context are 'ä' -> 'a'
            if char == "\ufffd":
                char = "a"

            # NFD normalization splits diacritics from base characters
            nfd_chars = unicodedata.normalize("NFD", char)

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
    def strict_match(pdf_text: str, exact_quotes: list[str]) -> bool:
        """Phase 2: O(N) Anchoring using strict substring matching.

        Args:
            pdf_text: The source text context.
            exact_quotes: The extracted quotes to search for.

        Returns:
            True if all exact quotes exist in the normalized source text, False otherwise.
        """
        if not exact_quotes or not pdf_text:
            return False

        norm_pdf, _ = AnchorValidationService.normalize_text_with_mapping(pdf_text)

        for quote in exact_quotes:
            if not quote:
                return False
            norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(quote)
            if not norm_quote or norm_quote not in norm_pdf:
                return False

        return True

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
    def validate_evidence(
        pdf_text: str,
        exact_quotes: list[str] | None,
        reasoning_trace: str | None = None,
        contextual_override: bool = False,
        locale: str | None = None,
        strictness_level: int = 50,
    ) -> list[str] | None:
        """Validates evidence strictly and extracts the exact physical string.

        Args:
            pdf_text: The source text context.
            exact_quotes: The quotes extracted by the LLM.
            reasoning_trace: Optional trace containing the LLM's logical breakdown.
            contextual_override: If True, skips lexical validation.
            locale: Optional locale string to determine the fuzzy fallback threshold.

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

            # Use exact O(N) search on normalized text to find indices
            start_norm_idx = norm_pdf.find(norm_quote)
            if start_norm_idx != -1:
                start_idx = pdf_map[start_norm_idx]
                end_idx = pdf_map[start_norm_idx + len(norm_quote) - 1]
                extracted = pdf_text[start_idx : end_idx + 1]
                extracted_quotes.append(extracted)
            else:
                # Entropy Gate: If quote < 10 chars, fuzzy match is forbidden.
                if len(quote) < 10:
                    raise SemanticEvidenceError(
                        message=f"Entropy Gate Failure: Quote '{quote}' is under 10 chars. Fuzzy match is forbidden. 100% exact match required."
                    )

                # Deterministic Tiers based on locale and strictness modifier
                base_threshold = get_lexical_fuzz_threshold(locale)
                if strictness_level >= 100:
                    modifier = 15.0
                elif strictness_level >= 85:
                    modifier = 10.0
                elif strictness_level >= 50:
                    modifier = -5.0
                elif strictness_level >= 30:
                    modifier = -20.0
                else:
                    modifier = -35.0
                tier_threshold = min(100.0, base_threshold + modifier)

                if tier_threshold >= 100.0:
                    raise SemanticEvidenceError(
                        message=f"Lexical validation failed: strictness is ABSOLUTE. 100% exact match required for '{quote[:50]}...'."
                    )

                # Phase 4: Component: Anchor Validation Service
                score = AnchorValidationService.calculate_fuzzy_score(norm_quote, norm_pdf)
                if score >= tier_threshold:
                    logger.warning(
                        f"Lexical Verifier used Fuzzy Fallback for '{quote[:50]}...'. Score {score:.1f}% >= threshold {tier_threshold}%",
                        extra={
                            "exact_quote_snippet": quote[:50],
                            "rapidfuzz_score": score,
                            "strictness_level": strictness_level,
                        },
                    )
                    extracted_quotes.append(quote)
                else:
                    # Phase 2.5: Coverage-based safety net (BP-2)
                    safety_net = ValidationThresholdRatio.COVERAGE_SAFETY_NET.value
                    matcher = difflib.SequenceMatcher(None, norm_quote, norm_pdf)
                    match = matcher.find_longest_match(0, len(norm_quote), 0, len(norm_pdf))

                    coverage_pct = match.size / len(norm_quote) if len(norm_quote) > 0 else 0.0

                    if coverage_pct >= safety_net:
                        logger.warning(
                            f"[AnchorValidation] Coverage-based match: {coverage_pct:.0%} of quote anchored",
                            extra={
                                "exact_quote_snippet": quote[:50],
                                "coverage_pct": coverage_pct,
                                "matched_fragment": norm_quote[match.a : match.a + match.size],
                            },
                        )
                        extracted_quotes.append(quote)
                    else:
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
                        raise SemanticEvidenceError(
                            message=f"Lexical validation failed: exact_quote '{quote[:50]}...' not found. Best match {score:.1f}% < threshold {tier_threshold}%."
                        )

        return extracted_quotes
