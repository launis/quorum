<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

# Implementation Plan: Obsolete Scripts Eradication, Orphan Reference Sweep & CLI Help Synchronization

## Executive Summary

- **Objective:** Safely eradicate 6 obsolete/dead scripts (`migrate_seed_contrastive_pairs.py`, `convert_epic_to_hybrid.py`, `matrix_hardening_loop.py`, `matrix_hardening_generator.py`, `matrix_slice_engine.py`, `audit_matrix_auto_filler.py`) and their 5 corresponding unit test files from the repository, execute an automated AST-based scan to detect and sweep all orphaned references or dangling test fixtures from any script deleted manually or during this operation, and synchronize the CLI help inventory metatest (`test_scripts_cli_help.py`), the directory reference (`04_directory_reference.md`), and the database verification docstring (`audit_database_atoms.py`).
- **Target Scope:** 6 obsolete scripts to delete, 5 obsolete test files to delete, 1 metatest file to modify, 1 operational script to modify, 1 rule file to modify, and 1 workflow file to modify.
- **Root Cause & Rationale:**
  1. `scripts/migrate_seed_contrastive_pairs.py`: One-off seed migration script executed on Oct 7, 2026 to migrate 305 seed atoms from string to `ContrastivePairDTO`. The seed data has been 100% migrated and verified under PostgreSQL 19. The script is dead code.
  2. `scripts/convert_epic_to_hybrid.py`: One-off legacy Epic converter from Sep 25, 2026. All Epics in `docs/epic/` are now standardized hybrid documents. The script and its test `test_convert_epic_to_hybrid.py` are dead code.
  3. `scripts/matrix_hardening_loop.py`, `scripts/matrix_hardening_generator.py`, `scripts/matrix_slice_engine.py`: Legacy interactive terminal TUI tools from early October that manipulate obsolete slice files in `tmp/`. The authoritative matrix and atom quality gate has been consolidated into `scripts/audit_database_atoms.py --strict`. These 3 scripts and their corresponding 3 test files (`test_matrix_hardening_generator.py`, `test_matrix_hardening_loop.py`, `test_matrix_slice_engine.py`) are dead code.
  4. `scripts/audit_matrix_auto_filler.py`: Legacy boilerplate generator for the manual 177-rule JSON audit matrix (`audit_matrix.json`) from Epic 156. The modern `auto_hardening_runner.py` directly executes `backend_audit_loop.py --test --ast-strict` without manual JSON matrix generation. The script and its test `test_audit_matrix_auto_filler.py` are dead code.
  5. Orphan Prevention: A manual deletion of any script without synchronous inventory update breaks `test_scripts_cli_help.py` (`assert len(ALL_SCRIPTS) == 37`), leaves orphaned test files in `backend_v2/tests/unit/scripts/`, and leaves dangling references in documentation and workflows. An automated pre-flight and post-execution orphan detector ensures 100% clean repository state.

---

## Target Boundaries & Modification Inventory

| Modification Type | Target File Reference | Line Bounds | Description / Rationale |
|:---|:---|:---|:---|
| `[DELETE]` | `@[scripts/migrate_seed_contrastive_pairs.py]` | `#L1-L260` | Obsolete one-off seed contrastive pair migration script. |
| `[DELETE]` | `@[scripts/convert_epic_to_hybrid.py]` | `#L1-L503` | Obsolete one-off Epic converter script. |
| `[DELETE]` | `@[scripts/matrix_hardening_loop.py]` | `#L1-L466` | Obsolete interactive matrix hardening loop. |
| `[DELETE]` | `@[scripts/matrix_hardening_generator.py]` | `#L1-L251` | Obsolete matrix gap generator. |
| `[DELETE]` | `@[scripts/matrix_slice_engine.py]` | `#L1-L432` | Obsolete matrix slice engine. |
| `[DELETE]` | `@[scripts/audit_matrix_auto_filler.py]` | `#L1-L204` | Obsolete JSON audit matrix auto-filler utility. |
| `[DELETE]` | `@[backend_v2/tests/unit/scripts/test_convert_epic_to_hybrid.py]` | `#L1-L157` | Unit tests for deleted `convert_epic_to_hybrid.py`. |
| `[DELETE]` | `@[backend_v2/tests/unit/scripts/test_matrix_hardening_generator.py]` | `#L1-L97` | Unit tests for deleted `matrix_hardening_generator.py`. |
| `[DELETE]` | `@[backend_v2/tests/unit/scripts/test_matrix_hardening_loop.py]` | `#L1-L188` | Unit tests for deleted `matrix_hardening_loop.py`. |
| `[DELETE]` | `@[backend_v2/tests/unit/scripts/test_matrix_slice_engine.py]` | `#L1-L219` | Unit tests for deleted `matrix_slice_engine.py`. |
| `[DELETE]` | `@[backend_v2/tests/unit/scripts/test_audit_matrix_auto_filler.py]` | `#L1-L188` | Unit tests for deleted `audit_matrix_auto_filler.py`. |
| `[MODIFY]` | `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]` | - | Synchronize `ALL_SCRIPTS` list (remove 6 scripts) and update `assert len(ALL_SCRIPTS) == 31`. |
| `[MODIFY]` | `@[scripts/audit_database_atoms.py]` | - | Purge obsolete usage instructions referencing deleted `matrix_hardening_loop.py` and `matrix_hardening_generator.py`. |
| `[MODIFY]` | `@[.agents/rules/04_directory_reference.md#L118-L122]` | `#L118-L122` | Deregister deleted scripts from `<module path="scripts/">` key domains. |
| `[MODIFY]` | `@[.agents/workflows/tier2-hardening-matrix.md#L24-L62]` | `#L24-L62` | Update workflow to replace deleted `matrix_hardening_loop.py` with authoritative `audit_database_atoms.py --strict`. |

