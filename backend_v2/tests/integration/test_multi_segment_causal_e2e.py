"""End-to-End Multi-Segment Evidence and Causal Horizon Integration Test Suite.

Verifies WP4 completion contracts for EPIC 158:
1. DAG execution with multi-segment evidence quotes (2-3 non-contiguous sentences).
2. SlidingWindowLinker candidate deliverable root axiom header linking and dynamic quota allocation.
3. Decoupled lexical strictness tolerance calibration
   (strictness 50 permits morphology, strictness 100 rejects fail-fast).
4. SDUI, Jinja2 HTML, and Tabular export generation with ' [...] ' delimiter formatting.
5. Negative ISTQB boundary partitions: bounding span > 1000 chars, inverted order, and cross-document chimeras.
6. CausalCohesionEvaluator diagnosing WARRANT_GROUNDING_FAILURE vs NODE_FAILURE.
7. Empirical offline ablation benchmark (N=220, pass rate >= 56.4%, 0/21 chimeras).
"""

from __future__ import annotations

import importlib

import pytest

from backend_v2.exceptions import SemanticEvidenceError
from backend_v2.models.core_base import I18nText, coerce_source_quotes_tuple
from backend_v2.models.dtos.atom_evaluation import ReasoningStepDTO
from backend_v2.models.dtos.causal_discovery import CausalEdgeDTO, CausalGraphPayloadDTO, CausalNodeDTO
from backend_v2.models.dtos.dag_models import CausalEdge, ExtractedAtom
from backend_v2.models.dtos.export import ExportForensicAtomDTO
from backend_v2.models.dtos.matrix_scorecard import (
    MatrixScorecardRowDTO,
    ScorecardAtomDTO,
)
from backend_v2.models.dtos.quote_evidence import GateMatchResultDTO, QuoteEvidenceDTO
from backend_v2.models.dtos.report_data import ReportDataDTO
from backend_v2.models.enums import (
    CausalRootCauseType,
    ExecutionStatus,
    VisualIntent,
)
from backend_v2.models.view.sdui import SduiMatrixTableBlock
from backend_v2.services.export_evidence_formatter import format_text_observations
from backend_v2.services.orchestrator.anchor_validation_service import AnchorValidationService
from backend_v2.services.orchestrator.causal_cohesion_evaluator import CausalCohesionEvaluator
from backend_v2.services.orchestrator.sliding_window_linker import (
    SlidingWindowLinker,
    WindowCausalEdgesDTO,
)
from backend_v2.services.pdf_generator import PdfReportService

# ---------------------------------------------------------------------------
# Contract 1: DAG Execution with Multi-Segment Evidence Quotes
# ---------------------------------------------------------------------------


def test_multi_segment_causal_e2e_dag_execution() -> None:
    """Positive Contract 1: Multi-segment evidence quotes persist as tuples and pass lexical grounding."""
    seg1 = "Strateginen visio määrittelee organisaation pitkän aikavälin suunnan ja tavoitteet."
    seg2 = "Käytännön toimenpiteet ja resurssien kohdentaminen ratkaisevat strategian onnistumisen."
    doc_text = f"{seg1} Tähän väliin sijoittuu analyyttinen konteksti ja taustaselvitys. {seg2}"

    # Coerce to immutable tuple
    raw_quotes = [seg1, seg2]
    quotes_tuple = coerce_source_quotes_tuple(raw_quotes)
    assert quotes_tuple is not None
    assert isinstance(quotes_tuple, tuple)
    assert len(quotes_tuple) == 2
    assert quotes_tuple == (seg1, seg2)

    # Lexical grounding via AnchorValidationService
    match_res = AnchorValidationService.strict_match(doc_text, quotes_tuple)
    assert isinstance(match_res, GateMatchResultDTO)
    assert match_res.is_valid is True
    assert match_res.start_idx >= 0
    assert match_res.end_idx > match_res.start_idx
    assert (match_res.end_idx - match_res.start_idx) <= 1000

    # Ensure individual segments satisfy minimum length requirement (>= 30 chars)
    for seg in quotes_tuple:
        assert len(seg) >= 30


