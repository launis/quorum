# Tracker: Headless CLI Hardening Runner (Overnight Multi-Process Pipeline)
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_hardening_runner.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
</required_context_rules>

## Step Execution Status
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_hardening_runner.md]
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_hardening_runner.md] @[docs/implementationplans/TRACKER_auto_hardening_runner.md]`
  - [x] Step 1: Phase 1: Pre-Implementation Cleanups & 1-Hop Foundations
  - [x] Step 2: Phase 2: Domain DTOs & Argument Architecture
  - [x] Step 3: Phase 3: Queue Discovery & Execution Pipeline Implementation
  - [x] Step 4: Phase 4: Comprehensive Unit Test Suite
  - [x] Step 5: Phase 5: Quality Gate Verification
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_hardening_runner.md] @[docs/implementationplans/TRACKER_auto_hardening_runner.md]`

### Post-Implementation Gates
- [x] **[OK] Golden Master & Test Restoration Audit**: Verify zero skipped or disabled tests across the workspace.
- [x] **[OK] Tier 2 Hardening (Backend)**: Execute audit loop across modified backend files:
  - [x] [NEW] @[scripts/auto_hardening_runner.py]
- [ ] **[SKIPPED] Tier 2 Hardening (Frontend)**: No production Dart files modified in this plan.
- [x] **[OK] Pre-Delete Audit**: Verify zero dangling imports or dead code introduced by new CLI script.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Verify 100% test contract coverage across TC-AHR-001 through TC-AHR-014.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_auto_hardening_runner.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_hardening_runner.md] @[ki_deterministic_hardening_state.md] @[ki_god_code_prevention.md] @[ki_epic_lifecycle_workflow.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_deterministic_hardening_state.md]`: Document autonomous headless CLI runner `scripts/auto_hardening_runner.py` orchestrating unattended overnight hardening across isolated subagent processes with audit verification, circuit breaking, and atomic git checkpointing.
     - `@[ki_god_code_prevention.md]`: Document modular CLI script architecture reusing base infrastructure from `scripts/_script_base.py`, typed Pydantic V2 argument models, and pure tracker parsing functions.
     - `@[ki_epic_lifecycle_workflow.md]`: Document automated tracker markdown checklist discovery and in-place checkbox synchronization.
  2. **Directory Reference Sync:**
     - Register `scripts/auto_hardening_runner.py` and test suite `backend_v2/tests/unit/scripts/test_auto_hardening_runner.py` in `@[.agents/rules/04_directory_reference.md]`.
  3. **Pillar Documentation Sync:**
     - Update `docs/architecture/05_resilience_and_observability.md` documenting Windows process tree termination (`taskkill /F /T /PID`) and workspace snapshot diff rollback for unattended CLI workflows.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_hardening_runner.md] @[docs/implementationplans/TRACKER_auto_hardening_runner.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Atomic Commit Mandate**: After completing each logical step, run verification commands and perform an atomic commit using Conventional Commits (`feat(scripts): ...` or `test(scripts): ...`).
- **Markdown Boundary Verification**: At each step, ensure file references adhere to architectural standards.
- **Windows 11 PowerShell Syntax**: Exclusively use Windows PowerShell syntax; chaining with `;` and no Unix commands.
- **Zero Permissive Typing**: Enforce strict Pydantic V2 DTOs with `ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` syntax.
- **Subprocess Tree Termination**: Always kill child process trees via `taskkill /F /T /PID` on timeout before parent teardown.
- **Single Source of Truth**: All paths across workflow instructions and trackers must use POSIX forward slashes.
- **Execution Mode**: Continuous Full-Auto Mode is authorized via `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_hardening_runner.md] @[docs/implementationplans/TRACKER_auto_hardening_runner.md]`.
- **Session Handover Interval**: Trigger `/tier5-session-handover` after completing major milestones or before context budget limits are reached.

## Requirements Traceability Matrix
 
| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-AHR-001 | Pre-flight technical debt audit via `scripts/audit_technical_debt.py` verifying 1-hop foundations. | Step 1 | [x] |
| REQ-AHR-002 | Clean import of base infrastructure (`get_repo_root`, `setup_script_environment`, `ANSIColors`) without circular dependencies. | Step 1 | [x] |
| REQ-AHR-003 | Fail-fast CLI validation when neither `--tracker`, `--targets`, nor `--state-file` is specified. | Step 1 | [x] |
| REQ-AHR-004 | Module-level `__all__` export list and named timeout constants to comply with QGR008. | Step 2 | [x] |
| REQ-AHR-005 | Pydantic V2 state models enforcing strict mode, extra="forbid", and frozen=True with PEP 593 Annotated syntax. | Step 2 | [x] |
| REQ-AHR-006 | Eradication of anonymous state tuples through defining dedicated DTOs (`QualityGateResultDTO`, `CheckpointResultDTO`). | Step 2 | [x] |
| REQ-AHR-007 | Native tracker markdown discovery parsing unchecked items under backend and frontend hardening sections. | Step 3 | [x] |
| REQ-AHR-008 | In-place tracker checkbox update marking completed targets and advancing parent section status. | Step 3 | [x] |
| REQ-AHR-009 | Persistent JSON state synchronization per `ki_deterministic_hardening_state.md` (`REMAINING = TARGETS - DONE`). | Step 3 | [x] |
| REQ-AHR-010 | Windows 11 process tree termination via `taskkill /F /T /PID` upon subprocess timeout. | Step 3 | [x] |
| REQ-AHR-011 | Workspace snapshot capture and rollback diff restoration preserving `data/db_v2.json` and `hardening_state.json`. | Step 3 | [x] |
| REQ-AHR-012 | Atomic git commit checkpointing executed per verified target file strictly upon quality gate pass. | Step 3 | [x] |
| REQ-AHR-013 | Comprehensive unit test suite covering positive contracts (tracker discovery, audit passes, commit loops, batch capping). | Step 4 | [x] |
| REQ-AHR-014 | Full ISTQB negative boundary partition testing covering missing targets, nonexistent tracker, timeouts, and rollbacks. | Step 4 | [x] |
| REQ-AHR-015 | Universal Quality Gate verification proving zero Ruff errors, zero MyPy strict errors, and 100% AST guardrail compliance. | Step 5 | [x] |

# Session Handover Context
## Achieved
- Implemented autonomous headless CLI runner `@[scripts/auto_hardening_runner.py]` enforcing 100% strict Pydantic V2 DTOs, Windows 11 process tree termination (`taskkill /F /T /PID`), persistent state synchronization (`hardening_state.json`), circuit-breaker rollback, and atomic git checkpointing.
- Implemented comprehensive unit test suite `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]` covering all 14 planned test contracts TC-AHR-001 through TC-AHR-014 with 27 total tests (100% passing, 93% statement coverage).
- Passed Universal Quality Gate loops on both target files (`scripts/auto_hardening_runner.py` and `backend_v2/tests/unit/scripts/test_auto_hardening_runner.py`) with 0 Ruff errors, 0 MyPy strict errors, 0 AST violations, and 0 dict eradication findings.
- Registered `scripts/auto_hardening_runner.py` in `@[.agents/rules/04_directory_reference.md]`.
- Verified 100% plan-tracker parity and markdown boundaries.

## Learned
- Using PEP 593 `Annotated[T, Field(...)] = default` satisfies both strict MyPy model initialization and AST rule `QGR020` banning duplicate `= Field(...)` right-hand assignments.
- Windows process tree termination via `taskkill /F /T /PID` ensures child subprocesses spawned by `uv` or test runners are terminated cleanly without leaving orphaned background daemons.

## Remaining
- Final Plan Audit: `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_hardening_runner.md] @[docs/implementationplans/TRACKER_auto_hardening_runner.md]`

## Resume Command
```powershell
/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_hardening_runner.md] @[docs/implementationplans/TRACKER_auto_hardening_runner.md]
```
