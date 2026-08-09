"""Tests for the Rule Coverage section (Section 4) of audit_planner_output.py.

Validates that the audit script correctly detects missing core rules
and domain-specific rules in generated plan files' <required_context_rules> blocks.
"""

import subprocess
import sys
from pathlib import Path


def _run_audit(epic_path: str, plan_dir: str) -> subprocess.CompletedProcess[str]:
    """Execute the audit script as a subprocess and capture output."""
    return subprocess.run(
        [sys.executable, "scripts/audit_planner_output.py", "--epic", epic_path, "--plan-dir", plan_dir],
        capture_output=True,
        text=True,
        cwd=str(Path(__file__).resolve().parents[2]),
    )


def test_rule_coverage_success_with_core_and_domain(tmp_path: Path) -> None:
    """Positive: Plan with both core and domain rule references passes."""
    epic = tmp_path / "epic.md"
    epic.write_text("No line bounds here.", encoding="utf-8")

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan = plan_dir / "phase1.md"
    plan.write_text(
        "<required_context_rules>\n"
        "@[c:\\src\\quorum\\.agents\\rules\\00-antigravity-core.md]\n"
        "@[c:\\src\\quorum\\.agents\\rules\\01-python-backend.md]\n"
        "</required_context_rules>\n"
        "<anti_targets></anti_targets>\n"
        "<dod_checklist></dod_checklist>\n"
        "<validation_gate></validation_gate>\n",
        encoding="utf-8",
    )

    result = _run_audit(str(epic), str(plan_dir))
    assert "SUCCESS" in result.stdout
    assert "All" in result.stdout
    assert "00-antigravity-core.md" in result.stdout
    assert result.returncode == 0


def test_rule_coverage_fail_missing_core_rule(tmp_path: Path) -> None:
    """Negative: Plan with domain rule but no core rule fails."""
    epic = tmp_path / "epic.md"
    epic.write_text("No bounds.", encoding="utf-8")

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan = plan_dir / "phase1.md"
    plan.write_text(
        "<required_context_rules>\n"
        "@[c:\\src\\quorum\\.agents\\rules\\01-python-backend.md]\n"
        "</required_context_rules>\n"
        "<anti_targets></anti_targets>\n"
        "<dod_checklist></dod_checklist>\n"
        "<validation_gate></validation_gate>\n",
        encoding="utf-8",
    )

    result = _run_audit(str(epic), str(plan_dir))
    assert "FAILED" in result.stdout
    assert "00-antigravity-core.md" in result.stdout
    assert result.returncode == 1


def test_rule_coverage_fail_missing_domain_rule(tmp_path: Path) -> None:
    """Negative: Plan with core rule but no domain-specific rule fails."""
    epic = tmp_path / "epic.md"
    epic.write_text("No bounds.", encoding="utf-8")

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan = plan_dir / "phase1.md"
    plan.write_text(
        "<required_context_rules>\n"
        "@[c:\\src\\quorum\\.agents\\rules\\00-antigravity-core.md]\n"
        "</required_context_rules>\n"
        "<anti_targets></anti_targets>\n"
        "<dod_checklist></dod_checklist>\n"
        "<validation_gate></validation_gate>\n",
        encoding="utf-8",
    )

    result = _run_audit(str(epic), str(plan_dir))
    assert "FAILED" in result.stdout
    assert "zero domain-specific rules" in result.stdout
    assert result.returncode == 1


def test_rule_coverage_skip_no_required_context_rules_block(tmp_path: Path) -> None:
    """Boundary: Plan with no <required_context_rules> block skips the check."""
    epic = tmp_path / "epic.md"
    epic.write_text("No bounds.", encoding="utf-8")

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan = plan_dir / "phase1.md"
    plan.write_text(
        "Just a plan with no context rules block.\n"
        "<anti_targets></anti_targets>\n"
        "<dod_checklist></dod_checklist>\n"
        "<validation_gate></validation_gate>\n",
        encoding="utf-8",
    )

    result = _run_audit(str(epic), str(plan_dir))
    assert "SKIP" in result.stdout
    assert "non-self-hydrating" in result.stdout
    assert result.returncode == 0


def test_rule_coverage_multiple_domain_rules(tmp_path: Path) -> None:
    """Positive: Plan with core and multiple domain rules passes."""
    epic = tmp_path / "epic.md"
    epic.write_text("No bounds.", encoding="utf-8")

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan = plan_dir / "phase1.md"
    plan.write_text(
        "<required_context_rules>\n"
        "@[c:\\src\\quorum\\.agents\\rules\\00-antigravity-core.md]\n"
        "@[c:\\src\\quorum\\.agents\\rules\\01-python-backend.md]\n"
        "@[c:\\src\\quorum\\.agents\\rules\\05_llm_architecture.md]\n"
        "</required_context_rules>\n"
        "<anti_targets></anti_targets>\n"
        "<dod_checklist></dod_checklist>\n"
        "<validation_gate></validation_gate>\n",
        encoding="utf-8",
    )

    result = _run_audit(str(epic), str(plan_dir))
    assert "SUCCESS" in result.stdout
    assert result.returncode == 0
