"""Unit tests for atom row and denormalized flat row dataset builders in the export domain."""

from __future__ import annotations

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.prompt_blocks import MatrixPromptBlock
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.atom_result import AtomResultDTO, HydratedAtomDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalTdaFusionResultDTO,
    FairScoringBreakdownDTO,
)
from backend_v2.models.dtos.matrix_scorecard import MatrixScorecardRowDTO, ScorecardAtomDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import ExecutionStatus, SDUIComponentType, VisualIntent
from backend_v2.services.export.atom_row_builder import (
    build_atom_rows,
    build_denormalized_rows,
)
from backend_v2.services.export_service import ExportService
from backend_v2.services.localization import LocalizationService


def _create_sample_blocks_and_matrices() -> tuple[
    dict[str, MatrixPromptBlock],
    list[MatrixScorecardRowDTO],
    dict[str, str],
    ReportDataDTO,
    CausalTdaFusionResultDTO,
]:
    tda_id = "tda_0123456789abcdef0123456789abcdef"
    blk_id = "blk_0123456789abcdef0123456789abcdef"

    assertion = TDAAssertion(
        tda_id=tda_id,
        concept_description="Concept definition for TDA 1",
        aggregation_mode="EXISTS",
        inverse_evidence=False,
    )
    claim = MatrixClaim(
        label=I18nText(translations={"fi": "Kriteeri 1", "en": "Criterion 1"}),
        tda_assertions=[assertion],
    )
    scale = MatrixScale(
        score=5,
        ai_label="Level 5",
        name=I18nText(translations={"fi": "Taso 5", "en": "Level 5"}),
        claims=[claim],
    )
    block = MatrixPromptBlock(
        id=blk_id,
        slug="matrix_1",
        label=I18nText(translations={"fi": "Matriisi 1", "en": "Matrix 1"}),
        description=I18nText(translations={"fi": "Kuvaus 1", "en": "Description 1"}),
        scales=[scale],
    )
    blocks_by_id = {blk_id: block}
    matrix_title_lookup = {blk_id: "Matriisi 1"}

    logic = ReasoningStepDTO(
        step_1_identify_premise="Premise",
        step_2_scan_source="Scan",
        step_3_evaluate_anti_patterns="Anti",
        step_4_final_conclusion="Conclusion",
    )
    scorecard_atom = ScorecardAtomDTO(
        atom_id=tda_id,
        level=5,
        level_name="Taso 5",
        claim_label="Väite 1",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=logic,
        status=ExecutionStatus.PASSED,
        semantic_reasoning="Pätevä perustelu ja todistusaineisto.",
        contextual_override=False,
        chart_display_label="Väite 1",
        visual_intent=VisualIntent.NEUTRAL,
    )
    scorecard_row = MatrixScorecardRowDTO(
        block_id=blk_id,
        name="Matriisi 1",
        label_i18n=I18nText(translations={"fi": "Matriisi 1", "en": "Matrix 1"}),
        score=5.0,
        raw_score=5.0,
        scale_max=5.0,
        normalized_score=100.0,
        true_atoms=1,
        total_atoms=1,
        evaluated_atoms=[scorecard_atom],
        row_explanation="Selitys matriisin pisteytykselle.",
        is_evaluative=True,
    )
    matrices = [scorecard_row]

    atom_result = AtomResultDTO(
        tda_id=tda_id,
        matrix_id=blk_id,
        status=ExecutionStatus.PASSED,
        source_quotes=["Tarkka suora lainaus dokumentista."],
        evaluation_reasoning="Pätevä perustelu ja todistusaineisto.",
    )
    hydrated_ref = HydratedAtomDTO(
        sdui_component=SDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Väite 1",
        source_quotes=["Tarkka suora lainaus dokumentista."],
    )
    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prf_0123456789abcdef",
        results=[atom_result],
        hydrated_references={tda_id: hydrated_ref},
    )

    causal_node = CausalNodeDTO(
        node_id=tda_id,
        claim="Väite 1",
        status=ExecutionStatus.PASSED,
        source_quotes=["Tarkka suora lainaus dokumentista."],
        source_input_key="doc1",
        blame_parent_ids=[],
        dependent_child_ids=[],
    )
    unmapped_causal_node = CausalNodeDTO(
        node_id="csl_unmapped_0123456789abcdef",
        claim="Erillinen kausaalipäättely ilman matriisia",
        status=ExecutionStatus.PASSED,
        source_quotes=["Kausaalinen lähdelainaus."],
        source_input_key="doc1",
        blame_parent_ids=[],
        dependent_child_ids=[],
    )
    graph = CausalGraphPayloadDTO(
        nodes=[causal_node, unmapped_causal_node],
        edges=[],
        root_cause_node_ids=[tda_id],
        isolated_node_ids=["csl_unmapped_0123456789abcdef"],
        partition_node_ids={},
        edge_root_causes=[],
    )
    audit = AntiFluffAuditDTO(
        isolated_concept_count=1,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=85.0,
        detected_hollow_terms=[],
    )
    breakdown = FairScoringBreakdownDTO(
        independent_error_count=0,
        cascading_fault_count=0,
        raw_penalty_points=0.0,
        deduplicated_penalty_points=0.0,
        dampened_savings_points=0.0,
    )
    fusion_result = CausalTdaFusionResultDTO(
        graph=graph,
        anti_fluff_audit=audit,
        fair_scoring=breakdown,
        root_cause_diagnoses=[],
        prescriptive_remediations=[],
        total_deliverable_nodes=2,
    )

    return blocks_by_id, matrices, matrix_title_lookup, report_dto, fusion_result


