"""Integrity Domain Models.

Provides strict Pydantic V2 validation schemas for the integrity hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field, ValidationInfo, field_validator

from backend_v2.models.core_base import V2CoreBase


class KnowledgeItem(V2CoreBase):
    """Knowledge item structure representing term definitions.

    Attributes:
        term: The specific vocabulary term.
        definition: The corresponding validation reference explanation.
    """

    term: str = Field(..., description="The specific vocabulary term.")
    definition: str = Field(..., description="The corresponding validation reference explanation.")


class StepContext(V2CoreBase):
    """Step context structure containing prior precedent data and knowledge items.

    Attributes:
        precedents: Textual reference representation of predecessor steps.
        knowledge_items: Collection of related domain-specific knowledge assertions.
    """

    precedents: str | None = Field(default=None, description="Textual reference representation of predecessor steps.")
    knowledge_items: list[KnowledgeItem] = Field(
        default_factory=list, description="Collection of related domain-specific knowledge assertions."
    )


class CitationAudit(V2CoreBase):
    """Audit result for citation integrity metrics.

    Attributes:
        valid_citations: Count of valid, verified citations found within target sources.
        invalid_citations: List of identified hallucinated citations.
        integrity_score: Ratio of verified to total citations (0.0 to 1.0).
    """

    valid_citations: int = Field(default=0, description="Count of valid, verified citations.")
    invalid_citations: list[str] = Field(
        default_factory=list, description="List of hallucinations (citations not found in text)."
    )
    integrity_score: float = Field(default=1.0, description="Ratio of valid citations (0.0 - 1.0).")

    @field_validator("integrity_score")
    @classmethod
    def validate_integrity_score_bounds(cls, v: float, info: ValidationInfo) -> float:
        """Validates that the integrity score is bounds-compliant (0.0 to 1.0).

        Args:
            v: The computed integrity score ratio to validate.
            info: Pydantic validation context.

        Returns:
            The validated integrity score.

        Raises:
            ValueError: Raised if the score falls outside the safe mathematical range [0.0, 1.0].
        """
        if not (0.0 <= v <= 1.0):
            raise ValueError("integrity_score must be between 0.0 and 1.0 inclusive")
        return v


class IntegrityGlobalInputsDTO(V2CoreBase):
    """Strict schema to safely extract nested source texts from global context vars.

    Enforces Zero-Compromise Pydantic V2 schema without duck-typing.

    Attributes:
        raw_inputs: Unstructured input envelope at database boundaries.
    """

    raw_inputs: dict[str, Any] | None = Field(
        default=None, description="Unstructured input envelope at database boundaries."
    )

    def extract_source_texts(self) -> list[str]:
        """Extracts source text securely from strictly parsed properties.

        Returns:
            A list of securely extracted and string-formatted input texts.
        """
        texts: list[str] = []
        if self.raw_inputs:
            for v in self.raw_inputs.values():
                if v is not None:
                    texts.append(str(v))
        return texts
