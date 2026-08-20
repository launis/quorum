"""Unit tests for synthesis prompt directives."""

import xml.etree.ElementTree as ET

from backend_v2.models.enums import TargetBlockType
from backend_v2.models.prompts.synthesis_directives import (
    EXECUTIVE_SUMMARY_DIRECTIVE,
    EXECUTIVE_SUMMARY_SECTION_ID,
    MATRIX_1D_SYNTHESIS_DIRECTIVE,
    MATRIX_2D_SYNTHESIS_DIRECTIVE,
    MATRIX_3D_SYNTHESIS_DIRECTIVE,
    SDUI_SYNTHESIS_MANDATE_BLOCK,
    SECTION_SYNTHESIS_DIRECTIVE_BLOCK,
    STATE_ISOLATION_BLOCK,
)


def test_executive_summary_section_id_ssot_parity() -> None:
    """Verify EXECUTIVE_SUMMARY_SECTION_ID strictly matches TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value."""
    assert EXECUTIVE_SUMMARY_SECTION_ID == "executive_summary_block"
    assert EXECUTIVE_SUMMARY_SECTION_ID == TargetBlockType.EXECUTIVE_SUMMARY_BLOCK.value


def test_executive_summary_directive_valid_xml() -> None:
    """Verify EXECUTIVE_SUMMARY_DIRECTIVE is valid XML with expected root tag and content."""
    root = ET.fromstring(EXECUTIVE_SUMMARY_DIRECTIVE)
    assert root.tag == "executive_summary_directive"
    assert "EXECUTIVE SUMMARY SYNTHESIS MANDATE:" in (root.text or "")


def test_matrix_directives_valid_xml() -> None:
    """Verify that all matrix directives wrap valid XML blocks."""
    # 1D directive
    root_1d = ET.fromstring(MATRIX_1D_SYNTHESIS_DIRECTIVE)
    assert root_1d.tag == "matrix_1d_directive"
    assert "1D METRICS SYNTHESIS MANDATE" in root_1d.text

    # 2D directive
    root_2d = ET.fromstring(MATRIX_2D_SYNTHESIS_DIRECTIVE)
    assert root_2d.tag == "matrix_2d_directive"
    assert "2D COMPARISON SYNTHESIS MANDATE" in root_2d.text

    # 3D directive
    root_3d = ET.fromstring(MATRIX_3D_SYNTHESIS_DIRECTIVE)
    assert root_3d.tag == "matrix_3d_directive"
    assert "3D RADAR SYNTHESIS MANDATE" in root_3d.text


def test_sdui_and_section_directives_valid_xml() -> None:
    """Verify that global synthesis mandate and section directive are valid XML."""
    root_sdui = ET.fromstring(SDUI_SYNTHESIS_MANDATE_BLOCK)
    assert root_sdui.tag == "sdui_synthesis_mandate"

    root_section = ET.fromstring(SECTION_SYNTHESIS_DIRECTIVE_BLOCK)
    assert root_section.tag == "section_synthesis_directive"

    root_state = ET.fromstring(STATE_ISOLATION_BLOCK)
    assert root_state.tag == "state_isolation_mandate"