def test_build_atom_rows_existing_parity() -> None:
    """Verify atom row generation with forensic quotes, AI reasoning, causal metadata, and ExportService parity."""
    blocks_by_id, matrices, matrix_title_lookup, report_dto, fusion_result = _create_sample_blocks_and_matrices()

    direct_rows = build_atom_rows(
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
        blocks_by_id=blocks_by_id,
        matrix_title_lookup=matrix_title_lookup,
        causal_result=fusion_result,
    )
    service = ExportService()
    service_rows = service._build_atom_rows(
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
        blocks_by_id=blocks_by_id,
        matrix_title_lookup=matrix_title_lookup,
        causal_result=fusion_result,
    )

    assert len(direct_rows) == 2  # 1 mapped atom + 1 unmapped causal node
    assert len(service_rows) == 2
    assert direct_rows == service_rows

    row0 = direct_rows[0]
    assert row0.matrix_label == "Matriisi 1"
    assert row0.level == 5
    assert row0.criterion == "Väite 1"
    assert row0.result_status == 1
    assert row0.points_awarded == 1.0
    assert "Tarkka suora lainaus" in row0.quotes
    assert "Pätevä perustelu" in row0.ai_reasoning
    assert row0.causal_status == "validated"


def test_build_denormalized_rows_existing_parity() -> None:
    """Verify 22-column flat row generation combining parent matrix metrics, atom evaluations, and ExportService parity."""
    blocks_by_id, matrices, matrix_title_lookup, report_dto, fusion_result = _create_sample_blocks_and_matrices()
    execution_id = "exe_0123456789abcdef"

    direct_rows = build_denormalized_rows(
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
        blocks_by_id=blocks_by_id,
        matrix_title_lookup=matrix_title_lookup,
        execution_id=execution_id,
        causal_result=fusion_result,
    )
    service = ExportService()
    service_rows = service._build_denormalized_rows(
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
        blocks_by_id=blocks_by_id,
        matrix_title_lookup=matrix_title_lookup,
        execution_id=execution_id,
        causal_result=fusion_result,
    )

    assert len(direct_rows) == 2
    assert len(service_rows) == 2
    assert direct_rows == service_rows

    row0 = direct_rows[0]
    assert row0.execution_id == execution_id
    assert row0.matrix_label == "Matriisi 1"
    assert row0.hits == 1
    assert row0.total_atoms == 1
    assert row0.hit_ratio == 1.0
    assert row0.raw_score == 5.0
    assert row0.normalized_score == 100.0
    assert row0.level == 5
    assert row0.criterion == "Väite 1"
    assert row0.result_status == 1
    assert row0.points_awarded == 1.0
    assert "Tarkka suora lainaus" in row0.quotes
    assert "Pätevä perustelu" in row0.ai_reasoning


def test_causal_propositions_single_pipeline_streaming() -> None:
    """Verify unmapped causal propositions stream under localized causal reasoning label."""
    blocks_by_id, matrices, matrix_title_lookup, report_dto, fusion_result = _create_sample_blocks_and_matrices()

    atom_rows = build_atom_rows(
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
        blocks_by_id=blocks_by_id,
        matrix_title_lookup=matrix_title_lookup,
        causal_result=fusion_result,
    )
    denorm_rows = build_denormalized_rows(
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
        blocks_by_id=blocks_by_id,
        matrix_title_lookup=matrix_title_lookup,
        execution_id="exe_0123456789abcdef",
        causal_result=fusion_result,
    )

    unmapped_atom = atom_rows[1]
    unmapped_denorm = denorm_rows[1]

    assert unmapped_atom.matrix_label == "Kausaalipäättely"
    assert unmapped_atom.criterion == "Erillinen kausaalipäättely ilman matriisia"
    assert unmapped_atom.result_status == 1
    assert unmapped_atom.points_awarded == 0.0
    assert unmapped_atom.causal_status == "orphan"

    assert unmapped_denorm.matrix_label == "Kausaalipäättely"
    assert unmapped_denorm.criterion == "Erillinen kausaalipäättely ilman matriisia"
    assert unmapped_denorm.hits == 1
    assert unmapped_denorm.total_atoms == 1
    assert unmapped_denorm.hit_ratio == 1.0
    assert unmapped_denorm.normalized_score == 100.0


