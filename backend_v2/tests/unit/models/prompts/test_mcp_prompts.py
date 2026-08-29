"""Unit tests for backend_v2/models/prompts/mcp_prompts.py."""

import pytest

from backend_v2.models.prompts.mcp_prompts import (
    CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION,
    MCP_EVIDENCE_INJECTION_DIRECTIVE,
    SOURCE_EXTRACTION_SYSTEM_INSTRUCTION,
    SOURCE_VERIFICATION_SYSTEM_INSTRUCTION,
    __all__ as mcp_prompts_all,
    build_mcp_citation_extraction_directive,
)


def test_mcp_prompts_constants_exist_and_non_empty() -> None:
    """Verify that all MCP prompt constants are valid, non-empty XML strings."""
    assert isinstance(SOURCE_EXTRACTION_SYSTEM_INSTRUCTION, str)
    assert "<system_directive>" in SOURCE_EXTRACTION_SYSTEM_INSTRUCTION
    assert "<objective>" in SOURCE_EXTRACTION_SYSTEM_INSTRUCTION
    assert "</system_directive>" in SOURCE_EXTRACTION_SYSTEM_INSTRUCTION

    assert isinstance(SOURCE_VERIFICATION_SYSTEM_INSTRUCTION, str)
    assert "<system_directive>" in SOURCE_VERIFICATION_SYSTEM_INSTRUCTION
    assert "VERIFIED" in SOURCE_VERIFICATION_SYSTEM_INSTRUCTION
    assert "</system_directive>" in SOURCE_VERIFICATION_SYSTEM_INSTRUCTION

    assert isinstance(CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION, str)
    assert "<system_directive>" in CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION
    assert "corrected_claim" in CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION
    assert "</system_directive>" in CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION

    assert isinstance(MCP_EVIDENCE_INJECTION_DIRECTIVE, str)
    assert "<system_directive>" in MCP_EVIDENCE_INJECTION_DIRECTIVE
    assert "EVIDENCE INJECTION COMPLETE" in MCP_EVIDENCE_INJECTION_DIRECTIVE
    assert "</system_directive>" in MCP_EVIDENCE_INJECTION_DIRECTIVE


def test_mcp_prompts_dynamic_builder() -> None:
    """Verify that dynamic builder generates valid system directives with target language."""
    directive_fi = build_mcp_citation_extraction_directive("fi")
    assert "<system_directive>" in directive_fi
    assert "language code 'fi'" in directive_fi

    directive_en = build_mcp_citation_extraction_directive("en")
    assert "<system_directive>" in directive_en
    assert "language code 'en'" in directive_en


def test_mcp_prompts_exports_integrity() -> None:
    """Verify that __all__ contains strictly unique, non-empty strings with expected exports."""
    expected_exports = {
        "SOURCE_EXTRACTION_SYSTEM_INSTRUCTION",
        "SOURCE_VERIFICATION_SYSTEM_INSTRUCTION",
        "CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION",
        "MCP_EVIDENCE_INJECTION_DIRECTIVE",
        "build_mcp_citation_extraction_directive",
    }
    assert set(mcp_prompts_all) == expected_exports
    assert len(mcp_prompts_all) == len(set(mcp_prompts_all))


@pytest.mark.parametrize(
    "prompt_text",
    [
        SOURCE_EXTRACTION_SYSTEM_INSTRUCTION,
        SOURCE_VERIFICATION_SYSTEM_INSTRUCTION,
        CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION,
        MCP_EVIDENCE_INJECTION_DIRECTIVE,
    ],
)
def test_mcp_prompts_xml_tags_balanced(prompt_text: str) -> None:
    """Verify that XML structural tags are properly balanced in every prompt."""
    tags = ["system_directive", "objective", "rules"]
    for tag in tags:
        open_tag = f"<{tag}>"
        close_tag = f"</{tag}>"
        assert prompt_text.count(open_tag) == prompt_text.count(close_tag), f"Mismatched tag: {tag}"
