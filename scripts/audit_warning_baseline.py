"""Warning Baseline Ledger and Quality Gate Verification Engine.

Single Source of Truth for tracking AST advisory warning baselines across backend_v2,
asserting mathematical zero FATAL violations, and enforcing monotonic warning reduction.
"""

from __future__ import annotations

import argparse
import io
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

import re
import tokenize

from pydantic import ConfigDict, Field

from backend_v2.models.core_base import V2CoreBase
from scripts._ast_guardrails import GuardrailSeverity, scan_files_for_guardrails

CURRENT_WARNING_CEILING = 0

__all__ = [
    "CURRENT_RESIDUAL_CEILINGS",
    "CURRENT_WARNING_CEILING",
    "BaselineLedgerReportDTO",
    "ResidualDebtCeilingsDTO",
    "RuleWarningStatDTO",
    "compute_census_counts",
    "format_report_table",
    "generate_baseline_report",
    "main",
    "verify_residual_debt_ceilings",
]


class ResidualDebtCeilingsDTO(V2CoreBase):
    """Residual Debt Ceiling Ledger enforcing exact-equality ceilings across all census categories."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    d: Annotated[int, Field(ge=0, description="Census D: Keyword-injected repository mocks ceiling.")]
    f: Annotated[int, Field(ge=0, description="Census F: String-target repository patches ceiling.")]
    k: Annotated[int, Field(ge=0, description="Census K: Ad-hoc repository classes ceiling.")]
    x: Annotated[int, Field(ge=0, description="Census X: cast(Any, ...) ceiling.")]
    n: Annotated[int, Field(ge=0, description="Census N: # noqa comment tokens ceiling.")]
    t: Annotated[int, Field(ge=0, description="Census T: type-ignore annotations ceiling.")]
    p: Annotated[int, Field(ge=0, description="Census P: dict[str, Any/object] in tests/scripts ceiling.")]
    m: Annotated[int, Field(ge=0, description="Census M: Production Mapping/test_settings dicts ceiling.")]
    r: Annotated[int, Field(ge=0, description="Census R: Non-codec Map in Dart ceiling.")]
    s: Annotated[int, Field(ge=0, description="Census S: Unconditional skip/xfail markers ceiling.")]


# Configured baseline ceilings (EPIC 157 Phase 3 ratchet)
CURRENT_RESIDUAL_CEILINGS = ResidualDebtCeilingsDTO(
    d=807,
    f=51,
    k=25,
    x=806,
    n=76,
    t=409,
    p=401,
    m=10,
    r=191,
    s=0,
)


def compute_census_counts(repo_root: Path | None = None) -> ResidualDebtCeilingsDTO:
    """Computes exact live census counts across all census categories (D, F, K, X, N, T, P, M, R, S)."""
    root = repo_root or Path(_workspace_root)
    tests_dir = root / "backend_v2" / "tests"

    # Census S: Unconditional skip / xfail markers
    s_count = 0
    if tests_dir.exists():
        for p in tests_dir.rglob("*.py"):
            text = p.read_text(encoding="utf-8", errors="ignore")
            s_count += len(re.findall(r"@pytest\.mark\.(skip|xfail)\b", text))

    # Census K: Ad-hoc repository classes
    k_count = 0
    if tests_dir.exists():
        for p in tests_dir.rglob("*.py"):
            p_str = p.as_posix()
            if "/fakes/" in p_str or "test_ast_engine_dispatch_guardrails" in p_str:
                continue
            for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                m = re.search(r"^\s*class\s+(\w*Repo\w*)\b", line)
                if m and not re.search(r"Report|Response", m.group(1)):
                    k_count += 1

    # Census F: String-target repository patches
    f_count = 0
    if tests_dir.exists():
        for p in tests_dir.rglob("*.py"):
            if "/tests/unit/scripts/" in p.as_posix():
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            f_count += len(re.findall(r"patch\(\s*[\"'][\w\.]*\.(\w*Repository)[\"']", text))

    # Census D: Keyword-injected repository mocks
    d_count = 0
    if tests_dir.exists():
        for p in tests_dir.rglob("*.py"):
            text = p.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r"\b(\w*repo\w*)=(AsyncMock|MagicMock|Mock)\(", text):
                if not re.search(r"report|response", m.group(1), re.IGNORECASE):
                    d_count += 1

    # Census X: cast(Any, ...)
    x_count = 0
    for search_dir in ["backend_v2", "scripts"]:
        d_path = root / search_dir
        if d_path.exists():
            for p in d_path.rglob("*.py"):
                text = p.read_text(encoding="utf-8", errors="ignore")
                x_count += len(re.findall(r"cast\(\s*Any\b", text))

    # Census T: type-ignore tokens
    t_count = 0
    for search_dir in ["backend_v2", "scripts"]:
        d_path = root / search_dir
        if d_path.exists():
            for p in d_path.rglob("*.py"):
                text = p.read_text(encoding="utf-8", errors="ignore")
                t_count += len(re.findall(r"#\s*type:\s*ignore", text))

    # Census P: naked dicts outside production modules
    p_count = 0
    if tests_dir.exists():
        for p in tests_dir.rglob("*.py"):
            text = p.read_text(encoding="utf-8", errors="ignore")
            p_count += len(re.findall(r"\b[Dd]ict\[\s*str\s*,\s*(?:Any|object)\s*\]", text))
    scripts_dir = root / "scripts"
    if scripts_dir.exists():
        for p in scripts_dir.rglob("*.py"):
            text = p.read_text(encoding="utf-8", errors="ignore")
            p_count += len(re.findall(r"\b[Dd]ict\[\s*str\s*,\s*(?:Any|object)\s*\]", text))

    # Census M: Production Mapping sites and test_settings.py dicts
    m_count = 0
    backend_dir = root / "backend_v2"
    if backend_dir.exists():
        for p in backend_dir.rglob("*.py"):
            if "/backend_v2/tests/" in p.as_posix():
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            m_count += len(re.findall(r"\b(?:Mutable)?Mapping\[\s*str\s*,\s*(?:Any|object)\s*\]", text))
    ts = root / "backend_v2" / "core" / "test_settings.py"
    if ts.exists():
        text = ts.read_text(encoding="utf-8", errors="ignore")
        m_count += len(re.findall(r"\b[Dd]ict\[\s*str\s*,\s*(?:Any|object)\s*\]", text))

    # Census N: # noqa comment tokens
    n_count = 0
    for search_dir in ["backend_v2", "scripts"]:
        d_path = root / search_dir
        if d_path.exists():
            for p in d_path.rglob("*.py"):
                try:
                    tokens = tokenize.tokenize(io.BytesIO(p.read_bytes()).readline)
                    for tok in tokens:
                        if tok.type == tokenize.COMMENT and "# noqa" in tok.string.lower():
                            n_count += 1
                except Exception:
                    pass

    # Census R: Non-codec Map<String, dynamic> in Dart
    r_count = 0
    client_lib = root / "client_app_v2" / "lib"
    if client_lib.exists():
        for p in client_lib.rglob("*.dart"):
            if p.name.endswith(".g.dart") or p.name.endswith(".freezed.dart"):
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            for line in text.splitlines():
                if re.search(r"Map<String,\s*dynamic>", line):
                    if not re.search(
                        r"fromJson\(\s*Map<String,\s*dynamic>\s+\w+\s*\)|Map<String,\s*dynamic>\s+toJson\(", line
                    ):
                        r_count += 1

    return ResidualDebtCeilingsDTO(
        d=d_count,
        f=f_count,
        k=k_count,
        x=x_count,
        n=n_count,
        t=t_count,
        p=p_count,
        m=m_count,
        r=r_count,
        s=s_count,
    )


def verify_residual_debt_ceilings(
    live: ResidualDebtCeilingsDTO,
    ceiling: ResidualDebtCeilingsDTO = CURRENT_RESIDUAL_CEILINGS,
) -> tuple[bool, list[str]]:
    """Asserts exact equality between live counts and configured ceilings (Monotonic Ratchet).

    Args:
        live: Live measured census counts.
        ceiling: Configured ceiling counts.

    Returns:
        Tuple of (is_compliant, list_of_report_lines).
    """
    messages: list[str] = [
        "\n🏛️ RESIDUAL DEBT CEILINGS (EPIC 157 MONOTONIC RATCHET)",
        "=" * 60,
        f"{'CENSUS':<10} {'LIVE':<10} {'CEILING':<10} {'STATUS':<20}",
        "-" * 60,
    ]
    is_valid = True
    for field_name in ["d", "f", "k", "x", "n", "t", "p", "m", "r", "s"]:
        live_val = getattr(live, field_name)
        ceil_val = getattr(ceiling, field_name)
        status = "MATCH"
        if live_val > ceil_val:
            is_valid = False
            status = "EXCEEDED ❌"
        elif live_val < ceil_val:
            is_valid = False
            status = "LOWERED ⚠️ (RATCHET NEEDED)"
        messages.append(f"{field_name.upper():<10} {live_val:<10} {ceil_val:<10} {status:<20}")
    messages.append("=" * 60)
    if is_valid:
        messages.append("✅ PASSED: All residual debt categories strictly conform to ratchet ceilings.")
    else:
        messages.append("❌ FAILED: Residual debt mismatch. Ceilings must match exact counts (monotonic ratchet).")
    return is_valid, messages


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
    """Scan target directory and compile a typed baseline ledger report.

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
        RuleWarningStatDTO(rule_code=code, count=count) for code, count in sorted(counts.items(), key=lambda x: x[0])
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
    """Format a BaselineLedgerReportDTO into a human-readable console table.

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
        lines.append(f"❌ FAILED: Warning count ({report.warning_count}) exceeds ceiling ({report.warning_ceiling}).")
    else:
        lines.append("✅ PASSED: 0 fatal violations and warning count is within baseline ceiling.")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    """CLI entry point for running the warning baseline ledger.

    Args:
        argv: Optional list of command-line argument strings.
    """
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
        "--check-residual",
        action="store_true",
        default=False,
        help="Check residual debt ceilings (automatically checked when --verify-zero is supplied).",
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

    residual_passed = True
    if args.verify_zero or args.check_residual:
        live_census = compute_census_counts()
        residual_passed, residual_msgs = verify_residual_debt_ceilings(live_census)
        if not args.json:
            print("\n".join(residual_msgs))

    if not report.is_clean_of_fatals or not report.is_under_ceiling or not residual_passed:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
