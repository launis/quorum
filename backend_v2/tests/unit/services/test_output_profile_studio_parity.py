"""Comprehensive Unit Tests for Output Profile Studio Parity, DTOs, Prompts, and Adapters."""

import pytest

from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.synthesis import MatrixSynthesisGroup
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO
from backend_v2.models.dtos.output_profile import (
    OutputProfileCreateDTO,
    OutputProfileUpdateDTO,
)
from backend_v2.models.enums import PresetView
from backend_v2.models.prompts import (
    ANTI_JARGON_MANDATE_BLOCK,
    SECTION_SYNTHESIS_DIRECTIVE_BLOCK,
    SPARSE_DATA_SYNTHESIS_MANDATE,
    STATE_ISOLATION_BLOCK,
    SYNTHESIS_CITATION_RULES_HARVARD,
    SYNTHESIS_SDUI_MANDATES,
    SYNTHESIS_SYSTEM_PROMPT,
)
from backend_v2.models.view.sdui import (
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
    assert "ANTI-JARGON MANDATE" in ANTI_JARGON_MANDATE_BLOCK
    assert "sparse_data_synthesis_mandate" in SPARSE_DATA_SYNTHESIS_MANDATE
    assert "citation_rules" in SYNTHESIS_CITATION_RULES_HARVARD
    assert "Strategic Report Evaluator" in SYNTHESIS_SYSTEM_PROMPT


def test_output_profile_substantive_directives_database_sovereignty() -> None:
    """Verify that all 8 substantive directives are pre-populated in OutputProfile drafts (Database Sovereignty)."""
    profile = build_draft_output_profile(
        profile_id="prf_0195f3a0000070018234567890abcdef",
        workflow_id="wf_0195f3a0000070018234567890abcdef",
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
        "id": "prf_0195f3a0000070018234567890abcdef",
        "slug": "exec_summary",
        "workflow_id": "wf_0195f3a0000070018234567890abcdef",
        "name": {"translations": {"en": "Executive Summary"}},
        "matrix_visible_columns": ["label", "distribution", "raw_score"],
    }
    update_dto = OutputProfileUpdateDTO.model_validate(update_data)
    assert update_dto.id == "prf_0195f3a0000070018234567890abcdef"
    assert update_dto.matrix_visible_columns == ["label", "distribution", "raw_score"]

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
        id="prf_0195f3a0000070018111111111111111",
        slug="test_1d",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "1D Test"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070018111111111111111",
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
    assert len(blocks_1d) == 1
    assert isinstance(blocks_1d[0], SduiMetrics1DBlock)

    # 2. 2D Compare View
    p_2d = OutputProfile(
        id="prf_0195f3a0000070028222222222222222",
        slug="test_2d",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "2D Test"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070028222222222222222",
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
    assert len(blocks_2d) == 1
    assert isinstance(blocks_2d[0], SduiScatterPlotBlock)

    # 3. 3D Radar View
    p_3d = OutputProfile(
        id="prf_0195f3a0000070038333333333333333",
        slug="test_3d",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "3D Test"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070038333333333333333",
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
    assert len(blocks_3d) == 1
    assert isinstance(blocks_3d[0], SduiRadarChartBlock)

    # 4. Text-Only View
    p_text = OutputProfile(
        id="prf_0195f3a0000070048444444444444444",
        slug="test_text",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "Text Test"}),
        target_block_order=[],
        matrix_synthesis_groups=[
            MatrixSynthesisGroup(
                id="grp_0195f3a0000070048444444444444444",
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
    assert len(blocks_text) == 0


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
    custom_cols = ["label", "raw_score"]
    profile = OutputProfile(
        id="prf_0195f3a0000070058555555555555555",
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


def test_all_seed_output_profiles_variance_dynamic_scale_parity() -> None:
    """Parameterized test verifying all OutputProfiles in seed_data.json have dynamic scale parity."""
    import json
    from pathlib import Path

    from pydantic import TypeAdapter

    from backend_v2.models.domain.execution import ExecutionRecord
    from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock, PromptBlockAdapter
    from backend_v2.models.domain.synthesis import RenderedSynthesisCache
    from backend_v2.models.dtos.atom_result import ExtensionMetricsDTO
    from backend_v2.models.enums import XaiExtensionType
    from backend_v2.models.execution_core import ExecutionMetadata
    from backend_v2.models.view.sdui import SduiGridBlock, SduiQuadrantMatrixBlock
    from backend_v2.services.sdui.adapters.variance_adapter import VarianceAdapter

    seed_path = Path("backend_v2/seed/seed_data.json")
    assert seed_path.exists(), "seed_data.json must exist"
    with open(seed_path, encoding="utf-8") as f:
        data = json.load(f)

    profiles = TypeAdapter(list[OutputProfile]).validate_python(data["output_profiles"])
    assert len(profiles) > 0, "No output profiles found in seed_data.json"

    # Build prompt blocks lookup map
    prompt_blocks = {}
    for raw_pb in data["prompt_blocks"]:
        pb = PromptBlockAdapter.validate_python(raw_pb)
        prompt_blocks[pb.id] = pb

    for prof in profiles:
        has_variance = (
            XaiExtensionType.VARIANCE_VALIDATION in prof.visible_workflow_extensions
            or "variance_validation_block" in prof.target_block_order
        )

        if not has_variance:
            # Verify profiles without variance validation do not emit spurious variance blocks
            ctx = AdapterContext(
                execution=None,
                locale="en",
                penalties_applied=[],
                mcp_audit_map=None,
                global_score=None,
                profile=prof,
                profile_cache=None,
                user_name=None,
                org_name=None,
                parsed_matrices={},
            )
            blocks = VarianceAdapter.build(ctx)
            assert len(blocks) == 0, (
                f"Profile '{prof.id}' without variance validation emitted spurious blocks: {blocks}"
            )
            continue

        # For profiles where variance validation is enabled:
        assert prof.variance_target_block, f"Profile '{prof.id}' has variance active but variance_target_block is empty"
        assert prof.variance_target_block in prompt_blocks, (
            f"Profile '{prof.id}' variance_target_block '{prof.variance_target_block}' not found in seed vault"
        )

        target_pb = prompt_blocks[prof.variance_target_block]
        assert isinstance(target_pb, MatrixPromptBlock), (
            f"Target block '{prof.variance_target_block}' must be a MatrixPromptBlock, got {type(target_pb)}"
        )
        assert target_pb.computed_max is not None and target_pb.computed_max > 0, (
            f"Target block '{prof.variance_target_block}' has invalid computed_max: {target_pb.computed_max}"
        )

        expected_scale_max = float(target_pb.computed_max)
        expected_scale_min = float(target_pb.computed_min or 1.0)

        # Build mock evaluation record and parsed_matrices
        score_val = (expected_scale_min + expected_scale_max) / 2.0
        parsed_mat = {
            prof.variance_target_block: MatrixScorecardRowDTO(
                block_id=prof.variance_target_block,
                name="Target Matrix",
                score=score_val,
                scale_min=expected_scale_min,
                scale_max=expected_scale_max,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "Target Matrix"}),
                row_explanation="Evaluated target matrix",
            )
        }
        cache = RenderedSynthesisCache(
            extension_metrics=ExtensionMetricsDTO(
                authenticity_score=score_val,
                performative_phrases_count=0.0,
                variance_score=0.1,
                alignment_verdict="ALIGNED",
            ),
        )
        exec_rec = ExecutionRecord(
            id="exe_0195f3a00000700283456789abcdef01",
            workflow_id=prof.workflow_id,
            output_profile_id=prof.id,
            execution_trace=[],
            context_variables={},
            target_locale="en",
            metadata=ExecutionMetadata(),
        )
        ctx = AdapterContext(
            execution=exec_rec,
            locale="en",
            penalties_applied=[],
            mcp_audit_map=None,
            global_score=None,
            profile=prof,
            profile_cache=cache,
            user_name=None,
            org_name=None,
            parsed_matrices=parsed_mat,
        )

        blocks = VarianceAdapter.build(ctx)
        assert len(blocks) > 0, f"Profile '{prof.id}' failed to emit variance blocks"

        # Assert scale extrema dynamically anchored to target matrix's true extrema
        quadrant = next((b for b in blocks if isinstance(b, SduiQuadrantMatrixBlock)), None)
        assert quadrant is not None, f"Profile '{prof.id}' did not emit SduiQuadrantMatrixBlock"
        cog_axis = quadrant.axes[0]
        assert cog_axis.scale_max == expected_scale_max
        assert cog_axis.scale_min == expected_scale_min

        grid = next((b for b in blocks if isinstance(b, SduiGridBlock)), None)
        assert grid is not None, f"Profile '{prof.id}' did not emit SduiGridBlock"
        # If scale_max is not 3.0 (e.g. HACM scale is 5.0), verify no hardcoded '/ 3.0'
        if expected_scale_max != 3.0:
            assert f"/ {expected_scale_max:.1f}" in grid.items[1].text
            assert "/ 3.0" not in grid.items[1].text
