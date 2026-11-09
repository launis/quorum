"""Backend Audit Loop Script (Antigravity Quality Gate).

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

```powershell
uv run python scripts/backend_audit_loop.py <target_folder_or_file> [--permissive-warn] [--openapi] [--test]
```

**Examples:**

1. Check and format a single file (executes strict AST guardrails by default):
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/hooks/scoring.py
```

2. Check in advisory mode for emergency diagnostics:
```powershell
uv run python scripts/backend_audit_loop.py scripts/backend_audit_loop.py --permissive-warn
```

3. Check an entire folder and execute tests with coverage:
```powershell
uv run python scripts/backend_audit_loop.py backend_v2/ --test
```
"""

from __future__ import annotations

import argparse
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

__all__ = [
    "_MACRO_AUTHORITATIVE_SCRIPTS",
    "discover_authoritative_scripts",
    "discover_companion_test_targets",
    "find_transitional_strangler_proxy_files",
    "main",
    "run_audit_loop",
    "run_tests_with_strict_coverage",
]


def discover_authoritative_scripts(scripts_dir: Path = Path("scripts")) -> tuple[str, ...]:
    """Dynamically discover all authoritative Python scripts in the scripts directory.

    Args:
        scripts_dir: Directory containing operational and guardrail Python scripts.

    Returns:
        Sorted tuple of workspace-relative POSIX script paths.

    Raises:
        OSError: If the scripts directory cannot be accessed during glob traversal.
    """
    return tuple(sorted(p.as_posix() for p in scripts_dir.glob("*.py") if p.is_file()))


_MACRO_AUTHORITATIVE_SCRIPTS: tuple[str, ...] = discover_authoritative_scripts()


# Force pure Python Protobuf implementation to prevent duplicate descriptor pool crashes in Python 3.14+
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

# Force UTF-8 encoding for stdout to support emojis on Windows without reflection
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError, io.UnsupportedOperation:
        pass


def find_transitional_strangler_proxy_files(targets: list[str]) -> list[str]:
    """Discover in-flight Strangler Fig proxy files coexisting with same-stem subdirectories.

    When MyPy scans a parent folder (specifically: backend_v2/), its file crawler skips any foo.py
    if a directory named foo/ exists in the same folder. Adding foo.py explicitly ensures
    MyPy loads the proxy module symbols during multi-phase strangler fig migrations.

    Args:
        targets: List of target file or directory paths.

    Returns:
        List of transitional proxy file paths discovered.

    Raises:
        OSError: If directory traversal fails on the filesystem.
    """
    discovered: list[str] = []
    for target in targets:
        t_path = Path(target)
        if t_path.is_dir():
            for child_dir in sorted(t_path.rglob("*")):
                if child_dir.is_dir():
                    sibling_file = child_dir.with_suffix(".py")
                    if sibling_file.is_file():
                        sibling_str = sibling_file.as_posix()
                        if sibling_str not in targets and sibling_str not in discovered:
                            discovered.append(sibling_str)
    return discovered


def _build_py_file_test_candidates(parts: list[str], filename: str) -> list[str]:
    """Build ordered candidate unit test filenames for a Python source file.

    Args:
        parts: Path components split by '/'.
        filename: Base filename with .py extension.

    Returns:
        Ordered list of candidate test filenames.
    """
    if len(parts) >= 2 and filename == "__init__.py":
        pkg_name = parts[-2]
        clean_base = filename.removesuffix(".py").lstrip("_")
        return [
            f"test_{pkg_name}.py",
            f"test_{pkg_name}_facade.py",
            f"test_{pkg_name}_init.py",
            "test_facade.py",
            f"test__{pkg_name}.py",
            f"test_{clean_base}.py",
            f"test_{filename}",
        ]
    clean_base = filename.removesuffix(".py").lstrip("_")
    candidates = [
        f"test_{clean_base}.py",
        f"test_{clean_base}_dtos.py",
        f"test__{clean_base}.py",
        f"test_{filename}",
    ]
    if clean_base.startswith("audit_"):
        candidates.append(f"test_{clean_base.removeprefix('audit_')}.py")
    if clean_base.startswith("test_"):
        candidates.append(f"{clean_base}.py")
    return candidates


def _resolve_probe_path(rel_path: Path, repo_root: Path | None) -> Path:
    """Resolve a workspace-relative probe path against an optional repository root.

    Args:
        rel_path: Relative path to probe.
        repo_root: Optional repository root directory.

    Returns:
        Resolved Path instance for existence and globbing checks.
    """
    return (repo_root / rel_path) if repo_root is not None else rel_path


def _append_unique_posix_path(paths: list[str], rel_path: Path) -> None:
    """Append a normalized POSIX path string to paths if not already present.

    Args:
        paths: Mutable list of POSIX path strings.
        rel_path: Relative path to normalize and append.
    """
    path_str = str(rel_path).replace("\\", "/")
    if path_str not in paths:
        paths.append(path_str)


def _append_with_sibling_tests(
    test_paths: list[str],
    rel_cand: Path,
    cand_path: Path,
    sib_glob_prefix: str,
) -> None:
    """Append a matched test file and any sibling split test files to test_paths.

    Args:
        test_paths: Accumulator list of discovered test paths.
        rel_cand: Workspace-relative path of the matched candidate test file.
        cand_path: Filesystem path of the matched candidate test file.
        sib_glob_prefix: Prefix stem used to glob sibling test_<prefix>_*.py files.

    Raises:
        OSError: If directory globbing fails on the filesystem.
    """
    _append_unique_posix_path(test_paths, rel_cand)
    for sib in sorted(cand_path.parent.glob(f"test_{sib_glob_prefix}_*.py")):
        _append_unique_posix_path(test_paths, rel_cand.parent / sib.name)


