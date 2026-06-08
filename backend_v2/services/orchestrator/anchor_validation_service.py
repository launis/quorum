import logging
import re
import unicodedata

from backend_v2.exceptions import SemanticEvidenceError

logger = logging.getLogger(__name__)


class AnchorValidationService:
    """TDD-testable service for deterministic evidence anchoring using strict substring matching.

    Enforces a strict Fail-Fast architecture. If lexical validation fails,
    a SemanticEvidenceError is raised immediately to eliminate LLM hallucinations.
    """

    @staticmethod
    def normalize_text_with_mapping(text: str) -> tuple[str, list[int]]:
        """Normalizes text and returns a mapping from normalized index to original index."""
        if not text:
            return "", []

        norm_chars = []
        index_map = []
        for i, char in enumerate(text):
            norm_char = unicodedata.normalize("NFKC", char).lower()
            norm_char = re.sub(r"[\W_]+", "", norm_char)
            if norm_char:
                for nc in norm_char:
                    norm_chars.append(nc)
                    index_map.append(i)

        return "".join(norm_chars), index_map

    @staticmethod
    def strict_match(pdf_text: str, exact_quote: str) -> bool:
        """Phase 2: O(N) Anchoring using strict substring matching."""
        if not exact_quote or not pdf_text:
            return False

        norm_pdf, _ = AnchorValidationService.normalize_text_with_mapping(pdf_text)
        norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(exact_quote)

        if not norm_quote:
            return False

        return norm_quote in norm_pdf

    @staticmethod
    def validate_evidence(
        pdf_text: str,
        exact_quote: str | None,
        reasoning_trace: str | None = None,
        contextual_override: bool = False,
    ) -> str | None:
        """Validates evidence strictly and extracts the exact physical string.

        Args:
            pdf_text: The source text context.
            exact_quote: The quote extracted by the LLM.
            reasoning_trace: Optional trace containing the LLM's logical breakdown.
            contextual_override: If True, skips lexical validation.

        Returns:
            The exact_quote (overridden with original whitespace) if valid, or None if overridden.

        Raises:
            SemanticEvidenceError: If lexical validation or logical Trace consistency fails.
        """
        if contextual_override:
            return None

        if not exact_quote:
            raise SemanticEvidenceError(
                message="Lexical validation failed: exact_quote is required when contextual_override is False."
            )

        if reasoning_trace:
            trace_lower = reasoning_trace.lower()

            # 1. Trace Contradiction Ban
            if "[5. validation decision: fail]" in trace_lower or "condition not met" in trace_lower:
                logger.warning("Lexical Verifier failed: Trace Contradiction.", extra={"exact_quote": exact_quote})
                raise SemanticEvidenceError(
                    message="Logical contradiction: Trace concluded Fail, but exact_quote was populated."
                )

            # 2. Empty Anchor Ban
            if "[2. syntactic anchor: none]" in trace_lower or "[2. syntactic anchor: n/a]" in trace_lower:
                logger.warning("Lexical Verifier failed: Empty Anchor.", extra={"exact_quote": exact_quote})
                raise SemanticEvidenceError(
                    message="Anchorless Extraction: Cannot pass validation without a physical syntactic anchor."
                )

            # 3. Lexical Reality Ban
            regex_pattern = r"\[2\.\s*SYNTACTIC\s*ANCHOR:\s*['\"]([^'\"]+)['\"]\]"
            anchor_match = re.search(regex_pattern, reasoning_trace, re.IGNORECASE)
            if anchor_match:
                parsed_anchor = anchor_match.group(1)
                if parsed_anchor.lower() not in ["none", "n/a"]:
                    if not AnchorValidationService.strict_match(pdf_text, parsed_anchor):
                        logger.warning(
                            "Lexical Verifier failed: Hallucinated Anchor.",
                            extra={"parsed_anchor": parsed_anchor},
                        )
                        raise SemanticEvidenceError(
                            message=(
                                f"Hallucinated Anchor: The anchor '{parsed_anchor}' does not exist in the source text."
                            )
                        )

        norm_pdf, pdf_map = AnchorValidationService.normalize_text_with_mapping(pdf_text)
        norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(exact_quote)

        if not norm_quote:
            raise SemanticEvidenceError(message="Lexical validation failed: exact_quote normalized to empty string.")

        # Use exact O(N) search on normalized text to find indices
        start_norm_idx = norm_pdf.find(norm_quote)
        if start_norm_idx != -1:
            start_idx = pdf_map[start_norm_idx]
            end_idx = pdf_map[start_norm_idx + len(norm_quote) - 1]
            extracted = pdf_text[start_idx : end_idx + 1]
            return extracted

        logger.warning(
            "Backend Lexical Verifier failed: exact_quote not found in source text.", extra={"exact_quote": exact_quote}
        )
        raise SemanticEvidenceError(
            message=f"Lexical validation failed: exact_quote '{exact_quote}' not found in source text."
        )
