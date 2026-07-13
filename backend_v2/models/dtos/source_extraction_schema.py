"""Data Transfer Objects for LLM Source Extraction mapping.

These schemas enforce structured JSON outputs from the LLM when extracting source claims.
"""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from backend_v2.models.domain.source_verification import SourceClaimDTO


class SourceExtractionResponseSchema(BaseModel):
    """Structured response schema for extracting claims from a document.

    Attributes:
        claims: A list of extracted source claims. If no claims exist, this is empty.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    claims: Annotated[
        list[SourceClaimDTO], Field(default_factory=list, description="List of source claims extracted from the text.")
    ]
