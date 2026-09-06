"""Unit tests for OutputProfile factory and baseline templates."""

from backend_v2.models.enums import PresetView, TargetBlockType
from backend_v2.services.factories.output_profile_factory import (
    DEFAULT_FACTORY_EXECUTIVE_SUMMARY_DIRECTIVE,
    DEFAULT_FACTORY_MATRIX_1D_DIRECTIVE,
    DEFAULT_FACTORY_MATRIX_2D_DIRECTIVE,
    DEFAULT_FACTORY_MATRIX_3D_DIRECTIVE,
    DEFAULT_FACTORY_MATRIX_TEXT_DIRECTIVE,
    DEFAULT_FACTORY_ROW_EXPLANATION_DIRECTIVE,
    DEFAULT_FACTORY_TONE_INSTRUCTION,
    DEFAULT_FACTORY_VARIANCE_DIRECTIVE,
    DEFAULT_FACTORY_XAI_DIRECTIVE,
    build_draft_output_profile,
)


def test_build_draft_output_profile_default() -> None:
    """Verify build_draft_output_profile produces a valid OutputProfile with bare TargetBlockType enums."""
    profile = build_draft_output_profile(
        profile_id="prf_0000000000000001",
        workflow_id="wor_0000000000000001",
    )

    assert profile.id == "prf_0000000000000001"
    assert profile.workflow_id == "wor_0000000000000001"
    assert profile.organization_id is None
    assert profile.matrix_synthesis_groups == []

    # Verify target_block_order contains bare TargetBlockType instances (no string .value)
    expected_blocks = [
        TargetBlockType.METADATA_BLOCK,
        TargetBlockType.EXECUTIVE_SUMMARY_BLOCK,
        TargetBlockType.SYNTHESIS_TEXT_BLOCK,
        TargetBlockType.GROUPED_EXTENSIONS_BLOCK,
        TargetBlockType.VARIANCE_VALIDATION_BLOCK,
    ]
    assert profile.target_block_order == expected_blocks
    assert all(isinstance(block, TargetBlockType) for block in profile.target_block_order)

    # Verify substantive directives match default factory constants
    assert profile.tone_instruction == DEFAULT_FACTORY_TONE_INSTRUCTION
    assert profile.executive_summary_directive == DEFAULT_FACTORY_EXECUTIVE_SUMMARY_DIRECTIVE
    assert profile.matrix_1d_synthesis_directive == DEFAULT_FACTORY_MATRIX_1D_DIRECTIVE
    assert profile.matrix_2d_synthesis_directive == DEFAULT_FACTORY_MATRIX_2D_DIRECTIVE
    assert profile.matrix_3d_synthesis_directive == DEFAULT_FACTORY_MATRIX_3D_DIRECTIVE
    assert profile.matrix_text_synthesis_directive == DEFAULT_FACTORY_MATRIX_TEXT_DIRECTIVE
    assert profile.row_explanation_directive == DEFAULT_FACTORY_ROW_EXPLANATION_DIRECTIVE
    assert profile.xai_synthesis_directive == DEFAULT_FACTORY_XAI_DIRECTIVE
    assert profile.variance_synthesis_directive == DEFAULT_FACTORY_VARIANCE_DIRECTIVE


def test_build_draft_output_profile_with_initial_target_block() -> None:
    """Verify build_draft_output_profile correctly inserts MATRIX_GRAPHS_BLOCK and synthesis group."""
    profile = build_draft_output_profile(
        profile_id="prf_0000000000000002",
        workflow_id="wor_0000000000000002",
        organization_id="org_0000000000000001",
        initial_target_block="blk_0000000000000001",
    )

    assert profile.id == "prf_0000000000000002"
    assert profile.workflow_id == "wor_0000000000000002"
    assert profile.organization_id == "org_0000000000000001"

    # Verify MATRIX_GRAPHS_BLOCK was inserted at index 3 as bare Enum
    assert profile.target_block_order[3] == TargetBlockType.MATRIX_GRAPHS_BLOCK
    assert all(isinstance(block, TargetBlockType) for block in profile.target_block_order)

    # Verify matrix_synthesis_groups populated
    assert len(profile.matrix_synthesis_groups) == 1
    group = profile.matrix_synthesis_groups[0]
    assert group.target_blocks == ["blk_0000000000000001"]
    assert group.view_type == PresetView.METRICS_1D
    assert group.title.translations["en"] == "Executive Overview"
    assert group.title.translations["fi"] == "Johdon yleiskuva"


def test_factory_constants_integrity() -> None:
    """Verify that all default factory directive constants are populated with substantive text."""
    directives = [
        DEFAULT_FACTORY_TONE_INSTRUCTION,
        DEFAULT_FACTORY_EXECUTIVE_SUMMARY_DIRECTIVE,
        DEFAULT_FACTORY_MATRIX_1D_DIRECTIVE,
        DEFAULT_FACTORY_MATRIX_2D_DIRECTIVE,
        DEFAULT_FACTORY_MATRIX_3D_DIRECTIVE,
        DEFAULT_FACTORY_MATRIX_TEXT_DIRECTIVE,
        DEFAULT_FACTORY_ROW_EXPLANATION_DIRECTIVE,
        DEFAULT_FACTORY_XAI_DIRECTIVE,
        DEFAULT_FACTORY_VARIANCE_DIRECTIVE,
    ]
    for directive in directives:
        assert isinstance(directive, str)
        assert len(directive) > 20
