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
