from __future__ import annotations

import backend_v2.models.state  # noqa: F401
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.sdui_rules import MatrixSummaryAestheticsDTO
from backend_v2.models.view.sdui import SduiMatrixTableBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.matrix_summary_table_adapter import (
    MATRIX_SUMMARY_RULES,
    STANDARD_COLUMNS,
    MatrixSummaryTableAdapter,
)



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
        matrix_visible_columns=[
            "label",
            "distribution",
            "row_explanation",
            "criteria",
            "quotes",
            "source",
            "normalized_score",
            "score",
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
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiMatrixTableBlock)
    assert len(blocks[0].axes) == 2
    assert "label" in blocks[0].matrix_column_labels
    assert blocks[0].matrix_column_labels["label"].resolve("en") == "Logic Matrix"
    assert blocks[0].matrix_column_labels["label"].resolve("fi") == "Logiikkamatriisi"
    assert "criteria" in blocks[0].matrix_column_labels
    assert blocks[0].matrix_column_labels["criteria"].resolve("en") == "Criterion"
    assert blocks[0].matrix_column_labels["criteria"].resolve("fi") == "Kriteeri"
    assert "quotes" in blocks[0].matrix_column_labels
    assert blocks[0].matrix_column_labels["quotes"].resolve("en") == "Text Observation"
    assert blocks[0].matrix_column_labels["quotes"].resolve("fi") == "Tekstin havainto"
    assert "source" in blocks[0].matrix_column_labels
    assert blocks[0].matrix_column_labels["source"].resolve("en") == "Citation"
    assert blocks[0].matrix_column_labels["source"].resolve("fi") == "Lähdeviite"


def test_matrix_summary_table_adapter_starved() -> None:
    from backend_v2.models.domain.synthesis import RenderedSynthesisCache
    from backend_v2.models.dtos.trace import DataStarvationEvent

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


def test_matrix_summary_table_adapter_filters_unsupported_columns() -> None:
    profile = OutputProfile(
        id="prf_1234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        target_block_order=[],
        matrix_visible_columns=[
            "label",
            "remediation_steps",
            "coaching",
            "falsification",
            "score",
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
            )
        },
    )
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiMatrixTableBlock)
    assert blocks[0].matrix_visible_columns == ["label", "score"]
    assert set(blocks[0].matrix_column_labels.keys()) == {"label", "score"}


def test_matrix_summary_rules_and_columns() -> None:
    """Verify MATRIX_SUMMARY_RULES export and STANDARD_COLUMNS integrity."""
    assert isinstance(MATRIX_SUMMARY_RULES, MatrixSummaryAestheticsDTO)
    assert MATRIX_SUMMARY_RULES["matrix_summary"].min_axes == 1
    assert "label" in STANDARD_COLUMNS
    assert "score" in STANDARD_COLUMNS
    assert len(STANDARD_COLUMNS) == 9

