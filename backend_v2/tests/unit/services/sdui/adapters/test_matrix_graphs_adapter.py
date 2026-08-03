import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.v2_core import I18nText, MatrixScorecardRowDTO, OutputLayoutBlock, OutputProfile
from backend_v2.models.view.sdui import SduiRadarChartBlock
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
        parsed_matrices={},
    )
    blocks = MatrixGraphsAdapter.build(context)
    assert len(blocks) == 0


def test_matrix_graphs_adapter_structural_failure():
    # 3d_matrix requires 3 axes, providing 1 will raise AppException
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="3d_matrix",
                title=I18nText(default_locale="en", translations={"en": "Graph"}),
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
    with pytest.raises(AppException) as exc:
        MatrixGraphsAdapter.build(context)

    assert "Structurally incompatible: layout '3d_matrix' requires at least 3 axes, found 1." in str(exc.value)


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
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiRadarChartBlock)
    assert len(blocks[0].axes) == 3
