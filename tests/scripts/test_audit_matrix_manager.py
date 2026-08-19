"""Tests for audit_matrix_manager.py."""

import argparse
import json
from pathlib import Path

import pytest
from scripts.audit_matrix_manager import (
    check_anti_laziness,
    check_conflicting_file_references,
    cmd_generate,
    cmd_verify,
    extract_rule_blocks,
    get_repo_root,
    main,
)


def test_check_anti_laziness_short() -> None:
    """Test that a short justification fails."""
    err = check_anti_laziness("Too short.")
    assert err is not None
    assert "Justification too short" in err


def test_check_anti_laziness_few_words() -> None:
    """Test that justification with few words fails."""
    err = check_anti_laziness("ThisIsAVeryLongWordThatIsLongerThanTwentyFiveCharacters.")
    assert err is not None
    assert "Justification lacks detail" in err


def test_check_anti_laziness_pass() -> None:
    """Test that a valid justification passes."""
    err = check_anti_laziness("This is a sufficiently long and detailed justification.")
    assert err is None


def test_check_conflicting_file_references_allowed() -> None:
    """Test that valid/allowed file mentions in justification pass without error."""
    err = check_conflicting_file_references(
        "Adheres to constraints in settings.py and enums.py line 45.",
        "backend_v2/services/execution.py",
    )
    assert err is None


def test_check_conflicting_file_references_conflicting() -> None:
    """Test that citing an unrelated code file in justification triggers an anchor error."""
    err = check_conflicting_file_references(
        "Implemented strictly inside auth_service.py at line 120.",
        "backend_v2/services/execution.py",
    )
    assert err is not None
    assert "Conflicting file reference 'auth_service.py' detected" in err


def test_extract_rule_blocks(tmp_path: Path) -> None:
    """Test extracting rule blocks from a markdown file."""
    md_file = tmp_path / "rules.md"
    md_file.write_text(
        """
<rule_block id="test_rule">
    <banned_pattern>banned</banned_pattern>
    <mandatory_pattern>mandatory</mandatory_pattern>
</rule_block>
    """,
        encoding="utf-8",
    )

    rules = extract_rule_blocks(md_file)
    assert len(rules) == 1
    assert rules[0]["rule_id"] == "test_rule"
    assert rules[0]["banned_pattern"] == "banned"
    assert rules[0]["mandatory_pattern"] == "mandatory"


def test_extract_rule_blocks_nonexistent_file(tmp_path: Path) -> None:
    """Test extract_rule_blocks on nonexistent file exits with code 1."""
    with pytest.raises(SystemExit) as exc_info:
        extract_rule_blocks(tmp_path / "nonexistent.md")
    assert exc_info.value.code == 1


def test_get_repo_root() -> None:
    """Test getting repo root."""
    root = get_repo_root()
    assert root.name in ("quorum", "antigravity-ide")


def test_cmd_generate_invalid_type() -> None:
    """Test generating with invalid type raises SystemExit(1)."""
    args = argparse.Namespace(type="invalid", target="backend_v2/settings.py")
    with pytest.raises(SystemExit) as exc_info:
        cmd_generate(args)
    assert exc_info.value.code == 1


def test_cmd_generate_empty_target() -> None:
    """Test generating with empty target raises SystemExit(1)."""
    args = argparse.Namespace(type="backend", target="")
    with pytest.raises(SystemExit) as exc_info:
        cmd_generate(args)
    assert exc_info.value.code == 1


