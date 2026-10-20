"""Unit tests for Component Ablation Benchmark Driver (scripts/run_ablation_benchmark.py).

Verifies CLI parsing, fail-fast validations, dry-run execution, chimera detection,
Popperian lexical firewall rejection, Cohen's Kappa boundary values, call cardinality,
monolithic step-judge evaluation, transient error DLQ recovery, and Table 5 Markdown formatting.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock

import pytest

from backend_v2.models.enums import CognitiveTier, ExecutionStatus
from scripts.run_ablation_benchmark import (
    CONFIGURATIONS,
    AblationAtomEvaluationDTO,
    AblationBenchmarkReportDTO,
    AblationBenchmarkRunner,
    AblationConfigResultDTO,
    AblationMode,
    AblationPropositionDTO,
    AblationStepBatchDTO,
    build_arg_parser,
    calculate_chimera_rate,
    calculate_dlq_rate,
    calculate_pass_rate,
    compute_cluster_bootstrapped_kappa_for_runs,
    compute_cohens_kappa_for_runs,
    format_ablation_table_markdown,
    main,
    print_ablation_telemetry_banner,
    run_ablation_benchmark,
)


def test_ablation_cli_arguments() -> None:
    """Verifies that CLI arguments are correctly parsed by build_arg_parser."""
    parser = build_arg_parser()
    args = parser.parse_args(
        [
            "--case",
            "pair_a",
            "--config",
            "1",
            "--runs",
            "1",
            "--dry-run",
            "--output-format",
            "json",
            "--output-file",
            "artifacts/test_table_5.json",
        ]
    )

    assert args.case == "pair_a"
    assert args.config == "1"
    assert args.runs == 1
    assert args.dry_run is True
    assert args.output_format == "json"
    assert args.output_file == "artifacts/test_table_5.json"


def test_ablation_cli_invalid_arguments_fail_fast() -> None:
    """Verifies negative equivalence partition: invalid CLI options trigger SystemExit(2)."""
    parser = build_arg_parser()

    with pytest.raises(SystemExit) as exc_info_config:
        parser.parse_args(["--config", "6"])
    assert exc_info_config.value.code == 2

    with pytest.raises(SystemExit) as exc_info_case:
        parser.parse_args(["--case", "invalid_case_dataset"])
    assert exc_info_case.value.code == 2

    with pytest.raises(SystemExit) as exc_info_runs:
        parser.parse_args(["--runs", "3"])
    assert exc_info_runs.value.code == 2


def test_ablation_dry_run_all_configs() -> None:
    """Verifies that all 5 configurations execute cleanly in dry-run mode and produce valid metrics."""
    runner = AblationBenchmarkRunner(case_filter="both", selected_configs=[1, 2, 3, 4, 5], runs=2, dry_run=True)
    report = runner.run_all()

    assert isinstance(report, AblationBenchmarkReportDTO)
    assert report.case_filter == "both"
    assert len(report.config_results) == 5

    for cfg_res in report.config_results:
        assert isinstance(cfg_res, AblationConfigResultDTO)
        assert cfg_res.total_atoms == 220
        assert cfg_res.runs == 2
        assert 0.0 <= cfg_res.observed_agreement <= 100.0
        assert -1.0 <= cfg_res.cohens_kappa <= 1.0
        assert -1.0 <= cfg_res.ci_lower <= 1.0
        assert -1.0 <= cfg_res.ci_upper <= 1.0
        assert 0.0 <= cfg_res.chimera_rate_pct <= 100.0
        assert 0.0 <= cfg_res.pass_rate_pct <= 100.0
        assert 0.0 <= cfg_res.dlq_rate_pct <= 100.0

    # Verify Config 1 achieves top reproducibility
    cfg1 = next(r for r in report.config_results if r.config_id == 1)
    assert cfg1.cohens_kappa >= 0.85
    assert cfg1.chimera_rate_pct == 0.0
    assert cfg1.dlq_rate_pct == 0.0


def test_ablation_chimera_detection_in_config_2() -> None:
    """Verifies that Configuration 2 accepts atom but flags chimera and increments chimera rate."""
    runner = AblationBenchmarkRunner(case_filter="pair_a", runs=1, dry_run=True)
    config2 = CONFIGURATIONS[2]

    # Create a proposition with a fabricated/unanchored quote
    prop = AblationPropositionDTO(
        tda_id="tda_test_chimera_001",
        step_id="step_test",
        claim_text="Fabricated claim that is not in the text.",
        expected_true=True,
        synthetic_quote="Completely hallucinated citation substring.",
        is_quote_valid_in_source=False,
    )

    eval_dto = runner.evaluate_atom_with_config(config=config2, prop=prop, run_idx=1)

    # In Config 2 without lexical firewall, raw is_true is accepted as PASSED
    assert eval_dto.status == ExecutionStatus.PASSED
    # But chimera status is audited and detected as True
    assert eval_dto.is_chimera is True

    # When computing chimera rate, it reflects 100% of passed atoms
    rate = calculate_chimera_rate([eval_dto])
    assert rate == 100.0


def test_ablation_lexical_firewall_rejection_in_config_1() -> None:
    """Verifies that Configuration 1 rejects fabricated quote per Popperian null hypothesis to FAILED."""
    runner = AblationBenchmarkRunner(case_filter="pair_a", runs=1, dry_run=True)
    config1 = CONFIGURATIONS[1]

    prop = AblationPropositionDTO(
        tda_id="tda_test_firewall_001",
        step_id="step_test",
        claim_text="Fabricated claim with unanchored quote.",
        expected_true=True,
        synthetic_quote="Hallucinated quote rejected by firewall.",
        is_quote_valid_in_source=False,
    )

    eval_dto = runner.evaluate_atom_with_config(config=config1, prop=prop, run_idx=1)

    # In Config 1 with lexical firewall active, unanchored quote forces status to FAILED
    assert eval_dto.status == ExecutionStatus.FAILED
    assert eval_dto.is_chimera is False

    # Passed atoms chimera rate remains 0.0%
    rate = calculate_chimera_rate([eval_dto])
    assert rate == 0.0


def test_ablation_cohens_kappa_perfect_and_zero_division() -> None:
    """Boundary value tests for Cohen's Kappa: perfect agreement, empty input, and zero division."""
    # 1. Perfect agreement (kappa = 1.0)
    run1 = [
        AblationAtomEvaluationDTO(
            tda_id="tda_001",
            raw_is_true=True,
            source_quote="Quote 1",
            is_chimera=False,
            status=ExecutionStatus.PASSED,
        ),
        AblationAtomEvaluationDTO(
            tda_id="tda_002",
            raw_is_true=False,
            source_quote=None,
            is_chimera=False,
            status=ExecutionStatus.FAILED,
        ),
    ]
    run2 = list(run1)

    kappa_perfect = compute_cohens_kappa_for_runs(run1, run2)
    assert kappa_perfect.kappa == 1.0
    assert kappa_perfect.observed_agreement == 1.0
    assert kappa_perfect.ci_lower == 1.0
    assert kappa_perfect.ci_upper == 1.0

    # 2. Empty input
    kappa_empty = compute_cohens_kappa_for_runs([], [])
    assert kappa_empty.kappa == 0.0
    assert kappa_empty.observed_agreement == 0.0

    # 3. Zero-division defenses in rate calculators
    assert calculate_chimera_rate([]) == 0.0
    assert calculate_pass_rate([]) == 0.0
    assert calculate_dlq_rate([]) == 0.0

    # 4. Zero passed atoms chimera defense
    failed_only = [
        AblationAtomEvaluationDTO(
            tda_id="tda_fail",
            raw_is_true=False,
            source_quote=None,
            is_chimera=False,
            status=ExecutionStatus.FAILED,
        )
    ]
    assert calculate_chimera_rate(failed_only) == 0.0


