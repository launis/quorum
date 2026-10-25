"""MCP Models.

This module defines the standardized request and response structures for interacting
with Model Context Protocol (MCP) tool loops.
"""

from typing import Annotated, Any

from pydantic import ConfigDict, Field, JsonValue, field_validator

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.system_config import MCPAuditTrace
from backend_v2.models.domain.usage import TokenUsage
from backend_v2.models.dtos.mcp import MCPArgumentValue


class OpenAIFunctionCallDTO(V2CoreBase):
    """Schema for a function call in an OpenAI tool call.

    Attributes:
        name: Function name.
        arguments: Function arguments as a string or typed argument mapping.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    name: Annotated[str, Field(description="Function name.")]
    arguments: Annotated[
        str | dict[str, MCPArgumentValue],
        Field(description="Function arguments as a JSON string or typed argument dictionary."),
    ]


class OpenAIToolCallDTO(V2CoreBase):
    """Schema for an OpenAI tool call.

    Attributes:
        index: Call index.
        id: Tool call ID.
        type: Call type, defaults to 'function'.
        function: The function call payload.
        provider_specific_fields: Optional provider-specific fields.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    index: Annotated[int | None, Field(default=None, description="Call index.")] = None
    id: Annotated[str, Field(description="Tool call ID.")]
    type: Annotated[str, Field(default="function", description="Call type.")] = "function"
    function: Annotated[OpenAIFunctionCallDTO, Field(description="The function call payload.")]
    provider_specific_fields: Annotated[
        dict[str, JsonValue] | None,
        Field(default=None, description="Optional provider-specific metadata."),
    ] = None


class OpenAIProbeResponseDTO(V2CoreBase):
    """Schema for parsing the LLM response during the Tool Loop Phase 1 probe.

    Attributes:
        tool_calls: Optional list of tool calls requested by the LLM.
        content: Optional conversational response from the LLM.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    tool_calls: Annotated[
        list[OpenAIToolCallDTO] | None,
        Field(default=None, description="Optional list of tool calls requested by the LLM."),
    ] = None
    content: Annotated[
        str | None,
        Field(default=None, description="Optional conversational response from the LLM."),
    ] = None


class TavilyToolArgsDTO(V2CoreBase):
    """Arguments for a Tavily tool call.

    Attributes:
        query: The search query.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    query: Annotated[str, Field(description="The search query.")]


class MCPToolLoopResult(V2CoreBase):
    """Result from the Tool Loop — structured output + audit trail.

    Attributes:
        result_data: Final structured output dict.
        audit_traces: Audit log of all tool invocations.
        usage: Cumulative token usage.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    result_data: Annotated[dict[str, JsonValue], Field(description="Final structured output dict.")]
    audit_traces: list[MCPAuditTrace] = Field(default_factory=list, description="Audit log of all tool invocations.")
    usage: TokenUsage = Field(
        default_factory=lambda: TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        description="Cumulative token usage.",
    )


class MCPRetrievalResultDTO(V2CoreBase):
    """Result of an MCP retrieval phase.

    Attributes:
        audit_traces: Audit log of all tool invocations during retrieval.
        usage: Token usage incurred during retrieval.
        evidence_payload: Assembled evidence text formatted for prompt inclusion.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    audit_traces: list[MCPAuditTrace] = Field(
        default_factory=list, description="Audit log of all tool invocations during retrieval."
    )
    usage: TokenUsage = Field(
        default_factory=lambda: TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        description="Token usage incurred during retrieval.",
    )
    evidence_payload: Annotated[
        str,
        Field(default="", description="Assembled evidence text formatted for prompt inclusion."),
    ] = ""


