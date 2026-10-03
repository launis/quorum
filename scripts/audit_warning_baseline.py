"""Warning Baseline Ledger and Quality Gate Verification Engine.

Single Source of Truth for tracking AST advisory warning baselines across backend_v2,
asserting mathematical zero FATAL violations, and enforcing monotonic warning reduction.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Annotated

# Ensure workspace root is in sys.path for direct script execution
_workspace_root = str(Path(__file__).resolve().parent.parent)
if _workspace_root not in sys.path:
    sys.path.insert(0, _workspace_root)

# Force UTF-8 encoding for stdout/stderr on Windows
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")
if isinstance(sys.stderr, io.TextIOWrapper):
    sys.stderr.reconfigure(encoding="utf-8")

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from scripts._ast_guardrails import GuardrailSeverity, scan_files_for_guardrails

CURRENT_WARNING_CEILING = 934


class RuleWarningStatDTO(V2CoreBase):
    """Warning statistics for a specific AST guardrail rule."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    rule_code: Annotated[str, Field(description="Guardrail rule identifier, e.g., QGR001.")]
    count: Annotated[int, Field(ge=0, description="Number of active warnings for this rule.")]


class BaselineLedgerReportDTO(V2CoreBase):
    """Comprehensive report produced by the warning baseline ledger."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    target_directory: Annotated[str, Field(description="Target directory evaluated.")]
    fatal_count: Annotated[int, Field(ge=0, description="Total unsuppressed fatal violations.")]
    warning_count: Annotated[int, Field(ge=0, description="Total unsuppressed advisory warnings.")]
    warning_ceiling: Annotated[int, Field(ge=0, description="Configured maximum permissible warnings.")]
    rule_breakdown: Annotated[list[RuleWarningStatDTO], Field(description="Per-rule warning breakdown.")]
    is_clean_of_fatals: Annotated[bool, Field(description="True if fatal count is strictly 0.")]
    is_under_ceiling: Annotated[bool, Field(description="True if warning count <= warning ceiling.")]


def generate_baseline_report(
    target: str = "backend_v2",
    ceiling: int = CURRENT_WARNING_CEILING,
    verify_zero: bool = False,
) -> BaselineLedgerReportDTO:
    """Scans target directory and compiles a typed baseline ledger report.

    Args:
        target: Target directory or file to scan.
        ceiling: Maximum allowable warning count.
        verify_zero: If True, requires warning count to be strictly 0.

    Returns:
        BaselineLedgerReportDTO containing audit results and compliance flags.
    """
    violations, _ = scan_files_for_guardrails([target], strict=False)
    unsuppressed = [v for v in violations if not v.is_suppressed]

    fatals = [v for v in unsuppressed if v.severity == GuardrailSeverity.FATAL]
    warnings = [v for v in unsuppressed if v.severity == GuardrailSeverity.WARNING]

    counts = Counter(v.rule_code for v in warnings)
    breakdown = [
        RuleWarningStatDTO(rule_code=code, count=count)
        for code, count in sorted(counts.items(), key=lambda x: x[0])
    ]

    effective_ceiling = 0 if verify_zero else ceiling

    return BaselineLedgerReportDTO(
        target_directory=target,
        fatal_count=len(fatals),
        warning_count=len(warnings),
        warning_ceiling=effective_ceiling,
        rule_breakdown=breakdown,
        is_clean_of_fatals=(len(fatals) == 0),
        is_under_ceiling=(len(warnings) <= effective_ceiling),
    )


def format_report_table(report: BaselineLedgerReportDTO) -> str:
    """Formats a BaselineLedgerReportDTO into a human-readable console table.

    Args:
        report: BaselineLedgerReportDTO to format.

    Returns:
        Formatted console report string.
    """
    lines: list[str] = [
        "\n📊 AST ADVISORY WARNING BASELINE LEDGER",
        "=" * 60,
        f"Target:             {report.target_directory}",
        f"Fatal Violations:   {report.fatal_count} (Mandate: 0)",
        f"Advisory Warnings:  {report.warning_count} (Ceiling: {report.warning_ceiling})",
        "-" * 60,
        f"{'RULE CODE':<15} {'ACTIVE WARNINGS':<20}",
        "-" * 60,
    ]

    for stat in report.rule_breakdown:
        lines.append(f"{stat.rule_code:<15} {stat.count:<20}")

    lines.append("=" * 60)

    if not report.is_clean_of_fatals:
        lines.append(f"❌ FAILED: Detected {report.fatal_count} fatal violations. All fatals must be 0.")
    elif not report.is_under_ceiling:
        lines.append(
            f"❌ FAILED: Warning count ({report.warning_count}) exceeds ceiling ({report.warning_ceiling})."
        )
    else:
        lines.append("✅ PASSED: 0 fatal violations and warning count is within baseline ceiling.")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    """CLI entry point for running the warning baseline ledger."""
    parser = argparse.ArgumentParser(
        description="AST Warning Baseline Ledger (EPIC 156)",
    )
    parser.add_argument(
        "--target",
        default="backend_v2",
        help="Target directory to evaluate (default: backend_v2).",
    )
    parser.add_argument(
        "--ceiling",
        type=int,
        default=CURRENT_WARNING_CEILING,
        help=f"Warning ceiling (default: {CURRENT_WARNING_CEILING}).",
    )
    parser.add_argument(
        "--verify-zero",
        action="store_true",
        help="Assert zero warnings and zero fatals (Phase 4 completion gate).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON ledger report.",
    )

    args = parser.parse_args(argv)

    report = generate_baseline_report(
        target=args.target,
        ceiling=args.ceiling,
        verify_zero=args.verify_zero,
    )

    if args.json:
        print(report.model_dump_json(indent=2))
    else:
        print(format_report_table(report))

    if not report.is_clean_of_fatals or not report.is_under_ceiling:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
