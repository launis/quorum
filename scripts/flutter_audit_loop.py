"""Flutter Audit Loop Script.

Automated Quality Gate for the Flutter client (`client_app_v2`).
Executes sequential code hygiene and validation stages:
1. `build_runner` (Optional): Runs the Dart code generator for SDUI/Freezed/JSON models.
2. `_dart_guardrails.py` & `audit_flutter_theme_sovereignty.py`: Enforces Dart static guardrails (DGR001-DGR010) and Theme Sovereignty across full multi-line source with generated file immunity.
3. `dart format`: Formats Dart files to ensure consistent indentation and layout.
4. `dart analyze`: Statically analyzes source code to enforce architectural invariants.
5. `flutter test` (Optional): Executes Flutter unit tests with coverage reporting or isolated micro test.

Usage:
    uv run python scripts/flutter_audit_loop.py <target_directory> [--build] [--test] [--strict] [--micro]
"""

import argparse
import io
import os
import subprocess
import sys
from pathlib import Path

__all__ = [
    "main",
    "requires_dart_codegen",
    "resolve_flutter_unit_test_files",
]

_CODEGEN_DIRECTIVES: tuple[str, ...] = (
    ".g.dart",
    ".freezed.dart",
    "@freezed",
    "@Freezed",
    "@riverpod",
    "@Riverpod",
    "@JsonSerializable",
)


def requires_dart_codegen(target_path: Path) -> bool:
    """Determine whether a Flutter target requires l10n or build_runner code generation.

    Args:
        target_path: Resolved filesystem path to the target file or directory.

    Returns:
        True if the target is a directory, an `.arb` file, or a `.dart` file containing
        Freezed, Riverpod, or JsonSerializable codegen directives; False otherwise.
    """
    if target_path.is_dir():
        return True
    name_lower = target_path.name.lower()
    if name_lower.endswith(".arb"):
        return True
    if target_path.is_file() and name_lower.endswith(".dart"):
        source_text = target_path.read_text(encoding="utf-8", errors="replace")
        return any(directive in source_text for directive in _CODEGEN_DIRECTIVES)
    return False


def _collect_unit_tests_for_lib_rel(rel: Path, client_app_dir: Path) -> set[str]:
    """Collect existing test/unit and test file paths for a path relative to lib/.

    Args:
        rel: Path of the Dart source file relative to client_app_v2/lib.
        client_app_dir: Resolved path to the client_app_v2 root directory.

    Returns:
        Set of existing POSIX test paths relative to client_app_dir.
    """
    candidates: set[str] = set()
    for prefix in (Path("test/unit"), Path("test")):
        candidate_rel = (prefix / rel.parent / f"{rel.stem}_test.dart").as_posix()
        if (client_app_dir / candidate_rel).is_file():
            candidates.add(candidate_rel)
    return candidates


def resolve_flutter_unit_test_files(target_dir: str, client_app_dir: Path) -> list[str]:
    """Resolve existing Flutter unit test files corresponding to a single Dart target file.

    Args:
        target_dir: Target file path relative to workspace root or `client_app_v2`.
        client_app_dir: Resolved path to the `client_app_v2` root directory.

    Returns:
        Sorted list of existing POSIX relative paths inside `client_app_dir`.
    """
    norm = target_dir.replace("\\", "/").strip()
    if norm.startswith("client_app_v2/"):
        norm = norm[len("client_app_v2/") :]

    if norm.startswith("test/") and norm.endswith("_test.dart"):
        return [norm] if (client_app_dir / norm).is_file() else []

    if norm.startswith("lib/") and norm.endswith(".dart"):
        rel = Path(norm).relative_to("lib")
        return sorted(_collect_unit_tests_for_lib_rel(rel, client_app_dir))

    # Resolve unit tests for lib/ leaf directories in --micro mode
    if norm.startswith("lib/") and not norm.endswith(".dart"):
        dir_path = client_app_dir / norm.rstrip("/")
        if dir_path.is_dir():
            dir_candidates: set[str] = set()
            lib_root = client_app_dir / "lib"
            for dart_file in dir_path.rglob("*.dart"):
                if not dart_file.name.endswith((".g.dart", ".freezed.dart")):
                    dir_candidates.update(
                        _collect_unit_tests_for_lib_rel(dart_file.relative_to(lib_root), client_app_dir)
                    )
            return sorted(dir_candidates)

    return []


