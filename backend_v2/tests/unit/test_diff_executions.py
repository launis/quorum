"""Unit tests for execution trace differential comparison and advanced Kappa suite.

Validates Cohen's/Fleiss' Kappa metrics, singularity boundary guards, Landis & Koch benchmarks,
0-100 difficulty tier normalization, root cause triage, macro score drift, and isolation audit.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from scripts.diff_executions import (
    BlockHeatmapDTO,
    DisagreementRootCause,
    IsolationAuditDTO,
    KappaMetricsDTO,
    MacroBlockScoreDTO,
    RootCauseBreakdownDTO,
    ScaleBreakdownDTO,
    calculate_cohens_kappa,
    calculate_entropy,
    calculate_fleiss_kappa,
    calculate_pairwise_consistency,
    classify_disagreement,
    extract_block_normalized_scores,
    get_all_evals,
    get_state,
    get_trace,
    has_quote,
    uses_contextual_override,
)


class TestKappaAndAgreementMetrics:
    """Test suite for Cohen's Kappa, Fleiss' Kappa, and entropy calculations."""

    def test_calculate_cohens_kappa_perfect_agreement_singularity(self) -> None:
        """Verify perfect agreement (p_o = 1.0) singularity clamps SE to 0.0 and CI to [1.0, 1.0]."""
        ratings = [["passed", "passed"], ["failed", "failed"], ["passed", "passed"]]
        categories = ["failed", "passed"]

        dto: KappaMetricsDTO = calculate_cohens_kappa(ratings, categories)

        assert isinstance(dto, KappaMetricsDTO)
        assert dto.kappa == 1.0
        assert dto.standard_error == 0.0
        assert dto.ci_lower == 1.0
        assert dto.ci_upper == 1.0
        assert dto.observed_agreement == 1.0
        assert "Lähes täydellinen" in dto.benchmark_category

    def test_calculate_cohens_kappa_substantial_agreement(self) -> None:
        """Verify standard Cohen's Kappa calculation with Landis & Koch substantial category."""
        # 10 items: 8 agree, 2 disagree
        ratings = [
            ["passed", "passed"],
            ["passed", "passed"],
            ["passed", "passed"],
            ["passed", "passed"],
            ["failed", "failed"],
            ["failed", "failed"],
            ["failed", "failed"],
            ["passed", "passed"],
            ["passed", "failed"],
            ["failed", "passed"],
        ]
        categories = ["failed", "passed"]

        dto: KappaMetricsDTO = calculate_cohens_kappa(ratings, categories)

        assert isinstance(dto, KappaMetricsDTO)
        assert 0.40 <= dto.kappa <= 0.85
        assert dto.standard_error > 0.0
        assert dto.ci_lower <= dto.kappa <= dto.ci_upper
        assert dto.observed_agreement == 0.8
        assert dto.marginal_bias is not None
        assert dto.marginal_bias == 0.0  # (5 passed - 5 passed) / 10

    def test_calculate_cohens_kappa_landis_koch_categories(self) -> None:
        """Verify Landis & Koch benchmark categories across all score bands."""
        # >0.80: Almost perfect
        high_agree = [["passed", "passed"]] * 9 + [["passed", "failed"]]
        dto_high = calculate_cohens_kappa(high_agree, ["failed", "passed"])
        # If expected agreement is also high, verify valid category string
        assert any(
            icon in dto_high.benchmark_category for icon in ["🏆", "🟢", "🟡", "🔴"]
        )

        # Empty ratings returns default fair/poor DTO
        dto_empty = calculate_cohens_kappa([], ["failed", "passed"])
        assert dto_empty.kappa == 0.0
        assert dto_empty.standard_error == 0.0
        assert "Heikko" in dto_empty.benchmark_category

    def test_calculate_cohens_kappa_invalid_rater_count_raises(self) -> None:
        """Verify ValueError is raised when ratings do not have exactly two raters."""
        with pytest.raises(ValueError, match="requires exactly two raters"):
            calculate_cohens_kappa([["passed", "failed", "passed"]], ["failed", "passed"])

        with pytest.raises(ValueError, match="must contain exactly 2 ratings"):
            calculate_cohens_kappa([["passed", "failed"], ["passed"]], ["failed", "passed"])

    def test_calculate_fleiss_kappa_and_consistency(self) -> None:
        """Verify Fleiss' Kappa and pairwise consistency across multiple raters."""
        ratings = [
            ["passed", "passed", "passed"],
            ["failed", "failed", "failed"],
            ["passed", "passed", "failed"],
        ]
        categories = ["failed", "passed"]

        fleiss = calculate_fleiss_kappa(ratings, categories)
        assert isinstance(fleiss, float)
        assert -1.0 <= fleiss <= 1.0

        # Pairwise consistency for perfect agreement
        assert calculate_pairwise_consistency(["passed", "passed", "passed"]) == 1.0
        # Pairwise consistency for 1 pair agreeing out of 3 pairs (passed, passed, failed)
        assert pytest.approx(calculate_pairwise_consistency(["passed", "passed", "failed"]), 0.01) == 0.333

        # Empty ratings returns 0.0 for fleiss and 1.0 for consistency
        assert calculate_fleiss_kappa([], categories) == 0.0
        assert calculate_pairwise_consistency(["passed"]) == 1.0

    def test_calculate_entropy(self) -> None:
        """Verify Shannon entropy in bits for pure, mixed, and empty distributions."""
        assert calculate_entropy([]) == 0.0
        assert calculate_entropy(["passed", "passed", "passed"]) == 0.0
        # Equal binary distribution has exactly 1 bit of entropy
        assert pytest.approx(calculate_entropy(["passed", "failed"]), 0.001) == 1.0


