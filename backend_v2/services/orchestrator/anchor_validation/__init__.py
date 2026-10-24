"""Canonical package facade for AnchorValidationService and forensic quote verification."""

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
    """Stateless package facade for deterministic evidence anchoring and quote verification.

    Attributes:
        MAX_CITATION_SPAN_CHARS: Maximum character span permitted across a citation chain.
        MIN_MULTI_SEGMENT_FLOOR_CHARS: Minimum character length required per segment in multi-segment citations.
        MIN_ENTROPY_GATE_CHARS: Minimum character length required before fuzzy matching is permitted.
    """

    MAX_CITATION_SPAN_CHARS: int = MAX_CITATION_SPAN_CHARS
    MIN_MULTI_SEGMENT_FLOOR_CHARS: int = MIN_MULTI_SEGMENT_FLOOR_CHARS
    MIN_ENTROPY_GATE_CHARS: int = MIN_ENTROPY_GATE_CHARS

    @staticmethod
    def normalize_text_with_mapping(text: str) -> tuple[str, list[int]]:
        """Normalize text and return a mapping from normalized index to original index.

        Args:
            text: Source text string to normalize.

        Returns:
            Tuple containing the normalized string and a list mapping each normalized
            character index to its original character index in text.
        """
        return normalize_text_with_mapping(text)

    @staticmethod
    def strict_match(
        pdf_text: str,
        exact_quotes: Sequence[str] | tuple[str, ...] | list[str],
    ) -> GateMatchResultDTO:
        """Execute O(N) anchoring using strict substring matching.

        Args:
            pdf_text: Source text context.
            exact_quotes: Ordered sequence of extracted quote segments.

        Returns:
            GateMatchResultDTO indicating match validity and normalized coordinate bounds.
        """
        return strict_match(pdf_text, exact_quotes)

    @staticmethod
    def calculate_fuzzy_score(norm_quote: str, norm_text: str) -> float:
        """Choose fuzzy algorithm based on length of the normalized quote.

        Args:
            norm_quote: Normalized quote string.
            norm_text: Normalized source text context.

        Returns:
            Fuzzy similarity score from 0.0 to 100.0.
        """
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
        """Determine if a quote or multi-segment quote is lexically valid against normalized text.

        Args:
            quote: Exact quote string or ordered sequence of quote segments.
            norm_quote: Normalized quote string or sequence of normalized quote segments.
            norm_text: Normalized source text context.
            strictness_level: Validation strictness level constraint.
            locale: Optional locale identifier.
            source_text: Optional original source text prior to normalization for word-boundary stemming.
            lexical_strictness_level: Sovereign workflow lexical strictness level (0-100 continuous).

        Returns:
            GateMatchResultDTO indicating match validity and normalized coordinate bounds.
        """
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
        """Validate evidence strictly and extract the exact physical string segments.

        Args:
            pdf_text: Source text context.
            exact_quotes: Ordered quote segments extracted by the LLM.
            reasoning_trace: Optional trace containing the LLM logical breakdown.
            syntactic_anchors: Optional list of syntactic anchors to locate.
            contextual_override: Whether cognitive override is active to skip lexical validation.
            locale: Optional locale identifier to resolve the fuzzy fallback threshold.
            strictness_level: Strictness tolerance boundary percentage.
            target_speaker: Target speaker stream for conversational dialogue provenance.
            lexical_strictness_level: Sovereign workflow lexical strictness level (0-100 continuous).

        Returns:
            Tuple of extracted physical quote substrings if valid, or None if overridden.

        Raises:
            SemanticEvidenceError: If lexical validation, provenance boundary isolation,
                monotonic ordering, span ceiling, or reasoning trace consistency fails
                (ErrorCodes.AGENT_LOGICAL_VALIDATION_FAILED).
        """
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

        Args:
            atom: AtomResultDTO instance to process.
            alias_map: Mapping of short aliases to canonical document IDs.
            source_documents: Optional list of static source document contexts.
            mcp_source_texts: Optional dictionary of MCP-provided source texts.
            locale: Optional locale identifier.
            strictness_level: Strictness tier (0-100).
            lexical_strictness_level: Sovereign workflow lexical strictness level (0-100 continuous).

        Returns:
            New AtomResultDTO instance with hydrated evaluation_reasoning and validated source_quotes.
        """
        return process_atom_evaluation(
            atom=atom,
            alias_map=alias_map,
            source_documents=source_documents,
            mcp_source_texts=mcp_source_texts,
            locale=locale,
            strictness_level=strictness_level,
            lexical_strictness_level=lexical_strictness_level,
        )