def _probe_parent_package_test_paths(
    parts: list[str],
    cand: str,
    sib_glob_prefix: str,
    repo_root: Path | None,
) -> list[str]:
    """Probe parent package directories for matching candidate or package test files.

    Args:
        parts: Path components of the target Python file.
        cand: Candidate test filename.
        sib_glob_prefix: Prefix stem used to glob sibling test files.
        repo_root: Optional repository root directory.

    Returns:
        List of matched parent package test file paths, or empty list if none exist.

    Raises:
        OSError: If directory globbing fails on the filesystem.
    """
    test_paths: list[str] = []
    for i in range(len(parts) - 2, 0, -1):
        rel_parent_cand = Path("backend_v2/tests/unit") / "/".join(parts[1:i]) / cand
        parent_cand = _resolve_probe_path(rel_parent_cand, repo_root)
        if parent_cand.exists():
            _append_with_sibling_tests(test_paths, rel_parent_cand, parent_cand, sib_glob_prefix)
            return test_paths
    for i in range(len(parts) - 2, 0, -1):
        parent_pkg = parts[i]
        rel_parent_pkg_cand = Path("backend_v2/tests/unit") / "/".join(parts[1:i]) / f"test_{parent_pkg}.py"
        parent_cand = _resolve_probe_path(rel_parent_pkg_cand, repo_root)
        if parent_cand.exists():
            _append_unique_posix_path(test_paths, rel_parent_pkg_cand)
            return test_paths
    return test_paths


def _probe_backend_candidate_test_paths(
    parts: list[str],
    cand: str,
    sib_glob_prefix: str,
    repo_root: Path | None,
) -> list[str]:
    """Probe backend_v2/tests/unit hierarchy for a single candidate test filename.

    Args:
        parts: Path components of the target Python file.
        cand: Candidate test filename.
        sib_glob_prefix: Prefix stem used to glob sibling test files.
        repo_root: Optional repository root directory.

    Returns:
        List of matched test file paths for the candidate, or empty list if none exist.

    Raises:
        OSError: If directory globbing fails on the filesystem.
    """
    test_paths: list[str] = []
    rel_p = Path("backend_v2/tests/unit") / "/".join(parts[1:-1]) / cand
    p = _resolve_probe_path(rel_p, repo_root)
    if p.exists():
        _append_with_sibling_tests(test_paths, rel_p, p, sib_glob_prefix)
        return test_paths

    parent_matches = _probe_parent_package_test_paths(parts, cand, sib_glob_prefix, repo_root)
    if parent_matches:
        return parent_matches

    rel_flat = Path("backend_v2/tests/unit") / cand
    if _resolve_probe_path(rel_flat, repo_root).exists():
        _append_unique_posix_path(test_paths, rel_flat)
        return test_paths

    rel_pkg_prefix_cand = Path("backend_v2/tests/unit") / f"test_{'_'.join(parts[1:-1])}_{cand[5:]}"
    if _resolve_probe_path(rel_pkg_prefix_cand, repo_root).exists():
        _append_unique_posix_path(test_paths, rel_pkg_prefix_cand)
    return test_paths


def _discover_existing_py_test_paths(
    parts: list[str],
    filename: str,
    candidates: list[str],
    repo_root: Path | None = None,
) -> list[str]:
    """Resolve existing unit test file paths on disk for a Python source file.

    Args:
        parts: Path components split by '/'.
        filename: Base filename with .py extension.
        candidates: Ordered candidate test filenames to probe.
        repo_root: Optional repository root directory to resolve probes against.

    Returns:
        List of existing test file paths in POSIX format.

    Raises:
        OSError: If directory globbing fails on the filesystem.
    """
    clean_base = filename.removesuffix(".py").lstrip("_")
    sib_glob_prefix = parts[-2] if (len(parts) >= 2 and filename == "__init__.py") else clean_base
    test_paths: list[str] = []
    if parts[0] == "scripts":
        for cand in candidates:
            rel_cand = Path("backend_v2/tests/unit/scripts") / cand
            cand_path = _resolve_probe_path(rel_cand, repo_root)
            if cand_path.exists():
                _append_with_sibling_tests(test_paths, rel_cand, cand_path, sib_glob_prefix)
                break
    elif parts[0] == "backend_v2":
        for cand in candidates:
            matched = _probe_backend_candidate_test_paths(parts, cand, sib_glob_prefix, repo_root)
            if matched:
                return matched
    return test_paths


def _append_submodule_dir_tests(
    discovered_tests: list[str],
    target_dir: Path,
    parent_test_dir: Path,
    rel_parent_test_dir: Path,
    flat_unit: Path,
    rel_flat_unit: Path,
) -> None:
    """Append unit test files matching individual .py modules inside a target directory.

    Args:
        discovered_tests: Accumulator list of discovered test paths.
        target_dir: Filesystem path to the target package directory.
        parent_test_dir: Filesystem path to the parent unit test directory.
        rel_parent_test_dir: Workspace-relative path to the parent unit test directory.
        flat_unit: Filesystem path to backend_v2/tests/unit.
        rel_flat_unit: Workspace-relative path to backend_v2/tests/unit.

    Raises:
        OSError: If directory traversal fails on the filesystem.
    """
    if not target_dir.is_dir():
        return
    for sub_py in sorted(target_dir.glob("*.py")):
        if sub_py.name == "__init__.py":
            continue
        stem = sub_py.stem
        if (parent_test_dir / f"test_{stem}.py").exists():
            _append_unique_posix_path(discovered_tests, rel_parent_test_dir / f"test_{stem}.py")
        if (flat_unit / f"test_{stem}.py").exists():
            _append_unique_posix_path(discovered_tests, rel_flat_unit / f"test_{stem}.py")


