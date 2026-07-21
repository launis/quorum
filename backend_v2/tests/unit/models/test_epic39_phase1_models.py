from unittest.mock import AsyncMock
from backend_v2.models.domain.xai import (
    CitationExtension,
    ComparisonDataDTO,
    XAIOutputDTO,
)
from backend_v2.models.enums import ReferenceTitle, XaiExtensionType


def test_xai_output_dto_polymorphic_extensions() -> None:
    """Test the discriminated union in XAIOutputDTO."""
    ext = CitationExtension(source_id="src_1", snippet="Important quote", url="http://example.com")
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


def test_reference_title_enum() -> None:
    """Test the newly added ReferenceTitle Enum."""
    assert ReferenceTitle.WEB_SEARCH.value == "REF_WEB_SEARCH"
    assert ReferenceTitle.INTERNAL_DOCUMENT.value == "REF_INTERNAL_DOCUMENT"
