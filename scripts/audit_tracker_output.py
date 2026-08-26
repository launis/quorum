"""Audit Tracker Output.

A deterministic structural audit script to ensure generated Epic tracking documents
strictly conform to Quorum formatting laws, mandatory sections, handover structures,
and bidirectional Requirements Traceability Matrix mapping.
"""

from __future__ import annotations

import argparse
import io
import re
import sys
from enum import StrEnum
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

# Force UTF-8 encoding for stdout on Windows without reflection
if isinstance(sys.stdout, io.TextIOWrapper):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError, io.UnsupportedOperation:
        pass


class GuardrailSeverity(StrEnum):
    """Severity classification for tracker audit findings."""

    WARNING = "WARNING"
    FATAL = "FATAL"


class TrackerAuditFinding(BaseModel):
    """Pydantic V2 DTO representing an architectural tracker structure violation."""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True)

    section: Annotated[str, Field(description="Section where violation occurred")]
    rule_code: Annotated[str, Field(pattern=r"^TRK\d{3}$", description="Rule code e.g. TRK001")]
    message: Annotated[str, Field(description="Descriptive violation message")]
    severity: Annotated[GuardrailSeverity, Field(description="Severity tier")]
    remediation: Annotated[str, Field(description="Deterministic remediation guidance")]


def check_mandatory_sections(content: str) -> list[TrackerAuditFinding]:
    """Verify presence of all mandatory section headers in the tracker content."""
    patterns: list[tuple[str, str]] = [
        (r"##\s+Phase Execution Status", "## Phase Execution Status"),
        (r"###\s+Post-Implementation Gates", "### Post-Implementation Gates"),
        (r"###\s+Final Epic Audit", "### Final Epic Audit"),
        (r"##\s+Instructions for the Execution Agent", "## Instructions for the Execution Agent"),
        (r"##\s+Requirements Traceability Matrix", "## Requirements Traceability Matrix"),
        (r"#\s+Session Handover Context", "# Session Handover Context"),
    ]
    findings: list[TrackerAuditFinding] = []
    for pat, name in patterns:
        if not re.search(pat, content, re.IGNORECASE):
            findings.append(
                TrackerAuditFinding(
                    section=name,
                    rule_code="TRK001",
                    message=f"Missing mandatory section header: '{name}'.",
                    severity=GuardrailSeverity.FATAL,
                    remediation=f"Add '{name}' section header to the tracker document.",
                )
            )
    return findings


def check_phase_format(content: str) -> list[TrackerAuditFinding]:
    """Validate format compliance for all Phase sections in the tracker."""
    phase_pattern = re.compile(
        r"###\s+Phase\s+(\d+)[^\n]*\n([\s\S]*?)(?=(?:###\s+Phase\s+\d+|###\s+Integration Checkpoint|###\s+Post-Implementation|\Z))",
        re.IGNORECASE,
    )
    phases = phase_pattern.findall(content)
    if not phases:
        return [
            TrackerAuditFinding(
                section="Phase Execution Status",
                rule_code="TRK002",
                message="No '### Phase N:' sections found in tracker.",
                severity=GuardrailSeverity.FATAL,
                remediation="Add at least one '### Phase N: <Title>' section under '## Phase Execution Status'.",
            )
        ]

    findings: list[TrackerAuditFinding] = []
    for phase_num, phase_body in phases:
        section_name = f"Phase {phase_num}"
        if not re.search(r"\*\*Plan:\*\*\s+@\[[^\]]+\]", phase_body):
            findings.append(
                TrackerAuditFinding(
                    section=section_name,
                    rule_code="TRK002",
                    message=f"Phase {phase_num}: Missing `**Plan:** @[...]` reference.",
                    severity=GuardrailSeverity.FATAL,
                    remediation=f"Add `**Plan:** @[path/to/plan.md]` under '### Phase {phase_num}'.",
                )
            )

        has_step_line = bool(
            re.search(r"-\s+\[[ x]\]\s+\*\*\[(?:OK|NOK)\]\s+(?:Red-Teaming|Execution|Audit)", phase_body, re.IGNORECASE)
        )
        if not has_step_line:
            findings.append(
                TrackerAuditFinding(
                    section=section_name,
                    rule_code="TRK002",
                    message=f"Phase {phase_num}: Missing standard step lines (Red-Teaming/Execution/Audit).",
                    severity=GuardrailSeverity.FATAL,
                    remediation="Add step lines `- [ ] **[NOK] Execution:** /tier2-execute` or similar.",
                )
            )

        has_indented_steps = bool(re.search(r"^\s{2,}-\s+\[[ x]\]\s+Step\b", phase_body, re.MULTILINE))
        is_deferred = bool(re.search(r"\[(?:OK|NOK)\]\s+Create Plan", phase_body, re.IGNORECASE))
        if not has_indented_steps and not is_deferred:
            findings.append(
                TrackerAuditFinding(
                    section=section_name,
                    rule_code="TRK002",
                    message=f"Phase {phase_num}: Missing indented `- [ ] Step` or `- [x] Step` checkboxes.",
                    severity=GuardrailSeverity.FATAL,
                    remediation="Add indented `- [ ] Step N.M:` checkboxes under the execution step line.",
                )
            )
    return findings


