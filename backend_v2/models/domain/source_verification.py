"""Domain models for Source Verification features.

These models handle the representation of claims extracted from documents
and their verification statuses via external search services.
"""

from enum import StrEnum
from typing import Annotated

from pydantic import BeforeValidator, Field

from backend_v2.models.core_base import V2CoreBase


class SourceVerificationStatus(StrEnum):
    """Enumeration of possible verification statuses for a source claim."""

    VERIFIED = "VERIFIED"
    HALLUCINATION = "HALLUCINATION"
    INCONCLUSIVE = "INCONCLUSIVE"


class SourceClaimDTO(V2CoreBase):
    """Data Transfer Object representing a source claim extracted from text.

    Attributes:
        claim_text: The explicitly claimed source text in the document.
        institution_name: The name of the institution, if mentioned.
        publication_year: The year of publication, if mentioned.
    """

    claim_text: Annotated[str, Field(description="The explicitly claimed source text in the document.")]
    institution_name: Annotated[str | None, Field(description="The name of the institution, if mentioned.")] = None
    publication_year: Annotated[int | None, Field(description="The year of publication, if mentioned.")] = None


class VerifiedSourceDTO(V2CoreBase):
    """Data Transfer Object representing the result of verifying a SourceClaim.

    Attributes:
        claim_text: The original claim text.
        status: The verification status.
        source_urls: Relevant URLs where the claim was found or analyzed.
        tavily_answer: The textual answer/summary returned by the search API.
    """

    claim_text: Annotated[str, Field(description="The original claim text.")]
    status: Annotated[
        SourceVerificationStatus,
        BeforeValidator(lambda v: SourceVerificationStatus(v) if isinstance(v, str) else v),
        Field(description="The verification status."),
    ]
    source_urls: Annotated[list[str], Field(description="Relevant URLs.")] = Field(default_factory=list)
    tavily_answer: Annotated[str | None, Field(description="The textual answer from the search provider.")] = None


class SourceVerificationResultDTO(V2CoreBase):
    """Data Transfer Object aggregating all verification results for a document.

    Attributes:
        claims: Verified claims.
        verification_timestamp: Timestamp when verification ran.
        total_claims: Count of claims extracted.
        verified_count: Count of claims marked as VERIFIED.
        hallucination_count: Count of claims marked as HALLUCINATION.
    """

    claims: Annotated[list[VerifiedSourceDTO], Field(description="Verified claims.")] = Field(default_factory=list)
    verification_timestamp: Annotated[str, Field(description="Timestamp when verification ran.")]
    total_claims: Annotated[int, Field(description="Count of claims extracted.")]
    verified_count: Annotated[int, Field(description="Count of claims marked as VERIFIED.")]
    hallucination_count: Annotated[int, Field(description="Count of claims marked as HALLUCINATION.")]
