"""Integrity Domain Models.

Provides strict Pydantic V2 validation schemas for the integrity hooks
to eliminate legacy dictionary-based parsing and enforce Zero-Compromise protocols.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeItem(BaseModel):
    """Knowledge item structure."""

    term: str
    definition: str
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class StepContext(BaseModel):
    """Step context structure."""

    precedents: str | None = None
    knowledge_items: list[KnowledgeItem] = Field(default_factory=list)
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class CitationAudit(BaseModel):
    """Audit result for citation integrity."""

    valid_citations: int = Field(default=0, description="Count of valid, verified citations.")
    invalid_citations: list[str] = Field(
        default_factory=list, description="List of hallucinations (citations not found in text)."
    )
    integrity_score: float = Field(default=1.0, description="Ratio of valid citations (0.0 - 1.0).")
    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class IntegrityGlobalInputsDTO(BaseModel):
    """Strict schema to safely extract nested source texts from global context vars
    without using hasattr() or isinstance().
    """

    raw_inputs: dict[str, Any] | None = Field(default=None)
    model_config = ConfigDict(frozen=True, extra="allow")

    def extract_source_texts(self) -> list[str]:
        """Extracts source text securely from strictly parsed properties."""
        texts = []
        if self.raw_inputs:
            for v in self.raw_inputs.values():
                if v:
                    texts.append(str(v))
        elif self.model_extra:
            for v in self.model_extra.values():
                if v:
                    texts.append(str(v))
        return texts
