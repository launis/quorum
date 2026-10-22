"""Unit tests for metadata resolver functions in the export domain."""

from __future__ import annotations

import pytest

from backend_v2.exceptions import AppException, ErrorCodes
from backend_v2.models.core_base import I18nText
from backend_v2.models.domain.execution import ExecutionRecord
from backend_v2.models.domain.matrix import MatrixClaim, MatrixScale, TDAAssertion
from backend_v2.models.domain.prompt_blocks import (
    AnyPromptBlock,
    MatrixPromptBlock,
)
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.causal_discovery import (
    AntiFluffAuditDTO,
    CausalGraphPayloadDTO,
    CausalNodeDTO,
    CausalTdaFusionResultDTO,
    FairScoringBreakdownDTO,
)
from backend_v2.models.dtos.export import (
    AtomCausalMetadataDTO,
    AtomScaleMetadataDTO,
)
from backend_v2.models.dtos.matrix_scorecard import (
    MatrixScorecardRowDTO,
    ScorecardAtomDTO,
)
from backend_v2.models.dtos.step_output import StepOutputDTO
from backend_v2.models.enums import ExecutionStatus, VisualIntent
from backend_v2.models.state import TraceEvent
from backend_v2.services.export import ExportService
from backend_v2.services.export.metadata_resolver import (
    build_matrix_atom_maps,
    build_scale_metadata,
    extract_causal_result,
    resolve_causal_meta,
    resolve_context_target,
    resolve_matrix_label,
)


def _create_sample_matrices() -> list[MatrixScorecardRowDTO]:
    logic = ReasoningStepDTO(
        step_1_identify_premise="Premise 1",
        step_2_scan_source="Scan 1",
        step_3_evaluate_anti_patterns="Anti 1",
        step_4_final_conclusion="Conclusion 1",
    )
    atom1 = ScorecardAtomDTO(
        atom_id="tda_0123456789abcdef0123456789abcdef",
        level=5,
        level_name="Level 5",
        claim_label="Claim 1",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=logic,
        status=ExecutionStatus.PASSED,
        semantic_reasoning="Reasoning 1",
        contextual_override=False,
        chart_display_label="Atom 1",
        visual_intent=VisualIntent.NEUTRAL,
    )
    atom2 = ScorecardAtomDTO(
        atom_id="tda_fedcba9876543210fedcba9876543210",
        level=1,
        level_name="Level 1",
        claim_label="Claim 2",
        extracted_facts={},
        exact_quotes=[],
        internal_logic_en=logic,
        status=ExecutionStatus.FAILED,
        semantic_reasoning="Reasoning 2",
        contextual_override=False,
        chart_display_label="Atom 2",
        visual_intent=VisualIntent.NEUTRAL,
    )
    matrix = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Matrix Axis 1",
        label_i18n=I18nText(translations={"fi": "Akseli 1", "en": "Axis 1"}),
        score=4.0,
        scale_max=5.0,
        row_explanation="Explanation 1",
        is_evaluative=True,
        evaluated_atoms=[atom1, atom2],
    )
    return [matrix]


def _create_sample_prompt_blocks() -> dict[str, AnyPromptBlock]:
    tda = TDAAssertion(
        tda_id="tda_0123456789abcdef0123456789abcdef",
        concept_description="Concept definition for TDA 1",
        aggregation_mode="EXISTS",
        inverse_evidence=False,
    )
    claim = MatrixClaim(
        label=I18nText(translations={"fi": "Kriteeri 1", "en": "Criterion 1"}),
        tda_assertions=[tda],
    )
    scale = MatrixScale(
        score=5,
        ai_label="Level 5",
        name=I18nText(translations={"fi": "Taso 5", "en": "Level 5"}),
        claims=[claim],
    )
    block = MatrixPromptBlock(
        id="blk_0123456789abcdef",
        slug="matrix_1",
        label=I18nText(translations={"fi": "Matriisi 1", "en": "Matrix 1"}),
        description=I18nText(translations={"fi": "Kuvaus 1", "en": "Description 1"}),
        scales=[scale],
    )
    return {block.id: block}


