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

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]`
  - [x] Step 1: Implement QGR020 Bare Field Ban, QGR031 Filter Guard, QGR032 Factory Guard & QGR033 Docstring/RFC7807 Guard in scripts/_ast_guardrails.py
  - [x] Step 2: Replace Hardcoded Script Tuple with Dynamic scripts/*.py Discovery in scripts/backend_audit_loop.py
  - [x] Step 3: Add ISTQB Unit Tests for QGR020, QGR031, QGR032, QGR033 & Dynamic Script Discovery and Upgrade Polyfactory Meta-Test
  - [ ] Step 4: Implement SHA-256 Hardening Cache DTOs, Tracker Seeding (Waves 1-4 & UUIDv7) & 0s Short-Circuit in scripts/auto_hardening_runner.py
  - [ ] Step 5: Add Comprehensive ISTQB Unit Tests for SHA-256 Hardening Cache & Tracker Seeding in test_auto_hardening_runner.py
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]" --gate backend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`.
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/backend_audit_loop.py]
  - [ ] @[scripts/auto_hardening_runner.py]
- [ ] **[NOK] Tier 2 Hardening (Frontend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]" --gate frontend --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-frontend @[{target}]'"`.
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
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

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

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
| REQ-004 | Implement deterministic content-addressed SHA-256 hardening cache (`HardeningCacheEntryDTO`, `HardeningCacheManifestDTO`, `target + unit_test + .agents/rules/ SHA-256`), automatic seeding from completed Wave 1–4 and UUIDv7 trackers, and 0-second `[x]` cache-hit short-circuit in `@[scripts/auto_hardening_runner.py]`. | Step 4 | [ ] Pending |
| REQ-005 | Add ISTQB unit tests for 0-second SHA-256 cache hits, cache invalidation on target/test/rule mutation, completed tracker seeding, and `--no-cache` bypass in `@[backend_v2/tests/unit/scripts/test_auto_hardening_runner.py]`. | Step 5 | [ ] Pending |

# Session Handover Context

## Achieved
- Drafted and synchronized `@[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md]` and `@[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]` covering `QGR020` Check 20B, `QGR031`, `QGR032`, `QGR033`, dynamic `scripts/*.py` discovery, and the content-addressed SHA-256 hardening cache in `scripts/auto_hardening_runner.py` seeded from completed Wave 1–4 and UUIDv7 trackers.

## Learned
- Across the 403 production files in `backend_v2/`, `Raises: None` has 0 violations, missing top-level public class docstrings has 0 violations, unlogged `AppException` has only 1 domain file (`backend_v2/services/auth/repositories.py`), missing module docstrings has 4 files, and legacy bare `Field(...)` has 25 files. Locking these in self-verifying `RESIDUAL_*_FILES` sets prevents any regressions on already-hardened Wave 1–4 and UUIDv7 files while strictly enforcing `FATAL` guardrails on all new and modified code.

## Remaining
- Execute Steps 1 through 5 via `/tier2-execute --full-auto`, run Tier 2 Hardening (`auto_hardening_runner.py`), synchronize documentation via `/tier7-describe-architecture`, and complete `/tier8-audit-plan`.

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_AST_Guardrails_QGR031_QGR032.md] @[docs/implementationplans/TRACKER_AST_Guardrails_QGR031_QGR032.md]
```
