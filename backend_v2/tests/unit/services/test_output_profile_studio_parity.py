"""Comprehensive Unit Tests for Output Profile Studio Parity, DTOs, Prompts, and Adapters."""

import pytest

import backend_v2.models.state  # noqa: F401
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.dtos.output_profile import (
    OutputProfileCreateDTO,
    OutputProfileUpdateDTO,
)
from backend_v2.models.enums import PresetView
from backend_v2.models.prompts import (
    ANTI_JARGON_MANDATE_BLOCK,
    DEFAULT_COACHING_TONE_MANDATE,
    DEFAULT_SYNTHESIS_SYSTEM_PROMPT,
    SECTION_SYNTHESIS_DIRECTIVE_BLOCK,
    SPARSE_DATA_SYNTHESIS_MANDATE,
    STATE_ISOLATION_BLOCK,
    SYNTHESIS_CITATION_RULES_HARVARD,
    SYNTHESIS_LENGTH_CONSTRAINT,
    SYNTHESIS_SDUI_MANDATES,
)
from backend_v2.models.v2_core import (
    I18nText,
    MatrixScorecardRowDTO,
    MatrixSynthesisGroup,
)
from backend_v2.models.view.sdui import (
    MarkdownBlock,
    SduiMetrics1DBlock,
    SduiRadarChartBlock,
    SduiScatterPlotBlock,
)
from backend_v2.services.factories.output_profile_factory import build_draft_output_profile
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.matrix_graphs_adapter import MatrixGraphsAdapter
from backend_v2.services.sdui.adapters.matrix_summary_table_adapter import MatrixSummaryTableAdapter


def test_prompt_architecture_segregation() -> None:
    """Verify segregation of prompt modules and structural invariants."""
    # SDUI structural mandates
    assert "SDUI POLYMORPHIC SYNTHESIS MANDATE" in SYNTHESIS_SDUI_MANDATES
    assert "section_synthesis_directive" in SECTION_SYNTHESIS_DIRECTIVE_BLOCK
    assert "state_isolation_mandate" in STATE_ISOLATION_BLOCK

    # Qualitative coaching style and tone directives
    assert "SENIOR EXECUTIVE COACH BEHAVIORAL POSTURE" in DEFAULT_COACHING_TONE_MANDATE
    assert "ANTI-JARGON MANDATE" in ANTI_JARGON_MANDATE_BLOCK
    assert "sparse_data_synthesis_mandate" in SPARSE_DATA_SYNTHESIS_MANDATE
    assert "length_constraint" in SYNTHESIS_LENGTH_CONSTRAINT
    assert "citation_rules" in SYNTHESIS_CITATION_RULES_HARVARD
    assert "Senior Executive Coach and Strategic Evaluator" in DEFAULT_SYNTHESIS_SYSTEM_PROMPT


def test_output_profile_substantive_directives_database_sovereignty() -> None:
    """Verify that all 8 substantive directives are pre-populated in OutputProfile drafts (Database Sovereignty)."""
    profile = build_draft_output_profile(
        profile_id="prf_1234567890abcdef",
        workflow_id="wf_1234567890abcdef",
    )
    assert profile.executive_summary_directive is not None
    assert profile.matrix_1d_synthesis_directive is not None
    assert profile.matrix_2d_synthesis_directive is not None
    assert profile.matrix_3d_synthesis_directive is not None
    assert profile.matrix_text_synthesis_directive is not None
    assert profile.row_explanation_directive is not None
    assert profile.xai_synthesis_directive is not None
    assert profile.variance_synthesis_directive is not None
    assert profile.matrix_graph_length_constraint == 400


def test_output_profile_dto_put_save_with_id() -> None:
    """Verify OutputProfileUpdateDTO allows id from frontend and OutputProfileCreateDTO excludes it."""
    # Update DTO accepts client id
    update_data = {
        "id": "prf_1234567890abcdef",
        "slug": "exec_summary",
        "workflow_id": "wf_1234567890abcdef",
        "name": {"translations": {"en": "Executive Summary"}},
        "matrix_visible_columns": ["label", "distribution", "score"],
    }
    update_dto = OutputProfileUpdateDTO.model_validate(update_data)
    assert update_dto.id == "prf_1234567890abcdef"
    assert update_dto.matrix_visible_columns == ["label", "distribution", "score"]

    # Create DTO forbids id (per AST guardrail QGR011)
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        OutputProfileCreateDTO.model_validate(update_data)


def test_matrix_graphs_adapter_view_type_dispatch() -> None:
    """Verify MatrixGraphsAdapter emits correct block types according to PresetView."""
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

    # 1. 1D Metrics View
    p_1d = OutputProfile(
        id="prf_1111111111111111",
        slug="test_1d",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "1D Test"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_1111111111111111",
                title=I18nText(translations={"en": "1D Group"}),
                target_blocks=["m1"],
                view_type=PresetView.METRICS_1D,
            )
        ],
    )
    ctx_1d = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=None,
        profile=p_1d,
        profile_cache=None,
        user_name=None,
        org_name=None,
        parsed_matrices=parsed,
    )
    blocks_1d = MatrixGraphsAdapter.build(ctx_1d)
    assert len(blocks_1d) == 2
    assert isinstance(blocks_1d[1], SduiMetrics1DBlock)

    # 2. 2D Compare View
    p_2d = OutputProfile(
        id="prf_2222222222222222",
        slug="test_2d",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "2D Test"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_2222222222222222",
                title=I18nText(translations={"en": "2D Group"}),
                target_blocks=["m1", "m2"],
                view_type=PresetView.COMPARE_2D,
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
    blocks_2d = MatrixGraphsAdapter.build(ctx_2d)
    assert len(blocks_2d) == 2
    assert isinstance(blocks_2d[1], SduiScatterPlotBlock)

    # 3. 3D Radar View
    p_3d = OutputProfile(
        id="prf_3333333333333333",
        slug="test_3d",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "3D Test"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_3333333333333333",
                title=I18nText(translations={"en": "3D Group"}),
                target_blocks=["m1", "m2", "m3"],
                view_type=PresetView.MATRIX_3D,
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
    blocks_3d = MatrixGraphsAdapter.build(ctx_3d)
    assert len(blocks_3d) == 2
    assert isinstance(blocks_3d[1], SduiRadarChartBlock)

    # 4. Text-Only View
    p_text = OutputProfile(
        id="prf_4444444444444444",
        slug="test_text",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "Text Test"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_4444444444444444",
                title=I18nText(translations={"en": "Text Group"}),
                target_blocks=["m1"],
                view_type=PresetView.TEXT_ONLY,
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
    blocks_text = MatrixGraphsAdapter.build(ctx_text)
    assert len(blocks_text) == 1
    assert isinstance(blocks_text[0], MarkdownBlock)


def test_matrix_summary_table_adapter_respects_visible_columns() -> None:
    """Verify MatrixSummaryTableAdapter filters columns by profile.matrix_visible_columns."""
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
        )
    }
    custom_cols = ["label", "score"]
    profile = OutputProfile(
        id="prf_5555555555555555",
        slug="test_cols",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "Cols Test"}),
        target_block_order=[],
        matrix_visible_columns=custom_cols,
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
        parsed_matrices=parsed,
    )
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 1
    table_block = blocks[0]
    from backend_v2.models.view.sdui import SduiMatrixTableBlock

    assert isinstance(table_block, SduiMatrixTableBlock)
    assert table_block.matrix_visible_columns == custom_cols
    assert set(table_block.matrix_column_labels.keys()) == set(custom_cols)
