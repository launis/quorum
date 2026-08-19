"""Unit tests for synthesis prompt directives."""

from backend_v2.models.prompts import (
    SDUI_SYNTHESIS_MANDATE_BLOCK,
    SECTION_SYNTHESIS_DIRECTIVE_BLOCK,
    STATE_ISOLATION_BLOCK,
)


def test_sdui_synthesis_mandate_block_structure() -> None:
    """Verify that SDUI_SYNTHESIS_MANDATE_BLOCK contains valid XML tags and strict rules."""
    assert SDUI_SYNTHESIS_MANDATE_BLOCK.startswith("<sdui_synthesis_mandate>")
    assert SDUI_SYNTHESIS_MANDATE_BLOCK.endswith("</sdui_synthesis_mandate>")
    assert "ALLOWED SDUI BLOCKS" in SDUI_SYNTHESIS_MANDATE_BLOCK
    assert "NO RECURSION" in SDUI_SYNTHESIS_MANDATE_BLOCK
    assert "NO MARKDOWN" in SDUI_SYNTHESIS_MANDATE_BLOCK
    assert "CITATIONS ARRAYS" in SDUI_SYNTHESIS_MANDATE_BLOCK
    assert "USER ROLE EXTRACTION" in SDUI_SYNTHESIS_MANDATE_BLOCK


def test_section_synthesis_directive_block_structure() -> None:
    """Verify that SECTION_SYNTHESIS_DIRECTIVE_BLOCK contains valid XML tags and section routing rules."""
    assert SECTION_SYNTHESIS_DIRECTIVE_BLOCK.startswith("<section_synthesis_directive>")
    assert SECTION_SYNTHESIS_DIRECTIVE_BLOCK.endswith("</section_synthesis_directive>")
    assert "section_syntheses" in SECTION_SYNTHESIS_DIRECTIVE_BLOCK
    assert "layout_id" in SECTION_SYNTHESIS_DIRECTIVE_BLOCK


def test_state_isolation_block_structure() -> None:
    """Verify that STATE_ISOLATION_BLOCK contains valid XML tags and historical isolation rules."""
    assert STATE_ISOLATION_BLOCK.startswith("<state_isolation_mandate>")
    assert STATE_ISOLATION_BLOCK.endswith("</state_isolation_mandate>")
    assert "HistoricalContext" in STATE_ISOLATION_BLOCK
    assert "source_data" in STATE_ISOLATION_BLOCK