def test_metadata_resolver_direct_import() -> None:
    """Verify direct import and invocation of functions from metadata_resolver."""
    matrices = _create_sample_matrices()
    atom_to_matrix, atom_to_scorecard = build_matrix_atom_maps(matrices)
    assert "tda_0123456789abcdef0123456789abcdef" in atom_to_matrix
    assert "tda_0123456789abcdef0123456789abcdef" in atom_to_scorecard


def test_build_matrix_atom_maps_existing_parity() -> None:
    """Verify atom-to-matrix and atom-to-scorecard lookup returns identical dictionaries."""
    matrices = _create_sample_matrices()
    direct_matrix_map, direct_atom_map = build_matrix_atom_maps(matrices)
    proxy_matrix_map, proxy_atom_map = ExportService._build_matrix_atom_maps(matrices)

    assert direct_matrix_map == proxy_matrix_map
    assert direct_atom_map == proxy_atom_map
    assert len(direct_matrix_map) == 2
    assert len(direct_atom_map) == 2


def test_resolve_matrix_label_existing_parity() -> None:
    """Verify localized matrix label resolution matches authoritative scorecard names."""
    blocks_by_id = _create_sample_prompt_blocks()
    atom_scale_meta = build_scale_metadata(blocks_by_id, locale="fi")
    matrices = _create_sample_matrices()
    parent_m = matrices[0]
    title_lookup = {"blk_custom": "Custom Title"}

    # 1. From title lookup
    lbl_lookup = resolve_matrix_label(
        atom_matrix_id="blk_custom",
        tda_id="tda_0123456789abcdef0123456789abcdef",
        parent_m=parent_m,
        matrix_title_lookup=title_lookup,
        blocks_by_id=blocks_by_id,
        atom_scale_meta=atom_scale_meta,
        locale="fi",
    )
    proxy_lookup = ExportService._resolve_matrix_label(
        atom_matrix_id="blk_custom",
        tda_id="tda_0123456789abcdef0123456789abcdef",
        parent_m=parent_m,
        matrix_title_lookup=title_lookup,
        blocks_by_id=blocks_by_id,
        atom_scale_meta=atom_scale_meta,
        locale="fi",
    )
    assert lbl_lookup == "Custom Title"
    assert lbl_lookup == proxy_lookup

    # 2. From prompt blocks
    lbl_blocks = resolve_matrix_label(
        atom_matrix_id="blk_0123456789abcdef",
        tda_id="tda_0123456789abcdef0123456789abcdef",
        parent_m=None,
        matrix_title_lookup={},
        blocks_by_id=blocks_by_id,
        atom_scale_meta=atom_scale_meta,
        locale="fi",
    )
    assert lbl_blocks == "Matriisi 1"

    # 3. From parent matrix
    lbl_parent = resolve_matrix_label(
        atom_matrix_id=None,
        tda_id="tda_unknown",
        parent_m=parent_m,
        matrix_title_lookup={},
        blocks_by_id={},
        atom_scale_meta={},
        locale="en",
    )
    assert lbl_parent == "Axis 1"


def test_resolve_context_target_existing_parity() -> None:
    """Verify context target fallback string resolution."""
    assert resolve_context_target(None, "fi") == ""
    assert ExportService._resolve_context_target(None, "fi") == ""

    m1 = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Axis 1",
        label_i18n=I18nText(translations={"fi": "Akseli 1", "en": "Axis 1"}),
        score=4.0,
        scale_max=5.0,
        row_explanation="Explanation",
        is_evaluative=True,
        context_target_label=I18nText(translations={"fi": "Kohteen kuvaus", "en": "Target desc"}),
    )
    assert resolve_context_target(m1, "fi") == "Kohteen kuvaus"
    assert ExportService._resolve_context_target(m1, "fi") == "Kohteen kuvaus"
    assert resolve_context_target(m1, "en") == "Target desc"

    m2 = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Axis 1",
        label_i18n=I18nText(translations={"fi": "Akseli 1", "en": "Axis 1"}),
        score=4.0,
        scale_max=5.0,
        row_explanation="Explanation",
        is_evaluative=True,
        context_target="raw_target_string",
    )
    assert resolve_context_target(m2, "fi") == "raw_target_string"
    assert ExportService._resolve_context_target(m2, "fi") == "raw_target_string"


