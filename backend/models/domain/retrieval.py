"""Retrieval Agent Domain Models.

This module contains the schemas for the Retrieval Agent (RAG),
including Precedent and ContextData.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend.models.domain.base import ReasoningTrace


class Precedent(BaseModel):
    """A past case/execution retrieved by RetrievalAgent."""
    id: str
    date: str
    scores: str
    verdict: str

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "date", "scores", "verdict")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class KnowledgeItem(BaseModel):
    """A single item retrieved from the Knowledge Base."""
    id: str
    type: str = Field(..., description="concept, reference, or claim")
    term: str
    definition: str
    source: str
    score: float | None = Field(None, description="Relevance score (if available)")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("id", "type", "term", "definition", "source")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class ContextData(BaseModel):
    """Output schema for the Retrieval Agent."""
    precedents: str = Field(..., description="Summary text of precedents.")
    precedent_list: list[Precedent] = Field(default_factory=list, description="Structured list of precedents.")
    knowledge_items: list[KnowledgeItem] = Field(default_factory=list, description="Structured list of knowledge items.", json_schema_extra={"reader_mode": "hidden"})
    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("precedents")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        # Precedents summary might be legitimately empty if nothing found?
        # But schema says ... (required).
        # Let's enforce non-empty if it's a required field describing retrieval.
        if not v or not v.strip():
             # If retrieval found nothing, it should probably say "No precedents found."
             raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()
