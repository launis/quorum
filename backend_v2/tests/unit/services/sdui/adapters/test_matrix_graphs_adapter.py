import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup, RenderedSynthesisCache
from backend_v2.models.dtos.base import DataStarvationEvent
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.sdui_rules import MatrixGraphsAestheticsDTO
from backend_v2.models.enums import PresetView
from backend_v2.models.view.sdui import (
    MarkdownBlock,
    ParagraphBlock,
    SduiMetrics1DBlock,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
)
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.matrix_graphs_adapter import MATRIX_GRAPHS_RULES, MatrixGraphsAdapter


def test_matrix_graphs_adapter_empty_groups() -> None:
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[],
        target_block_order=[],
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


def test_matrix_graphs_adapter_single_group_1d() -> None:
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070018111111111111111",
                title=I18nText(translations={"en": "Metrics 1D"}),
                target_blocks=["m1"],
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

    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiMetrics1DBlock)
    assert blocks[0].title == I18nText(translations={"en": "Metrics 1D"})
    assert len(blocks[0].axes) == 1


def test_matrix_graphs_adapter_single_group_2d() -> None:
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070028222222222222222",
                title=I18nText(translations={"en": "Compare 2D"}),
                target_blocks=["m1", "m2"],
                view_type=PresetView.COMPARE_2D,
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
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiScatterPlotBlock)
    assert blocks[0].title == I18nText(translations={"en": "Compare 2D"})
    assert blocks[0].block_type == "2d_compare"
    assert len(blocks[0].axes) == 2


def test_matrix_graphs_adapter_success_3d() -> None:
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070038333333333333333",
                title=I18nText(translations={"en": "Graph 3D"}),
                target_blocks=["m1", "m2", "m3"],
                view_type=PresetView.MATRIX_3D,
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
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiRadarChartBlock)
    assert blocks[0].title == I18nText(translations={"en": "Graph 3D"})
    assert len(blocks[0].axes) == 3


def test_matrix_graphs_adapter_wildcard_target_blocks() -> None:
    """Verify target_blocks=['*'] matches all parsed matrices."""
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070048444444444444444",
                title=I18nText(translations={"en": "All Matrices"}),
                target_blocks=["*"],
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
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiMetrics1DBlock)
    assert blocks[0].title == I18nText(translations={"en": "All Matrices"})


def test_matrix_graphs_adapter_with_section_syntheses() -> None:
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070058555555555555555",
                title=I18nText(translations={"en": "Synthesized Group"}),
                target_blocks=["m1"],
            )
        ],
    )
    cache = RenderedSynthesisCache(
        section_syntheses={
            "grp_0195f3a0000070058555555555555555": [
                ParagraphBlock(text="Section synthesis summary text.", exact_quotes=[], citations=[])
            ]
        }
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
                name="M1",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M1"}),
                row_explanation="expl",
            )
        },
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], SduiMetrics1DBlock)
    assert blocks[0].title == I18nText(translations={"en": "Synthesized Group"})
    assert isinstance(blocks[1], ParagraphBlock)
    assert blocks[1].text == "Section synthesis summary text."


def test_matrix_graphs_adapter_text_only_with_section_syntheses() -> None:
    """Verify that text_only synthesis group emits MarkdownBlock title header before synthesis text."""
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test_text_only",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a00000700a8aaaaaaaaaaaaaaa",
                title=I18nText(translations={"en": "Text Only Group", "fi": "Tekstiryhmä"}),
                target_blocks=["m1"],
                view_type=PresetView.TEXT_ONLY,
            )
        ],
    )
    cache = RenderedSynthesisCache(
        section_syntheses={
            "grp_0195f3a00000700a8aaaaaaaaaaaaaaa": [
                ParagraphBlock(text="Text-only qualitative narrative.", exact_quotes=[], citations=[])
            ]
        }
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
                name="M1",
                score=4.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M1"}),
                row_explanation="expl",
            )
        },
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Text Only Group"
    assert isinstance(blocks[1], ParagraphBlock)
    assert blocks[1].text == "Text-only qualitative narrative."