def _discover_existing_dir_test_paths(
    target_clean: str,
    parts: list[str],
    repo_root: Path | None = None,
) -> list[str]:
    """Discover existing unit test directories or files for a backend_v2 directory target.

    Args:
        target_clean: Normalized POSIX path to a backend_v2 directory.
        parts: Path components split by '/'.
        repo_root: Optional repository root directory to resolve probes against.

    Returns:
        List of existing test directory or file paths in POSIX format.

    Raises:
        OSError: If directory traversal fails on the filesystem.
    """
    target_stem = Path(target_clean).stem
    rel_target_dir = Path(target_clean.strip("/"))
    target_dir = _resolve_probe_path(rel_target_dir, repo_root)
    rel_test_dir = Path("backend_v2/tests/unit") / "/".join(parts[1:])
    test_dir = _resolve_probe_path(rel_test_dir, repo_root)
    rel_test_file = Path("backend_v2/tests/unit") / "/".join(parts[1:-1]) / f"test_{target_stem}.py"
    test_file = _resolve_probe_path(rel_test_file, repo_root)
    has_test_dir = test_dir.exists()
    if has_test_dir and len(parts) <= 2:
        return [str(rel_test_dir).replace("\\", "/")]
    if test_file.exists() and not has_test_dir:
        return [str(rel_test_file).replace("\\", "/")]

    discovered_tests: list[str] = []
    if has_test_dir:
        _append_unique_posix_path(discovered_tests, rel_test_dir)
    rel_parent_test_dir = Path("backend_v2/tests/unit") / "/".join(parts[1:-1])
    parent_test_dir = _resolve_probe_path(rel_parent_test_dir, repo_root)
    if parent_test_dir.exists():
        for m in sorted(parent_test_dir.glob(f"test_{target_stem}*.py")):
            _append_unique_posix_path(discovered_tests, rel_parent_test_dir / m.name)

    rel_flat_unit = Path("backend_v2/tests/unit")
    flat_unit = _resolve_probe_path(rel_flat_unit, repo_root)
    rel_flat_pkg_test = rel_flat_unit / f"test_{target_stem}.py"
    if _resolve_probe_path(rel_flat_pkg_test, repo_root).exists():
        _append_unique_posix_path(discovered_tests, rel_flat_pkg_test)

    _append_submodule_dir_tests(
        discovered_tests, target_dir, parent_test_dir, rel_parent_test_dir, flat_unit, rel_flat_unit
    )
    return discovered_tests


def _discover_companion_for_single_target(
    target_clean: str,
    repo_root: Path | None,
) -> list[str]:
    """Discover companion test paths for a single file or directory target.

    Args:
        target_clean: Forward-slash normalized target path.
        repo_root: Optional repository root directory.

    Returns:
        List of discovered companion test paths for the target.

    Raises:
        OSError: If directory globbing fails on the filesystem.
    """
    if target_clean.endswith(".py"):
        parts = target_clean.split("/")
        filename = parts[-1]
        if "tests" in parts:
            rel_sibling_test = Path("/".join(parts[:-1])) / f"test_{filename}"
            sibling_test = _resolve_probe_path(rel_sibling_test, repo_root)
            if not filename.startswith("test_") and sibling_test.exists():
                return [str(rel_sibling_test).replace("\\", "/")]
            return []
        candidates = _build_py_file_test_candidates(parts, filename)
        return _discover_existing_py_test_paths(parts, filename, candidates, repo_root=repo_root)

    parts = target_clean.strip("/").split("/")
    if "tests" in parts or parts == ["backend_v2"]:
        return []
    if parts[0] == "scripts":
        rel_scripts_test_dir = Path("backend_v2/tests/unit/scripts")
        if _resolve_probe_path(rel_scripts_test_dir, repo_root).exists():
            return [str(rel_scripts_test_dir).replace("\\", "/")]
        return []
    if parts[0] == "backend_v2":
        return _discover_existing_dir_test_paths(target_clean, parts, repo_root=repo_root)
    return []


def discover_companion_test_targets(
    targets: list[str],
    repo_root: Path | None = None,
) -> list[str]:
    """Discover existing companion unit test files or directories for target paths.

    Used when --test is enabled so that Stage 1 (ruff check --fix) and Stage 2
    (ruff format) automatically lint and format the companion test files alongside
    the target source files.

    Args:
        targets: Target file or directory paths passed to the audit loop.
        repo_root: Optional repository root directory to resolve probes against.

    Returns:
        Deduplicated list of existing companion test paths not already in targets.

    Raises:
        OSError: If directory globbing fails on the filesystem.
    """
    discovered: list[str] = []
    normalized_inputs = {t.replace("\\", "/").rstrip("/") for t in targets}

    for target in targets:
        target_clean = target.replace("\\", "/")
        for cand_str in _discover_companion_for_single_target(target_clean, repo_root):
            if cand_str not in normalized_inputs and cand_str not in discovered:
                discovered.append(cand_str)

    return discovered


def _resolve_globbed_unit_cov_target(sub_parts: list[str], clean_name: str) -> str:
    """Resolve coverage module path by globbing backend_v2 and scripts for a unit test stem.

    Args:
        sub_parts: Subdirectory components between 'unit' and the test filename.
        clean_name: Source module stem stripped of 'test_' prefix and '.py' suffix.

    Returns:
        Dotted Python module path for coverage instrumentation.

    Raises:
        OSError: If filesystem globbing fails.
    """
    prefix = "/".join(sub_parts) + "/" if sub_parts else ""
    found = list(Path("backend_v2").glob(f"{prefix}**/{clean_name}.py"))
    if not found and not sub_parts:
        found = list(Path("scripts").glob(f"**/{clean_name}.py"))
    if not found:
        found = list(Path("backend_v2").glob(f"**/{clean_name}.py"))
    if not found:
        return "backend_v2"
    if found[0].is_relative_to(Path("backend_v2")):
        rel_found = found[0].relative_to("backend_v2")
        return "backend_v2." + str(rel_found).removesuffix(".py").replace("\\", ".").replace("/", ".")
    return str(found[0]).removesuffix(".py").replace("\\", ".").replace("/", ".")


