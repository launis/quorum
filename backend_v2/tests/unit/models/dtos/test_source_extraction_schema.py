"""Tests for source_extraction_schema."""

import pytest
from pydantic import ValidationError

import backend_v2.models.dtos.source_extraction_schema as schema_module
from backend_v2.models.domain.source_verification import SourceClaimDTO
from backend_v2.models.dtos.source_extraction_schema import (
    SourceExtractionResponseSchema,
    SourceVerificationInputsDTO,
)


def test_source_extraction_schema_module_exports() -> None:
    """Verify that source_extraction_schema.py exports expected symbols via __all__."""
    expected = {"SourceExtractionResponseSchema", "SourceVerificationInputsDTO"}
    assert set(schema_module.__all__) == expected
    for name in schema_module.__all__:
        assert hasattr(schema_module, name)


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


def test_source_extraction_response_schema_extra_forbid() -> None:
    """Test that SourceExtractionResponseSchema rejects undeclared fields."""
    with pytest.raises(ValidationError):
        SourceExtractionResponseSchema.model_validate({"claims": [], "extra_forbidden": True})


def test_source_verification_inputs_dto_valid() -> None:
    """Test valid instantiation and optional field defaults of SourceVerificationInputsDTO."""
    dto_empty = SourceVerificationInputsDTO()
    assert dto_empty.document_text is None
    assert dto_empty.prior_analysis is None
    assert dto_empty.text is None
    assert dto_empty.document is None

    dto_full = SourceVerificationInputsDTO(
        document_text="Doc text",
        prior_analysis="Prior analysis text",
        text="Raw text",
        document="Body text",
    )
    assert dto_full.document_text == "Doc text"
    assert dto_full.prior_analysis == "Prior analysis text"
    assert dto_full.text == "Raw text"
    assert dto_full.document == "Body text"


def test_source_verification_inputs_dto_extra_forbid() -> None:
    """Test that SourceVerificationInputsDTO rejects undeclared fields."""
    with pytest.raises(ValidationError):
        SourceVerificationInputsDTO.model_validate({"document_text": "valid", "extra_field": "forbidden"})
