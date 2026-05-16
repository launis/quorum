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
    def validate_evidence(pdf_text: str, exact_quote: str) -> str:
        """Validates evidence with RapidFuzz.

        Args:
            pdf_text: The source text context.
            exact_quote: The quote extracted by the LLM.

        Returns:
            The exact_quote if valid.

        Raises:
            SemanticEvidenceError: If the quote is not found in the pdf_text.
        """
        if AnchorValidationService.fuzzy_match(pdf_text, exact_quote):
            return exact_quote

        logger.error(
            "Backend Lexical Verifier failed: exact_quote not found in source text.", extra={"exact_quote": exact_quote}
        )
        raise SemanticEvidenceError(
            message=f"Lexical validation failed: exact_quote '{exact_quote}' not found in source text."
        )