def test_atom_row_builder_direct_import() -> None:
    """Verify direct invocation of build_atom_rows and build_denormalized_rows from atom_row_builder."""
    from backend_v2.services.export.atom_row_builder import (
        build_atom_rows as direct_atom_func,
    )
    from backend_v2.services.export.atom_row_builder import (
        build_denormalized_rows as direct_denorm_func,
    )

    assert callable(direct_atom_func)
    assert callable(direct_denorm_func)

    empty_report = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prf_0123456789abcdef",
        results=[],
        hydrated_references={},
    )
    atom_res = direct_atom_func(
        report_dto=empty_report,
        matrices=[],
        locale="en",
        blocks_by_id={},
        matrix_title_lookup={},
    )
    denorm_res = direct_denorm_func(
        report_dto=empty_report,
        matrices=[],
        locale="en",
        blocks_by_id={},
        matrix_title_lookup={},
        execution_id="exe_0123456789abcdef",
    )
    assert atom_res == []
    assert denorm_res == []


def test_build_atom_rows_missing_matrix_raises_not_found() -> None:
    """Verify build_atom_rows raises AppException (404) when atom matrix definition cannot be resolved."""
    orphan_id = "tda_orphan_0123456789abcdef"
    atom_with_missing_matrix = AtomResultDTO(
        tda_id=orphan_id,
        matrix_id="blk_nonexistent_0123456789abcdef",
        status=ExecutionStatus.FAILED,
        source_quotes=None,
        evaluation_reasoning="Failed because matrix block could not be located.",
    )
    hydrated_ref = HydratedAtomDTO(
        sdui_component=SDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Orphan Claim",
        source_quotes=[],
    )
    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prf_0123456789abcdef",
        results=[atom_with_missing_matrix],
        hydrated_references={orphan_id: hydrated_ref},
    )

    with pytest.raises(AppException) as exc_info:
        build_atom_rows(
            report_dto=report_dto,
            matrices=[],
            locale="fi",
            blocks_by_id={},
            matrix_title_lookup={},
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.error_code == ErrorCodes.RESOURCE_NOT_FOUND


def test_build_denormalized_rows_missing_matrix_raises_not_found() -> None:
    """Verify build_denormalized_rows raises AppException (404) when atom matrix definition cannot be resolved."""
    orphan_id = "tda_orphan_0123456789abcdef"
    atom_with_missing_matrix = AtomResultDTO(
        tda_id=orphan_id,
        matrix_id="blk_nonexistent_0123456789abcdef",
        status=ExecutionStatus.FAILED,
        source_quotes=None,
        evaluation_reasoning="Failed because matrix block could not be located.",
    )
    hydrated_ref = HydratedAtomDTO(
        sdui_component=SDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Orphan Claim",
        source_quotes=[],
    )
    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prf_0123456789abcdef",
        results=[atom_with_missing_matrix],
        hydrated_references={orphan_id: hydrated_ref},
    )

    with pytest.raises(AppException) as exc_info:
        build_denormalized_rows(
            report_dto=report_dto,
            matrices=[],
            locale="fi",
            blocks_by_id={},
            matrix_title_lookup={},
            execution_id="exe_0123456789abcdef",
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.error_code == ErrorCodes.RESOURCE_NOT_FOUND


def test_build_atom_rows_and_denorm_all_matrices_override_and_inverse_claims() -> None:
    """Verify all_matrices override, inverse claims, and level breakdown formatting."""
    blocks_by_id, matrices, matrix_title_lookup, _, fusion_result = _create_sample_blocks_and_matrices()
    blk_id = "blk_0123456789abcdef0123456789abcdef"
    tda_id = "tda_0123456789abcdef0123456789abcdef"

    atom_inverse = AtomResultDTO(
        tda_id=tda_id,
        matrix_id=blk_id,
        status=ExecutionStatus.PASSED,
        is_inverse_evidence=True,
        source_quotes=None,
        evaluation_reasoning="Käänteinen väite hyväksytty.",
    )
    hydrated_ref = HydratedAtomDTO(
        sdui_component=SDUIComponentType.BOOLEAN_CARD,
        resolved_claim="Käänteinen väite",
        source_quotes=["Lähdelainaus viitteestä."],
    )
    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prf_0123456789abcdef",
        results=[atom_inverse],
        hydrated_references={tda_id: hydrated_ref},
    )

    alt_scorecard_row = MatrixScorecardRowDTO(
        block_id=blk_id,
        name="Vaihtoehtoinen Matriisi",
        label_i18n=I18nText(translations={"fi": "Vaihtoehtoinen Matriisi", "en": "Alt Matrix"}),
        score=4.0,
        raw_score=None,
        scale_max=5.0,
        normalized_score=80.0,
        true_atoms=1,
        total_atoms=1,
        evaluated_atoms=matrices[0].evaluated_atoms,
        row_explanation="Selitys vaihtoehtoiselle matriisille.",
        level_breakdown={"Taso 5": "1"},
        is_evaluative=True,
    )

    atom_rows = build_atom_rows(
        report_dto=report_dto,
        matrices=[],
        all_matrices=[alt_scorecard_row],
        locale="fi",
        blocks_by_id=blocks_by_id,
        matrix_title_lookup=matrix_title_lookup,
        causal_result=fusion_result,
    )
    denorm_rows = build_denormalized_rows(
        report_dto=report_dto,
        matrices=[],
        all_matrices=[alt_scorecard_row],
        locale="fi",
        blocks_by_id=blocks_by_id,
        matrix_title_lookup=matrix_title_lookup,
        execution_id="exe_0123456789abcdef",
        causal_result=fusion_result,
    )

    assert len(atom_rows) == 2
    row0 = atom_rows[0]
    assert row0.is_inverse == 1
    assert row0.points_awarded == 0.0
    assert row0.claim_type == LocalizationService.translate("export_claim_inverse", "fi")
    assert "Lähdelainaus viitteestä" in row0.quotes

    d_row0 = denorm_rows[0]
    assert d_row0.is_inverse == 1
    assert d_row0.points_awarded == 0.0
    assert d_row0.distribution == "Taso 5: 1"
    assert d_row0.raw_score == 4.0