def _resolve_test_file_cov_target(target_clean: str, parts: list[str], filename: str) -> str:
    """Resolve the coverage module target string when the audit target is inside tests/.

    Args:
        target_clean: Normalized POSIX path of the test file target.
        parts: Path components split by '/'.
        filename: Base filename with .py extension.

    Returns:
        Dotted Python module path for coverage instrumentation.

    Raises:
        OSError: If filesystem existence or glob checks fail.
    """
    sibling_test = Path("/".join(parts[:-1])) / f"test_{filename}"
    if not filename.startswith("test_") and sibling_test.exists():
        return target_clean.removesuffix(".py").replace("/", ".")

    clean_name = filename.replace("test_", "", 1).removesuffix(".py")
    sibling_src = Path("/".join(parts[:-1])) / f"{clean_name}.py"
    if "scripts" in parts:
        if (Path("scripts") / f"_{clean_name}.py").exists():
            return f"scripts._{clean_name}"
        if (Path("scripts") / f"{clean_name}.py").exists():
            return f"scripts.{clean_name}"
        return target_clean.removesuffix(".py").replace("/", ".")
    if filename.startswith("test_") and sibling_src.exists():
        return str(sibling_src).removesuffix(".py").replace("\\", ".").replace("/", ".")
    if parts[0] == "backend_v2" and "unit" in parts:
        unit_idx = parts.index("unit")
        rel_parts = parts[unit_idx + 1 : -1] + [clean_name]
        expected_src = Path("backend_v2") / ("/".join(rel_parts) + ".py")
        if expected_src.exists():
            return "backend_v2." + ".".join(rel_parts)
        return _resolve_globbed_unit_cov_target(parts[unit_idx + 1 : -1], clean_name)
    return target_clean.removesuffix(".py").replace("/", ".")


def _resolve_test_file_cov_filter(parts: list[str], filename: str, cov_target: str) -> str:
    """Resolve the coverage report filename filter when the audit target is inside tests/.

    Args:
        parts: Path components split by '/'.
        filename: Base filename with .py extension.
        cov_target: Resolved dotted module target string.

    Returns:
        Filename filter string (or empty string if coverage applies to all of backend_v2).

    Raises:
        OSError: If filesystem existence checks fail.
    """
    sibling_test = Path("/".join(parts[:-1])) / f"test_{filename}"
    if not filename.startswith("test_") and sibling_test.exists():
        return filename

    clean_name = filename.replace("test_", "", 1).removesuffix(".py")
    sibling_src = Path("/".join(parts[:-1])) / f"{clean_name}.py"
    if "scripts" in parts:
        if (Path("scripts") / f"_{clean_name}.py").exists():
            return f"_{clean_name}.py"
        if (Path("scripts") / f"{clean_name}.py").exists():
            return f"{clean_name}.py"
        return filename
    if filename.startswith("test_") and sibling_src.exists():
        return f"{clean_name}.py"
    if parts[0] == "backend_v2" and "unit" in parts:
        return "" if cov_target == "backend_v2" else f"{clean_name}.py"
    return filename


def _resolve_py_file_test_paths(target_clean: str, parts: list[str], filename: str) -> list[str]:
    """Resolve pytest execution file paths for a single .py target file.

    Args:
        target_clean: Normalized POSIX path of the .py target.
        parts: Path components split by '/'.
        filename: Base filename with .py extension.

    Returns:
        Non-empty list of test file paths to pass to pytest.

    Raises:
        OSError: If filesystem existence or glob checks fail.
    """
    if "tests" in parts:
        sibling_test = Path("/".join(parts[:-1])) / f"test_{filename}"
        if not filename.startswith("test_") and sibling_test.exists():
            return [str(sibling_test).replace("\\", "/")]
        return [target_clean]

    candidates = _build_py_file_test_candidates(parts, filename)
    test_paths = _discover_existing_py_test_paths(parts, filename, candidates)
    if test_paths:
        return test_paths
    if parts[0] == "scripts":
        return ["backend_v2/tests/unit/scripts/" + candidates[0]]
    return ["backend_v2/tests/unit/" + "/".join(parts[1:-1]) + "/" + candidates[0]]


def _resolve_py_file_cov_target(target_clean: str, parts: list[str], filename: str) -> str:
    """Resolve the dotted coverage module string for any single .py target file.

    Args:
        target_clean: Normalized POSIX path of the .py target.
        parts: Path components split by '/'.
        filename: Base filename with .py extension.

    Returns:
        Dotted Python module path for coverage instrumentation.

    Raises:
        OSError: If filesystem existence or glob checks fail.
    """
    if "tests" in parts:
        return _resolve_test_file_cov_target(target_clean, parts, filename)
    if target_clean.endswith("/__init__.py"):
        return target_clean.removesuffix("/__init__.py").replace("/", ".")
    return target_clean.removesuffix(".py").replace("/", ".")


def _resolve_py_file_cov_filter(parts: list[str], filename: str, cov_target: str) -> str:
    """Resolve the coverage report filename filter for any single .py target file.

    Args:
        parts: Path components split by '/'.
        filename: Base filename with .py extension.
        cov_target: Resolved dotted module target string.

    Returns:
        Filename filter string (or empty string if coverage applies to all of backend_v2).

    Raises:
        OSError: If filesystem existence checks fail.
    """
    if "tests" in parts:
        return _resolve_test_file_cov_filter(parts, filename, cov_target)
    return filename


