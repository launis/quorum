import backend_v2.models.state  # noqa: F401
from backend_v2.models.v2_core import (
    I18nText,
    MatrixScorecardRowDTO,
    MatrixSynthesisGroup,
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


def test_matrix_graphs_adapter_empty_groups() -> None:
    profile = OutputProfile(
        id="prf_1234567890abcdef",
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
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_1111111111111111",
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
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Metrics 1D"
    assert isinstance(blocks[1], SduiMetrics1DBlock)
    assert len(blocks[1].axes) == 1


def test_matrix_graphs_adapter_single_group_2d() -> None:
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_2222222222222222",
                title=I18nText(translations={"en": "Compare 2D"}),
                target_blocks=["m1", "m2"],
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
    assert len(blocks[1].axes) == 2


def test_matrix_graphs_adapter_success_3d() -> None:
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_3333333333333333",
                title=I18nText(translations={"en": "Graph 3D"}),
                target_blocks=["m1", "m2", "m3"],
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


def test_matrix_graphs_adapter_wildcard_target_blocks() -> None:
    """Verify target_blocks=['*'] matches all parsed matrices."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_4444444444444444",
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
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert isinstance(blocks[1], SduiRadarChartBlock)


def test_matrix_graphs_adapter_with_section_syntheses() -> None:
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_5555555555555555",
                title=I18nText(translations={"en": "Synthesized Group"}),
                target_blocks=["m1"],
            )
        ],
    )
    cache = RenderedSynthesisCache(
        section_syntheses={
            "grp_5555555555555555": [
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
    assert len(blocks) == 3
    assert isinstance(blocks[0], MarkdownBlock)
    assert isinstance(blocks[1], ParagraphBlock)
    assert blocks[1].text == "Section synthesis summary text."
    assert isinstance(blocks[2], SduiMetrics1DBlock)


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
        id="prf_2222222222222222",
        slug="test_2d",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "2D"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_2222222222222222",
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
    assert len(b_2d) == 2
    assert isinstance(b_2d[1], SduiScatterPlotBlock)

    # 2. 3D matrix
    p_3d = OutputProfile(
        id="prf_3333333333333333",
        slug="test_3d",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "3D"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_3333333333333333",
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
    assert len(b_3d) == 2
    assert isinstance(b_3d[1], SduiRadarChartBlock)

    # 3. text_only
    p_text = OutputProfile(
        id="prf_4444444444444444",
        slug="test_text",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "Text"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_4444444444444444",
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
    assert len(b_text) == 1
    assert isinstance(b_text[0], MarkdownBlock)
