"""Audit Tracker Output.

A deterministic structural audit script to ensure generated Epic tracking documents
strictly conform to Quorum formatting laws, mandatory sections, handover structures,
and bidirectional Requirements Traceability Matrix mapping.
"""

import argparse
import re
import sys
from pathlib import Path

scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))


def check_mandatory_sections(content: str) -> list[str]:
    """Verify presence of all mandatory section headers in the tracker content."""
    patterns = [
        (r"##\s+Phase Execution Status", "## Phase Execution Status"),
        (r"###\s+Post-Implementation Gates", "### Post-Implementation Gates"),
        (r"###\s+Final Epic Audit", "### Final Epic Audit"),
        (r"##\s+Instructions for the Execution Agent", "## Instructions for the Execution Agent"),
        (r"##\s+Requirements Traceability Matrix", "## Requirements Traceability Matrix"),
        (r"#\s+Session Handover Context", "# Session Handover Context"),
    ]
    return [name for pat, name in patterns if not re.search(pat, content, re.IGNORECASE)]


def check_phase_format(content: str) -> list[str]:
    """Validate format compliance for all Phase sections in the tracker."""
    phase_pattern = re.compile(
        r"###\s+Phase\s+(\d+)[^\n]*\n([\s\S]*?)(?=(?:###\s+Phase\s+\d+|###\s+Integration Checkpoint|###\s+Post-Implementation|\Z))",
        re.IGNORECASE,
    )
    phases = phase_pattern.findall(content)
    if not phases:
        return ["No '### Phase N:' sections found in tracker."]

    errors = []
    for phase_num, phase_body in phases:
        if not re.search(r"\*\*Plan:\*\*\s+@\[[^\]]+\]", phase_body):
            errors.append(f"Phase {phase_num}: Missing `**Plan:** @[...]` reference.")

        has_step_line = bool(
            re.search(r"-\s+\[[ x]\]\s+\*\*\[(?:OK|NOK)\]\s+(?:Red-Teaming|Execution|Audit)", phase_body, re.IGNORECASE)
        )
        if not has_step_line:
            errors.append(f"Phase {phase_num}: Missing standard step lines (Red-Teaming/Execution/Audit).")

        has_indented_steps = bool(re.search(r"^\s{2,}-\s+\[[ x]\]\s+Step\b", phase_body, re.MULTILINE))
        is_deferred = bool(re.search(r"\[(?:OK|NOK)\]\s+Create Plan", phase_body, re.IGNORECASE))
        if not has_indented_steps and not is_deferred:
            errors.append(f"Phase {phase_num}: Missing indented `- [ ] Step` or `- [x] Step` checkboxes.")
    return errors


def check_required_context_rules(content: str) -> list[str]:
    """Verify presence of <required_context_rules> block referencing 00-antigravity-core.md."""
    match = re.search(r"<required_context_rules>([\s\S]*?)</required_context_rules>", content)
    if not match:
        return ["Missing `<required_context_rules>` XML block."]
    if not re.search(r"00-antigravity-core\.md", match.group(1)):
        return ["`<required_context_rules>` block does not reference `00-antigravity-core.md`."]
    return []


def check_session_handover(content: str) -> list[str]:
    """Verify Session Handover Context sub-headings (tolerating Status for completed trackers)."""
    match = re.search(r"#\s+Session Handover Context([\s\S]*?)(?=\Z)", content, re.IGNORECASE)
    if not match:
        return ["Missing `# Session Handover Context` section."]
    body = match.group(1)
    errors = [
        f"Missing sub-heading `{h}` in Session Handover Context."
        for h in ["## Achieved", "## Learned", "## Remaining"]
        if not re.search(rf"^{re.escape(h)}\b", body, re.MULTILINE)
    ]
    if not re.search(r"^##\s+(?:Resume Command|Status)\b", body, re.MULTILINE):
        errors.append("Missing `## Resume Command` (or `## Status` for completed trackers) in Session Handover.")
    return errors


def check_traceability_mapping(content: str, plan_dir: Path) -> tuple[list[str], list[str]]:
    """Bidirectional verification between Requirements Traceability Matrix and Plan Steps."""
    plan_files = sorted(plan_dir.glob("*.md"))
    if not plan_files:
        return [], [f"No .md plan files found in plan directory: {plan_dir.as_posix()}"]

    plan_steps: dict[tuple[int, str], str] = {}
    for pf in plan_files:
        p_match = re.search(r"(?:phase\s*(\d+)|0?(\d+)_phase)", pf.name, re.IGNORECASE)
        p_num = int(p_match.group(1) or p_match.group(2)) if p_match else 1
        for s_id in re.findall(r'<step\s+id="([^"]+)"', pf.read_text(encoding="utf-8")):
            if str(s_id) != "0":
                plan_steps[(p_num, str(s_id))] = pf.name

    m_match = re.search(
        r"##\s+Requirements Traceability Matrix([\s\S]*?)(?=(?:#\s+Session Handover|\Z))", content, re.IGNORECASE
    )
    if not m_match:
        return ["Cannot find Requirements Traceability Matrix content for step mapping."], []

    m_steps = {
        (int(p), s)
        for p, s in re.findall(r"Phase\s+(\d+)[,\s]+Step\s+([0-9a-zA-Z_.-]+)", m_match.group(1), re.IGNORECASE)
    }

    errors = [
        f"Untracked Plan Step: Phase {p}, Step {s} (from `{f}`) not in Traceability Matrix."
        for (p, s), f in sorted(plan_steps.items())
        if (p, s) not in m_steps
    ]
    warnings = [
        f"Orphan Matrix Step: Matrix references Phase {p}, Step {s}, which was not found in plans."
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

    for cat_name, errs in [
        ("Mandatory Sections", check_mandatory_sections(content)),
        ("Phase Format", check_phase_format(content)),
        ("Context Rules", check_required_context_rules(content)),
        ("Session Handover", check_session_handover(content)),
    ]:
        if errs:
            print(f"[FAIL] {cat_name}:")
            for e in errs:
                print(f"  - {e}")
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
                    print(f"  - {e}")
                failed = True
            else:
                print("[PASS] Traceability Matrix: All plan steps tracked in matrix.")
            if t_warns:
                print("[WARN] Traceability Matrix Reverse Map:")
                for w in t_warns:
                    print(f"  - {w}")
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
