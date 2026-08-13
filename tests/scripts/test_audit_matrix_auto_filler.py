"""Tests for the Neuro-Symbolic Audit Matrix auto-filler."""

import json
from pathlib import Path

from scripts.audit_matrix_auto_filler import main


def test_auto_filler_pass(tmp_path: Path, monkeypatch) -> None:
    """Test that the auto filler correctly fills the matrix with PASS and FAIL."""
    # Create a dummy matrix file
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

    # Mock CLI arguments
    monkeypatch.setattr(
        "sys.argv",
        [
            "audit_matrix_auto_filler.py",
            "--file",
            str(matrix_file),
            "--fail",
            "rule_2",
            "--na",
            "rule_3",
        ],
    )

    # Run the auto-filler
    main()

    # Verify the output
    result = json.loads(matrix_file.read_text(encoding="utf-8"))
    rules = result["rules"]

    assert rules[0]["rule_id"] == "rule_1"
    assert rules[0]["status"] == "PASS"
    assert "Automated PASS for rule rule_1" in rules[0]["justification"]

    assert rules[1]["rule_id"] == "rule_2"
    assert rules[1]["status"] == "FAIL"
    assert "Manual override FAIL for rule rule_2" in rules[1]["justification"]

    assert rules[2]["rule_id"] == "rule_3"
    assert rules[2]["status"] == "NA"
    assert "Manual override NA for rule rule_3" in rules[2]["justification"]
