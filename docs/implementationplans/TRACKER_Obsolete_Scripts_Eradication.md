# Tracker: Obsolete Scripts Eradication, Orphan Reference Sweep & CLI Help Synchronization

@[docs/implementationplans/IMPLEMENTATION_PLAN_Obsolete_Scripts_Eradication_and_Orphan_Sweep.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Obsolete_Scripts_Eradication_and_Orphan_Sweep.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Obsolete_Scripts_Eradication_and_Orphan_Sweep.md] @[docs/implementationplans/TRACKER_Obsolete_Scripts_Eradication.md]`
  - [x] Step 1: PRE-FLIGHT ORPHAN AUDIT & DANGLING REFERENCE SWEEP (VERIFIED_EXISTING)
  - [x] Step 2: PHYSICAL SCRIPT AND DEDICATED TEST ERADICATION (VERIFIED_EXISTING)
  - [x] Step 3: METATEST AND CLI HELP INVENTORY SYNCHRONIZATION (VERIFIED_EXISTING)
  - [x] Step 4: DOCUMENTATION, DIRECTORY REFERENCE & WORKFLOW PURGE (VERIFIED_EXISTING)
  - [x] Step 5: POST-ERADICATION ORPHAN VERIFICATION & QUALITY GATE (VERIFIED_EXISTING)
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Obsolete_Scripts_Eradication_and_Orphan_Sweep.md] @[docs/implementationplans/TRACKER_Obsolete_Scripts_Eradication.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Obsolete_Scripts_Eradication.md]" --gate backend --model gemini-4-argon-medium`
  - [ ] @[scripts/audit_database_atoms.py]
