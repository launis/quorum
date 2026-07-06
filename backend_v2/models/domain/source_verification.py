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

    claim_text: str = Field(description="The explicitly claimed source text in the document.")
    institution_name: str | None = Field(default=None, description="The name of the institution, if mentioned.")
    publication_year: int | None = Field(default=None, description="The year of publication, if mentioned.")


class VerifiedSourceDTO(V2CoreBase):
    """Data Transfer Object representing the result of verifying a SourceClaim.

    Attributes:
        claim_text: The original claim text.
        status: The verification status.
        source_urls: Relevant URLs where the claim was found or analyzed.
        tavily_answer: The textual answer/summary returned by the search API.
    """

    claim_text: str = Field(description="The original claim text.")
    status: Annotated[
        SourceVerificationStatus,
        BeforeValidator(lambda v: SourceVerificationStatus(v) if isinstance(v, str) else v),
    ] = Field(description="The verification status.")
    source_urls: list[str] = Field(default_factory=list, description="Relevant URLs.")
    tavily_answer: str | None = Field(default=None, description="The textual answer from the search provider.")


class SourceVerificationResultDTO(V2CoreBase):
    """Data Transfer Object aggregating all verification results for a document.

    Attributes:
        claims: Verified claims.
        verification_timestamp: Timestamp when verification ran.
        total_claims: Count of claims extracted.
        verified_count: Count of claims marked as VERIFIED.
        hallucination_count: Count of claims marked as HALLUCINATION.
    """

    claims: list[VerifiedSourceDTO] = Field(default_factory=list, description="Verified claims.")
    verification_timestamp: str = Field(description="Timestamp when verification ran.")
    total_claims: int = Field(description="Count of claims extracted.")
    verified_count: int = Field(description="Count of claims marked as VERIFIED.")
    hallucination_count: int = Field(description="Count of claims marked as HALLUCINATION.")
