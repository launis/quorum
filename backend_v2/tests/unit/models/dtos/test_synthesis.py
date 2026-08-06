import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.synthesis import SynthesisOutputDTO, SynthesisSectionDTO, XaiHighlightItem
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
    )
    assert len(dto.section_syntheses) == 1

    with pytest.raises(ValidationError):
        SynthesisOutputDTO(
            user_role="ROLE_ARCHITECT",
            user_role_justification="Test",
            extra="fail",
        )  # type: ignore
