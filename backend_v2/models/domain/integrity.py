"""Integrity Domain Models.

Provides strict Pydantic V2 validation schemas for the integrity hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any

from pydantic import ConfigDict, Field, ValidationInfo, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase

logger = logging.getLogger(__name__)


class KnowledgeItem(V2CoreBase):
    """Knowledge item structure representing term definitions.

    Attributes:
        term: The specific vocabulary term.
        definition: The corresponding validation reference explanation.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    term: Annotated[str, Field(description="The specific vocabulary term.")]
    definition: Annotated[str, Field(description="The corresponding validation reference explanation.")]


class StepContext(V2CoreBase):
    """Step context structure containing prior precedent data and knowledge items.

    Attributes:
        precedents: Textual reference representation of predecessor steps.
        knowledge_items: Collection of related domain-specific knowledge assertions.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    precedents: Annotated[str | None, Field(description="Textual reference representation of predecessor steps.")] = (
        None
    )
    knowledge_items: Annotated[
        list[KnowledgeItem],
        Field(default_factory=list, description="Collection of related domain-specific knowledge assertions."),
    ]


class CitationAudit(V2CoreBase):
    """Audit result for citation integrity metrics.

    Attributes:
        valid_citations: Count of valid, verified citations found within target sources.
        invalid_citations: List of identified hallucinated citations.
        integrity_score: Ratio of verified to total citations (0.0 to 1.0).
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    valid_citations: Annotated[int, Field(description="Count of valid, verified citations.")] = 0
    invalid_citations: Annotated[
        list[str], Field(default_factory=list, description="List of hallucinations (citations not found in text).")
    ]
    integrity_score: Annotated[float, Field(description="Ratio of valid citations (0.0 - 1.0).")] = 1.0

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
            AppException: Raised if the score falls outside the safe mathematical range [0.0, 1.0].
        """
        if not (0.0 <= v <= 1.0):
            msg = "integrity_score must be between 0.0 and 1.0 inclusive"
            logger.error("[CitationAudit] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class IntegrityGlobalInputsDTO(V2CoreBase):
    """Strict schema to safely extract nested source texts from global context vars.

    Enforces Zero-Compromise Pydantic V2 schema without duck-typing.

    Attributes:
        raw_inputs: Unstructured input envelope at database boundaries.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    raw_inputs: Annotated[
        dict[str, Any] | None, Field(description="Unstructured input envelope at database boundaries.")
    ] = None

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