- [x] **[SKIPPED] Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Obsolete_Scripts_Eradication.md]" --gate frontend --model gemini-4-argon-medium` (Zero production frontend `.dart` files modified in this plan).
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain across `backend_v2/`, `scripts/`, `docs/`, and `.agents/`.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic and 100% pass rate across all 31 scripts in `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]`.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Obsolete_Scripts_Eradication.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Obsolete_Scripts_Eradication_and_Orphan_Sweep.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document the permanent eradication of obsolete one-off migration and terminal slice utilities (`migrate_seed_contrastive_pairs.py`, `convert_epic_to_hybrid.py`, `matrix_hardening_loop.py`, `matrix_hardening_generator.py`, `matrix_slice_engine.py`, `audit_matrix_auto_filler.py`), consolidation of matrix and atom verification into `@[scripts/audit_database_atoms.py]`, and enforcement of the 31-script inventory in `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` under `<module path="scripts/">` to deregister deleted scripts (`migrate_seed_contrastive_pairs.py`, `matrix_slice_engine.py`, `matrix_hardening_generator.py`) from `<key_domains>`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `@[docs/architecture/00_README_META_ARCHITECTURE.md]` and `@[docs/architecture/05_resilience_and_observability.md]` describing the 31-script automated quality gate and `@[scripts/audit_database_atoms.py]` verification pipeline in present tense without historical language or plan IDs.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Obsolete_Scripts_Eradication_and_Orphan_Sweep.md] @[docs/implementationplans/TRACKER_Obsolete_Scripts_Eradication.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing all verification gates, instruct the user to perform an atomic `git commit` using Conventional Commits syntax (`chore(scripts): eradicate 6 obsolete scripts, purge orphan tests, and synchronize cli help inventory`) with explicit file paths in `git add`.
- **Universal Quality Gate Loops**: Run `uv run python scripts/backend_audit_loop.py scripts/ --test --ast-strict`, `uv run python scripts/audit_clean_imports.py`, and `uv run pytest backend_v2/tests/unit/scripts/ -v` to verify 100% compliance.
- **Workspace-Relative `@-Reference` Syntax**: Normalize all file references to workspace-relative POSIX paths (`@[scripts/...]`, `@[backend_v2/...]`). Never use hardcoded local absolute paths.
- **Windows 11 PowerShell Syntax**: Exclusively use Windows PowerShell syntax; chain commands with `;` and use `Remove-Item` instead of Unix commands.
- **Execution Mode**: Step-by-Step mode halts after each step by default; Continuous Full-Auto Mode is authorized when invoked via `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Obsolete_Scripts_Eradication_and_Orphan_Sweep.md] @[docs/implementationplans/TRACKER_Obsolete_Scripts_Eradication.md]`.
- **Session Handover Rules**: Proactively trigger `/tier5-session-handover` if processing >8 user prompts, completing 3 atomic commits, or modifying >5 complex files.
- **Post-Implementation Hardening Execution Options**: Execute hardening either interactively in chat via `/tier2-hardening-backend @[scripts/audit_database_atoms.py]` or autonomously via `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Obsolete_Scripts_Eradication.md]" --gate backend --model gemini-4-argon-medium`.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Execute pre-flight AST and filesystem orphan scanner verifying that every `backend_v2/tests/unit/scripts/test_*.py` maps to an active script or planned deletion and no test or script imports a missing module. | Step 1 | [x] |
| REQ-002 | Physically delete obsolete seed contrastive pair migration script `scripts/migrate_seed_contrastive_pairs.py`. | Step 2 | [x] |
| REQ-003 | Physically delete obsolete Epic converter script `scripts/convert_epic_to_hybrid.py` and its dedicated unit test `backend_v2/tests/unit/scripts/test_convert_epic_to_hybrid.py`. | Step 2 | [x] |
| REQ-004 | Physically delete obsolete matrix TUI hardening scripts (`scripts/matrix_hardening_loop.py`, `scripts/matrix_hardening_generator.py`, `scripts/matrix_slice_engine.py`) and their dedicated unit tests (`backend_v2/tests/unit/scripts/test_matrix_hardening_loop.py`, `backend_v2/tests/unit/scripts/test_matrix_hardening_generator.py`, `backend_v2/tests/unit/scripts/test_matrix_slice_engine.py`). | Step 2 | [x] |
| REQ-005 | Physically delete obsolete JSON audit matrix auto-filler `scripts/audit_matrix_auto_filler.py` and its dedicated unit test `backend_v2/tests/unit/scripts/test_audit_matrix_auto_filler.py`. | Step 2 | [x] |
| REQ-006 | Remove the 6 eradicated script filenames from `ALL_SCRIPTS` in `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]`. | Step 3 | [x] |
| REQ-007 | Update script count assertion in `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]` from `assert len(ALL_SCRIPTS) == 37` to `assert len(ALL_SCRIPTS) == 31`, update module docstring to `all 31 scripts`, and verify 100% metatest pass rate. | Step 3 | [x] |
| REQ-008 | Purge obsolete docstring sections (`2. Matrix and Atom Hardening Loop` and `3. Automated Gap Identification and Generation`) referencing deleted scripts from `@[scripts/audit_database_atoms.py]`. | Step 4 | [x] |
| REQ-009 | Deregister `migrate_seed_contrastive_pairs.py`, `matrix_slice_engine.py`, and `matrix_hardening_generator.py` from `<module path="scripts/">` in `@[.agents/rules/04_directory_reference.md]`. | Step 4 | [x] |
| REQ-010 | Update `@[.agents/workflows/tier2-hardening-matrix.md]` to replace obsolete `matrix_hardening_loop.py` invocations with `uv run python scripts/audit_database_atoms.py --strict`. | Step 4 | [x] |
| REQ-011 | Execute post-eradication verification gates: assert physical script count equals 31, run `pytest backend_v2/tests/unit/scripts/ -v`, `audit_clean_imports.py`, `backend_audit_loop.py scripts/ --test --ast-strict`, and `audit_markdown_boundaries.py`. | Step 5 | [x] |

# Session Handover Context
## Achieved
- Verified Step 1 pre-flight AST and filesystem orphan scan confirming zero unexpected orphaned test files or dangling imports across `backend_v2/` and `scripts/`.
- Verified Step 2 physical eradication of 6 obsolete scripts (`scripts/migrate_seed_contrastive_pairs.py`, `scripts/convert_epic_to_hybrid.py`, `scripts/matrix_hardening_loop.py`, `scripts/matrix_hardening_generator.py`, `scripts/matrix_slice_engine.py`, `scripts/audit_matrix_auto_filler.py`) and 5 dedicated unit test files (`test_convert_epic_to_hybrid.py`, `test_matrix_hardening_generator.py`, `test_matrix_hardening_loop.py`, `test_matrix_slice_engine.py`, `test_audit_matrix_auto_filler.py`).
- Verified Step 3 CLI help inventory synchronization in `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py]` across all 31 remaining operational scripts.
- Verified Step 4 documentation, directory reference, and workflow purge across `@[scripts/audit_database_atoms.py]`, `@[.agents/rules/04_directory_reference.md]`, and `@[.agents/workflows/tier2-hardening-matrix.md]`.
- Verified Step 5 post-eradication quality gates (`test_scripts_cli_help.py`, `backend_v2/tests/unit/scripts/`, `audit_clean_imports.py`, `backend_audit_loop.py scripts/ --test --ast-strict`, and `audit_markdown_boundaries.py`).

## Learned
- All 6 obsolete scripts were isolated utilities with zero active imports in `backend_v2/` or surviving `scripts/`, reducing the operational script inventory from 37 to 31 scripts while preserving 100% CLI help and AST guardrail compliance.

## Remaining
- Execute Post-Implementation Hardening on `@[scripts/audit_database_atoms.py]`, Documentation & Knowledge Item Update (`/tier7-describe-architecture`), and System 2 Red-Team Plan Audit (`/tier8-audit-plan`).

## Resume Command
```powershell
/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Obsolete_Scripts_Eradication_and_Orphan_Sweep.md] @[docs/implementationplans/TRACKER_Obsolete_Scripts_Eradication.md]
```