# ---------------------------------------------------------------------------
# Contract 2: Candidate Deliverable Root Axiom Header Linking
# ---------------------------------------------------------------------------


def test_multi_segment_causal_e2e_root_axiom_header_linking() -> None:
    """Positive Contract 2: SlidingWindowLinker injects root axioms with dynamic quota allocation."""
    linker = SlidingWindowLinker(window_size=10, overlap=2)

    # Provision candidate deliverable root axioms with multi-segment quotes
    processed_atoms: dict[str, ExtractedAtom] = {}
    for i in range(12):
        tda_id = f"tda_{i:08x}"
        processed_atoms[tda_id] = ExtractedAtom(
            tda_id=tda_id,
            resolved_claim=f"Candidate root deliverable claim assertion {i}",
            reasoning=f"High-confidence justification for claim {i}",
            source_quotes=(
                f"Lainaus ensimmäisestä kappaleesta {i} riittävän pitkänä.",
                f"Lainaus toisesta kappaleesta {i} riittävän pitkänä.",
            ),
            source_sequence_index=i,
        )

    # Master dependencies: high out-degree for axioms 0, 1, and 2
    master_deps: dict[str, WindowCausalEdgesDTO] = {
        "tda_10000001": WindowCausalEdgesDTO(
            edges={
                "tda_00000001": CausalEdge(
                    edge_reasoning="r1",
                    tda_id="tda_00000001",
                    source_id="tda_10000001",
                    warrant_quotes=("Warrantti lainaus ensimmäinen.", "Warrantti lainaus toinen."),
                ),
                "tda_00000000": CausalEdge(
                    edge_reasoning="r0",
                    tda_id="tda_00000000",
                    source_id="tda_10000001",
                ),
            }
        ),
        "tda_10000002": WindowCausalEdgesDTO(
            edges={
                "tda_00000001": CausalEdge(
                    edge_reasoning="r1_2",
                    tda_id="tda_00000001",
                    source_id="tda_10000002",
                ),
            }
        ),
    }

    current_window_ids = {f"tda_1000{j:04x}" for j in range(1, 11)}  # window size = 10
    selected_axioms = linker._select_root_axioms(
        processed_atoms=processed_atoms,
        current_window_ids=current_window_ids,
        master_deps=master_deps,
        current_window_size=10,
    )

    # Invariants: K_eff = min(8, max(0, 20 - 10)) = 8
    assert len(selected_axioms) <= 8
    assert len(selected_axioms) == 8
    assert 10 + len(selected_axioms) <= 20

    # Axiom 00000001 has highest out-degree (2), selected first
    assert selected_axioms[0].tda_id == "tda_00000001"
    assert selected_axioms[0].source_quotes is not None
    assert len(selected_axioms[0].source_quotes) == 2


# ---------------------------------------------------------------------------
# Contract 3: Decoupled Lexical Strictness Calibration
# ---------------------------------------------------------------------------


