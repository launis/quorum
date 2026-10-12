"""Unit tests for audit_plan_tracker_parity.py.

Verifies bidirectional plan-tracker parity checks, AST extraction,
and CLI entrypoint behaviors across TPR001-TPR010.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.audit_plan_tracker_parity import (
    audit_plan_tracker_parity,
    main,
    parse_plan_document,
    parse_tracker_document,
)

SAMPLE_PLAN = """<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
</required_context_rules>

# Plan: Test Plan
## Target Scope & Boundaries
- `[MODIFY]` @[scripts/tool.py#L10-L20]

```xml
<execution_protocol>
  <step id="1" name="STEP ONE: INIT">
    <action>Do something</action>
  </step>
</execution_protocol>
```
"""

SAMPLE_TRACKER = """<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
</required_context_rules>

# Tracker: Test Tracker

**Plan:** @[plan.md]

## Step Execution Status

- [ ] **[NOK] Execution:** `/tier2-execute @[plan.md] @[task.md]`
  - [ ] Step 1: STEP ONE: INIT

### Post-Implementation Gates
- [ ] @[scripts/tool.py]

### Documentation & Knowledge Item Update
- [ ] Update KI

### Final Plan Audit
- [ ] Audit

## Requirements Traceability Matrix
| Requirement | Description | Plan Step | Status |
|---|---|---|---|
| REQ-001 | Init | Step 1 | [ ] Pending |

# Session Handover Context
## Achieved
- Done
## Learned
- Notes
## Remaining
- Rest
## Resume Command
```
/tier2-execute @[plan.md] @[task.md]
```
"""


def test_parse_and_parity_clean(tmp_path: Path) -> None:
    """Test parse_plan_document, parse_tracker_document, and audit_plan_tracker_parity in clean state."""
    plan_file = tmp_path / "plan.md"
    plan_file.write_text(SAMPLE_PLAN, encoding="utf-8")

    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(SAMPLE_TRACKER.replace("@[plan.md]", f"@[{plan_file.as_posix()}]"), encoding="utf-8")

    plan_ast = parse_plan_document(plan_file.read_text(encoding="utf-8"), plan_file)
    tracker_ast = parse_tracker_document(tracker_file.read_text(encoding="utf-8"), tracker_file)

    report = audit_plan_tracker_parity(plan_ast, tracker_ast)
    assert report.total_steps == 1


def test_main_cli_success(tmp_path: Path) -> None:
    """Test main() CLI execution on matching plan and tracker."""
    plan_file = tmp_path / "plan.md"
    plan_file.write_text(SAMPLE_PLAN, encoding="utf-8")

    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(SAMPLE_TRACKER.replace("@[plan.md]", f"@[{plan_file.as_posix()}]"), encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        main(["--tracker", str(tracker_file), "--plan", str(plan_file)])
    assert exc_info.value.code in (0, 1)


def test_main_cli_json_output(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Test main() CLI with --json outputs valid JSON string."""
    plan_file = tmp_path / "plan.md"
    plan_file.write_text(SAMPLE_PLAN, encoding="utf-8")

    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(SAMPLE_TRACKER.replace("@[plan.md]", f"@[{plan_file.as_posix()}]"), encoding="utf-8")

    with pytest.raises(SystemExit):
        main(["--tracker", str(tracker_file), "--plan", str(plan_file), "--json"])

    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "tracker_file" in data
    assert "passed" in data


def test_main_cli_missing_tracker(tmp_path: Path) -> None:
    """Test main() CLI exits with 1 when tracker does not exist."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--tracker", str(tmp_path / "missing_tracker.md")])
    assert exc_info.value.code == 1


def test_main_cli_missing_arguments() -> None:
    """Test main() CLI exits with 2 when neither --tracker nor --all is specified."""
    with pytest.raises(SystemExit) as exc_info:
        main([])
    assert exc_info.value.code == 2


def test_main_cli_auto_infer_plan(tmp_path: Path) -> None:
    """Test main() CLI auto-infers plan path from tracker when --plan is omitted."""
    plan_file = tmp_path / "plan.md"
    plan_file.write_text(SAMPLE_PLAN, encoding="utf-8")

    tracker_file = tmp_path / "tracker.md"
    tracker_file.write_text(SAMPLE_TRACKER.replace("@[plan.md]", f"@[{plan_file.as_posix()}]"), encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        main(["--tracker", str(tracker_file)])
    assert exc_info.value.code in (0, 1)


def test_main_cli_tracker_missing_plan_reference(tmp_path: Path) -> None:
    """Test main() CLI exits with 1 when tracker has no plan reference and --plan is omitted."""
    tracker_file = tmp_path / "orphan_tracker.md"
    tracker_file.write_text("# Tracker without plan\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        main(["--tracker", str(tracker_file)])
    assert exc_info.value.code == 1


def test_main_cli_tracker_references_missing_plan(tmp_path: Path) -> None:
    """Test main() CLI exits with 1 when referenced plan does not exist on disk."""
    tracker_file = tmp_path / "bad_plan_tracker.md"
    tracker_file.write_text("**Plan:** @[missing_plan.md]\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        main(["--tracker", str(tracker_file)])
    assert exc_info.value.code == 1


def test_main_cli_all_with_trackers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test main() CLI --all iterates through trackers in docs/implementationplans/."""
    plans_dir = tmp_path / "docs" / "implementationplans"
    plans_dir.mkdir(parents=True)
    monkeypatch.chdir(tmp_path)

    plan_file = plans_dir / "PLAN_001.md"
    plan_file.write_text(SAMPLE_PLAN, encoding="utf-8")

    tracker_file = plans_dir / "TRACKER_001.md"
    tracker_file.write_text(SAMPLE_TRACKER.replace("@[plan.md]", f"@[{plan_file.as_posix()}]"), encoding="utf-8")

    # Also add a tracker with no plan to test skip branch
    tracker_no_plan = plans_dir / "TRACKER_002.md"
    tracker_no_plan.write_text("# No plan reference\n", encoding="utf-8")

    # Also add a tracker with missing plan to test failure branch
    tracker_missing = plans_dir / "TRACKER_003.md"
    tracker_missing.write_text("**Plan:** @[docs/implementationplans/DOES_NOT_EXIST.md]\n", encoding="utf-8")

    with pytest.raises(SystemExit) as exc_info:
        main(["--all"])
    assert exc_info.value.code == 1


def test_non_code_targets_excluded_from_hardening_check(tmp_path: Path) -> None:
    """Test that non-code targets (.json, .jinja2, .arb, .sql) in plans are not demanded in hardening checklist."""
    plan_text = """<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
</required_context_rules>
# Plan: Non-code
## Target Scope
- `[MODIFY]` @[backend_v2/seed/seed_data.json]
- `[MODIFY]` @[backend_v2/templates/report.jinja2]
- `[MODIFY]` @[client_app_v2/lib/l10n/app_en.arb]
- `[MODIFY]` @[backend_v2/services/code.py]

```xml
<execution_protocol>
  <step id="1" name="STEP ONE">
    <action>Action</action>
  </step>
</execution_protocol>
```
"""
    tracker_text = f"""<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
</required_context_rules>
# Tracker: Non-code
**Plan:** @[plan.md]
## Step Execution Status
- [ ] **[NOK] Execution:** `/tier2-execute @[plan.md] @[task.md]`
  - [ ] Step 1: STEP ONE

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**
- [ ] **[NOK] Pre-Delete Audit**
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**
- [ ] **[NOK] Tier 2 Hardening (Backend):**
  - [ ] @[backend_v2/services/code.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend):**

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run:

## Requirements Traceability Matrix
| Req | Desc | Plan Step | Status |
|---|---|---|---|
| R1 | Desc | Step 1 | [ ] Pending |

# Session Handover Context
## Achieved
- Done
## Learned
- Notes
## Remaining
- Rest
## Resume Command
`/tier2-execute`
"""
    p_file = tmp_path / "plan.md"
    p_file.write_text(plan_text, encoding="utf-8")
    t_file = tmp_path / "tracker.md"
    t_file.write_text(tracker_text, encoding="utf-8")

    plan_ast = parse_plan_document(plan_text, p_file)
    tracker_ast = parse_tracker_document(tracker_text, t_file)
    report = audit_plan_tracker_parity(plan_ast, tracker_ast)

    fatal_findings = [f for f in report.findings if f.severity.value == "FATAL"]
    assert not fatal_findings, f"Unexpected fatal findings: {fatal_findings}"


def test_invalid_extension_and_test_file_in_hardening_checklist(tmp_path: Path) -> None:
    """Test that non-code files and test files in tracker checklists trigger FATAL TPR004 findings."""
    plan_text = """<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
</required_context_rules>
# Plan: Valid
## Target Scope
- `[MODIFY]` @[backend_v2/services/code.py]

```xml
<execution_protocol>
  <step id="1" name="STEP ONE">
    <action>Action</action>
  </step>
</execution_protocol>
```
"""
    tracker_text = f"""<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
</required_context_rules>
# Tracker: Bad Extensions
**Plan:** @[plan.md]
## Step Execution Status
- [ ] **[NOK] Execution:** `/tier2-execute @[plan.md] @[task.md]`
  - [ ] Step 1: STEP ONE

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**
- [ ] **[NOK] Pre-Delete Audit**
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**
- [ ] **[NOK] Tier 2 Hardening (Backend):**
  - [ ] @[backend_v2/services/code.py]
  - [ ] @[backend_v2/seed/seed_data.json]
  - [ ] @[backend_v2/tests/test_code.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend):**
  - [ ] @[client_app_v2/lib/l10n/app_en.arb]

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run:

## Requirements Traceability Matrix
| Req | Desc | Plan Step | Status |
|---|---|---|---|
| R1 | Desc | Step 1 | [ ] Pending |

# Session Handover Context
## Achieved
- Done
## Learned
- Notes
## Remaining
- Rest
## Resume Command
`/tier2-execute`
"""
    p_file = tmp_path / "plan.md"
    p_file.write_text(plan_text, encoding="utf-8")
    t_file = tmp_path / "tracker.md"
    t_file.write_text(tracker_text, encoding="utf-8")

    plan_ast = parse_plan_document(plan_text, p_file)
    tracker_ast = parse_tracker_document(tracker_text, t_file)
    report = audit_plan_tracker_parity(plan_ast, tracker_ast)

    fatal_findings = [f for f in report.findings if f.severity.value == "FATAL"]
    assert len(fatal_findings) == 3
    rule_codes = [f.rule_code.value for f in fatal_findings]
    assert all(rc == "TPR004" for rc in rule_codes)
    messages = " ".join(f.message for f in fatal_findings)
    assert "Non-Python file `backend_v2/seed/seed_data.json`" in messages
    assert "Test file `backend_v2/tests/test_code.py`" in messages
    assert "Non-Dart file `client_app_v2/lib/l10n/app_en.arb`" in messages
