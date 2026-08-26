"""Unit tests for the neuro-symbolic audit matrix manager (scripts/audit_matrix_manager.py).

Tests all verification gates: matrix generation, AST evidence binding, anti-rubber-stamping heuristics,
target lock, duplicate justification rejection, CLI execution, and zero reflection.
"""

from __future__ import annotations

import argparse
import ast
from datetime import UTC, datetime
from pathlib import Path

import pytest

from scripts._ast_guardrails import GuardrailSeverity, GuardrailViolation
from scripts.audit_matrix_manager import (
    AuditMatrixDTO,
    AuditRuleEntryDTO,
    AuditRuleStatus,
    EvidenceType,
    check_anti_laziness,
    check_conflicting_file_references,
    cmd_generate,
    cmd_verify,
    extract_rule_blocks,
    main,
)


def test_audit_matrix_dto_strictness() -> None:
    """Test AuditMatrixDTO and AuditRuleEntryDTO strict Pydantic V2 schemas."""
    rule_entry = AuditRuleEntryDTO(
        rule_id="the_duct_tape_ban",
        banned_pattern="except Exception: pass",
        mandatory_pattern="AppException",
        status=AuditRuleStatus.PASS,
        evidence_type=EvidenceType.STATIC_AST,
        ast_violations=[],
        justification="Strictly raises typed AppException on line 45.",
    )

    matrix = AuditMatrixDTO(
        target_file="backend_v2/services/execution.py",
        generated_at=datetime.now(UTC).isoformat(),
        rules=[rule_entry],
    )

    json_str = matrix.model_dump_json()
    reloaded = AuditMatrixDTO.model_validate_json(json_str)
    assert reloaded.target_file == "backend_v2/services/execution.py"
    assert reloaded.rules[0].rule_id == "the_duct_tape_ban"
    assert reloaded.rules[0].status == AuditRuleStatus.PASS


def test_check_anti_laziness_placeholders_and_bounds() -> None:
    """Test anti-rubber-stamping heuristic rejects placeholders and short texts."""
    for placeholder in ["n/a", "NA", "ok", "verified", "passed", "none", "test", "done", "pass", "fail", ""]:
        err = check_anti_laziness(placeholder)
        assert err is not None, f"Expected placeholder '{placeholder}' to be rejected"
        assert "rejected under anti-rubber-stamping heuristic" in err

    # Too short
    short_err = check_anti_laziness("Too short text.")
    assert short_err is not None
    assert "Justification too short" in short_err

    # Few words
    few_words_err = check_anti_laziness("ThisIsAVeryLongSingleWordWithoutAnySpacesAtAll.")
    assert few_words_err is not None
    assert "Justification lacks detail" in few_words_err

    # Valid substantive text
    valid_err = check_anti_laziness("This is a sufficiently long, substantive, and detailed code audit justification.")
    assert valid_err is None


def test_check_conflicting_file_references() -> None:
    """Test conflicting file reference detection in justifications."""
    # Allowed system references
    assert (
        check_conflicting_file_references(
            "Adheres strictly to settings.py and enums.py constraints.",
            "backend_v2/services/execution.py",
        )
        is None
    )

    # Own target file stem
    assert (
        check_conflicting_file_references(
            "Defined in execution.py line 88 with full type safety.",
            "backend_v2/services/execution.py",
        )
        is None
    )

    # Conflicting target file
    conflict_err = check_conflicting_file_references(
        "Implemented inside auth_service.py at line 120.",
        "backend_v2/services/execution.py",
    )
    assert conflict_err is not None
    assert "Conflicting file reference 'auth_service.py' detected" in conflict_err


def test_extract_rule_blocks(tmp_path: Path) -> None:
    """Test extracting rule blocks dynamically from markdown."""
    rules_md = tmp_path / "rules.md"
    rules_md.write_text(
        '<rule_block id="test_rule_1">\n'
        "  <banned_pattern>banned pattern 1</banned_pattern>\n"
        "  <mandatory_pattern>mandatory pattern 1</mandatory_pattern>\n"
        "</rule_block>\n"
        '<rule_block id="test_rule_2">\n'
        "  <banned_pattern>banned pattern 2</banned_pattern>\n"
        "  <mandatory_pattern>mandatory pattern 2</mandatory_pattern>\n"
        "</rule_block>\n",
        encoding="utf-8",
    )

    rules = extract_rule_blocks(rules_md)
    assert len(rules) == 2
    assert rules[0]["rule_id"] == "test_rule_1"
    assert rules[0]["banned_pattern"] == "banned pattern 1"
    assert rules[1]["rule_id"] == "test_rule_2"


