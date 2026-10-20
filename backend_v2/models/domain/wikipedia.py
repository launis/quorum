"""Wikipedia MCP Domain Models and Ingress Intake DTOs.

Defines the Pydantic V2 DTO hierarchy for Wikipedia API communication:
1. External Intake DTOs (sanitized at HTTP boundary before validation)
2. Tool Input DTOs (WikipediaReadInputDTO; search consumes StandardSearchInputDTO)
3. Internal Domain Results (WikipediaSearchResultItem, WikipediaSearchResponseDTO, WikipediaPageSummaryResult)
"""

from __future__ import annotations

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "SUPPORTED_WIKIPEDIA_LANGUAGES",
    "WikimediaActionApiResponseDTO",
    "WikimediaActionQueryDTO",
    "WikimediaActionSearchItemDTO",
    "WikimediaRestSummaryResponseDTO",
    "WikipediaPageSummaryResult",
    "WikipediaReadInputDTO",
    "WikipediaSearchResponseDTO",
    "WikipediaSearchResultItem",
]

# Single Source of Truth for supported Wikipedia subdomains
SUPPORTED_WIKIPEDIA_LANGUAGES: frozenset[str] = frozenset({"fi", "en", "sv", "de"})


# --- External Intake DTOs (sanitized at HTTP ingress boundary before validation) ---
class WikimediaActionSearchItemDTO(BaseModel):
    """Single search match item from Wikimedia Action API query search array."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    ns: int
    title: str
    pageid: int
    size: int | None = None
    wordcount: int | None = None
    snippet: str


class WikimediaActionQueryDTO(BaseModel):
    """Query container inside Wikimedia Action API response."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    search: Annotated[list[WikimediaActionSearchItemDTO], Field(default_factory=list)]


class WikimediaActionApiResponseDTO(BaseModel):
    """Root envelope from Wikimedia Action API (action=query&list=search)."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    query: Annotated[WikimediaActionQueryDTO, Field(default_factory=WikimediaActionQueryDTO)]


class WikimediaRestSummaryResponseDTO(BaseModel):
    """Page summary response from Wikimedia REST API (/page/summary/{title})."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    title: str
    extract: str
    pageid: int | None = None
    description: str | None = None


# --- Tool Input DTOs (Search tools strictly consume StandardSearchInputDTO from tools.py) ---
class WikipediaReadInputDTO(BaseModel):
    """Validated input payload for Wikipedia read summary tool."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, arbitrary_types_allowed=True)

    title: Annotated[str, Field(min_length=1, description="The exact article title to retrieve")]
    target_language: Annotated[str, Field(description="Target language code")] = "en"
    reasoning: Annotated[str, Field(description="Search rationale")] = ""
    step_name: Annotated[str, Field(description="Name of the calling step")] = ""
    claim_text: Annotated[str | None, Field(description="Verbatim claim being verified")] = None
    llm_client: Annotated[Any, Field(description="Optional LLM client for translation")] = None


# --- Internal Domain Results ---
class WikipediaSearchResultItem(BaseModel):
    """Domain model representing a single normalized Wikipedia search hit."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    title: str
    snippet: str
    pageid: int
    url: str


class WikipediaSearchResponseDTO(BaseModel):
    """Domain response container for Wikipedia search execution."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    query: str
    results: list[WikipediaSearchResultItem]
    total_hits: int


class WikipediaPageSummaryResult(BaseModel):
    """Domain model representing an article extract and canonical URL."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    title: str
    extract: str
    pageid: int | None
    url: str
