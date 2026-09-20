"""Tests for Tier 1 and Tier 8 audit planner output verification script."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.audit_planner_output import main


def test_main_missing_epic_file(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that missing epic file exits with 1."""
    monkeypatch.setattr("sys.argv", ["audit_planner_output.py", "--epic", "nonexistent.md", "--plan-dir", "."])
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1


def test_main_missing_plan_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that missing plan directory exits with 1."""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text("dummy", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        ["audit_planner_output.py", "--epic", str(epic_file), "--plan-dir", "nonexistent"],
    )
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1


def test_main_empty_plan_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that empty plan directory exits with 1."""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text("dummy", encoding="utf-8")
    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    monkeypatch.setattr(
        "sys.argv",
        ["audit_planner_output.py", "--epic", str(epic_file), "--plan-dir", str(plan_dir)],
    )
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1


def test_main_missing_tags(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that missing mandatory tags fails."""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text("dummy", encoding="utf-8")
    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan_file = plan_dir / "plan.md"
    plan_file.write_text("dummy plan", encoding="utf-8")

    monkeypatch.setattr(
        "sys.argv",
        ["audit_planner_output.py", "--epic", str(epic_file), "--plan-dir", str(plan_dir)],
    )
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1


def test_main_success_all_checks(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that valid inputs with line bounds, targets, KIs, and demolish symbols succeed."""
    py_file = tmp_path / "sample.py"
    py_file.write_text("def fn() -> None:\n    pass\n", encoding="utf-8")
    rel_py_path = py_file.as_posix()

    epic_file = tmp_path / "epic.md"
    epic_file.write_text(
        f"# Epic\n"
        f"- `[MODIFY]` `@[{rel_py_path}#L1-L2]`\n"
        f"#{rel_py_path}#L1-L2\n"
        f"<required_context_rules>\n"
        f"  <knowledge_item>@[ki_test.md]</knowledge_item>\n"
        f"</required_context_rules>\n"
        f"<demolish>\n`old_fn`\n</demolish>\n",
        encoding="utf-8",
    )

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan_file = plan_dir / "01_plan.md"
    plan_file.write_text(
        f"# Plan 1\n"
        f"Target: `@[{rel_py_path}#L1-L2]`\n"
        f"#{rel_py_path}#L1-L2\n"
        f"<required_context_rules>\n"
        f"  <rule>@[.agents/rules/00-antigravity-core.md]</rule>\n"
        f"  <rule>@[.agents/rules/01-python-backend.md]</rule>\n"
        f"  <knowledge_item>@[ki_test.md]</knowledge_item>\n"
        f"</required_context_rules>\n"
        f"<demolish>\n`old_fn`\n</demolish>\n"
        f"<anti_targets></anti_targets>\n"
        f"<dod_checklist></dod_checklist>\n"
        f"<validation_gate></validation_gate>\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["audit_planner_output.py", "--epic", str(epic_file), "--plan-dir", str(plan_dir)],
    )
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 0


def test_main_fails_on_missing_bounds(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that missing bounds from epic triggers exit code 1."""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text("# Epic\n#sample.py#L1-L10\n", encoding="utf-8")

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan_file = plan_dir / "01_plan.md"
    plan_file.write_text(
        "# Plan\n"
        "<required_context_rules>\n"
        "  <rule>@[.agents/rules/00-antigravity-core.md]</rule>\n"
        "</required_context_rules>\n"
        "<anti_targets></anti_targets>\n"
        "<dod_checklist></dod_checklist>\n"
        "<validation_gate></validation_gate>\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["audit_planner_output.py", "--epic", str(epic_file), "--plan-dir", str(plan_dir)],
    )
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1


def test_main_fails_on_missing_targets(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that missing targets from epic triggers exit code 1."""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text("# Epic\n- `[MODIFY]` `@[backend_v2/missing.py]`\n", encoding="utf-8")

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan_file = plan_dir / "01_plan.md"
    plan_file.write_text(
        "# Plan\n"
        "<required_context_rules>\n"
        "  <rule>@[.agents/rules/00-antigravity-core.md]</rule>\n"
        "</required_context_rules>\n"
        "<anti_targets></anti_targets>\n"
        "<dod_checklist></dod_checklist>\n"
        "<validation_gate></validation_gate>\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["audit_planner_output.py", "--epic", str(epic_file), "--plan-dir", str(plan_dir)],
    )
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1


def test_main_fails_on_missing_ki(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that missing KI from epic triggers exit code 1."""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text(
        "# Epic\n"
        "<required_context_rules>\n"
        "  <knowledge_item>@[ki_uninherited.md]</knowledge_item>\n"
        "</required_context_rules>\n",
        encoding="utf-8",
    )

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan_file = plan_dir / "01_plan.md"
    plan_file.write_text(
        "# Plan\n"
        "<required_context_rules>\n"
        "  <rule>@[.agents/rules/00-antigravity-core.md]</rule>\n"
        "</required_context_rules>\n"
        "<anti_targets></anti_targets>\n"
        "<dod_checklist></dod_checklist>\n"
        "<validation_gate></validation_gate>\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["audit_planner_output.py", "--epic", str(epic_file), "--plan-dir", str(plan_dir)],
    )
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1


def test_main_fails_on_missing_demolish(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that missing demolish symbols from epic triggers exit code 1."""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text(
        "# Epic\n<demolish>\n  `old_deprecated_symbol`\n</demolish>\n",
        encoding="utf-8",
    )

    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan_file = plan_dir / "01_plan.md"
    plan_file.write_text(
        "# Plan\n"
        "<required_context_rules>\n"
        "  <rule>@[.agents/rules/00-antigravity-core.md]</rule>\n"
        "</required_context_rules>\n"
        "<anti_targets></anti_targets>\n"
        "<dod_checklist></dod_checklist>\n"
        "<validation_gate></validation_gate>\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "sys.argv",
        ["audit_planner_output.py", "--epic", str(epic_file), "--plan-dir", str(plan_dir)],
    )
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1
