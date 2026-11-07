"""Hermetically Isolated ISTQB Unit Tests for flutter_audit_loop.py.

Verifies CLI argument parsing, working directory validation, code generator (--build),
Dart static guardrail execution (_dart_guardrails.py & audit_flutter_theme_sovereignty.py),
dart format, dart analyze, Flutter unit tests (--test), and error status handling.
Enforces 100% hermetic isolation via module-scoped @patch('scripts.flutter_audit_loop.*').
"""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.flutter_audit_loop import (
    main,
    requires_dart_codegen,
    resolve_flutter_unit_test_files,
)


def _mock_completed_process(
    returncode: int = 0, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    """Create a hermetic subprocess.CompletedProcess mock.

    Args:
        returncode: Process exit status code.
        stdout: Captured standard output string.
        stderr: Captured standard error string.

    Returns:
        Configured CompletedProcess instance.
    """
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


# ==============================================================================
# Partition 1: CLI Argument Parsing & Root Directory Validation
# ==============================================================================


@patch("scripts.flutter_audit_loop.sys.exit")
def test_cli_no_args_triggers_exit(mock_exit: MagicMock) -> None:
    """Verify that calling without target argument triggers usage exit."""
    mock_exit.side_effect = SystemExit(1)
    with patch.object(sys, "argv", ["flutter_audit_loop.py"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 1


@patch("scripts.flutter_audit_loop.sys.exit")
def test_cli_invalid_root_directory_exit(mock_exit: MagicMock, tmp_path: Path) -> None:
    """Verify exit when executed outside repository root where client_app_v2 does not exist."""
    mock_exit.side_effect = SystemExit(1)
    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(tmp_path)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


# ==============================================================================
# Partition 2: Directory Normalization & Navigation
# ==============================================================================


@patch("scripts.flutter_audit_loop.subprocess.run", return_value=_mock_completed_process(0))
@patch("scripts.flutter_audit_loop.os.chdir")
def test_cli_executed_from_root_navigates_to_client_app(
    mock_chdir: MagicMock, mock_sub: MagicMock, tmp_path: Path
) -> None:
    """Verify script switches directory to client_app_v2 when launched from root."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(tmp_path)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib"]):
            main()
            mock_chdir.assert_called_once_with(client_app)


@patch("scripts.flutter_audit_loop.subprocess.run", return_value=_mock_completed_process(0))
@patch("scripts.flutter_audit_loop.os.chdir")
def test_cli_executed_inside_client_app_v2_does_not_chdir(
    mock_chdir: MagicMock, mock_sub: MagicMock, tmp_path: Path
) -> None:
    """Verify script does not call os.chdir when current directory is already client_app_v2."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "client_app_v2/lib/features"]):
            main()
            mock_chdir.assert_not_called()


@patch("scripts.flutter_audit_loop.subprocess.run", return_value=_mock_completed_process(0))
def test_cli_target_dir_prefix_stripping(mock_sub: MagicMock, tmp_path: Path) -> None:
    """Verify client_app_v2 prefix and trailing slash are stripped cleanly to '.' for format and analyze."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "client_app_v2"]):
            main()
            calls = mock_sub.call_args_list
            assert any(c[0][0] == ["dart", "format", "."] for c in calls)

        mock_sub.reset_mock()
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "client_app_v2/"]):
            main()
            calls_slash = mock_sub.call_args_list
            assert any(c[0][0] == ["dart", "format", "."] for c in calls_slash)


@patch("scripts.flutter_audit_loop.subprocess.run", return_value=_mock_completed_process(0))
def test_cli_absolute_target_path_resolution(mock_sub: MagicMock, tmp_path: Path) -> None:
    """Verify absolute target path is passed directly to guardrail scanners without rewriting."""
    client_app = tmp_path / "client_app_v2"
    lib_dir = client_app / "lib"
    lib_dir.mkdir(parents=True)
    abs_target = (lib_dir / "widget.dart").resolve()
    abs_target.write_text("class MyWidget {}\n", encoding="utf-8")

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        main([str(abs_target)])
        guardrail_calls = [c[0][0] for c in mock_sub.call_args_list if "_dart_guardrails.py" in str(c[0][0])]
        assert len(guardrail_calls) == 1
        assert str(abs_target) in guardrail_calls[0]


# ==============================================================================
# Partition 3: Code Generation & Build Stage (--build)
# ==============================================================================


@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_build_flag_triggers_l10n_and_build_runner(mock_sub: MagicMock, tmp_path: Path) -> None:
    """Verify --build flag runs flutter gen-l10n and build_runner build."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()

    mock_sub.return_value = _mock_completed_process(0)
    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib", "--build"]):
            main()
            calls = [c[0][0] for c in mock_sub.call_args_list]
            assert ["flutter", "gen-l10n"] in calls
            assert ["dart", "run", "build_runner", "build", "-d"] in calls


def test_requires_dart_codegen_positive_and_negative_partitions(tmp_path: Path) -> None:
    """Verify requires_dart_codegen across directories, .arb files, Freezed/Riverpod Dart files, and plain widgets."""
    # Directory -> True
    assert requires_dart_codegen(tmp_path) is True

    # .arb file -> True
    arb_file = tmp_path / "app_en.arb"
    arb_file.write_text("{}", encoding="utf-8")
    assert requires_dart_codegen(arb_file) is True

    # Plain Dart widget -> False
    plain_dart = tmp_path / "widget.dart"
    plain_dart.write_text("class MyWidget {}\n", encoding="utf-8")
    assert requires_dart_codegen(plain_dart) is False

    # Dart file with Freezed / Riverpod / .g.dart -> True
    codegen_dart = tmp_path / "model.dart"
    codegen_dart.write_text("part 'model.freezed.dart';\n@freezed\nclass Model {}\n", encoding="utf-8")
    assert requires_dart_codegen(codegen_dart) is True

    # Non-existent or non-dart file -> False
    assert requires_dart_codegen(tmp_path / "missing.dart") is False
    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("@freezed", encoding="utf-8")
    assert requires_dart_codegen(txt_file) is False


def test_resolve_flutter_unit_test_files_positive_and_negative_partitions(tmp_path: Path) -> None:
    """Verify resolve_flutter_unit_test_files resolves matching test/unit and test files or empty list when absent."""
    client_app = tmp_path / "client_app_v2"
    unit_test = client_app / "test" / "unit" / "features" / "studio" / "my_view_test.dart"
    unit_test.parent.mkdir(parents=True)
    unit_test.write_text("void main() {}\n", encoding="utf-8")

    resolved = resolve_flutter_unit_test_files(
        "client_app_v2/lib/features/studio/my_view.dart",
        client_app,
    )
    assert resolved == ["test/unit/features/studio/my_view_test.dart"]

    # Direct test target
    direct_resolved = resolve_flutter_unit_test_files(
        "client_app_v2/test/unit/features/studio/my_view_test.dart",
        client_app,
    )
    assert direct_resolved == ["test/unit/features/studio/my_view_test.dart"]

    # Missing test file -> empty list
    assert resolve_flutter_unit_test_files("lib/features/studio/untested.dart", client_app) == []
    assert resolve_flutter_unit_test_files("test/unit/missing_test.dart", client_app) == []
    assert resolve_flutter_unit_test_files("lib/features/studio", client_app) == []


@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_micro_skips_codegen_for_plain_widget_and_runs_isolated_test(mock_sub: MagicMock, tmp_path: Path) -> None:
    """Verify --micro skips gen-l10n and build_runner for plain widget and executes isolated unit test."""
    client_app = tmp_path / "client_app_v2"
    lib_dir = client_app / "lib"
    lib_dir.mkdir(parents=True)
    target_file = lib_dir / "app.dart"
    target_file.write_text("class MyApp {}\n", encoding="utf-8")

    test_dir = client_app / "test" / "unit"
    test_dir.mkdir(parents=True)
    (test_dir / "app_test.dart").write_text("void main() {}\n", encoding="utf-8")

    mock_sub.return_value = _mock_completed_process(0)
    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(
            sys,
            "argv",
            ["flutter_audit_loop.py", "client_app_v2/lib/app.dart", "--build", "--strict", "--micro"],
        ):
            main()
            calls = [c[0][0] for c in mock_sub.call_args_list]
            assert ["flutter", "gen-l10n"] not in calls
            assert ["dart", "run", "build_runner", "build", "-d"] not in calls
            assert ["flutter", "test", "test/unit/app_test.dart"] in calls


@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_micro_runs_codegen_when_target_contains_freezed_directive(mock_sub: MagicMock, tmp_path: Path) -> None:
    """Verify --micro executes gen-l10n and build_runner when target file contains codegen directives."""
    client_app = tmp_path / "client_app_v2"
    lib_dir = client_app / "lib"
    lib_dir.mkdir(parents=True)
    target_file = lib_dir / "model.dart"
    target_file.write_text("part 'model.freezed.dart';\n", encoding="utf-8")

    test_dir = client_app / "test" / "unit"
    test_dir.mkdir(parents=True)
    (test_dir / "model_test.dart").write_text("void main() {}\n", encoding="utf-8")

    mock_sub.return_value = _mock_completed_process(0)
    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(
            sys,
            "argv",
            ["flutter_audit_loop.py", "client_app_v2/lib/model.dart", "--build", "--micro"],
        ):
            main()
            calls = [c[0][0] for c in mock_sub.call_args_list]
            assert ["flutter", "gen-l10n"] in calls
            assert ["dart", "run", "build_runner", "build", "-d"] in calls
            assert ["flutter", "test", "test/unit/model_test.dart"] in calls


@patch("scripts.flutter_audit_loop.sys.exit")
@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_build_l10n_failure_triggers_exit(mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path) -> None:
    """Verify failure during l10n generation exits immediately."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_exit.side_effect = SystemExit(1)
    mock_sub.return_value = _mock_completed_process(1)

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib", "--build"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("scripts.flutter_audit_loop.sys.exit")
@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_build_runner_failure_triggers_exit(mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path) -> None:
    """Verify failure during build_runner generation exits immediately."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_exit.side_effect = SystemExit(2)
    mock_sub.side_effect = [
        _mock_completed_process(0),  # gen-l10n succeeds
        _mock_completed_process(2),  # build_runner fails
    ]

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib", "--build"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 2


# ==============================================================================
# Partition 4: Dart Static Guardrails Stage (_dart_guardrails.py & theme sovereignty)
# ==============================================================================


@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_strict_flag_propagates_to_dart_guardrails(mock_sub: MagicMock, tmp_path: Path) -> None:
    """Verify --strict flag appends --strict to the _dart_guardrails.py invocation."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_sub.return_value = _mock_completed_process(0)

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib", "--strict"]):
            main()
            guardrail_calls = [c[0][0] for c in mock_sub.call_args_list if "_dart_guardrails.py" in str(c[0][0])]
            assert len(guardrail_calls) == 1
            assert "--strict" in guardrail_calls[0]


@patch("scripts.flutter_audit_loop.subprocess.run")
@patch("scripts.flutter_audit_loop.os.chdir")
def test_cli_guardrails_targets_specific_file_when_provided(
    mock_chdir: MagicMock, mock_sub: MagicMock, tmp_path: Path
) -> None:
    """Verify that providing a specific target file passes that specific file to _dart_guardrails."""
    client_app = tmp_path / "client_app_v2"
    models_dir = client_app / "lib" / "features" / "studio" / "models"
    models_dir.mkdir(parents=True)
    target_file = models_dir / "workflow.dart"
    target_file.write_text("// test", encoding="utf-8")
    mock_sub.return_value = _mock_completed_process(0)

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(tmp_path)):
        with patch.object(
            sys, "argv", ["flutter_audit_loop.py", "client_app_v2/lib/features/studio/models/workflow.dart", "--strict"]
        ):
            main()
            guardrail_calls = [c[0][0] for c in mock_sub.call_args_list if "_dart_guardrails.py" in str(c[0][0])]
            assert len(guardrail_calls) == 1
            assert str(target_file) in guardrail_calls[0]
            mock_chdir.assert_called_once_with(client_app)


@patch("scripts.flutter_audit_loop.sys.exit")
@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_guardrail_failure_triggers_exit(mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path) -> None:
    """Verify fatal guardrail violations trigger script exit."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_exit.side_effect = SystemExit(1)
    mock_sub.return_value = _mock_completed_process(1)

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("scripts.flutter_audit_loop.sys.exit")
@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_theme_sovereignty_failure_triggers_exit(mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path) -> None:
    """Verify Flutter Theme Sovereignty violations trigger script exit."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_exit.side_effect = SystemExit(1)
    mock_sub.side_effect = [
        _mock_completed_process(0),  # _dart_guardrails.py passes
        _mock_completed_process(1),  # audit_flutter_theme_sovereignty.py fails
    ]

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


# ==============================================================================
# Partition 5: Formatting, Static Analysis, and Tests
# ==============================================================================


@patch("scripts.flutter_audit_loop.sys.exit")
@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_format_failure_triggers_exit(mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path) -> None:
    """Verify dart format failure triggers exit."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_exit.side_effect = SystemExit(1)
    mock_sub.side_effect = [
        _mock_completed_process(0),  # guardrails pass
        _mock_completed_process(0),  # theme sovereignty passes
        _mock_completed_process(1),  # dart format fails
    ]

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("scripts.flutter_audit_loop.sys.exit")
@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_analyze_failure_triggers_exit(mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path) -> None:
    """Verify dart analyze failure triggers exit."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_exit.side_effect = SystemExit(3)
    mock_sub.side_effect = [
        _mock_completed_process(0),  # guardrails pass
        _mock_completed_process(0),  # theme sovereignty passes
        _mock_completed_process(0),  # dart format passes
        _mock_completed_process(3),  # dart analyze fails
    ]

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 3


@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_test_flag_executes_flutter_test(mock_sub: MagicMock, tmp_path: Path) -> None:
    """Verify --test flag runs flutter test --coverage."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_sub.return_value = _mock_completed_process(0)

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib", "--test"]):
            main()
            calls = [c[0][0] for c in mock_sub.call_args_list]
            assert ["flutter", "test", "--coverage"] in calls


@patch("scripts.flutter_audit_loop.sys.exit")
@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_micro_missing_unit_test_triggers_fail_fast_exit(
    mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path
) -> None:
    """Verify --micro exits with code 1 when the target Dart file has no corresponding unit test."""
    client_app = tmp_path / "client_app_v2"
    lib_dir = client_app / "lib"
    lib_dir.mkdir(parents=True)
    (lib_dir / "untested.dart").write_text("class Untested {}\n", encoding="utf-8")

    mock_exit.side_effect = SystemExit(1)
    mock_sub.return_value = _mock_completed_process(0)

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "client_app_v2/lib/untested.dart", "--micro"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("scripts.flutter_audit_loop.sys.exit")
@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_micro_unit_test_failure_triggers_exit(mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path) -> None:
    """Verify --micro exits with the failing test returncode when the isolated unit test fails."""
    client_app = tmp_path / "client_app_v2"
    lib_dir = client_app / "lib"
    lib_dir.mkdir(parents=True)
    (lib_dir / "app.dart").write_text("class MyApp {}\n", encoding="utf-8")
    test_dir = client_app / "test" / "unit"
    test_dir.mkdir(parents=True)
    (test_dir / "app_test.dart").write_text("void main() {}\n", encoding="utf-8")

    mock_exit.side_effect = SystemExit(1)
    mock_sub.side_effect = [
        _mock_completed_process(0),  # guardrails pass
        _mock_completed_process(0),  # theme sovereignty passes
        _mock_completed_process(0),  # dart format passes
        _mock_completed_process(0),  # dart analyze passes
        _mock_completed_process(1),  # isolated flutter test fails
    ]

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "client_app_v2/lib/app.dart", "--micro"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


@patch("scripts.flutter_audit_loop.subprocess.run", return_value=_mock_completed_process(0))
@patch("scripts.flutter_audit_loop.os.chdir")
def test_cli_micro_lib_leaf_directory_positive_and_negative(
    mock_chdir: MagicMock, mock_sub: MagicMock, tmp_path: Path
) -> None:
    """Verify resolve_flutter_unit_test_files and --micro handle lib/ leaf directories positively and negatively."""
    client_app = tmp_path / "client_app_v2"
    feature_dir = client_app / "lib" / "features" / "studio"
    feature_dir.mkdir(parents=True)
    (feature_dir / "studio_view.dart").write_text("class StudioView {}\n", encoding="utf-8")
    (feature_dir / "studio_view.freezed.dart").write_text("// generated\n", encoding="utf-8")

    test_dir = client_app / "test" / "unit" / "features" / "studio"
    test_dir.mkdir(parents=True)
    (test_dir / "studio_view_test.dart").write_text("void main() {}\n", encoding="utf-8")

    resolved = resolve_flutter_unit_test_files("client_app_v2/lib/features/studio", client_app)
    assert resolved == ["test/unit/features/studio/studio_view_test.dart"]

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(tmp_path)):
        main(["client_app_v2/lib/features/studio", "--micro"])
        calls = [c[0][0] for c in mock_sub.call_args_list]
        assert ["flutter", "test", "test/unit/features/studio/studio_view_test.dart"] in calls
        mock_chdir.assert_called_once_with(client_app)

    untested_dir = client_app / "lib" / "features" / "untested_leaf"
    untested_dir.mkdir(parents=True)
    (untested_dir / "widget.dart").write_text("class UntestedWidget {}\n", encoding="utf-8")
    assert resolve_flutter_unit_test_files("lib/features/untested_leaf", client_app) == []

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(tmp_path)):
        with pytest.raises(SystemExit) as exc:
            main(["client_app_v2/lib/features/untested_leaf", "--micro"])
        assert exc.value.code == 1


@patch("scripts.flutter_audit_loop.sys.exit")
@patch("scripts.flutter_audit_loop.subprocess.run")
def test_cli_flutter_test_failure_triggers_exit(mock_sub: MagicMock, mock_exit: MagicMock, tmp_path: Path) -> None:
    """Verify flutter test failure triggers exit."""
    client_app = tmp_path / "client_app_v2"
    client_app.mkdir()
    mock_exit.side_effect = SystemExit(1)
    mock_sub.side_effect = [
        _mock_completed_process(0),  # guardrails pass
        _mock_completed_process(0),  # theme sovereignty passes
        _mock_completed_process(0),  # dart format passes
        _mock_completed_process(0),  # dart analyze passes
        _mock_completed_process(1),  # flutter test fails
    ]

    with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
        with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib", "--test"]):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1


# ==============================================================================
# Partition 6: Terminal Stream Reconfiguration Resilience
# ==============================================================================


@patch("scripts.flutter_audit_loop.subprocess.run", return_value=_mock_completed_process(0))
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
            with patch("scripts.flutter_audit_loop.os.getcwd", return_value=str(client_app)):
                with patch.object(sys, "argv", ["flutter_audit_loop.py", "lib"]):
                    main()
                    assert mock_sub.called


def test_normalize_cmd_dir_handles_empty_and_prefixed_paths() -> None:
    """Verify _normalize_cmd_dir strips client_app_v2 prefix and defaults empty strings to dot."""
    from scripts.flutter_audit_loop import _normalize_cmd_dir

    assert _normalize_cmd_dir("client_app_v2/lib/main.dart") == "lib/main.dart"
    assert _normalize_cmd_dir("client_app_v2/") == "."
    assert _normalize_cmd_dir("client_app_v2") == "."
    assert _normalize_cmd_dir("lib/features") == "lib/features"
