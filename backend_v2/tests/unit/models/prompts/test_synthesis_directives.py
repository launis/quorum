"""Unit tests for synthesis prompt directives."""

import json
import os
import xml.etree.ElementTree as ET

import backend_v2.models.prompts as prompts_module
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


def test_synthesis_directives_xml_validity() -> None:
    """Verify all mandate constants parse cleanly as valid XML."""
    for block_str in [SDUI_SYNTHESIS_MANDATE_BLOCK, SECTION_SYNTHESIS_DIRECTIVE_BLOCK, STATE_ISOLATION_BLOCK]:
        root = ET.fromstring(block_str)
        assert root is not None
        assert len(root.tag) > 0


def test_synthesis_directives_exports() -> None:
    """Verify backend_v2.models.prompts.__all__ exports all synthesis directive constants."""
    assert hasattr(prompts_module, "__all__")
    assert "SDUI_SYNTHESIS_MANDATE_BLOCK" in prompts_module.__all__
    assert "SECTION_SYNTHESIS_DIRECTIVE_BLOCK" in prompts_module.__all__
    assert "STATE_ISOLATION_BLOCK" in prompts_module.__all__


def test_prompt_preservation_qualitative_integrity() -> None:
    """Verify qualitative coaching concepts in seed_data.json remain intact per prompt_preservation_mandate."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
    seed_path = os.path.join(repo_root, "backend_v2", "seed", "seed_data.json")

    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    prompt_blocks = data.get("prompt_blocks", [])
    assert len(prompt_blocks) > 0

    all_descriptions = " ".join(
        b.get("ai_description", "") for b in prompt_blocks if isinstance(b.get("ai_description"), str)
    )

    core_concepts = ["Toulmin", "Goodhart", "Kahneman", "Popper", "Pearl", "Humility", "Traceability", "Coherence"]
    for concept in core_concepts:
        assert concept in all_descriptions, f"Core qualitative concept '{concept}' missing from seed prompt blocks!"
