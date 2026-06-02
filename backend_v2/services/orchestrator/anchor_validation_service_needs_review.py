import logging
import re
import unicodedata

from rapidfuzz import fuzz

from backend_v2.exceptions import ErrorCodes, SemanticEvidenceError

logger = logging.getLogger(__name__)


class AnchorValidationService:
    """TDD-testable service for deterministic evidence anchoring using RapidFuzz.

    Enforces a strict Fail-Fast architecture. If lexical validation fails,
    a SemanticEvidenceError is raised immediately to eliminate LLM hallucinations.
    """

    @staticmethod
    def normalize_text_with_mapping(text: str) -> tuple[str, list[int]]:
        """Normalizes text and returns a mapping from normalized index to original index.

        Args:
            text: Input string to process and normalize.

        Returns:
            A tuple containing the normalized lower-case alphanumeric string and
            a list mapping each normalized char index back to its original character position.
        """
        if not text:
            return "", []

        norm_chars: list[str] = []
        index_map: list[int] = []
        for i, char in enumerate(text):
            norm_char = unicodedata.normalize("NFKC", char).lower()
            norm_char = re.sub(r"[\W_]+", "", norm_char)
            if norm_char:
                for nc in norm_char:
                    norm_chars.append(nc)
                    index_map.append(i)

        return "".join(norm_chars), index_map

    @staticmethod
    def fuzzy_match(pdf_text: str, exact_quote: str, threshold: float = 85.0) -> bool:
        """Phase 2: O(N) Anchoring using RapidFuzz partial_ratio.

        Args:
            pdf_text: Source text.
            exact_quote: Quote string to match.
            threshold: Float passing threshold ratio.

        Returns:
            Boolean indicating whether the fuzzy score matches or exceeds the threshold.
        """
        if not exact_quote or not pdf_text:
            return False

        norm_pdf, _ = AnchorValidationService.normalize_text_with_mapping(pdf_text)
        norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(exact_quote)

        if not norm_quote:
            return False

        score = float(fuzz.partial_ratio(norm_quote, norm_pdf))
        return score >= threshold

    @staticmethod
    def validate_evidence(
        pdf_text: str,
        exact_quote: str | None,
        reasoning_trace: str | None = None,
        contextual_override: bool = False,
    ) -> str | None:
        """Validates evidence with RapidFuzz and extracts the exact physical string.

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
            logger.error("Lexical validation failed: exact_quote is missing when contextual_override is False.")
            raise SemanticEvidenceError(
                message="Lexical validation failed: exact_quote is required when contextual_override is False.",
                details={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.value},
            )

        if reasoning_trace:
            trace_lower = reasoning_trace.lower()

            # 1. Trace Contradiction Ban
            if "[5. validation decision: fail]" in trace_lower or "condition not met" in trace_lower:
                logger.warning("Lexical Verifier failed: Trace Contradiction.", extra={"exact_quote": exact_quote})
                raise SemanticEvidenceError(
                    message="Logical contradiction: Trace concluded Fail, but exact_quote was populated.",
                    details={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.value},
                )

            # 2. Empty Anchor Ban
            if "[2. syntactic anchor: none]" in trace_lower or "[2. syntactic anchor: n/a]" in trace_lower:
                logger.warning("Lexical Verifier failed: Empty Anchor.", extra={"exact_quote": exact_quote})
                raise SemanticEvidenceError(
                    message="Anchorless Extraction: Cannot pass validation without a physical syntactic anchor.",
                    details={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.value},
                )

            # 3. Lexical Reality Ban
            regex_pattern = r"\[2\.\s*SYNTACTIC\s*ANCHOR:\s*['\"]([^'\"]+)['\"]\]"
            anchor_match = re.search(regex_pattern, reasoning_trace, re.IGNORECASE)
            if anchor_match:
                parsed_anchor = anchor_match.group(1)
                if parsed_anchor.lower() not in ["none", "n/a"]:
                    if not AnchorValidationService.fuzzy_match(pdf_text, parsed_anchor, threshold=85.0):
                        logger.warning(
                            "Lexical Verifier failed: Hallucinated Anchor.",
                            extra={"parsed_anchor": parsed_anchor},
                        )
                        raise SemanticEvidenceError(
                            message=f"Hallucinated Anchor: The anchor '{parsed_anchor}' does not exist in the source text.",
                            details={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.value},
                        )

        norm_pdf, pdf_map = AnchorValidationService.normalize_text_with_mapping(pdf_text)
        norm_quote, _ = AnchorValidationService.normalize_text_with_mapping(exact_quote)

        if not norm_quote:
            logger.error("Lexical validation failed: exact_quote normalized to empty string.")
            raise SemanticEvidenceError(
                message="Lexical validation failed: exact_quote normalized to empty string.",
                details={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.value},
            )

        # Use partial_ratio_alignment to find the exact indices
        alignment = fuzz.partial_ratio_alignment(norm_quote, norm_pdf)
        if alignment is not None and getattr(alignment, "score", 0.0) >= 85.0:
            start_idx = pdf_map[getattr(alignment, "dest_start", 0)]
            end_idx = pdf_map[getattr(alignment, "dest_end", 1) - 1]
            extracted = pdf_text[start_idx : end_idx + 1]
            return extracted

        logger.warning(
            "Backend Lexical Verifier failed: exact_quote not found in source text.", extra={"exact_quote": exact_quote}
        )
        raise SemanticEvidenceError(
            message=f"Lexical validation failed: exact_quote '{exact_quote}' not found in source text.",
            details={"error_code": ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED.value},
        )
