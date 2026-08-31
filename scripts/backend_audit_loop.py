"""Backend Audit Loop Script (Antigravity Quality Gate)

**What this script does:**
This script is the Automated Quality Gate for the Python backend. It runs a multi-stage pipeline:
1. `ruff check --fix`: Detects formatting and lint issues and fixes them automatically where possible.
2. `ruff format`: Formats code to strict standard compliance.
3. `mypy --strict`: Performs strict type checking according to the Universal Quality Gate.
4. AST Guardrail Validation (`_ast_guardrails.py`): Enforces structural domain rules and fault isolation.
5. UI Template Validation: Verifies that Jinja2 templates remain strictly passive (Dumb Painter).
6. Seed Data Validation: Runs a dry-run of the database seeder to ensure SSOT schema integrity.
Additionally, the script can update OpenAPI specifications (--openapi) and run unit tests with strict 90% TDD coverage (--test).

**Usage Instructions:**
Execute this script from the workspace root using `uv run python`:

```bash
uv run python scripts/backend_audit_loop.py <target_folder_or_file> [--ast-strict] [--openapi] [--test]
```

**Examples:**

1. Check and format a single file:
```bash
uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring.py
```

2. Check with strict AST guardrails:
```bash
uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py --ast-strict
```

3. Check an entire folder and execute tests with coverage:
```bash
uv run python scripts/backend_audit_loop.py backend_v2/ --test
```
"""

import io
import os
import re
import subprocess
import sys
from pathlib import Path

# Ensure workspace root is in sys.path for direct script execution
_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

from scripts._ast_guardrails import (
    GuardrailSeverity,
    format_violations_table,
    scan_files_for_guardrails,
)

# Force pure Python Protobuf implementation to prevent duplicate descriptor pool crashes in Python 3.14+
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Force UTF-8 encoding for stdout to support emojis on Windows without reflection
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError, io.UnsupportedOperation:
        pass