def test_extract_rule_blocks_missing_file(tmp_path: Path) -> None:
    """Test extract_rule_blocks exits with code 1 when file does not exist."""
    with pytest.raises(SystemExit) as exc_info:
        extract_rule_blocks(tmp_path / "nonexistent.md")
    assert exc_info.value.code == 1


def test_cmd_generate_backend_and_frontend(tmp_path: Path) -> None:
    """Test generating audit matrices for backend and frontend targets."""
    out_backend = tmp_path / "matrix_backend.json"
    args_backend = argparse.Namespace(
        type="backend",
        target="backend_v2/services/execution.py",
        ast_scan=False,
        output=str(out_backend),
    )
    matrix_dto_backend = cmd_generate(args_backend, exit_on_completion=False)
    assert matrix_dto_backend.target_file == "backend_v2/services/execution.py"
    assert len(matrix_dto_backend.rules) > 10
    assert out_backend.exists()

    out_frontend = tmp_path / "matrix_frontend.json"
    args_frontend = argparse.Namespace(
        type="frontend",
        target="client_app_v2/lib/core/models/enums.dart",
        ast_scan=False,
        output=str(out_frontend),
    )
    matrix_dto_frontend = cmd_generate(args_frontend, exit_on_completion=False)
    assert matrix_dto_frontend.target_file == "client_app_v2/lib/core/models/enums.dart"
    assert len(matrix_dto_frontend.rules) > 5


def test_cmd_generate_with_ast_scan(tmp_path: Path) -> None:
    """Test generating matrix with automated AST scan evidence binding."""
    target_py = tmp_path / "target_sample.py"
    target_py.write_text("x = getattr(obj, 'field')\n", encoding="utf-8")

    out_json = tmp_path / "ast_matrix.json"
    args = argparse.Namespace(
        type="backend",
        target=str(target_py),
        ast_scan=True,
        output=str(out_json),
    )
    matrix_dto = cmd_generate(args, exit_on_completion=False)

    zero_comp_rule = next(r for r in matrix_dto.rules if r.rule_id == "the_zero_compromise_pledge")
    assert zero_comp_rule.evidence_type == EvidenceType.STATIC_AST
    assert len(zero_comp_rule.ast_violations) >= 1
    assert zero_comp_rule.ast_violations[0].rule_code == "QGR001"


def test_cmd_generate_invalid_type_or_empty_target() -> None:
    """Test error handling in cmd_generate for invalid type or empty target."""
    args_invalid_type = argparse.Namespace(type="invalid", target="backend_v2/settings.py")
    with pytest.raises(SystemExit) as exc_info1:
        cmd_generate(args_invalid_type, exit_on_completion=True)
    assert exc_info1.value.code == 1

    args_empty_target = argparse.Namespace(type="backend", target="")
    with pytest.raises(SystemExit) as exc_info2:
        cmd_generate(args_empty_target, exit_on_completion=True)
    assert exc_info2.value.code == 1


def test_cmd_verify_valid_matrix(tmp_path: Path) -> None:
    """Test verifying a valid, strictly compliant audit matrix passes with code 0."""
    matrix_file = tmp_path / "valid_matrix.json"
    matrix_dto = AuditMatrixDTO(
        target_file="backend_v2/services/execution.py",
        generated_at=datetime.now(UTC).isoformat(),
        rules=[
            AuditRuleEntryDTO(
                rule_id="the_duct_tape_ban",
                banned_pattern="except Exception: pass",
                mandatory_pattern="AppException",
                status=AuditRuleStatus.PASS,
                evidence_type=EvidenceType.MANUAL_AUDIT,
                ast_violations=[],
                justification="All exceptions are caught and explicitly re-raised via AppException on line 55.",
            ),
            AuditRuleEntryDTO(
                rule_id="the_zero_compromise_pledge",
                banned_pattern="hasattr/getattr",
                mandatory_pattern="Strict types",
                status=AuditRuleStatus.NA,
                evidence_type=EvidenceType.MANUAL_AUDIT,
                ast_violations=[],
                justification="Target file does not deal with reflection or dynamic attributes.",
            ),
        ],
    )
    matrix_file.write_text(matrix_dto.model_dump_json(indent=2), encoding="utf-8")

    args = argparse.Namespace(file=str(matrix_file), target="backend_v2/services/execution.py")
    errors = cmd_verify(args, exit_on_completion=False)
    assert errors == []


