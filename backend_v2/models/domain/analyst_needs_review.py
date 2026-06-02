"""Analyst Agent Domain Models.

This module contains the schemas for the Analyst Agent, including hypotheses and search results.
"""

import logging
from typing import Any

from pydantic import Field, model_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.integrity import CitationAudit

logger = logging.getLogger(__name__)


class AnalystInput(V2CoreBase):
    """Strict input schema for AnalystAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are encapsulated dynamically.
    """

    chat_log: str = Field(..., description="Mandatory chatlog to analyze.")
    last_reasoning_trace: str | None = Field(default=None, description="Previous reasoning trace.")

    dynamic_inputs: dict[str, Any] = Field(
        default_factory=dict, description="Structured dictionary for dynamic inputs."
    )


class Hypothesis(V2CoreBase):
    """A single hypothesis formed by the Analyst."""

    id: str = Field(..., pattern=r"^hyp_[a-zA-Z0-9]+$", min_length=1, description="Hypothesis ID.")
    claim_text: str = Field(
        ...,
        min_length=1,
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
        min_length=1,
        description="Search query used.",
        json_schema_extra={"x-ui-label": "Search Query"},
    )
    quotes: list[str] = Field(
        default_factory=list,
        description="Direct quotes found.",
        json_schema_extra={"x-ui-label": "Quotes"},
    )

    @model_validator(mode="after")
    def validate_consistency(self) -> Hypothesis:
        if self.evidence_found and not self.quotes:
            # Strict: If evidence is found, quotes MUST be provided.
            # This prevents "hallucinated" evidence flags without backing data.
            msg = "Hypothesis claims evidence_found=True but provides no quotes."
            logger.error("[AnalystModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise ValueError(msg)
        return self


class AnalystDTO(ReasoningTraceDTO):
    """Analyst DTO (Content Only)."""

    hypotheses: list[Hypothesis] = Field(
        ...,
        min_length=1,
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
    integrity_audit: CitationAudit | None = Field(
        default=None,
        description="Integrity audit results for citations.",
        json_schema_extra={"x-ui-label": "Integrity Audit"},
    )


class AnalystOutput(AnalystDTO, ReasoningTrace):
    """Output schema for the Analyst Agent."""


class SearchResultItem(V2CoreBase):
    """Single search result."""

    title: str = Field(
        ...,
        min_length=1,
        description="Title of the result.",
        json_schema_extra={"x-ui-label": "Title"},
    )
    link: str = Field(
        ...,
        min_length=1,
        description="Link to the result.",
        json_schema_extra={"x-ui-label": "Link"},
    )
    snippet: str = Field(
        ...,
        min_length=1,
        description="Snippet of the result.",
        json_schema_extra={"x-ui-label": "Snippet"},
    )


class SearchResult(V2CoreBase):
    """Result of the Google Search (Hook)."""

    results: list[SearchResultItem] = Field(
        ..., min_length=1, description="Search results.", json_schema_extra={"x-ui-label": "Search Results"}
    )
