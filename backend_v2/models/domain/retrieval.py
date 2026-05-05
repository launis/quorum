"""Retrieval Agent Domain Models.

This module contains the schemas for the Retrieval Agent, focusing on facts extracted from sources.
"""

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO


class RetrievalInput(BaseModel):
    """Strict input schema for RetrievalAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.
    """

    chat_log: str = Field(
        ...,
        description="The mandatory conversation history.",
        json_schema_extra={"x-ui-label": "Chatlog"},
        min_length=1,
    )
    product_text: str | None = Field(None, description="Reference text/documents to retrieve from.", min_length=1)

    model_config = ConfigDict(frozen=True, extra="allow")


class RetrievedFact(BaseModel):
    """A single fact extracted from the material."""

    id: str = Field(..., description="Fact ID.", min_length=1)
    fact_statement: str = Field(
        ...,
        description="The retrieved fact.",
        json_schema_extra={"x-ui-label": "Fact Statement"},
        min_length=1,
    )
    source_quote: str = Field(
        ...,
        description="Exact quote from the source material.",
        json_schema_extra={"x-ui-label": "Source Quote"},
        min_length=1,
    )
    relevance_score: int = Field(
        ..., description="Relevance to the objective (1-5).", json_schema_extra={"x-ui-label": "Relevance"}, ge=1, le=5
    )

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class RetrievalDTO(ReasoningTraceDTO):
    """Retrieval DTO (Content Only)."""

    retrieved_facts: list[RetrievedFact] = Field(
        ...,
        description="List of facts retrieved.",
        json_schema_extra={"x-ui-label": "Retrieved Facts"},
        min_length=1,
    )
    key_takeaways: str = Field(
        ...,
        description="High-level summary of the retrieved information.",
        json_schema_extra={"x-ui-label": "Key Takeaways"},
        min_length=1,
    )

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")


class RetrievalOutput(RetrievalDTO, ReasoningTrace):
    """Output schema for the Retrieval Agent."""

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")
