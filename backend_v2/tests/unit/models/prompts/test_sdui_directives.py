"""Unit tests for SDUI synthesis prompt directives."""

import xml.etree.ElementTree as ET

from backend_v2.models.prompts.synthesis.sdui_directives import (
    SDUI_BLOCK_STRUCTURE_MANDATE,
    SDUI_SYNTHESIS_MANDATE_BLOCK,
    SECTION_SYNTHESIS_DIRECTIVE_BLOCK,
    STATE_ISOLATION_BLOCK,
    SYNTHESIS_SDUI_MANDATES,
)


def test_sdui_block_structure_mandate_valid_xml() -> None:
    """Verify SDUI_BLOCK_STRUCTURE_MANDATE is valid XML."""
    root = ET.fromstring(SDUI_BLOCK_STRUCTURE_MANDATE)
    assert root.tag == "sdui_block_structure_mandate"
    assert "UNIVERSAL SDUI PRESENTATION RULE" in (root.text or "")


def test_sdui_and_section_directives_valid_xml() -> None:
    """Verify that global synthesis mandate and section directive are valid XML."""
    root_sdui = ET.fromstring(SDUI_SYNTHESIS_MANDATE_BLOCK)
    assert root_sdui.tag in ("sdui_mandate", "sdui_synthesis_mandate")
    assert SYNTHESIS_SDUI_MANDATES == SDUI_SYNTHESIS_MANDATE_BLOCK

    root_section = ET.fromstring(SECTION_SYNTHESIS_DIRECTIVE_BLOCK)
    assert root_section.tag == "section_synthesis_directive"

    root_state = ET.fromstring(STATE_ISOLATION_BLOCK)
    assert root_state.tag == "state_isolation_mandate"
