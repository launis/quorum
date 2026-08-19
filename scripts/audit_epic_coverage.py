"""Audit Epic Coverage.

A deterministic post-flight reverse audit script verifying physical codebase
implementation against Epic requirements via physical file existence and AST symbol absence.
"""

import argparse
import re
import sys
from pathlib import Path

# Add scripts directory to sys.path if not present
scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from _ast_boundary_utils import (  # noqa: E402
    extract_deprecated_symbols,
    extract_target_files,
    find_symbols_in_python_code,
)


def extract_phase_content(epic_text: str, phase_num: int | None) -> str:
    """Extract Markdown content for a specific phase or return full content if phase is None."""
    if phase_num is None:
        return epic_text

    phase_pattern = re.compile(
        rf"(?:##|###)\s+(?:Phase\s+{phase_num}[:\s]|.*Phase\s+{phase_num}\b)([\s\S]*?)(?=(?:##|###)\s+(?:Phase\s+\d+|[1-9]\.|\Z))",
        re.IGNORECASE,
    )
    match = phase_pattern.search(epic_text)
    if match:
        return match.group(0)
    return epic_text


def scan_for_lingering_symbols(workspace_root: Path, symbols: set[str]) -> list[tuple[str, str, int]]:
    """Scan backend Python files (AST) and frontend Dart files for lingering deprecated symbols."""
    findings: list[tuple[str, str, int]] = []
    if not symbols:
        return findings

    # Python AST scanning in backend_v2
    backend_dir = workspace_root / "backend_v2"
    if backend_dir.exists():
        for py_file in backend_dir.rglob("*.py"):
            try:
                code = py_file.read_text(encoding="utf-8")
                matches = find_symbols_in_python_code(code, symbols)
                for sym, lines in matches.items():
                    for match_lineno in lines:
                        rel_path = py_file.relative_to(workspace_root).as_posix()
                        findings.append((sym, rel_path, match_lineno))
            except SyntaxError, UnicodeDecodeError:
                continue

    # Dart text scanning in client_app_v2
    client_dir = workspace_root / "client_app_v2"
    if client_dir.exists():
        for dart_file in client_dir.rglob("*.dart"):
            try:
                content = dart_file.read_text(encoding="utf-8")
                for lineno, line_text in enumerate(content.splitlines(), start=1):
                    for sym in symbols:
                        if re.search(rf"\b{re.escape(sym)}\b", line_text):
                            rel_path = dart_file.relative_to(workspace_root).as_posix()
                            findings.append((sym, rel_path, lineno))
            except UnicodeDecodeError:
                continue

    return findings


def main() -> None:
    """Execute post-flight reverse audit against Epic requirements."""
    parser = argparse.ArgumentParser(description="Audit Epic coverage and symbol eradication.")
    parser.add_argument("--epic", required=True, type=str, help="Path to the source Epic .md file")
    parser.add_argument("--phase", required=False, type=int, default=None, help="Phase number to audit")
    parser.add_argument("--workspace-root", required=False, type=str, default=".", help="Workspace root")
    parser.add_argument("--output-report", required=False, type=str, default=None, help="Output report path")
    args = parser.parse_args()

    epic_path = Path(args.epic)
    workspace_root = Path(args.workspace_root).resolve()

    if not epic_path.exists():
        print(f"ERROR: Epic file not found: {epic_path}")
        sys.exit(1)

    epic_text = epic_path.read_text(encoding="utf-8")
    scoped_text = extract_phase_content(epic_text, args.phase)

    target_files = extract_target_files(scoped_text)
    deprecated_symbols = extract_deprecated_symbols(scoped_text)

    report_rows: list[tuple[str, str, str, str]] = []
    has_failure = False

    # 1. PHYSICAL FILE EXISTENCE VERIFICATION
    for action, rel_path, _ in target_files:
        full_path = workspace_root / rel_path
        exists = full_path.exists()

        if action == "NEW":
            status = "PASS" if exists else "FAIL"
            evidence = f"Exists at {rel_path}" if exists else f"Missing file {rel_path}"
        elif action == "DELETE":
            status = "PASS" if not exists else "FAIL"
            evidence = f"Deleted at {rel_path}" if not exists else f"File still exists at {rel_path}"
        else:  # MODIFY
            status = "PASS" if exists else "FAIL"
            evidence = f"Verified at {rel_path}" if exists else f"File not found at {rel_path}"

        if status == "FAIL":
            has_failure = True
        report_rows.append((f"[{action}] `{rel_path}`", "File", status, evidence))

    # 2. DEPRECATED SYMBOLS SCANNING
    lingering = scan_for_lingering_symbols(workspace_root, deprecated_symbols)
    if lingering:
        has_failure = True
        for sym, file_path, line in lingering:
            report_rows.append(
                (f"Eradicate `{sym}`", "Symbol", "FAIL", f"NOT ERADICATED: found in `{file_path}:{line}`")
            )
    elif deprecated_symbols:
        for sym in sorted(deprecated_symbols):
            report_rows.append((f"Eradicate `{sym}`", "Symbol", "PASS", "No lingering references found in codebase"))

    # Print markdown table
    phase_label = f"Phase {args.phase}" if args.phase else "All Phases"
    print(f"\n# Epic Coverage Audit Report: {epic_path.name} ({phase_label})\n")
    print("| Requirement | Category | Status | Evidence |")
    print("| :--- | :--- | :--- | :--- |")
    for req, cat, stat, evid in report_rows:
        print(f"| {req} | {cat} | **{stat}** | {evid} |")

    if args.output_report:
        out_p = Path(args.output_report)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        report_lines = [
            f"# Epic Coverage Audit Report: {epic_path.name} ({phase_label})\n",
            "| Requirement | Category | Status | Evidence |",
            "| :--- | :--- | :--- | :--- |",
        ]
        for req, cat, stat, evid in report_rows:
            report_lines.append(f"| {req} | {cat} | **{stat}** | {evid} |")
        out_p.write_text("\n".join(report_lines) + "\n", encoding="utf-8")
        print(f"\nAudit report saved to: {out_p.as_posix()}")

    if has_failure:
        print("\n[FAILED] AUDIT FAILED: Physical files or symbol eradications do not match Epic specifications.")
        sys.exit(1)
    else:
        print("\n[PASSED] AUDIT PASSED: All physical target files and symbol eradication requirements satisfied.")
        sys.exit(0)


if __name__ == "__main__":
    main()