def _configure_utf8_streams() -> None:
    """Reconfigure stdout and stderr to UTF-8 encoding when backed by TextIOWrapper."""
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            try:
                stream.reconfigure(encoding="utf-8")
            except AttributeError, io.UnsupportedOperation:
                pass


def _build_flutter_cli_parser() -> argparse.ArgumentParser:
    """Construct the CLI ArgumentParser for flutter_audit_loop.py.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="""Sequential Flutter client quality gate pipeline (client_app_v2).

Executes a five-stage code hygiene and validation sequence:
  1/5 (Optional): Code generation (flutter gen-l10n & dart run build_runner build -d)
  2/5: Dart codebase guardrails & Theme Sovereignty (scripts/_dart_guardrails.py & scripts/audit_flutter_theme_sovereignty.py)
  3/5: Code style formatting (dart format)
  4/5: Static architectural analysis (dart analyze)
  5/5 (Optional): Flutter unit tests and coverage (flutter test --coverage or isolated micro test)
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples (PowerShell):
  uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/
  uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/ --build
  uv run python scripts/flutter_audit_loop.py client_app_v2/ --strict --test
  uv run python scripts/flutter_audit_loop.py client_app_v2/lib/app.dart --build --strict --micro
""",
    )
    parser.add_argument(
        "target_directory",
        nargs="?",
        default=None,
        help="Target directory or file path within client_app_v2 to format, analyze, and test.",
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Execute code generation (flutter gen-l10n and build_runner build -d).",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run Flutter unit tests with coverage reporting (flutter test --coverage).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enforce strict Dart Guardrail validation (DGR001-DGR010).",
    )
    parser.add_argument(
        "--micro",
        action="store_true",
        help=(
            "Execute fast single-file micro-audit: run codegen only when target uses "
            "Freezed/Riverpod/JsonSerializable part directives, and run the target's isolated unit test."
        ),
    )
    return parser


def _ensure_client_app_working_dir(current_dir: Path) -> Path:
    """Verify or switch the process working directory to client_app_v2.

    Args:
        current_dir: Resolved current working directory.

    Returns:
        Resolved Path to the client_app_v2 directory.

    Raises:
        SystemExit: If executed outside both repository root and client_app_v2.
    """
    if current_dir.name == "client_app_v2":
        return current_dir
    client_app_dir = current_dir / "client_app_v2"
    if client_app_dir.exists():
        os.chdir(client_app_dir)
        return client_app_dir
    print("Error: Script must be run from repository root or client_app_v2 directory.")
    sys.exit(1)


def _normalize_cmd_dir(target_dir: str) -> str:
    """Normalize the CLI target directory relative to client_app_v2.

    Args:
        target_dir: Raw CLI target directory or file string.

    Returns:
        Normalized relative target string for dart format and dart analyze.
    """
    cmd_dir = target_dir
    if cmd_dir.replace("\\", "/").startswith("client_app_v2/"):
        cmd_dir = cmd_dir[len("client_app_v2/") :]
    elif cmd_dir.strip("\\/") == "client_app_v2":
        cmd_dir = "."
    return cmd_dir if cmd_dir else "."


def _resolve_target_scan_dir(target_dir: str, cmd_dir: str, root_dir: Path) -> Path:
    """Resolve the filesystem path to scan for Dart guardrails and theme sovereignty.

    Args:
        target_dir: Raw CLI target string.
        cmd_dir: Normalized relative target string inside client_app_v2.
        root_dir: Resolved repository root directory.

    Returns:
        Resolved Path for static guardrail scanning.
    """
    raw_target = Path(target_dir)
    if raw_target.is_absolute():
        return raw_target
    if cmd_dir == ".":
        return root_dir / "client_app_v2"
    target_scan_dir = root_dir / "client_app_v2" / cmd_dir
    if not target_scan_dir.exists():
        return root_dir / "client_app_v2" / "lib"
    return target_scan_dir


def _run_codegen_stage(
    run_build: bool,
    run_micro: bool,
    target_scan_dir: Path,
    cmd_dir: str,
    total_steps: int,
) -> None:
    """Execute Stage 1 (Optional l10n and build_runner code generation).

    Args:
        run_build: Whether --build was requested.
        run_micro: Whether --micro mode is active.
        target_scan_dir: Resolved target file or directory path.
        cmd_dir: Normalized relative target path string.
        total_steps: Total number of pipeline steps for progress output.

    Raises:
        SystemExit: If l10n or build_runner exits with a non-zero code.
    """
    if not run_build:
        print(f"\n⏭️ 1/{total_steps}: Skipping code generation (no --build flag).")
        return
    if run_micro and target_scan_dir.is_file() and not requires_dart_codegen(target_scan_dir):
        print(f"\n⏭️ 1/{total_steps}: Micro mode — skipping code generation (no codegen directives in {cmd_dir}).")
        return

    print(f"\n⏳ 1/{total_steps}: Running code generator (flutter gen-l10n & build_runner)...")
    res_l10n = subprocess.run(["flutter", "gen-l10n"], shell=True)
    if res_l10n.returncode != 0:
        print("❌ L10N generation failed! Aborting.")
        sys.exit(res_l10n.returncode)

    res = subprocess.run(["dart", "run", "build_runner", "build", "-d"], shell=True)
    if res.returncode != 0:
        print("❌ Generator failed! Aborting.")
        sys.exit(res.returncode)
    print("✅ Generation complete.")


def _run_guardrail_format_and_analyze_stages(
    root_dir: Path,
    target_scan_dir: Path,
    cmd_dir: str,
    run_strict: bool,
    total_steps: int,
) -> None:
    """Execute Stage 2 (Dart Guardrails & Theme Sovereignty), Stage 3 (dart format), and Stage 4 (dart analyze).

    Args:
        root_dir: Resolved repository root directory.
        target_scan_dir: Resolved target path for guardrail scanning.
        cmd_dir: Normalized target path for dart format and dart analyze.
        run_strict: Whether strict Dart guardrail mode is enabled.
        total_steps: Total number of pipeline steps for progress output.

    Raises:
        SystemExit: If any guardrail, format, or static analysis stage fails.
    """
    print(f"\n⏳ 2/{total_steps}: Checking Dart Codebase Guardrails & Theme Sovereignty...")
    dart_guardrails_script = root_dir / "scripts" / "_dart_guardrails.py"
    guardrail_cmd = [sys.executable, str(dart_guardrails_script), str(target_scan_dir)]
    if run_strict:
        guardrail_cmd.append("--strict")
    res_guardrail = subprocess.run(guardrail_cmd)
    if res_guardrail.returncode != 0:
        print("\n❌ AUDIT FAILED: Fatal Dart guardrail violations detected!")
        sys.exit(res_guardrail.returncode)

    theme_sovereignty_script = root_dir / "scripts" / "audit_flutter_theme_sovereignty.py"
    res_theme = subprocess.run([sys.executable, str(theme_sovereignty_script), str(target_scan_dir)])
    if res_theme.returncode != 0:
        print("\n❌ AUDIT FAILED: Flutter Theme Sovereignty violations detected!")
        sys.exit(res_theme.returncode)
    print("✅ Dart Guardrails & Theme Sovereignty passed.")

    print(f"\n⏳ 3/{total_steps}: Formatting code (dart format {cmd_dir})...")
    res_fmt = subprocess.run(["dart", "format", cmd_dir], shell=True)
    if res_fmt.returncode != 0:
        print("❌ Formatting failed!")
        sys.exit(res_fmt.returncode)
    print("✅ Formatting complete.")

    print(f"\n⏳ 4/{total_steps}: Analyzing code (dart analyze {cmd_dir})...")
    res_analyze = subprocess.run(["dart", "analyze", cmd_dir], shell=True)
    if res_analyze.returncode != 0:
        print("\n❌ AUDIT FAILED: Analysis found errors in code. Fix them before proceeding!")
        print("🤖 AI INSTRUCTION: Read the above report and resolve static analysis errors.")
        print(
            "🚨 THE ANTI-TDD TRAP MANDATE: The architectural laws in `.agents/rules` are ABSOLUTE. Do NOT fall into the 'Test-Driven Development Trap' where you preserve legacy dict-parsing, fallback hacks, or hardcoded strings just to satisfy existing unit tests. If old tests conflict with the new rules (e.g., No-String Mandate, De-Generator, Pydantic V2), you MUST ruthlessly tear down the legacy code AND rewrite the tests. A green test suite that violates architectural sovereignty is a failed state.\n"
        )
        sys.exit(res_analyze.returncode)
    print("✅ Analysis complete.")


def _run_flutter_test_stage(
    run_micro: bool,
    run_test: bool,
    cmd_dir: str,
    target_scan_dir: Path,
    client_app_dir: Path,
    total_steps: int,
) -> None:
    """Execute Stage 5 (isolated micro unit test or full flutter test --coverage).

    Args:
        run_micro: Whether --micro mode is active.
        run_test: Whether --test mode is active.
        cmd_dir: Normalized relative target path inside client_app_v2.
        target_scan_dir: Resolved filesystem path of the target.
        client_app_dir: Resolved path to client_app_v2.
        total_steps: Total number of pipeline steps for progress output.

    Raises:
        SystemExit: If unit tests are missing in micro mode or flutter test fails.
    """
    is_micro_target = cmd_dir.endswith(".dart") or (
        target_scan_dir.is_dir()
        and cmd_dir.replace("\\", "/").startswith("lib/")
        and any(not p.name.endswith((".g.dart", ".freezed.dart")) for p in target_scan_dir.rglob("*.dart"))
    )
    if run_micro and is_micro_target:
        resolved_tests = resolve_flutter_unit_test_files(cmd_dir, client_app_dir)
        if not resolved_tests:
            print(
                f"\n❌ AUDIT FAILED: Missing isolated unit test for {cmd_dir}! "
                "Create the corresponding *_test.dart file under client_app_v2/test/unit/."
            )
            sys.exit(1)
        print(f"\n⏳ 5/{total_steps}: Running isolated Flutter unit tests ({', '.join(resolved_tests)})...")
        res_test = subprocess.run(["flutter", "test", *resolved_tests], shell=True)
        if res_test.returncode != 0:
            print("\n❌ AUDIT FAILED: Flutter unit tests failed!")
            sys.exit(res_test.returncode)
        print("✅ Flutter unit tests passed.")
    elif run_test:
        print(f"\n⏳ 5/{total_steps}: Running Flutter unit tests and coverage (flutter test --coverage)...")
        res_test = subprocess.run(["flutter", "test", "--coverage"], shell=True)
        if res_test.returncode != 0:
            print("\n❌ AUDIT FAILED: Flutter tests failed!")
            sys.exit(res_test.returncode)
        print("✅ Flutter tests passed.")


def main(argv: list[str] | None = None) -> None:
    """Main CLI entrypoint executing the sequential Flutter quality gate pipeline.

    Parses CLI flags and executes optional code generation, Dart static guardrail
    validation (_dart_guardrails.py & audit_flutter_theme_sovereignty.py), dart format,
    dart analyze, and optional flutter test.

    Args:
        argv: Optional list of CLI arguments; defaults to sys.argv[1:] when None.

    Returns:
        None.

    Raises:
        SystemExit: If CLI arguments are missing, working directory is invalid, or any
            validation stage returns a non-zero exit code.
    """
    _configure_utf8_streams()
    parser = _build_flutter_cli_parser()
    args = parser.parse_args(argv)

    if not args.target_directory:
        print("Usage: python flutter_audit_loop.py <target_directory> [--build] [--test] [--strict] [--micro]")
        sys.exit(1)

    target_dir: str = args.target_directory
    run_build: bool = bool(args.build)
    run_test: bool = bool(args.test)
    run_strict: bool = bool(args.strict)
    run_micro: bool = bool(args.micro)

    current_dir = Path(os.getcwd()).resolve()
    root_dir = current_dir if current_dir.name != "client_app_v2" else current_dir.parent
    client_app_dir = _ensure_client_app_working_dir(current_dir)

    print(f"\n🚀 Running quality loop for target: {target_dir}")
    print("--------------------------------------------------")

    cmd_dir = _normalize_cmd_dir(target_dir)
    target_scan_dir = _resolve_target_scan_dir(target_dir, cmd_dir, root_dir)
    total_steps = 5 if (run_test or run_micro) else 4

    _run_codegen_stage(run_build, run_micro, target_scan_dir, cmd_dir, total_steps)
    _run_guardrail_format_and_analyze_stages(root_dir, target_scan_dir, cmd_dir, run_strict, total_steps)
    _run_flutter_test_stage(run_micro, run_test, cmd_dir, target_scan_dir, client_app_dir, total_steps)

    print("\n🏆 All clean! Target conforms to architectural standards.\n")


if __name__ == "__main__":
    main()