def test_ablation_single_pass_vs_bo3_call_cardinality() -> None:
    """Verifies that Configs 1-2 perform 3 calls (k=3), Configs 3-4 perform 1 call, and Config 5 calls 1 per step."""
    # 1. Config 1 (Bo3): 1 atom -> 3 calls
    runner1 = AblationBenchmarkRunner(case_filter="pair_a", selected_configs=[1], runs=1, dry_run=True)
    prop = runner1.propositions[0]
    runner1.evaluate_atom_with_config(CONFIGURATIONS[1], prop, run_idx=1)
    assert runner1.call_counts[1] == 3

    # 2. Config 2 (Bo3): 1 atom -> 3 calls
    runner2 = AblationBenchmarkRunner(case_filter="pair_a", selected_configs=[2], runs=1, dry_run=True)
    runner2.evaluate_atom_with_config(CONFIGURATIONS[2], prop, run_idx=1)
    assert runner2.call_counts[2] == 3

    # 3. Config 3 (Single-Pass): 1 atom -> 1 call
    runner3 = AblationBenchmarkRunner(case_filter="pair_a", selected_configs=[3], runs=1, dry_run=True)
    runner3.evaluate_atom_with_config(CONFIGURATIONS[3], prop, run_idx=1)
    assert runner3.call_counts[3] == 1

    # 4. Config 4 (Single-Pass): 1 atom -> 1 call
    runner4 = AblationBenchmarkRunner(case_filter="pair_a", selected_configs=[4], runs=1, dry_run=True)
    runner4.evaluate_atom_with_config(CONFIGURATIONS[4], prop, run_idx=1)
    assert runner4.call_counts[4] == 1

    # 5. Config 5 (Monolithic Step): 1 step batch of 25 atoms -> 1 call
    runner5 = AblationBenchmarkRunner(case_filter="pair_a", selected_configs=[5], runs=1, dry_run=True)
    batch = AblationStepBatchDTO(step_id="step_test_batch", propositions=runner5.propositions[:25])
    runner5.evaluate_monolithic_step(CONFIGURATIONS[5], batch, run_idx=1)
    assert runner5.call_counts[5] == 1


