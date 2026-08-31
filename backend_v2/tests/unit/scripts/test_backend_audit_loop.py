"""Hermetically Isolated ISTQB Unit Tests for backend_audit_loop.py.

Verifies CLI argument parsing, multi-stage pipeline gates, AST gate strict/advisory behavior,
Jinja template enforcement, subprocess failure handling, and coverage runner mechanics.
Enforces 100% hermetic isolation via @patch('subprocess.run') and @patch('sys.exit').
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from scripts._ast_guardrails import GuardrailSeverity, GuardrailViolation
from scripts.backend_audit_loop import main, run_tests_with_strict_coverage


def _mock_completed_process(
    returncode: int = 0, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    """Helper creating a hermetic subprocess.CompletedProcess mock."""
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


# ==============================================================================
# Partition 1-2: CLI Parsing & Working Directory Validation
# ==============================================================================


@patch("sys.exit")
def test_cli_no_args_triggers_exit(mock_exit: MagicMock) -> None:
    mock_exit.side_effect = SystemExit(1)
    with patch.object(sys, "argv", ["backend_audit_loop.py"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1


@patch("scripts.backend_audit_loop.scan_files_for_guardrails", return_value=([], True))
@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_cli_parsing_with_targets_and_flags(mock_sub: MagicMock, mock_scan: MagicMock) -> None:
    with patch.object(
        sys,
        "argv",
        ["backend_audit_loop.py", "backend_v2/services/execution.py", "--ast-strict", "--openapi", "--test"],
    ):
        with patch("scripts.backend_audit_loop.run_tests_with_strict_coverage") as mock_cov_run:
            main()
            assert mock_scan.called
            assert mock_scan.call_args[1]["strict"] is True
            assert mock_cov_run.called


@patch("scripts.backend_audit_loop.scan_files_for_guardrails", return_value=([], True))
@patch("subprocess.run", return_value=_mock_completed_process(0))
@patch("os.chdir")
def test_cli_scripts_dir_cd_handling(mock_chdir: MagicMock, mock_sub: MagicMock, mock_scan: MagicMock) -> None:
    mock_path = MagicMock()
    mock_path.name = "scripts"
    with patch("scripts.backend_audit_loop.Path", return_value=mock_path):
        with patch.object(sys, "argv", ["backend_audit_loop.py", "scripts/"]):
            main()
            mock_chdir.assert_called_once_with("..")


@patch("sys.exit")
def test_cli_invalid_root_directory_exit(mock_exit: MagicMock) -> None:
    mock_exit.side_effect = SystemExit(1)
    mock_path = MagicMock()
    mock_path.name = "other_folder"
    mock_path.__truediv__.return_value.exists.return_value = False

    with patch("scripts.backend_audit_loop.Path", return_value=mock_path):
        with patch.object(sys, "argv", ["backend_audit_loop.py", "target.py"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


# ==============================================================================
# Partition 3-4: Jinja Template Validation (Dumb Painter Enforcement)
# ==============================================================================


@patch("scripts.backend_audit_loop.scan_files_for_guardrails", return_value=([], True))
@patch("subprocess.run", return_value=_mock_completed_process(0))
@patch("sys.exit")
def test_jinja_validation_fails_on_forbidden_expression(
    mock_exit: MagicMock, mock_sub: MagicMock, mock_scan: MagicMock, tmp_path: Path
) -> None:
    mock_exit.side_effect = SystemExit(1)
    fake_jinja = tmp_path / "bad.jinja2"
    fake_jinja.write_text("Hello {{ user.get('name') }}", encoding="utf-8")

    with patch("scripts.backend_audit_loop.Path") as mock_path_cls:
        real_path = Path
        mock_templates = MagicMock()
        mock_templates.exists.return_value = True
        mock_templates.rglob.return_value = [fake_jinja]

        def path_side_effect(arg: str) -> Any:
            if arg == "backend_v2/templates":
                return mock_templates
            return real_path(arg)

        mock_path_cls.side_effect = path_side_effect

        with patch.object(sys, "argv", ["backend_audit_loop.py", "backend_v2/"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("scripts.backend_audit_loop.scan_files_for_guardrails", return_value=([], True))
@patch("subprocess.run", return_value=_mock_completed_process(0))
@patch("sys.exit")
def test_jinja_validation_fails_fast_on_read_error(
    mock_exit: MagicMock, mock_sub: MagicMock, mock_scan: MagicMock
) -> None:
    mock_exit.side_effect = SystemExit(1)
    fake_jinja = MagicMock()
    fake_jinja.name = "corrupted.jinja2"
    fake_jinja.read_text.side_effect = OSError("Permission denied")

    with patch("scripts.backend_audit_loop.Path") as mock_path_cls:
        real_path = Path
        mock_templates = MagicMock()
        mock_templates.exists.return_value = True
        mock_templates.rglob.return_value = [fake_jinja]

        def path_side_effect(arg: str) -> Any:
            if arg == "backend_v2/templates":
                return mock_templates
            return real_path(arg)

        mock_path_cls.side_effect = path_side_effect

        with patch.object(sys, "argv", ["backend_audit_loop.py", "backend_v2/"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


# ==============================================================================
# Partition 5-7: AST Guardrail Stage Gating (Strict vs Advisory Modes)
# ==============================================================================


@patch("subprocess.run", return_value=_mock_completed_process(0))
@patch("sys.exit")
def test_ast_gate_strict_mode_fails_on_warning_violation(mock_exit: MagicMock, mock_sub: MagicMock) -> None:
    mock_exit.side_effect = SystemExit(1)
    warning_violation = GuardrailViolation(
        filepath="backend_v2/test.py",
        lineno=5,
        col_offset=2,
        rule_code="QGR001",
        message="getattr reflection",
        remediation="Use match/case",
        severity=GuardrailSeverity.WARNING,
        is_suppressed=False,
    )

    with patch("scripts.backend_audit_loop.scan_files_for_guardrails", return_value=([warning_violation], False)):
        with patch.object(sys, "argv", ["backend_audit_loop.py", "backend_v2/test.py", "--ast-strict"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("subprocess.run", return_value=_mock_completed_process(0))
@patch("sys.exit")
def test_ast_gate_advisory_mode_fails_on_fatal_qgr000(mock_exit: MagicMock, mock_sub: MagicMock) -> None:
    mock_exit.side_effect = SystemExit(1)
    fatal_violation = GuardrailViolation(
        filepath="backend_v2/test.py",
        lineno=1,
        col_offset=0,
        rule_code="QGR000",
        message="SyntaxError",
        remediation="Fix syntax",
        severity=GuardrailSeverity.FATAL,
        is_suppressed=False,
    )

    with patch("scripts.backend_audit_loop.scan_files_for_guardrails", return_value=([fatal_violation], False)):
        with patch.object(sys, "argv", ["backend_audit_loop.py", "backend_v2/test.py"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_ast_gate_advisory_mode_passes_on_warning_only(mock_sub: MagicMock) -> None:
    warning_violation = GuardrailViolation(
        filepath="backend_v2/test.py",
        lineno=5,
        col_offset=2,
        rule_code="QGR001",
        message="getattr reflection",
        remediation="Use match/case",
        severity=GuardrailSeverity.WARNING,
        is_suppressed=False,
    )

    with patch("scripts.backend_audit_loop.scan_files_for_guardrails", return_value=([warning_violation], True)):
        with patch.object(sys, "argv", ["backend_audit_loop.py", "backend_v2/test.py"]):
            main()


# ==============================================================================
# Partition 8-10: Subprocess Stage Failures (Ruff, MyPy, Seed, OpenAPI)
# ==============================================================================


@patch("scripts.backend_audit_loop.scan_files_for_guardrails", return_value=([], True))
@patch("sys.exit")
def test_subprocess_ruff_check_failure(mock_exit: MagicMock, mock_scan: MagicMock) -> None:
    mock_exit.side_effect = SystemExit(1)
    with patch("subprocess.run", return_value=_mock_completed_process(1)):
        with patch.object(sys, "argv", ["backend_audit_loop.py", "backend_v2/"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("scripts.backend_audit_loop.scan_files_for_guardrails", return_value=([], True))
@patch("sys.exit")
def test_subprocess_ruff_format_failure(mock_exit: MagicMock, mock_scan: MagicMock) -> None:
    mock_exit.side_effect = SystemExit(1)

    def sub_side_effect(cmd: list[str], *args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if "format" in cmd:
            return _mock_completed_process(1)
        return _mock_completed_process(0)

    with patch("subprocess.run", side_effect=sub_side_effect):
        with patch.object(sys, "argv", ["backend_audit_loop.py", "backend_v2/"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("scripts.backend_audit_loop.scan_files_for_guardrails", return_value=([], True))
@patch("sys.exit")
def test_subprocess_mypy_strict_failure(mock_exit: MagicMock, mock_scan: MagicMock) -> None:
    mock_exit.side_effect = SystemExit(1)

    def sub_side_effect(cmd: list[str], *args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if any("mypy" in str(c) for c in cmd):
            return _mock_completed_process(1)
        return _mock_completed_process(0)

    with patch("subprocess.run", side_effect=sub_side_effect):
        with patch.object(sys, "argv", ["backend_audit_loop.py", "backend_v2/"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("scripts.backend_audit_loop.scan_files_for_guardrails", return_value=([], True))
@patch("sys.exit")
def test_subprocess_seed_dry_run_failure(mock_exit: MagicMock, mock_scan: MagicMock) -> None:
    mock_exit.side_effect = SystemExit(1)

    def sub_side_effect(cmd: list[str], *args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if any("run_seed.py" in str(c) for c in cmd):
            return _mock_completed_process(1)
        return _mock_completed_process(0)

    with patch("subprocess.run", side_effect=sub_side_effect):
        with patch.object(sys, "argv", ["backend_audit_loop.py", "backend_v2/"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("scripts.backend_audit_loop.scan_files_for_guardrails", return_value=([], True))
@patch("sys.exit")
def test_subprocess_openapi_failure(mock_exit: MagicMock, mock_scan: MagicMock) -> None:
    mock_exit.side_effect = SystemExit(1)

    def sub_side_effect(cmd: list[str], *args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if any("generate_openapi.py" in str(c) for c in cmd):
            return _mock_completed_process(1)
        return _mock_completed_process(0)

    with patch("subprocess.run", side_effect=sub_side_effect):
        with patch.object(sys, "argv", ["backend_audit_loop.py", "backend_v2/", "--openapi"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


# ==============================================================================
# Partition 11: Coverage Runner & Module Path Mechanics
# ==============================================================================


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_coverage_runner_single_file_target(mock_sub: MagicMock) -> None:
    run_tests_with_strict_coverage("backend_v2/services/sample.py")
    assert mock_sub.call_count == 2
    cov_cmd = mock_sub.call_args_list[1][0][0]
    assert "--fail-under=90" in cov_cmd
    assert "--include=*sample.py" in cov_cmd


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_coverage_runner_init_file_target(mock_sub: MagicMock) -> None:
    run_tests_with_strict_coverage("backend_v2/hooks/__init__.py")
    assert mock_sub.call_count == 2


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_coverage_runner_scripts_target(mock_sub: MagicMock) -> None:
    run_tests_with_strict_coverage("scripts/_ast_guardrails.py")
    assert mock_sub.call_count == 2


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_coverage_runner_direct_test_file_target(mock_sub: MagicMock) -> None:
    run_tests_with_strict_coverage("backend_v2/tests/unit/scripts/test_ast_guardrails.py")
    assert mock_sub.call_count == 2


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_coverage_runner_directory_target(mock_sub: MagicMock) -> None:
    run_tests_with_strict_coverage("backend_v2/services/")
    assert mock_sub.call_count == 1
    pytest_cmd = mock_sub.call_args_list[0][0][0]
    assert "--cov=backend_v2.services" in pytest_cmd[4]


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_coverage_runner_root_dot_directory_target(mock_sub: MagicMock) -> None:
    run_tests_with_strict_coverage(".")
    assert mock_sub.call_count == 1


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_coverage_runner_other_directory_target(mock_sub: MagicMock) -> None:
    run_tests_with_strict_coverage("tests/e2e")
    assert mock_sub.call_count == 1


@patch("sys.exit")
def test_coverage_runner_failure_triggers_exit(mock_exit: MagicMock) -> None:
    mock_exit.side_effect = SystemExit(1)
    with patch("subprocess.run", return_value=_mock_completed_process(1)):
        with pytest.raises(SystemExit) as exc:
            run_tests_with_strict_coverage("backend_v2/services/sample.py")
        assert exc.value.code == 1


@patch("scripts.backend_audit_loop.scan_files_for_guardrails", return_value=([], True))
@patch("sys.exit")
def test_subprocess_audit_database_atoms_failure(mock_exit: MagicMock, mock_scan: MagicMock) -> None:
    mock_exit.side_effect = SystemExit(1)

    def sub_side_effect(cmd: list[str], *args: Any, **kwargs: Any) -> subprocess.CompletedProcess[str]:
        if any("audit_database_atoms.py" in str(c) for c in cmd):
            return _mock_completed_process(1)
        return _mock_completed_process(0)

    with patch("subprocess.run", side_effect=sub_side_effect):
        with patch.object(sys, "argv", ["backend_audit_loop.py", "backend_v2/"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_coverage_runner_scripts_non_prefixed_target(mock_sub: MagicMock) -> None:
    run_tests_with_strict_coverage("backend_v2/tests/unit/scripts/test_backend_audit_loop.py")
    assert mock_sub.call_count == 2


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_coverage_runner_unit_test_in_backend_v2(mock_sub: MagicMock) -> None:
    run_tests_with_strict_coverage("backend_v2/tests/unit/services/test_execution.py")
    assert mock_sub.call_count == 2


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_coverage_runner_directory_with_test_file_fallback(mock_sub: MagicMock) -> None:
    with patch("scripts.backend_audit_loop.Path.exists", side_effect=[False, True]):
        run_tests_with_strict_coverage("backend_v2/models/dtos")
        assert mock_sub.call_count == 1


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_coverage_runner_directory_no_test_dir_or_file(mock_sub: MagicMock) -> None:
    with patch("scripts.backend_audit_loop.Path.exists", return_value=False):
        run_tests_with_strict_coverage("backend_v2/unknown_dir")
        assert mock_sub.call_count == 1


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_coverage_runner_flat_unit_test_fallback(mock_sub: MagicMock) -> None:
    with patch("scripts.backend_audit_loop.Path.exists", side_effect=[False, False, False, True, True, True]):
        run_tests_with_strict_coverage("backend_v2/services/subservice/sample.py")
        assert mock_sub.call_count == 2
