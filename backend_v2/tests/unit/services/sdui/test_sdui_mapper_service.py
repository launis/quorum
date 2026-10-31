"""Unit tests for relocated SduiMapperService at canonical path."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText, generate_opaque_id
from backend_v2.models.domain.output_profile import OutputProfile
from backend_v2.models.domain.proposition_graph import FalsifiedClaimMatch
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalEdgeDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalRootCauseDiagnosisDTO,
    CausalTdaFusionResultDTO,
    FairScoringBreakdownDTO,
)
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.dtos.quote_evidence import QuoteEvidenceDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import (
    EntityPrefix,
    ExecutionStatus,
    SDUIComponentType,
    VisualIntent,
)
from backend_v2.models.view.sdui import (
    ReportView,
    SduiCausalGraphBlock,
    SduiMatrixSummaryTableBlock,
    SduiMatrixTableBlock,
    SduiNACard,
    SduiQuoteCard,
    SduiWarningCard,
)
from backend_v2.services.sdui.adapters.base_adapter import AdapterContext
from backend_v2.services.sdui.adapters.causal_graph_adapter import CausalGraphAdapter
from backend_v2.services.sdui.adapters.matrix_summary_table_adapter import MatrixSummaryTableAdapter
from backend_v2.services.sdui.sdui_mapper_service import SduiMapperService

__all__ = [
    "test_causal_graph_adapter_null_causal_result_raises",
    "test_causal_graph_adapter_populates_falsified_warrant_claims",
    "test_matrix_summary_table_adapter_populates_short_circuited_by_claims",
    "test_matrix_summary_table_adapter_unknown_column_raises",
    "test_sdui_mapper_service_canonical_import_and_evidence_mapping",
    "test_sdui_mapper_service_empty_short_circuits_produces_empty_list",
    "test_sdui_mapper_service_legacy_root_import_fails_fast",
    "test_sdui_mapper_service_map_evidence_empty_lang_raises",
    "test_sdui_mapper_service_map_report_empty_execution_id_raises",
    "test_sdui_mapper_service_map_report_empty_lang_raises",
    "test_sdui_mapper_service_map_report_success_and_warning",
    "test_sdui_mapper_service_map_report_with_na_cards_and_override",
    "test_sdui_mapper_service_unverified_evidence_warning_card",
    "test_sdui_matrix_row_extra_field_raises_validation_error",
]


def test_sdui_mapper_service_canonical_import_and_evidence_mapping() -> None:
    """Verify SduiMapperService functions correctly from canonical path."""
    mapper = SduiMapperService()
    evidence = QuoteEvidenceDTO.model_validate(
        {"source_quotes": "Direct quote from source.", "source_alias": "DOC-1"},
        context={"alias_registry": {"DOC-1": "opaque_source_1"}},
    )
    card = mapper.map_evidence_to_sdui(evidence, lang="en")
    assert isinstance(card, SduiQuoteCard)
    assert card.quote == "Direct quote from source."
    assert card.source_aliases == ["opaque_source_1"]


def test_sdui_mapper_service_unverified_evidence_warning_card() -> None:
    """Verify unverified quote evidence maps to SduiWarningCard."""
    mapper = SduiMapperService()
    evidence = QuoteEvidenceDTO.model_validate(
        {"source_quotes": "Unverified claim.", "source_alias": "UNKNOWN-ALIAS"},
        context={"alias_registry": {"DOC-1": "opaque_source_1"}},
    )
    card = mapper.map_evidence_to_sdui(evidence, lang="en")
    assert isinstance(card, SduiWarningCard)
    assert "Hallucinated citations detected:" in card.message


def test_sdui_mapper_service_legacy_root_import_fails_fast() -> None:
    """Scenario NEG-14: Importing from deleted root path raises ModuleNotFoundError."""
    with pytest.raises(ModuleNotFoundError):
        __import__("backend_v2.services.sdui_mapper_service")


def test_sdui_mapper_service_map_report_success_and_warning() -> None:
    """Verify map_report_to_sdui maps ReportDataDTO to ReportView with success/warning themes."""
    mapper = SduiMapperService()

    report_success = ReportDataDTO(
        workflow_id="wf_test",
        execution_id="exe_test_1",
        profile_id="prf_test",
        global_score=92.5,
        strictness_level=50,
        has_warning=False,
    )
    view_success = mapper.map_report(report_success)
    assert isinstance(view_success, ReportView)
    assert view_success.view_id == "exe_test_1"
    assert view_success.status_theme == VisualIntent.SUCCESS
    assert view_success.metrics is not None
    assert view_success.metrics.global_score == 92.5
    assert view_success.metrics.strictness_level == 50

    report_warning = ReportDataDTO(
        workflow_id="wf_test",
        execution_id="exe_test_2",
        profile_id="prf_test",
        has_warning=True,
    )
    view_warning = mapper.map_report_to_sdui(report_warning)
    assert view_warning.status_theme == VisualIntent.WARNING


def test_sdui_mapper_service_map_report_with_na_cards_and_override() -> None:
    """Verify map_report_to_sdui anchors N_A outcomes inline onto SduiMatrixTableBlock without bottom orphans."""
    mapper = SduiMapperService()

    hydrated_eval = HydratedAtomDTO(
        sdui_component=SDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Evaluated metric",
    )
    hydrated_atom = HydratedAtomDTO(
        sdui_component=SDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Prerequisite metric satisfied",
    )
    result_na = AtomResultDTO(
        tda_id="tda_eval_1",
        status=ExecutionStatus.N_A,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=["tda_prereq_1"],
    )
    result_na_default = AtomResultDTO(
        tda_id="tda_eval_1",
        status=ExecutionStatus.N_A,
        extensions={},
        depends_on_tda_ids=[],
        short_circuit_reason_tda_ids=[],
    )

    matrix_block = SduiMatrixTableBlock(axes=[])
    report = ReportDataDTO(
        workflow_id="wf_test",
        execution_id="exe_original",
        profile_id="prf_test",
        inner_sdui_blocks=[matrix_block],
        results=[result_na, result_na_default],
        hydrated_references={"tda_eval_1": hydrated_eval, "tda_prereq_1": hydrated_atom},
    )

    view = mapper.map_report_to_sdui(report, execution_id="exe_override", lang="en")
    assert view.view_id == "exe_override"
    assert len(view.inner_sdui_blocks) == 1
    assert not any(isinstance(b, SduiNACard) for b in view.inner_sdui_blocks)
    updated_table = view.inner_sdui_blocks[0]
    assert isinstance(updated_table, SduiMatrixTableBlock)
    assert "Skipped based on rule: Prerequisite metric satisfied" in updated_table.short_circuited_by_claims
    assert "Not applicable (N/A)" in updated_table.short_circuited_by_claims


def test_matrix_summary_table_adapter_populates_short_circuited_by_claims() -> None:
    """Verify MatrixSummaryTableAdapter and SduiMapperService populate short_circuited_by_claims."""
    profile_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    block_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
    profile = OutputProfile(
        id=profile_id,
        slug="test_profile",
        workflow_id="wf_test",
        name=I18nText(translations={"en": "Test Profile", "fi": "Testiprofiili"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        target_block_order=[],
        matrix_visible_columns=["label", "raw_score"],
    )
    rebuttal_id = generate_opaque_id(EntityPrefix.NODE)
    warrant_id = generate_opaque_id(EntityPrefix.NODE)
    claim_id = generate_opaque_id(EntityPrefix.NODE)
    row = MatrixScorecardRowDTO(
        block_id=block_id,
        name="Axis 1",
        label_i18n=I18nText(translations={"en": "Axis 1", "fi": "Akseli 1"}),
        score=2.0,
        scale_min=1.0,
        scale_max=5.0,
        row_explanation="Short-circuited row.",
        ui_plot_ratio=0.25,
        is_evaluative=True,
        evaluated_atoms=[
            ScorecardAtomDTO(
                atom_id="a1",
                level=1,
                level_name="Level 1",
                claim_label="Prerequisite Claim A",
                extracted_facts={},
                exact_quotes=[],
                internal_logic_en=ReasoningStepDTO(
                    step_1_identify_premise="P",
                    step_2_scan_source="E",
                    step_3_evaluate_anti_patterns="I",
                    step_4_final_conclusion="C",
                ),
                status=ExecutionStatus.N_A,
                semantic_reasoning="Failed verification",
                contextual_override=False,
                chart_display_label="L1",
                visual_intent=VisualIntent.WARNING,
            )
        ],
    )
    fusion = CausalTdaFusionResultDTO(
        graph=CausalGraphPayloadDTO(
            nodes=[
                CausalNodeDTO(node_id=rebuttal_id, claim="Rebuttal R1", status=ExecutionStatus.PASSED),
                CausalNodeDTO(node_id=warrant_id, claim="Warrant W1", status=ExecutionStatus.FAILED),
                CausalNodeDTO(node_id=claim_id, claim="Claim C1", status=ExecutionStatus.FAILED),
            ],
            edges=[CausalEdgeDTO(source_id=rebuttal_id, target_id=claim_id, reasoning="Warrant W1")],
            root_cause_node_ids=[rebuttal_id],
        ),
        root_cause_diagnoses=[
            CausalRootCauseDiagnosisDTO(
                failing_node_id=claim_id,
                root_cause_parent_id=rebuttal_id,
                paragraph_ref="P1",
                explanation="Falsified via rebuttal.",
                penalty_points=5.0,
                root_cause_claim="Root Blocker Claim",
                failing_node_claim="Claim C1",
                warrant_relation="rebuts",
            )
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
            cascading_fault_count=0,
            raw_penalty_points=5.0,
            deduplicated_penalty_points=5.0,
            dampened_savings_points=0.0,
        ),
        total_deliverable_nodes=3,
        falsified_claims=[
            FalsifiedClaimMatch(
                rebuttal_id=rebuttal_id,
                invalidated_warrant_id=warrant_id,
                falsified_claim_id=claim_id,
                rebuttal_confidence=0.95,
                claim_statement="Claim C1",
            )
        ],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=50.0,
        profile=profile,
        profile_cache=None,
        user_name="Tester",
        org_name="Org",
        parsed_matrices={block_id: row},
        causal_result=fusion,
    )
    blocks = MatrixSummaryTableAdapter.build(context)
    assert len(blocks) == 1
    table_block = blocks[0]
    assert isinstance(table_block, SduiMatrixSummaryTableBlock)
    assert "Prerequisite Claim A: Failed verification" in table_block.short_circuited_by_claims
    assert "Root Blocker Claim" in table_block.short_circuited_by_claims
    assert "Rebuttal R1 -> Warrant W1 -> Claim C1" in table_block.falsified_warrant_claims

    report_dto = ReportDataDTO(
        workflow_id="wf_test",
        execution_id="exe_test",
        profile_id=profile_id,
        inner_sdui_blocks=[SduiMatrixSummaryTableBlock(axes=[row])],
        short_circuited_by_claims=["Prerequisite Claim A: Failed verification"],
    )
    mapped_view = SduiMapperService().map_report_to_sdui(report_dto, lang="en")
    mapped_block = mapped_view.inner_sdui_blocks[0]
    assert isinstance(mapped_block, SduiMatrixSummaryTableBlock)
    assert mapped_block.short_circuited_by_claims == ["Prerequisite Claim A: Failed verification"]


def test_causal_graph_adapter_populates_falsified_warrant_claims() -> None:
    """Verify CausalGraphAdapter populates formatted falsified_warrant_claims on block and nodes."""
    profile_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    rebuttal_id = generate_opaque_id(EntityPrefix.NODE)
    warrant_id = generate_opaque_id(EntityPrefix.NODE)
    claim_id = generate_opaque_id(EntityPrefix.NODE)
    profile = OutputProfile(
        id=profile_id,
        slug="test_profile",
        workflow_id="wf_test",
        name=I18nText(translations={"en": "Test Profile", "fi": "Testiprofiili"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        target_block_order=[],
    )
    node_c1 = CausalNodeDTO(
        node_id=claim_id,
        claim="Claim C1",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=[rebuttal_id],
    )
    node_w1 = CausalNodeDTO(
        node_id=warrant_id,
        claim="Warrant W1",
        status=ExecutionStatus.FAILED,
    )
    node_r1 = CausalNodeDTO(
        node_id=rebuttal_id,
        claim="Rebuttal R1",
        status=ExecutionStatus.PASSED,
    )
    graph = CausalGraphPayloadDTO(
        nodes=[node_r1, node_w1, node_c1],
        edges=[CausalEdgeDTO(source_id=rebuttal_id, target_id=claim_id, reasoning="Warrant W1")],
        root_cause_node_ids=[rebuttal_id],
    )
    fusion = CausalTdaFusionResultDTO(
        graph=graph,
        root_cause_diagnoses=[
            CausalRootCauseDiagnosisDTO(
                failing_node_id=claim_id,
                root_cause_parent_id=rebuttal_id,
                paragraph_ref="P1",
                explanation="Falsified via rebuttal.",
                penalty_points=5.0,
                root_cause_claim="Rebuttal R1",
                failing_node_claim="Claim C1",
                warrant_relation="rebuts",
            )
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
            cascading_fault_count=0,
            raw_penalty_points=5.0,
            deduplicated_penalty_points=5.0,
            dampened_savings_points=0.0,
        ),
        total_deliverable_nodes=3,
        falsified_claims=[
            FalsifiedClaimMatch(
                rebuttal_id=rebuttal_id,
                invalidated_warrant_id=warrant_id,
                falsified_claim_id=claim_id,
                rebuttal_confidence=0.95,
                claim_statement="Claim C1",
            )
        ],
    )
    ctx = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=80.0,
        profile=profile,
        profile_cache=None,
        user_name="Tester",
        org_name="Org",
        causal_result=fusion,
    )
    blocks = CausalGraphAdapter.build(ctx)
    assert len(blocks) == 1
    causal_block = blocks[0]
    assert isinstance(causal_block, SduiCausalGraphBlock)
    expected_entry = "Rebuttal R1 -> Warrant W1 -> Claim C1"
    assert expected_entry in causal_block.falsified_warrant_claims
    assert "Rebuttal R1" in causal_block.short_circuited_by_claims
    matching_nodes = [n for n in causal_block.critical_path_nodes if n.node_id == claim_id]
    assert len(matching_nodes) == 1
    assert expected_entry in matching_nodes[0].falsified_warrant_claims
    assert "Rebuttal R1" in matching_nodes[0].short_circuited_by_claims


def test_sdui_mapper_service_empty_short_circuits_produces_empty_list() -> None:
    """Verify zero N_A atoms and zero falsified claims produce empty lists and zero SduiNACard orphans."""
    mapper = SduiMapperService()
    matrix_block = SduiMatrixSummaryTableBlock(axes=[])
    report = ReportDataDTO(
        workflow_id="wf_test",
        execution_id="exe_empty",
        profile_id="prf_test",
        inner_sdui_blocks=[matrix_block],
        results=[],
        hydrated_references={},
    )
    view = mapper.map_report_to_sdui(report, lang="en")
    assert len(view.inner_sdui_blocks) == 1
    assert not any(isinstance(b, SduiNACard) for b in view.inner_sdui_blocks)
    first_block = view.inner_sdui_blocks[0]
    assert isinstance(first_block, SduiMatrixSummaryTableBlock)
    assert first_block.short_circuited_by_claims == []
    assert first_block.falsified_warrant_claims == []


def test_sdui_matrix_row_extra_field_raises_validation_error() -> None:
    """Verify SduiMatrixSummaryTableBlock rejects unrecognized fields under extra='forbid'."""
    with pytest.raises(ValidationError):
        SduiMatrixSummaryTableBlock.model_validate(
            {
                "block_type": "matrix_summary",
                "axes": [],
                "unrecognized_extra_field": "forbidden",
            }
        )


def test_matrix_summary_table_adapter_unknown_column_raises() -> None:
    """Verify MatrixSummaryTableAdapter raises AppException on unknown matrix_visible_columns entry."""
    profile_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    block_id = generate_opaque_id(EntityPrefix.PROMPT_BLOCK)
    profile = OutputProfile.model_construct(
        id=profile_id,
        slug="test_profile",
        workflow_id="wf_test",
        name=I18nText(translations={"en": "Test Profile", "fi": "Testiprofiili"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        target_block_order=[],
        matrix_visible_columns=["invalid_column_key"],
    )
    row = MatrixScorecardRowDTO(
        block_id=block_id,
        name="Axis 1",
        label_i18n=I18nText(translations={"en": "Axis 1", "fi": "Akseli 1"}),
        score=2.0,
        scale_min=1.0,
        scale_max=5.0,
        row_explanation="Test explanation.",
        ui_plot_ratio=0.25,
        is_evaluative=True,
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=50.0,
        profile=profile,
        profile_cache=None,
        user_name="Tester",
        org_name="Org",
        parsed_matrices={block_id: row},
    )
    with pytest.raises(AppException) as exc_info:
        MatrixSummaryTableAdapter.build(context)
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_causal_graph_adapter_null_causal_result_raises() -> None:
    """Verify CausalGraphAdapter.build_action_card raises AppException when causal_result is None."""
    profile_id = generate_opaque_id(EntityPrefix.OUTPUT_PROFILE)
    profile = OutputProfile(
        id=profile_id,
        slug="test_profile",
        workflow_id="wf_test",
        name=I18nText(translations={"en": "Test Profile", "fi": "Testiprofiili"}),
        description=I18nText(translations={"en": "Desc", "fi": "Kuvaus"}),
        target_block_order=[],
    )
    context = AdapterContext(
        execution=None,
        locale="en",
        penalties_applied=[],
        mcp_audit_map=None,
        global_score=50.0,
        profile=profile,
        profile_cache=None,
        user_name="Tester",
        org_name="Org",
        causal_result=None,
    )
    with pytest.raises(AppException) as exc_info:
        CausalGraphAdapter.build_action_card(context)
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_sdui_mapper_service_map_evidence_empty_lang_raises() -> None:
    """Verify map_evidence_to_sdui raises AppException when lang is empty or whitespace."""
    mapper = SduiMapperService()
    evidence = QuoteEvidenceDTO.model_validate(
        {"source_quotes": "Direct quote from source.", "source_alias": "DOC-1"},
        context={"alias_registry": {"DOC-1": "opaque_source_1"}},
    )
    with pytest.raises(AppException) as exc_info:
        mapper.map_evidence_to_sdui(evidence, lang="   ")
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_sdui_mapper_service_map_report_empty_lang_raises() -> None:
    """Verify map_report_to_sdui raises AppException when lang is empty or whitespace."""
    mapper = SduiMapperService()
    report = ReportDataDTO(
        workflow_id="wf_test",
        execution_id="exe_test_1",
        profile_id="prf_test",
    )
    with pytest.raises(AppException) as exc_info:
        mapper.map_report_to_sdui(report, lang="")
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value


def test_sdui_mapper_service_map_report_empty_execution_id_raises() -> None:
    """Verify map_report_to_sdui raises AppException when resolved execution_id is empty."""
    mapper = SduiMapperService()
    report = ReportDataDTO(
        workflow_id="wf_test",
        execution_id="   ",
        profile_id="prf_test",
    )
    with pytest.raises(AppException) as exc_info:
        mapper.map_report_to_sdui(report, execution_id="  ", lang="en")
    assert exc_info.value.status_code == 400
    assert exc_info.value.details["error_code"] == ErrorCodes.VALIDATION_FAILED.value