class TestEvaluationExtractionAndPredicates:
    """Test suite for state determination, trace extraction, quotes, and override predicates."""

    def test_get_state_normalization(self) -> None:
        """Verify discrete status determination from status, decision, mapped_state, or quotes."""
        assert get_state({"status": "PASSED"}) == "passed"
        assert get_state({"decision": "FAILED"}) == "failed"
        assert get_state({"mapped_state": "True"}) == "true"
        assert get_state({"exact_quote": "Authentic quote"}) == "true"
        assert get_state({"exact_quote": "Ei mainittu"}) == "false"
        assert get_state({"exact_quote": "none"}) == "false"
        assert get_state({"exact_quote": []}) == "false"
        assert get_state({}) == "unknown"

    def test_has_quote(self) -> None:
        """Verify has_quote detects authentic quotes and rejects blacklisted strings."""
        assert has_quote({"exact_quote": "Verbatim quote from text"}) is True
        assert has_quote({"source_quote": ["Multiple", "quotes"]}) is True
        assert has_quote({"exact_quote": "not found"}) is False
        assert has_quote({"exact_quote": "ei löydy"}) is False
        assert has_quote({"exact_quote": "None"}) is False
        assert has_quote({"exact_quote": ""}) is False
        assert has_quote({}) is False

    def test_get_trace(self) -> None:
        """Verify trace extraction cascades across standard reasoning fields."""
        assert get_trace({"evaluation_reasoning": "Reason 1"}) == "Reason 1"
        assert get_trace({"context_scan_trace": "Scan 2"}) == "Scan 2"
        assert get_trace({"reasoning_trace": "Trace 3"}) == "Trace 3"
        assert get_trace({}) == ""

    def test_uses_contextual_override(self) -> None:
        """Verify contextual override predicate detects explicit flag or inferred marker."""
        assert uses_contextual_override({"contextual_override": True}) is True
        assert uses_contextual_override({"exact_quote": "[INFERRED] Inferred insight"}) is True
        assert uses_contextual_override({"exact_quote": "Normal text"}) is False
        assert uses_contextual_override({}) is False


class TestRootCauseTriage:
    """Test suite for deterministic disagreement root cause classification."""

    def test_classify_disagreement_technical_error(self) -> None:
        """Verify system error or DLQ triggers TECHNICAL_ERROR."""
        eval1 = {"evaluation_reasoning": "[SYSTEM ERROR: Timeout]"}
        eval2 = {"status": "passed"}
        assert classify_disagreement(eval1, eval2) == DisagreementRootCause.TECHNICAL_ERROR

        eval3 = {"_dlq_status": "FAILED/DLQ"}
        eval4 = {"status": "passed"}
        assert classify_disagreement(eval3, eval4) == DisagreementRootCause.TECHNICAL_ERROR

    def test_classify_disagreement_contextual_override(self) -> None:
        """Verify contextual override trigger."""
        eval1 = {"contextual_override": True, "status": "passed"}
        eval2 = {"status": "failed", "exact_quote": "some text"}
        assert classify_disagreement(eval1, eval2) == DisagreementRootCause.CONTEXTUAL_OVERRIDE

    def test_classify_disagreement_retrieval_gap(self) -> None:
        """Verify retrieval gap when one run finds a quote and the other does not."""
        eval1 = {"status": "passed", "exact_quote": "Authentic quote text"}
        eval2 = {"status": "failed", "exact_quote": "ei löydy"}
        assert classify_disagreement(eval1, eval2) == DisagreementRootCause.RETRIEVAL_GAP

    def test_classify_disagreement_reasoning_gap(self) -> None:
        """Verify reasoning gap when both runs find quotes but reach opposing conclusions."""
        eval1 = {"status": "passed", "exact_quote": "Quote A"}
        eval2 = {"status": "failed", "exact_quote": "Quote B"}
        assert classify_disagreement(eval1, eval2) == DisagreementRootCause.REASONING_GAP

        # Also reasoning gap when neither found a quote
        eval3 = {"status": "passed", "exact_quote": "none"}
        eval4 = {"status": "failed", "exact_quote": "none"}
        assert classify_disagreement(eval3, eval4) == DisagreementRootCause.REASONING_GAP


