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


def test_run_diff_on_mock_directories(tmp_path: Path) -> None:
    run1_dir = tmp_path / "exe_1"
    run2_dir = tmp_path / "exe_2"
    run1_dir.mkdir()
    run2_dir.mkdir()

    trace1 = [
        {
            "step_id": "stp_1",
            "content": {
                "evaluations": [
                    {
                        "atom_id": "tda_216cc3fd45284deb8d51ea4cf2b2fd93",
                        "status": "PASSED",
                        "evaluation_reasoning": "Reason 1",
                    },
                    {
                        "atom_id": "tda_3b951170f9f54f649b7da95fb9f121e6",
                        "status": "PASSED",
                        "contextual_override": True,
                        "evaluation_reasoning": "Reason 2",
                    },
                ]
            },
        }
    ]
    trace2 = [
        {
            "step_id": "stp_1",
            "content": {
                "evaluations": [
                    {
                        "atom_id": "tda_216cc3fd45284deb8d51ea4cf2b2fd93",
                        "status": "PASSED",
                        "evaluation_reasoning": "Reason 1 matching",
                    },
                    {
                        "atom_id": "tda_3b951170f9f54f649b7da95fb9f121e6",
                        "status": "FAILED",
                        "evaluation_reasoning": "Reason 2 mismatch",
                    },
                ]
            },
        }
    ]

    with (run1_dir / "execution_trace.json").open("w", encoding="utf-8") as f:
        json.dump(trace1, f)
    with (run2_dir / "execution_trace.json").open("w", encoding="utf-8") as f:
        json.dump(trace2, f)

    # Add mock telemetry
    telem1 = [{"tokens": 150, "cache_hit": True}, {"tokens": 200, "cache_hit": False}]
    with (run1_dir / "llm_telemetry.jsonl").open("w", encoding="utf-8") as f:
        for row in telem1:
            f.write(json.dumps(row) + "\n")

    # Add mock frozen_context
    frozen_ctx = {
        "ui_hints_snapshot": {
            "blk_f921c7c0989b47e8": {"options": [{"label": {"translations": {"fi": "Luovuus ja syvyys"}}}]}
        }
    }
    with (run1_dir / "frozen_context.json").open("w", encoding="utf-8") as f:
        json.dump(frozen_ctx, f)

    # Optional inputs dir
    inputs1 = run1_dir / "inputs"
    inputs1.mkdir()
    (inputs1 / "test_input.txt").write_text("Test", encoding="utf-8")

    report_path = run_diff([str(run1_dir), str(run2_dir)])
    assert Path(report_path).exists()
    report_text = Path(report_path).read_text(encoding="utf-8")
    assert "Mittauksen Luotettavuus ja Vakausraportti" in report_text
    assert "tda_3b951170f9f54f649b7da95fb9f121e6" in report_text


def test_run_diff_missing_or_empty() -> None:
    with pytest.raises(SystemExit):
        run_diff(["nonexistent/path/1", "nonexistent/path/2"])