def check_required_context_rules(content: str) -> list[TrackerAuditFinding]:
    """Verify presence of <required_context_rules> block referencing 00-antigravity-core.md."""
    match = re.search(r"<required_context_rules>([\s\S]*?)</required_context_rules>", content)
    if not match:
        return [
            TrackerAuditFinding(
                section="Required Context Rules",
                rule_code="TRK003",
                message="Missing `<required_context_rules>` XML block.",
                severity=GuardrailSeverity.FATAL,
                remediation="Add canonical `<required_context_rules>` XML block at top of tracker.",
            )
        ]
    if not re.search(r"00-antigravity-core\.md", match.group(1)):
        return [
            TrackerAuditFinding(
                section="Required Context Rules",
                rule_code="TRK003",
                message="`<required_context_rules>` block does not reference `00-antigravity-core.md`.",
                severity=GuardrailSeverity.FATAL,
                remediation="Add `<rule>@[.agents/rules/00-antigravity-core.md]</rule>` inside `<required_context_rules>`.",
            )
        ]
    return []


def check_session_handover(content: str) -> list[TrackerAuditFinding]:
    """Verify Session Handover Context sub-headings (tolerating Status for completed trackers)."""
    match = re.search(r"#\s+Session Handover Context([\s\S]*?)(?=\Z)", content, re.IGNORECASE)
    if not match:
        return [
            TrackerAuditFinding(
                section="Session Handover Context",
                rule_code="TRK004",
                message="Missing `# Session Handover Context` section.",
                severity=GuardrailSeverity.FATAL,
                remediation="Add `# Session Handover Context` section with ## Achieved, ## Learned, ## Remaining.",
            )
        ]
    body = match.group(1)
    findings: list[TrackerAuditFinding] = []
    for h in ["## Achieved", "## Learned", "## Remaining"]:
        if not re.search(rf"^{re.escape(h)}\b", body, re.MULTILINE):
            findings.append(
                TrackerAuditFinding(
                    section="Session Handover Context",
                    rule_code="TRK004",
                    message=f"Missing sub-heading `{h}` in Session Handover Context.",
                    severity=GuardrailSeverity.FATAL,
                    remediation=f"Add sub-heading '{h}' under '# Session Handover Context'.",
                )
            )
    if not re.search(r"^##\s+(?:Resume Command|Status)\b", body, re.MULTILINE):
        findings.append(
            TrackerAuditFinding(
                section="Session Handover Context",
                rule_code="TRK004",
                message="Missing `## Resume Command` (or `## Status` for completed trackers) in Session Handover.",
                severity=GuardrailSeverity.FATAL,
                remediation="Add '## Resume Command' or '## Status' under '# Session Handover Context'.",
            )
        )
    return findings


