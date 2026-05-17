import logging
import re
import unicodedata

from rapidfuzz import fuzz

from backend_v2.exceptions import SemanticEvidenceError

logger = logging.getLogger(__name__)


class AnchorValidationService:
    """TDD-testable service for deterministic evidence anchoring using RapidFuzz.

    Enforces a strict Fail-Fast architecture. If lexical validation fails,
    a SemanticEvidenceError is raised immediately to eliminate LLM hallucinations.
    """

    @staticmethod
    def normalize_text(text: str) -> str:
        """Phase 1: Normalization (NFKC, lowercasing, Regex [^a-z0-9])."""
        if not text:
            return ""
        # 1. NFKC normalization
        text = unicodedata.normalize("NFKC", text)
        # 2. Lowercase
        text = text.lower()
        # 3. Regex: remove non-word characters and underscores (keeps unicode letters)
        text = re.sub(r"[\W_]+", "", text)
        return text

    @staticmethod
    def fuzzy_match(pdf_text: str, exact_quote: str, threshold: float = 90.0) -> bool:
        """Phase 2: O(N) Anchoring using RapidFuzz partial_ratio."""
        if not exact_quote or not pdf_text:
            return False

        norm_pdf = AnchorValidationService.normalize_text(pdf_text)
        norm_quote = AnchorValidationService.normalize_text(exact_quote)

        if not norm_quote:
            return False

        score = fuzz.partial_ratio(norm_quote, norm_pdf)
        return score >= threshold

    @staticmethod
    def validate_evidence(pdf_text: str, exact_quote: str, reasoning_trace: str | None = None) -> str:
        """Validates evidence with RapidFuzz.

        Args:
            pdf_text: The source text context.
            exact_quote: The quote extracted by the LLM.
            reasoning_trace: Optional trace containing the LLM's logical breakdown.

        Returns:
            The exact_quote if valid.

        Raises:
            SemanticEvidenceError: If lexical validation or logical Trace consistency fails.
        """
        if reasoning_trace and exact_quote:
            trace_lower = reasoning_trace.lower()

            # 1. Trace Contradiction Ban
            if "[5. validation decision: fail]" in trace_lower:
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
                    if not AnchorValidationService.fuzzy_match(pdf_text, parsed_anchor):
                        logger.warning(
                            "Lexical Verifier failed: Hallucinated Anchor.",
                            extra={"parsed_anchor": parsed_anchor},
                        )
                        raise SemanticEvidenceError(
                            message=(
                                f"Hallucinated Anchor: The anchor '{parsed_anchor}' does not exist in the source text."
                            )
                        )

        if AnchorValidationService.fuzzy_match(pdf_text, exact_quote):
            return exact_quote

        logger.warning(
            "Backend Lexical Verifier failed: exact_quote not found in source text.", extra={"exact_quote": exact_quote}
        )
        raise SemanticEvidenceError(
            message=f"Lexical validation failed: exact_quote '{exact_quote}' not found in source text."
        )
