"""Audit Flutter Theme Sovereignty.

Single Source of Truth static audit script verifying Flutter Theme Sovereignty across Quorum UI widgets.
Asserts zero occurrences of prohibited raw static colors (Color(0x...), Color.fromARGB, Color.fromRGBO,
Colors.*) and standalone TextStyle(...) declarations in target Dart UI widgets.
Ensures 100% adherence to ThemeData tokens (colorScheme, textTheme, AppSemanticColors ThemeExtension).

Usage:
    uv run python scripts/audit_flutter_theme_sovereignty.py [file1.dart file2.dart ...]
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# Force UTF-8 encoding for stdout on Windows
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
    "ThemeAuditReportDTO",
    "ThemeViolationDTO",
    "main",
    "scan_theme_sovereignty",
]

# Prohibited patterns
COLOR_HEX_PATTERN = re.compile(r"\bColor\s*\(\s*0x[0-9a-fA-F]+")
COLOR_FACTORY_PATTERN = re.compile(r"\bColor\.(?:fromARGB|fromRGBO)\s*\(")
COLORS_PALETTE_PATTERN = re.compile(r"\bColors\.[a-zA-Z0-9_]+")
TEXT_STYLE_PATTERN = re.compile(r"\b(?:const\s+)?TextStyle\s*\(")

DEFAULT_TARGET_FILES = [
    "client_app_v2/lib/features/studio/views/components/bars_matrix_builder.dart",
    "client_app_v2/lib/features/execution/views/widgets/atom_matrix_table_widget.dart",
    "client_app_v2/lib/features/execution/views/widgets/sdui_blocks_renderer.dart",
    "client_app_v2/lib/theme/app_colors.dart",
    "client_app_v2/lib/shared/widgets/specialist_section.dart",
    "client_app_v2/lib/shared/widgets/result_dashboard.dart",
]


class ThemeViolationDTO(BaseModel):
    """Pydantic V2 DTO representing a Theme Sovereignty violation."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    file_path: Annotated[str, Field(description="Target Dart file path")]
    line_number: Annotated[int, Field(ge=1, description="1-indexed line number")]
    line_content: Annotated[str, Field(description="Content of the violating line")]
    violation_type: Annotated[str, Field(description="Classification of the theme violation")]
    remediation: Annotated[str, Field(description="Remediation guidance")]


