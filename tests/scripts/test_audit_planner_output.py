"""Tests for audit_planner_output.py."""

import pytest
import sys
from pathlib import Path
from scripts.audit_planner_output import main

def test_main_missing_epic_file():
    """Test that missing epic file exits with 1."""
    sys.argv = ["audit_planner_output.py", "--epic", "nonexistent.md", "--plan-dir", "."]
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1

def test_main_missing_plan_dir(tmp_path: Path):
    """Test that missing plan directory exits with 1."""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text("dummy")
    sys.argv = ["audit_planner_output.py", "--epic", str(epic_file), "--plan-dir", "nonexistent"]
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1

def test_main_missing_tags(tmp_path: Path):
    """Test that missing mandatory tags fails."""
    epic_file = tmp_path / "epic.md"
    epic_file.write_text("dummy")
    plan_dir = tmp_path / "plans"
    plan_dir.mkdir()
    plan_file = plan_dir / "plan.md"
    plan_file.write_text("dummy plan")
    
    sys.argv = ["audit_planner_output.py", "--epic", str(epic_file), "--plan-dir", str(plan_dir)]
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 1

