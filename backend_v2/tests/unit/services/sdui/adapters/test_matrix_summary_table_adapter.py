import backend_v2.models.state  # noqa: F401
from backend_v2.models.v2_core import I18nText, MatrixScorecardRowDTO, OutputProfile
from backend_v2.models.view.sdui import SduiMatrixTableBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.matrix_summary_table_adapter import MatrixSummaryTableAdapter


def test_matrix_summary_table_adapter_empty_parsed_matrices() -> None:
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
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
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 0


def test_matrix_summary_table_adapter_success() -> None:
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
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
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiMatrixTableBlock)
    assert len(blocks[0].axes) == 2
    assert "label" in blocks[0].matrix_column_labels
    assert blocks[0].matrix_column_labels["label"].resolve("en") == "Logic Matrix"
    assert blocks[0].matrix_column_labels["label"].resolve("fi") == "Logiikkamatriisi"


def test_matrix_summary_table_adapter_starved() -> None:
    from backend_v2.models.dtos.trace import DataStarvationEvent
    from backend_v2.models.v2_core import RenderedSynthesisCache

    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        target_block_order=[],
    )
    cache = RenderedSynthesisCache(
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
                row_explanation="expl 1",
            )
        },
    )
    blocks = MatrixSummaryTableAdapter.build(context)
    assert blocks == []
