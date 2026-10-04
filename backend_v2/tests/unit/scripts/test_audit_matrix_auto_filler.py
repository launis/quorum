"""Tests for the Neuro-Symbolic Audit Matrix auto-filler."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.audit_matrix_auto_filler import (
    AutoFillMatrixDTO,
    AutoFillRuleDTO,
    auto_fill_matrix,
    main,
)


def test_auto_filler_pass(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that the auto filler correctly fills the matrix with PASS, FAIL, and NA."""
    matrix_file = tmp_path / "audit_matrix.json"
    dummy_matrix = {
        "target_file": "dummy.py",
        "rules": [
            {"rule_id": "rule_1", "status": "PENDING", "justification": ""},
            {"rule_id": "rule_2", "status": "PENDING", "justification": ""},
            {"rule_id": "rule_3", "status": "PENDING", "justification": ""},
        ],
    }
    matrix_file.write_text(json.dumps(dummy_matrix), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "audit_matrix_auto_filler.py",
            "--file",
            str(matrix_file),
            "--target",
            "backend_v2/settings.py",
            "--fail",
            "rule_2",
            "--na",
            "rule_3",
        ],
    )

    main()

    result = json.loads(matrix_file.read_text(encoding="utf-8"))
    assert result["target_file"] == "backend_v2/settings.py"
    rules = result["rules"]

    assert rules[0]["rule_id"] == "rule_1"
    assert rules[0]["status"] == "PASS"
    assert "Automated PASS for rule rule_1 in backend_v2/settings.py" in rules[0]["justification"]

    assert rules[1]["rule_id"] == "rule_2"
    assert rules[1]["status"] == "FAIL"
    assert "Manual override FAIL for rule rule_2 in backend_v2/settings.py" in rules[1]["justification"]

    assert rules[2]["rule_id"] == "rule_3"
    assert rules[2]["status"] == "NA"
    assert "Manual override NA for rule rule_3" in rules[2]["justification"]


def test_auto_filler_missing_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test auto-filler exits with code 1 on missing file."""
    monkeypatch.setattr(
        "sys.argv",
        [
            "audit_matrix_auto_filler.py",
            "--file",
            str(tmp_path / "missing.json"),
        ],
    )
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_auto_filler_empty_rules(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test auto-filler exits with code 1 on empty rules."""
    matrix_file = tmp_path / "audit_matrix.json"
    matrix_file.write_text(json.dumps({"target_file": "dummy.py", "rules": []}), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "audit_matrix_auto_filler.py",
            "--file",
            str(matrix_file),
        ],
    )
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_auto_filler_corrupt_json(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test auto-filler exits with code 1 on corrupt JSON."""
    matrix_file = tmp_path / "audit_matrix.json"
    matrix_file.write_text("{bad", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "audit_matrix_auto_filler.py",
            "--file",
            str(matrix_file),
        ],
    )
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1


def test_auto_fill_matrix_pure_function() -> None:
    """Test pure auto_fill_matrix function directly with DTO models."""
    input_dto = AutoFillMatrixDTO(
        target_file="scripts/target.py",
        generated_at="2026-10-04T00:00:00Z",
        rules=[
            AutoFillRuleDTO(rule_id="r1"),
            AutoFillRuleDTO(rule_id="r2"),
            AutoFillRuleDTO(rule_id="r3"),
        ],
    )

    output_dto = auto_fill_matrix(
        matrix_dto=input_dto,
        target_override="backend_v2/services/execution.py",
        fail_rules=["r1"],
        na_rules=["r2"],
    )

    assert output_dto.target_file == "backend_v2/services/execution.py"
    assert len(output_dto.rules) == 3
    assert output_dto.rules[0].status == "FAIL"
    assert "Manual override FAIL for rule r1" in output_dto.rules[0].justification
    assert output_dto.rules[1].status == "NA"
    assert "Manual override NA for rule r2" in output_dto.rules[1].justification
    assert output_dto.rules[2].status == "PASS"
    assert "Automated PASS for rule r3" in output_dto.rules[2].justification


def test_auto_fill_matrix_empty_target_fallback() -> None:
    """Test fallback to 'target' when both target_file and override are empty."""
    input_dto = AutoFillMatrixDTO(
        target_file="   ",
        generated_at="",
        rules=[AutoFillRuleDTO(rule_id="r_empty")],
    )

    output_dto = auto_fill_matrix(
        matrix_dto=input_dto,
        target_override="",
    )

    assert output_dto.target_file == "target"
    assert output_dto.rules[0].status == "PASS"
    assert "in target." in output_dto.rules[0].justification


def test_auto_filler_main_default_args(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main execution with default target from file and no overrides."""
    matrix_file = tmp_path / "default_matrix.json"
    dummy_matrix = {
        "target_file": "backend_v2/default.py",
        "rules": [
            {"rule_id": "rule_def", "status": "PENDING", "justification": ""},
        ],
    }
    matrix_file.write_text(json.dumps(dummy_matrix), encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        [
            "audit_matrix_auto_filler.py",
            "--file",
            str(matrix_file),
        ],
    )

    main()

    result = json.loads(matrix_file.read_text(encoding="utf-8"))
    assert result["target_file"] == "backend_v2/default.py"
    assert result["rules"][0]["status"] == "PASS"
    assert "Automated PASS for rule rule_def in backend_v2/default.py" in result["rules"][0]["justification"]