def test_extract_causal_result_existing_parity() -> None:
    """Verify extraction of CausalTdaFusionResultDTO and CausalGraphPayloadDTO from trace and step states."""
    c_node = CausalNodeDTO(
        node_id="c_0123456789abcdef",
        claim="Claim A",
        status=ExecutionStatus.PASSED,
        source_quotes=("Quote A",),
    )
    graph = CausalGraphPayloadDTO(nodes=[c_node], edges=[])
    audit = AntiFluffAuditDTO(
        isolated_concept_count=0,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=5.0,
        detected_hollow_terms=[],
    )
    scoring = FairScoringBreakdownDTO(
        independent_error_count=0,
        cascading_fault_count=0,
        raw_penalty_points=0.0,
        deduplicated_penalty_points=0.0,
        dampened_savings_points=0.0,
    )
    fusion = CausalTdaFusionResultDTO(
        graph=graph,
        anti_fluff_audit=audit,
        fair_scoring=scoring,
        total_deliverable_nodes=1,
    )

    # 1. From trace event
    exec_trace = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        organization_id="org_0123456789abcdef",
        target_locale="fi",
        status=ExecutionStatus.PASSED,
        execution_trace=[
            TraceEvent(
                step_name="causal_step",
                event_type="output",
                content=fusion,
            )
        ],
    )
    extracted_direct = extract_causal_result(exec_trace)
    extracted_proxy = ExportService._extract_causal_result(exec_trace)
    assert extracted_direct == fusion
    assert extracted_proxy == fusion

    # 2. From trace event with graph
    exec_graph = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        organization_id="org_0123456789abcdef",
        target_locale="fi",
        status=ExecutionStatus.PASSED,
        execution_trace=[
            TraceEvent(
                step_name="causal_step",
                event_type="output",
                content=graph,
            )
        ],
    )
    assert extract_causal_result(exec_graph) == graph
    assert ExportService._extract_causal_result(exec_graph) == graph


def test_resolve_causal_meta_existing_parity() -> None:
    """Verify causal status tagging ('orphan', 'validated', 'cascading_fault', 'root_cause')."""
    # 1. None node
    assert resolve_causal_meta(None, set(), set()) == AtomCausalMetadataDTO()
    assert ExportService._resolve_causal_meta(None, set(), set()) == AtomCausalMetadataDTO()

    # 2. Orphan
    orphan_node = CausalNodeDTO(
        node_id="c_orphan",
        claim="Orphan claim",
        status=ExecutionStatus.PASSED,
    )
    meta_orphan = resolve_causal_meta(orphan_node, set(), {"c_orphan"})
    assert meta_orphan.causal_status == "orphan"

    # 3. Validated passed
    passed_node = CausalNodeDTO(
        node_id="c_passed",
        claim="Passed claim",
        status=ExecutionStatus.PASSED,
    )
    meta_passed = resolve_causal_meta(passed_node, set(), set())
    assert meta_passed.causal_status == "validated"

    # 4. Cascading fault
    cascade_node = CausalNodeDTO(
        node_id="c_cascade",
        claim="Cascade claim",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=["c_parent"],
    )
    meta_cascade = resolve_causal_meta(cascade_node, set(), set())
    assert meta_cascade.causal_status == "cascading_fault"
    assert meta_cascade.blame_parent_id == "c_parent"

    # 5. Root cause
    root_node = CausalNodeDTO(
        node_id="c_root",
        claim="Root claim",
        status=ExecutionStatus.FAILED,
        dependent_child_ids=["c_child1", "c_child2"],
    )
    meta_root = resolve_causal_meta(root_node, {"c_root"}, set())
    assert meta_root.causal_status == "root_cause"
    assert meta_root.dependent_count == 2