def test_cmd_generate_backend_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test generate creates valid audit_matrix.json with target, timestamp, and PENDING rules."""
    monkeypatch.setattr("scripts.audit_matrix_manager.get_repo_root", lambda: tmp_path)
    rules_dir = tmp_path / ".agents" / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "00-antigravity-core.md").write_text(
        '<rule_block id="rule_core"><banned_pattern>b1</banned_pattern><mandatory_pattern>m1</mandatory_pattern></rule_block>',
        encoding="utf-8",
    )
    (rules_dir / "01-python-backend.md").write_text(
        '<rule_block id="rule_backend"><banned_pattern>b2</banned_pattern><mandatory_pattern>m2</mandatory_pattern></rule_block>',
        encoding="utf-8",
    )

    args = argparse.Namespace(type="backend", target="backend_v2/settings.py")
    cmd_generate(args)

    out_file = tmp_path / "tmp" / "audit_matrix.json"
    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["target_file"] == "backend_v2/settings.py"
    assert "generated_at" in data
    assert len(data["rules"]) == 2
    assert all(r["status"] == "PENDING" for r in data["rules"])
    assert all(r["justification"] == "" for r in data["rules"])


def test_cmd_generate_frontend_success(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test generate creates frontend audit matrix."""
    monkeypatch.setattr("scripts.audit_matrix_manager.get_repo_root", lambda: tmp_path)
    rules_dir = tmp_path / ".agents" / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "00-antigravity-core.md").write_text(
        '<rule_block id="rule_core"><banned_pattern>b1</banned_pattern><mandatory_pattern>m1</mandatory_pattern></rule_block>',
        encoding="utf-8",
    )
    (rules_dir / "02_flutter_desktop.md").write_text(
        '<rule_block id="rule_flutter"><banned_pattern>b3</banned_pattern><mandatory_pattern>m3</mandatory_pattern></rule_block>',
        encoding="utf-8",
    )

    args = argparse.Namespace(type="frontend", target="client_app_v2/lib/main.dart")
    cmd_generate(args)

    out_file = tmp_path / "tmp" / "audit_matrix.json"
    assert out_file.exists()
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert data["target_file"] == "client_app_v2/lib/main.dart"


def test_cmd_verify_nonexistent_file() -> None:
    """Test verify on missing file exits with code 1."""
    args = argparse.Namespace(file="tmp/nonexistent_matrix.json", target="dummy.py")
    with pytest.raises(SystemExit) as exc_info:
        cmd_verify(args)
    assert exc_info.value.code == 1


def test_cmd_verify_invalid_json(tmp_path: Path) -> None:
    """Test verify on malformed JSON exits with code 1."""
    mat_file = tmp_path / "matrix.json"
    mat_file.write_text("{bad json", encoding="utf-8")
    args = argparse.Namespace(file=str(mat_file), target="dummy.py")
    with pytest.raises(SystemExit) as exc_info:
        cmd_verify(args)
    assert exc_info.value.code == 1


def test_cmd_verify_empty_target_in_matrix(tmp_path: Path) -> None:
    """Test verify when target_file is empty in matrix exits with code 1."""
    mat_file = tmp_path / "matrix.json"
    mat_file.write_text(json.dumps({"target_file": "", "rules": [{"rule_id": "r1"}]}), encoding="utf-8")
    args = argparse.Namespace(file=str(mat_file), target="dummy.py")
    with pytest.raises(SystemExit) as exc_info:
        cmd_verify(args)
    assert exc_info.value.code == 1


def test_cmd_verify_missing_target_cli(tmp_path: Path) -> None:
    """Test verify when --target CLI argument is empty exits with code 1."""
    mat_file = tmp_path / "matrix.json"
    mat_file.write_text(json.dumps({"target_file": "dummy.py", "rules": [{"rule_id": "r1"}]}), encoding="utf-8")
    args = argparse.Namespace(file=str(mat_file), target="")
    with pytest.raises(SystemExit) as exc_info:
        cmd_verify(args)
    assert exc_info.value.code == 1


def test_cmd_verify_target_mismatch(tmp_path: Path) -> None:
    """Test verify when target_file does not match CLI target exits with code 1."""
    mat_file = tmp_path / "matrix.json"
    mat_file.write_text(json.dumps({"target_file": "file_a.py", "rules": [{"rule_id": "r1"}]}), encoding="utf-8")
    args = argparse.Namespace(file=str(mat_file), target="file_b.py")
    with pytest.raises(SystemExit) as exc_info:
        cmd_verify(args)
    assert exc_info.value.code == 1


