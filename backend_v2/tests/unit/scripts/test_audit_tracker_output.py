"""Unit tests for the tracker structural audit script (scripts/audit_tracker_output.py).

Tests all verification gates: section presence, phase format compliance, required context rules,
session handover context, bidirectional Traceability Matrix mapping, DTO structures, CLI execution, and zero reflection.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.audit_tracker_output import (
    GuardrailSeverity,
    TrackerAuditFinding,
    check_mandatory_sections,
    check_phase_format,
    check_required_context_rules,
    check_session_handover,
    check_traceability_mapping,
    main,
)


def _run_tracker_audit(tracker_path: Path, plan_dir: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Helper to run audit_tracker_output.py via subprocess."""
    script_path = Path("scripts/audit_tracker_output.py").resolve()
    cmd = [sys.executable, str(script_path), "--tracker", str(tracker_path)]
    if plan_dir:
        cmd.extend(["--plan-dir", str(plan_dir)])
    return subprocess.run(cmd, capture_output=True, text=True)


def test_tracker_audit_dto_structure() -> None:
    """Test TrackerAuditFinding Pydantic V2 DTO creation and strictness."""
    finding = TrackerAuditFinding(
        section="Mandatory Sections",
        rule_code="TRK001",
        message="Missing mandatory section header.",
        severity=GuardrailSeverity.FATAL,
        remediation="Add section header.",
    )
    assert finding.section == "Mandatory Sections"
    assert finding.rule_code == "TRK001"
    assert finding.severity == GuardrailSeverity.FATAL
    assert finding.remediation == "Add section header."


def test_tracker_audit_direct_helper_functions(tmp_path: Path) -> None:
    """Direct unit tests for helper functions verifying TrackerAuditFinding DTOs."""
    # check_mandatory_sections
    content = (
        "## Phase Execution Status\n"
        "### Post-Implementation Gates\n"
        "### Final Epic Audit\n"
        "## Instructions for the Execution Agent\n"
        "## Requirements Traceability Matrix\n"
        "# Session Handover Context\n"
    )
    assert check_mandatory_sections(content) == []
    empty_findings = check_mandatory_sections("")
    assert len(empty_findings) == 6
    assert all(f.rule_code == "TRK001" for f in empty_findings)
    assert all(f.severity == GuardrailSeverity.FATAL for f in empty_findings)

    # check_phase_format
    assert len(check_phase_format("no phases")) == 1
    assert check_phase_format("no phases")[0].rule_code == "TRK002"

    phase_text = (
        "### Phase 1: Test\n**Plan:** @[plan.md]\n- [ ] **[NOK] Execution:** `/tier2-execute`\n  - [ ] Step 1\n- [ ] **[NOK] Audit:** `/tier8-audit-plan`\n"
    )
    assert check_phase_format(phase_text) == []

    # Missing Audit step
    missing_audit_phase = (
        "### Phase 1: Test\n**Plan:** @[plan.md]\n- [ ] **[NOK] Execution:** `/tier2-execute`\n  - [ ] Step 1\n"
    )
    missing_audit_findings = check_phase_format(missing_audit_phase)
    assert len(missing_audit_findings) == 1
    assert missing_audit_findings[0].rule_code == "TRK002"
    assert "Missing mandatory `Audit:` step line" in missing_audit_findings[0].message

    broken_phase = "### Phase 1: Test\nNo plan reference here"
    broken_findings = check_phase_format(broken_phase)
    assert len(broken_findings) > 0
    assert all(f.rule_code == "TRK002" for f in broken_findings)

    # Deferred plan format
    deferred_phase = "### Phase 2: Deferred\n**Plan:** @[plan.md]\n- [ ] **[NOK] Execution:** `/tier2-execute`\n- [ ] [NOK] Create Plan\n- [ ] **[NOK] Audit:** `/tier8-audit-plan`\n"
    assert check_phase_format(deferred_phase) == []

    # check_required_context_rules
    valid_rules = "<required_context_rules>\n@[.agents/rules/00-antigravity-core.md]\n</required_context_rules>"
    assert check_required_context_rules(valid_rules) == []
    empty_rules_findings = check_required_context_rules("<required_context_rules></required_context_rules>")
    assert len(empty_rules_findings) == 1
    assert empty_rules_findings[0].rule_code == "TRK003"
    no_block_findings = check_required_context_rules("no block")
    assert len(no_block_findings) == 1
    assert no_block_findings[0].rule_code == "TRK003"

    # check_session_handover
    valid_handover = "# Session Handover Context\n## Achieved\n## Learned\n## Remaining\n## Resume Command\n"
    assert check_session_handover(valid_handover) == []
    valid_handover_status = "# Session Handover Context\n## Achieved\n## Learned\n## Remaining\n## Status\n"
    assert check_session_handover(valid_handover_status) == []
    missing_handover_findings = check_session_handover("# Session Handover Context\n## Achieved\n")
    assert len(missing_handover_findings) > 0
    assert all(f.rule_code == "TRK004" for f in missing_handover_findings)

    # check_traceability_mapping empty plan dir
    empty_plan_dir = tmp_path / "empty_plans"
    empty_plan_dir.mkdir()
    errs, warns = check_traceability_mapping("content", empty_plan_dir)
    assert len(warns) == 1
    assert warns[0].rule_code == "TRK006"
    assert warns[0].severity == GuardrailSeverity.WARNING

    # check_traceability_mapping missing traceability section
    plan_dir = tmp_path / "plans_has_files"
    plan_dir.mkdir()
    (plan_dir / "phase1.md").write_text('<step id="1"></step>', encoding="utf-8")
    m_errs, m_warns = check_traceability_mapping("no matrix here", plan_dir)
    assert len(m_errs) == 1
    assert m_errs[0].rule_code == "TRK005"


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
        "  - [ ] Step 1: Implementation\n"
        "- [ ] **[NOK] Audit:** `/tier8-audit-plan`\n\n"
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


