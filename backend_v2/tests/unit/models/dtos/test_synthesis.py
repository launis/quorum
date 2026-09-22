import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.synthesis import (
    ExecutiveSummarySectionResult,
    MatrixExplanationContextDTO,
    MatrixExplanationContextList,
    MatrixExplanationsResult,
    MatrixSectionSynthesesResult,
    SynthesisDistillationDTO,
    SynthesisOutputDTO,
    SynthesisRowExplanationDTO,
    SynthesisSectionDTO,
    XaiHighlightItem,
    XaiHighlightsResult,
)
from backend_v2.models.enums import RoleClassification
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
        user_role=RoleClassification.ARCHITECT,
        user_role_justification="High maturity",
        cited_sources=["src_1"],
        executive_summary=[
            ParagraphBlock(block_type="paragraph", text="Summary paragraph", exact_quotes=[], citations=[])
        ],
    )
    assert dto.user_role == RoleClassification.ARCHITECT
    assert len(dto.executive_summary) == 1

    with pytest.raises(ValidationError):
        ExecutiveSummarySectionResult(
            user_role=RoleClassification.ARCHITECT,
            user_role_justification="High maturity",
            executive_summary=[ParagraphBlock(block_type="paragraph", text="Valid", exact_quotes=[], citations=[])],
            extra_field="fail",
        )  # type: ignore

    with pytest.raises(ValidationError):
        ExecutiveSummarySectionResult(
            user_role="ROLE_EXECUTIVE_STRATEGIST",  # type: ignore[arg-type]
            user_role_justification="Invalid role hallucination",
            executive_summary=[ParagraphBlock(block_type="paragraph", text="Valid", exact_quotes=[], citations=[])],
        )


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


def test_executive_summary_section_result_role_optional() -> None:
    """Verify that user_role and user_role_justification default to None and are optional."""
    dto = ExecutiveSummarySectionResult(
        cited_sources=[],
        executive_summary=[
            ParagraphBlock(block_type="paragraph", text="Summary narrative", exact_quotes=[], citations=[])
        ],
    )
    assert dto.user_role is None
    assert dto.user_role_justification is None
    assert len(dto.executive_summary) == 1


def test_synthesis_output_role_optional() -> None:
    """Verify that SynthesisOutputDTO validates successfully when user_role is omitted."""
    dto = SynthesisOutputDTO(
        cited_sources=[],
        section_syntheses=[],
        xai_highlights=[],
    )
    assert dto.user_role is None
    assert dto.user_role_justification is None


def test_executive_summary_section_result_requires_executive_summary() -> None:
    """Regression test: ExecutiveSummarySectionResult must strictly require non-empty executive_summary."""
    with pytest.raises(ValidationError):
        ExecutiveSummarySectionResult(
            cited_sources=[],
            executive_summary=[],
        )


def test_matrix_explanation_context_strictness() -> None:
    """Test MatrixExplanationContextDTO and TypeAdapter list validation."""
    dto = MatrixExplanationContextDTO(
        real_matrix_id="blk_0123456789abcdef01",
        matrix_id="m0",
        matrix_label="Strategic Alignment",
        score=4.5,
        justification="Strong alignment observed.",
    )
    assert dto.real_matrix_id == "blk_0123456789abcdef01"
    assert dto.score == 4.5

    # Test TypeAdapter validation
    validated_list = MatrixExplanationContextList.validate_python([dto])
    assert len(validated_list) == 1
    assert validated_list[0].matrix_id == "m0"

    with pytest.raises(ValidationError):
        MatrixExplanationContextDTO(
            real_matrix_id="blk_0123456789abcdef01",
            matrix_id="m0",
            matrix_label="Strategic Alignment",
            justification="Justification",
            extra="forbidden",
        )  # type: ignore[call-arg]


def test_synthesis_distillation_strictness() -> None:
    """Test SynthesisDistillationDTO defaults, frozen immutability, and strict extra forbid."""
    dto = SynthesisDistillationDTO(distilled_inputs="Concatenated input text.")
    assert dto.distilled_inputs == "Concatenated input text."
    assert dto.max_extensions == 5
    assert dto.target_locale == "en"

    with pytest.raises(ValidationError):
        dto.distilled_inputs = "mutated"  # type: ignore[misc]

    with pytest.raises(ValidationError):
        SynthesisDistillationDTO(distilled_inputs="test", unknown_field="fail")  # type: ignore[call-arg]


def test_row_explanation_and_matrix_explanations_result_strictness() -> None:
    """Test SynthesisRowExplanationDTO and MatrixExplanationsResult strict validation."""
    row = SynthesisRowExplanationDTO(
        matrix_id="m0",
        row_explanation="High focus on strategic clarity.",
        curated_quotes=["clarity quote"],
    )
    assert row.matrix_id == "m0"
    assert len(row.curated_quotes) == 1

    res = MatrixExplanationsResult(explanations=[row])
    assert len(res.explanations) == 1

    with pytest.raises(ValidationError):
        SynthesisRowExplanationDTO(
            matrix_id="m0",
            row_explanation="Explanation",
            extra="forbidden",
        )  # type: ignore[call-arg]

    with pytest.raises(ValidationError):
        MatrixExplanationsResult(
            explanations=[row],
            extra="forbidden",
        )  # type: ignore[call-arg]
