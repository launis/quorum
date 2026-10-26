# Tracker: Autonomous Hardening Pipeline & Audit Loop Performance Optimization
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_Pipeline_Optimization.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
</required_context_rules>

## Step Execution Status
**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_Pipeline_Optimization.md]
- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_Pipeline_Optimization.md] @[docs/implementationplans/TRACKER_Hardening_Pipeline_Optimization.md]`
  - [x] Step 1: Add Micro-Audit Mode to backend_audit_loop.py
  - [x] Step 2: Add Model Selection and Two-Tier Auditing to auto_hardening_runner.py
  - [x] Step 3: Make Tracker Target Parsing Resilient to Backticks and Quoting
  - [x] Step 4: Expand Unit Test Suites in test_auto_hardening_runner.py and test_backend_audit_loop.py
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_Pipeline_Optimization.md] @[docs/implementationplans/TRACKER_Hardening_Pipeline_Optimization.md]`

### Post-Implementation Gates
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Verify zero skipped or disabled tests across the workspace.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Execute audit loop across modified backend files:
  - [ ] @[scripts/auto_hardening_runner.py]
  - [ ] @[scripts/backend_audit_loop.py]
- [ ] **[SKIPPED] Tier 2 Hardening (Frontend)**: No production Dart files modified in this plan.
- [ ] **[NOK] Pre-Delete Audit**: Verify zero dangling imports or dead code introduced by audit optimizations.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Verify 100% test contract coverage across performance and resilience scenarios.

