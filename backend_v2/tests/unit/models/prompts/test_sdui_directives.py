"""Unit tests for SDUI synthesis prompt directives."""

import xml.etree.ElementTree as ET

import pytest

from backend_v2.models.prompts.synthesis.sdui_directives import (
    SDUI_BLOCK_STRUCTURE_MANDATE,
    SECTION_SYNTHESIS_DIRECTIVE_BLOCK,
    STATE_ISOLATION_BLOCK,
    SYNTHESIS_SDUI_MANDATES,
)


def test_sdui_block_structure_mandate_valid_xml() -> None:
    """Verify SDUI_BLOCK_STRUCTURE_MANDATE is valid XML."""
    root = ET.fromstring(SDUI_BLOCK_STRUCTURE_MANDATE)
    assert root.tag == "sdui_block_structure_mandate"
    assert root.text is not None
    assert "UNIVERSAL SDUI PRESENTATION RULE" in root.text


def test_sdui_and_section_directives_valid_xml() -> None:
    """Verify that global synthesis mandate and section directive are valid XML."""
    root_sdui = ET.fromstring(SYNTHESIS_SDUI_MANDATES)
    assert root_sdui.tag in ("sdui_mandate", "sdui_synthesis_mandate")
    assert "SDUI POLYMORPHIC SYNTHESIS MANDATE" in SYNTHESIS_SDUI_MANDATES
    assert "ALLOWED SDUI BLOCKS" in SYNTHESIS_SDUI_MANDATES
    assert "BULLET LISTS MUST USE OBJECTS" in SYNTHESIS_SDUI_MANDATES

    root_section = ET.fromstring(SECTION_SYNTHESIS_DIRECTIVE_BLOCK)
    assert root_section.tag == "section_synthesis_directive"

    root_state = ET.fromstring(STATE_ISOLATION_BLOCK)
    assert root_state.tag == "state_isolation_mandate"


def test_state_isolation_block_unescaped_tags_raise_parse_error() -> None:
    """Verify that unescaping inner tags in STATE_ISOLATION_BLOCK triggers XML ParseError."""
    corrupted_xml = STATE_ISOLATION_BLOCK.replace("&lt;HistoricalContext&gt;", "<HistoricalContext>")
    with pytest.raises(ET.ParseError):
        ET.fromstring(corrupted_xml)


def test_sdui_directives_exclude_dynamic_placeholders_and_raw_child_elements() -> None:
    """Verify static prompt directives contain zero unformatted template placeholders or nested XML child elements."""
    for directive in (
        SDUI_BLOCK_STRUCTURE_MANDATE,
        SYNTHESIS_SDUI_MANDATES,
        SECTION_SYNTHESIS_DIRECTIVE_BLOCK,
        STATE_ISOLATION_BLOCK,
    ):
        root = ET.fromstring(directive)
        assert len(list(root)) == 0
        assert "{layout_id}" not in directive
        assert "{source_data}" not in directive
