import pytest
from pydantic import ValidationError

from backend_v2.models.domain.xai import (
    CitationExtension,
    XAIOutputDTO,
    ComparisonDataDTO,
)
from backend_v2.models.dtos.report import MatrixObservabilityDTO
from backend_v2.models.enums import XaiExtensionType, ReferenceTitle

def test_matrix_observability_dto_strictness():
    """Test that MatrixObservabilityDTO forbids extra fields."""
    dto = MatrixObservabilityDTO(true_atoms_count=5, false_atoms_count=2)
    assert dto.true_atoms_count == 5

    with pytest.raises(ValidationError):
        MatrixObservabilityDTO(true_atoms_count=5, false_atoms_count=2, extra_field="should fail")

def test_xai_output_dto_polymorphic_extensions():
    """Test the discriminated union in XAIOutputDTO."""
    ext = CitationExtension(
        source_id="src_1",
        snippet="Important quote",
        url="http://example.com"
    )
    dto = XAIOutputDTO(
        thought_process="Mock thought process",
        conclusion="Mock conclusion",
        executive_summary="Summary",
        verified_facts="Facts",
        cognitive_behavior="Cognitive",
        causal_chain="Causal",
        analysis_strengths="Strengths",
        analysis_weaknesses="Weaknesses",
        analysis_opportunities="Opportunities",
        analysis_recommendations="Recommendations",
        final_verdict="Verdict",
        confidence_score=0.9,
        output_extensions=[ext],
        comparison_data=ComparisonDataDTO(baseline_score=4.0, delta=0.5, trend="up"),
    )
    assert len(dto.output_extensions) == 1
    assert dto.output_extensions[0].extension_type == XaiExtensionType.CITATION

def test_reference_title_enum():
    """Test the newly added ReferenceTitle Enum."""
    assert ReferenceTitle.WEB_SEARCH == "REF_WEB_SEARCH"
    assert ReferenceTitle.INTERNAL_DOCUMENT == "REF_INTERNAL_DOCUMENT"