def _resolve_directory_test_path(target_clean: str, parts: list[str]) -> str:
    """Resolve space-separated pytest target path string for a directory target.

    Args:
        target_clean: Normalized POSIX directory target path.
        parts: Path components split by '/'.

    Returns:
        Space-separated test directory or file paths to execute.

    Raises:
        OSError: If directory test discovery fails on the filesystem.
    """
    if "tests" in parts:
        return target_clean
    if parts[0] == "backend_v2":
        discovered_tests = _discover_existing_dir_test_paths(target_clean, parts)
        if discovered_tests:
            return " ".join(discovered_tests)
        return "backend_v2/tests/unit/" + "/".join(parts[1:])
    if parts[0] == "scripts":
        return "backend_v2/tests/unit/scripts"
    if parts[0] == "tests":
        return "backend_v2/tests/" + "/".join(parts[1:])
    if parts == ["."]:
        return "backend_v2/tests/"
    return "backend_v2/tests/" + "/".join(parts)


def _run_pytest_subprocess(
    pytest_args: list[str], logfire: bool, print_cmd: bool
) -> subprocess.CompletedProcess[bytes]:
    """Execute pytest in a subprocess with pure-Python protobuf pre-initialization.

    Args:
        pytest_args: Arguments list to pass into pytest.main(...).
        logfire: Whether to append --logfire tracing flags.
        print_cmd: Whether to print the constructed command before execution.

    Returns:
        CompletedProcess result from subprocess.run.
    """
    full_args = list(pytest_args)
    if logfire:
        full_args.extend(["--logfire", "--logfire-service-name=quorum-audit-loop"])
    cmd = [
        "uv",
        "run",
        "python",
        "-c",
        f"import os, sys\nos.environ['PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION'] = 'python'\ntry: import numpy, pydantic.root_model\nexcept ImportError: pass\nimport pytest\nsys.exit(pytest.main({full_args}))",
    ]
    if print_cmd:
        print("Executing:", " ".join(cmd))
    return subprocess.run(cmd)


def run_tests_with_strict_coverage(target: str, logfire: bool = False) -> None:
    """Execute pytest unit tests and enforce strict 90% TDD line coverage.

    Resolves matching unit test files corresponding to target source files or directories,
    invokes pytest with coverage instrumentation, and verifies line coverage meets or exceeds
    the required 90% threshold.

    When targeting a package facade (__init__.py), candidate test discovery checks:
    1. test_{pkg_name}.py
    2. test_{pkg_name}_facade.py
    3. test_facade.py
    When auditing a package directory (specifically: backend_v2/services/auth/ --test),
    the aggregate package test suite is automatically discovered and executed.

    Args:
        target: File path or directory path to test with coverage.
        logfire: When True, enables Logfire distributed tracing plugin in Pytest.
            Defaults to False.

    Raises:
        SystemExit: If test execution fails or line coverage falls below 90%.
    """
    print("🚀 Verifying Strict 90% TDD Coverage...")

    target_clean = target.replace("\\", "/")

    if target_clean.endswith(".py"):
        parts = target_clean.split("/")
        filename = parts[-1]
        test_paths = _resolve_py_file_test_paths(target_clean, parts, filename)
        cov_target = _resolve_py_file_cov_target(target_clean, parts, filename)
        cov_filter_name = _resolve_py_file_cov_filter(parts, filename, cov_target)

        pytest_args = [*test_paths, "-v", "--tb=short", f"--cov={cov_target}", "--cov-fail-under=0"]
        result = _run_pytest_subprocess(pytest_args, logfire=logfire, print_cmd=True)

        if result.returncode == 0:
            if cov_filter_name:
                coverage_cmd = [
                    "uv",
                    "run",
                    "coverage",
                    "report",
                    f"--include=*{cov_filter_name}",
                    "--fail-under=90",
                    "-m",
                ]
            else:
                coverage_cmd = ["uv", "run", "coverage", "report", "--fail-under=0", "-m"]
            result = subprocess.run(coverage_cmd)
    else:
        parts = target_clean.strip("/").split("/")
        cov_target = target_clean.removesuffix(".py").replace("/", ".").strip(".")
        test_path = _resolve_directory_test_path(target_clean, parts)
        args = [
            *test_path.split(),
            "-v",
            "--tb=short",
            f"--cov={cov_target}",
            "--cov-fail-under=90",
            "--cov-report=term-missing",
        ]
        result = _run_pytest_subprocess(args, logfire=logfire, print_cmd=False)

    if result.returncode != 0:
        print("\n❌ AUDIT FAILED: Tests had errors OR test coverage is under 90%.")
        print(
            "🔍 DIAGNOSTIC TRACE: Inspect data/files/traces/latest_execution_trace.json using `view_file` or use Logfire MCP tools (`query_spans`, `get_trace`) to identify root error spans and failing assertions."
        )
        print(
            "🤖 AI INSTRUCTION: Read the report above and fix either failing tests (-v or --tb=short explains the cause) OR add tests for missing lines (Miss column)."
        )
        print(
            "🚨 THE ANTI-TDD TRAP MANDATE: The architectural laws in `.agents/rules/` are ABSOLUTE. Do NOT fall into the 'Test-Driven Development Trap' where you preserve legacy dict-parsing, fallback hacks, or hardcoded strings just to satisfy existing unit tests. If old tests conflict with the new rules (specifically: No-String Mandate, De-Generator, Pydantic V2), you MUST ruthlessly tear down the legacy code AND rewrite the tests. A green test suite that violates architectural sovereignty is a failed state."
        )
        sys.exit(result.returncode)
    else:
        print("\n✅ Strict 90% Coverage Target Met.")


def _build_cli_parser() -> argparse.ArgumentParser:
    """Construct the CLI ArgumentParser for backend_audit_loop.py.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        description="""Sequential backend quality gate pipeline.