### Documentation & Knowledge Item Update
- [x] **[OK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Hardening_Pipeline_Optimization.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_Pipeline_Optimization.md] @[ki_deterministic_hardening_state.md] @[ki_epic_lifecycle_workflow.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_deterministic_hardening_state.md]`: Document Two-Tier quality gate architecture (micro-audit for per-target iterations vs macro-audit for queue completion) and configurable AI models (`--model`, defaulting to `gemini-4-argon-medium`) for autonomous subagents.
     - `@[ki_epic_lifecycle_workflow.md]`: Document resilient tracker checklist parsing tolerating backtick enclosed tags and target paths.
  2. **Directory Reference Sync:**
     - Verify `scripts/auto_hardening_runner.py` and `scripts/backend_audit_loop.py` CLI argument options are accurately reflected in `@[.agents/rules/04_directory_reference.md]`.
  3. **Pillar Documentation Sync:**
     - Update `docs/architecture/05_resilience_and_observability.md` documenting Two-Tier Audit Loop optimization and Logfire telemetry suppression during local batch test execution.

### Final Plan Audit
- [ ] **[NOK]** System 2 Red-Team Audit: Verify all requirements and Quorum 2026 invariants physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent
- **Atomic Commit Mandate**: After completing each logical step, run verification commands and perform an atomic commit using Conventional Commits (`feat(scripts): ...` or `test(scripts): ...`).
- **Markdown Boundary Verification**: At each step, ensure file references adhere to architectural standards.
- **Windows 11 PowerShell Syntax**: Exclusively use Windows PowerShell syntax; chaining with `;` and no Unix commands.
- **Zero Permissive Typing**: Enforce strict Pydantic V2 DTOs with `ConfigDict(strict=True, extra="forbid", frozen=True)` and PEP 593 `Annotated` syntax.
- **Two-Tier Quality Gate Law**: Micro-audit mode executes Stages 1-4 + unit tests; Macro-audit executes Stages 1-10 across all processed targets at queue conclusion.
- **Single Source of Truth**: All paths across workflow instructions and trackers must use POSIX forward slashes.
- **Execution Mode**: Continuous Full-Auto Mode is authorized via `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Hardening_Pipeline_Optimization.md] @[docs/implementationplans/TRACKER_Hardening_Pipeline_Optimization.md]`.
- **Session Handover Interval**: Trigger `/tier5-session-handover` after completing major milestones or before context budget limits are reached.

## Requirements Traceability Matrix
 
| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-OPT-001 | Add `--micro` / `--fast` flag to `scripts/backend_audit_loop.py` executing Stages 1-4 and localized tests. | Step 1 | [x] |
| REQ-OPT-002 | Defer repository-wide scans (Stages 5-10) in `scripts/backend_audit_loop.py` when `--micro` is active. | Step 1 | [x] |
| REQ-OPT-003 | Pass `--no-logfire` in micro-audit mode to eliminate network telemetry latency during automated batch execution. | Step 1 | [x] |
| REQ-OPT-004 | Update `DEFAULT_BACKEND_AGENT_TEMPLATE` with configurable `{model}` token defaulting to `gemini-4-argon-medium`. | Step 2 | [x] |
| REQ-OPT-005 | Extend HardeningRunnerArgsDTO with model and micro_audit attributes with strict validation. | Step 2 | [x] |
| REQ-OPT-006 | Dispatch `--micro` quality gate during per-target iterations in `scripts/auto_hardening_runner.py`. | Step 2 | [x] |
| REQ-OPT-007 | Execute universal macro-audit once across all processed targets at completion of hardening queue. | Step 2 | [x] |
| REQ-OPT-008 | Make `parse_tracker_unhardened_targets` resilient to backticks enclosing `[NEW]` tags and paths. | Step 3 | [x] |
| REQ-OPT-009 | Make `mark_tracker_target_done` resilient to backticks enclosing `[NEW]` tags and paths. | Step 3 | [x] |
| REQ-OPT-010 | Add comprehensive unit tests in `backend_v2/tests/unit/scripts/test_auto_hardening_runner.py` and `backend_v2/tests/unit/scripts/test_backend_audit_loop.py`. | Step 4 | [x] |

# Session Handover Context
## Achieved
- Implemented Step 1 in `@[scripts/backend_audit_loop.py]`: added `--micro` (`--fast`) flag, deferred Stages 5–10 during micro-audits, and set `--logfire` `default=None` so `--micro` automatically disables Logfire network telemetry unless `--logfire` is explicitly passed.
- Implemented Step 2 in `@[scripts/auto_hardening_runner.py]`: parameterized `DEFAULT_BACKEND_AGENT_TEMPLATE` and `DEFAULT_FRONTEND_AGENT_TEMPLATE` with `--model {model}` (defaulting to `gemini-4-argon-medium`), extended runner CLI arguments DTO (`model` and `micro_audit`), updated `run_quality_gate(..., micro_audit=args.micro_audit)`, added `run_macro_quality_gate` completion gate at the end of `run_hardening_pipeline`, and exposed `--model` and `--no-micro` CLI flags.
- Implemented Step 3 in `@[scripts/auto_hardening_runner.py]`: updated regex patterns in `parse_tracker_unhardened_targets` and `mark_tracker_target_done` to tolerate optional backticks wrapping `[NEW|MODIFY|DELETE]` tags and target references.
- Implemented Step 4 in `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]` and `@[backend_v2/tests/unit/scripts/test_backend_audit_loop.py]`: added unit tests for `--micro` mode, explicit `--logfire` override, default model selection, `--model` CLI override, `run_macro_quality_gate` success/failure/timeout, and backtick-wrapped tracker parsing/marking.
- Verified 100% Universal Quality Gate pass across both scripts (`92%` coverage on `backend_audit_loop.py`, `93%` coverage on `auto_hardening_runner.py`).

## Learned
- In `run_hardening_pipeline`, `--dry-run` with explicit `--targets` defaults to all gates unless `--gate` is specified; checking whether target is a Python file ensures `.py` targets display the planned `backend_audit_loop.py ... --micro --no-logfire` command accurately.

## Remaining
- Tier 2 Hardening (Backend): Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Hardening_Pipeline_Optimization.md]" --gate backend`.

## Resume Command
```powershell
uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Hardening_Pipeline_Optimization.md]" --gate backend
```
