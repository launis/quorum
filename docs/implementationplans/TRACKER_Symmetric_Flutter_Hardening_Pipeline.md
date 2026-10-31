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

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Symmetric_Flutter_Hardening_Pipeline.md] @[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md]`
  - [x] Step 1: Phase 1: Add --micro Mode to flutter_audit_loop.py, Update DGR010/DGR007 in _dart_guardrails.py, Enable Strict Modes in analysis_options.yaml & Enforce Tripartite Layer Guardrails in _ast_guardrails.py
  - [x] Step 2: Phase 2: Symmetric Frontend Micro/Macro Dispatch, Retry Feedback Loop, Process Tree Cleanup, Atomic Staging & Wake-Lock in auto_hardening_runner.py
  - [ ] Step 3: Phase 3: Symbolic AST Auto-Binding (--fix) in audit_markdown_boundaries.py & Creative Skill Context Offloading
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Symmetric_Flutter_Hardening_Pipeline.md] @[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/_dart_guardrails.py]
  - [ ] @[scripts/audit_markdown_boundaries.py]
  - [ ] @[scripts/auto_hardening_runner.py]
  - [ ] @[scripts/flutter_audit_loop.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

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

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_Symmetric_Flutter_Hardening_Pipeline.md] @[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

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
| REQ-001 | Implement `requires_dart_codegen(target_path: Path) -> bool` and `resolve_flutter_unit_test_files(target_dir: str, client_app_dir: Path) -> list[str]` in `@[scripts/flutter_audit_loop.py#L25-L179]` and export both in `__all__` | Step 1 | [x] Completed |
| REQ-002 | Add `--micro` CLI flag to `@[scripts/flutter_audit_loop.py#L25-L179]` to skip `flutter gen-l10n` and `build_runner` when codegen directives are absent and enforce isolated unit test execution (`sys.exit(1)` if missing) | Step 1 | [x] Completed |
| REQ-003 | Update `DGR010` remediation in `@[scripts/_dart_guardrails.py#L231-L353]` to mandate Dart 3 native `switch` pattern matching (`AsyncData`, `AsyncError`, `AsyncLoading`) and extend `DGR007` to flag deprecated `.withOpacity(` calls in feature widgets | Step 1 | [x] Completed |
| REQ-004 | Enable `strict-casts: true`, `strict-inference: true`, and `strict-raw-types: true` under `analyzer: language:` in `@[client_app_v2/analysis_options.yaml]` | Step 1 | [x] Completed |
| REQ-005 | Add `<rule_block id="tripartite_postgres_pydantic_python_boundary">` to `@[.agents/rules/01-python-backend.md]` codifying strict interface isolation across `backend_v2/models/`, `backend_v2/database/`, and `backend_v2/services/` + `backend_v2/hooks/` + `backend_v2/api/routers/` | Step 1 | [x] Completed |
| REQ-006 | Track `self._in_type_checking` in `@[scripts/_ast_guardrails.py#L778-L807]` and `@[scripts/_ast_guardrails.py#L2115-L2123]`, and enforce `QGR017` (`GuardrailSeverity.FATAL`) Tripartite Layer & Protocol Firewall in `@[scripts/_ast_guardrails.py#L2619-L2758]` and `@[scripts/_ast_guardrails.py#L2760-L3068]` | Step 1 | [x] Completed |
| REQ-007 | Add positive, negative, and boundary unit tests in `@[backend_v2/tests/unit/scripts/test_flutter_audit_loop.py#L109-L121]`, `@[backend_v2/tests/unit/scripts/test_flutter_audit_loop.py#L264-L275]`, `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L633-L645]`, and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L2854-L2878]` | Step 1 | [x] Completed |
| REQ-008 | Add `head_sha: str \| None = None` to `WorkspaceSnapshotDTO` in `@[scripts/auto_hardening_runner.py#L304-L310]` and capture/restore `HEAD` via `git rev-parse HEAD` and `git reset --hard` in `@[scripts/auto_hardening_runner.py#L1153-L1190]` and `@[scripts/auto_hardening_runner.py#L1193-L1247]` | Step 2 | [x] Completed |
| REQ-009 | Execute post-exit `taskkill /F /T /PID` on Windows in `execute_subprocess_with_tree_kill` (`@[scripts/auto_hardening_runner.py#L877-L936]`) to reap orphaned child MCP server processes (`dart.exe`, `node.exe`) | Step 2 | [x] Completed |
| REQ-010 | Accept `previous_error: str \| None = None` in `execute_subagent_pass` (`@[scripts/auto_hardening_runner.py#L980-L1067]`) and pass `previous_error=last_error` in `process_target_with_retries` (`@[scripts/auto_hardening_runner.py#L1316-L1414]`) so retry attempts receive truncated failure diagnostics | Step 2 | [x] Completed |
| REQ-011 | Append `--micro` to `flutter_audit_loop.py` when `micro_audit=True` in `run_quality_gate` (`@[scripts/auto_hardening_runner.py#L1070-L1115]`) and implement `run_frontend_macro_quality_gate` alongside `@[scripts/auto_hardening_runner.py#L1118-L1150]` | Step 2 | [x] Completed |
| REQ-012 | Update `mark_tracker_and_checkpoint` (`@[scripts/auto_hardening_runner.py#L1250-L1313]`) to atomically stage resolved unit test files and sibling `.g.dart`/`.freezed.dart` artifacts alongside `target_file` and `cleaned_tracker` | Step 2 | [x] Completed |
| REQ-013 | Add `acquire_windows_wake_lock` and `release_windows_wake_lock` using Win32 `SetThreadExecutionState` and invoke `run_frontend_macro_quality_gate` in `run_hardening_pipeline` (`@[scripts/auto_hardening_runner.py#L1417-L1562]`) | Step 2 | [x] Completed |
| REQ-014 | Expand unit tests in `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L183-L208]`, `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L1044-L1084]`, and `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py#L1087-L1154]` for all Phase 2 capabilities | Step 2 | [x] Completed |
| REQ-015 | Implement `auto_fix_ast_bounds(self) -> int` on `MarkdownAuditor` (`@[scripts/audit_markdown_boundaries.py#L68-L540]`) and `--fix` CLI flag in `main` (`@[scripts/audit_markdown_boundaries.py#L543-L580]`) using `get_ast_definition_bounds` | Step 3 | [ ] Pending |
| REQ-016 | Add unit tests in `@[backend_v2/tests/unit/scripts/test_audit_markdown_boundaries.py#L204-L221]` verifying `auto_fix_ast_bounds` and `--fix` CLI execution on symbolic `@[module.py#SymbolName]` and drifted `#Lnn-mm` references | Step 3 | [ ] Pending |
| REQ-017 | Update `@[.agents/skills/tier0-create-plan/SKILL.md]`, `@[.agents/skills/tier0-create-epic/SKILL.md]`, and `@[.agents/skills/tier8-audit-feature/SKILL.md]` with `subagent_context_offloading` (`research` subagent delegation and `--fix` symbolic AST auto-binding) | Step 3 | [ ] Pending |
| REQ-018 | Update `@[.agents/skills/tier2-hardening-frontend/SKILL.md]` and `@[.agents/skills/tier2-hardening-backend/SKILL.md]` to use `--micro` on single-file targets and skip duplicate internal `git commit` calls inside `auto_hardening_runner.py` | Step 3 | [ ] Pending |

# Session Handover Context

## Achieved
- Promoted implementation plan to `@[docs/implementationplans/IMPLEMENTATION_PLAN_Symmetric_Flutter_Hardening_Pipeline.md]` and normalized all file references to workspace-relative POSIX paths.
- Generated full standalone execution tracker `@[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md]` with 18 granular requirements (`REQ-001` through `REQ-018`) mapped across Step 1, Step 2, and Step 3, plus 5 surviving production `.py` files in the `Tier 2 Hardening (Backend)` checklist.

## Learned
- Pre-flight technical debt audit (`scripts/audit_technical_debt.py --include-one-hop`) across all 10 Python scripts and unit test files in scope passed with 0 findings.
- Codebase AST verification across `backend_v2/` confirmed zero existing runtime Tripartite Layer & Protocol Firewall violations once `backend_v2.services.storage` in `backend_v2/database/repositories/execution.py` and `if TYPE_CHECKING:` blocks are accounted for.

## Remaining
- Execute Step 1, Step 2, and Step 3 via `/tier2-execute --full-auto` (or optionally run `/tier0-research-plan` first).
- Complete Post-Implementation Gates (`Tier 2 Hardening (Backend)` across all 5 production scripts, `Pre-Delete Audit`, `Semantic Coverage & Zero-Loss Audit`), `Tier 7 As-Built Architectural Sync`, and `Tier 8 Final Plan Audit`.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_Symmetric_Flutter_Hardening_Pipeline.md] @[docs/implementationplans/TRACKER_Symmetric_Flutter_Hardening_Pipeline.md]
```
