"""Retrieval Agent Domain Models.

This module contains the schemas for the Retrieval Agent, focusing on facts extracted from sources.
"""

import logging

from pydantic import BaseModel, ConfigDict, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes

logger = logging.getLogger(__name__)

from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO


class RetrievalInput(BaseModel):
    """Strict input schema for RetrievalAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.
    """

    chat_log: str = Field(
        ..., description="The mandatory conversation history.", json_schema_extra={"x-ui-label": "Chatlog"}
    )
    product_text: str | None = Field(None, description="Reference text/documents to retrieve from.")

    model_config = ConfigDict(frozen=True, extra="allow")

    @field_validator("chat_log", "product_text")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not str(v).strip():
            msg = "Input fields cannot be empty strings."
            logger.error("[RetrievalModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return str(v).strip()


class RetrievedFact(BaseModel):
    """A single fact extracted from the material."""

    id: str = Field(..., description="Fact ID.")
    fact_statement: str = Field(
        ...,
        description="The retrieved fact.",
        json_schema_extra={"x-ui-label": "Fact Statement"},
    )
    source_quote: str = Field(
        ...,
        description="Exact quote from the source material.",
        json_schema_extra={"x-ui-label": "Source Quote"},
    )
    relevance_score: int = Field(
        ..., description="Relevance to the objective (1-5).", json_schema_extra={"x-ui-label": "Relevance"}, ge=1, le=5
    )

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("id", "fact_statement", "source_quote")
    @classmethod
    def validate_non_empty(cls, v: str | None) -> str:
        if not v or not str(v).strip():
            msg = "Field cannot be empty or whitespace only."
            logger.error("[RetrievalModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return str(v).strip()


class RetrievalDTO(ReasoningTraceDTO):
    """Retrieval DTO (Content Only)."""

    retrieved_facts: list[RetrievedFact] = Field(
        ...,
        description="List of facts retrieved.",
        json_schema_extra={"x-ui-label": "Retrieved Facts"},
    )
    key_takeaways: str = Field(
        ...,
        description="High-level summary of the retrieved information.",
        json_schema_extra={"x-ui-label": "Key Takeaways"},
    )

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")

    @field_validator("retrieved_facts")
    @classmethod
    def validate_facts_not_empty(cls, v: list[RetrievedFact]) -> list[RetrievedFact]:
        if not v:
            msg = "Retrieval output must contain at least one fact."
            logger.error("[RetrievalModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return v

    @field_validator("key_takeaways")
    @classmethod
    def validate_non_empty_takeaways(cls, v: str | None) -> str:
        if not v or not str(v).strip():
            msg = "key_takeaways cannot be empty."
            logger.error("[RetrievalModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, status_code=422, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})
        return str(v).strip()


class RetrievalOutput(RetrievalDTO, ReasoningTrace):
    """Output schema for the Retrieval Agent."""

    model_config = ConfigDict(frozen=True, strict=False, extra="forbid")
