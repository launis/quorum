"""Unit tests for backend_v2/models/prompts/execution/mcp_prompts.py."""

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.prompts.execution.mcp_prompts import (
    CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION,
    MCP_EVIDENCE_INJECTION_DIRECTIVE,
    MCP_JIT_ARGUMENT_SYNTHESIS_SYSTEM_INSTRUCTION,
    SOURCE_EXTRACTION_SYSTEM_INSTRUCTION,
    SOURCE_VERIFICATION_SYSTEM_INSTRUCTION,
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

    assert isinstance(MCP_JIT_ARGUMENT_SYNTHESIS_SYSTEM_INSTRUCTION, str)
    assert "<system_directive>" in MCP_JIT_ARGUMENT_SYNTHESIS_SYSTEM_INSTRUCTION
    assert "Deterministic MCP Argument Synthesizer" in MCP_JIT_ARGUMENT_SYNTHESIS_SYSTEM_INSTRUCTION
    assert "</system_directive>" in MCP_JIT_ARGUMENT_SYNTHESIS_SYSTEM_INSTRUCTION


def test_mcp_prompts_dynamic_builder() -> None:
    """Verify that dynamic builder generates valid system directives with target language and query guidance."""
    directive_fi = build_mcp_citation_extraction_directive("fi")
    assert "<system_directive>" in directive_fi
    assert "language code 'fi'" in directive_fi
    assert "Formulate 'search_query' strictly as concise entity or topic keywords" in directive_fi

    directive_en = build_mcp_citation_extraction_directive("en")
    assert "<system_directive>" in directive_en
    assert "language code 'en'" in directive_en
    assert "Formulate 'search_query' strictly as concise entity or topic keywords" in directive_en

    # Positive: with custom query guidance
    directive_with_guidance = build_mcp_citation_extraction_directive(
        "en", query_guidance="Focus search strictly on corporate acquisitions."
    )
    assert "<rule>Focus search strictly on corporate acquisitions.</rule>" in directive_with_guidance

    # Boundary: empty or whitespace query guidance is ignored without empty rule tags
    directive_whitespace = build_mcp_citation_extraction_directive("en", query_guidance="   \n\t  ")
    assert "<rule></rule>" not in directive_whitespace
    assert "<rule>   " not in directive_whitespace
    assert directive_whitespace == directive_en


@pytest.mark.parametrize(
    "invalid_target_language",
    [
        "",
        "   \t\n  ",
    ],
)
def test_build_mcp_citation_extraction_directive_rejects_empty_target_language(
    invalid_target_language: str,
) -> None:
    """Verify that empty or whitespace-only target_language raises AppException with VALIDATION_FAILED."""
    with pytest.raises(AppException) as exc_info:
        build_mcp_citation_extraction_directive(invalid_target_language)

    assert exc_info.value.status_code == 400
    assert exc_info.value.details == {"error_code": ErrorCodes.VALIDATION_FAILED.value}


@pytest.mark.parametrize(
    "prompt_text",
    [
        SOURCE_EXTRACTION_SYSTEM_INSTRUCTION,
        SOURCE_VERIFICATION_SYSTEM_INSTRUCTION,
        CITATION_SELF_CORRECTION_SYSTEM_INSTRUCTION,
        MCP_EVIDENCE_INJECTION_DIRECTIVE,
        MCP_JIT_ARGUMENT_SYNTHESIS_SYSTEM_INSTRUCTION,
    ],
)
def test_mcp_prompts_xml_tags_balanced(prompt_text: str) -> None:
    """Verify that XML structural tags are properly balanced in every prompt."""
    tags = ["system_directive", "objective", "rules"]
    for tag in tags:
        open_tag = f"<{tag}>"
        close_tag = f"</{tag}>"
        assert prompt_text.count(open_tag) == prompt_text.count(close_tag), f"Mismatched tag: {tag}"

