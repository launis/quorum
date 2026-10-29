"""Unit tests for Source Verification domain models."""

from __future__ import annotations

import pytest
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import ValidationError

from backend_v2.models.domain.source_verification import (
    SourceClaimDTO,
    SourceVerificationResultDTO,
    SourceVerificationStatus,
    VerifiedSourceDTO,
)
from backend_v2.models.domain.system_config import MCPAuditTrace


class SourceClaimDTOFactory(ModelFactory[SourceClaimDTO]):
    """Polyfactory for SourceClaimDTO."""

    __model__ = SourceClaimDTO


class VerifiedSourceDTOFactory(ModelFactory[VerifiedSourceDTO]):
    """Polyfactory for VerifiedSourceDTO."""

    __model__ = VerifiedSourceDTO


def test_source_claim_dto_valid_instantiation_and_defaults() -> None:
    """Positive test: SourceClaimDTO instantiates cleanly with defaults and explicit optional values."""
    minimal = SourceClaimDTO(claim_text=" OECD 2025 Economic Outlook ")
    assert minimal.claim_text == "OECD 2025 Economic Outlook"
    assert minimal.institution_name is None
    assert minimal.publication_year is None
    assert SourceClaimDTO.model_config["frozen"] is True

    full = SourceClaimDTOFactory.build(
        claim_text="World Bank Report on Infrastructure",
        institution_name="World Bank",
        publication_year=2024,
    )
    assert full.claim_text == "World Bank Report on Infrastructure"
    assert full.institution_name == "World Bank"
    assert full.publication_year == 2024


def test_source_claim_dto_negative_strict_and_extra_forbid() -> None:
    """Negative test: SourceClaimDTO rejects non-strict types and extra fields."""
    with pytest.raises(ValidationError):
        SourceClaimDTO.model_validate({"claim_text": 12345})

    with pytest.raises(ValidationError):
        SourceClaimDTO.model_validate(
            {
                "claim_text": "Valid claim",
                "publication_year": "2024",
            }
        )

    with pytest.raises(ValidationError):
        SourceClaimDTO.model_validate(
            {
                "claim_text": "Valid claim",
                "unexpected_field": "disallowed",
            }
        )


def test_verified_source_dto_valid_enum_and_string_coercion() -> None:
    """Positive test: VerifiedSourceDTO accepts both SourceVerificationStatus enum and valid string."""
    from_enum = VerifiedSourceDTOFactory.build(
        claim_text="Claim A",
        status=SourceVerificationStatus.VERIFIED,
        source_urls=["https://example.org/a"],
        tavily_answer="Confirmed by source A.",
    )
    assert from_enum.status is SourceVerificationStatus.VERIFIED
    assert from_enum.source_urls == ["https://example.org/a"]
    assert from_enum.tavily_answer == "Confirmed by source A."
    assert VerifiedSourceDTO.model_config["frozen"] is True

    from_str = VerifiedSourceDTO.model_validate(
        {
            "claim_text": "Claim B",
            "status": "HALLUCINATION",
        }
    )
    assert from_str.status is SourceVerificationStatus.HALLUCINATION
    assert from_str.source_urls == []
    assert from_str.tavily_answer is None


def test_verified_source_dto_negative_invalid_status_and_extra_fields() -> None:
    """Negative test: VerifiedSourceDTO rejects invalid status strings, wrong types, and extra fields."""
    with pytest.raises(ValidationError):
        VerifiedSourceDTO.model_validate(
            {
                "claim_text": "Claim C",
                "status": "UNKNOWN_STATUS",
            }
        )

    with pytest.raises(ValidationError):
        VerifiedSourceDTO.model_validate(
            {
                "claim_text": "Claim D",
                "status": 999,
            }
        )

    with pytest.raises(ValidationError):
        VerifiedSourceDTO.model_validate(
            {
                "claim_text": "Claim E",
                "status": SourceVerificationStatus.INCONCLUSIVE,
                "extra_key": "forbidden",
            }
        )


def test_source_verification_result_dto_valid_aggregation() -> None:
    """Positive test: SourceVerificationResultDTO aggregates verified claims and MCP audit traces."""
    verified_claim = VerifiedSourceDTO(
        claim_text="StatFinland 2025 GDP growth was 1.8%",
        status=SourceVerificationStatus.VERIFIED,
        source_urls=["https://stat.fi/gdp"],
        tavily_answer="Verified at 1.8%.",
    )
    trace = MCPAuditTrace(
        id="trc_0195f3a0000070018234567890abcdef",
        tool_id="tavily_search",
        gateway_id="sys_0195f3a0000070018234567890abcdef",
        step_name="source_verification",
        query="Verify this claim: StatFinland 2025 GDP growth was 1.8%",
        response_summary="Verified at 1.8%.",
        source_urls=["https://stat.fi/gdp"],
        duration_ms=120,
    )
    result = SourceVerificationResultDTO(
        claims=[verified_claim],
        verification_timestamp="2026-10-29T15:00:00Z",
        total_claims=1,
        verified_count=1,
        hallucination_count=0,
        audit_traces=[trace],
    )
    assert len(result.claims) == 1
    assert result.claims[0].status is SourceVerificationStatus.VERIFIED
    assert result.total_claims == 1
    assert result.verified_count == 1
    assert result.hallucination_count == 0
    assert len(result.audit_traces) == 1
    assert result.audit_traces[0].tool_id == "tavily_search"
    assert SourceVerificationResultDTO.model_config["frozen"] is True


def test_source_verification_result_dto_negative_validation() -> None:
    """Negative test: SourceVerificationResultDTO enforces strict integer counts and forbids extra fields."""
    with pytest.raises(ValidationError):
        SourceVerificationResultDTO.model_validate(
            {
                "verification_timestamp": "2026-10-29T15:00:00Z",
                "total_claims": "1",
                "verified_count": 1,
                "hallucination_count": 0,
            }
        )

    with pytest.raises(ValidationError):
        SourceVerificationResultDTO.model_validate(
            {
                "verification_timestamp": "2026-10-29T15:00:00Z",
                "total_claims": 0,
                "verified_count": 0,
                "hallucination_count": 0,
                "rogue_field": True,
            }
        )