def test_build_atom_rows_and_denorm_fallback_to_scorecard_and_meta_criterion() -> None:
    """Verify fallback to scorecard claim_label and metadata criterion when hydrated claim is empty."""
    blocks_by_id, matrices, matrix_title_lookup, _, _ = _create_sample_blocks_and_matrices()
    blk_id = "blk_0123456789abcdef0123456789abcdef"
    tda_id = "tda_0123456789abcdef0123456789abcdef"

    atom_no_ref_claim = AtomResultDTO(
        tda_id=tda_id,
        matrix_id=blk_id,
        status=ExecutionStatus.PASSED,
        source_quotes=["Suora lainaus."],
        evaluation_reasoning="Arviointi tehty.",
    )
    hydrated_ref_empty = HydratedAtomDTO(
        sdui_component=SDUIComponentType.BOOLEAN_CARD,
        resolved_claim="",
        source_quotes=["Suora lainaus."],
    )
    report_dto = ReportDataDTO(
        workflow_id="wor_0123456789abcdef",
        execution_id="exe_0123456789abcdef",
        profile_id="prf_0123456789abcdef",
        results=[atom_no_ref_claim],
        hydrated_references={tda_id: hydrated_ref_empty},
    )

    # 1. Fallback to scorecard claim_label
    atom_rows = build_atom_rows(
        report_dto=report_dto,
        matrices=matrices,
        locale="fi",
        blocks_by_id=blocks_by_id,
        matrix_title_lookup=matrix_title_lookup,
    )
    assert atom_rows[0].criterion == "Väite 1"

    # 2. Fallback to meta criterion when scorecard_atom is None
    matrix_without_atoms = [
        MatrixScorecardRowDTO(
            block_id=blk_id,
            name="Matriisi 1",
            label_i18n=I18nText(translations={"fi": "Matriisi 1", "en": "Matrix 1"}),
            score=5.0,
            raw_score=5.0,
            scale_max=5.0,
            normalized_score=100.0,
            true_atoms=1,
            total_atoms=1,
            evaluated_atoms=[],
            row_explanation="Selitys matriisin pisteytykselle.",
            is_evaluative=True,
        )
    ]
    atom_rows_meta = build_atom_rows(
        report_dto=report_dto,
        matrices=matrix_without_atoms,
        locale="fi",
        blocks_by_id=blocks_by_id,
        matrix_title_lookup=matrix_title_lookup,
    )
    assert atom_rows_meta[0].level == 5
    assert atom_rows_meta[0].criterion == "Kriteeri 1"
