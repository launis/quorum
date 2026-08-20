import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.synthesis import (
    ExecutiveSummarySectionResult,
    MatrixSectionSynthesesResult,
    SynthesisOutputDTO,
    SynthesisSectionDTO,
    XaiHighlightItem,
    XaiHighlightsResult,
)
from backend_v2.models.view.sdui import ParagraphBlock


def test_synthesis_section_strictness() -> None:
    dto = SynthesisSectionDTO(
        layout_id="lay_1",
        content_blocks=[ParagraphBlock(block_type="paragraph", text="content", exact_quotes=[], citations=[])],
    )
    assert dto.layout_id == "lay_1"

    with pytest.raises(ValidationError):
        SynthesisSectionDTO(
            layout_id="lay_1",
            content_blocks=[ParagraphBlock(block_type="paragraph", text="content", exact_quotes=[], citations=[])],
            extra="fail",
        )  # type: ignore


def test_xai_highlight_strictness() -> None:
    dto = XaiHighlightItem(extension_type="risk_flag", content="High risk detected.")
    assert dto.extension_type == "risk_flag"

    with pytest.raises(ValidationError):
        XaiHighlightItem(extension_type="risk", content="text", extra="fail")  # type: ignore


def test_executive_summary_section_result_strictness() -> None:
    dto = ExecutiveSummarySectionResult(
        user_role="ROLE_ARCHITECT",
        user_role_justification="High maturity",
        cited_sources=["src_1"],
        executive_summary=[
            ParagraphBlock(block_type="paragraph", text="Summary paragraph", exact_quotes=[], citations=[])
        ],
    )
    assert dto.user_role == "ROLE_ARCHITECT"
    assert len(dto.executive_summary) == 1

    with pytest.raises(ValidationError):
        ExecutiveSummarySectionResult(
            user_role="ROLE_ARCHITECT",
            user_role_justification="High maturity",
            extra_field="fail",
        )  # type: ignore


def test_matrix_section_syntheses_result_strictness() -> None:
    dto = MatrixSectionSynthesesResult(
        sections=[
            SynthesisSectionDTO(
                layout_id="layout_0_1d_metrics",
                content_blocks=[
                    ParagraphBlock(block_type="paragraph", text="1D metrics", exact_quotes=[], citations=[])
                ],
            )
        ]
    )
    assert len(dto.sections) == 1

    with pytest.raises(ValidationError):
        MatrixSectionSynthesesResult(
            sections=[],
            extra_forbidden="fail",
        )  # type: ignore


def test_xai_highlights_result_strictness() -> None:
    dto = XaiHighlightsResult(
        xai_highlights=[
            XaiHighlightItem(extension_type="authenticity_evaluation", content="Authentic communication verified.")
        ]
    )
    assert len(dto.xai_highlights) == 1

    with pytest.raises(ValidationError):
        XaiHighlightsResult(
            xai_highlights=[],
            extra_forbidden="fail",
        )  # type: ignore


def test_synthesis_output_strictness() -> None:
    dto = SynthesisOutputDTO(
        user_role="ROLE_ARCHITECT",
        user_role_justification="Test",
        cited_sources=["source1"],
        section_syntheses=[
            SynthesisSectionDTO(
                layout_id="l1",
                content_blocks=[ParagraphBlock(block_type="paragraph", text="test", exact_quotes=[], citations=[])],
            )
        ],
        xai_highlights=[],
    )
    assert len(dto.section_syntheses) == 1

    with pytest.raises(ValidationError):
        SynthesisOutputDTO(
            user_role="ROLE_ARCHITECT",
            user_role_justification="Test",
            extra="fail",
        )  # type: ignore
