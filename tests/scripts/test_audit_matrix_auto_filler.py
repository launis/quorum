"""Tests for the Neuro-Symbolic Audit Matrix auto-filler."""

import json
from pathlib import Path

import pytest
from scripts.audit_matrix_auto_filler import main


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
