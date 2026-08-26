import pytest

from backend_v2.exceptions import ConfigurationError
from backend_v2.models.v2_core import (
    I18nText,
    MatrixScorecardRowDTO,
    OutputLayoutBlock,
    OutputProfile,
    RenderedSynthesisCache,
)
from backend_v2.models.view.sdui import (
    MarkdownBlock,
    ParagraphBlock,
    SduiMetrics1DBlock,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
)
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.matrix_graphs_adapter import MatrixGraphsAdapter


def test_matrix_graphs_adapter_empty_layouts():
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        layouts=[],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 0


def test_matrix_graphs_adapter_graceful_degradation():
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="3d_matrix",
                title=I18nText(translations={"en": "Graph 3D"}),
                target_blocks=["m1"],
                text_delivery_mode="none",
            )
        ],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="Matrix 1",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M1"}),
                row_explanation="expl",
            )
        },
    )

    # Degrades from 3d_matrix (needs 3) to 1d_metrics (needs 1)
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Graph 3D"
    assert isinstance(blocks[1], SduiMetrics1DBlock)


def test_matrix_graphs_adapter_degrade_to_2d_compare():
    """Verify graceful degradation when 2 axes are provided for 3d_matrix."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="3d_matrix",
                title=I18nText(translations={"en": "Graph 3D"}),
                target_blocks=["m1", "m2"],
                text_delivery_mode="none",
            )
        ],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="M1",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M1"}),
                row_explanation="expl 1",
            ),
            "m2": MatrixScorecardRowDTO(
                block_id="m2",
                name="M2",
                score=4.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M2"}),
                row_explanation="expl 2",
            ),
        },
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert isinstance(blocks[1], SduiScatterPlotBlock)


def test_matrix_graphs_adapter_success_3d():
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="3d_matrix",
                title=I18nText(translations={"en": "Graph 3D"}),
                target_blocks=["m1", "m2", "m3"],
                text_delivery_mode="none",
            )
        ],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="M1",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M1"}),
                row_explanation="expl",
            ),
            "m2": MatrixScorecardRowDTO(
                block_id="m2",
                name="M2",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M1"}),
                row_explanation="expl",
            ),
            "m3": MatrixScorecardRowDTO(
                block_id="m3",
                name="M3",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M1"}),
                row_explanation="expl",
            ),
        },
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Graph 3D"
    assert isinstance(blocks[1], SduiRadarChartBlock)
    assert len(blocks[1].axes) == 3


def test_matrix_graphs_adapter_wildcard_target_blocks():
    """Verify target_blocks=['*'] matches all parsed matrices."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="3d_matrix",
                title=I18nText(translations={"en": "All Matrices"}),
                description=I18nText(translations={"en": "Description for all"}),
                target_blocks=["*"],
                text_delivery_mode="none",
            )
        ],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="M1",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M1"}),
                row_explanation="expl 1",
            ),
            "m2": MatrixScorecardRowDTO(
                block_id="m2",
                name="M2",
                score=4.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M2"}),
                row_explanation="expl 2",
            ),
            "m3": MatrixScorecardRowDTO(
                block_id="m3",
                name="M3",
                score=3.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M3"}),
                row_explanation="expl 3",
            ),
        },
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 3
    assert isinstance(blocks[0], MarkdownBlock)
    assert isinstance(blocks[1], ParagraphBlock)
    assert isinstance(blocks[2], SduiRadarChartBlock)