def test_cmd_verify_pending_status_rejected(tmp_path: Path) -> None:
    """Test that any PENDING rule status causes verification failure."""
    matrix_file = tmp_path / "pending_matrix.json"
    matrix_dto = AuditMatrixDTO(
        target_file="backend_v2/services/execution.py",
        generated_at=datetime.now(UTC).isoformat(),
        rules=[
            AuditRuleEntryDTO(
                rule_id="the_duct_tape_ban",
                banned_pattern="except Exception: pass",
                mandatory_pattern="AppException",
                status=AuditRuleStatus.PENDING,
                evidence_type=EvidenceType.MANUAL_AUDIT,
                ast_violations=[],
                justification="",
            )
        ],
    )
    matrix_file.write_text(matrix_dto.model_dump_json(indent=2), encoding="utf-8")

    args = argparse.Namespace(file=str(matrix_file), target="backend_v2/services/execution.py")
    errors = cmd_verify(args, exit_on_completion=False)
    assert len(errors) >= 1
    assert any("Status is still PENDING" in e for e in errors)


def test_cmd_verify_unsuppressed_ast_violations_fail(tmp_path: Path) -> None:
    """Test that a rule marked PASS with unsuppressed AST violations fails verification."""
    matrix_file = tmp_path / "ast_violation_matrix.json"
    violation = GuardrailViolation(
        filepath="backend_v2/services/execution.py",
        lineno=42,
        col_offset=4,
        rule_code="QGR001",
        message="Reflection call getattr",
        remediation="Use match/case",
        severity=GuardrailSeverity.WARNING,
        is_suppressed=False,
    )
    matrix_dto = AuditMatrixDTO(
        target_file="backend_v2/services/execution.py",
        generated_at=datetime.now(UTC).isoformat(),
        rules=[
            AuditRuleEntryDTO(
                rule_id="the_zero_compromise_pledge",
                banned_pattern="hasattr/getattr",
                mandatory_pattern="Strict types",
                status=AuditRuleStatus.PASS,
                evidence_type=EvidenceType.STATIC_AST,
                ast_violations=[violation],
                justification="Verified strictly according to architectural specifications.",
            )
        ],
    )
    matrix_file.write_text(matrix_dto.model_dump_json(indent=2), encoding="utf-8")

    args = argparse.Namespace(file=str(matrix_file), target="backend_v2/services/execution.py")
    errors = cmd_verify(args, exit_on_completion=False)
    assert len(errors) >= 1
    assert any("Marked as PASS but contains 1 un-suppressed AST violations" in e for e in errors)


def test_cmd_verify_duplicate_pass_justifications(tmp_path: Path) -> None:
    """Test that duplicate PASS justifications trigger verification error."""
    matrix_file = tmp_path / "dup_matrix.json"
    matrix_dto = AuditMatrixDTO(
        target_file="backend_v2/services/execution.py",
        generated_at=datetime.now(UTC).isoformat(),
        rules=[
            AuditRuleEntryDTO(
                rule_id="rule_1",
                banned_pattern="banned",
                mandatory_pattern="mandatory",
                status=AuditRuleStatus.PASS,
                evidence_type=EvidenceType.MANUAL_AUDIT,
                ast_violations=[],
                justification="Identical copied and pasted justification text.",
            ),
            AuditRuleEntryDTO(
                rule_id="rule_2",
                banned_pattern="banned",
                mandatory_pattern="mandatory",
                status=AuditRuleStatus.PASS,
                evidence_type=EvidenceType.MANUAL_AUDIT,
                ast_violations=[],
                justification="Identical copied and pasted justification text.",
            ),
        ],
    )
    matrix_file.write_text(matrix_dto.model_dump_json(indent=2), encoding="utf-8")

    args = argparse.Namespace(file=str(matrix_file), target="backend_v2/services/execution.py")
    errors = cmd_verify(args, exit_on_completion=False)
    assert len(errors) >= 1
    assert any("Duplicate PASS justification detected" in e for e in errors)


