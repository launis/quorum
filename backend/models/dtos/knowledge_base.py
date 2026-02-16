"""Strict DTOs for Knowledge Base content."""

from pydantic import BaseModel, ConfigDict, Field, field_validator

class ReferenceItem(BaseModel):
    """A bibliography reference entry from the Knowledge Base."""
    citation: str | None = None
    short_citation: str
    definition: str | None = None # Legacy support

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("short_citation")
    @classmethod
    def validate_short_citation(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Short citation cannot be empty.")
        return v.strip()

    @property
    def full_text(self) -> str:
        """Return the best available full text representation."""
        return self.citation or self.definition or self.short_citation

class ConceptItem(BaseModel):
    """A defined concept from the Knowledge Base."""
    term: str
    definition: str

    model_config = ConfigDict(frozen=True, strict=True)

    @field_validator("term", "definition")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Term/Definition cannot be empty.")
        return v.strip()

class KnowledgeBaseSchema(BaseModel):
    """Strict schema for the entire Knowledge Base input."""
    references: list[ReferenceItem] = Field(default_factory=list)
    concepts: list[ConceptItem] = Field(default_factory=list)

    model_config = ConfigDict(frozen=True, strict=True)

class CitationReport(BaseModel):
    """Typed output for advanced scanning."""
    # Map of Full Reference String -> List of Contexts/Reasons
    relevance_map: dict[str, list[str]] = Field(default_factory=dict)

    model_config = ConfigDict(frozen=True, strict=True)