class MCPSynthesisInstructionsDTO(V2CoreBase):
    """Execution parameters injected into the tool loop for formatting/synthesis constraints.

    Attributes:
        synthesis_preamble: Optional text prepended to synthesis.
        synthesis_length_limit: Optional length limit for synthesis.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    synthesis_preamble: Annotated[
        str | None,
        Field(default=None, description="Optional text prepended to synthesis."),
    ] = None
    synthesis_length_limit: Annotated[
        int | None,
        Field(default=None, description="Optional length limit for synthesis."),
    ] = None


class TavilyApiResultItemDTO(V2CoreBase):
    """A single search result item from Tavily API.

    Attributes:
        id: Unique identifier for the search result, if provided.
        title: Title of the search result.
        url: URL of the search result.
        content: Search result content.
        raw_content: Unprocessed raw content, if available.
        score: Relevance score.
        published_date: Published date, if available.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    id: Annotated[str | None, Field(default=None, description="Unique identifier for the search result.")] = None
    title: Annotated[str, Field(default="", description="Title of the search result.")] = ""
    url: Annotated[str, Field(default="", description="URL of the search result.")] = ""
    content: Annotated[str, Field(default="", description="Search result content.")] = ""
    raw_content: Annotated[str | None, Field(default=None, description="Unprocessed raw content.")] = None
    score: Annotated[float, Field(default=0.0, description="Relevance score.")] = 0.0
    published_date: Annotated[str | None, Field(default=None, description="Published date.")] = None


class TavilyApiResponseDTO(V2CoreBase):
    """Complete response payload from Tavily API.

    Attributes:
        query: The original search query.
        answer: AI-generated answer, if requested.
        response_time: Response time in seconds.
        images: List of related images.
        results: Search results list from Tavily.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    query: Annotated[str, Field(default="", description="The original search query.")] = ""
    answer: Annotated[str | None, Field(default="", description="AI-generated answer.")] = ""
    response_time: Annotated[float, Field(default=0.0, description="Response time in seconds.")] = 0.0
    images: list[str] = Field(default_factory=list, description="List of related images.")
    results: Annotated[list[TavilyApiResultItemDTO], Field(description="Search results list from Tavily.")]
    follow_up_questions: Annotated[list[str] | None, Field(default=None, description="Follow-up questions.")] = None
    request_id: Annotated[str | None, Field(default=None, description="Request ID.")] = None


class TavilySearchResult(V2CoreBase):
    """Parsed Tavily response for downstream consumption.

    Attributes:
        query: Echo of the original search query.
        answer: AI-generated summary from Tavily.
        source_urls: Deduplicated source URLs.
        raw_content: Concatenated source texts (truncated).
        duration_ms: Round-trip latency in milliseconds.
    """

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    query: Annotated[str, Field(description="Echo of the original search query.")]
    answer: Annotated[str, Field(description="AI-generated summary from Tavily.")] = ""
    source_urls: list[str] = Field(default_factory=list, description="Deduplicated source URLs.")
    raw_content: Annotated[str, Field(description="Concatenated source texts (truncated).")] = ""
    duration_ms: Annotated[int, Field(description="Round-trip latency in milliseconds.")] = 0


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

    claim_text: Annotated[str, Field(description="Exact quote of the claim from the text.")]
    search_query: Annotated[
        str,
        Field(
            description=(
                "Concise entity or topic keywords (1-3 key terms, specifically: proper nouns, organization names, or "
                "core subject concepts) for tool verification."
            )
        ),
    ]
    knowledge_gap: Annotated[str, Field(description="The specific knowledge gap needing resolution.")] = ""
    search_rationale: Annotated[str, Field(description="The rationale mapping the query to the knowledge gap.")] = ""
    reasoning: Annotated[
        str,
        Field(max_length=400, description="Max 1-2 short sentences. Briefly explain WHY you are verifying this claim."),
    ]

    @field_validator("reasoning", mode="before")
    @classmethod
    def truncate_reasoning(cls, v: Any) -> Any:
        if isinstance(v, str) and len(v) > 400:
            truncated = v[:397]
            last_period = truncated.rfind(".")
            if last_period > 50:  # Truncate at period if positioned reasonably
                return truncated[: last_period + 1]
            return truncated + "..."
        return v


class CitationExtractionResult(V2CoreBase):
    """Result of Phase 0 extraction from source document.

    Attributes:
        citations: List of extracted claims to verify.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    citations: Annotated[list[CitationExtractionItemDTO], Field(description="List of extracted claims to verify.")]


class CitationCorrectionResult(V2CoreBase):
    """Result of the citation self-correction LLM task.

    Attributes:
        corrected_claim: The verbatim corrected claim text found in the source context.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    corrected_claim: Annotated[str, Field(description="The verbatim corrected claim text found in the source context.")]


class CitationExtractionFailure(V2CoreBase):
    """Ensemble citation extraction worker failure.

    Attributes:
        error_message: Error message from failed ensemble run.
    """

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")

    error_message: Annotated[str, Field(description="Error message from failed ensemble run.")]
