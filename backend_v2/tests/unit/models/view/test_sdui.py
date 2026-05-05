import pytest
from pydantic import ValidationError

from backend_v2.models.view.sdui import (
    HighlightBoxDisplay,
    MarkdownBlockDisplay,
    ReferenceIntent,
    ReferenceItem,
)


def test_markdown_block_strictness() -> None:
    dto = MarkdownBlockDisplay(content="## Title")
    assert dto.content == "## Title"

    with pytest.raises(ValidationError):
        MarkdownBlockDisplay(content="test", extra="fail")  # type: ignore


def test_highlight_box_strictness() -> None:
    dto = HighlightBoxDisplay(content="Warning insight", color_theme="danger")
    assert dto.color_theme == "danger"

    with pytest.raises(ValidationError):
        HighlightBoxDisplay(content="test", color_theme="invalid")  # type: ignore


def test_reference_item_strictness() -> None:
    dto = ReferenceItem(id="H-1", intent=ReferenceIntent.SEARCH, snippet="test")
    assert dto.id == "H-1"

    with pytest.raises(ValidationError):
        ReferenceItem(id="H-1", intent=ReferenceIntent.SEARCH, snippet="test", extra="fail")  # type: ignore
