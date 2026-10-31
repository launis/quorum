from __future__ import annotations

import logging

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.proposition_graph import FalsifiedClaimMatch
from backend_v2.models.domain.synthesis import RenderedSynthesisCache
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalRootCauseDiagnosisDTO,
    CausalTdaFusionResultDTO,
    FairScoringBreakdownDTO,
)
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.dtos.sdui_rules import MatrixSummaryAestheticsDTO
from backend_v2.models.dtos.trace import DataStarvationEvent
from backend_v2.models.enums import ExecutionStatus, VisualIntent
from backend_v2.models.view.sdui import SduiMatrixTableBlock
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.matrix_summary_table_adapter import (
    MATRIX_SUMMARY_RULES,
    STANDARD_COLUMNS,
    MatrixSummaryTableAdapter,
)


def test_matrix_summary_table_adapter_empty_parsed_matrices() -> None:
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
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
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        target_block_order=[],
        matrix_visible_columns=[
            "label",
            "distribution",
            "row_explanation",
            "criteria",
            "source",
            "normalized_score",
            "raw_score",
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
    assert blocks[0].matrix_column_labels["criteria"].resolve("en") == "Criteria"
    assert blocks[0].matrix_column_labels["criteria"].resolve("fi") == "Kriteeri"
    assert "source" in blocks[0].matrix_column_labels
    assert blocks[0].matrix_column_labels["source"].resolve("en") == "Source Citation"
    assert blocks[0].matrix_column_labels["source"].resolve("fi") == "Lähdeviite"


def test_matrix_summary_table_adapter_starved() -> None:
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
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


def test_output_profile_rejects_unsupported_matrix_columns_fail_fast() -> None:
    with pytest.raises(ValidationError) as exc_info:
        OutputProfile(
            id="prf_0195f3a0000070018234567890abcdef",
            slug="test",
            workflow_id="wf_123",
            name=I18nText(translations={"en": "test"}),
            target_block_order=[],
            matrix_visible_columns=[
                "label",
                "remediation_steps",
                "coaching",
                "falsification",
                "raw_score",
            ],
        )
    assert "is not a valid ReportMatrixColumn" in str(exc_info.value)


def test_matrix_summary_table_adapter_straightforward_visible_columns() -> None:
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        target_block_order=[],
        matrix_visible_columns=[
            "label",
            "raw_score",
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
    assert blocks[0].matrix_visible_columns == ["label", "raw_score"]
    assert set(blocks[0].matrix_column_labels.keys()) == {"label", "raw_score"}


def test_matrix_summary_rules_and_columns() -> None:
    """Verify MATRIX_SUMMARY_RULES export and STANDARD_COLUMNS integrity."""
    assert isinstance(MATRIX_SUMMARY_RULES, MatrixSummaryAestheticsDTO)
    assert MATRIX_SUMMARY_RULES["matrix_summary"].min_axes == 1
    assert "label" in STANDARD_COLUMNS
    assert "raw_score" in STANDARD_COLUMNS
    assert len(STANDARD_COLUMNS) == 13


def test_matrix_summary_table_adapter_empty_visible_columns_preserved() -> None:
    """Positive: empty matrix_visible_columns is preserved without falling back to STANDARD_COLUMNS."""
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        target_block_order=[],
        matrix_visible_columns=[],
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
            )
        },
    )
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 1
    assert isinstance(blocks[0], SduiMatrixTableBlock)
    assert blocks[0].matrix_visible_columns == []
    assert blocks[0].matrix_column_labels == {}