def test_ablation_monolithic_step_judge_evaluation() -> None:
    """Verifies that Configuration 5 evaluates step batches and maps omitted atoms to FAILED with reason."""
    runner = AblationBenchmarkRunner(case_filter="pair_a", selected_configs=[5], runs=1, dry_run=True)
    config5 = CONFIGURATIONS[5]

    batch = AblationStepBatchDTO(step_id="step_bloom", propositions=runner.propositions[:20])

    # Evaluate step batch with 25% forced omitted atoms
    results = runner.evaluate_monolithic_step(config=config5, batch=batch, run_idx=1, drop_missing_ratio=0.25)

    assert len(results) == 20
    missing_atoms = [r for r in results if r.error_reason == "MISSING_FROM_MONOLITHIC_RESPONSE"]
    assert len(missing_atoms) > 0

    for m in missing_atoms:
        assert m.status == ExecutionStatus.FAILED
        assert m.raw_is_true is False

    dlq_pct = calculate_dlq_rate(results)
    assert dlq_pct > 0.0


def test_ablation_transient_error_dlq_recovery() -> None:
    """Verifies that Bo3 (Config 1) recovers from 1 transient 429 error, while Single-Pass (Config 3) yields DLQ."""
    runner = AblationBenchmarkRunner(case_filter="pair_a", runs=1, dry_run=True)
    prop = runner.propositions[0]

    # In Config 1 (Bo3): 1 transient error recovers via 2/2 consensus
    eval_cfg1 = runner.evaluate_atom_with_config(
        config=CONFIGURATIONS[1],
        prop=prop,
        run_idx=1,
        force_transient_error=True,
    )
    assert eval_cfg1.status != ExecutionStatus.SYSTEM_ERROR

    # In Config 3 (Single-Pass): 1 transient error fails fast to SYSTEM_ERROR / DLQ
    eval_cfg3 = runner.evaluate_atom_with_config(
        config=CONFIGURATIONS[3],
        prop=prop,
        run_idx=1,
        force_transient_error=True,
    )
    assert eval_cfg3.status == ExecutionStatus.SYSTEM_ERROR
    assert eval_cfg3.error_reason == "TRANSIENT_API_ERROR_HTTP_429"

    # DLQ rate reflects the system error
    assert calculate_dlq_rate([eval_cfg3]) == 100.0


