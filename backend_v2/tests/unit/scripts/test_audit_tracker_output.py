"""Unit tests for the tracker structural audit script (scripts/audit_tracker_output.py).

Tests all verification gates: section presence, phase format compliance, required context rules,
session handover context, bidirectional Traceability Matrix mapping, and boundary conditions.
"""

import subprocess
import sys
from pathlib import Path

# Add scripts directory to sys.path to allow direct import of audit_tracker_output
scripts_dir = Path("scripts").resolve()
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from audit_tracker_output import (  # noqa: E402
    check_mandatory_sections,
    check_phase_format,
    check_required_context_rules,
    check_session_handover,
    check_traceability_mapping,
)


def _run_tracker_audit(tracker_path: Path, plan_dir: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Helper to run audit_tracker_output.py via subprocess."""
    script_path = Path("scripts/audit_tracker_output.py").resolve()
    cmd = [sys.executable, str(script_path), "--tracker", str(tracker_path)]
    if plan_dir:
        cmd.extend(["--plan-dir", str(plan_dir)])
    return subprocess.run(cmd, capture_output=True, text=True)


def test_tracker_audit_direct_helper_functions(tmp_path: Path) -> None:
    """Direct unit tests for helper functions to guarantee complete coverage."""
    # check_mandatory_sections
    content = "## Phase Execution Status\n### Post-Implementation Gates\n### Final Epic Audit\n## Instructions for the Execution Agent\n## Requirements Traceability Matrix\n# Session Handover Context\n"
    assert check_mandatory_sections(content) == []
    assert len(check_mandatory_sections("")) == 6

    # check_phase_format
    assert len(check_phase_format("no phases")) == 1
    phase_text = (
        "### Phase 1: Test\n**Plan:** @[plan.md]\n- [ ] **[NOK] Execution:** `/tier2-execute`\n  - [ ] Step 1\n"
    )
    assert check_phase_format(phase_text) == []
    broken_phase = "### Phase 1: Test\nNo plan reference here"
    assert len(check_phase_format(broken_phase)) > 0

    # check_required_context_rules
    valid_rules = "<required_context_rules>\n@[.agents/rules/00-antigravity-core.md]\n</required_context_rules>"
    assert check_required_context_rules(valid_rules) == []
    assert len(check_required_context_rules("<required_context_rules></required_context_rules>")) == 1
    assert len(check_required_context_rules("no block")) == 1

    # check_session_handover
    valid_handover = "# Session Handover Context\n## Achieved\n## Learned\n## Remaining\n## Resume Command\n"
    assert check_session_handover(valid_handover) == []
    valid_handover_status = "# Session Handover Context\n## Achieved\n## Learned\n## Remaining\n## Status\n"
    assert check_session_handover(valid_handover_status) == []
    assert len(check_session_handover("# Session Handover Context\n## Achieved\n")) > 0

    # check_traceability_mapping empty plan dir
    empty_plan_dir = tmp_path / "empty_plans"
    empty_plan_dir.mkdir()
    errs, warns = check_traceability_mapping("content", empty_plan_dir)
    assert len(warns) == 1


def test_tracker_audit_valid_full_tracker(tmp_path: Path) -> None:
    """Positive test: Valid full tracker passes audit with returncode 0."""
    tracker = tmp_path / "EPIC_TEST_tracker.md"
    tracker.write_text(
        "# EPIC TEST Tracker\n\n"
        "<required_context_rules>\n"
        "- @[.agents/rules/00-antigravity-core.md]\n"
        "</required_context_rules>\n\n"
        "## Phase Execution Status\n\n"
        "### Phase 1: Core Foundation\n"
        "**Plan:** @[docs/epic/tasks_EPIC_TEST/01_phase1_plan.md]\n"
        "- [x] **[OK] Red-Teaming:** `/tier0-research-plan @[01_plan.md] @[tracker.md]`\n"
        "- [x] **[OK] Execution:** `/tier2-execute @[01_plan.md] @[tracker.md]`\n"
        "  - [x] Step 1: Implementation\n"
        "- [x] **[OK] Audit:** `/tier8-audit-plan @[01_plan.md] @[tracker.md]`\n\n"
        "### Post-Implementation Gates\n"
        "- [x] Gate 1\n\n"
        "### Final Epic Audit\n"
        "- [x] Audit 1\n\n"
        "## Instructions for the Execution Agent\n"
        "- Always follow atomic commits.\n\n"
        "## Requirements Traceability Matrix\n"
        "| ID | Description | Mapped Step |\n"
        "|---|---|---|\n"
        "| REQ-01 | Test Req | Phase 1, Step 1 |\n\n"
        "# Session Handover Context\n"
        "## Achieved\n"
        "- Done\n\n"
        "## Learned\n"
        "- Baseline\n\n"
        "## Remaining\n"
        "- None\n\n"
        "## Status\n"
        "Complete\n",
        encoding="utf-8",
    )
    result = _run_tracker_audit(tracker)
    assert result.returncode == 0
    assert "[PASSED]" in result.stdout


def test_tracker_audit_missing_traceability_matrix(tmp_path: Path) -> None:
    """Negative test: Missing Requirements Traceability Matrix section fails audit."""
    tracker = tmp_path / "EPIC_TEST_tracker.md"
    tracker.write_text(
        "# EPIC TEST Tracker\n\n"
        "<required_context_rules>\n"
        "- @[.agents/rules/00-antigravity-core.md]\n"
        "</required_context_rules>\n\n"
        "## Phase Execution Status\n\n"
        "### Phase 1: Core Foundation\n"
        "**Plan:** @[01_plan.md]\n"
        "- [ ] **[NOK] Execution:** `/tier2-execute`\n"
        "  - [ ] Step 1: Implementation\n\n"
        "### Post-Implementation Gates\n- [ ] Gate\n\n"
        "### Final Epic Audit\n- [ ] Audit\n\n"
        "## Instructions for the Execution Agent\n- Instructions\n\n"
        "# Session Handover Context\n"
        "## Achieved\n- Done\n"
        "## Learned\n- Info\n"
        "## Remaining\n- None\n"
        "## Resume Command\n`/tier2-execute`\n",
        encoding="utf-8",
    )
    result = _run_tracker_audit(tracker)
    assert result.returncode == 1
    assert "Requirements Traceability Matrix" in result.stdout


def test_tracker_audit_missing_handover_subheading(tmp_path: Path) -> None:
    """Negative test: Missing Resume Command / Status in Session Handover fails audit."""
    tracker = tmp_path / "EPIC_TEST_tracker.md"
    tracker.write_text(
        "# EPIC TEST Tracker\n\n"
        "<required_context_rules>\n"
        "- @[.agents/rules/00-antigravity-core.md]\n"
        "</required_context_rules>\n\n"
        "## Phase Execution Status\n\n"
        "### Phase 1: Core Foundation\n"
        "**Plan:** @[01_plan.md]\n"
        "- [ ] **[NOK] Execution:** `/tier2-execute`\n"
        "  - [ ] Step 1: Implementation\n\n"
        "### Post-Implementation Gates\n- [ ] Gate\n\n"
        "### Final Epic Audit\n- [ ] Audit\n\n"
        "## Instructions for the Execution Agent\n- Instructions\n\n"
        "## Requirements Traceability Matrix\n| ID | Desc | Step |\n\n"
        "# Session Handover Context\n"
        "## Achieved\n- Done\n"
        "## Learned\n- Info\n"
        "## Remaining\n- None\n",
        encoding="utf-8",
    )
    result = _run_tracker_audit(tracker)
    assert result.returncode == 1
    assert "Resume Command" in result.stdout


def test_tracker_audit_missing_core_rule(tmp_path: Path) -> None:
    """Negative test: <required_context_rules> without 00-antigravity-core.md fails audit."""
    tracker = tmp_path / "EPIC_TEST_tracker.md"
    tracker.write_text(
        "# EPIC TEST Tracker\n\n"
        "<required_context_rules>\n"
        "- @[.agents/rules/01-python-backend.md]\n"
        "</required_context_rules>\n\n"
        "## Phase Execution Status\n\n"
        "### Phase 1: Core Foundation\n"
        "**Plan:** @[01_plan.md]\n"
        "- [ ] **[NOK] Execution:** `/tier2-execute`\n"
        "  - [ ] Step 1: Implementation\n\n"
        "### Post-Implementation Gates\n- [ ] Gate\n\n"
        "### Final Epic Audit\n- [ ] Audit\n\n"
        "## Instructions for the Execution Agent\n- Instructions\n\n"
        "## Requirements Traceability Matrix\n| ID | Desc | Step |\n\n"
        "# Session Handover Context\n"
        "## Achieved\n- Done\n"
        "## Learned\n- Info\n"
        "## Remaining\n- None\n"
        "## Resume Command\n`/tier2-execute`\n",
        encoding="utf-8",
    )
    result = _run_tracker_audit(tracker)
    assert result.returncode == 1
    assert "00-antigravity-core.md" in result.stdout


def test_tracker_audit_phase_missing_plan_reference(tmp_path: Path) -> None:
    """Negative test: Phase section missing **Plan:** @[...] fails audit."""
    tracker = tmp_path / "EPIC_TEST_tracker.md"
    tracker.write_text(
        "# EPIC TEST Tracker\n\n"
        "<required_context_rules>\n"
        "- @[.agents/rules/00-antigravity-core.md]\n"
        "</required_context_rules>\n\n"
        "## Phase Execution Status\n\n"
        "### Phase 1: Core Foundation\n"
        "- [ ] **[NOK] Execution:** `/tier2-execute`\n"
        "  - [ ] Step 1: Implementation\n\n"
        "### Post-Implementation Gates\n- [ ] Gate\n\n"
        "### Final Epic Audit\n- [ ] Audit\n\n"
        "## Instructions for the Execution Agent\n- Instructions\n\n"
        "## Requirements Traceability Matrix\n| ID | Desc | Step |\n\n"
        "# Session Handover Context\n"
        "## Achieved\n- Done\n"
        "## Learned\n- Info\n"
        "## Remaining\n- None\n"
        "## Resume Command\n`/tier2-execute`\n",
        encoding="utf-8",
    )
    result = _run_tracker_audit(tracker)
    assert result.returncode == 1
    assert "Missing `**Plan:** @[...]`" in result.stdout


def test_tracker_audit_traceability_forward_map(tmp_path: Path) -> None:
    """Negative test: Plan step not tracked in Requirements Traceability Matrix fails audit."""
    plan_dir = tmp_path / "tasks"
    plan_dir.mkdir()
    plan_file = plan_dir / "01_phase1_plan.md"
    plan_file.write_text(
        '<step id="1" name="First Step"></step>\n<step id="2" name="Second Step"></step>\n',
        encoding="utf-8",
    )

    tracker = tmp_path / "EPIC_TEST_tracker.md"
    tracker.write_text(
        "# EPIC TEST Tracker\n\n"
        "<required_context_rules>\n"
        "- @[.agents/rules/00-antigravity-core.md]\n"
        "</required_context_rules>\n\n"
        "## Phase Execution Status\n\n"
        "### Phase 1: Core Foundation\n"
        "**Plan:** @[docs/epic/tasks/01_phase1_plan.md]\n"
        "- [ ] **[NOK] Execution:** `/tier2-execute`\n"
        "  - [ ] Step 1: Implementation\n"
        "  - [ ] Step 2: Second Step\n\n"
        "### Post-Implementation Gates\n- [ ] Gate\n\n"
        "### Final Epic Audit\n- [ ] Audit\n\n"
        "## Instructions for the Execution Agent\n- Instructions\n\n"
        "## Requirements Traceability Matrix\n"
        "| ID | Desc | Mapped Step |\n"
        "|---|---|---|\n"
        "| REQ-01 | First | Phase 1, Step 1 |\n\n"
        "# Session Handover Context\n"
        "## Achieved\n- Done\n"
        "## Learned\n- Info\n"
        "## Remaining\n- None\n"
        "## Resume Command\n`/tier2-execute`\n",
        encoding="utf-8",
    )
    result = _run_tracker_audit(tracker, plan_dir=plan_dir)
    assert result.returncode == 1
    assert "Untracked Plan Step: Phase 1, Step 2" in result.stdout


def test_tracker_audit_traceability_reverse_map_valid(tmp_path: Path) -> None:
    """Positive test: All plan steps are mapped in Traceability Matrix."""
    plan_dir = tmp_path / "tasks"
    plan_dir.mkdir()
    plan_file = plan_dir / "01_phase1_plan.md"
    plan_file.write_text(
        '<step id="1" name="First Step"></step>\n',
        encoding="utf-8",
    )

    tracker = tmp_path / "EPIC_TEST_tracker.md"
    tracker.write_text(
        "# EPIC TEST Tracker\n\n"
        "<required_context_rules>\n"
        "- @[.agents/rules/00-antigravity-core.md]\n"
        "</required_context_rules>\n\n"
        "## Phase Execution Status\n\n"
        "### Phase 1: Core Foundation\n"
        "**Plan:** @[docs/epic/tasks/01_phase1_plan.md]\n"
        "- [ ] **[NOK] Execution:** `/tier2-execute`\n"
        "  - [ ] Step 1: Implementation\n\n"
        "### Post-Implementation Gates\n- [ ] Gate\n\n"
        "### Final Epic Audit\n- [ ] Audit\n\n"
        "## Instructions for the Execution Agent\n- Instructions\n\n"
        "## Requirements Traceability Matrix\n"
        "| ID | Desc | Mapped Step |\n"
        "|---|---|---|\n"
        "| REQ-01 | First | Phase 1, Step 1 |\n\n"
        "# Session Handover Context\n"
        "## Achieved\n- Done\n"
        "## Learned\n- Info\n"
        "## Remaining\n- None\n"
        "## Resume Command\n`/tier2-execute`\n",
        encoding="utf-8",
    )
    result = _run_tracker_audit(tracker, plan_dir=plan_dir)
    assert result.returncode == 0
    assert "[PASSED]" in result.stdout


def test_tracker_audit_empty_tracker(tmp_path: Path) -> None:
    """Boundary test: Empty file as tracker fails all section checks."""
    tracker = tmp_path / "empty_tracker.md"
    tracker.write_text("", encoding="utf-8")
    result = _run_tracker_audit(tracker)
    assert result.returncode == 1
    assert "[FAIL] Mandatory Sections" in result.stdout