def run_tests_with_strict_coverage(target: str) -> None:
    print("🚀 Verifying Strict 90% TDD Coverage...")

    target_clean = target.replace("\\", "/")

    if target_clean.endswith(".py"):
        parts = target_clean.split("/")
        filename = parts[-1]

        if filename.startswith("test_") or "tests" in parts:
            test_path = target_clean
            clean_name = filename.replace("test_", "", 1).removesuffix(".py")
            if "scripts" in parts:
                if (Path("scripts") / f"_{clean_name}.py").exists():
                    cov_target = f"scripts._{clean_name}"
                    cov_filter_name = f"_{clean_name}.py"
                elif (Path("scripts") / f"{clean_name}.py").exists():
                    cov_target = f"scripts.{clean_name}"
                    cov_filter_name = f"{clean_name}.py"
                else:
                    cov_target = f"scripts.{clean_name}"
                    cov_filter_name = f"{clean_name}.py"
            elif parts[0] == "backend_v2" and "unit" in parts:
                unit_idx = parts.index("unit")
                rel_parts = parts[unit_idx + 1 : -1] + [clean_name]
                cov_target = "backend_v2." + ".".join(rel_parts)
                cov_filter_name = f"{clean_name}.py"
            else:
                cov_target = target_clean.removesuffix(".py").replace("/", ".")
                cov_filter_name = filename
        else:
            if target_clean.endswith("/__init__.py"):
                cov_target = target_clean.removesuffix("/__init__.py").replace("/", ".")
                pkg_name = parts[-2] if len(parts) >= 2 else "init"
                clean_base = filename.removesuffix(".py").lstrip("_")
                candidates = [
                    f"test_{pkg_name}.py",
                    f"test__{pkg_name}.py",
                    f"test_{clean_base}.py",
                    f"test_{filename}",
                ]
            else:
                cov_target = target_clean.removesuffix(".py").replace("/", ".")
                clean_base = filename.removesuffix(".py").lstrip("_")
                candidates = [f"test_{clean_base}.py", f"test__{clean_base}.py", f"test_{filename}"]
            cov_filter_name = filename

            test_path = ""
            if parts[0] == "scripts":
                for cand in candidates:
                    cand_path = Path("backend_v2/tests/unit/scripts") / cand
                    if cand_path.exists():
                        test_path = str(cand_path).replace("\\", "/")
                        break
            elif parts[0] == "backend_v2":
                for cand in candidates:
                    # 1. Direct subfolder match
                    p = Path("backend_v2/tests/unit") / "/".join(parts[1:-1]) / cand
                    if p.exists():
                        test_path = str(p).replace("\\", "/")
                        break
                    # 2. Parent package test file (e.g. backend_v2/hooks/scoring/passivity_hook.py -> test_scoring.py or test_hooks.py)
                    for i in range(len(parts) - 2, 0, -1):
                        parent_pkg = parts[i]
                        parent_cand = Path("backend_v2/tests/unit") / "/".join(parts[1:i]) / f"test_{parent_pkg}.py"
                        if parent_cand.exists():
                            test_path = str(parent_cand).replace("\\", "/")
                            break
                    if test_path:
                        break
                    # 3. Flat unit test match
                    flat = Path("backend_v2/tests/unit") / cand
                    if flat.exists():
                        test_path = str(flat).replace("\\", "/")
                        break

            if not test_path:
                test_path = "backend_v2/tests/unit/" + "/".join(parts[1:-1]) + "/" + candidates[0]

        # 1. Run Pytest and collect coverage data (no fail-under crash yet)
        cmd = [
            "uv",
            "run",
            "python",
            "-c",
            f"import os, sys\ntry: import numpy, pandas\nexcept ImportError: pass\ntry: import backend_v2.tests.conftest\nexcept ImportError: pass\nimport pytest\nsys.exit(pytest.main(['{test_path}', '-v', '--tb=short', '--cov={cov_target}', '--cov-fail-under=0']))",
        ]
        print("Executing:", " ".join(cmd))
        result = subprocess.run(cmd)

        # 2. Run Coverage Report filtered strictly to this target file
        if result.returncode == 0:
            coverage_cmd = ["uv", "run", "coverage", "report", f"--include=*{cov_filter_name}", "--fail-under=90", "-m"]
            result = subprocess.run(coverage_cmd)
    else:
        parts = target_clean.strip("/").split("/")
        cov_target = target_clean.replace("/", ".").strip(".")
        if "tests" in parts:
            test_path = target_clean
        else:
            if parts[0] == "backend_v2":
                test_dir = Path("backend_v2/tests/unit") / "/".join(parts[1:])
                test_file = Path("backend_v2/tests/unit") / "/".join(parts[1:-1]) / f"test_{parts[-1]}.py"
                if test_dir.exists():
                    test_path = str(test_dir).replace("\\", "/")
                elif test_file.exists():
                    test_path = str(test_file).replace("\\", "/")
                else:
                    test_path = "backend_v2/tests/unit/" + "/".join(parts[1:])
            else:
                if parts == ["."]:
                    test_path = "backend_v2/tests/"
                else:
                    test_path = "tests/" + "/".join(parts)

        test_paths_list = test_path.split()
        args = test_paths_list + [
            "-v",
            "--tb=short",
            f"--cov={cov_target}",
            "--cov-fail-under=90",
            "--cov-report=term-missing",
        ]

        cmd = [
            "uv",
            "run",
            "python",
            "-c",
            f"import os, sys\nos.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'\ntry: import numpy\nexcept ImportError: pass\nimport pytest\nsys.exit(pytest.main({args}))",
        ]
        result = subprocess.run(cmd)

    if result.returncode != 0:
        print("\n❌ AUDIT FAILED: Tests had errors OR test coverage is under 90%.")
        print(
            "🤖 AI INSTRUCTION: Read the report above and fix either failing tests (-v or --tb=short explains the cause) OR add tests for missing lines (Miss column)."
        )
        print(
            "🚨 THE ANTI-TDD TRAP MANDATE: The architectural laws in `.agents/rules/` are ABSOLUTE. Do NOT fall into the 'Test-Driven Development Trap' where you preserve legacy dict-parsing, fallback hacks, or hardcoded strings just to satisfy existing unit tests. If old tests conflict with the new rules (e.g., No-String Mandate, De-Generator, Pydantic V2), you MUST ruthlessly tear down the legacy code AND rewrite the tests. A green test suite that violates architectural sovereignty is a failed state."
        )
        sys.exit(result.returncode)
    else:
        print("\n✅ Strict 90% Coverage Target Met.")