Executes a validation sequence to guarantee architectural invariants:
  1/10: Code hygiene and auto-formatting (ruff check --fix --extend-ignore=E501)
  2/10: Code style formatting (ruff format)
  3/10: Strict type checking (mypy --strict)
  4/10: AST codebase guardrails (scripts/_ast_guardrails.py)
  5/10: Jinja Dumb Painter template validation (backend_v2/templates/)
  6/10: Seed data dry-run and database atom integrity audit
  7/10: Clean import verification (scripts/audit_clean_imports.py)
  8/10: DTO parity verification (scripts/audit_dto_parity.py)
  9/10: Warning and Residual Debt Baseline Ledger (scripts/audit_warning_baseline.py)
  10/10: Dict eradication and typed domain transit verification (scripts/audit_dict_eradication.py)

Optional steps:
  --openapi: Generates updated OpenAPI documentation (backend_v2/scripts/generate_openapi.py)
  --test: Runs Pytest unit tests with strict line coverage (>90%)
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples (PowerShell):
  uv run python scripts/backend_audit_loop.py backend_v2/services/execution.py
  uv run python scripts/backend_audit_loop.py backend_v2/services/execution.py --test
  uv run python scripts/backend_audit_loop.py backend_v2/services/auth/ --test
  uv run python scripts/backend_audit_loop.py backend_v2/models/dtos/ --strict
  uv run python scripts/backend_audit_loop.py backend_v2/ --openapi