def check_traceability_mapping(
    content: str, plan_dir: Path
) -> tuple[list[TrackerAuditFinding], list[TrackerAuditFinding]]:
    """Bidirectional verification between Requirements Traceability Matrix and Plan Steps."""
    plan_files = sorted(plan_dir.glob("*.md"))
    if not plan_files:
        return [], [
            TrackerAuditFinding(
                section="Requirements Traceability Matrix",
                rule_code="TRK006",
                message=f"No .md plan files found in plan directory: {plan_dir.as_posix()}",
                severity=GuardrailSeverity.WARNING,
                remediation="Ensure plan directory contains valid Markdown plan documents.",
            )
        ]

    plan_steps: dict[tuple[int, str], str] = {}
    for pf in plan_files:
        p_match = re.search(r"phase\s*(\d+)", pf.name, re.IGNORECASE) or re.search(
            r"0?(\d+)_phase", pf.name, re.IGNORECASE
        )
        p_num = int(p_match.group(1)) if p_match else 1
        for s_id in re.findall(r'<step\s+id="([^"]+)"', pf.read_text(encoding="utf-8")):
            if str(s_id) != "0":
                plan_steps[(p_num, str(s_id))] = pf.name

    m_match = re.search(
        r"##\s+Requirements Traceability Matrix([\s\S]*?)(?=(?:#\s+Session Handover|\Z))", content, re.IGNORECASE
    )
    if not m_match:
        return [
            TrackerAuditFinding(
                section="Requirements Traceability Matrix",
                rule_code="TRK005",
                message="Cannot find Requirements Traceability Matrix content for step mapping.",
                severity=GuardrailSeverity.FATAL,
                remediation="Add '## Requirements Traceability Matrix' table mapping requirements to plan steps.",
            )
        ], []

    m_steps = {
        (int(p), s)
        for p, s in re.findall(r"Phase\s+(\d+)[,\s]+Step\s+([0-9a-zA-Z_.-]+)", m_match.group(1), re.IGNORECASE)
    }

    errors: list[TrackerAuditFinding] = [
        TrackerAuditFinding(
            section="Requirements Traceability Matrix",
            rule_code="TRK005",
            message=f"Untracked Plan Step: Phase {p}, Step {s} (from `{f}`) not in Traceability Matrix.",
            severity=GuardrailSeverity.FATAL,
            remediation=f"Add Phase {p}, Step {s} to Requirements Traceability Matrix.",
        )
        for (p, s), f in sorted(plan_steps.items())
        if (p, s) not in m_steps
    ]
    warnings: list[TrackerAuditFinding] = [
        TrackerAuditFinding(
            section="Requirements Traceability Matrix",
            rule_code="TRK006",
            message=f"Orphan Matrix Step: Matrix references Phase {p}, Step {s}, which was not found in plans.",
            severity=GuardrailSeverity.WARNING,
            remediation=f"Verify Phase {p}, Step {s} exists in plan files or remove from matrix.",
        )
        for p, s in sorted(m_steps)
        if (p, s) not in plan_steps
    ]
    return errors, warnings


def main() -> None:
    """Execute structural audit for tracker file."""
    parser = argparse.ArgumentParser(description="Audit Epic Tracker output for structural compliance.")
    parser.add_argument("--tracker", required=True, type=str, help="Path to the tracker .md file")
    parser.add_argument("--plan-dir", required=False, type=str, default=None, help="Path to task plan directory")
    args = parser.parse_args()

    tracker_path = Path(args.tracker)
    if not tracker_path.exists():
        print(f"ERROR: Tracker file not found: {tracker_path.as_posix()}")
        sys.exit(1)

    content = tracker_path.read_text(encoding="utf-8")
    failed = False
    print(f"\n# Tracker Structural Audit: {tracker_path.name}\n" + "-" * 50)

    for cat_name, findings in [
        ("Mandatory Sections", check_mandatory_sections(content)),
        ("Phase Format", check_phase_format(content)),
        ("Context Rules", check_required_context_rules(content)),
        ("Session Handover", check_session_handover(content)),
    ]:
        if findings:
            print(f"[FAIL] {cat_name}:")
            for f in findings:
                print(f"  - [{f.rule_code}] {f.message}")
                print(f"    Remediation: {f.remediation}")
            failed = True
        else:
            print(f"[PASS] {cat_name}: Valid.")

    if args.plan_dir:
        p_dir = Path(args.plan_dir)
        if p_dir.exists() and p_dir.is_dir():
            t_errs, t_warns = check_traceability_mapping(content, p_dir)
            if t_errs:
                print("[FAIL] Traceability Matrix Forward Map:")
                for e in t_errs:
                    print(f"  - [{e.rule_code}] {e.message}")
                    print(f"    Remediation: {e.remediation}")
                failed = True
            else:
                print("[PASS] Traceability Matrix: All plan steps tracked in matrix.")
            if t_warns:
                print("[WARN] Traceability Matrix Reverse Map:")
                for w in t_warns:
                    print(f"  - [{w.rule_code}] {w.message}")
                    print(f"    Remediation: {w.remediation}")
        else:
            print(f"[WARN] Plan directory `{args.plan_dir}` does not exist, skipping mapping check.")

    print("-" * 50)
    if failed:
        print(f"[FAILED] AUDIT FAILED: Tracker `{tracker_path.name}` violates structural standards.")
        sys.exit(1)
    print(f"[PASSED] AUDIT PASSED: Tracker `{tracker_path.name}` is structurally compliant.")
    sys.exit(0)


if __name__ == "__main__":
    main()