def test_resolve_matrix_label_missing_block_raises_not_found() -> None:
    """Verify resolve_matrix_label raises AppException with ErrorCodes.RESOURCE_NOT_FOUND when missing."""
    with pytest.raises(AppException) as exc_info:
        resolve_matrix_label(
            atom_matrix_id="blk_missing",
            tda_id="tda_unknown",
            parent_m=None,
            matrix_title_lookup={},
            blocks_by_id={},
            atom_scale_meta={},
            locale="fi",
        )
    assert exc_info.value.status_code == 404
    assert exc_info.value.error_code == ErrorCodes.RESOURCE_NOT_FOUND.value


def test_extract_causal_result_none_input_returns_none() -> None:
    """Verify extract_causal_result safely returns None when ExecutionRecord is None or empty."""
    assert extract_causal_result(None) is None

    empty_exec = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        organization_id="org_0123456789abcdef",
        target_locale="fi",
        status=ExecutionStatus.PASSED,
    )
    assert extract_causal_result(empty_exec) is None


def test_resolve_matrix_label_additional_branches() -> None:
    """Verify resolve_matrix_label fallback paths for parent name, atom scale meta, and missing atom_matrix_id."""
    # 1. parent_m.name fallback when label_i18n has no translation
    parent_no_i18n = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Authoritative Fallback Name",
        label_i18n=I18nText(translations={"en": "Authoritative Fallback Name", "sv": "Svenska"}),
        score=3.0,
        scale_max=5.0,
        row_explanation="Explanation",
        is_evaluative=True,
    )
    res_parent_name = resolve_matrix_label(
        atom_matrix_id="blk_unmapped",
        tda_id="tda_123",
        parent_m=parent_no_i18n,
        matrix_title_lookup={},
        blocks_by_id={},
        atom_scale_meta={},
        locale="fi",
    )
    assert res_parent_name == "Authoritative Fallback Name"

    # 2. parent_m.name when atom_matrix_id is None
    res_parent_none_atom = resolve_matrix_label(
        atom_matrix_id=None,
        tda_id="tda_123",
        parent_m=parent_no_i18n,
        matrix_title_lookup={},
        blocks_by_id={},
        atom_scale_meta={},
        locale="fi",
    )
    assert res_parent_none_atom == "Authoritative Fallback Name"

    # 3. atom_scale_meta path when matrix is in blocks_by_id
    blocks_by_id = _create_sample_prompt_blocks()
    atom_scale_meta = {
        "tda_scaled": AtomScaleMetadataDTO(
            matrix_id="blk_0123456789abcdef",
            level=5,
            level_name="Level 5",
            criterion="Criterion",
            is_inverse=False,
        )
    }
    res_scale_meta_block = resolve_matrix_label(
        atom_matrix_id=None,
        tda_id="tda_scaled",
        parent_m=None,
        matrix_title_lookup={},
        blocks_by_id=blocks_by_id,
        atom_scale_meta=atom_scale_meta,
        locale="fi",
    )
    assert res_scale_meta_block == "Matriisi 1"

    # 4. Strict Fail-Fast when atom_matrix_id is None and unmapped
    with pytest.raises(AppException) as exc_info:
        resolve_matrix_label(
            atom_matrix_id=None,
            tda_id="tda_completely_missing",
            parent_m=None,
            matrix_title_lookup={},
            blocks_by_id={},
            atom_scale_meta={},
            locale="fi",
        )
    assert exc_info.value.status_code == 404
    assert "Strict Fail-Fast: Matrix block for atom 'tda_completely_missing'" in exc_info.value.message