def test_tracker_audit_main_in_process(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """In-process execution of main() to ensure full coverage on CLI driver."""
    # 1. Non-existent tracker
    monkeypatch.setattr(sys, "argv", ["audit_tracker_output.py", "--tracker", str(tmp_path / "nonexistent.md")])
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 1

    # 2. Valid tracker with valid plan directory
    plan_dir = tmp_path / "tasks_valid"
    plan_dir.mkdir()
    (plan_dir / "01_phase.md").write_text('<step id="1"></step>', encoding="utf-8")

    tracker = tmp_path / "valid_tracker.md"
    tracker.write_text(
        "# Tracker\n\n"
        "<required_context_rules>\n@[.agents/rules/00-antigravity-core.md]\n</required_context_rules>\n\n"
        "## Phase Execution Status\n\n"
        "### Phase 1: Core\n"
        "**Plan:** @[01_phase.md]\n"
        "- [x] **[OK] Execution:** `/tier2-execute`\n"
        "  - [x] Step 1\n"
        "- [x] **[OK] Audit:** `/tier8-audit-plan`\n\n"
        "### Post-Implementation Gates\n- [x] Gate\n\n"
        "### Final Epic Audit\n- [x] Audit\n\n"
        "## Instructions for the Execution Agent\n- Run tests\n\n"
        "## Requirements Traceability Matrix\n"
        "| REQ-1 | Desc | Phase 1, Step 1 |\n\n"
        "# Session Handover Context\n"
        "## Achieved\n- Done\n\n"
        "## Learned\n- Info\n\n"
        "## Remaining\n- None\n\n"
        "## Status\nComplete\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        sys,
        "argv",
        ["audit_tracker_output.py", "--tracker", str(tracker), "--plan-dir", str(plan_dir)],
    )
    with pytest.raises(SystemExit) as exc_valid:
        main()
    assert exc_valid.value.code == 0

    # 3. Failing tracker with un-mapped plan step
    (plan_dir / "01_phase.md").write_text('<step id="1"></step>\n<step id="2"></step>', encoding="utf-8")
    with pytest.raises(SystemExit) as exc_fail:
        main()
    assert exc_fail.value.code == 1

    # 4. Plan dir not existing (warns and exits 0 if tracker is valid)
    monkeypatch.setattr(
        sys,
        "argv",
        ["audit_tracker_output.py", "--tracker", str(tracker), "--plan-dir", str(tmp_path / "no_such_dir")],
    )
    with pytest.raises(SystemExit) as exc_nonexistent_dir:
        main()
    assert exc_nonexistent_dir.value.code == 0

    # 5. Invalid tracker with missing sections
    broken_tracker = tmp_path / "broken_tracker.md"
    broken_tracker.write_text("# Just title", encoding="utf-8")
    monkeypatch.setattr(
        sys,
        "argv",
        ["audit_tracker_output.py", "--tracker", str(broken_tracker)],
    )
    with pytest.raises(SystemExit) as exc_broken:
        main()
    assert exc_broken.value.code == 1


def test_tracker_audit_zero_reflection_compliance() -> None:
    """Verify scripts/audit_tracker_output.py contains zero getattr/hasattr calls."""
    script_path = Path("scripts/audit_tracker_output.py").resolve()
    tree = ast.parse(script_path.read_text(encoding="utf-8"), filename=script_path.as_posix())

    reflection_calls: list[int] = []
    for node in ast.walk(tree):
        match node:
            case ast.Call(func=ast.Name(id="getattr" | "hasattr")):
                reflection_calls.append(node.lineno)
            case _:
                pass

    assert reflection_calls == [], f"Found banned reflection calls at lines: {reflection_calls}"
