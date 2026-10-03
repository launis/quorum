"""Source Extraction and Verification DTO Schemas."""

from typing import Annotated

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from backend_v2.models.domain.source_verification import SourceClaimDTO

__all__ = [
    "SourceExtractionResponseSchema",
    "SourceVerificationInputsDTO",
    "SourceVerificationPayloadDTO",
]


class SourceVerificationPayloadDTO(V2CoreBase):
    """Payload DTO for heterogeneous source verification hook input data."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    document_text: Annotated[
        str | None,
        Field(default=None, description="The raw document text to scan for external source citations."),
    ] = None
    prior_analysis: Annotated[
        str | None,
        Field(default=None, description="Prior analysis output text from upstream steps."),
    ] = None
    text: Annotated[
        str | None,
        Field(default=None, description="Raw input text."),
    ] = None
    document: Annotated[
        str | None,
        Field(default=None, description="Document body text."),
    ] = None
    extra_sections: Annotated[
        dict[str, str],
        Field(default_factory=dict, description="Additional document sections."),
    ]

    def extract_text(self) -> str:
        """Extract consolidated text prioritizing canonical text fields."""
        for candidate in (self.document_text, self.prior_analysis, self.text, self.document):
            if candidate is not None and candidate.strip():
                return candidate.strip()
        if self.extra_sections:
            text_parts = [str(v).strip() for v in self.extra_sections.values() if v is not None and str(v).strip()]
            return "\n\n".join(text_parts).strip()
        return ""


class SourceVerificationInputsDTO(V2CoreBase):
    """Data Transfer Object for validating inputs to the Source Verification Hook.

    Attributes:
        document_text: The main text content to verify for external source citations.
        prior_analysis: Prior analysis output text from upstream steps.
        text: Raw input text.
        document: Document body text.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    document_text: Annotated[
        str | None,
        Field(default=None, description="The raw document text to scan for external source citations."),
    ] = None
    prior_analysis: Annotated[
        str | None,
        Field(default=None, description="Prior analysis output text from upstream steps."),
    ] = None
    text: Annotated[
        str | None,
        Field(default=None, description="Raw input text."),
    ] = None
    document: Annotated[
        str | None,
        Field(default=None, description="Document body text."),
    ] = None


class SourceExtractionResponseSchema(V2CoreBase):
    """Structured response schema for extracting claims from a document.

    Attributes:
        claims: A list of extracted source claims. If no claims exist, this is empty.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    claims: Annotated[
        list[SourceClaimDTO], Field(default_factory=list, description="List of source claims extracted from the text.")
    ]
