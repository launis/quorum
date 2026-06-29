"""MCP Models.

This module defines the standardized request and response structures for interacting
with Model Context Protocol (MCP) tool loops.
"""

from typing import Any

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.v2_core import MCPAuditTrace


class OpenAIFunctionCallDTO(V2CoreBase):
    """Schema for a function call in an OpenAI tool call.

    Attributes:
        name: Function name.
        arguments: Function arguments as a string or dict.
    """

    name: str
    arguments: str | dict[str, Any]


class OpenAIToolCallDTO(V2CoreBase):
    """Schema for an OpenAI tool call.

    Attributes:
        index: Call index.
        id: Tool call ID.
        type: Call type, defaults to 'function'.
        function: The function call payload.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="ignore")

    index: int | None = None
    id: str
    type: str = "function"
    function: OpenAIFunctionCallDTO


class OpenAIProbeResponseDTO(V2CoreBase):
    """Schema for parsing the LLM response during the Tool Loop Phase 1 probe.

    Attributes:
        tool_calls: Optional list of tool calls requested by the LLM.
        content: Optional conversational response from the LLM.
    """

    tool_calls: list[OpenAIToolCallDTO] | None = None
    content: str | None = None


class TavilyToolArgsDTO(V2CoreBase):
    """Arguments for a Tavily tool call.

    Attributes:
        query: The search query.
    """

    query: str


class MCPToolLoopResult(V2CoreBase):
    """Result from the Tool Loop — structured output + audit trail.

    Attributes:
        result_data: Final structured output dict.
        audit_traces: Audit log of all tool invocations.
        usage: Cumulative token usage.
    """

    result_data: dict[str, Any] = Field(description="Final structured output dict.")
    audit_traces: list[MCPAuditTrace] = Field(default_factory=list, description="Audit log of all tool invocations.")
    usage: TokenUsage = Field(
        default_factory=lambda: TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        description="Cumulative token usage.",
    )


class MCPSynthesisInstructionsDTO(V2CoreBase):
    """Execution parameters injected into the tool loop for formatting/synthesis constraints.

    Attributes:
        synthesis_preamble: Optional text prepended to synthesis.
        synthesis_length_limit: Optional length limit for synthesis.
    """

    synthesis_preamble: str | None = None
    synthesis_length_limit: int | None = None


class TavilyApiResultItemDTO(V2CoreBase):
    """A single search result item from Tavily API.

    Attributes:
        title: Title of the search result.
        url: URL of the search result.
        content: Search result content.
        raw_content: Unprocessed raw content, if available.
        score: Relevance score.
        published_date: Published date, if available.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="ignore")

    title: str = Field(default="")
    url: str = Field(default="")
    content: str = Field(default="")
    raw_content: str | None = Field(default=None)
    score: float = Field(default=0.0)
    published_date: str | None = Field(default=None)


class TavilyApiResponseDTO(V2CoreBase):
    """Complete response payload from Tavily API.

    Attributes:
        query: The original search query.
        answer: AI-generated answer, if requested.
        response_time: Response time in seconds.
        images: List of related images.
        results: Search results list from Tavily.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="ignore")

    query: str = Field(default="")
    answer: str | None = Field(default="")
    response_time: float = Field(default=0.0)
    images: list[str] = Field(default_factory=list)
    results: list[TavilyApiResultItemDTO] = Field(description="Search results list from Tavily.")


class TavilySearchResult(V2CoreBase):
    """Parsed Tavily response for downstream consumption.

    Attributes:
        query: Echo of the original search query.
        answer: AI-generated summary from Tavily.
        source_urls: Deduplicated source URLs.
        raw_content: Concatenated source texts (truncated).
        duration_ms: Round-trip latency in milliseconds.
    """

    query: str = Field(description="Echo of the original search query.")
    answer: str = Field(default="", description="AI-generated summary from Tavily.")
    source_urls: list[str] = Field(default_factory=list, description="Deduplicated source URLs.")
    raw_content: str = Field(default="", description="Concatenated source texts (truncated).")
    duration_ms: int = Field(default=0, description="Round-trip latency in milliseconds.")


class CitationExtractionItemDTO(V2CoreBase):
    """A single extracted citation claim and its corresponding search query.

    Attributes:
        claim_text: Exact quote of the claim from the text.
        search_query: Optimized search query for the tool to verify the claim.
        knowledge_gap: The specific knowledge gap needing resolution.
        search_rationale: The rationale mapping the query to the knowledge gap.
        reasoning: Max 1 short sentence. Briefly explain WHY you are verifying this claim.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    claim_text: str = Field(description="Exact quote of the claim from the text.")
    search_query: str = Field(description="Optimized search query for the tool to verify the claim.")
    knowledge_gap: str = Field(default="", description="The specific knowledge gap needing resolution.")
    search_rationale: str = Field(default="", description="The rationale mapping the query to the knowledge gap.")
    reasoning: str = Field(
        max_length=150, description="Max 1 short sentence. Briefly explain WHY you are verifying this claim."
    )


class CitationExtractionResult(V2CoreBase):
    """Result of Phase 0 extraction from source document.

    Attributes:
        citations: List of extracted claims to verify.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    citations: list[CitationExtractionItemDTO] = Field(
        default_factory=list, description="List of extracted claims to verify."
    )


class CitationCorrectionResult(V2CoreBase):
    """Result of the citation self-correction LLM task.

    Attributes:
        corrected_claim: The verbatim corrected claim text found in the source context.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    corrected_claim: str = Field(description="The verbatim corrected claim text found in the source context.")
