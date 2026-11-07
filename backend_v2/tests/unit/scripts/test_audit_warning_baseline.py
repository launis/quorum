"""Unit tests for Warning Baseline Ledger (scripts/audit_warning_baseline.py)."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts._ast_guardrails import GuardrailSeverity, GuardrailViolation
from scripts.audit_warning_baseline import (
    CURRENT_RESIDUAL_CEILINGS,
    BaselineLedgerReportDTO,
    ResidualDebtCeilingsDTO,
    RuleWarningStatDTO,
    compute_census_counts,
    format_report_table,
    generate_baseline_report,
    main,
    verify_residual_debt_ceilings,
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
        ),
        GuardrailViolation(
            filepath="backend_v2/test2.py",
            lineno=20,
            col_offset=0,
            rule_code="QGR001",
            message="Reflection",
            remediation="Fix it",
            severity=GuardrailSeverity.WARNING,
        ),
        GuardrailViolation(
            filepath="backend_v2/test3.py",
            lineno=30,
            col_offset=0,
            rule_code="QGR002",
            message="Naked dict",
            remediation="Fix it",
            severity=GuardrailSeverity.WARNING,
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
        ),
    ]
    with patch("scripts.audit_warning_baseline.scan_files_for_guardrails", return_value=(fake_violations, True)):
        with pytest.raises(SystemExit) as exc_info:
            main(["--target", "backend_v2", "--ceiling", "0"])
        assert exc_info.value.code == 1


# ==============================================================================
# Residual Debt Ceilings (EPIC 157)
# ==============================================================================


def test_residual_debt_ceilings_dto_asserts_exact_equality() -> None:
    """Contract: test_residual_debt_ceilings_dto_asserts_exact_equality.

    Positive: ResidualDebtCeilingsDTO validates successfully with extra='forbid' and frozen=True.
    """
    from pydantic import ValidationError

    dto = ResidualDebtCeilingsDTO(
        d=821,
        f=51,
        k=25,
        x=806,
        n=78,
        t=411,
        p=407,
        m=10,
        r=191,
        s=11,
    )
    assert dto.d == 821
    assert dto.f == 51
    assert dto.k == 25
    assert dto.x == 806
    assert dto.n == 78
    assert dto.t == 411
    assert dto.p == 407
    assert dto.m == 10
    assert dto.r == 191
    assert dto.s == 11

    # Verify frozen
    with pytest.raises(ValidationError):
        dto.__setattr__("d", 999)

    # Verify extra='forbid'
    with pytest.raises(ValidationError):
        ResidualDebtCeilingsDTO.model_validate(
            {
                "d": 821,
                "f": 51,
                "k": 25,
                "x": 806,
                "n": 78,
                "t": 411,
                "p": 407,
                "m": 10,
                "r": 191,
                "s": 11,
                "unknown_category": 99,
            }
        )


def test_verify_residual_debt_ceilings_exact_match() -> None:
    """Positive: verify_residual_debt_ceilings succeeds when live matches ceiling."""
    dto = ResidualDebtCeilingsDTO(
        d=821,
        f=51,
        k=25,
        x=806,
        n=78,
        t=411,
        p=407,
        m=10,
        r=191,
        s=11,
    )
    is_valid, msgs = verify_residual_debt_ceilings(dto, dto)
    assert is_valid is True
    assert any("PASSED" in m for m in msgs)


def test_verify_residual_debt_ceilings_detects_exceeded() -> None:
    """Negative: verify_residual_debt_ceilings flags error when live count exceeds ceiling."""
    ceil = ResidualDebtCeilingsDTO(
        d=10,
        f=10,
        k=10,
        x=10,
        n=10,
        t=10,
        p=10,
        m=10,
        r=10,
        s=10,
    )
    live = ResidualDebtCeilingsDTO(
        d=11,  # Exceeded
        f=10,
        k=10,
        x=10,
        n=10,
        t=10,
        p=10,
        m=10,
        r=10,
        s=10,
    )
    is_valid, msgs = verify_residual_debt_ceilings(live, ceil)
    assert is_valid is False
    assert any("EXCEEDED" in m for m in msgs)


def test_verify_residual_debt_ceilings_detects_lowered() -> None:
    """Boundary: verify_residual_debt_ceilings flags ratchet needed when live count is below ceiling."""
    ceil = ResidualDebtCeilingsDTO(
        d=10,
        f=10,
        k=10,
        x=10,
        n=10,
        t=10,
        p=10,
        m=10,
        r=10,
        s=10,
    )
    live = ResidualDebtCeilingsDTO(
        d=9,  # Lowered - requires ratcheting down
        f=10,
        k=10,
        x=10,
        n=10,
        t=10,
        p=10,
        m=10,
        r=10,
        s=10,
    )
    is_valid, msgs = verify_residual_debt_ceilings(live, ceil)
    assert is_valid is False
    assert any("RATCHET NEEDED" in m for m in msgs)


def test_compute_census_counts_multiline_and_categories(tmp_path: Path) -> None:
    """Verify compute_census_counts across synthetic repo_root including multi-line Dart fromJson."""
    tests_unit = tmp_path / "backend_v2" / "tests" / "unit" / "services"
    tests_unit.mkdir(parents=True)
    fakes_dir = tmp_path / "backend_v2" / "tests" / "fakes"
    fakes_dir.mkdir(parents=True)
    scripts_tests_dir = tmp_path / "backend_v2" / "tests" / "unit" / "scripts"
    scripts_tests_dir.mkdir(parents=True)

    # Concatenate tokens so real repo census scans do not match literals in this test file
    skip_marker = "@pytest.mark." + "skip"
    repo_cls = "class " + "CustomRepo:"
    dict_ann = "dict" + "[str, Any]"
    mapping_ann = "Mapping" + "[str, Any]"
    type_ign = "# " + "type: ignore"
    noqa_tok = "# " + "noqa: F401"

    (fakes_dir / "fake_repo.py").write_text(f"{repo_cls}\n    pass\n", encoding="utf-8")
    (scripts_tests_dir / "ignored_script_test.py").write_text(
        'patch("pkg.UserRepository")\nService(user_repo=AsyncMock())\ncast(Any, x)\n',
        encoding="utf-8",
    )
    (tests_unit / "sample_test.py").write_text(
        f"{skip_marker}\n"
        f"{repo_cls}\n    pass\n"
        'patch("backend_v2.services.UserRepository")\n'
        "Service(user_repo=AsyncMock())\n"
        f"x: {dict_ann} = {{}}  {type_ign}\n",
        encoding="utf-8",
    )

    prod_dir = tmp_path / "backend_v2" / "services"
    prod_dir.mkdir(parents=True)
    (prod_dir / "svc.py").write_text(
        f"def f(a: {mapping_ann}) -> None:\n    cast(Any, a)  {noqa_tok}\n",
        encoding="utf-8",
    )

    core_dir = tmp_path / "backend_v2" / "core"
    core_dir.mkdir(parents=True)
    (core_dir / "test_settings.py").write_text(f"s: {dict_ann} = {{}}\n", encoding="utf-8")

    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir(parents=True)
    (scripts_dir / "tool.py").write_text(f"y: {dict_ann} = {{}}\n", encoding="utf-8")

    dart_dir = tmp_path / "client_app_v2" / "lib" / "models"
    dart_dir.mkdir(parents=True)
    (dart_dir / "model.g.dart").write_text("Map<String, dynamic> ignored = {};\n", encoding="utf-8")
    (dart_dir / "model.dart").write_text(
        "class Model {\n"
        "  factory Model.fromJson(\n"
        "    Map<String, dynamic> json,\n"
        "  ) => Model();\n"
        "  Map<String, dynamic> toJson() => {};\n"
        "  final Map<String, dynamic> nonCodec = {};\n"
        "}\n",
        encoding="utf-8",
    )

    counts = compute_census_counts(repo_root=tmp_path)
    assert counts.s == 1
    assert counts.k == 1
    assert counts.f == 1
    assert counts.d == 1
    assert counts.x == 1
    assert counts.t == 1
    assert counts.p == 2
    assert counts.m == 2
    assert counts.n == 1
    assert counts.r == 1


def test_main_cli_with_check_residual(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify CLI execution with --check-residual prints residual table and exits 0 when matching."""
    fake_violations: list[GuardrailViolation] = []
    with (
        patch("scripts.audit_warning_baseline.scan_files_for_guardrails", return_value=(fake_violations, True)),
        patch("scripts.audit_warning_baseline.compute_census_counts", return_value=CURRENT_RESIDUAL_CEILINGS),
    ):
        with pytest.raises(SystemExit) as exc_info:
            main(["--target", "backend_v2", "--check-residual"])
        assert exc_info.value.code == 0
        out, _ = capsys.readouterr()
        assert "RESIDUAL DEBT CEILINGS" in out


def test_audit_warning_baseline_verify_ceilings_all_zero(capsys: pytest.CaptureFixture[str]) -> None:
    """Phase 6, Step 6.2: Verify all 10 residual categories equal 0 and --verify-ceilings exits 0."""
    assert CURRENT_RESIDUAL_CEILINGS == ResidualDebtCeilingsDTO(
        d=0,
        f=0,
        k=0,
        x=0,
        n=0,
        t=0,
        p=0,
        m=0,
        r=0,
        s=0,
    )
    live_counts = compute_census_counts()
    assert live_counts == CURRENT_RESIDUAL_CEILINGS

    fake_violations: list[GuardrailViolation] = []
    with patch("scripts.audit_warning_baseline.scan_files_for_guardrails", return_value=(fake_violations, True)):
        with pytest.raises(SystemExit) as exc_info:
            main(["--target", "backend_v2", "--verify-ceilings"])
        assert exc_info.value.code == 0
        out, _ = capsys.readouterr()
        assert "PASSED: All residual debt categories strictly conform to ratchet ceilings." in out