---

## Pre-Implementation Technical Debt & Orphan Audit Findings

The pre-flight scan of target files executed via `audit_technical_debt.py` reported 0 technical debt findings. However, the orphan analysis identified four systemic coupling points that must be addressed synchronously:
1. `backend_v2/tests/unit/scripts/test_scripts_cli_help.py`: Enforces an exact bi-directional inventory match (`ALL_SCRIPTS == physical_scripts`) and hard asserts `len(ALL_SCRIPTS) == 37`. Deleting 6 scripts without updating this test causes immediate test suite failure.
2. `scripts/audit_database_atoms.py`: The module docstring advertises running `matrix_hardening_loop.py` and `matrix_hardening_generator.py`. These dead references must be purged.
3. `.agents/rules/04_directory_reference.md`: Line 120 lists `migrate_seed_contrastive_pairs.py`, `matrix_slice_engine.py`, and `matrix_hardening_generator.py`. These must be removed.
4. `.agents/workflows/tier2-hardening-matrix.md`: Lines 25, 37, 38, 40, and 60 instruct running `matrix_hardening_loop.py`. These must be updated to use `audit_database_atoms.py --strict`.

---

```xml
<execution_protocol>
  <step id="1" name="PRE-FLIGHT ORPHAN AUDIT &amp; DANGLING REFERENCE SWEEP">
    <objective>Execute an automated AST and filesystem sweep to detect any orphaned test files, missing scripts, or dangling imports across backend_v2, scripts, docs, and .agents.</objective>
    <action>Execute an in-memory orphan verification scanner to verify that:
      1. Every test file in `backend_v2/tests/unit/scripts/test_*.py` maps to an existing operational script or is in the explicit deletion list.
      2. No test in `backend_v2/tests/` imports a missing script module.
      3. No operational script in `scripts/` imports a missing script module.
      4. Any script manually deleted prior to this execution is detected and its lingering artifacts reported.
    </action>
    <command>uv run python -c "
import ast, pathlib, sys

scripts_dir = pathlib.Path('scripts')
existing_scripts = {p.stem for p in scripts_dir.glob('*.py')}

planned_deletions = {
    'migrate_seed_contrastive_pairs',
    'convert_epic_to_hybrid',
    'matrix_hardening_loop',
    'matrix_hardening_generator',
    'matrix_slice_engine',
    'audit_matrix_auto_filler',
}

# 1. Check unit test files in backend_v2/tests/unit/scripts/
tests_dir = pathlib.Path('backend_v2/tests/unit/scripts')
orphaned_tests = []
for t in tests_dir.glob('test_*.py'):
    stem = t.stem[5:]
    if stem not in existing_scripts and f'_{stem}' not in existing_scripts:
        if stem not in planned_deletions and t.name not in ('test_scripts_cli_help.py', 'test_audit_verification_scripts.py', 'test_clean_imports.py', 'test_generate_openapi.py'):
            orphaned_tests.append(t.name)

# 2. Check imports across all tests
missing_imports = []
for test_path in pathlib.Path('backend_v2/tests').rglob('*.py'):
    try:
        tree = ast.parse(test_path.read_text(encoding='utf-8'))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith('scripts.'):
                sub = node.module.split('.')[1]
                if sub not in existing_scripts:
                    missing_imports.append((sub, str(test_path), node.lineno))
    except Exception:
        pass

if orphaned_tests:
    print('ERROR: Unexpected orphaned test files found:', orphaned_tests)
    sys.exit(1)
if missing_imports:
    print('ERROR: Dangling imports found in tests:', missing_imports)
    sys.exit(1)
print('Pre-flight orphan audit passed: Zero unexpected orphaned test files or dangling imports.')
"</command>
    <constraint invariant="universal_fail_fast">If the pre-flight scan identifies unexpected orphaned files or broken imports outside the planned deletion list, fail fast and inspect before proceeding.</constraint>
  </step>

  <step id="2" name="PHYSICAL SCRIPT AND DEDICATED TEST ERADICATION">
    <objective>Physically delete the 6 obsolete scripts and their 5 corresponding dedicated unit test files.</objective>
    <action>Delete the 6 obsolete scripts from `scripts/`:
      - Remove `scripts/migrate_seed_contrastive_pairs.py`
      - Remove `scripts/convert_epic_to_hybrid.py`
      - Remove `scripts/matrix_hardening_loop.py`
      - Remove `scripts/matrix_hardening_generator.py`
      - Remove `scripts/matrix_slice_engine.py`
      - Remove `scripts/audit_matrix_auto_filler.py`
    </action>
    <action>Delete the 5 dedicated unit test files from `backend_v2/tests/unit/scripts/`:
      - Remove `backend_v2/tests/unit/scripts/test_convert_epic_to_hybrid.py`
      - Remove `backend_v2/tests/unit/scripts/test_matrix_hardening_generator.py`
      - Remove `backend_v2/tests/unit/scripts/test_matrix_hardening_loop.py`
      - Remove `backend_v2/tests/unit/scripts/test_matrix_slice_engine.py`
      - Remove `backend_v2/tests/unit/scripts/test_audit_matrix_auto_filler.py`
    </action>
    <constraint invariant="explicit_scope_write">Delete exclusively the 11 targeted files. Do NOT modify or delete any other script or test file.</constraint>
  </step>

  <step id="3" name="METATEST AND CLI HELP INVENTORY SYNCHRONIZATION">
    <objective>Update backend_v2/tests/unit/scripts/test_scripts_cli_help.py to reflect the new 31-script inventory.</objective>
    <action>In `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]`:
      1. Remove `"audit_matrix_auto_filler.py"`, `"convert_epic_to_hybrid.py"`, `"matrix_hardening_generator.py"`, `"matrix_hardening_loop.py"`, `"matrix_slice_engine.py"`, and `"migrate_seed_contrastive_pairs.py"` from `ALL_SCRIPTS`.
      2. Update line 68: change `assert len(ALL_SCRIPTS) == 37` to `assert len(ALL_SCRIPTS) == 31`.
      3. Update module docstring on line 1: change `all 25 scripts` to `all 31 scripts`.
    </action>
    <action>Verify synchronization by running the CLI help metatest:
      `uv run pytest backend_v2/tests/unit/scripts/test_scripts_cli_help.py -v`
    </action>
    <constraint invariant="universal_quality_gates">test_scripts_cli_help.py MUST pass with 100% success across all 31 remaining scripts without warnings or failures.</constraint>
  </step>

  <step id="4" name="DOCUMENTATION, DIRECTORY REFERENCE &amp; WORKFLOW PURGE">
    <objective>Synchronize docstrings, directory laws, and workflow directives with the eradicated script inventory.</objective>
    <action>In `[MODIFY]` `@[scripts/audit_database_atoms.py]`:
      Remove sections `2. Matrix and Atom Hardening Loop` and `3. Automated Gap Identification and Generation` from the module docstring. Retain the authoritative `audit_database_atoms.py --strict` and `backend_v2/seed/run_seed.py local` instructions.
    </action>
    <action>In `@[.agents/rules/04_directory_reference.md#L118-L122]`:
      Remove `migrate_seed_contrastive_pairs.py`, `matrix_slice_engine.py`, and `matrix_hardening_generator.py` from the `scripts/` `<key_domains>` list.
    </action>
    <action>In `@[.agents/workflows/tier2-hardening-matrix.md#L24-L62]`:
      Update the workflow prompt:
      - Line 25: Remove `matrix_hardening_loop.py --audit-best-practice`.
      - Lines 37-40: Replace `matrix_hardening_loop.py --status`, `--audit-best-practice`, `--inspect` with `uv run python scripts/audit_database_atoms.py --strict`.
      - Line 60: Replace `matrix_hardening_loop.py --done` with running `uv run python scripts/audit_database_atoms.py --strict` to verify atom compliance.
    </action>
    <constraint invariant="documentation_present_tense_mandate">Document current operational reality in present tense without historical transition notes.</constraint>
  </step>

  <step id="5" name="POST-ERADICATION ORPHAN VERIFICATION &amp; QUALITY GATE">
    <objective>Execute the comprehensive quality gate to mathematically prove zero lingering orphans, clean imports, and 100% test passage.</objective>
    <action>Run the post-eradication orphan verification check:
      `uv run python -c "import pathlib; scripts = sorted([p.name for p in pathlib.Path('scripts').glob('*.py') if p.name != '__init__.py']); assert len(scripts) == 31, f'Expected 31 scripts, found {len(scripts)}'; print('Physical scripts count: 31 (OK)')"`
    </action>
    <action>Run all remaining unit tests in `backend_v2/tests/unit/scripts/`:
      `uv run pytest backend_v2/tests/unit/scripts/ -v`
    </action>
    <action>Run the Clean Import Analyzer:
      `uv run python scripts/audit_clean_imports.py`
    </action>
    <action>Run the 10-stage backend audit loop on scripts:
      `uv run python scripts/backend_audit_loop.py scripts/ --test --ast-strict`
    </action>
    <action>Run the markdown boundaries audit on the plan and related documents:
      `uv run python scripts/audit_markdown_boundaries.py --file docs/implementationplans/IMPLEMENTATION_PLAN_Obsolete_Scripts_Eradication_and_Orphan_Sweep.md`
    </action>
    <constraint invariant="atomic_checkpoint_mandate">Upon passing all gates, instruct the user to execute an atomic commit:
      `git add scripts/ backend_v2/tests/unit/scripts/ .agents/rules/04_directory_reference.md .agents/workflows/tier2-hardening-matrix.md docs/implementationplans/IMPLEMENTATION_PLAN_Obsolete_Scripts_Eradication_and_Orphan_Sweep.md`
      `git commit -m "chore(scripts): eradicate 6 obsolete scripts, purge orphan tests, and synchronize cli help inventory"`
    </constraint>
  </step>
</execution_protocol>
```

---

## Verification Plan & Anti-Happy-Path Scenarios

### Success Path
1. **Physical Inventory Count:** `len(scripts/*.py)` drops from 37 to exactly 31.
2. **CLI Help Metatest:** `test_scripts_cli_help.py` runs all 31 scripts with `--help` and `-h`, asserting exit code 0, non-empty usage descriptions, and sub-second execution latency.
3. **Unit Test Suite:** All 34 remaining test suites in `backend_v2/tests/unit/scripts/` pass 100%.
4. **AST Guardrails:** `backend_audit_loop.py scripts/ --test --ast-strict` passes all 10 stages with 0 violations.

### Failure / Edge Case Scenarios
1. **Scenario 1: Dangling Import in Untracked Test File**
   - *Input:* A test file attempts to `from scripts.matrix_slice_engine import detect_empirical_contamination`.
   - *Expected Behavior:* Step 1 pre-flight scanner immediately halts execution with `ERROR: Dangling imports found in tests` before any physical deletion occurs.
2. **Scenario 2: Script Count Mismatch in Metatest**
   - *Input:* `ALL_SCRIPTS` in `test_scripts_cli_help.py` has 32 scripts while physical disk has 31 (or vice versa).
   - *Expected Behavior:* `test_script_count_is_exhaustive` fails fast with `AssertionError: Mismatch in script inventory. Expected 31, got 32`.
3. **Scenario 3: Corrupted Docstring or Syntax Error in audit_database_atoms.py**
   - *Input:* Editing lines introduces indentation or unclosed string literal.
   - *Expected Behavior:* Stage 2 (Ruff) and Stage 3 (MyPy) in `backend_audit_loop.py` immediately flag syntax or formatting defects, preventing commit.

---

## Next Steps

1. **Plan Tracker Generation (Double-Entry Bookkeeping):**
   Execute `/tier1-plan-tracker-generator @[docs/implementationplans/IMPLEMENTATION_PLAN_Obsolete_Scripts_Eradication_and_Orphan_Sweep.md]` to synchronize `@[docs/implementationplans/TRACKER_Obsolete_Scripts_Eradication.md]`.
2. **Autonomous Execution:**
   Execute `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Obsolete_Scripts_Eradication_and_Orphan_Sweep.md] @[docs/implementationplans/TRACKER_Obsolete_Scripts_Eradication.md]`.