""",
    )
    parser.add_argument(
        "targets",
        nargs="*",
        default=[],
        help=(
            "Target files or directories to validate sequentially through the pipeline. "
            "Passing a package directory (specifically: backend_v2/services/auth/ --test) "
            "runs the aggregate package test suite."
        ),
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Execute Pytest unit tests with strict line coverage enforcement on target files.",
    )
    parser.add_argument(
        "--openapi",
        action="store_true",
        help="Trigger OpenAPI documentation generation and schema validation.",
    )
    parser.add_argument(
        "--ast-strict",
        "--strict",
        dest="ast_strict",
        action="store_true",
        default=True,
        help="Enforce strict AST Guardrail validation (default: enabled; fail on warnings as well as fatal errors).",
    )
    parser.add_argument(
        "--permissive-warn",
        dest="ast_strict",
        action="store_false",
        help="Enable advisory AST mode for emergency diagnostics only (warn on advisory violations, fail on fatal).",
    )
    parser.add_argument(
        "--micro",
        "--fast",
        dest="micro",
        action="store_true",
        default=False,
        help="Execute fast targeted audit loop for single-file iterations (Stages 1-4 + unit tests), deferring whole-repository scans (Stages 5-10) to the macro completion gate.",
    )
    parser.add_argument(
        "--logfire",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Enable/disable Logfire distributed tracing in Pytest runs (default: disabled; use --logfire to enable).",
    )
    return parser


def _ensure_project_root_working_dir() -> None:
    """Verify or switch the process working directory to the repository root.

    Raises:
        SystemExit: If executed outside the repository root and scripts directory.
    """
    current_dir = Path(os.getcwd())
    if current_dir.name == "scripts":
        os.chdir("..")
    elif not (current_dir / "backend_v2").exists():
        print("Error: Script must be executed from the project root (where backend_v2 is located).")
        sys.exit(1)


def _resolve_mypy_targets(stage_targets: list[str]) -> list[str]:
    """Resolve MyPy targets by mapping excluded backend_v2/tests/ directories to source packages.

    MyPy directory arguments honor pyproject.toml exclusions (^backend_v2/tests/) and exit
    with 'no .py[i] files in directory', whereas explicit .py files are type-checked directly.

    Args:
        stage_targets: Expanded stage targets.

    Returns:
        List of targets safe for MyPy --strict execution.
    """
    mypy_targets: list[str] = []
    for target in stage_targets:
        norm = target.replace("\\", "/").rstrip("/")
        if norm.startswith("backend_v2/tests") and not norm.endswith(".py"):
            parts = norm.split("/")
            mapped = "backend_v2"
            if len(parts) > 3 and parts[2] == "unit":
                candidate = "backend_v2/" + "/".join(parts[3:])
                if Path(candidate).exists():
                    mapped = candidate
            if mapped not in mypy_targets:
                mypy_targets.append(mapped)
        elif target not in mypy_targets:
            mypy_targets.append(target)
    return mypy_targets


def _resolve_stage_targets(targets: list[str], micro: bool) -> list[str]:
    """Expand stage targets with authoritative scripts and transitional proxy files.

    Args:
        targets: Raw CLI target paths.
        micro: Whether micro-audit mode is enabled.

    Returns:
        Expanded list of stage targets.

    Raises:
        OSError: If directory traversal fails on the filesystem.
    """
    is_macro_backend_gate = not micro and any(t.replace("\\", "/").rstrip("/") == "backend_v2" for t in targets)
    stage_targets: list[str] = [
        t for t in targets if not (is_macro_backend_gate and t.replace("\\", "/").rstrip("/") == "scripts")
    ]
    if is_macro_backend_gate:
        for script_path in discover_authoritative_scripts():
            if script_path not in stage_targets:
                stage_targets.append(script_path)

    for proxy_path in find_transitional_strangler_proxy_files(stage_targets):
        if proxy_path not in stage_targets:
            stage_targets.append(proxy_path)
    return stage_targets


def _resolve_ruff_targets(stage_targets: list[str], run_test: bool) -> list[str]:
    """Expand stage targets with companion unit test paths when --test is enabled.

    Args:
        stage_targets: Expanded stage targets.
        run_test: Whether unit test execution is enabled.

    Returns:
        List of targets for Ruff lint and format stages.

    Raises:
        OSError: If companion test discovery fails on the filesystem.
    """
    ruff_targets: list[str] = list(stage_targets)
    if run_test:
        for companion_test in discover_companion_test_targets(stage_targets):
            if companion_test not in ruff_targets:
                ruff_targets.append(companion_test)
    return ruff_targets


def _run_checked_stage(cmd: list[str], failure_message: str) -> None:
    """Run a subprocess stage command and exit with its return code on failure.

    Args:
        cmd: Subprocess command list to execute.
        failure_message: Error banner printed before exiting on non-zero returncode.

    Raises:
        SystemExit: If the subprocess exits with a non-zero status code.
    """
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print(failure_message)
        sys.exit(res.returncode)


def _run_lint_format_and_type_stages(stage_targets: list[str], ruff_targets: list[str]) -> None:
    """Execute Stages 1/10 (Ruff lint), 2/10 (Ruff format), and 3/10 (MyPy strict).

    Args:
        stage_targets: Target paths for MyPy strict type checking.
        ruff_targets: Target paths for Ruff linting and formatting.

    Raises:
        SystemExit: If Ruff or MyPy returns a non-zero exit code.
    """
    print("\n⏳ 1/10: Checking and fixing files (ruff check --fix)...")
    _run_checked_stage(
        ["uv", "run", "ruff", "check", *ruff_targets, "--fix", "--extend-ignore=E501"],
        "❌ Ruff linter found unfixable errors!",
    )
    print("✅ Linting and auto-fix complete.")

    print("\n⏳ 2/10: Formatting code (ruff format)...")
    _run_checked_stage(
        ["uv", "run", "ruff", "format", *ruff_targets],
        "❌ Ruff formatting failed!",
    )
    print("✅ Formatting complete.")

    print("\n⏳ 3/10: Type checking code (mypy --strict)...")
    mypy_targets = _resolve_mypy_targets(stage_targets)
    _run_checked_stage(
        ["uv", "run", "mypy", *mypy_targets, "--strict"],
        "\n❌ MyPy found type errors! Resolve Universal Quality Gate violations.\n",
    )
    print("✅ Type check passed.")


def _run_ast_guardrail_stage(stage_targets: list[str], ast_strict: bool) -> None:
    """Execute Stage 4/10 (AST Codebase Guardrails).

    Args:
        stage_targets: Target paths to scan for AST guardrail violations.
        ast_strict: Whether advisory warnings also fail the gate.

    Raises:
        SystemExit: If fatal violations (or any violations in strict mode) are detected.
    """
    print("\n⏳ 4/10: Checking AST Codebase Guardrails (scripts/_ast_guardrails.py)...")
    violations, _ = scan_files_for_guardrails(stage_targets, strict=ast_strict)
    fatal_violations = [v for v in violations if v.severity == GuardrailSeverity.FATAL]

    if ast_strict and violations:
        print("\n❌ AST Guardrail check failed in strict mode!")
        print(format_violations_table(violations))
        sys.exit(1)
    elif fatal_violations:
        print("\n❌ Fatal AST Guardrail violations detected!")
        print(format_violations_table(fatal_violations))
        sys.exit(1)
    elif violations:
        print("\n⚠️  Advisory AST Guardrail warnings detected:")
        print(format_violations_table(violations))
    else:
        print("✅ AST Guardrails passed cleanly.")


def _validate_jinja_templates() -> None:
    """Execute Stage 5/10 (Jinja Dumb Painter template validation).

    Raises:
        SystemExit: If any Jinja2 template contains forbidden fallback expressions or cannot be read.
    """
    print("\n⏳ 5/10: Validating UI templates (Jinja Dumb Painter Enforcement)...")
    jinja_dir = Path("backend_v2/templates")
    dumb_painter_pattern = re.compile(r"\|\s*(default|d)\s*\(|\.get\s*\(|\bor\s+(''|\"\"|\[\]|\{\})")
    if jinja_dir.exists():
        for jinja_file in jinja_dir.rglob("*.jinja2"):
            try:
                content = jinja_file.read_text(encoding="utf-8")
                if dumb_painter_pattern.search(content):
                    print(f"\n❌ UI template validation failed in {jinja_file.name}!")
                    print("   Found forbidden dumb-painter expression: `| default`, `.get`, or fallback `or ''/[]/{}`.")
                    print("   UI templates must be completely passive (Strict ICU Markdown Parity).")
                    sys.exit(1)
            except (OSError, UnicodeDecodeError) as e:
                print(f"\n❌ Error reading template {jinja_file}: {e}")
                sys.exit(1)
    print("✅ UI templates validated.")


def _run_macro_repository_stages() -> None:
    """Execute whole-repository Stages 5/10 through 10/10 in Macro Mode.

    Raises:
        SystemExit: If any repository-wide validation stage fails.
    """
    _validate_jinja_templates()

    print("\n⏳ 6/10: Validating Seed Data (Dry-Run & Strict Atom Audit)...")
    _run_checked_stage(
        ["uv", "run", "python", "backend_v2/seed/run_seed.py", "local", "--dry-run"],
        "\n❌ Seed Data Dry-Run failed! Pydantic model changes broke the SSOT JSON seed file.\n",
    )
    _run_checked_stage(
        ["uv", "run", "python", "scripts/audit_database_atoms.py", "--strict"],
        "\n❌ Database Atom & Prompt Audit failed! Structural or referential errors in seed_data.json.\n",
    )
    print("✅ Seed Data and Database Atoms integrated and validated.")

    print("\n⏳ 7/10: Verifying Clean Imports (scripts/audit_clean_imports.py)...")
    _run_checked_stage(
        ["uv", "run", "python", "scripts/audit_clean_imports.py"],
        "\n❌ Clean import audit failed in backend_v2! Circular dependencies or import errors detected.\n",
    )
    _run_checked_stage(
        ["uv", "run", "python", "scripts/audit_clean_imports.py", "--target-dir", "scripts"],
        "\n❌ Clean import audit failed in scripts! Circular dependencies or import errors detected.\n",
    )
    print("✅ Clean imports verified.")

    print("\n⏳ 8/10: Verifying DTO Parity (scripts/audit_dto_parity.py --fail-on-mismatch)...")
    _run_checked_stage(
        ["uv", "run", "python", "scripts/audit_dto_parity.py", "--fail-on-mismatch"],
        "\n❌ DTO Parity Audit failed! Discrepancies between backend Pydantic models and frontend Freezed models.\n",
    )
    print("✅ DTO Parity verified.")

    print("\n⏳ 9/10: Verifying Warning & Residual Debt Baseline Ledger (scripts/audit_warning_baseline.py)...")
    _run_checked_stage(
        ["uv", "run", "python", "scripts/audit_warning_baseline.py", "--verify-zero"],
        "\n❌ Warning baseline or residual debt ceiling exceeded! See ledger report above.\n",
    )
    print("✅ Residual debt ceilings and warning baseline verified.")

    print("\n⏳ 10/10: Verifying Dict Eradication and Typed Domain Transit (scripts/audit_dict_eradication.py)...")
    _run_checked_stage(
        ["uv", "run", "python", "scripts/audit_dict_eradication.py", "backend_v2", "scripts", "--strict"],
        "\n❌ Dict eradication audit failed! Eliminate naked dicts/casts.\n",
    )
    _run_checked_stage(
        ["uv", "run", "python", "scripts/audit_zero_orm_strictness.py"],
        "\n❌ Zero-ORM strictness audit failed! Resolve ZORM001-ZORM006 violations.\n",
    )
    _run_checked_stage(
        ["uv", "run", "python", "scripts/audit_skills_architecture.py"],
        "\n❌ Skills architecture & rule budget audit failed! Resolve SKL001-SKL004 violations.\n",
    )
    print("✅ Dict eradication, Zero-ORM, and Skills architecture verified.")


def _run_micro_audit_stages(stage_targets: list[str]) -> None:
    """Execute target-scoped Dict Eradication and Technical Debt gates in Micro Mode.

    Args:
        stage_targets: Target files or directories to audit in micro mode.

    Raises:
        SystemExit: If target-scoped dict eradication or technical debt checks fail.
    """
    print("\n⚡ Micro-audit mode active (--micro): Running target-scoped Dict Eradication & Technical Debt gates...")
    _run_checked_stage(
        ["uv", "run", "python", "scripts/audit_dict_eradication.py", *stage_targets, "--strict"],
        "\n❌ Micro-mode Dict eradication audit failed! Eliminate naked dicts/casts in target files.\n",
    )
    _run_checked_stage(
        ["uv", "run", "python", "scripts/audit_technical_debt.py", "--targets", *stage_targets, "--strict"],
        "\n❌ Micro-mode Technical Debt audit failed! Resolve technical debt in target files.\n",
    )
    print("✅ Micro-mode Dict Eradication and Technical Debt verified (skipping repository-wide Stages 5-10).")


def run_audit_loop(args: argparse.Namespace) -> None:
    """Execute the configured backend quality gate stages for parsed CLI arguments.

    Args:
        args: Parsed CLI namespace containing targets, micro, test, openapi, ast_strict, and logfire flags.

    Raises:
        SystemExit: If working directory validation or any quality gate stage fails.
    """
    targets: list[str] = args.targets
    run_openapi: bool = bool(args.openapi)
    run_test: bool = bool(args.test)
    ast_strict: bool = bool(args.ast_strict)
    use_logfire: bool = bool(args.logfire)

    _ensure_project_root_working_dir()
    stage_targets = _resolve_stage_targets(targets, micro=bool(args.micro))
    ruff_targets = _resolve_ruff_targets(stage_targets, run_test=run_test)

    targets_str = ", ".join(stage_targets)
    print(f"\n🚀 Executing quality-loop for targets: {targets_str}")
    print("--------------------------------------------------")

    _run_lint_format_and_type_stages(stage_targets, ruff_targets)
    _run_ast_guardrail_stage(stage_targets, ast_strict=ast_strict)

    if not args.micro:
        _run_macro_repository_stages()
    else:
        _run_micro_audit_stages(stage_targets)

    if run_openapi:
        print("\n⏳ Option: Generating OpenAPI documentation (--openapi)...")
        _run_checked_stage(
            ["uv", "run", "python", "backend_v2/scripts/generate_openapi.py"],
            "❌ OpenAPI generation failed! Check Pydantic models.",
        )
        print("✅ OpenAPI documentation successfully updated.")

    if run_test:
        print("\n⏳ Option: Running Pytest unit tests and coverage (--test)...")
        for target in targets:
            print(f"\n🏃 Running tests for target: {target}")
            run_tests_with_strict_coverage(target, logfire=use_logfire)
        print("✅ Unit tests passed.")

    print("\n🏆 All clean! Targets comply with Universal Quality Gate standards.\n")


def main(argv: list[str] | None = None) -> None:
    """Execute the sequential backend quality gate pipeline.

    Parses command line arguments and runs the validation sequence:
    Ruff lint, Ruff format, MyPy strict type checking, AST guardrail validation,
    Jinja template validation, Seed dry-run verification, Clean imports verification,
    DTO parity verification, and Warning & Residual Debt baseline verification.

    Args:
        argv: Optional list of CLI argument strings to parse. Defaults to None.

    Raises:
        SystemExit: If CLI arguments are invalid or any quality gate stage fails.
    """
    parser = _build_cli_parser()
    args = parser.parse_args(argv)

    if not args.targets:
        print(
            "Usage: python backend_audit_loop.py <target_folder_or_files...> [--permissive-warn] [--openapi] [--test]"
        )
        sys.exit(1)

    run_audit_loop(args)


if __name__ == "__main__":
    main()