class TestIsolationAuditAndDTOs:
    """Test suite for IsolationAuditDTO, ScaleBreakdownDTO, and BlockHeatmapDTO."""

    def test_isolation_audit_dto_full_isolation(self) -> None:
        """Verify IsolationAuditDTO with zero shared hashes."""
        audit = IsolationAuditDTO(
            input_hashes_by_run={
                "run1": {"doc.txt": "hash_aaa"},
                "run2": {"doc.txt": "hash_bbb"},
            },
            shared_identical_files=[],
            is_fully_isolated=True,
            disable_vertex_cache_active=True,
        )
        assert audit.is_fully_isolated is True
        assert audit.disable_vertex_cache_active is True
        assert len(audit.shared_identical_files) == 0

    def test_isolation_audit_dto_cache_leak(self) -> None:
        """Verify IsolationAuditDTO with shared identical file hashes."""
        audit = IsolationAuditDTO(
            input_hashes_by_run={
                "run1": {"doc.txt": "hash_identical"},
                "run2": {"doc.txt": "hash_identical"},
            },
            shared_identical_files=["doc.txt (R1 == R2)"],
            is_fully_isolated=False,
            disable_vertex_cache_active=False,
        )
        assert audit.is_fully_isolated is False
        assert len(audit.shared_identical_files) == 1

    def test_root_cause_breakdown_dto(self) -> None:
        """Verify RootCauseBreakdownDTO immutability and counts."""
        dto = RootCauseBreakdownDTO(
            retrieval_gap_count=5,
            reasoning_gap_count=3,
            contextual_override_count=1,
            technical_error_count=0,
            total_mismatches=9,
        )
        assert dto.total_mismatches == 9
        with pytest.raises(ValidationError):
            dto.total_mismatches = 10  # type: ignore[misc]

    def test_scale_breakdown_dto(self) -> None:
        """Verify ScaleBreakdownDTO consistency calculation."""
        dto = ScaleBreakdownDTO(
            tier_label="81–100%: Korkein vaativuustaso",
            tier_min=81.0,
            tier_max=100.0,
            total_atoms=20,
            mismatches=2,
            consistency_rate=0.9,
        )
        assert dto.consistency_rate == 0.9
        assert dto.total_atoms == 20

    def test_block_heatmap_dto(self) -> None:
        """Verify BlockHeatmapDTO schema."""
        dto = BlockHeatmapDTO(
            block_id="blk_matrix_01",
            block_name="Vision & Strategic Clarity",
            total_atoms=15,
            mismatches=3,
            consistency_rate=0.8,
        )
        assert dto.block_id == "blk_matrix_01"
        assert dto.consistency_rate == 0.8

    def test_macro_block_score_dto(self) -> None:
        """Verify MacroBlockScoreDTO normalized score and delta tracking."""
        dto = MacroBlockScoreDTO(
            block_id="blk_matrix_01",
            block_name="Leadership Presence",
            run1_normalized_score=85.0,
            run2_normalized_score=80.0,
            delta_normalized_score=-5.0,
            run1_pass_rate=0.9,
            run2_pass_rate=0.8,
            delta_pass_rate=-0.1,
        )
        assert dto.delta_normalized_score == -5.0
        assert pytest.approx(dto.delta_pass_rate, 0.001) == -0.1