def main() -> None:
    targets: list[str] = []
    run_openapi = False
    run_test = False
    ast_strict = False

    for arg in sys.argv[1:]:
        if arg == "--openapi":
            run_openapi = True
        elif arg == "--test":
            run_test = True
        elif arg in ("--ast-strict", "--strict"):
            ast_strict = True
        else:
            targets.append(arg)

    if not targets:
        print("Usage: python backend_audit_loop.py <target_folder_or_files...> [--ast-strict] [--openapi] [--test]")
        sys.exit(1)

    # Ensure we are in the project root directory
    current_dir = Path(os.getcwd())
    if current_dir.name == "scripts":
        os.chdir("..")
    elif not (current_dir / "backend_v2").exists():
        print("Error: Script must be executed from the project root (where backend_v2 is located).")
        sys.exit(1)

    targets_str = ", ".join(targets)
    print(f"\n🚀 Executing quality-loop for targets: {targets_str}")
    print("--------------------------------------------------")

    print("\n⏳ 1/6: Checking and fixing files (ruff check --fix)...")
    res = subprocess.run(["uv", "run", "ruff", "check", *targets, "--fix", "--extend-ignore=E501"])
    if res.returncode != 0:
        print("❌ Ruff linter found unfixable errors!")
        sys.exit(res.returncode)
    print("✅ Linting and auto-fix complete.")

    print("\n⏳ 2/6: Formatting code (ruff format)...")
    res = subprocess.run(["uv", "run", "ruff", "format", *targets])
    if res.returncode != 0:
        print("❌ Ruff formatting failed!")
        sys.exit(res.returncode)
    print("✅ Formatting complete.")

    print("\n⏳ 3/6: Type checking code (mypy --strict)...")
    res = subprocess.run(["uv", "run", "mypy", *targets, "--strict"])
    if res.returncode != 0:
        print("\n❌ MyPy found type errors! Resolve Universal Quality Gate violations.\n")
        sys.exit(res.returncode)
    print("✅ Type check passed.")

    print("\n⏳ 4/6: Checking AST Codebase Guardrails (scripts/_ast_guardrails.py)...")
    violations, is_success = scan_files_for_guardrails(targets, strict=ast_strict)
    unsuppressed = [v for v in violations if not v.is_suppressed]
    fatal_violations = [v for v in unsuppressed if v.severity == GuardrailSeverity.FATAL]

    if ast_strict and unsuppressed:
        print("\n❌ AST Guardrail check failed in strict mode!")
        print(format_violations_table(unsuppressed))
        sys.exit(1)
    elif fatal_violations:
        print("\n❌ Fatal AST Guardrail violations detected!")
        print(format_violations_table(fatal_violations))
        sys.exit(1)
    elif unsuppressed:
        print("\n⚠️  Advisory AST Guardrail warnings detected:")
        print(format_violations_table(unsuppressed))
    else:
        print("✅ AST Guardrails passed cleanly.")

    print("\n⏳ 5/6: Validating UI templates (Jinja Dumb Painter Enforcement)...")
    jinja_dir = Path("backend_v2/templates")
    dumb_painter_pattern = re.compile(r"\|\s*(default|d)\s*\(|\.get\s*\(")
    if jinja_dir.exists():
        for jinja_file in jinja_dir.rglob("*.jinja2"):
            try:
                content = jinja_file.read_text(encoding="utf-8")
                if dumb_painter_pattern.search(content):
                    print(f"\n❌ UI template validation failed in {jinja_file.name}!")
                    print("   Found forbidden dumb-painter expression: `| default` or `.get`.")
                    print("   UI templates must be completely passive (Strict ICU Markdown Parity).")
                    sys.exit(1)
            except (OSError, UnicodeDecodeError) as e:
                print(f"\n❌ Error reading template {jinja_file}: {e}")
                sys.exit(1)
    print("✅ UI templates validated.")

    print("\n⏳ 6/6: Validating Seed Data (Dry-Run & Strict Atom Audit)...")
    res = subprocess.run(["uv", "run", "python", "backend_v2/seed/run_seed.py", "local", "--dry-run"])
    if res.returncode != 0:
        print("\n❌ Seed Data Dry-Run failed! Pydantic model changes broke the SSOT JSON seed file.\n")
        sys.exit(res.returncode)

    res_audit = subprocess.run(["uv", "run", "python", "scripts/audit_database_atoms.py", "--strict"])
    if res_audit.returncode != 0:
        print("\n❌ Database Atom & Prompt Audit failed! Structural or referential errors in seed_data.json.\n")
        sys.exit(res_audit.returncode)
    print("✅ Seed Data and Database Atoms integrated and validated.")

    if run_openapi:
        print("\n⏳ Option: Generating OpenAPI documentation (--openapi)...")
        res = subprocess.run(["uv", "run", "python", "backend_v2/scripts/generate_openapi.py"])
        if res.returncode != 0:
            print("❌ OpenAPI generation failed! Check Pydantic models.")
            sys.exit(res.returncode)
        print("✅ OpenAPI documentation successfully updated.")

    if run_test:
        print("\n⏳ Option: Running Pytest unit tests and coverage (--test)...")
        for target in targets:
            print(f"\n🏃 Running tests for target: {target}")
            run_tests_with_strict_coverage(target)
        print("✅ Unit tests passed.")

    print("\n🏆 All clean! Targets comply with Universal Quality Gate standards.\n")


if __name__ == "__main__":
    main()