def test_matrix_graphs_adapter_insufficient_axes_with_section_syntheses() -> None:
    """Verify that synthesis group with axes below chart threshold emits MarkdownBlock title header before synthesis text."""
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test_insufficient_axes",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a00000700b8bbbbbbbbbbbbbbb",
                title=I18nText(translations={"en": "Radar Under Axes Group", "fi": "Tutka vajaat akselit"}),
                target_blocks=["m1", "m2", "m3"],
                view_type=PresetView.MATRIX_3D,
            )
        ],
    )
    cache = RenderedSynthesisCache(
        section_syntheses={
            "grp_0195f3a00000700b8bbbbbbbbbbbbbbb": [
                ParagraphBlock(text="Synthesis text when chart cannot be drawn.", exact_quotes=[], citations=[])
            ]
        }
    )
    # Only supply 1 parsed matrix, while radar chart requires 3 axes
    context = AdapterContext(
        execution=None,
        locale="fi",
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
                name="M1",
                score=3.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M1"}),
                row_explanation="expl",
            )
        },
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Tutka vajaat akselit"
    assert isinstance(blocks[1], ParagraphBlock)
    assert blocks[1].text == "Synthesis text when chart cannot be drawn."


def test_matrix_graphs_adapter_data_starvation_returns_empty() -> None:
    """Verify that when context.is_data_starved is True, build() deterministically returns empty list."""
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test_starvation",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a00000700c8ccccccccccccccc",
                title=I18nText(translations={"en": "Starved Group"}),
                target_blocks=["m1"],
                view_type=PresetView.METRICS_1D,
            )
        ],
    )
    cache = RenderedSynthesisCache(
        section_syntheses={
            "grp_0195f3a00000700c8ccccccccccccccc": [
                ParagraphBlock(text="Starved synthesis text.", exact_quotes=[], citations=[])
            ]
        },
        data_starvation=DataStarvationEvent(total_atoms=0, reason="insufficient_tokens"),
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
                name="M1",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M1"}),
                row_explanation="expl",
            )
        },
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert blocks == []


def test_matrix_graphs_adapter_explicit_view_types() -> None:
    """Verify explicit view_type routing for 2D, 3D, and Text Only."""
    parsed = {
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
    }

    # 1. 2D compare
    p_2d = OutputProfile(
        id="prf_0195f3a0000070028222222222222222",
        slug="test_2d",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "2D"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070028222222222222222",
                title=I18nText(translations={"en": "2D"}),
                target_blocks=["m1", "m2"],
                view_type="2d_compare",
            )
        ],
    )
    ctx_2d = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=p_2d,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices=parsed,
    )
    b_2d = MatrixGraphsAdapter.build(ctx_2d)
    assert len(b_2d) == 1
    assert isinstance(b_2d[0], SduiScatterPlotBlock)
    assert b_2d[0].title == I18nText(translations={"en": "2D"})
    assert b_2d[0].block_type == "2d_compare"

    # 2. 3D matrix
    p_3d = OutputProfile(
        id="prf_0195f3a0000070038333333333333333",
        slug="test_3d",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "3D"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070038333333333333333",
                title=I18nText(translations={"en": "3D"}),
                target_blocks=["m1", "m2", "m3"],
                view_type="3d_matrix",
            )
        ],
    )
    ctx_3d = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=p_3d,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices=parsed,
    )
    b_3d = MatrixGraphsAdapter.build(ctx_3d)
    assert len(b_3d) == 1
    assert isinstance(b_3d[0], SduiRadarChartBlock)
    assert b_3d[0].title == I18nText(translations={"en": "3D"})

    # 3. text_only
    p_text = OutputProfile(
        id="prf_0195f3a0000070048444444444444444",
        slug="test_text",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "Text"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070048444444444444444",
                title=I18nText(translations={"en": "Text"}),
                target_blocks=["m1"],
                view_type="text_only",
            )
        ],
    )
    ctx_text = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=p_text,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices=parsed,
    )
    b_text = MatrixGraphsAdapter.build(ctx_text)
    assert len(b_text) == 0


