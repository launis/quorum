# Task Tracker: Standalone CLI Invocation Bug Fix in run_e2e_variance_test.py

<required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
</required_context_rules>

Implementation Plan: @[C:\Users\risto\.gemini\antigravity-ide\brain\28d0a646-ccc1-4f6b-8d6d-eaf4fc6069c3\bug_fix_plan.md]

## Pre-Flight Checklist (<constraint> tags)
- [x] Constraint: `sys_path_bootstrap_order` - Project root must be inserted into `sys.path` before any project imports in `scripts/run_e2e_variance_test.py`.
- [x] Constraint: `reflection_cleanup` - Replace `hasattr(sys.stdout, ...)` with `isinstance(sys.stdout, io.TextIOWrapper)`.
- [x] Constraint: `zero_regression_guarantee` - Standalone CLI regression test in `test_run_e2e_variance_test.py` must turn green.

## Execution Tasks

- [x] **Phase 1: Implementation & Scoped Boy Scout Cleanup**
  - [x] Step 1: In `@[scripts/run_e2e_variance_test.py#L40-L86]`, add `import io` to standard library imports and relocate `sys.path.insert(0, str(_project_root))` immediately after standard library imports, strictly preceding `backend_v2` and `scripts` imports.
  - [x] Step 2: In `@[scripts/run_e2e_variance_test.py#L81-L86]`, replace `hasattr` reflection with `isinstance(sys.stdout, io.TextIOWrapper)` and `isinstance(sys.stderr, io.TextIOWrapper)`.
  - [x] Step 3: In `@[backend_v2/tests/unit/test_run_e2e_variance_test.py#L114-L165]`, add ISTQB negative/boundary tests `test_run_e2e_variance_test_cli_isolated_cwd` and `test_run_e2e_variance_test_cli_unrecognized_argument`.

- [x] **Phase 2: Verification & Quality Gate**
  - [x] Step 4: Run regression test suite `uv run pytest backend_v2/tests/unit/test_run_e2e_variance_test.py` to verify Green phase.
  - [x] Step 5: Run CLI smoke test `uv run python scripts/run_e2e_variance_test.py --help` to verify exit code 0.
  - [x] Step 6: Run universal quality gate `uv run python scripts/backend_audit_loop.py scripts/run_e2e_variance_test.py --test`.

## Session Handover Context
- **Achieved**: Implementation and verification complete. Standalone CLI bootstrap relocated before project imports in `scripts/run_e2e_variance_test.py`; reflection cleaned with `isinstance(sys.stdout, io.TextIOWrapper)`. Standalone invocation regression test, isolated CWD test, and unrecognized argument test implemented in `backend_v2/tests/unit/test_run_e2e_variance_test.py`. All 8 tests pass 100%. Quality gate loop verified clean with exit code 0.
- **Learned**: Relocating `sys.path.insert(0, str(_project_root))` immediately after standard library imports allows direct execution of scripts from any working directory while adhering to Ruff formatting and import structure without `hasattr` reflection.
- **Remaining**: Atomic git commit and routing to `/tier8-audit-plan`.
- **Resume Command**:
  ```text
  /tier5-resume --workflow=/tier8-audit-plan --target="@[C:\Users\risto\.gemini\antigravity-ide\brain\28d0a646-ccc1-4f6b-8d6d-eaf4fc6069c3\task.md], @[C:\Users\risto\.gemini\antigravity-ide\brain\28d0a646-ccc1-4f6b-8d6d-eaf4fc6069c3\bug_fix_plan.md]" --rules="00-antigravity-core.md, 01-python-backend.md"
  ```