def test_resolve_context_target_empty_target() -> None:
    """Verify resolve_context_target returns empty string when target is unset."""
    parent_m = MatrixScorecardRowDTO(
        block_id="blk_0123456789abcdef",
        name="Axis 1",
        label_i18n=I18nText(translations={"en": "Axis 1", "fi": "Akseli 1"}),
        score=3.0,
        scale_max=5.0,
        row_explanation="Explanation",
        is_evaluative=True,
        context_target_label=None,
        context_target="",
    )
    assert resolve_context_target(parent_m, "fi") == ""


def test_extract_causal_result_dict_and_step_states() -> None:
    """Verify extract_causal_result extracts from dict trace events and step states."""
    c_node = CausalNodeDTO(
        node_id="c_0123456789abcdef",
        claim="Claim A",
        status=ExecutionStatus.PASSED,
        source_quotes=("Quote A",),
    )
    graph = CausalGraphPayloadDTO(nodes=[c_node], edges=[])
    audit = AntiFluffAuditDTO(
        isolated_concept_count=0,
        cycle_detected=False,
        unsupported_claims_count=0,
        logical_cohesion_score=5.0,
        detected_hollow_terms=[],
    )
    scoring = FairScoringBreakdownDTO(
        independent_error_count=0,
        cascading_fault_count=0,
        raw_penalty_points=0.0,
        deduplicated_penalty_points=0.0,
        dampened_savings_points=0.0,
    )
    fusion = CausalTdaFusionResultDTO(
        graph=graph,
        anti_fluff_audit=audit,
        fair_scoring=scoring,
        total_deliverable_nodes=1,
    )

    # 1. Trace event with dict fusion
    exec_dict_fusion = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        organization_id="org_0123456789abcdef",
        target_locale="fi",
        status=ExecutionStatus.PASSED,
        execution_trace=[
            TraceEvent(
                step_name="causal_step",
                event_type="output",
                content={"fusion": fusion.model_dump(mode="json")},
            )
        ],
    )
    assert extract_causal_result(exec_dict_fusion) == fusion

    # 2. Trace event with dict graph
    exec_dict_graph = ExecutionRecord(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        organization_id="org_0123456789abcdef",
        target_locale="fi",
        status=ExecutionStatus.PASSED,
        execution_trace=[
            TraceEvent(
                step_name="causal_step",
                event_type="output",
                content={"graph": graph.model_dump(mode="json")},
            )
        ],
    )
    assert extract_causal_result(exec_dict_graph) == graph

    # 3. Step states with StepOutputDTO
    exec_step_output = ExecutionRecord.model_construct(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        organization_id="org_0123456789abcdef",
        target_locale="fi",
        status=ExecutionStatus.PASSED,
        execution_trace=[],
        step_states={
            "causal": StepOutputDTO(
                step_id="stp_causal",
                block_id="blk_causal",
                data_type="causal",
                payload=graph,
            )
        },
    )
    assert extract_causal_result(exec_step_output) == graph

    # 4. Step states with StepOutputDTO non-causal payload
    exec_step_non_causal = ExecutionRecord.model_construct(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        organization_id="org_0123456789abcdef",
        target_locale="fi",
        status=ExecutionStatus.PASSED,
        execution_trace=[],
        step_states={
            "non_causal": StepOutputDTO(
                step_id="stp_text",
                block_id="blk_text",
                data_type="text",
                payload="simple text",
            )
        },
    )
    assert extract_causal_result(exec_step_non_causal) is None

    # 5. Step states with direct causal DTO
    exec_step_direct = ExecutionRecord.model_construct(
        id="exe_0123456789abcdef",
        workflow_id="wor_0123456789abcdef",
        organization_id="org_0123456789abcdef",
        target_locale="fi",
        status=ExecutionStatus.PASSED,
        execution_trace=[],
        step_states={"causal": fusion},
    )
    assert extract_causal_result(exec_step_direct) == fusion
