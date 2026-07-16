"""Tests for source_extraction_schema."""

from backend_v2.models.domain.source_verification import SourceClaimDTO
from backend_v2.models.dtos.source_extraction_schema import SourceExtractionResponseSchema


def test_source_extraction_response_schema_valid() -> None:
    """Test valid instantiation of SourceExtractionResponseSchema."""
    claim = SourceClaimDTO(claim_text="Test quote", institution_name="Test Inst", publication_year=2023)
    dto = SourceExtractionResponseSchema(claims=[claim])
    assert len(dto.claims) == 1
    assert dto.claims[0].claim_text == "Test quote"


def test_source_extraction_response_schema_defaults() -> None:
    """Test defaults for SourceExtractionResponseSchema."""
    dto = SourceExtractionResponseSchema()
    assert dto.claims == []