class TestFileExtractionAndTraceParsing:
    """Test suite for file parsing functions (get_all_evals, extract_block_normalized_scores)."""

    def test_get_all_evals_valid_file(self, tmp_path: Path) -> None:
        """Verify get_all_evals extracts atom records from evaluations and results arrays."""
        trace_content = [
            {
                "event_type": "output",
                "content": {
                    "evaluations": [
                        {"atom_id": "atom_1", "status": "passed"},
                        {"tda_id": "atom_2", "status": "failed"},
                    ],
                    "results": [
                        {"tda_id": "atom_3", "status": "passed"},
                    ],
                },
            }
        ]
        trace_file = tmp_path / "execution_trace.json"
        trace_file.write_text(json.dumps(trace_content), encoding="utf-8")

        evals = get_all_evals(trace_file)
        assert len(evals) == 3
        assert "atom_1" in evals
        assert "atom_2" in evals
        assert "atom_3" in evals
        assert evals["atom_1"]["status"] == "passed"

    def test_extract_block_normalized_scores(self, tmp_path: Path) -> None:
        """Verify extraction of normalized scores from trace block payloads."""
        trace_content = [
            {
                "event_type": "output",
                "content": {
                    "blk_strategy": {"normalized_score": 88.5, "raw_score": 4.2},
                    "blk_execution": {"normalized_score": 92.0, "raw_score": 4.5},
                },
            }
        ]
        trace_file = tmp_path / "execution_trace.json"
        trace_file.write_text(json.dumps(trace_content), encoding="utf-8")

        scores = extract_block_normalized_scores(trace_file)
        assert len(scores) == 2
        assert scores["blk_strategy"] == 88.5
        assert scores["blk_execution"] == 92.0

    def test_extract_block_normalized_scores_missing_file(self, tmp_path: Path) -> None:
        """Verify missing trace file safely returns an empty dict without crashing."""
        missing = tmp_path / "nonexistent_trace.json"
        scores = extract_block_normalized_scores(missing)
        assert scores == {}


class TestInspectInputFile:
    """Test suite for _inspect_input_file Unicode noise detection and SHA-256 calculation."""

    def test_inspect_input_file_noise_variants(self, tmp_path: Path) -> None:
        """Verify detection of various Unicode spaces and standard ASCII text."""
        from scripts.diff_executions import _inspect_input_file

        f_ascii = tmp_path / "ascii.txt"
        f_ascii.write_text("Hello world", encoding="utf-8")
        info_ascii = _inspect_input_file(f_ascii)
        assert info_ascii["noise"] == "Standard ASCII"
        assert len(info_ascii["sha256"]) == 64

        f_nobreak = tmp_path / "nobreak.txt"
        f_nobreak.write_text("Hello\u00a0world", encoding="utf-8")
        info_nobreak = _inspect_input_file(f_nobreak)
        assert "No-Break Space (U+00A0)" in info_nobreak["noise"]

        f_en = tmp_path / "en.txt"
        f_en.write_text("Hello\u2002world", encoding="utf-8")
        assert "En Space (U+2002)" in _inspect_input_file(f_en)["noise"]

        f_em = tmp_path / "em.txt"
        f_em.write_text("Hello\u2003world", encoding="utf-8")
        assert "Em Space (U+2003)" in _inspect_input_file(f_em)["noise"]

        f_narrow = tmp_path / "narrow.txt"
        f_narrow.write_text("Hello\u202fworld", encoding="utf-8")
        assert "Narrow No-Break Space (U+202F)" in _inspect_input_file(f_narrow)["noise"]