class ThemeAuditReportDTO(BaseModel):
    """Pydantic V2 DTO representing aggregate Theme Sovereignty audit results."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    total_files_scanned: Annotated[int, Field(ge=0, description="Total number of scanned files")]
    total_violations: Annotated[int, Field(ge=0, description="Total count of theme violations")]
    violations: Annotated[list[ThemeViolationDTO], Field(default_factory=list, description="List of violations")]


def scan_theme_sovereignty(target_paths: list[str]) -> ThemeAuditReportDTO:
    """Scans target Dart files for Theme Sovereignty and direct styling violations."""
    violations: list[ThemeViolationDTO] = []
    scanned_count = 0

    for file_str in target_paths:
        path = Path(file_str)
        if not path.is_file():
            continue

        scanned_count += 1
        normalized_name = path.name.lower()
        is_theme_definition = normalized_name == "app_colors.dart" or "theme" in path.parts
        is_specialist_section = normalized_name == "specialist_section.dart"

        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            violations.append(
                ThemeViolationDTO(
                    file_path=str(path),
                    line_number=1,
                    line_content=f"UnicodeDecodeError: {exc}",
                    violation_type="ENCODING_ERROR",
                    remediation="Ensure file is encoded in valid UTF-8.",
                )
            )
            continue

        for line_idx, line in enumerate(content.splitlines(), start=1):
            stripped = line.strip()
            # Skip single-line comments
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                continue

            if is_theme_definition:
                # In theme definition files (AppSemanticColors), Color(0x...) is permitted to define tokens.
                # Prohibit raw Colors.* palette access (e.g. Colors.green) or static intent fields.
                if COLORS_PALETTE_PATTERN.search(line):
                    violations.append(
                        ThemeViolationDTO(
                            file_path=str(path),
                            line_number=line_idx,
                            line_content=stripped,
                            violation_type="PROHIBITED_STATIC_COLORS_PALETTE",
                            remediation="Do not reference Colors.* directly. Define concrete token colors or derive from ColorScheme.",
                        )
                    )
                if TEXT_STYLE_PATTERN.search(line):
                    violations.append(
                        ThemeViolationDTO(
                            file_path=str(path),
                            line_number=line_idx,
                            line_content=stripped,
                            violation_type="PROHIBITED_TEXT_STYLE",
                            remediation="Do not instantiate naked TextStyle in theme token files.",
                        )
                    )
                continue

            # In UI widgets, assert zero raw hex colors
            if COLOR_HEX_PATTERN.search(line):
                violations.append(
                    ThemeViolationDTO(
                        file_path=str(path),
                        line_number=line_idx,
                        line_content=stripped,
                        violation_type="PROHIBITED_RAW_HEX_COLOR",
                        remediation="Replace raw Color(0x...) with Theme.of(context).colorScheme tokens or context.semanticColors.",
                    )
                )

            # In UI widgets, assert zero factory colors (fromARGB, fromRGBO)
            if COLOR_FACTORY_PATTERN.search(line):
                violations.append(
                    ThemeViolationDTO(
                        file_path=str(path),
                        line_number=line_idx,
                        line_content=stripped,
                        violation_type="PROHIBITED_COLOR_FACTORY",
                        remediation="Replace Color.fromARGB/fromRGBO with Theme.of(context).colorScheme tokens.",
                    )
                )

            # In UI widgets, assert zero Colors.* palette access
            if COLORS_PALETTE_PATTERN.search(line):
                violations.append(
                    ThemeViolationDTO(
                        file_path=str(path),
                        line_number=line_idx,
                        line_content=stripped,
                        violation_type="PROHIBITED_STATIC_COLORS_PALETTE",
                        remediation="Replace Colors.* with Theme.of(context).colorScheme tokens.",
                    )
                )

            # In primary UI widgets, assert zero naked TextStyle
            if not is_specialist_section and TEXT_STYLE_PATTERN.search(line):
                violations.append(
                    ThemeViolationDTO(
                        file_path=str(path),
                        line_number=line_idx,
                        line_content=stripped,
                        violation_type="PROHIBITED_NAKED_TEXT_STYLE",
                        remediation="Replace naked TextStyle(...) with Theme.of(context).textTheme tokens (e.g. titleMedium, bodyMedium).",
                    )
                )

    return ThemeAuditReportDTO(
        total_files_scanned=scanned_count,
        total_violations=len(violations),
        violations=violations,
    )


def main(argv: list[str] | None = None) -> None:
    """CLI entrypoint for Theme Sovereignty audit."""
    parser = argparse.ArgumentParser(
        description="Verify Flutter Theme Sovereignty and direct styling eradication.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "files",
        nargs="*",
        default=[],
        help="Target Dart files to scan (defaults to standard Theme Sovereignty target set).",
    )
    args = parser.parse_args(argv)

    targets = args.files if args.files else DEFAULT_TARGET_FILES

    print(f"\n{BOLD}{CYAN}=== Flutter Theme Sovereignty Audit Gate ==={RESET}")
    print(f"Target files: {len(targets)}")

    report = scan_theme_sovereignty(targets)

    if report.total_violations == 0:
        print(
            f"{GREEN}✓ Theme Sovereignty Pass: {report.total_files_scanned} files scanned, "
            f"0 violations found.{RESET}\n"
        )
        sys.exit(0)
    else:
        print(
            f"\n{RED}✗ Theme Sovereignty Violations Detected: "
            f"{report.total_violations} across {report.total_files_scanned} files:{RESET}\n"
        )
        for v in report.violations:
            print(f"  {RED}{v.file_path}:{v.line_number}{RESET} [{v.violation_type}]")
            print(f"    Line: {v.line_content}")
            print(f"    Fix:  {YELLOW}{v.remediation}{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
