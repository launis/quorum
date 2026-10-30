# Tracker: AST & Quality Gate Extensions (QGR020, QGR031–QGR033), Dynamic Script Scanning & Content-Addressed SHA-256 Hardening Cache

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]` (`49e524fa8`)
  - [x] Step 1: Implement QGR020 Bare Field Ban, QGR031 Filter Guard, QGR032 Factory Guard & QGR033 Docstring/RFC7807 Guard in scripts/_ast_guardrails.py
  - [x] Step 2: Replace Hardcoded Script Tuple with Dynamic scripts/*.py Discovery in scripts/backend_audit_loop.py
  - [x] Step 3: Add ISTQB Unit Tests for QGR020, QGR031, QGR032, QGR033 & Dynamic Script Discovery and Upgrade Polyfactory Meta-Test
  - [x] Step 4: Implement SHA-256 Hardening Cache DTOs, Tracker Seeding (Waves 1-4 & UUIDv7) & 0s Short-Circuit in scripts/auto_hardening_runner.py
  - [x] Step 5: Add Comprehensive ISTQB Unit Tests for SHA-256 Hardening Cache & Tracker Seeding in test_auto_hardening_runner.py
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [x] @[scripts/_ast_guardrails.py]
  - [x] @[scripts/backend_audit_loop.py]
  - [x] @[scripts/auto_hardening_runner.py]
- [x] **[OK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"`.
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [x] **[OK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[ki_god_code_prevention.md] @[ki_deterministic_hardening_state.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document `QGR020` Check 20B (bare `Field()` ban without `Annotated`), `QGR031` (`Filter` / `QueryCondition` static operator and value discipline), `QGR032` (Polyfactory `Use(generate_opaque_id, ...)` invariant), `QGR033` (PEP 257 module/class docstrings, `Raises: None` ban, and RFC 7807 `logger.error` before `raise AppException`), and dynamic `scripts/*.py` discovery in `backend_audit_loop.py`.
     - `@[ki_deterministic_hardening_state.md]`: Document the content-addressed SHA-256 hardening cache (`data/hardening_cache.json`, `HardeningCacheEntryDTO`, `HardeningCacheManifestDTO`) in `scripts/auto_hardening_runner.py`, composite hashing of `(target_file + unit_test_files + .agents/rules/*.md)`, automatic seeding from completed Wave 1–4 and UUIDv7 trackers, and the 0-second `[x]` cache-hit short-circuit.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to reflect `QGR001`–`QGR033` in `scripts/_ast_guardrails.py` and the SHA-256 hardening cache in `scripts/auto_hardening_runner.py`.
  3. **Pillar Documentation Sync:**
     - Synchronize `docs/architecture/05_resilience_and_observability.md` in present tense.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths (`@[scripts/_ast_guardrails.py]`).
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Implement `QGR020` Check 20B (bare `Field()` ban on non-`Annotated` Pydantic fields), `QGR031` (`Filter`/`QueryCondition` static operator & value validation), `QGR032` (`ModelFactory` `Use(generate_opaque_id, ...)` invariant), and `QGR033` (`Raises: None` ban, PEP 257 module/public-class docstrings, and RFC 7807 `logger.error` before `raise AppException`) in `@[scripts/_ast_guardrails.py]`. | Step 1 | [x] Completed |
| REQ-002 | Replace hardcoded `_MACRO_AUTHORITATIVE_SCRIPTS` maintenance with dynamic `discover_authoritative_scripts()` (`Path("scripts").glob("*.py")`) in `@[scripts/backend_audit_loop.py]`. | Step 2 | [x] Completed |
| REQ-003 | Add ISTQB positive/negative unit tests for `QGR020`, `QGR031`, `QGR032`, `QGR033`, and `discover_authoritative_scripts` in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, and add dynamic `ModelFactory.__subclasses__()` discovery in `@[backend_v2/tests/factories/test_model_factories.py]`. | Step 3 | [x] Completed |
| REQ-004 | Implement deterministic content-addressed SHA-256 hardening cache (`HardeningCacheEntryDTO`, `HardeningCacheManifestDTO`, `target + unit_test + .agents/rules/ SHA-256`), automatic seeding from completed Wave 1–4 and UUIDv7 trackers, and 0-second `[x]` cache-hit short-circuit in `@[scripts/auto_hardening_runner.py]`. | Step 4 | [x] Completed |
| REQ-005 | Add ISTQB unit tests for 0-second SHA-256 cache hits, cache invalidation on target/test/rule mutation, completed tracker seeding, and `--no-cache` bypass in `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]`. | Step 5 | [x] Completed |

# Session Handover Context

## Achieved
- Completed and verified Steps 1 through 5 (`REQ-001` through `REQ-005`) of `@[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]`.
- Implemented `QGR020` Check 20B (bare `Field()` ban on non-`Annotated` Pydantic fields), `QGR031` (`Filter`/`QueryCondition` static operator & value validation), `QGR032` (`ModelFactory` `Use(generate_opaque_id, ...)` invariant), and `QGR033` (`Raises: None` ban, PEP 257 module/public-class docstrings, and RFC 7807 `logger.error` before `raise AppException`) in `@[scripts/_ast_guardrails.py]`.
- Replaced hardcoded script whitelisting with dynamic `discover_authoritative_scripts()` (`Path("scripts").glob("*.py")`) in `@[scripts/backend_audit_loop.py]`.
- Implemented deterministic content-addressed SHA-256 hardening cache (`HardeningCacheEntryDTO`, `HardeningCacheManifestDTO`, composite SHA-256 over `target_file + unit_test_files + .agents/rules/*.md`), automatic seeding of 335 hardened files from completed Wave 1–4 and UUIDv7 trackers into `data/hardening_cache.json`, and 0-second `⚡ CACHE HIT` short-circuit in `@[scripts/auto_hardening_runner.py]`.
- Added ISTQB unit tests in `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py]`, `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]`, and `@[backend_v2/tests/factories/test_model_factories.py]`, and updated `@[.agents/rules/04_directory_reference.md]`.
- Completed Tier 7 As-Built Architectural Sync (`/tier7-describe-architecture`) synchronizing `@[ki_god_code_prevention.md]`, `@[ki_deterministic_hardening_state.md]`, their `metadata.json` manifests, and `@[docs/architecture/05_resilience_and_observability.md]` in timeless present tense.
- Completed Tier 8 System 2 Red-Team Audit (`/tier8-audit-plan`) producing `@[red_team_audit_AST_Guardrails_QGR031_QGR032.md]`, verifying 100% plan-tracker parity (`audit_plan_tracker_parity.py`), 0 technical debt findings (`audit_technical_debt.py`), and passing the Global Completion Gate (`backend_audit_loop.py backend_v2/ --test` with 6,614 tests passed, 0 failures, and 97.40% coverage).

## Learned
- `backend_v2/services/orchestrator/strategies/llm_strategy/*.py` invokes `step_logger.error(...)` on injected structured logger instances; matching any receiver identifier containing `"log"` in `_function_has_error_log` cleanly recognizes all structured logger instances with 0 false positives across all 403 `backend_v2/` modules.
- Pinning `visible_workflow_extensions` to `[]` in `OutputProfileFactory` prevents Polyfactory from randomly injecting `XaiExtensionType.VARIANCE_VALIDATION` when `variance_target_block` is `None`.
- Dynamic `Path("scripts").glob("*.py")` script discovery in `backend_audit_loop.py` eliminates maintenance of hardcoded script lists, guaranteeing that newly created operational and guardrail scripts immediately undergo the full 10-stage quality gate.

## Remaining
- None. Implementation Plan and Tracker are 100% complete, verified, and audited.

## Resume Command
```powershell
# Plan and Tracker 100% Complete
```
