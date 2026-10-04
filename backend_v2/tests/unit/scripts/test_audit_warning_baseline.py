"""Unit tests for Warning Baseline Ledger (scripts/audit_warning_baseline.py)."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from scripts._ast_guardrails import GuardrailSeverity, GuardrailViolation
from scripts.audit_warning_baseline import (
    BaselineLedgerReportDTO,
    RuleWarningStatDTO,
    format_report_table,
    generate_baseline_report,
    main,
)


def test_baseline_ledger_report_dto_validation() -> None:
    """Positive: verifies DTO fields and validation constraints."""
    stat = RuleWarningStatDTO(rule_code="QGR001", count=0)
    assert stat.rule_code == "QGR001"
    assert stat.count == 0

    report = BaselineLedgerReportDTO(
        target_directory="backend_v2",
        fatal_count=0,
        warning_count=0,
        warning_ceiling=0,
        rule_breakdown=[stat],
        is_clean_of_fatals=True,
        is_under_ceiling=True,
    )
    assert report.is_clean_of_fatals is True
    assert report.is_under_ceiling is True
    assert len(report.rule_breakdown) == 1


def test_warning_baseline_ledger_asserts_zero_ceiling() -> None:
    """Contract: verifies that default generation asserts zero ceiling and clean backend."""
    fake_violations: list[GuardrailViolation] = []
    with patch("scripts.audit_warning_baseline.scan_files_for_guardrails", return_value=(fake_violations, True)):
        report = generate_baseline_report("backend_v2", verify_zero=True)
        assert report.fatal_count == 0
        assert report.warning_count == 0
        assert report.warning_ceiling == 0
        assert report.is_clean_of_fatals is True
        assert report.is_under_ceiling is True


def test_warning_baseline_ledger_rejects_any_nonzero_warning_violation() -> None:
    """Contract: verifies that nonzero warning count with verify_zero triggers failure."""
    fake_violations = [
        GuardrailViolation(
            filepath="backend_v2/test.py",
            lineno=10,
            col_offset=0,
            rule_code="QGR001",
            message="Reflection",
            remediation="Fix it",
            severity=GuardrailSeverity.WARNING,
            is_suppressed=False,
        ),
    ]
    with patch("scripts.audit_warning_baseline.scan_files_for_guardrails", return_value=(fake_violations, True)):
        report = generate_baseline_report("backend_v2", verify_zero=True)
        assert report.fatal_count == 0
        assert report.warning_count == 1
        assert report.warning_ceiling == 0
        assert report.is_under_ceiling is False


def test_generate_baseline_report_compiles_correctly() -> None:
    """Positive: verifies that generate_baseline_report correctly tallies violations."""
    fake_violations = [
        GuardrailViolation(
            filepath="backend_v2/test1.py",
            lineno=10,
            col_offset=0,
            rule_code="QGR001",
            message="Reflection",
            remediation="Fix it",
            severity=GuardrailSeverity.WARNING,
            is_suppressed=False,
        ),
        GuardrailViolation(
            filepath="backend_v2/test2.py",
            lineno=20,
            col_offset=0,
            rule_code="QGR001",
            message="Reflection",
            remediation="Fix it",
            severity=GuardrailSeverity.WARNING,
            is_suppressed=False,
        ),
        GuardrailViolation(
            filepath="backend_v2/test3.py",
            lineno=30,
            col_offset=0,
            rule_code="QGR002",
            message="Naked dict",
            remediation="Fix it",
            severity=GuardrailSeverity.WARNING,
            is_suppressed=False,
        ),
    ]

    with patch("scripts.audit_warning_baseline.scan_files_for_guardrails", return_value=(fake_violations, True)):
        report = generate_baseline_report("backend_v2", ceiling=10)
        assert report.fatal_count == 0
        assert report.warning_count == 3
        assert report.is_clean_of_fatals is True
        assert report.is_under_ceiling is True
        breakdown_dict = {s.rule_code: s.count for s in report.rule_breakdown}
        assert breakdown_dict == {"QGR001": 2, "QGR002": 1}


def test_generate_baseline_report_fails_on_fatals() -> None:
    """Error path: verifies that report flags fatal violations."""
    fake_violations = [
        GuardrailViolation(
            filepath="backend_v2/bad.py",
            lineno=10,
            col_offset=0,
            rule_code="QGR000",
            message="Syntax error",
            remediation="Fix syntax",
            severity=GuardrailSeverity.FATAL,
            is_suppressed=False,
        ),
    ]

    with patch("scripts.audit_warning_baseline.scan_files_for_guardrails", return_value=(fake_violations, False)):
        report = generate_baseline_report("backend_v2", ceiling=10)
        assert report.fatal_count == 1
        assert report.is_clean_of_fatals is False


def test_generate_baseline_report_verify_zero() -> None:
    """Boundary: verifies verify_zero requires 0 warnings."""
    fake_violations = [
        GuardrailViolation(
            filepath="backend_v2/test.py",
            lineno=10,
            col_offset=0,
            rule_code="QGR001",
            message="Reflection",
            remediation="Fix it",
            severity=GuardrailSeverity.WARNING,
            is_suppressed=False,
        ),
    ]

    with patch("scripts.audit_warning_baseline.scan_files_for_guardrails", return_value=(fake_violations, True)):
        report = generate_baseline_report("backend_v2", ceiling=10, verify_zero=True)
        assert report.warning_ceiling == 0
        assert report.is_under_ceiling is False


def test_format_report_table() -> None:
    """Positive: verifies table formatting output strings."""
    report = BaselineLedgerReportDTO(
        target_directory="backend_v2",
        fatal_count=0,
        warning_count=5,
        warning_ceiling=10,
        rule_breakdown=[RuleWarningStatDTO(rule_code="QGR001", count=5)],
        is_clean_of_fatals=True,
        is_under_ceiling=True,
    )
    table_str = format_report_table(report)
    assert "AST ADVISORY WARNING BASELINE LEDGER" in table_str
    assert "QGR001" in table_str
    assert "PASSED" in table_str


def test_format_report_table_failure_fatals() -> None:
    """Negative: verifies table formatting reports failure when fatal violations exist."""
    report = BaselineLedgerReportDTO(
        target_directory="backend_v2",
        fatal_count=2,
        warning_count=0,
        warning_ceiling=10,
        rule_breakdown=[],
        is_clean_of_fatals=False,
        is_under_ceiling=True,
    )
    table_str = format_report_table(report)
    assert "FAILED: Detected 2 fatal violations" in table_str


def test_format_report_table_failure_ceiling() -> None:
    """Negative: verifies table formatting reports failure when warning count exceeds ceiling."""
    report = BaselineLedgerReportDTO(
        target_directory="backend_v2",
        fatal_count=0,
        warning_count=12,
        warning_ceiling=10,
        rule_breakdown=[RuleWarningStatDTO(rule_code="QGR001", count=12)],
        is_clean_of_fatals=True,
        is_under_ceiling=False,
    )
    table_str = format_report_table(report)
    assert "FAILED: Warning count (12) exceeds ceiling (10)" in table_str


def test_main_cli_execution_plain_table(capsys: pytest.CaptureFixture[str]) -> None:
    """Positive: verifies CLI execution with plain table output and success exit code 0."""
    fake_violations: list[GuardrailViolation] = []
    with patch("scripts.audit_warning_baseline.scan_files_for_guardrails", return_value=(fake_violations, True)):
        with pytest.raises(SystemExit) as exc_info:
            main(["--target", "backend_v2"])
        assert exc_info.value.code == 0
        out, _ = capsys.readouterr()
        assert "AST ADVISORY WARNING BASELINE LEDGER" in out
        assert "PASSED" in out



def test_main_cli_execution(capsys: pytest.CaptureFixture[str]) -> None:
    """Positive: verifies CLI execution with --json and success exit code 0."""
    fake_violations: list[GuardrailViolation] = []
    with patch("scripts.audit_warning_baseline.scan_files_for_guardrails", return_value=(fake_violations, True)):
        with pytest.raises(SystemExit) as exc_info:
            main(["--target", "backend_v2", "--json"])
        assert exc_info.value.code == 0
        out, _ = capsys.readouterr()
        data = json.loads(out)
        assert data["fatal_count"] == 0
        assert data["is_clean_of_fatals"] is True


def test_main_cli_failure_on_exceeding_ceiling() -> None:
    """Negative: verifies CLI exits with code 1 when warning count exceeds ceiling."""
    fake_violations = [
        GuardrailViolation(
            filepath="backend_v2/test.py",
            lineno=10,
            col_offset=0,
            rule_code="QGR001",
            message="Reflection",
            remediation="Fix it",
            severity=GuardrailSeverity.WARNING,
            is_suppressed=False,
        ),
    ]
    with patch("scripts.audit_warning_baseline.scan_files_for_guardrails", return_value=(fake_violations, True)):
        with pytest.raises(SystemExit) as exc_info:
            main(["--target", "backend_v2", "--ceiling", "0"])
        assert exc_info.value.code == 1