def test_matrix_graphs_adapter_unsupported_view_type_fails_fast() -> None:
    """Negative: Unsupported view_type raises Fail-Fast AppException with CONFIGURATION_ERROR."""
    p_invalid = OutputProfile(
        id="prf_0195f3a0000070098999999999999999",
        slug="test_invalid",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "Invalid"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup.model_construct(
                id="grp_0195f3a0000070098999999999999999",
                title=I18nText(translations={"en": "Invalid"}),
                target_blocks=["m1"],
                view_type="unsupported_view_type",
            )
        ],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=p_invalid,
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
            )
        },
    )
    with pytest.raises(AppException) as excinfo:
        MatrixGraphsAdapter.build(context)
    assert excinfo.value.details["error_code"] == "CONFIGURATION_ERROR"


def test_matrix_graphs_adapter_empty_view_type_boundary_fails_fast() -> None:
    """Negative (Boundary): Empty string view_type raises Fail-Fast AppException with CONFIGURATION_ERROR."""
    p_empty_view = OutputProfile(
        id="prf_0195f3a0000070088888888888888888",
        slug="test_empty_view",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "Empty View"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup.model_construct(
                id="grp_0195f3a0000070088888888888888888",
                title=I18nText(translations={"en": "Empty View"}),
                target_blocks=["m1"],
                view_type="",
            )
        ],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=p_empty_view,
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
            )
        },
    )
    with pytest.raises(AppException) as excinfo:
        MatrixGraphsAdapter.build(context)
    assert excinfo.value.details["error_code"] == "CONFIGURATION_ERROR"


def test_matrix_graphs_adapter_2d_boundary_insufficient_axes() -> None:
    """Boundary (min_axes - 1): 2d_compare with only 1 matched axis omits scatter plot block."""
    p_2d_under = OutputProfile(
        id="prf_0195f3a0000070078777777777777777",
        slug="test_2d_under",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "2D Under"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070078777777777777777",
                title=I18nText(translations={"en": "2D Under"}),
                target_blocks=["m1", "m2"],
                view_type=PresetView.COMPARE_2D,
            )
        ],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=p_2d_under,
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
            )
        },
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert blocks == []


def test_matrix_graphs_adapter_1d_boundary_insufficient_axes_with_section_syntheses() -> None:
    """Boundary (min_axes - 1): 1d_metrics with 0 matched axes but section_syntheses present emits MarkdownBlock."""
    p_1d_under = OutputProfile(
        id="prf_0195f3a0000070068666666666666666",
        slug="test_1d_under",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "1D Under"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070068666666666666666",
                title=I18nText(translations={"en": "1D Under Header"}),
                target_blocks=["m_missing"],
                view_type=PresetView.METRICS_1D,
            )
        ],
    )
    cache = RenderedSynthesisCache(
        section_syntheses={
            "grp_0195f3a0000070068666666666666666": [
                ParagraphBlock(text="1D fallback prose.", exact_quotes=[], citations=[])
            ]
        }
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=p_1d_under,
        profile_cache=cache,
        user_name=None,
        org_name=None,
        parsed_matrices={},
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### 1D Under Header"
    assert isinstance(blocks[1], ParagraphBlock)


def test_matrix_graphs_rules() -> None:
    """Verify MATRIX_GRAPHS_RULES export is a valid MatrixGraphsAestheticsDTO with correct thresholds."""
    assert isinstance(MATRIX_GRAPHS_RULES, MatrixGraphsAestheticsDTO)
    assert MATRIX_GRAPHS_RULES["radar"].min_axes == 3
    assert MATRIX_GRAPHS_RULES["scatter"].min_axes == 2
    assert MATRIX_GRAPHS_RULES["metrics"].min_axes == 1
