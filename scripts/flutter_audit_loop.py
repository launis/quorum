"""Flutter Audit Loop Script.

Automated Quality Gate for the Flutter client (`client_app_v2`).
Executes sequential code hygiene and validation stages:
1. `build_runner` (Optional): Runs the Dart code generator for SDUI/Freezed/JSON models.
2. `_dart_guardrails.py`: Enforces Dart static guardrails (DGR001-DGR004) with generated file immunity.
3. `dart format`: Formats Dart files to ensure consistent indentation and layout.
4. `dart analyze`: Statically analyzes source code to enforce architectural invariants.
5. `flutter test` (Optional): Executes Flutter unit tests with coverage reporting.

Usage:
    uv run python scripts/flutter_audit_loop.py <target_directory> [--build] [--test] [--strict]
"""

import io
import os
import subprocess
import sys
from pathlib import Path


def main() -> None:
    if isinstance(sys.stdout, io.TextIOWrapper):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError, io.UnsupportedOperation:
            pass
    if isinstance(sys.stderr, io.TextIOWrapper):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except AttributeError, io.UnsupportedOperation:
            pass

    if len(sys.argv) < 2:
        print("Usage: python flutter_audit_loop.py <target_directory> [--build] [--test] [--strict]")
        sys.exit(1)

    target_dir = sys.argv[1]
    run_build = "--build" in sys.argv
    run_test = "--test" in sys.argv
    run_strict = "--strict" in sys.argv

    # Ensure correct working directory (client_app_v2) and track repository root
    current_dir = Path(os.getcwd()).resolve()
    root_dir = current_dir if current_dir.name != "client_app_v2" else current_dir.parent
    if current_dir.name != "client_app_v2":
        client_app_dir = current_dir / "client_app_v2"
        if client_app_dir.exists():
            os.chdir(client_app_dir)
        else:
            print("Error: Script must be run from repository root or client_app_v2 directory.")
            sys.exit(1)

    print(f"\n🚀 Running quality loop for target: {target_dir}")
    print("--------------------------------------------------")

    cmd_dir = target_dir
    if cmd_dir.replace("\\", "/").startswith("client_app_v2/"):
        cmd_dir = cmd_dir[len("client_app_v2/") :]
    elif cmd_dir.strip("\\/") == "client_app_v2":
        cmd_dir = "."

    if not cmd_dir:
        cmd_dir = "."

    total_steps = 5 if run_test else 4

    if run_build:
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
    else:
        print(f"\n⏭️ 1/{total_steps}: Skipping code generation (no --build flag).")

    print(f"\n⏳ 2/{total_steps}: Checking Dart Codebase Guardrails (scripts/_dart_guardrails.py)...")
    dart_guardrails_script = root_dir / "scripts" / "_dart_guardrails.py"
    target_scan_dir = root_dir / "client_app_v2" / "lib"
    guardrail_cmd = [sys.executable, str(dart_guardrails_script), str(target_scan_dir)]
    if run_strict:
        guardrail_cmd.append("--strict")
    res_guardrail = subprocess.run(guardrail_cmd)
    if res_guardrail.returncode != 0:
        print("\n❌ AUDIT FAILED: Fatal Dart guardrail violations detected!")
        sys.exit(res_guardrail.returncode)
    print("✅ Dart Guardrails passed.")

    print(f"\n⏳ 3/{total_steps}: Formatting code (dart format {cmd_dir})...")
    res = subprocess.run(["dart", "format", cmd_dir], shell=True)
    if res.returncode != 0:
        print("❌ Formatting failed!")
        sys.exit(res.returncode)
    print("✅ Formatting complete.")

    print(f"\n⏳ 4/{total_steps}: Analyzing code (dart analyze {cmd_dir})...")
    res = subprocess.run(["dart", "analyze", cmd_dir], shell=True)
    if res.returncode != 0:
        print("\n❌ AUDIT FAILED: Analysis found errors in code. Fix them before proceeding!")
        print("🤖 AI INSTRUCTION: Read the above report and resolve static analysis errors.")
        print(
            "🚨 THE ANTI-TDD TRAP MANDATE: The architectural laws in `.agents/rules` are ABSOLUTE. Do NOT fall into the 'Test-Driven Development Trap' where you preserve legacy dict-parsing, fallback hacks, or hardcoded strings just to satisfy existing unit tests. If old tests conflict with the new rules (e.g., No-String Mandate, De-Generator, Pydantic V2), you MUST ruthlessly tear down the legacy code AND rewrite the tests. A green test suite that violates architectural sovereignty is a failed state.\n"
        )
        sys.exit(res.returncode)
    print("✅ Analysis complete.")

    if run_test:
        print(f"\n⏳ 5/{total_steps}: Running Flutter unit tests and coverage (flutter test --coverage)...")
        res_test = subprocess.run(["flutter", "test", "--coverage"], shell=True)
        if res_test.returncode != 0:
            print("\n❌ AUDIT FAILED: Flutter tests failed!")
            sys.exit(res_test.returncode)
        print("✅ Flutter tests passed.")

    print("\n🏆 All clean! Target conforms to architectural standards.\n")


if __name__ == "__main__":
    main()
