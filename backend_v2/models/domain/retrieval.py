"""Retrieval Agent Domain Models.

This module contains the schemas for the Retrieval Agent, focusing on facts extracted from sources.
"""

import logging
from typing import Annotated

from pydantic import ConfigDict, Field, field_validator

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.base import ReasoningTrace, ReasoningTraceDTO

logger = logging.getLogger(__name__)


class RetrievalInput(V2CoreBase):
    """Strict input schema for RetrievalAgent.

    V2 Dynamic: 'chatlog' is mandatory, but other inputs are allowed dynamically.

    Attributes:
        chat_log: The mandatory conversation history to be analyzed.
        product_text: Optional reference text or documents to retrieve facts from.
    """

    chat_log: Annotated[
        str,
        Field(
            description="The mandatory conversation history.",
            json_schema_extra={"x-ui-label": "Chatlog"},
            min_length=1,
        ),
    ]
    product_text: Annotated[
        str | None, Field(description="Reference text/documents to retrieve from.", min_length=1)
    ] = None

    model_config = ConfigDict(frozen=True, strict=True, extra="forbid")


class RetrievedFact(V2CoreBase):
    """A single fact extracted from the material.

    Attributes:
        id: Unique fact identifier string.
        fact_statement: The retrieved factual statement.
        source_quote: Exact quote from the source material validating the fact.
        relevance_score: Integer from 1-5 assessing relevance to the objective.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    id: Annotated[str, Field(description="Fact ID.", min_length=1)]
    fact_statement: Annotated[
        str,
        Field(
            description="The retrieved fact.",
            json_schema_extra={"x-ui-label": "Fact Statement"},
            min_length=1,
        ),
    ]
    source_quote: Annotated[
        str,
        Field(
            description="Exact quote from the source material.",
            json_schema_extra={"x-ui-label": "Source Quote"},
            min_length=1,
        ),
    ]
    relevance_score: Annotated[
        int, Field(description="Relevance to the objective (1-5).", json_schema_extra={"x-ui-label": "Relevance"})
    ]

    @field_validator("relevance_score")
    @classmethod
    def validate_relevance_score(cls, v: int) -> int:
        """Ensure relevance score is between 1 and 5.

        Args:
            v: The score to validate.

        Returns:
            The validated score.

        Raises:
            AppException: If score is not between 1 and 5.
        """
        if not (1 <= v <= 5):
            msg = "relevance_score must be between 1 and 5"
            logger.error("[RetrievalModel] %s: %s", ErrorCodes.VALIDATION_FAILED.name, msg)
            raise AppException(message=msg, details={"error_code": ErrorCodes.VALIDATION_FAILED})
        return v


class RetrievalDTO(ReasoningTraceDTO):
    """Retrieval DTO (Content Only).

    Attributes:
        retrieved_facts: List of facts retrieved and validated by the agent.
        key_takeaways: High-level summary string capturing the retrieved information.
    """
    model_config = ConfigDict(strict=True, extra="forbid")

    retrieved_facts: Annotated[
        list[RetrievedFact],
        Field(
            description="List of facts retrieved.",
            json_schema_extra={"x-ui-label": "Retrieved Facts"},
            min_length=1,
        ),
    ]
    key_takeaways: Annotated[
        str,
        Field(
            description="High-level summary of the retrieved information.",
            json_schema_extra={"x-ui-label": "Key Takeaways"},
            min_length=1,
        ),
    ]


class RetrievalOutput(RetrievalDTO, ReasoningTrace):
    model_config = ConfigDict(strict=True, extra="forbid")
    """Output schema for the Retrieval Agent."""
