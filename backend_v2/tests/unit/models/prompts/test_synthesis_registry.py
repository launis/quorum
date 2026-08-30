"""Unit tests for SynthesisPromptRegistry.

Verifies all 4 ISTQB partitions:
1. Executive Summary block mapping
2. Variance / Authenticity / XAI block mappings
3. 1D/2D/3D/Text-only preset view mappings (Enum and string aliases)
4. Fallbacks on unknown views, unmapped blocks, and falsy/None inputs
"""

import pytest

from backend_v2.models.enums import PresetView, TargetBlockType
from backend_v2.models.prompts.synthesis_directives import (
    EXECUTIVE_SUMMARY_DIRECTIVE,
    MATRIX_1D_SYNTHESIS_DIRECTIVE,
    MATRIX_2D_SYNTHESIS_DIRECTIVE,
    MATRIX_3D_SYNTHESIS_DIRECTIVE,
    MATRIX_TEXT_SYNTHESIS_DIRECTIVE,
    ROW_EXPLANATION_DIRECTIVE,
    VARIANCE_EXPLANATION_DIRECTIVE,
    XAI_EXPLANATIONS_DIRECTIVE,
)
from backend_v2.models.prompts.synthesis_registry import SynthesisPromptRegistry


def test_target_block_executive_summary_mapping() -> None:
    """Test that TargetBlockType.EXECUTIVE_SUMMARY_BLOCK resolves to EXECUTIVE_SUMMARY_DIRECTIVE."""
    # Enum lookup
    directive_enum = SynthesisPromptRegistry.get_section_directive(TargetBlockType.EXECUTIVE_SUMMARY_BLOCK)
    assert directive_enum == EXECUTIVE_SUMMARY_DIRECTIVE

    # String value lookup
    directive_str = SynthesisPromptRegistry.get_section_directive("executive_summary_block")
    assert directive_str == EXECUTIVE_SUMMARY_DIRECTIVE


def test_target_block_variance_and_authenticity_mappings() -> None:
    """Test that variance and authenticity blocks map to VARIANCE_EXPLANATION_DIRECTIVE."""
    variance_enum = SynthesisPromptRegistry.get_section_directive(TargetBlockType.VARIANCE_VALIDATION_BLOCK)
    assert variance_enum == VARIANCE_EXPLANATION_DIRECTIVE

    authenticity_enum = SynthesisPromptRegistry.get_section_directive(TargetBlockType.AUTHENTICITY_EVALUATION_BLOCK)
    assert authenticity_enum == VARIANCE_EXPLANATION_DIRECTIVE

    variance_str = SynthesisPromptRegistry.get_section_directive("variance_validation_block")
    assert variance_str == VARIANCE_EXPLANATION_DIRECTIVE

    authenticity_str = SynthesisPromptRegistry.get_section_directive("authenticity_evaluation_block")
    assert authenticity_str == VARIANCE_EXPLANATION_DIRECTIVE


def test_target_block_grouped_extensions_and_synthesis_text_mappings() -> None:
    """Test that grouped extensions and synthesis text blocks resolve to their respective directives."""
    xai_enum = SynthesisPromptRegistry.get_section_directive(TargetBlockType.GROUPED_EXTENSIONS_BLOCK)
    assert xai_enum == XAI_EXPLANATIONS_DIRECTIVE

    xai_str = SynthesisPromptRegistry.get_section_directive("grouped_extensions_block")
    assert xai_str == XAI_EXPLANATIONS_DIRECTIVE

    text_enum = SynthesisPromptRegistry.get_section_directive(TargetBlockType.SYNTHESIS_TEXT_BLOCK)
    assert text_enum == MATRIX_TEXT_SYNTHESIS_DIRECTIVE

    text_str = SynthesisPromptRegistry.get_section_directive("synthesis_text_block")
    assert text_str == MATRIX_TEXT_SYNTHESIS_DIRECTIVE


@pytest.mark.parametrize(
    ("view_input", "expected_directive"),
    [
        (PresetView.METRICS_1D, MATRIX_1D_SYNTHESIS_DIRECTIVE),
        ("1d_metrics", MATRIX_1D_SYNTHESIS_DIRECTIVE),
        ("metrics1d", MATRIX_1D_SYNTHESIS_DIRECTIVE),
        ("1D_METRICS", MATRIX_1D_SYNTHESIS_DIRECTIVE),
        (PresetView.COMPARE_2D, MATRIX_2D_SYNTHESIS_DIRECTIVE),
        ("2d_compare", MATRIX_2D_SYNTHESIS_DIRECTIVE),
        ("compare2d", MATRIX_2D_SYNTHESIS_DIRECTIVE),
        ("2D_COMPARE", MATRIX_2D_SYNTHESIS_DIRECTIVE),
        (PresetView.MATRIX_3D, MATRIX_3D_SYNTHESIS_DIRECTIVE),
        ("3d_matrix", MATRIX_3D_SYNTHESIS_DIRECTIVE),
        ("matrix3d", MATRIX_3D_SYNTHESIS_DIRECTIVE),
        ("3D_MATRIX", MATRIX_3D_SYNTHESIS_DIRECTIVE),
        (PresetView.TEXT_ONLY, MATRIX_TEXT_SYNTHESIS_DIRECTIVE),
        ("text_only", MATRIX_TEXT_SYNTHESIS_DIRECTIVE),
        ("textonly", MATRIX_TEXT_SYNTHESIS_DIRECTIVE),
        ("TEXT_ONLY", MATRIX_TEXT_SYNTHESIS_DIRECTIVE),
    ],
)
def test_preset_view_partitions(view_input: PresetView | str, expected_directive: str) -> None:
    """Test all valid 1D, 2D, 3D, and text_only preset views across enum and string variants."""
    directive = SynthesisPromptRegistry.get_section_directive(view_input)
    assert directive == expected_directive


def test_fallback_on_unknown_views_and_none() -> None:
    """Test that None, unknown view strings, and unmapped target blocks fall back cleanly."""
    # None input
    assert SynthesisPromptRegistry.get_section_directive(None) == MATRIX_2D_SYNTHESIS_DIRECTIVE

    # Unknown string key
    assert SynthesisPromptRegistry.get_section_directive("unknown_custom_view") == MATRIX_2D_SYNTHESIS_DIRECTIVE

    # Unmapped TargetBlockType (e.g. GLOBAL_SCORE_BLOCK)
    assert (
        SynthesisPromptRegistry.get_section_directive(TargetBlockType.GLOBAL_SCORE_BLOCK)
        == MATRIX_2D_SYNTHESIS_DIRECTIVE
    )


def test_row_explanation_directive_retrieval() -> None:
    """Test that get_row_explanation_directive returns the SSOT ROW_EXPLANATION_DIRECTIVE."""
    assert SynthesisPromptRegistry.get_row_explanation_directive() == ROW_EXPLANATION_DIRECTIVE
