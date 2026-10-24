"""Service for validating evidence using strict lexical anchoring and fuzzy fallbacks."""

from collections.abc import Sequence

from backend_v2.models.dtos.atom_result import AtomResultDTO
from backend_v2.models.dtos.quote_evidence import GateMatchResultDTO, SourceDocumentContext
from backend_v2.models.enums import TargetSpeaker
from backend_v2.services.orchestrator.anchor_validation.atom_evaluation_processor import (
    process_atom_evaluation as process_atom_evaluation,
)
from backend_v2.services.orchestrator.anchor_validation.evidence_validator import (
    validate_evidence as validate_evidence,
)
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

# Phase 1, Step 2, Phase 2, Step 2 & Phase 3, Step 2: Re-export extracted symbols using explicit redundant aliases
__all__ = [
    "MAX_CITATION_SPAN_CHARS",
    "MIN_ENTROPY_GATE_CHARS",
    "MIN_MULTI_SEGMENT_FLOOR_CHARS",
    "AnchorValidationService",
    "calculate_fuzzy_score",
    "is_lexically_valid",
    "normalize_text_with_mapping",
    "process_atom_evaluation",
    "strict_match",
    "validate_evidence",
]


class AnchorValidationService:
    """TDD-testable service for deterministic evidence anchoring using strict substring matching.

    Enforces a strict Fail-Fast architecture. If lexical validation fails,
    a SemanticEvidenceError is raised immediately to eliminate fabricated quote
    hallucinations and enforce physical citation provenance.
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
        # Phase 3, Step 2: Delegate to extracted forensic evidence validator
        return validate_evidence(
            pdf_text=pdf_text,
            exact_quotes=exact_quotes,
            reasoning_trace=reasoning_trace,
            syntactic_anchors=syntactic_anchors,
            contextual_override=contextual_override,
            locale=locale,
            strictness_level=strictness_level,
            target_speaker=target_speaker,
            lexical_strictness_level=lexical_strictness_level,
        )

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
        # Phase 3, Step 2: Delegate to extracted atom evaluation processor
        return process_atom_evaluation(
            atom=atom,
            alias_map=alias_map,
            source_documents=source_documents,
            mcp_source_texts=mcp_source_texts,
            locale=locale,
            strictness_level=strictness_level,
            lexical_strictness_level=lexical_strictness_level,
        )