def test_cmd_verify_target_mismatch_and_missing_file(tmp_path: Path) -> None:
    """Test target mismatch and missing file error handling."""
    # Missing file
    args_missing = argparse.Namespace(file=str(tmp_path / "nonexistent.json"), target="some_target.py")
    errors_missing = cmd_verify(args_missing, exit_on_completion=False)
    assert len(errors_missing) == 1
    assert "not found" in errors_missing[0]

    # Target mismatch
    matrix_file = tmp_path / "mismatch.json"
    matrix_dto = AuditMatrixDTO(
        target_file="backend_v2/services/execution.py",
        generated_at=datetime.now(UTC).isoformat(),
        rules=[],
    )
    matrix_file.write_text(matrix_dto.model_dump_json(indent=2), encoding="utf-8")
    args_mismatch = argparse.Namespace(file=str(matrix_file), target="backend_v2/other.py")
    errors_mismatch = cmd_verify(args_mismatch, exit_on_completion=False)
    assert any("Target mismatch" in e for e in errors_mismatch)


def test_cmd_verify_malformed_json(tmp_path: Path) -> None:
    """Test that malformed JSON or invalid schema triggers verification error."""
    bad_json_file = tmp_path / "bad.json"
    bad_json_file.write_text("{ unclosed: json", encoding="utf-8")
    args = argparse.Namespace(file=str(bad_json_file), target="backend_v2/services/execution.py")
    errors = cmd_verify(args, exit_on_completion=False)
    assert any("Error parsing or validating JSON" in e for e in errors)


def test_main_cli_generate_and_verify(tmp_path: Path) -> None:
    """Test main() CLI generate and verify commands end-to-end."""
    matrix_path = tmp_path / "cli_matrix.json"

    # 1. Generate CLI command (exits with 0 on success)
    with pytest.raises(SystemExit) as exc_gen:
        main(
            [
                "generate",
                "--type",
                "backend",
                "--target",
                "backend_v2/services/execution.py",
                "--output",
                str(matrix_path),
            ]
        )
    assert exc_gen.value.code == 0
    assert matrix_path.exists()

    # Fill matrix with valid pass justifications
    matrix_dto = AuditMatrixDTO.model_validate_json(matrix_path.read_text(encoding="utf-8"))
    filled_rules = [
        r.model_copy(
            update={
                "status": AuditRuleStatus.PASS,
                "justification": f"Substantive unique evidence for rule {r.rule_id} on lines 10-20.",
            }
        )
        for r in matrix_dto.rules
    ]
    filled_matrix = matrix_dto.model_copy(update={"rules": filled_rules})
    matrix_path.write_text(filled_matrix.model_dump_json(indent=2), encoding="utf-8")

    # 2. Verify CLI command (exits with 0 on success)
    with pytest.raises(SystemExit) as exc_ver:
        main(
            [
                "verify",
                "--file",
                str(matrix_path),
                "--target",
                "backend_v2/services/execution.py",
            ]
        )
    assert exc_ver.value.code == 0


def test_audit_matrix_manager_zero_reflection_compliance() -> None:
    """Verify scripts/audit_matrix_manager.py contains zero getattr/hasattr calls."""
    script_path = Path("scripts/audit_matrix_manager.py").resolve()
    tree = ast.parse(script_path.read_text(encoding="utf-8"), filename=script_path.as_posix())

    reflection_calls: list[int] = []
    for node in ast.walk(tree):
        match node:
            case ast.Call(func=ast.Name(id="getattr" | "hasattr")):
                reflection_calls.append(node.lineno)
            case _:
                pass

    assert reflection_calls == [], f"Found banned reflection calls at lines: {reflection_calls}"
