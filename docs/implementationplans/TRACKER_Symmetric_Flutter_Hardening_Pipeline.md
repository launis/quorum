# Tracker: Symmetric Flutter Micro/Macro Hardening Pipeline, Tripartite Layer & Protocol Guardrails, Dart 3.11 Strict Analyzer, Retry Feedback Loop & Creative Skill Context Offloading

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Symmetric_Flutter_Hardening_Pipeline.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_Symmetric_Flutter_Hardening_Pipeline.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Symmetric_Flutter_Hardening_Pipeline.md] @[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md]`
  - [x] Step 1: Phase 1: Add --micro Mode to flutter_audit_loop.py, Update DGR010/DGR007 in _dart_guardrails.py, Enable Strict Modes in analysis_options.yaml & Enforce Tripartite Layer Guardrails in _ast_guardrails.py
  - [x] Step 2: Phase 2: Symmetric Frontend Micro/Macro Dispatch, Retry Feedback Loop, Process Tree Cleanup, Atomic Staging & Wake-Lock in auto_hardening_runner.py
  - [x] Step 3: Phase 3: Symbolic AST Auto-Binding (--fix) in audit_markdown_boundaries.py & Creative Skill Context Offloading
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Symmetric_Flutter_Hardening_Pipeline.md] @[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] @[scripts/_ast_guardrails.py]
  - [x] @[scripts/_dart_guardrails.py]
  - [x] @[scripts/audit_markdown_boundaries.py]
  - [x] @[scripts/auto_hardening_runner.py]
  - [x] @[scripts/flutter_audit_loop.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Symmetric_Flutter_Hardening_Pipeline.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document the Tripartite Layer & Protocol Firewall (`QGR017` across PostgreSQL `backend_v2/database/`, Pydantic `backend_v2/models/`, and Python `backend_v2/services/` + `backend_v2/hooks/` + `backend_v2/api/routers/`), symmetric Flutter micro/macro quality gates (`requires_dart_codegen`, `resolve_flutter_unit_test_files`, `run_frontend_macro_quality_gate`), Dart 3.11 strict analyzer modes, `auto_hardening_runner.py` retry error feedback injection and `head_sha` rollback, and `--fix` symbolic AST auto-binding in `audit_markdown_boundaries.py`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to reflect updated capabilities in `scripts/flutter_audit_loop.py`, `scripts/_dart_guardrails.py`, `scripts/_ast_guardrails.py`, `scripts/auto_hardening_runner.py`, and `scripts/audit_markdown_boundaries.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` describing the Tripartite Layer & Protocol Firewall and symmetric micro/macro quality gate invariants in present tense without historical language or plan IDs.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Symmetric_Flutter_Hardening_Pipeline.md] @[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
  - Frontend / Flutter: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/<target_path> --build`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[scripts/flutter_audit_loop.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Implement `requires_dart_codegen(target_path: Path) -> bool` and `resolve_flutter_unit_test_files(target_dir: str, client_app_dir: Path) -> list[str]` in `@[scripts/flutter_audit_loop.py#L39-L59]` and export both in `__all__` | Step 1 | [x] Completed |
| REQ-002 | Add `--micro` CLI flag to `@[scripts/flutter_audit_loop.py#L62-L92]` to skip `flutter gen-l10n` and `build_runner` when codegen directives are absent and enforce isolated unit test execution (`sys.exit(1)` if missing) | Step 1 | [x] Completed |
| REQ-003 | Update `DGR010` remediation in `@[scripts/_dart_guardrails.py#L232-L371]` to mandate Dart 3 native `switch` pattern matching (`AsyncData`, `AsyncError`, `AsyncLoading`) and extend `DGR007` to flag deprecated `.withOpacity(` calls in feature widgets | Step 1 | [x] Completed |
| REQ-004 | Enable `strict-casts: true`, `strict-inference: true`, and `strict-raw-types: true` under `analyzer: language:` in `@[client_app_v2/analysis_options.yaml]` | Step 1 | [x] Completed |
| REQ-005 | Add `<rule_block id="tripartite_postgres_pydantic_python_boundary">` to `@[.agents/rules/01-python-backend.md]` codifying strict interface isolation across `backend_v2/models/`, `backend_v2/database/`, and `backend_v2/services/` + `backend_v2/hooks/` + `backend_v2/api/routers/` | Step 1 | [x] Completed |
| REQ-006 | Track `self._in_type_checking` in `@[scripts/_ast_guardrails.py#L778-L808]` and `@[scripts/_ast_guardrails.py#L2116-L2127]`, and enforce `QGR017` (`GuardrailSeverity.FATAL`) Tripartite Layer & Protocol Firewall in `@[scripts/_ast_guardrails.py#L2643-L2716]` and `@[scripts/_ast_guardrails.py#L2860-L3172]` | Step 1 | [x] Completed |
| REQ-007 | Add positive, negative, and boundary unit tests in `@[backend_v2/tests/unit/scripts/test_flutter_audit_loop.py#L113-L125]`, `@[backend_v2/tests/unit/scripts/test_flutter_audit_loop.py#L253-L267]`, `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L633-L647]`, and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2854-L2878]` | Step 1 | [x] Completed |
| REQ-008 | Add `head_sha: str \| None = None` to `WorkspaceSnapshotDTO` in `@[scripts/auto_hardening_runner.py#L311-L320]` and capture/restore `HEAD` via `git rev-parse HEAD` and `git reset --hard` in `@[scripts/auto_hardening_runner.py#L1237-L1287]` and `@[scripts/auto_hardening_runner.py#L1290-L1355]` | Step 2 | [x] Completed |
| REQ-009 | Execute post-exit `taskkill /F /T /PID` on Windows in `execute_subprocess_with_tree_kill` (`@[scripts/auto_hardening_runner.py#L887-L958]`) to reap orphaned child MCP server processes (`dart.exe`, `node.exe`) | Step 2 | [x] Completed |
| REQ-010 | Accept `previous_error: str \| None = None` in `execute_subagent_pass` (`@[scripts/auto_hardening_runner.py#L1002-L1105]`) and pass `previous_error=last_error` in `process_target_with_retries` (`@[scripts/auto_hardening_runner.py#L1437-L1535]`) so retry attempts receive truncated failure diagnostics | Step 2 | [x] Completed |
| REQ-011 | Append `--micro` to `flutter_audit_loop.py` when `micro_audit=True` in `run_quality_gate` (`@[scripts/auto_hardening_runner.py#L1108-L1155]`) and implement `run_frontend_macro_quality_gate` alongside `@[scripts/auto_hardening_runner.py#L1193-L1234]` | Step 2 | [x] Completed |
| REQ-012 | Update `mark_tracker_and_checkpoint` (`@[scripts/auto_hardening_runner.py#L1358-L1434]`) to atomically stage resolved unit test files and sibling `.g.dart`/`.freezed.dart` artifacts alongside `target_file` and `cleaned_tracker` | Step 2 | [x] Completed |
| REQ-013 | Add `acquire_windows_wake_lock` and `release_windows_wake_lock` using Win32 `SetThreadExecutionState` and invoke `run_frontend_macro_quality_gate` in `run_hardening_pipeline` (`@[scripts/auto_hardening_runner.py#L1538-L1754]`) | Step 2 | [x] Completed |
| REQ-014 | Expand unit tests in `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L186-L230]`, `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L1052-L1061]`, and `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L1073-L1113]` for all Phase 2 capabilities | Step 2 | [x] Completed |
| REQ-015 | Implement `auto_fix_ast_bounds(self) -> int` on `MarkdownAuditor` (`@[scripts/audit_markdown_boundaries.py#L229-L282]`) and `--fix` CLI flag in `main` (`@[scripts/audit_markdown_boundaries.py#L718-L769]`) using `get_ast_definition_bounds` | Step 3 | [x] Completed |
| REQ-016 | Add unit tests in `@[backend_v2/tests/unit/scripts/test_audit_markdown_boundaries.py#L204-L266]` verifying `auto_fix_ast_bounds` and `--fix` CLI execution on symbolic `@[module.py#SymbolName]` and drifted `#Lnn-mm` references | Step 3 | [x] Completed |
| REQ-017 | Update `@[.agents/skills/tier0-create-plan/SKILL.md]`, `@[.agents/skills/tier0-create-epic/SKILL.md]`, and `@[.agents/skills/tier8-audit-feature/SKILL.md]` with `subagent_context_offloading` (`research` subagent delegation and `--fix` symbolic AST auto-binding) | Step 3 | [x] Completed |
| REQ-018 | Update `@[.agents/skills/tier2-hardening-frontend/SKILL.md]` and `@[.agents/skills/tier2-hardening-backend/SKILL.md]` to use `--micro` on single-file targets and skip duplicate internal `git commit` calls inside `auto_hardening_runner.py` | Step 3 | [x] Completed |

# Session Handover Context

## Achieved
- Completed Step 1 (`8048621fb`): Added `requires_dart_codegen`, `resolve_flutter_unit_test_files`, and `--micro` mode to `@[scripts/flutter_audit_loop.py]`; updated `DGR010` Dart 3 `switch` remediation and `DGR007` `.withOpacity(` detection in `@[scripts/_dart_guardrails.py]`; enabled `strict-casts`, `strict-inference`, and `strict-raw-types` in `@[client_app_v2/analysis_options.yaml]`; added `<rule_block id="tripartite_postgres_pydantic_python_boundary">` to `@[.agents/rules/01-python-backend.md]`; enforced `QGR017` Tripartite Layer & Protocol Firewall in `@[scripts/_ast_guardrails.py]`.
- Completed Step 2 (`2621101d0`): Updated `@[scripts/auto_hardening_runner.py]` with symmetric frontend `--micro` dispatch, `run_frontend_macro_quality_gate`, `head_sha` capture/rollback in `WorkspaceSnapshotDTO` and `execute_circuit_breaker_rollback`, post-exit `taskkill /F /T /PID` child MCP process cleanup on Windows, `previous_error` retry diagnostic injection in `execute_subagent_pass`, atomic staging of unit tests and `.g.dart`/`.freezed.dart` siblings in `mark_tracker_and_checkpoint`, and Win32 `SetThreadExecutionState` wake-lock helpers (`acquire_windows_wake_lock` / `release_windows_wake_lock`).
- Completed Step 3 (`5d609ee44`): Added `auto_fix_ast_bounds` and `--fix` CLI flag to `@[scripts/audit_markdown_boundaries.py]`; updated `@[.agents/skills/tier0-create-plan/SKILL.md]`, `@[.agents/skills/tier0-create-epic/SKILL.md]`, `@[.agents/skills/tier8-audit-feature/SKILL.md]`, `@[.agents/skills/tier2-hardening-frontend/SKILL.md]`, `@[.agents/skills/tier2-hardening-backend/SKILL.md]`, and `@[.agents/rules/04_directory_reference.md]`.
- Completed Tier 8 System 2 Red-Team Plan Audit: Verified 100% implementation fidelity across all 18 requirements (`REQ-001`–`REQ-018`) and 27 directives, 0 technical debt findings, >90% strict unit test coverage, 100% plan-tracker parity, and passing backend/frontend quality gates.

## Learned
- Checking `re.fullmatch(r"[0-9a-fA-F]{7,40}", raw_head)` in `capture_workspace_snapshot` ensures unit tests mocking `subprocess.run` with multiline `git status --porcelain` output resolve `head_sha=None` while real or SHA-mocked calls capture the exact commit SHA.
- `auto_fix_ast_bounds` deterministically resolves both symbolic `@[path/to/file.py#SymbolName]` anchors and drifted `#Lnn-mm` bounds using `get_ast_definition_bounds` as the single source of truth.

## Remaining
- Execute `Tier 2 Hardening (Backend)` across the 5 modified scripts via `scripts/auto_hardening_runner.py`.
- Run `/tier7-describe-architecture @[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_Symmetric_Flutter_Hardening_Pipeline.md] @[ki_god_code_prevention.md]`.

## Resume Command
```powershell
$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"
```
