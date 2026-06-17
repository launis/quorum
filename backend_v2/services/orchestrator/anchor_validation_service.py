import logging
import re
import unicodedata

from rapidfuzz import fuzz

from backend_v2.exceptions import SemanticEvidenceError

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

        # FAST-PATH: Etsi HTML-tagien indeksit ja jätä ne huomioimatta normalisoinnissa
        # Tämä estää esim. <br> -tagien 'b' ja 'r' kirjainten päätymisen normalisoituun tekstiin
        html_tag_indices: set[int] = set()
        for match in re.finditer(r"<[^>]+>", text):
            html_tag_indices.update(range(match.start(), match.end()))

        norm_chars = []
        index_map = []
        for i, char in enumerate(text):
            if i in html_tag_indices:
                continue

            norm_char = unicodedata.normalize("NFKC", char).lower()
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
    def validate_evidence(
        pdf_text: str,
        exact_quotes: list[str] | None,
        reasoning_trace: str | None = None,
        contextual_override: bool = False,
        locale: str | None = None,
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
                # Fallback to RapidFuzz to log the best match ratio
                score = fuzz.partial_ratio(norm_quote, norm_pdf)
                logger.warning(
                    f"Backend Lexical Verifier failed: exact_quote '{quote[:50]}...' not found in source text. "
                    f"RapidFuzz best match: {score:.1f}%",
                    extra={"exact_quote_snippet": quote[:50], "rapidfuzz_score": score},
                )
                raise SemanticEvidenceError(
                    message=f"Lexical validation failed: exact_quote '{quote[:50]}...' not found in source text. Best match was {score:.1f}%."
                )

        return extracted_quotes
