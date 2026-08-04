import pytest

from backend_v2.exceptions import AppException
from backend_v2.models.v2_core import I18nText, MatrixScorecardRowDTO, OutputLayoutBlock, OutputProfile
from backend_v2.models.view.sdui import SduiMatrixTableBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.matrix_summary_table_adapter import MatrixSummaryTableAdapter


def test_matrix_summary_table_adapter_empty_layouts():
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
        synthesis_md=None,
        parsed_matrices={},
    )
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 0


def test_matrix_summary_table_adapter_structural_failure():
    # matrix_summary requires at least 1 axis
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="matrix_summary",
                title=I18nText(default_locale="en", translations={"en": "Summary"}),
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
        synthesis_md=None,
        parsed_matrices={},
    )
    with pytest.raises(AppException) as exc:
        MatrixSummaryTableAdapter.build(context)

    assert "Structurally incompatible: layout 'matrix_summary' requires at least 1 axes, found 0." in str(exc.value)


def test_matrix_summary_table_adapter_success():
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="matrix_summary",
                title=I18nText(default_locale="en", translations={"en": "Table Summary"}),
                target_blocks=["m1"],
                matrix_visible_columns=["label", "score"],
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
        synthesis_md=None,
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
            )
        },
    )
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiMatrixTableBlock)
    assert len(blocks[0].axes) == 1
    assert blocks[0].matrix_visible_columns == ["label", "score"]


def test_matrix_summary_table_adapter_validation_missing_id():
    """EP (Validation Missing ID): Target block not found in parsed_matrices triggers exception."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="matrix_summary",
                title=I18nText(default_locale="en", translations={"en": "Summary"}),
                target_blocks=["invalid_id"],  # Missing ID in parsed_matrices
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
        synthesis_md=None,
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
            )
        },
    )
    with pytest.raises(AppException) as exc:
        MatrixSummaryTableAdapter.build(context)

    assert "requires at least 1 axes, found 0" in str(exc.value)


def test_matrix_summary_table_adapter_empty_scorecard_atoms():
    """BVA (Empty Scorecard Atoms): Provide a scorecard with an empty list of evaluated_atoms to assert it renders gracefully."""
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(default_locale="en", translations={"en": "test"}),
        layouts=[
            OutputLayoutBlock(
                preset_view="matrix_summary",
                title=I18nText(default_locale="en", translations={"en": "Table Summary"}),
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
        synthesis_md=None,
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
                evaluated_atoms=[],  # Empty atoms list
            )
        },
    )
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiMatrixTableBlock)
    assert len(blocks[0].axes) == 1
    assert blocks[0].axes[0].evaluated_atoms == []
