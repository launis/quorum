# Tracker: Autonomous Headless CLI Phase Orchestrator (`scripts/auto_phase_runner.py`)
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Step Execution Status
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md]
- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md] @[docs/implementationplans/TRACKER_auto_phase_runner.md]`
  - [ ] Step 1: Define Immutable Configuration & Telemetry DTOs in scripts/auto_phase_runner.py
  - [ ] Step 2: Implement Tracker Discovery & Phase Parsing Engine
  - [ ] Step 3: Implement agy Subagent Spawner with Streaming & Tree Killing
  - [ ] Step 4: Implement Quality Gate Verification & Atomic Git Checkpointing
  - [ ] Step 5: Implement In-Place Tracker Marking & Post-Implementation Hardening Handoff
  - [ ] Step 6: CLI Argument Parser, Main Entrypoint & test_scripts_cli_help.py Registration
  - [ ] Step 7: Comprehensive Unit & Mock Verification Suite in test_auto_phase_runner.py
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md] @[docs/implementationplans/TRACKER_auto_phase_runner.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_auto_phase_runner.md] --gate backend`.
  - [ ] [NEW] @[scripts/auto_phase_runner.py]
- [ ] **[SKIPPED] Tier 2 Hardening (Frontend)**: No production Dart files modified in this plan.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update
- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_auto_phase_runner.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md] @[ki_god_code_prevention.md] @[ki_epic_lifecycle_workflow.md] @[ki_deterministic_hardening_state.md] @[ki_zero_permissive_typing.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document modular CLI script architecture in `scripts/auto_phase_runner.py` employing isolated subprocess dispatching, bounded parsing, and clean separation between phase discovery, process lifecycle, and checkpointing.
     - `@[ki_epic_lifecycle_workflow.md]`: Document autonomous headless multi-phase orchestration across Epic trackers (`docs/epic/EPIC_XXX_tracker.md`, `*_decomposition_tracker.md`) and Standalone plan trackers (`docs/implementationplans/TRACKER_*.md`) via isolated `agy` CLI subagent processes with `--model gemini-4-argon-high`.
     - `@[ki_deterministic_hardening_state.md]`: Document seamless handoff from multi-phase execution to `scripts/auto_hardening_runner.py` for post-implementation hardening upon completion of all phases.
     - `@[ki_zero_permissive_typing.md]`: Document immutable Pydantic V2 DTOs (`PhaseItemDTO`, `AutoPhaseRunnerArgsDTO`, `PhaseExecutionResultDTO`, `AutoPhaseRunSummaryDTO`) enforcing strict mode, extra="forbid", frozen=True, and PEP 593 Annotated syntax with zero naked dicts or state tuples.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register newly created `scripts/auto_phase_runner.py` and test suite `backend_v2/tests/unit/scripts/test_auto_phase_runner.py`.
  3. **Pillar Documentation Sync:**
     - Update `docs/architecture/05_resilience_and_observability.md` documenting Windows process tree termination (`taskkill /F /T /PID`), subagent execution timeouts, streaming thought telemetry, and automated rollback/circuit breaking for unattended multi-phase CLI workflows.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md] @[docs/implementationplans/TRACKER_auto_phase_runner.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Atomic Commit Mandate**: After completing each logical step, run verification commands and perform an atomic commit using Conventional Commits (`feat(scripts): ...` or `test(scripts): ...`).
- **Markdown Boundary Verification**: At each step, ensure file references adhere to architectural standards.
- **Windows 11 PowerShell Syntax**: Exclusively use Windows PowerShell syntax; chaining with `;` and no Unix commands.
- **Zero Permissive Typing**: Enforce strict Pydantic V2 DTOs with `ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` syntax.
- **Subprocess Tree Termination**: Always terminate child process trees via `taskkill /F /T /PID` on timeout or cancellation before parent teardown.
- **Single Source of Truth**: All paths across workflow instructions and trackers must use POSIX forward slashes.
- **Execution Mode**: Continuous Full-Auto Mode is authorized via `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md] @[docs/implementationplans/TRACKER_auto_phase_runner.md]`.
- **Post-Implementation Hardening**: Execute `/tier2-hardening-backend` in chat or unattended via `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_auto_phase_runner.md] --gate backend`.
- **Session Handover Interval**: Trigger `/tier5-session-handover` after completing major milestones or before context budget limits are reached.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-APR-001 | Define immutable Pydantic V2 DTOs (`PhaseItemDTO`, `AutoPhaseRunnerArgsDTO`, `PhaseExecutionResultDTO`, `AutoPhaseRunSummaryDTO`) with strict mode, extra="forbid", frozen=True, and PEP 593 Annotated syntax. | Step 1 | [ ] |
| REQ-APR-002 | Implement tracker markdown discovery and parsing engine supporting both multi-phase Epic and single-phase Standalone Plan topologies. | Step 2 | [ ] |
| REQ-APR-003 | Fail-fast validation verifying referenced implementation plans physically exist on disk before execution starts. | Step 2 | [ ] |
| REQ-APR-004 | Antigravity CLI binary resolution checking `PATH`, user AppData, and standard installation directories. | Step 3 | [ ] |
| REQ-APR-005 | Headless `agy` subprocess spawner with live console output streaming, continuous full-auto permission framing, and Windows tree termination (`taskkill /F /T /PID`). | Step 3 | [ ] |
| REQ-APR-006 | Universal Quality Gate verification via `backend_audit_loop.py` failing fast on regressions before checkpointing. | Step 4 | [ ] |
| REQ-APR-007 | Atomic git checkpointing committing completed phases with Conventional Commits syntax and dirty file staging. | Step 4 | [ ] |
| REQ-APR-008 | In-place tracker markdown update marking completed phase and execution item checkboxes (`[x]`). | Step 5 | [ ] |
| REQ-APR-009 | Post-implementation hardening handoff executing `scripts/auto_hardening_runner.py` upon pipeline completion (supporting `--hardening-agent` and `--hardening-model`). | Step 5 | [ ] |
| REQ-APR-010 | CLI argument parser supporting standard flags (`--tracker`, `--model`, `--from-phase`, `--only-phase`, `--skip-commit`, `--skip-hardening`, `--hardening-agent`, `--hardening-model`, `--timeout`, `--dry-run`). | Step 6 | [ ] |
| REQ-APR-011 | Global CLI help inventory registration in `backend_v2/tests/unit/scripts/test_scripts_cli_help.py` updating script count from 35 to 36. | Step 6 | [ ] |
| REQ-APR-012 | Comprehensive unit test suite in `test_auto_phase_runner.py` covering parsing, dry-run, circuit breaking, quality gate rejection, and subagent spawning with mocks. | Step 7 | [ ] |

# Session Handover Context
## Achieved
- Formulated, hardened, and verified architectural implementation plan `@[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md]` with 0 fatal boundary errors via `/tier0-research-plan`.
- Executed Five-Axis System 2 Deconstruction and codified the 7-row Architectural Directives Table with 100% Table-Protocol bidirectional parity (`audit_markdown_boundaries.py` -> 0 findings).
- Hardened subprocess spawner with thread-safe watchdog timer (`threading.Timer`) and Windows tree termination (`taskkill /F /T /PID`) to prevent pipe-reading deadlock during hung CLI processes.
- Hardened console telemetry streaming to gracefully handle Windows console codepages with `UnicodeEncodeError` fallback to raw byte buffer writes.
- Hardened tracker parsing engine to support optional commit hashes preceding execution markers or trailing commands, and strip enclosing backticks and commit hashes from extracted slash commands.
- Hardened in-place tracker completion marker formatting to `- [x] **[OK] Execution: <command> (`{short_hash}`)` to strictly comply with `scripts/audit_tracker_output.py` rule TRK002.
- Specified clean working tree detection during checkpointing to prevent false-failure crashes when subagents commit intermediate steps.
- Expanded unit test matrix in `test_auto_phase_runner.py` from 13 to 15 tests, adding `--from-phase` and `--only-phase` filtering tests.
- Completed pre-implementation technical debt audit via `scripts/audit_technical_debt.py` confirming 0 debt items in `test_scripts_cli_help.py`.
- Synchronized double-entry bookkeeping plan tracker `@[docs/implementationplans/TRACKER_auto_phase_runner.md]` with 100% plan-tracker parity (`audit_tracker_output.py` -> PASSED).

## Learned
- Subagent processes spawned via `agy -i` require explicit full-auto authorization framing in the initial instruction prompt to proceed autonomously through multi-step workflows without interactive prompts, but existing prompt text in trackers must be checked first to avoid duplicate authorization sentences.
- Reading child process stdout synchronously via `proc.stdout.readline` can block indefinitely if a child process deadlocks without generating output; launching an asynchronous watchdog `threading.Timer` to kill the process tree ensures deterministic timeout handling and breaks pipe reads with clean EOF.
- Windows console code pages (such as cp1252) can raise `UnicodeEncodeError` when printing Unicode thought emojis from `agy`; catching `UnicodeEncodeError` and writing to `sys.stdout.buffer` guarantees zero crash risk.
- Real-world tracker documents record git commit hashes either preceding markers (`- [x] (hash) **[OK]`) or trailing commands (`` - [x] **[OK] Execution: `cmd` (`hash`) ``); placing the hash before `**[OK]` triggers TRK002 errors in `audit_tracker_output.py`, so completion writing must strictly format `- [x] **[OK] Execution: <command> (`{hash}`)`.
- Autonomous execution agents commit code per step; checkpoint handlers must check `git status --porcelain` to gracefully handle already-clean working trees without throwing git exit code 1 errors.
- `scripts/audit_markdown_boundaries.py` rule MBD004 requires AST line bounds to correspond to exact `ClassDef` or `FunctionDef` AST node spans; referencing module-level assignments fails MBD004.
- In planning markdown documents, literal `@[...]` bracket syntax is strictly reserved for physical existing files; template or interpolated variables must use alternative delimiters like `@<...>` to avoid MBD003 non-existent file validation errors.

## Remaining
- Execute autonomous implementation of Steps 1 through 7 via `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md] @[docs/implementationplans/TRACKER_auto_phase_runner.md]`.
- Execute post-implementation hardening loop via `uv run python scripts/auto_hardening_runner.py --tracker @[docs/implementationplans/TRACKER_auto_phase_runner.md] --gate backend`.
- Execute Red-Team audit via `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md] @[docs/implementationplans/TRACKER_auto_phase_runner.md]`.
- Execute As-Built Architectural Sync via `/tier7-describe-architecture`.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_auto_phase_runner.md] @[docs/implementationplans/TRACKER_auto_phase_runner.md]
```