def test_cmd_verify_empty_rules(tmp_path: Path) -> None:
    """Test verify when rules list is empty exits with code 1."""
    mat_file = tmp_path / "matrix.json"
    mat_file.write_text(json.dumps({"target_file": "dummy.py", "rules": []}), encoding="utf-8")
    args = argparse.Namespace(file=str(mat_file), target="dummy.py")
    with pytest.raises(SystemExit) as exc_info:
        cmd_verify(args)
    assert exc_info.value.code == 1


def test_cmd_verify_pending_status(tmp_path: Path) -> None:
    """Test verify with PENDING status fails."""
    mat_file = tmp_path / "matrix.json"
    matrix = {
        "target_file": "dummy.py",
        "rules": [
            {
                "rule_id": "rule_1",
                "status": "PENDING",
                "justification": "",
            }
        ],
    }
    mat_file.write_text(json.dumps(matrix), encoding="utf-8")
    args = argparse.Namespace(file=str(mat_file), target="dummy.py")
    with pytest.raises(SystemExit) as exc_info:
        cmd_verify(args)
    assert exc_info.value.code == 1


def test_cmd_verify_invalid_status(tmp_path: Path) -> None:
    """Test verify with invalid status fails."""
    mat_file = tmp_path / "matrix.json"
    matrix = {
        "target_file": "dummy.py",
        "rules": [
            {
                "rule_id": "rule_1",
                "status": "INVALID",
                "justification": "This is a sufficiently long justification for testing purposes.",
            }
        ],
    }
    mat_file.write_text(json.dumps(matrix), encoding="utf-8")
    args = argparse.Namespace(file=str(mat_file), target="dummy.py")
    with pytest.raises(SystemExit) as exc_info:
        cmd_verify(args)
    assert exc_info.value.code == 1


def test_cmd_verify_duplicate_pass_justification(tmp_path: Path) -> None:
    """Test verify fails when two PASS rules share identical justification."""
    mat_file = tmp_path / "matrix.json"
    matrix = {
        "target_file": "dummy.py",
        "rules": [
            {
                "rule_id": "rule_1",
                "status": "PASS",
                "justification": "Exact duplicate justification string for code checking in dummy.py.",
            },
            {
                "rule_id": "rule_2",
                "status": "PASS",
                "justification": "Exact duplicate justification string for code checking in dummy.py.",
            },
        ],
    }
    mat_file.write_text(json.dumps(matrix), encoding="utf-8")
    args = argparse.Namespace(file=str(mat_file), target="dummy.py")
    with pytest.raises(SystemExit) as exc_info:
        cmd_verify(args)
    assert exc_info.value.code == 1


def test_cmd_verify_multiple_na_allowed(tmp_path: Path) -> None:
    """Test verify passes when multiple NA rules share standard justification (<= 40)."""
    mat_file = tmp_path / "matrix.json"
    matrix = {
        "target_file": "dummy.py",
        "rules": [
            {
                "rule_id": f"rule_na_{i}",
                "status": "NA",
                "justification": "This rule is strictly not applicable for this standalone module.",
            }
            for i in range(10)
        ],
    }
    mat_file.write_text(json.dumps(matrix), encoding="utf-8")
    args = argparse.Namespace(file=str(mat_file), target="dummy.py")
    with pytest.raises(SystemExit) as exc_info:
        cmd_verify(args)
    assert exc_info.value.code == 0


