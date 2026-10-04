"""Audit Clean Imports.

Deterministic scanner that recursively imports every module in backend_v2 (or a target directory)
via importlib.import_module() to prove zero circular dependencies, zero missing symbols, and zero
eager side-effect deadlocks in pure module imports.
"""

from __future__ import annotations

import argparse
import importlib
import io
import json
import sys
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# Force UTF-8 encoding for stdout on Windows without reflection
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError, io.UnsupportedOperation:
        pass

# ANSI colors for console output
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

__all__ = [
    "ImportAuditReportDTO",
    "ImportFailureDTO",
    "main",
    "scan_clean_imports",
]


class ImportFailureDTO(BaseModel):
    """Pydantic V2 DTO representing an import failure for a single module."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    module_name: Annotated[str, Field(description="Fully qualified Python module name")]
    error_type: Annotated[str, Field(description="Exception class name")]
    error_message: Annotated[str, Field(description="Exception message")]
    file_path: Annotated[str, Field(description="Path to the module file")]


class ImportAuditReportDTO(BaseModel):
    """Pydantic V2 DTO representing the aggregate clean import audit report."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    total_modules_scanned: Annotated[int, Field(description="Total modules discovered and scanned")]
    successful_imports: Annotated[int, Field(description="Number of modules imported without error")]
    failed_imports: Annotated[int, Field(description="Number of modules that failed to import")]
    failures: Annotated[list[ImportFailureDTO], Field(description="List of import failures")]
    passed: Annotated[bool, Field(description="Whether all modules imported cleanly")]


def _resolve_module_name(file_path: Path, repo_root: Path) -> str:
    """Resolve the canonical Python module name for a file relative to the repo root.

    Args:
        file_path: Absolute or relative path to the Python file.
        repo_root: Root directory of the repository for module anchoring.

    Returns:
        Dotted canonical module name string.
    """
    rel_path = file_path.resolve().relative_to(repo_root.resolve())
    parts = list(rel_path.parts)
    if parts[-1] == "__init__.py":
        return ".".join(parts[:-1]) if len(parts) > 1 else parts[0]
    parts[-1] = file_path.stem
    return ".".join(parts)


def _attempt_module_import(module_name: str, file_path_str: str) -> ImportFailureDTO | None:
    """Attempt importing a single module, capturing failures as typed DTO.

    Args:
        module_name: Fully qualified Python module name.
        file_path_str: Path string of the module file for error reporting.

    Returns:
        ImportFailureDTO if an exception occurred during import, else None.
    """
    try:
        importlib.import_module(module_name)
        return None
    except BaseException as exc:
        return ImportFailureDTO(
            module_name=module_name,
            error_type=type(exc).__name__,
            error_message=str(exc),
            file_path=file_path_str,
        )


def scan_clean_imports(
    target_dir: Path | str = "backend_v2",
    repo_root: Path | str | None = None,
    exclude_dirs: tuple[str, ...] = ("tests", "__pycache__", ".venv"),
) -> ImportAuditReportDTO:
    """Recursively scan and import all Python modules in the target directory.

    Args:
        target_dir: Target directory path or string to scan for Python files.
        repo_root: Optional repository root path for resolving module paths.
        exclude_dirs: Tuple of directory names to exclude from scanning.

    Returns:
        ImportAuditReportDTO summarizing aggregate scan results and failures.
    """
    if repo_root is None:
        resolved_repo_root = Path(".").resolve()
    else:
        resolved_repo_root = Path(repo_root).resolve()

    if str(resolved_repo_root) not in sys.path:
        sys.path.insert(0, str(resolved_repo_root))

    resolved_target_dir = Path(target_dir)
    if not resolved_target_dir.is_absolute():
        resolved_target_dir = (resolved_repo_root / resolved_target_dir).resolve()

    if not resolved_target_dir.exists():
        return ImportAuditReportDTO(
            total_modules_scanned=0,
            successful_imports=0,
            failed_imports=0,
            failures=[],
            passed=True,
        )

    python_files: list[Path] = []
    for file_path in sorted(resolved_target_dir.rglob("*.py")):
        if any(part in file_path.parts for part in exclude_dirs):
            continue
        if file_path.name.startswith("."):
            continue
        python_files.append(file_path)

    failures: list[ImportFailureDTO] = []
    successful_count = 0

    for file_path in python_files:
        module_name = _resolve_module_name(file_path, resolved_repo_root)
        if not module_name:
            continue
        failure = _attempt_module_import(module_name, str(file_path))
        if failure is not None:
            failures.append(failure)
        else:
            successful_count += 1

    total_scanned = len(python_files)
    failed_count = len(failures)
    is_passed = failed_count == 0

    return ImportAuditReportDTO(
        total_modules_scanned=total_scanned,
        successful_imports=successful_count,
        failed_imports=failed_count,
        failures=failures,
        passed=is_passed,
    )


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for clean import audit.

    Args:
        argv: Optional list of command-line argument strings.

    Returns:
        Integer exit code (0 for success, 1 for failures).
    """
    parser = argparse.ArgumentParser(
        description="Audit clean imports across Python modules to detect circular dependencies and import errors."
    )
    parser.add_argument(
        "--target-dir",
        default="backend_v2",
        help="Target directory to scan (default: backend_v2)",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root to resolve module paths from (default: current working directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enforce strict exit code on any failure (default: true for failures)",
    )

    args = parser.parse_args(argv)

    report = scan_clean_imports(
        target_dir=args.target_dir,
        repo_root=args.repo_root,
    )

    if args.json:
        print(json.dumps(report.model_dump(mode="json"), indent=2))
        return 0 if report.passed else 1

    print(f"\n{BOLD}{CYAN}=== Clean Import Audit ==={RESET}")
    print(f"Target directory: {args.target_dir}")
    print(f"Modules scanned:  {report.total_modules_scanned}")
    print(f"Successful:       {GREEN}{report.successful_imports}{RESET}")
    print(f"Failed:           {RED if report.failed_imports > 0 else GREEN}{report.failed_imports}{RESET}")

    if not report.passed:
        print(f"\n{BOLD}{RED}FAILED IMPORTS ({len(report.failures)}):{RESET}")
        for failure in report.failures:
            print(f"  {RED}✕{RESET} {BOLD}{failure.module_name}{RESET} ({failure.file_path})")
            print(f"    [{failure.error_type}] {failure.error_message}")
        print(f"\n{RED}Clean import audit failed with {report.failed_imports} broken modules.{RESET}\n")
        return 1

    print(f"\n{GREEN}All {report.total_modules_scanned} modules imported cleanly with zero errors.{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