def test_matrix_summary_table_adapter_unmapped_column_fails_fast(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Negative: unmapped column in matrix_visible_columns triggers Fail-Fast AppException with VALIDATION_FAILED."""
    profile = OutputProfile.model_construct(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        target_block_order=[],
        matrix_visible_columns=["unmapped_column_xyz"],
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
            )
        },
    )
    with caplog.at_level(logging.ERROR), pytest.raises(AppException) as excinfo:
        MatrixSummaryTableAdapter.build(context)
    assert excinfo.value.details["error_code"] == "VALIDATION_FAILED"
    assert "Unknown matrix summary column: 'unmapped_column_xyz'" in excinfo.value.message
    assert any(r.exc_info is not None for r in caplog.records)


def test_matrix_summary_table_adapter_empty_column_boundary_fails_fast() -> None:
    """Negative (Boundary): empty string column identifier in matrix_visible_columns raises AppException."""
    profile = OutputProfile.model_construct(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test_empty_col",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        target_block_order=[],
        matrix_visible_columns=[""],
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
            )
        },
    )
    with pytest.raises(AppException) as excinfo:
        MatrixSummaryTableAdapter.build(context)
    assert excinfo.value.details["error_code"] == "VALIDATION_FAILED"
    assert "Unknown matrix summary column: ''" in excinfo.value.message


def test_matrix_summary_table_adapter_short_circuit_and_falsification_lineage() -> None:
    """Positive: populates short_circuited_by_claims and falsified_warrant_claims from N_A atoms and causal fusion."""
    profile = OutputProfile(
        id="prf_0195f3a0000070018234567890abcdef",
        slug="test",
        workflow_id="wf_123",
        name=I18nText(translations={"en": "test"}),
        target_block_order=[],
        matrix_visible_columns=["label", "raw_score"],
    )
    logic = ReasoningStepDTO(
        step_1_identify_premise="p",
        step_2_scan_source="s",
        step_3_evaluate_anti_patterns="a",
        step_4_final_conclusion="c",
    )
    na_atom_with_reason = ScorecardAtomDTO(
        atom_id="tda_0195f3a0000070018234567890abcde1",
        level=2,
        level_name="Level 2",
        claim_label="Advanced metric claim",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=logic,
        status=ExecutionStatus.N_A,
        semantic_reasoning="Blocked by foundational failure",
        contextual_override=False,
        chart_display_label="L2",
        visual_intent=VisualIntent.NEUTRAL,
    )
    na_atom_redundant_reason = ScorecardAtomDTO(
        atom_id="tda_0195f3a0000070018234567890abcde2",
        level=3,
        level_name="Level 3",
        claim_label="Self-contained N_A claim",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=logic,
        status=ExecutionStatus.N_A,
        semantic_reasoning="Self-contained",
        contextual_override=False,
        chart_display_label="L3",
        visual_intent=VisualIntent.NEUTRAL,
    )
    passed_atom = ScorecardAtomDTO(
        atom_id="tda_0195f3a0000070018234567890abcde3",
        level=1,
        level_name="Level 1",
        claim_label="Passed claim",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=logic,
        status=ExecutionStatus.PASSED,
        semantic_reasoning="Passed",
        contextual_override=False,
        chart_display_label="L1",
        visual_intent=VisualIntent.NEUTRAL,
    )

    rebuttal_node_id = "nod_0195f3a0000070018234567890abcde1"
    warrant_node_id = "nod_0195f3a0000070018234567890abcde2"
    claim_node_id = "nod_0195f3a0000070018234567890abcde3"
    unmapped_rebuttal_id = "nod_0195f3a0000070018234567890abcde4"
    unmapped_warrant_id = "nod_0195f3a0000070018234567890abcde5"

    causal_result = CausalTdaFusionResultDTO(
        graph=CausalGraphPayloadDTO(
            nodes=[
                CausalNodeDTO(
                    node_id=rebuttal_node_id,
                    claim="Empirical counter-evidence",
                    status=ExecutionStatus.PASSED,
                ),
                CausalNodeDTO(
                    node_id=warrant_node_id,
                    claim="Assumed linear growth warrant",
                    status=ExecutionStatus.FAILED,
                ),
            ],
            edges=[],
        ),
        root_cause_diagnoses=[
            CausalRootCauseDiagnosisDTO(
                failing_node_id=warrant_node_id,
                root_cause_parent_id=rebuttal_node_id,
                paragraph_ref="P1",
                explanation="Root flaw",
                penalty_points=1.0,
                root_cause_claim="Root cause prerequisite failure",
            ),
            CausalRootCauseDiagnosisDTO(
                failing_node_id=warrant_node_id,
                root_cause_parent_id=rebuttal_node_id,
                paragraph_ref="P1",
                explanation="Duplicate root flaw",
                penalty_points=1.0,
                root_cause_claim="Root cause prerequisite failure",
            ),
        ],
        anti_fluff_audit=AntiFluffAuditDTO(
            isolated_concept_count=0,
            cycle_detected=False,
            unsupported_claims_count=0,
            logical_cohesion_score=0.9,
        ),
        prescriptive_remediations=[],
        fair_scoring=FairScoringBreakdownDTO(
            independent_error_count=1,
            cascading_fault_count=1,
            raw_penalty_points=2.0,
            deduplicated_penalty_points=1.0,
            dampened_savings_points=1.0,
        ),
        falsified_claims=[
            FalsifiedClaimMatch(
                rebuttal_id=rebuttal_node_id,
                invalidated_warrant_id=warrant_node_id,
                falsified_claim_id=claim_node_id,
                rebuttal_confidence=0.95,
                claim_statement="Target conclusion claim",
            ),
            FalsifiedClaimMatch(
                rebuttal_id=unmapped_rebuttal_id,
                invalidated_warrant_id=unmapped_warrant_id,
                falsified_claim_id=claim_node_id,
                rebuttal_confidence=0.85,
                claim_statement="Fallback ID conclusion claim",
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
                name="M1",
                score=3.0,
                scale_min=1.0,
                scale_max=5.0,
                is_evaluative=True,
                label_i18n=I18nText(translations={"en": "M1"}),
                row_explanation="expl 1",
                evaluated_atoms=[
                    na_atom_with_reason,
                    na_atom_with_reason,
                    na_atom_redundant_reason,
                    passed_atom,
                ],
            )
        },
        causal_result=causal_result,
    )

    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 1
    block = blocks[0]
    assert isinstance(block, SduiMatrixTableBlock)
    assert block.short_circuited_by_claims == [
        "Advanced metric claim: Blocked by foundational failure",
        "Self-contained N_A claim",
        "Root cause prerequisite failure",
    ]
    assert block.falsified_warrant_claims == [
        "Empirical counter-evidence -> Assumed linear growth warrant -> Target conclusion claim",
        f"{unmapped_rebuttal_id} -> {unmapped_warrant_id} -> Fallback ID conclusion claim",
    ]