def test_multi_segment_causal_e2e_strictness_calibration() -> None:
    """Positive Contract 3: Strictness 50 permits Snowball morphology; strictness 100 rejects fail-fast."""
    source_text = "Työryhmä sitoutui johtajuudessaan selkeisiin tavoitteisiin ja strategiaan."
    inflected_quote = ["johtajuus ja selkeät tavoitteet"]

    # 1. Lexical strictness 50: permits morphological inflection
    extracted_50 = AnchorValidationService.validate_evidence(
        pdf_text=source_text,
        exact_quotes=inflected_quote,
        locale="fi",
        strictness_level=85,
        lexical_strictness_level=50,
    )
    assert extracted_50 is not None
    assert len(extracted_50) == 1
    assert extracted_50[0] == "johtajuudessaan selkeisiin tavoitteisiin"

    # 2. Absolute lexical zero-trust (100): rejects morphology fail-fast
    with pytest.raises(SemanticEvidenceError) as exc_info:
        AnchorValidationService.validate_evidence(
            pdf_text=source_text,
            exact_quotes=inflected_quote,
            locale="fi",
            strictness_level=85,
            lexical_strictness_level=100,
        )
    assert "not found" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# Contract 4: SDUI, Jinja2 HTML, and Tabular Export Generation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_multi_segment_causal_e2e_report_and_export_generation() -> None:
    """Positive Contract 4: SDUI, Jinja2 HTML, and Tabular exports contain ' [...] ' formatted citations."""
    seg1 = "Ensimmäinen todennettu havaintolause raportissa."
    seg2 = "Toinen todennettu havaintolause raportissa."
    expected_delimited = f"{seg1} [...] {seg2}"

    # 1. Tabular export evidence formatting
    formatted_export = format_text_observations((seg1, seg2))
    assert formatted_export == expected_delimited

    forensic_atom = ExportForensicAtomDTO(
        matrix_label="Kausaalipäättely",
        context_target="Yleinen konteksti",
        level=1,
        level_name="Taso 1",
        criterion="Multi-segment evidence claim",
        claim_type="Oletus",
        result_status=1,
        quotes=formatted_export,
        ai_reasoning="Corroborated by non-contiguous evidence segments.",
        is_inverse=0,
        points_awarded=1.0,
    )
    assert forensic_atom.quotes == expected_delimited

    # 2. PDF / Jinja2 HTML rendering
    pdf_service = PdfReportService()
    scorecard_atom = ScorecardAtomDTO(
        atom_id="atm_00000000000000010000000000000001",
        level=1,
        level_name="Level 1",
        claim_label="Claim 1",
        extracted_facts={"fact1": "val1"},
        exact_quotes=[
            QuoteEvidenceDTO(
                source_quotes=(seg1, seg2),
                verified_source_ids=["src_0"],
            )
        ],
        internal_logic_en=ReasoningStepDTO(
            step_1_identify_premise="p1",
            step_2_scan_source="s1",
            step_3_evaluate_anti_patterns="a1",
            step_4_final_conclusion="c1",
        ),
        status=ExecutionStatus.PASSED,
        semantic_reasoning="reasoning",
        contextual_override=False,
        structural_location=None,
        chart_display_label="A1",
        visual_intent=VisualIntent.SUCCESS,
    )
    axis_data = {
        "block_id": "axis_1",
        "name": "Test Axis",
        "label_i18n": {"translations": {"en": "Test Axis", "fi": "Testi Akseli"}},
        "is_evaluative": True,
        "allow_contextual_override": True,
        "level_names": {"1": "Level 1"},
        "level_breakdown": {"1": "1/1"},
        "evaluated_atoms": [scorecard_atom],
        "row_explanation": "All good",
        "ui_plot_ratio": 0.85,
        "score_display_label": "85%",
    }
    axis = MatrixScorecardRowDTO.model_validate(axis_data)
    sdui_block = SduiMatrixTableBlock(
        matrix_visible_columns=["label", "quotes", "distribution", "row_explanation", "normalized_score"],
        axes=[axis],
    )
    report_data = ReportDataDTO(
        execution_id="exe_multi_segment_test",
        strictness_level=85,
        workflow_id="wf_multi_segment_test",
        profile_id="prf_multi_segment_test",
        profile_name=I18nText(translations={"en": "Test Profile", "fi": "Testiprofiili"}),
        inner_sdui_blocks=[sdui_block],
    )
    html_output = await pdf_service.generate_execution_html(
        execution_id="exe_multi_segment_test",
        report_dto=report_data,
        locale="fi",
    )
    assert expected_delimited in html_output


# ---------------------------------------------------------------------------
# Contract 5: Negative ISTQB Partitions: Span, Order, and Chimera Rejection
# ---------------------------------------------------------------------------