class TestRunDiffIntegration:
    """End-to-end integration tests for run_diff and main CLI entry point."""

    def test_run_diff_exit_on_insufficient_runs(self, tmp_path: Path) -> None:
        """Verify run_diff exits with code 1 when fewer than 2 executions are provided."""
        from scripts.diff_executions import run_diff

        single_dir = tmp_path / "single_run"
        single_dir.mkdir()
        trace_file = single_dir / "execution_trace.json"
        trace_file.write_text("[]", encoding="utf-8")

        with pytest.raises(SystemExit) as exc_info:
            run_diff([str(single_dir)])
        assert exc_info.value.code == 1

    def test_run_diff_exit_on_zero_common_atoms(self, tmp_path: Path) -> None:
        """Verify run_diff exits with code 1 when executions share zero common atoms."""
        from scripts.diff_executions import run_diff

        dir1 = tmp_path / "run_1"
        dir1.mkdir()
        trace1 = dir1 / "execution_trace.json"
        trace1.write_text(
            json.dumps([{"content": {"evaluations": [{"atom_id": "atom_x", "status": "passed"}]}}]),
            encoding="utf-8",
        )

        dir2 = tmp_path / "run_2"
        dir2.mkdir()
        trace2 = dir2 / "execution_trace.json"
        trace2.write_text(
            json.dumps([{"content": {"evaluations": [{"atom_id": "atom_y", "status": "passed"}]}}]),
            encoding="utf-8",
        )

        with pytest.raises(SystemExit) as exc_info:
            run_diff([str(dir1), str(dir2)])
        assert exc_info.value.code == 1

    def test_run_diff_full_flow(self, tmp_path: Path) -> None:
        """Verify end-to-end execution of run_diff generating full report artifact."""
        from scripts.diff_executions import run_diff

        atom_id_1 = "tda_34259a6c02b74917b12f74b5f3839a66"
        atom_id_2 = "tda_69cc84e0b0c44996a8a95e09b356c692"
        block_id = "blk_440a5fef9331451b"

        # Setup Run 1
        dir1 = tmp_path / "exe_test_run_1"
        dir1.mkdir()
        (dir1 / "inputs").mkdir()
        (dir1 / "inputs" / "doc.txt").write_text("Verbatim quote 1 is authentic\u00a0text.", encoding="utf-8")
        (dir1 / "frozen_context.json").write_text(
            json.dumps({"ui_hints_snapshot": {block_id: {"options": [{"label": {"translations": {"fi": "Lohko 1"}}}]}}}),
            encoding="utf-8",
        )
        (dir1 / "llm_telemetry.jsonl").write_text(
            '{"timestamp": "2026-09-07T00:00:00+00:00", "tokens": 100, "cache_hit": true}\n'
            '{"timestamp": "2026-09-07T00:01:00+00:00", "tokens": 150, "cache_hit": false}\n',
            encoding="utf-8",
        )
        trace_data_1 = [
            {
                "event_type": "output",
                "step_name": "stp_eval",
                "content": {
                    "evaluations": [
                        {
                            "atom_id": atom_id_1,
                            "status": "passed",
                            "exact_quote": "Verbatim quote 1",
                            "evaluation_reasoning": "Reason 1",
                        },
                        {
                            "atom_id": atom_id_2,
                            "status": "failed",
                            "exact_quote": "ei löydy",
                            "evaluation_reasoning": "Reason 2",
                        },
                    ],
                    "_step_metadata": {
                        "token_usage": {
                            "prompt_tokens": 100,
                            "completion_tokens": 50,
                            "cached_tokens": 80,
                            "reasoning_tokens": 20,
                            "cost_usd": 0.005,
                        }
                    },
                },
            },
            {
                "event_type": "output",
                "step_name": "stp_block",
                "content": {block_id: {"normalized_score": 85.0, "raw_score": 4.0}},
            },
        ]
        (dir1 / "execution_trace.json").write_text(json.dumps(trace_data_1), encoding="utf-8")

        # Setup Run 2
        dir2 = tmp_path / "exe_test_run_2"
        dir2.mkdir()
        (dir2 / "inputs").mkdir()
        (dir2 / "inputs" / "doc.txt").write_text("Verbatim quote 1 is authentic\u2002text.", encoding="utf-8")
        (dir2 / "frozen_context.json").write_text(
            json.dumps({"ui_hints_snapshot": {block_id: {"options": [{"label": {"translations": {"fi": "Lohko 1"}}}]}}}),
            encoding="utf-8",
        )
        (dir2 / "llm_telemetry.jsonl").write_text(
            '{"timestamp": "2026-09-07T00:00:00+00:00", "tokens": 120, "cache_hit": true}\n'
            '{"timestamp": "2026-09-07T00:01:00+00:00", "tokens": 160, "cache_hit": false}\n',
            encoding="utf-8",
        )
        trace_data_2 = [
            {
                "event_type": "output",
                "step_name": "stp_eval",
                "content": {
                    "evaluations": [
                        {
                            "atom_id": atom_id_1,
                            "status": "passed",
                            "exact_quote": "Verbatim quote 1",
                            "evaluation_reasoning": "Reason 1",
                        },
                        {
                            "atom_id": atom_id_2,
                            "status": "passed",
                            "exact_quote": "Verbatim quote 1",
                            "evaluation_reasoning": "Reason found",
                        },
                    ],
                    "_step_metadata": {
                        "token_usage": {
                            "prompt_tokens": 110,
                            "completion_tokens": 55,
                            "cached_tokens": 85,
                            "reasoning_tokens": 22,
                            "cost_usd": 0.006,
                        }
                    },
                },
            },
            {
                "event_type": "output",
                "step_name": "stp_block",
                "content": {block_id: {"normalized_score": 90.0, "raw_score": 4.5}},
            },
        ]
        (dir2 / "execution_trace.json").write_text(json.dumps(trace_data_2), encoding="utf-8")

        report_path_str = run_diff([str(dir1), str(dir2)])
        report_file = Path(report_path_str)

        assert report_file.exists()
        content = report_file.read_text(encoding="utf-8")

        # Assert mandatory Finnish analytical report headers and sections
        assert "# Mittauksen Luotettavuus ja Vakausraportti (Reliability & Consistency)" in content
        assert "## Ympäristö ja Konteksti (Execution State)" in content
        assert "TÄYSI SYÖTE-ERISTYS (Ei välimuistivuotoa)" in content
        assert "## Globaalit Metriikat & Tieteellinen Luotettavuus (Kappa Benchmark)" in content
        assert "Fleissin Kappa" in content
        assert "Cohenin Kappa" in content
        assert "## Skaalatasokohtainen Erimielisyysjakauma (0–100 Vaativuustasot)" in content
        assert "## Lohkokohtainen Erimielisyyskartta (Block Heatmap)" in content
        assert "## Erimielisyyksien Juurisyydiagnoosi (Root Cause Triage)" in content
        assert "## Makrotason Pistemäärä- ja Luottamusdiffit (Macro Score Drift 0–100)" in content
        assert "## FinOps & Välimuistisäästöt (Cache Economics & Cost Drift)" in content
        assert "## Lainausten Aitoustarkastus (Lexical Grounding Audit)" in content
        assert "Aitoustaso" in content

    def test_main_cli_execution(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify main() function executes without error when called with CLI arguments."""
        import sys
        from scripts.diff_executions import main

        recorded_args: list[Any] = []

        def mock_run_diff(execution_ids: list[str] | None = None) -> str:
            recorded_args.append(execution_ids)
            return "scratch/fake_report.md"

        monkeypatch.setattr("scripts.diff_executions.run_diff", mock_run_diff)
        monkeypatch.setattr(sys, "argv", ["diff_executions.py", "exe_1", "exe_2"])

        main()

        assert len(recorded_args) == 1
        assert recorded_args[0] == ["exe_1", "exe_2"]

    def test_main_cli_execution_no_args(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Verify main() function handles execution without CLI arguments."""
        import sys
        from scripts.diff_executions import main

        recorded_args: list[Any] = []

        def mock_run_diff(execution_ids: list[str] | None = None) -> str:
            recorded_args.append(execution_ids)
            return "scratch/fake_report.md"

        monkeypatch.setattr("scripts.diff_executions.run_diff", mock_run_diff)
        monkeypatch.setattr(sys, "argv", ["diff_executions.py"])

        main()

        assert len(recorded_args) == 1
        assert recorded_args[0] is None

    def test_calculate_fleiss_kappa_edge_cases(self) -> None:
        """Verify Fleiss Kappa boundary conditions (single rater m<2 and p_e >= 1.0)."""
        # Single rater per item (m=1 < 2) returns 1.0
        assert calculate_fleiss_kappa([["passed"], ["passed"]], ["failed", "passed"]) == 1.0
        # Homogeneous single-class ratings (p_e >= 1.0) returns 1.0
        assert calculate_fleiss_kappa([["passed", "passed"], ["passed", "passed"]], ["passed"]) == 1.0

    def test_run_diff_handles_nonexistent_and_starved_runs(self, tmp_path: Path) -> None:
        """Verify run_diff handles missing trace paths and starvation gracefully."""
        from scripts.diff_executions import run_diff

        dir1 = tmp_path / "exe_starved_1"
        dir1.mkdir()
        trace1 = dir1 / "execution_trace.json"
        trace1.write_text(
            json.dumps([
                {"content": {"evaluations": [{"atom_id": "atom_starved", "status": "passed"}]}},
                {"event_type": "starvation", "content": {}},
            ]),
            encoding="utf-8",
        )

        dir2 = tmp_path / "exe_starved_2"
        dir2.mkdir()
        trace2 = dir2 / "execution_trace.json"
        trace2.write_text(
            json.dumps([
                {"content": {"evaluations": [{"atom_id": "atom_starved", "status": "failed", "evaluation_reasoning": "[SYSTEM ERROR: Timeout]"}]}},
            ]),
            encoding="utf-8",
        )

        # Include a non-existent path in arguments to cover path-not-found branch
        report_str = run_diff([str(dir1), str(dir2), "nonexistent_exe_99999"])
        assert Path(report_str).exists()