def test_ablation_table_5_markdown_formatting() -> None:
    """Verifies that Table Markdown output conforms strictly to paper publication requirements."""
    runner = AblationBenchmarkRunner(case_filter="both", selected_configs=[1, 2, 3, 4, 5], runs=2, dry_run=True)
    report = runner.run_all()
    md_output = format_ablation_table_markdown(report, table_num=7)

    # Check header columns
    assert (
        "| Experimental Configuration | Evaluated Atoms ($N$) | Observed Agreement ($P_o$) | Cohen’s Kappa ($\\kappa$) | 95% Confidence Interval (CI) | Chimera / Unanchored Rate (%) | Pass Rate (%) | DLQ / Errors (%) |"
        in md_output
    )
    assert "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |" in md_output

    # Check that all 5 configuration rows are present
    assert "| **1. Full Quorum (Bo3 + Lexical Firewall)** | 220 |" in md_output
    assert "| **2. Quorum without Lexical Firewall** | 220 |" in md_output
    assert "| **3. Quorum Single-Pass (k=1 + Lexical Firewall)** | 220 |" in md_output
    assert "| **4. Atom-level Unconstrained LLM-as-a-Judge** | 220 |" in md_output
    assert "| **5. Monolithic Step-Level LLM-as-a-Judge** | 220 |" in md_output

    # Check caption for Table 7
    assert "**Table 7:** Component ablation benchmark study across 220 proposition atom evaluations" in md_output

    # Verify format_ablation_table_markdown with table_num=5
    md_output_5 = format_ablation_table_markdown(report, table_num=5)
    assert "**Table 5:** Component ablation benchmark study across 220 proposition atom evaluations" in md_output_5


def test_ablation_source_text_lexical_verification() -> None:
    """Verifies AnchorValidationService live lexical check when source_text is provided."""
    runner = AblationBenchmarkRunner(case_filter="pair_a", runs=1, dry_run=True)
    config1 = CONFIGURATIONS[1]

    doc_text = "Tämä on johtoryhmän virallinen strategia ja visio vuodelle 2026."

    # Valid quote found in doc
    prop_valid = AblationPropositionDTO(
        tda_id="tda_src_001",
        step_id="step_test",
        claim_text="Strategia vuodelle 2026.",
        expected_true=True,
        synthetic_quote="strategia ja visio",
        is_quote_valid_in_source=True,
    )
    eval_valid = runner.evaluate_atom_with_config(config=config1, prop=prop_valid, run_idx=1, source_text=doc_text)
    assert eval_valid.status == ExecutionStatus.PASSED
    assert eval_valid.is_chimera is False

    # Invalid quote not found in doc
    prop_invalid = AblationPropositionDTO(
        tda_id="tda_src_002",
        step_id="step_test",
        claim_text="Strategia vuodelle 2026.",
        expected_true=True,
        synthetic_quote="täysin keksitty lainaus",
        is_quote_valid_in_source=False,
    )
    eval_invalid = runner.evaluate_atom_with_config(config=config1, prop=prop_invalid, run_idx=1, source_text=doc_text)
    assert eval_invalid.status == ExecutionStatus.FAILED
    assert eval_invalid.is_chimera is False


def test_ablation_run_benchmark_file_persistence(tmp_path: Path) -> None:
    """Verifies that run_ablation_benchmark executes CLI configuration and persists JSON and Markdown."""
    parser = build_arg_parser()

    # JSON output file
    json_file = str(tmp_path / "artifacts" / "test_report.json")
    args_json = parser.parse_args(
        [
            "--case",
            "pair_a",
            "--config",
            "1",
            "--runs",
            "1",
            "--dry-run",
            "--output-format",
            "json",
            "--output-file",
            json_file,
        ]
    )
    report_json = run_ablation_benchmark(args_json)
    assert Path(json_file).exists()
    assert report_json.config_results[0].total_atoms == 110

    # Markdown output file
    md_file = str(tmp_path / "artifacts" / "test_table_5.md")
    args_md = parser.parse_args(
        [
            "--case",
            "pair_a",
            "--config",
            "1",
            "--runs",
            "1",
            "--dry-run",
            "--output-format",
            "markdown",
            "--output-file",
            md_file,
        ]
    )
    report_md = run_ablation_benchmark(args_md)
    assert Path(md_file).exists()
    assert report_md.config_results[0].total_atoms == 110
    assert "Table 7" in Path(md_file).read_text(encoding="utf-8")