def test_multi_segment_causal_e2e_negative_chimera_and_ordering_rejection() -> None:
    """Negative Contract 5: AnchorValidationService rejects span violations, inverted order, and chimeras."""
    seg1 = "Ensimmäinen lause riittävän pitkällä tekstillä."
    seg2 = "Toinen lause riittävän pitkällä tekstillä."

    # Part A: Bounding span > 1000 characters
    filler_over_1000 = "Täytetekstiä analyyttisessä testissä yli tuhat merkkiä. " * 35
    text_long_span = f"{seg1} {filler_over_1000} {seg2}"
    res_span = AnchorValidationService.strict_match(text_long_span, (seg1, seg2))
    assert res_span.is_valid is False

    # Part B: Inverted segment order (monotonic forward scan violation)
    text_normal_order = f"{seg1} Lyhyt väliosa tähän. {seg2}"
    res_inverted = AnchorValidationService.strict_match(text_normal_order, (seg2, seg1))
    assert res_inverted.is_valid is False

    # Part C: Cross-document chimera (seg1 from Doc A, seg2 from Doc B)
    doc_a = f"{seg1} Tekstiä ainoastaan ensimmäisessä dokumentissa."
    doc_b = f"{seg2} Tekstiä ainoastaan toisessa dokumentissa."
    res_chimera_a = AnchorValidationService.strict_match(doc_a, (seg1, seg2))
    res_chimera_b = AnchorValidationService.strict_match(doc_b, (seg1, seg2))
    assert res_chimera_a.is_valid is False
    assert res_chimera_b.is_valid is False


# ---------------------------------------------------------------------------
# Contract 6: Negative Warrant Grounding Failure
# ---------------------------------------------------------------------------


def test_multi_segment_causal_e2e_negative_warrant_grounding_failure() -> None:
    """Negative Contract 6: CausalCohesionEvaluator diagnoses WARRANT_GROUNDING_FAILURE vs NODE_FAILURE."""
    evaluator = CausalCohesionEvaluator()

    parent_node = CausalNodeDTO(
        node_id="tda_p0001",
        claim="Pätevänä pysyvä perusolettama.",
        source_quotes=("Ensimmäinen lainaus perusolettamalle.",),
        paragraph_ref="P1",
        status=ExecutionStatus.PASSED,
        blame_parent_ids=[],
        dependent_child_ids=["tda_c0001"],
    )
    child_node = CausalNodeDTO(
        node_id="tda_c0001",
        claim="Päättelyketjun hylätty johtopäätös.",
        source_quotes=None,
        paragraph_ref="P2",
        status=ExecutionStatus.FAILED,
        blame_parent_ids=["tda_p0001"],
        dependent_child_ids=[],
    )
    graph = CausalGraphPayloadDTO(
        nodes=[parent_node, child_node],
        edges=[
            CausalEdgeDTO(
                source_id="tda_p0001",
                target_id="tda_c0001",
                reasoning="Syy-seurausyhteys perusolettamasta johtopäätökseen.",
                warrant_quotes=("Warrantti lainaus 1", "Warrantti lainaus 2"),
            )
        ],
        root_cause_node_ids=["tda_c0001"],
        cycle_detected=False,
        isolated_node_ids=[],
        partition_node_ids={},
        edge_root_causes=["tda_p0001->tda_c0001"],
    )

    diagnoses = evaluator.diagnose_root_causes(graph)

    assert len(diagnoses) == 1
    diag = diagnoses[0]
    assert diag.failing_node_id == "tda_c0001"
    assert diag.root_cause_parent_id == "tda_p0001"
    assert diag.root_cause_type == CausalRootCauseType.WARRANT_GROUNDING_FAILURE
    assert "Inferential warrant failure" in diag.explanation


# ---------------------------------------------------------------------------
# Contract 7: Offline Ablation Benchmark Empirical Pass Rate Gate
# ---------------------------------------------------------------------------


def test_offline_ablation_benchmark_pass_rate() -> None:
    """Positive Contract 7: Benchmark evaluates 220 proposition frames verifying pass rate >= 56.4% and 0 chimeras."""
    mod = importlib.import_module("scripts.run_e2e_variance_test")
    verify_fn = mod.verify_offline_ablation_benchmark
    report = verify_fn(min_pass_rate=56.4, max_chimera_rate=0.0)

    config_1 = next((c for c in report.config_results if c.config_id == 1), None)
    assert config_1 is not None
    assert config_1.total_atoms == 220
    assert config_1.pass_rate_pct >= 56.4
    assert config_1.chimera_rate_pct == 0.0
    assert config_1.dlq_rate_pct == 0.0
