"""Integrity Domain Models.

Provides strict Pydantic V2 validation schemas for the integrity hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Any

from pydantic import Field

from backend_v2.models.core_base import V2CoreBase


class KnowledgeItem(V2CoreBase):
    """Knowledge item structure."""

    term: str
    definition: str


class StepContext(V2CoreBase):
    """Step context structure."""

    precedents: str | None = None
    knowledge_items: list[KnowledgeItem] = Field(default_factory=list)


class CitationAudit(V2CoreBase):
    """Audit result for citation integrity."""

    valid_citations: int = Field(default=0, description="Count of valid, verified citations.")
    invalid_citations: list[str] = Field(
        default_factory=list, description="List of hallucinations (citations not found in text)."
    )
    integrity_score: float = Field(default=1.0, description="Ratio of valid citations (0.0 - 1.0).")


class IntegrityGlobalInputsDTO(V2CoreBase):
    """Strict schema to safely extract nested source texts from global context vars.

    Enforces Zero-Compromise Pydantic V2 schema without duck-typing.
    """

    raw_inputs: dict[str, Any] | None = Field(default=None)

    def extract_source_texts(self) -> list[str]:
        """Extracts source text securely from strictly parsed properties."""
        texts = []
        if self.raw_inputs:
            for v in self.raw_inputs.values():
                if v:
                    texts.append(str(v))
        return texts
