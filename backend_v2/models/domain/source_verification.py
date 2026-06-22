"""Domain models for Source Verification features.

These models handle the representation of claims extracted from documents
and their verification statuses via external search services.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class SourceVerificationStatus(str, Enum):
    """Enumeration of possible verification statuses for a source claim."""

    VERIFIED = "VERIFIED"
    HALLUCINATION = "HALLUCINATION"
    INCONCLUSIVE = "INCONCLUSIVE"


class SourceClaimDTO(BaseModel):
    """Data Transfer Object representing a source claim extracted from text.

    Attributes:
        claim_text: The explicitly claimed source text in the document.
        institution_name: The name of the institution, if mentioned.
        publication_year: The year of publication, if mentioned.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    claim_text: str = Field(description="The explicitly claimed source text in the document.")
    institution_name: str | None = Field(default=None, description="The name of the institution, if mentioned.")
    publication_year: int | None = Field(default=None, description="The year of publication, if mentioned.")


class VerifiedSourceDTO(BaseModel):
    """Data Transfer Object representing the result of verifying a SourceClaim.

    Attributes:
        claim_text: The original claim text.
        status: The verification status.
        source_urls: List of URLs where the claim was found or analyzed.
        tavily_answer: The textual answer/summary returned by the search API.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    claim_text: str = Field(description="The original claim text.")
    status: SourceVerificationStatus = Field(description="The verification status.")
    source_urls: list[str] = Field(default_factory=list, description="List of relevant URLs.")
    tavily_answer: str | None = Field(default=None, description="The textual answer from the search provider.")


class SourceVerificationResultDTO(BaseModel):
    """Data Transfer Object aggregating all verification results for a document.

    Attributes:
        claims: List of verified claims.
        verification_timestamp: ISO 8601 string representing when the check ran.
        total_claims: Total number of claims extracted.
        verified_count: Number of claims marked as VERIFIED.
        hallucination_count: Number of claims marked as HALLUCINATION.
    """

    model_config = ConfigDict(strict=True, extra="forbid")

    claims: list[VerifiedSourceDTO] = Field(default_factory=list, description="List of verified claims.")
    verification_timestamp: str = Field(description="ISO 8601 string when verification ran.")
    total_claims: int = Field(description="Total number of claims extracted.")
    verified_count: int = Field(description="Number of claims marked as VERIFIED.")
    hallucination_count: int = Field(description="Number of claims marked as HALLUCINATION.")
