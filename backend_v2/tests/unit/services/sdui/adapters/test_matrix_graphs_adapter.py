from backend_v2.models.v2_core import I18nText, MatrixScorecardRowDTO, OutputLayoutBlock, OutputProfile
from backend_v2.models.view.sdui import MarkdownBlock, SduiRadarChartBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.matrix_graphs_adapter import MatrixGraphsAdapter


def test_matrix_graphs_adapter_empty_layouts():
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
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
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="3d_matrix",
                title=I18nText(default_locale="en", translations={"en": "Graph 3D"}),
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
                label_i18n=I18nText(default_locale="en", translations={"en": "M1"}),
                row_explanation="expl",
            )
        },
    )

    # Degrades from 3d_matrix (needs 3) to 1d_metrics (needs 1)
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 2
    assert isinstance(blocks[0], MarkdownBlock)
    assert blocks[0].text == "### Graph 3D"
    from backend_v2.models.view.sdui import SduiMetrics1DBlock

    assert isinstance(blocks[1], SduiMetrics1DBlock)


def test_matrix_graphs_adapter_success():
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="3d_matrix",
                title=I18nText(default_locale="en", translations={"en": "Graph 3D"}),
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
                label_i18n=I18nText(default_locale="en", translations={"en": "M1"}),
                row_explanation="expl",
            ),
            "m2": MatrixScorecardRowDTO(
                block_id="m2",
                name="M2",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(default_locale="en", translations={"en": "M1"}),
                row_explanation="expl",
            ),
            "m3": MatrixScorecardRowDTO(
                block_id="m3",
                name="M3",
                score=5.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(default_locale="en", translations={"en": "M1"}),
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


def test_matrix_graphs_adapter_empty_valid_layout():
    """BVA (Empty Valid Layout): Pass a layout block requesting a valid preset 1d_metrics but without matching parsed_matrices."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="1d_metrics",
                title=I18nText(default_locale="en", translations={"en": "Metrics"}),
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