def test_matrix_graphs_adapter_text_only_modes():
    """Verify text_only preset view with full, titles_only, and none modes."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="text_only",
                title=I18nText(translations={"en": "Text Full"}),
                target_blocks=["m1"],
                text_delivery_mode="full",
            ),
            OutputLayoutBlock(
                preset_view="text_only",
                title=I18nText(translations={"en": "Text Titles"}),
                target_blocks=["m2"],
                text_delivery_mode="titles_only",
            ),
        ],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="Matrix 1",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M1"}),
                row_explanation="Full row explanation text.",
            ),
            "m2": MatrixScorecardRowDTO(
                block_id="m2",
                name="Matrix 2",
                score=4.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M2"}),
                row_explanation="Hidden explanation.",
            ),
        },
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) >= 4


def test_matrix_graphs_adapter_invalid_text_delivery_mode():
    """Verify invalid text_delivery_mode raises ConfigurationError."""
    layout = OutputLayoutBlock(
        preset_view="3d_matrix",
        title=I18nText(translations={"en": "Invalid Mode"}),
        target_blocks=["m1"],
        text_delivery_mode="none",
    )
    object.__setattr__(layout, "text_delivery_mode", "invalid_mode")

    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        layouts=[layout],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    with pytest.raises(ConfigurationError):
        MatrixGraphsAdapter.build(context)


def test_matrix_graphs_adapter_empty_valid_layout():
    """BVA (Empty Valid Layout): Pass a layout block requesting a valid preset 1d_metrics but without matching parsed_matrices."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="1d_metrics",
                title=I18nText(translations={"en": "Metrics"}),
                target_blocks=["missing_id"],
                text_delivery_mode="none",
            )
        ],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    blocks = MatrixGraphsAdapter.build(context)
    # The adapter skips creating the graph block when axes are empty and it's not text_only.
    assert len(blocks) == 0


def test_matrix_graphs_adapter_section_syntheses_positive():
    """Positive: When is_synthesis_enabled is True and layout_id matches section_syntheses, section blocks are appended."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="3d_matrix",
                title=I18nText(translations={"en": "3D Analysis"}),
                target_blocks=["m1", "m2", "m3"],
                is_synthesis_enabled=True,
            )
        ],
    )
    cache = RenderedSynthesisCache(
        section_syntheses={"layout_0_3d_matrix": [ParagraphBlock(text="3D Synthesis narrative")]}
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="A",
                score=4.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "A"}),
                row_explanation="expl A",
            ),
            "m2": MatrixScorecardRowDTO(
                block_id="m2",
                name="B",
                score=3.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "B"}),
                row_explanation="expl B",
            ),
            "m3": MatrixScorecardRowDTO(
                block_id="m3",
                name="C",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "C"}),
                row_explanation="expl C",
            ),
        },
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 3
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### 3D Analysis"
    assert isinstance(blocks[1], ParagraphBlock)
    assert blocks[1].text == "3D Synthesis narrative"
    assert isinstance(blocks[2], SduiRadarChartBlock)


def test_matrix_graphs_adapter_section_syntheses_disabled_negative():
    """Negative 1: When is_synthesis_enabled is False, matching section_syntheses blocks are NOT appended."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="3d_matrix",
                title=I18nText(translations={"en": "3D Analysis"}),
                target_blocks=["m1", "m2", "m3"],
                is_synthesis_enabled=False,
            )
        ],
    )
    cache = RenderedSynthesisCache(
        section_syntheses={"layout_0_3d_matrix": [ParagraphBlock(text="3D Synthesis narrative")]}
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="A",
                score=4.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "A"}),
                row_explanation="expl A",
            ),
            "m2": MatrixScorecardRowDTO(
                block_id="m2",
                name="B",
                score=3.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "B"}),
                row_explanation="expl B",
            ),
            "m3": MatrixScorecardRowDTO(
                block_id="m3",
                name="C",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "C"}),
                row_explanation="expl C",
            ),
        },
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert isinstance(blocks[1], SduiRadarChartBlock)


def test_matrix_graphs_adapter_section_syntheses_unmapped_key_negative():
    """Negative 2: When is_synthesis_enabled is True but layout_id does not exist in section_syntheses, no crash and synthesis blocks omitted."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="3d_matrix",
                title=I18nText(translations={"en": "3D Analysis"}),
                target_blocks=["m1", "m2", "m3"],
                is_synthesis_enabled=True,
            )
        ],
    )
    cache = RenderedSynthesisCache(section_syntheses={"layout_99_other": [ParagraphBlock(text="Other narrative")]})
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=profile,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={
            "m1": MatrixScorecardRowDTO(
                block_id="m1",
                name="A",
                score=4.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "A"}),
                row_explanation="expl A",
            ),
            "m2": MatrixScorecardRowDTO(
                block_id="m2",
                name="B",
                score=3.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "B"}),
                row_explanation="expl B",
            ),
            "m3": MatrixScorecardRowDTO(
                block_id="m3",
                name="C",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "C"}),
                row_explanation="expl C",
            ),
        },
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert isinstance(blocks[1], SduiRadarChartBlock)
