"""Hermetically Isolated ISTQB Unit Tests for flutter_audit_loop.py.

Verifies CLI argument parsing, working directory validation, code generator (--build),
Dart static guardrail execution (_dart_guardrails.py), dart format, dart analyze,
Flutter unit tests (--test), and error status handling.
Enforces 100% hermetic isolation via @patch('subprocess.run') and @patch('sys.exit').
"""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.flutter_audit_loop import main


def _mock_completed_process(
    returncode: int = 0, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    """Helper creating a hermetic subprocess.CompletedProcess mock."""
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


# ==============================================================================
# Partition 1: CLI Argument Parsing & Root Directory Validation
# ==============================================================================


@patch("sys.exit")
def test_cli_no_args_triggers_exit(mock_exit: MagicMock) -> None:
    """Verify that calling without target argument triggers usage exit."""
    mock_exit.side_effect = SystemExit(1)
    with patch.object(sys, "argv", ["flutter_audit_loop.py"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1


@patch("sys.exit")
def test_cli_invalid_root_directory_exit(mock_exit: MagicMock, tmp_path: Path) -> None:
    """Verify exit when executed outside repository root where client_app_v2 does not exist."""
    mock_exit.side_effect = SystemExit(1)
    with patch("os.getcwd", return_value=str(tmp_path)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


# ==============================================================================
# Partition 2: Directory Normalization & Navigation
# ==============================================================================


@patch("subprocess.run", return_value=_mock_completed_process(0))
@patch("os.chdir")
def test_cli_executed_from_root_navigates_to_client_app(
    mock_chdir: MagicMock, mock_sub: MagicMock, tmp_path: Path
) -> None:
    """Verify script switches directory to client_app_v2 when launched from root."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()

    with patch("os.getcwd", return_value=str(tmp_path)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib"]):
            main()
            mock_chdir.assert_called_once_with(client_app)


@patch("subprocess.run", return_value=_mock_completed_process(0))
@patch("os.chdir")
def test_cli_executed_inside_client_app_v2_does_not_chdir(
    mock_chdir: MagicMock, mock_sub: MagicMock, tmp_path: Path
) -> None:
    """Verify script does not call os.chdir when current directory is already client_app_v2."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()

    with patch("os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "client_app_v2/lib/features"]):
            main()
            mock_chdir.assert_not_called()


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_cli_target_dir_prefix_stripping(mock_sub: MagicMock, tmp_path: Path) -> None:
    """Verify client_app_v2 prefix is stripped cleanly for format and analyze commands."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()

    with patch("os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "client_app_v2"]):
            main()
            calls = mock_sub.call_args_list
            # Verify dart format received "."
            assert any(c[0][0] == ["dart", "format", "."] for c in calls)


# ==============================================================================
# Partition 3: Code Generation & Build Stage (--build)
# ==============================================================================


@patch("subprocess.run")
def test_cli_build_flag_triggers_l10n_and_build_runner(mock_sub: MagicMock, tmp_path: Path) -> None:
    """Verify --build flag runs flutter gen-l10n and build_runner build."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()

    mock_sub.return_value = _mock_completed_process(0)
    with patch("os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib", "--build"]):
            main()
            calls = [c[0][0] for c in mock_sub.call_args_list]
            assert ["flutter", "gen-l10n"] in calls
            assert ["dart", "run", "build_runner", "build", "-d"] in calls


@patch("sys.exit")
@patch("subprocess.run")
def test_cli_build_l10n_failure_triggers_exit(
    mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path
) -> None:
    """Verify failure during l10n generation exits immediately."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_exit.side_effect = SystemExit(1)
    mock_sub.return_value = _mock_completed_process(1)

    with patch("os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib", "--build"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("sys.exit")
@patch("subprocess.run")
def test_cli_build_runner_failure_triggers_exit(
    mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path
) -> None:
    """Verify failure during build_runner generation exits immediately."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_exit.side_effect = SystemExit(2)
    mock_sub.side_effect = [
        _mock_completed_process(0),  # gen-l10n succeeds
        _mock_completed_process(2),  # build_runner fails
    ]

    with patch("os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib", "--build"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 2


# ==============================================================================
# Partition 4: Dart Static Guardrails Stage (_dart_guardrails.py)
# ==============================================================================


@patch("subprocess.run")
def test_cli_strict_flag_propagates_to_dart_guardrails(mock_sub: MagicMock, tmp_path: Path) -> None:
    """Verify --strict flag appends --strict to the _dart_guardrails.py invocation."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_sub.return_value = _mock_completed_process(0)

    with patch("os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib", "--strict"]):
            main()
            # Find guardrail call
            guardrail_calls = [c[0][0] for c in mock_sub.call_args_list if "_dart_guardrails.py" in str(c[0][0])]
            assert len(guardrail_calls) == 1
            assert "--strict" in guardrail_calls[0]


@patch("sys.exit")
@patch("subprocess.run")
def test_cli_guardrail_failure_triggers_exit(
    mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path
) -> None:
    """Verify fatal guardrail violations trigger script exit."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_exit.side_effect = SystemExit(1)
    mock_sub.return_value = _mock_completed_process(1)

    with patch("os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


# ==============================================================================
# Partition 5: Formatting, Static Analysis, and Tests
# ==============================================================================


@patch("sys.exit")
@patch("subprocess.run")
def test_cli_format_failure_triggers_exit(
    mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path
) -> None:
    """Verify dart format failure triggers exit."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_exit.side_effect = SystemExit(1)
    mock_sub.side_effect = [
        _mock_completed_process(0),  # guardrails pass
        _mock_completed_process(1),  # dart format fails
    ]

    with patch("os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("sys.exit")
@patch("subprocess.run")
def test_cli_analyze_failure_triggers_exit(
    mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path
) -> None:
    """Verify dart analyze failure triggers exit."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_exit.side_effect = SystemExit(3)
    mock_sub.side_effect = [
        _mock_completed_process(0),  # guardrails pass
        _mock_completed_process(0),  # dart format passes
        _mock_completed_process(3),  # dart analyze fails
    ]

    with patch("os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 3


@patch("subprocess.run")
def test_cli_test_flag_executes_flutter_test(mock_sub: MagicMock, tmp_path: Path) -> None:
    """Verify --test flag runs flutter test --coverage."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_sub.return_value = _mock_completed_process(0)

    with patch("os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib", "--test"]):
            main()
            calls = [c[0][0] for c in mock_sub.call_args_list]
            assert ["flutter", "test", "--coverage"] in calls


@patch("sys.exit")
@patch("subprocess.run")
def test_cli_flutter_test_failure_triggers_exit(
    mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path
) -> None:
    """Verify flutter test failure triggers exit."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_exit.side_effect = SystemExit(1)
    mock_sub.side_effect = [
        _mock_completed_process(0),  # guardrails pass
        _mock_completed_process(0),  # dart format passes
        _mock_completed_process(0),  # dart analyze passes
        _mock_completed_process(1),  # flutter test fails
    ]

    with patch("os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib", "--test"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


# ==============================================================================
# Partition 6: Terminal Stream Reconfiguration Resilience
# ==============================================================================


@patch("subprocess.run", return_value=_mock_completed_process(0))
def test_stdout_stderr_reconfigure_exception_resilience(mock_sub: MagicMock, tmp_path: Path) -> None:
    """Verify stdout/stderr reconfigure exceptions (UnsupportedOperation) are swallowed gracefully."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()

    mock_stdout = MagicMock(spec=io.TextIOWrapper)
    mock_stdout.reconfigure.side_effect = io.UnsupportedOperation("not supported")
    mock_stderr = MagicMock(spec=io.TextIOWrapper)
    mock_stderr.reconfigure.side_effect = AttributeError("no attribute")

    with patch.object(sys, "stdout", mock_stdout):
        with patch.object(sys, "stderr", mock_stderr):
            with patch("os.getcwd", return_value=str(client_app)):
                with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib"]):
                    main()
                    assert mock_sub.called
