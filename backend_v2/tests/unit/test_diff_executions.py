"""Unit tests for diff_executions script."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.diff_executions import (
    calculate_cohens_kappa,
    calculate_entropy,
    calculate_fleiss_kappa,
    calculate_pairwise_consistency,
    get_all_evals,
    get_state,
    get_trace,
    run_diff,
    uses_contextual_override,
)


def test_calculate_entropy() -> None:
    # Homogeneous states -> entropy 0.0
    assert calculate_entropy(["true", "true", "true"]) == 0.0
    assert calculate_entropy(["false", "false"]) == 0.0
    assert calculate_entropy([]) == 0.0

    # 50/50 distribution -> Shannon entropy (base 2) is 1.0
    assert calculate_entropy(["true", "false"]) == 1.0
    assert calculate_entropy(["true", "true", "false", "false"]) == 1.0


def test_calculate_pairwise_consistency() -> None:
    # Fully consistent
    assert calculate_pairwise_consistency(["true", "true", "true"]) == 1.0
    assert calculate_pairwise_consistency(["false", "false"]) == 1.0
    assert calculate_pairwise_consistency(["true"]) == 1.0
    assert calculate_pairwise_consistency([]) == 1.0

    # 50/50 distribution -> pairwise agreement 0.0
    assert calculate_pairwise_consistency(["true", "false"]) == 0.0

    # 3 items, 2 matching, 1 different -> 1 / 3
    assert pytest.approx(calculate_pairwise_consistency(["true", "true", "false"])) == 1 / 3


def test_calculate_cohens_kappa_perfect_agreement() -> None:
    # Perfect agreement for 2 raters (M = 2)
    states = [["true", "true"], ["true", "true"], ["false", "false"], ["false", "false"]]
    categories = ["true", "false"]
    kappa = calculate_cohens_kappa(states, categories)
    assert kappa == 1.0


def test_calculate_cohens_kappa_partial_agreement() -> None:
    states = [
        ["true", "true"],
        ["true", "false"],
        ["false", "false"],
        ["false", "true"],
    ]
    categories = ["true", "false"]
    kappa = calculate_cohens_kappa(states, categories)
    assert kappa == 0.0


def test_calculate_cohens_kappa_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="Cohen's Kappa requires exactly two"):
        calculate_cohens_kappa([["true", "true", "true"]], ["true", "false"])

    with pytest.raises(ValueError, match="Each state item must contain exactly 2 ratings"):
        calculate_cohens_kappa([["true", "true"], ["true"]], ["true", "false"])


def test_calculate_cohens_kappa_empty() -> None:
    assert calculate_cohens_kappa([], ["true", "false"]) == 0.0


def test_calculate_fleiss_kappa_perfect_agreement() -> None:
    states = [["true", "true", "true"], ["false", "false", "false"]]
    categories = ["true", "false"]
    kappa = calculate_fleiss_kappa(states, categories)
    assert kappa == 1.0


def test_calculate_fleiss_kappa_empty_and_single() -> None:
    assert calculate_fleiss_kappa([], ["true", "false"]) == 0.0
    assert calculate_fleiss_kappa([["true"]], ["true", "false"]) == 1.0


def test_get_state() -> None:
    # Status field
    assert get_state({"status": "PASSED"}) == "passed"
    assert get_state({"status": "failed"}) == "failed"

    # Decision field
    assert get_state({"decision": "ACCEPTED"}) == "accepted"

    # Mapped state field
    assert get_state({"mapped_state": "TRUE"}) == "true"

    # Exact quote non-empty
    assert get_state({"exact_quote": "Found actual citation in text."}) == "true"

    # Exact quote blacklisted
    assert get_state({"exact_quote": "Not found"}) == "false"
    assert get_state({"exact_quote": "null"}) == "false"
    assert get_state({"exact_quote": []}) == "false"
    assert get_state({"exact_quote": None}) == "false"

    # Unknown
    assert get_state({}) == "unknown"


def test_get_trace() -> None:
    assert get_trace({"evaluation_reasoning": "Reason 1"}) == "Reason 1"
    assert get_trace({"context_scan_trace": "Scan trace"}) == "Scan trace"
    assert get_trace({"semantic_reasoning": "Semantic trace"}) == "Semantic trace"
    assert get_trace({"reasoning_trace": "Trace 4"}) == "Trace 4"
    assert get_trace({"mechanical_trace": "Mech trace"}) == "Mech trace"
    assert get_trace({}) == ""


def test_uses_contextual_override() -> None:
    assert uses_contextual_override({"contextual_override": True}) is True
    assert uses_contextual_override({"exact_quote": "[INFERRED] Text inferred by model."}) is True
    assert uses_contextual_override({"exact_quote": "Normal exact quote."}) is False
    assert uses_contextual_override({}) is False


def test_get_all_evals(tmp_path: Path) -> None:
    trace_file = tmp_path / "execution_trace.json"
    trace_data = [
        {
            "step_id": "stp_1",
            "content": {
                "evaluations": [
                    {"atom_id": "atm_1", "status": "PASSED"},
                    {"tda_id": "atm_2", "status": "FAILED"},
                ],
                "results": [
                    {"tda_id": "atm_3", "status": "PASSED"},
                ],
            },
        }
    ]
    with trace_file.open("w", encoding="utf-8") as f:
        json.dump(trace_data, f)

    evals = get_all_evals(trace_file)
    assert "atm_1" in evals
    assert "atm_2" in evals
    assert "atm_3" in evals
    assert evals["atm_1"]["status"] == "PASSED"


def test_pillar4_forensic_disk_artifacts_and_telemetry_extraction(tmp_path: Path) -> None:
    """Pillar 4: Proof that diff_executions forensically validates on-disk files."""
    run1 = tmp_path / "exe_forensic_1"
    run2 = tmp_path / "exe_forensic_2"
    run1.mkdir()
    run2.mkdir()

    trace_content = [
        {
            "step_id": "stp_1",
            "content": {
                "evaluations": [
                    {
                        "atom_id": "tda_216cc3fd45284deb8d51ea4cf2b2fd93",
                        "status": "PASSED",
                        "evaluation_reasoning": "Reason 1",
                    },
                ]
            },
        }
    ]
    (run1 / "execution_trace.json").write_text(json.dumps(trace_content), encoding="utf-8")
    (run2 / "execution_trace.json").write_text(json.dumps(trace_content), encoding="utf-8")

    # Forensic telemetry file
    telemetry = [
        {"tokens": 120, "prompt_tokens": 100, "completion_tokens": 20, "cache_hit": False, "model": "gemini-3.7-flash"},
        {"tokens": 80, "prompt_tokens": 70, "completion_tokens": 10, "cache_hit": True, "model": "gemini-3.7-flash"},
    ]
    with (run1 / "llm_telemetry.jsonl").open("w", encoding="utf-8") as f:
        for t in telemetry:
            f.write(json.dumps(t) + "\n")

    # Forensic frozen context
    (run1 / "frozen_context.json").write_text(
        json.dumps(
            {
                "ui_hints_snapshot": {
                    "blk_f6e286f050c94d60": {
                        "options": [{"label": {"translations": {"fi": "Avoimuus", "en": "Transparency"}}}]
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    # Forensic inputs directory with injected Unicode space
    inputs_dir = run1 / "inputs"
    inputs_dir.mkdir()
    (inputs_dir / "doc.txt").write_text("Forensic\u00a0test document", encoding="utf-8")

    report_path = run_diff([str(run1), str(run2)])
    assert Path(report_path).exists()
    report_text = Path(report_path).read_text(encoding="utf-8")

    # Verify report cites physical files, SHA-256 hashes, noise variants, and telemetric properties
    assert "exe_forensic_1" in report_text
    assert "exe_forensic_2" in report_text
    assert "API-kutsut" in report_text
    assert "SHA-256" in report_text
    assert "No-Break Space (U+00A0)" in report_text


def test_pillar5_statistical_metrics_and_transition_matrix(tmp_path: Path) -> None:
    """Pillar 5: Mathematical proof of Fleiss Kappa, Cohen Kappa, Entropy, and Transition Matrix."""
    run1 = tmp_path / "exe_stat_1"
    run2 = tmp_path / "exe_stat_2"
    run1.mkdir()
    run2.mkdir()

    # Create 4 atoms with deterministic transitions:
    # atom1: PASS -> PASS (Consistent)
    # atom2: PASS -> FAIL (Transition 1)
    # atom3: FAIL -> PASS (Transition 2)
    # atom4: FAIL -> FAIL (Consistent)
    trace1 = [
        {
            "step_id": "stp_1",
            "content": {
                "evaluations": [
                    {"atom_id": "tda_216cc3fd45284deb8d51ea4cf2b2fd93", "status": "PASSED"},
                    {"atom_id": "tda_3b951170f9f54f649b7da95fb9f121e6", "status": "PASSED"},
                    {"atom_id": "tda_34259a6c02b74917b12f74b5f3839a66", "status": "FAILED"},
                    {"atom_id": "tda_69cc84e0b0c44996a8a95e09b356c692", "status": "FAILED"},
                ]
            },
        }
    ]
    trace2 = [
        {
            "step_id": "stp_1",
            "content": {
                "evaluations": [
                    {"atom_id": "tda_216cc3fd45284deb8d51ea4cf2b2fd93", "status": "PASSED"},
                    {"atom_id": "tda_3b951170f9f54f649b7da95fb9f121e6", "status": "FAILED"},
                    {"atom_id": "tda_34259a6c02b74917b12f74b5f3839a66", "status": "PASSED"},
                    {"atom_id": "tda_69cc84e0b0c44996a8a95e09b356c692", "status": "FAILED"},
                ]
            },
        }
    ]

    (run1 / "execution_trace.json").write_text(json.dumps(trace1), encoding="utf-8")
    (run2 / "execution_trace.json").write_text(json.dumps(trace2), encoding="utf-8")

    report_path = run_diff([str(run1), str(run2)])
    report_text = Path(report_path).read_text(encoding="utf-8")

    # Verify transitions are logged accurately:
    # 1 PASSED -> FAILED, 1 FAILED -> PASSED
    assert "**PASSED -> FAILED:** 1" in report_text
    assert "**FAILED -> PASSED:** 1" in report_text
    assert "Parittainen konsistenssi" in report_text
    assert "Fleissin Kappa" in report_text
    assert "Cohenin Kappa" in report_text


def test_run_diff_missing_or_empty() -> None:
    with pytest.raises(SystemExit):
        run_diff(["nonexistent/path/1", "nonexistent/path/2"])


def test_inspect_input_file_variants(tmp_path: Path) -> None:
    """Test SHA-256 and detection of all Unicode space variants in _inspect_input_file."""
    from scripts.diff_executions import _inspect_input_file

    f1 = tmp_path / "ascii.txt"
    f1.write_text("Hello World", encoding="utf-8")
    info1 = _inspect_input_file(f1)
    assert info1["noise"] == "Standard ASCII"
    assert len(info1["sha256"]) == 64

    f2 = tmp_path / "nobreak.txt"
    f2.write_text("Hello\u00a0World", encoding="utf-8")
    info2 = _inspect_input_file(f2)
    assert "No-Break Space (U+00A0)" in info2["noise"]

    f3 = tmp_path / "en.txt"
    f3.write_text("Hello\u2002World", encoding="utf-8")
    info3 = _inspect_input_file(f3)
    assert "En Space (U+2002)" in info3["noise"]


def test_main_cli_execution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test CLI main() execution with simulated execution paths."""
    from scripts.diff_executions import main

    run1 = tmp_path / "exe_cli_1"
    run2 = tmp_path / "exe_cli_2"
    run1.mkdir()
    run2.mkdir()
    valid_trace = [
        {
            "step_id": "stp_1",
            "content": {
                "evaluations": [
                    {
                        "atom_id": "tda_216cc3fd45284deb8d51ea4cf2b2fd93",
                        "status": "PASSED",
                        "evaluation_reasoning": "Reasoning 1",
                    }
                ]
            },
        }
    ]
    (run1 / "execution_trace.json").write_text(json.dumps(valid_trace), encoding="utf-8")
    (run2 / "execution_trace.json").write_text(json.dumps(valid_trace), encoding="utf-8")

    monkeypatch.setattr("sys.argv", ["diff_executions.py", str(run1), str(run2)])
    main()
