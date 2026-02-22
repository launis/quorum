"""Knowledge Base Domain Models.

This module defines the strict Pydantic models for knowledge base artifacts
parsed from external files (DOCX, MD, etc.).
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DocumentChunk(BaseModel):
    """Strict model for a single chunk of a knowledge base document."""

    chunk_id: str = Field(..., description="Unique identifier for the chunk.")
    content: str = Field(..., description="Text content of the chunk.")
    page_number: int | None = Field(default=None, description="Page number/Position (if applicable).")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Chunk-specific metadata.")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("chunk_id", "content")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class Concept(BaseModel):
    """Strict model for an extracted Concept."""

    term: str
    definition: str

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("term", "definition")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class Reference(BaseModel):
    """Strict model for a Bibliographic Reference."""

    citation: str
    short_citation: str | None = None
    doi_link: str | None = None
    anchor_id: str | None = None

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("citation")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class Claim(BaseModel):
    """Strict model for an extracted Claim/Statement."""

    claim_text: str
    citation_keys: list[str] = Field(default_factory=list)
    citation_text: str | None = None
    original_markdown: str | None = None
    matches_text_citation: bool = False
    concept_context: str | None = None

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("claim_text")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class KnowledgeBaseDocument(BaseModel):
    """Strict model for a parsed Knowledge Base document."""

    document_id: str = Field(..., description="Unique identifier for the document.")
    filename: str = Field(..., description="Original filename.")
    content_type: str = Field(..., description="MIME type or extension (e.g. 'application/pdf').")
    total_tokens: int = Field(..., description="Total token count estimate.")

    # Raw Content Chunks
    chunks: list[DocumentChunk] = Field(default_factory=list, description="List of document chunks.")

    # Extracted Knowledge
    concepts: list[Concept] = Field(default_factory=list, description="Extracted terminology.")
    references: list[Reference] = Field(default_factory=list, description="Bibliographic references.")
    claims: list[Claim] = Field(default_factory=list, description="Extracted claims.")

    parsed_at: datetime = Field(..., description="Timestamp of parsing.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Document-level metadata.")

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("document_id", "filename", "content_type")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @field_validator("total_tokens")
    @classmethod
    def validate_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("Token count cannot be negative.")
        return v