def test_cmd_verify_na_exceeds_threshold(tmp_path: Path) -> None:
    """Test verify fails when identical NA justification is repeated > 40 times."""
    mat_file = tmp_path / "matrix.json"
    matrix = {
        "target_file": "dummy.py",
        "rules": [
            {
                "rule_id": f"rule_na_{i}",
                "status": "NA",
                "justification": "This rule is strictly not applicable for this standalone module.",
            }
            for i in range(42)
        ],
    }
    mat_file.write_text(json.dumps(matrix), encoding="utf-8")
    args = argparse.Namespace(file=str(mat_file), target="dummy.py")
    with pytest.raises(SystemExit) as exc_info:
        cmd_verify(args)
    assert exc_info.value.code == 1


def test_cmd_verify_conflicting_file_reference(tmp_path: Path) -> None:
    """Test verify fails when justification references a conflicting code file."""
    mat_file = tmp_path / "matrix.json"
    matrix = {
        "target_file": "dummy.py",
        "rules": [
            {
                "rule_id": "rule_1",
                "status": "PASS",
                "justification": "Verified code implementation inside conflicting_file.py at line 30.",
            }
        ],
    }
    mat_file.write_text(json.dumps(matrix), encoding="utf-8")
    args = argparse.Namespace(file=str(mat_file), target="dummy.py")
    with pytest.raises(SystemExit) as exc_info:
        cmd_verify(args)
    assert exc_info.value.code == 1


def test_cmd_verify_happy_path(tmp_path: Path) -> None:
    """Test verify passes with exit code 0 when all rules are valid and unique."""
    mat_file = tmp_path / "matrix.json"
    matrix = {
        "target_file": "dummy.py",
        "rules": [
            {
                "rule_id": "rule_1",
                "status": "PASS",
                "justification": "Verified line 10 in dummy.py complies with strict encapsulation invariants.",
            },
            {
                "rule_id": "rule_2",
                "status": "FAIL",
                "justification": "Line 25 in dummy.py violates Fail-Fast AppException raising contract.",
            },
            {
                "rule_id": "rule_3",
                "status": "NA",
                "justification": "Rule is strictly not applicable for dummy.py as it has no LLM prompt.",
            },
        ],
    }
    mat_file.write_text(json.dumps(matrix), encoding="utf-8")
    args = argparse.Namespace(file=str(mat_file), target="dummy.py")
    with pytest.raises(SystemExit) as exc_info:
        cmd_verify(args)
    assert exc_info.value.code == 0


def test_main_cli_dispatch(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main CLI entrypoint for generate and verify."""
    monkeypatch.setattr("scripts.audit_matrix_manager.get_repo_root", lambda: tmp_path)
    rules_dir = tmp_path / ".agents" / "rules"
    rules_dir.mkdir(parents=True)
    (rules_dir / "00-antigravity-core.md").write_text(
        '<rule_block id="rule_core"><banned_pattern>b1</banned_pattern><mandatory_pattern>m1</mandatory_pattern></rule_block>',
        encoding="utf-8",
    )
    (rules_dir / "01-python-backend.md").write_text(
        '<rule_block id="rule_backend"><banned_pattern>b2</banned_pattern><mandatory_pattern>m2</mandatory_pattern></rule_block>',
        encoding="utf-8",
    )

    # Test generate via main
    monkeypatch.setattr(
        "sys.argv",
        [
            "audit_matrix_manager.py",
            "generate",
            "--type",
            "backend",
            "--target",
            "backend_v2/settings.py",
        ],
    )
    main()

    out_file = tmp_path / "tmp" / "audit_matrix.json"
    assert out_file.exists()

    # Populate valid entries
    data = json.loads(out_file.read_text(encoding="utf-8"))
    for idx, r in enumerate(data["rules"]):
        r["status"] = "PASS"
        r["justification"] = f"Substantive unique evidence {idx} in backend_v2/settings.py at line 10."
    out_file.write_text(json.dumps(data), encoding="utf-8")

    # Test verify via main
    monkeypatch.setattr(
        "sys.argv",
        [
            "audit_matrix_manager.py",
            "verify",
            "--file",
            str(out_file),
            "--target",
            "backend_v2/settings.py",
        ],
    )
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0

