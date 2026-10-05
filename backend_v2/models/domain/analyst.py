"""Analyst Agent Domain Models.

This module contains the schemas for the Analyst Agent, including hypotheses and search results.
"""

from __future__ import annotations

import logging
from typing import Annotated, Self

from pydantic import ConfigDict, Field, model_validator

from backend_v2.exceptions import ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO
from backend_v2.models.domain.integrity import CitationAudit
from backend_v2.models.dtos.inputs import IngressInputValue

logger = logging.getLogger(__name__)

__all__ = [
    "AnalystDTO",
    "AnalystInput",
    "AnalystOutput",
    "Hypothesis",
    "SearchResult",
    "SearchResultItem",
]


class AnalystInput(V2CoreBase):
    """Strict input schema for AnalystAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are encapsulated dynamically.

    Attributes:
        chat_log: Mandatory chatlog to analyze.
        last_reasoning_trace: Previous reasoning trace.
        dynamic_inputs: Structured dictionary for dynamic inputs.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    chat_log: Annotated[str, Field(description="Mandatory chatlog to analyze.")]
    last_reasoning_trace: Annotated[str | None, Field(description="Previous reasoning trace.")] = None

    dynamic_inputs: Annotated[
        dict[str, IngressInputValue],
        Field(default_factory=dict, description="Structured dictionary for dynamic inputs."),
    ]


class Hypothesis(V2CoreBase):
    """A single hypothesis formed by the Analyst.

    Attributes:
        id: Hypothesis ID.
        claim_text: The claim text.
        evidence_found: Was evidence found?
        search_query: Search query used.
        quotes: Direct quotes found.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    id: Annotated[str, Field(pattern=r"^hyp_[a-zA-Z0-9]+$", min_length=1, description="Hypothesis ID.")]
    claim_text: Annotated[
        str,
        Field(min_length=1, description="The claim text.", json_schema_extra={"x-ui-label": "Claim"}),
    ]
    evidence_found: Annotated[
        bool,
        Field(description="Was evidence found?", json_schema_extra={"x-ui-label": "Evidence Found"}),
    ]
    search_query: Annotated[
        str,
        Field(min_length=1, description="Search query used.", json_schema_extra={"x-ui-label": "Search Query"}),
    ]
    quotes: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="Direct quotes found.",
            json_schema_extra={"x-ui-label": "Quotes"},
        ),
    ]

    @model_validator(mode="after")
    def validate_consistency(self) -> Self:
        """Validate consistency of evidence and quotes.

        Returns:
            The validated Hypothesis instance.

        Raises:
            ValueError: If evidence_found is True but quotes are missing.
        """
        if self.evidence_found and not self.quotes:
            # Strict: If evidence is found, quotes MUST be provided.
            # This prevents "hallucinated" evidence flags without backing data.
            msg = "Hypothesis claims evidence_found=True but provides no quotes."
            logger.error("[AnalystModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg, exc_info=True)
            raise ValueError(msg)
        return self


class AnalystDTO(ReasoningTraceDTO):
    """Analyst DTO (Content Only).

    Attributes:
        hypotheses: List of hypotheses.
        rag_evidence: RAG evidence snippets.
        critical_violation: Critical violation of Knowledge Base?
        integrity_audit: Integrity audit results for citations.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    hypotheses: Annotated[
        list[Hypothesis],
        Field(min_length=1, description="List of hypotheses.", json_schema_extra={"x-ui-label": "Hypotheses"}),
    ]
    rag_evidence: Annotated[
        list[str],
        Field(
            default_factory=list,
            description="RAG evidence snippets.",
            json_schema_extra={"x-ui-label": "RAG Evidence"},
        ),
    ]
    critical_violation: Annotated[
        bool,
        Field(
            description="Critical violation of Knowledge Base?", json_schema_extra={"x-ui-label": "Critical Violation"}
        ),
    ] = False
    integrity_audit: Annotated[
        CitationAudit | None,
        Field(
            description="Integrity audit results for citations.", json_schema_extra={"x-ui-label": "Integrity Audit"}
        ),
    ] = None


class AnalystOutput(AnalystDTO, ReasoningTrace):
    """Output schema for the Analyst Agent."""

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class SearchResultItem(V2CoreBase):
    """Single search result.

    Attributes:
        title: Title of the result.
        link: Link to the result.
        snippet: Snippet of the result.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    title: Annotated[
        str,
        Field(min_length=1, description="Title of the result.", json_schema_extra={"x-ui-label": "Title"}),
    ]
    link: Annotated[
        str,
        Field(min_length=1, description="Link to the result.", json_schema_extra={"x-ui-label": "Link"}),
    ]
    snippet: Annotated[
        str,
        Field(min_length=1, description="Snippet of the result.", json_schema_extra={"x-ui-label": "Snippet"}),
    ]


class SearchResult(V2CoreBase):
    """Result of the Google Search (Hook).

    Attributes:
        results: Search results.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    results: Annotated[
        list[SearchResultItem],
        Field(min_length=1, description="Search results.", json_schema_extra={"x-ui-label": "Search Results"}),
    ]
