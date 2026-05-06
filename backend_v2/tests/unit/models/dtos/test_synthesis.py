import pytest
from pydantic import ValidationError

from backend_v2.models.dtos.synthesis import SynthesisOutputDTO, SynthesisSectionDTO, XaiHighlightItem


def test_synthesis_section_strictness() -> None:
    dto = SynthesisSectionDTO(layout_id="lay_1", synthesized_markdown="content")
    assert dto.layout_id == "lay_1"

    with pytest.raises(ValidationError):
        SynthesisSectionDTO(layout_id="lay_1", synthesized_markdown="content", extra="fail")  # type: ignore


def test_xai_highlight_strictness() -> None:
    dto = XaiHighlightItem(extension_type="risk_flag", content="High risk detected.")
    assert dto.extension_type == "risk_flag"

    with pytest.raises(ValidationError):
        XaiHighlightItem(extension_type="risk", content="text", extra="fail")  # type: ignore


def test_synthesis_output_strictness() -> None:
    dto = SynthesisOutputDTO(
        synthesized_markdown="# Title",
        cited_sources=["source1"],
        section_syntheses=[SynthesisSectionDTO(layout_id="l1", synthesized_markdown="test")],
        xai_highlights=[XaiHighlightItem(extension_type="coaching", content="tip")],
    )
    assert dto.synthesized_markdown == "# Title"

    with pytest.raises(ValidationError):
        SynthesisOutputDTO(synthesized_markdown="# Title", extra="fail")  # type: ignore
