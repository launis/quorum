"""Analyst Agent Domain Models.

This module contains the schemas for the Analyst Agent, including hypotheses and search results.
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO


class AnalystInput(BaseModel):
    """Strict input schema for AnalystAgent."""

    history_text: str = Field(..., description="Chat history to analyze.")
    product_text: str | None = Field(None, description="Product context (optional).")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    model_config = ConfigDict(frozen=True, extra="ignore")


class Hypothesis(BaseModel):
    """A single hypothesis formed by the Analyst."""

    id: str = Field(..., description="Hypothesis ID.")
    claim_text: str = Field(
        ...,
        description="The claim text.",
        json_schema_extra={"x-ui-label": "Claim"},
    )
    evidence_found: bool = Field(
        ...,
        description="Was evidence found?",
        json_schema_extra={"x-ui-label": "Evidence Found"},
    )
    search_query: str = Field(
        ...,
        description="Search query used.",
        json_schema_extra={"x-ui-label": "Search Query"},
    )
    quotes: list[str] = Field(
        default_factory=list,
        description="Direct quotes found.",
        json_schema_extra={"x-ui-label": "Quotes"},
    )
    model_config = ConfigDict(frozen=True, strict=False)

    @field_validator("id", "claim_text", "search_query")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()

    @model_validator(mode="after")
    def validate_consistency(self) -> Hypothesis:
        if self.evidence_found and not self.quotes:
            # Strict: If evidence is found, quotes MUST be provided.
            # This prevents "hallucinated" evidence flags without backing data.
            raise ValueError("Hypothesis claims evidence_found=True but provides no quotes.")
        return self


class AnalystDTO(ReasoningTraceDTO):
    """Analyst DTO (Content Only)."""

    hypotheses: list[Hypothesis] = Field(
        ...,
        description="List of hypotheses.",
        json_schema_extra={"x-ui-label": "Hypotheses"},
    )
    rag_evidence: list[str] = Field(
        default_factory=list,
        description="RAG evidence snippets.",
        json_schema_extra={"x-ui-label": "RAG Evidence"},
    )
    critical_violation: bool = Field(
        default=False,
        description="Critical violation of Knowledge Base?",
        json_schema_extra={"x-ui-label": "Critical Violation"},
    )
    model_config = ConfigDict(frozen=True, strict=False)

    @field_validator("hypotheses")
    @classmethod
    def validate_hypotheses_not_empty(cls, v: list[Hypothesis]) -> list[Hypothesis]:
        if not v:
            raise ValueError("Analyst output must contain at least one hypothesis.")
        return v


class AnalystOutput(AnalystDTO, ReasoningTrace):
    """Output schema for the Analyst Agent."""

    model_config = ConfigDict(frozen=True, strict=False)


class SearchResultItem(BaseModel):
    """Single search result."""

    title: str = Field(..., description="Title of the result.", json_schema_extra={"x-ui-label": "Title"})
    link: str = Field(..., description="Link to the result.", json_schema_extra={"x-ui-label": "Link"})
    snippet: str = Field(..., description="Snippet of the result.", json_schema_extra={"x-ui-label": "Snippet"})

    model_config = ConfigDict(frozen=True, strict=False)

    @field_validator("title", "link", "snippet")
    @classmethod
    def validate_non_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only.")
        return v.strip()


class SearchResult(BaseModel):
    """Result of the Google Search (Hook)."""

    results: list[SearchResultItem] = Field(
        default_factory=list, description="Search results.", json_schema_extra={"x-ui-label": "Search Results"}
    )
    error: str | None = Field(
        default=None, description="Error message if search failed.", json_schema_extra={"x-ui-label": "Error"}
    )

    model_config = ConfigDict(frozen=True, strict=False)
