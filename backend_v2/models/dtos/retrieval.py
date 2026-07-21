"""Retrieval Data Transfer Objects.

Defines schemas for batch execution and retrieval orchestration.
"""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.enums import LaxSearchStatus


class BatchSearchQueryDTO(V2CoreBase):
    """DTO for receiving a batch of search queries from LLM structured extraction.

    Ensures strict validation when extracting queries for concurrent execution.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    queries: Annotated[list[str], Field(description="List of exact search queries to execute in parallel")]


class TavilySearchResultDTO(V2CoreBase):
    """DTO representing a single search result with DLQ status tracking.

    Used to return resilient results back to the Fact Checker, even if
    transient errors cause individual searches to fail.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    query: Annotated[str, Field(description="The original search query")]
    answer: Annotated[str, Field(description="The summarized answer from Tavily")]
    source_urls: Annotated[list[str], Field(description="List of source URLs")]
    raw_content: Annotated[str, Field(description="Concatenated raw snippet content")]
    duration_ms: Annotated[int, Field(description="Duration of the search in milliseconds")]
    status: Annotated[LaxSearchStatus, Field(description="DLQ tracking status")]