def test_ablation_main_cli_entrypoint(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies that main() executes cleanly in dry-run mode and prints output."""
    exit_code_md = main(["--dry-run", "--case", "pair_a", "--config", "1", "--runs", "1"])
    assert exit_code_md == 0
    captured_md = capsys.readouterr()
    assert "Table 7" in captured_md.out

    exit_code_json = main(["--dry-run", "--case", "pair_a", "--config", "1", "--runs", "1", "--output-format", "json"])
    assert exit_code_json == 0
    captured_json = capsys.readouterr()
    assert "config_results" in captured_json.out


def test_ablation_physical_production_trace_baseline() -> None:
    """Verifies that Configuration 1 correctly loads physical production traces when not dry-run."""
    runner = AblationBenchmarkRunner(case_filter="both", selected_configs=[1], runs=2, dry_run=False)
    result = runner.run_configuration(1)
    assert result.config_id == 1
    assert result.total_atoms == 220
    assert result.observed_agreement == 96.36
    assert result.cohens_kappa == 0.9260
    assert result.chimera_rate_pct == 0.0
    assert result.dlq_rate_pct == 0.0
    assert result.pass_rate_pct > 50.0

    # Also test case_filter="pair_a"
    runner_a = AblationBenchmarkRunner(case_filter="pair_a", selected_configs=[1], runs=1, dry_run=False)
    result_a = runner_a.run_configuration(1)
    assert result_a.total_atoms == 110

    # Also test case_filter="pair_b"
    runner_b = AblationBenchmarkRunner(case_filter="pair_b", selected_configs=[1], runs=1, dry_run=False)
    result_b = runner_b.run_configuration(1)
    assert result_b.total_atoms == 110


def test_ablation_cluster_bootstrapped_kappa_computation_positive() -> None:
    """TC-BOOT-06: Verifies cluster-bootstrapped Cohen's Kappa computation on ablation benchmark runs.

    Exercises dry-run ablation execution with 2 runs across 220 atoms grouped into 10 step clusters,
    confirming non-null cluster standard error, valid percentile CI bounds, and inflation factor >= 1.0.
    """
    runner = AblationBenchmarkRunner(case_filter="both", selected_configs=[1], runs=2, dry_run=True)
    result = runner.run_configuration(1)

    assert result.config_id == 1
    assert result.total_atoms == 220
    assert result.runs == 2

    # Cluster-bootstrapped statistical assertions
    assert result.cluster_se is not None
    assert result.cluster_se > 0.0
    assert result.ci_cluster_lower is not None
    assert result.ci_cluster_upper is not None
    assert result.ci_cluster_lower < result.ci_cluster_upper
    assert result.se_inflation_factor is not None
    assert result.se_inflation_factor > 0.90

    # Physical trace verification where intra-cluster correlation yields inflation factor >= 1.0
    runner_phys = AblationBenchmarkRunner(case_filter="both", selected_configs=[1], runs=2, dry_run=False)
    result_phys = runner_phys.run_configuration(1)
    assert result_phys.cluster_se is not None and result_phys.cluster_se > 0.0
    assert result_phys.se_inflation_factor is not None
    assert result_phys.se_inflation_factor >= 1.0

    # Also directly test compute_cluster_bootstrapped_kappa_for_runs with fail-fast unmapped atom check
    evals1 = [
        AblationAtomEvaluationDTO(
            tda_id="atom_1",
            raw_is_true=True,
            source_quote="Quote 1",
            is_chimera=False,
            status=ExecutionStatus.PASSED,
        ),
        AblationAtomEvaluationDTO(
            tda_id="atom_2",
            raw_is_true=False,
            source_quote=None,
            is_chimera=False,
            status=ExecutionStatus.FAILED,
        ),
    ]
    evals2 = list(evals1)

    # Negative test: unmapped atom raises ValueError
    with pytest.raises(ValueError, match="Atom identifier 'atom_2' is not mapped to any step cluster."):
        compute_cluster_bootstrapped_kappa_for_runs(evals1, evals2, {"atom_1": "cluster_1"})

    # Positive test: mapped atoms calculate cluster bootstrap
    mapping = {"atom_1": "cluster_1", "atom_2": "cluster_2"}
    dto = compute_cluster_bootstrapped_kappa_for_runs(evals1, evals2, mapping, b_samples=100)
    assert dto.kappa == 1.0
    assert dto.num_clusters == 2


def test_format_table_5_markdown_with_cluster_ci_boundary() -> None:
    """TC-BOOT-07: Verifies Table 5 Markdown formatting for both populated cluster CIs and None boundaries."""
    # Case 1: Populated cluster CI
    res_populated = AblationConfigResultDTO(
        config_id=1,
        name="Full Quorum (Bo3 + Lexical Firewall)",
        runs=2,
        total_atoms=220,
        observed_agreement=96.36,
        cohens_kappa=0.9453,
        ci_lower=0.9120,
        ci_upper=0.9786,
        chimera_rate_pct=0.0,
        pass_rate_pct=52.7,
        dlq_rate_pct=0.0,
        cluster_se=0.0210,
        ci_cluster_lower=0.8950,
        ci_cluster_upper=0.9850,
        se_inflation_factor=1.15,
    )

    md_populated = format_ablation_table_markdown([res_populated], table_num=7)
    assert "| Experimental Configuration | Evaluated Atoms ($N$) |" in md_populated
    assert "| :--- | :---: |" in md_populated
    assert (
        "| **1. Full Quorum (Bo3 + Lexical Firewall)** | 220 | 96.36% | 0.9453 | [0.9120, 0.9786] (Cluster: [0.8950, 0.9850]) | 0.0% | 52.7% | 0.0% |"
        in md_populated
    )
    assert "Methodological Note on Cluster Bootstrap Resampling: In Table 7" in md_populated

    # Case 2: Boundary with None cluster metrics (e.g. single run)
    res_none = AblationConfigResultDTO(
        config_id=1,
        name="Full Quorum (Bo3 + Lexical Firewall)",
        runs=1,
        total_atoms=220,
        observed_agreement=0.0,
        cohens_kappa=0.0,
        ci_lower=0.0,
        ci_upper=0.0,
        chimera_rate_pct=0.0,
        pass_rate_pct=52.7,
        dlq_rate_pct=0.0,
        cluster_se=None,
        ci_cluster_lower=None,
        ci_cluster_upper=None,
        se_inflation_factor=None,
    )

    md_none = format_ablation_table_markdown([res_none], table_num=7)
    assert "| **1. Full Quorum (Bo3 + Lexical Firewall)** | 220 | 0.00% | 0.0000 | [0.0000, 0.0000] |" in md_none
    assert "(Cluster:" not in md_none
    assert "Methodological Note on Cluster Bootstrap Resampling" not in md_none


def test_compute_cluster_bootstrapped_kappa_empty_evals() -> None:
    """Verifies that empty evaluations return zero metrics without crashing."""
    res = compute_cluster_bootstrapped_kappa_for_runs([], [], atom_to_cluster={})
    assert res.kappa == 0.0
    assert res.num_clusters == 0
    assert res.cluster_se == 0.0


def test_ablation_config_all_flag() -> None:
    """Verifies that --config all executes all 5 configurations in order."""
    args = build_arg_parser().parse_args(["--dry-run", "--config", "all", "--runs", "1"])
    report = run_ablation_benchmark(args)
    assert len(report.config_results) == 5
    assert [c.config_id for c in report.config_results] == [1, 2, 3, 4, 5]


def test_ablation_export_manifest_standalone(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies standalone manifest export via CLI entrypoint."""
    out_file = str(tmp_path / "test_manifest.json")
    code = main(["--export-manifest", "beta_sem", "--manifest-output", out_file, "--manifest-sample-size", "5"])
    assert code == 0
    assert Path(out_file).exists()
    captured = capsys.readouterr()
    assert "Successfully exported audit manifest" in captured.out


def test_ablation_export_manifest_during_benchmark(tmp_path: Path) -> None:
    """Verifies manifest export combined with benchmark execution."""
    out_file = str(tmp_path / "test_manifest.csv")
    args = build_arg_parser().parse_args(
        [
            "--dry-run",
            "--config",
            "1",
            "--runs",
            "1",
            "--export-manifest",
            "chimera",
            "--manifest-format",
            "csv",
            "--manifest-output",
            out_file,
            "--manifest-sample-size",
            "5",
        ]
    )
    report = run_ablation_benchmark(args)
    assert report is not None
    assert Path(out_file).exists()


def test_ablation_main_cli_error_handling(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies graceful exception handling and stderr logging in main CLI entrypoint."""

    def _mock_run(*args: Any, **kwargs: Any) -> Any:
        raise ValueError("Simulated benchmark failure")

    monkeypatch.setattr("scripts.run_ablation_benchmark.run_ablation_benchmark", _mock_run)
    code = main(["--dry-run", "--config", "1"])
    assert code == 1
    captured = capsys.readouterr()
    assert "ERROR: Simulated benchmark failure" in captured.err


def test_ablation_cli_new_parameters_parity() -> None:
    """Verifies that all new parity arguments are correctly parsed."""
    parser = build_arg_parser()
    args = parser.parse_args(
        [
            "data/files/sample_inputs",
            "--inputs",
            "data/files/override_inputs",
            "--workflow",
            "wf_test_123",
            "--num-runs",
            "2",
            "--mode",
            "in-silico",
            "--dev",
            "--sample",
            "executive_coaching",
            "--tier",
            "balanced",
            "--strategies",
            "fast",
            "deep",
            "--providers",
            "ai_studio",
            "openai",
            "--compare-providers",
            "google",
            "openai",
            "--compare-strategies",
            "fast",
            "deep",
            "--concurrency",
            "10",
            "--seed",
            "backend_v2/seed/seed_data.json",
            "--trace",
            "data/files/traces/sample.json",
            "--output-format",
            "both",
        ]
    )

    assert args.inputs_target == "data/files/sample_inputs"
    assert args.inputs == "data/files/override_inputs"
    assert args.workflow == "wf_test_123"
    assert args.num_runs == 2
    assert args.mode == "in-silico"
    assert args.dev is True
    assert args.sample == "executive_coaching"
    assert args.tier == "balanced"
    assert args.strategies == ["fast", "deep"]
    assert args.providers == ["ai_studio", "openai"]
    assert args.compare_providers == ["google", "openai"]
    assert args.compare_strategies == ["fast", "deep"]
    assert args.concurrency == 10
    assert args.seed == "backend_v2/seed/seed_data.json"
    assert args.trace == "data/files/traces/sample.json"
    assert args.output_format == "both"


def test_ablation_mode_resolution_and_conflict() -> None:
    """Verifies mode resolution and fail-fast validation on conflicting dry-run and mode flags."""
    # 1. Conflict between --dry-run and --mode live
    parser = build_arg_parser()
    args_conflict = parser.parse_args(["--dry-run", "--mode", "live"])
    with pytest.raises(ValueError, match="Conflicting parameters"):
        run_ablation_benchmark(args_conflict)

    # 2. Runner conflict validation
    with pytest.raises(ValueError, match="Conflicting parameters"):
        AblationBenchmarkRunner(mode=AblationMode.LIVE, dry_run=True)


def test_print_ablation_telemetry_banner_smoke(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies that the structured ASCII banner prints expected metadata."""
    print_ablation_telemetry_banner(
        mode=AblationMode.IN_SILICO,
        tier=CognitiveTier.FAST,
        runs=2,
        case_filter="both",
        selected_configs=[1, 2, 3, 4, 5],
        concurrency=5,
        compare_providers=("google", "openai"),
        compare_strategies=("fast", "deep"),
    )
    out = capsys.readouterr().out
    assert "QUORUM COMPONENT ABLATION BENCHMARK" in out
    assert "IN-SILICO" in out
    assert "fast" in out
    assert "Cross-Model Test:   google (Run 1) vs openai (Run 2)" in out
    assert "Cross-Strategy:     fast (Run 1) vs deep (Run 2)" in out


def test_ablation_output_format_both(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies that --output-format both prints both markdown and json output."""
    out_file = str(tmp_path / "report")
    parser = build_arg_parser()
    args = parser.parse_args(
        [
            "--mode",
            "in-silico",
            "--config",
            "1",
            "--runs",
            "1",
            "--output-format",
            "both",
            "--output-file",
            out_file,
        ]
    )
    report = run_ablation_benchmark(args)
    assert report is not None
    assert (tmp_path / "report.json").exists()
    assert (tmp_path / "report.md").exists()


def test_resolve_grounding_source_text_file_and_dir(tmp_path: Path) -> None:
    """Verifies that _resolve_grounding_source_text loads from file and directory correctly."""
    # 1. Single file input
    sample_file = tmp_path / "doc.txt"
    sample_file.write_text("Tämä on yksittäinen tiedosto.", encoding="utf-8")

    runner_file = AblationBenchmarkRunner(inputs_path=sample_file)
    assert runner_file._resolve_grounding_source_text() == "Tämä on yksittäinen tiedosto."

    # 2. Directory with multiple files
    sample_dir = tmp_path / "docs_dir"
    sample_dir.mkdir()
    (sample_dir / "a.md").write_text("Ensimmäinen osa.", encoding="utf-8")
    (sample_dir / "b.txt").write_text("Toinen osa.", encoding="utf-8")

    runner_dir = AblationBenchmarkRunner(inputs_path=sample_dir)
    resolved = runner_dir._resolve_grounding_source_text()
    assert "Ensimmäinen osa." in resolved
    assert "Toinen osa." in resolved


def test_runner_live_mode_execution() -> None:
    """Verifies that AblationBenchmarkRunner correctly coordinates AblationLiveExecutor in live mode."""
    mock_executor = AsyncMock()

    sample_eval_1 = AblationAtomEvaluationDTO(
        tda_id="tda_pair_a_001",
        raw_is_true=True,
        source_quote="valid quote 1",
        is_chimera=False,
        status=ExecutionStatus.PASSED,
    )
    sample_eval_2 = AblationAtomEvaluationDTO(
        tda_id="tda_pair_b_002",
        raw_is_true=True,
        source_quote="valid quote 2",
        is_chimera=False,
        status=ExecutionStatus.PASSED,
    )
    mock_executor.evaluate_configuration_live.return_value = [sample_eval_1, sample_eval_2]

    runner = AblationBenchmarkRunner(mode=AblationMode.LIVE, runs=2)
    runner.live_executor = mock_executor
    runner.propositions = [
        AblationPropositionDTO(
            tda_id="tda_pair_a_001",
            step_id="step_1",
            claim_text="väite 1",
            expected_true=True,
            is_quote_valid_in_source=True,
        ),
        AblationPropositionDTO(
            tda_id="tda_pair_b_002",
            step_id="step_2",
            claim_text="väite 2",
            expected_true=True,
            is_quote_valid_in_source=True,
        ),
    ]

    result = runner.run_configuration(1)
    assert result.config_id == 1
    assert result.runs == 2
    assert result.total_atoms == 2
    assert result.cohens_kappa == 1.0
    assert mock_executor.evaluate_configuration_live.call_count == 2


def test_cli_main_json_and_both_outputs(capsys: pytest.CaptureFixture[str]) -> None:
    """Verifies that main CLI prints json when requested and handles csv manifest export."""
    # 1. Output format json
    code_json = main(["--dry-run", "--config", "1", "--runs", "1", "--output-format", "json"])
    assert code_json == 0
    captured_json = capsys.readouterr()
    assert '"config_results"' in captured_json.out

    # 2. Output format both
    code_both = main(["--dry-run", "--config", "1", "--runs", "1", "--output-format", "both"])
    assert code_both == 0
    captured_both = capsys.readouterr()
    assert "| Experimental Configuration |" in captured_both.out
    assert '"config_results"' in captured_both.out


def test_run_ablation_benchmark_with_compare_providers() -> None:
    """Verifies benchmark execution with compare_providers and compare_strategies configured."""
    parser = build_arg_parser()
    args = parser.parse_args(
        [
            "--dry-run",
            "--config",
            "1",
            "--runs",
            "2",
            "--compare-providers",
            "google",
            "openai",
            "--compare-strategies",
            "fast",
            "deep",
        ]
    )
    report = run_ablation_benchmark(args)
    assert len(report.config_results) == 1
    assert report.config_results[0].runs == 2


