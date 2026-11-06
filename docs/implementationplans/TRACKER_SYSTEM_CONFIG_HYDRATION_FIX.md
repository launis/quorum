# Tracker: PostgreSQL 19 `system_configs` `NULL` `name` Hydration Failure, Preflight Schema Verification & Live Seed Synchronization

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_SYSTEM_CONFIG_HYDRATION_FIX.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_SYSTEM_CONFIG_HYDRATION_FIX.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_SYSTEM_CONFIG_HYDRATION_FIX.md] @[docs/implementationplans/TRACKER_SYSTEM_CONFIG_HYDRATION_FIX.md]`
  - [x] Step 1: Phase 1: Fail-Fast SystemConfig Hydration, Preflight Schema Verification, Idempotent DDL Constraint Evolution & Live PostgreSQL 19 Re-Seed
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_SYSTEM_CONFIG_HYDRATION_FIX.md] @[docs/implementationplans/TRACKER_SYSTEM_CONFIG_HYDRATION_FIX.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no @pytest.mark.skip or commented-out tests remain in modified domains.
- [x] **[OK] Tier 2 Hardening (Backend)**: Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_SYSTEM_CONFIG_HYDRATION_FIX.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend {target}'"`.
  - [x] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]
  - [x] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]
  - [x] @[backend_v2/seed/run_seed.py]
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [x] **[OK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_SYSTEM_CONFIG_HYDRATION_FIX.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_SYSTEM_CONFIG_HYDRATION_FIX.md] @[ki_god_code_prevention.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document the fail-fast `AppException` translation in `hydrate_system_config_row`, pre-flight `system_configs` schema hydration verification in `verify_seed_table_counts_rows`, and idempotent `DELETE FROM system_configs WHERE name IS NULL;` + `ALTER TABLE system_configs ALTER COLUMN name DROP DEFAULT / SET NOT NULL` constraint evolution in `001_pg19_uuidv7_schema.sql`.
  2. **Directory Reference Sync:**
     - Verify `@[.agents/rules/04_directory_reference.md]` remains synchronized with `backend_v2/database/postgres/entity_adapter/`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` if needed to reflect pre-flight `system_configs` hydration verification in present tense without historical language or plan IDs.

### Final Plan Audit

- [x] **[OK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_SYSTEM_CONFIG_HYDRATION_FIX.md] @[docs/implementationplans/TRACKER_SYSTEM_CONFIG_HYDRATION_FIX.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

- **Atomic Commit Mandate**: After completing each cohesive logical step and passing quality gates, execute an atomic git commit using strict Conventional Commits (`<type>(<scope>): <imperative summary in lowercase, max 72 chars>`).
- **Universal Quality Gate Loops**:
  - Backend / Scripts: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py <target_path> --test --ast-strict`
- **File Reference Syntax**: Normalize all codebase file references to workspace-relative POSIX paths.
- **Session Handover Protocol**: Trigger `/tier5-session-handover` if processing >8 user prompts in a session, completing 3 atomic git commits, or modifying >5 distinct complex modules.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| REQ-001 | Catch `ValidationError` in `hydrate_system_config_row` in `@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L912-L970]`, log a structured RFC 7807 `logger.error` with `ErrorCodes.VALIDATION_FAILED` and `entity_id`, and raise `AppException`. | Step 1 | [x] Completed |
| REQ-002 | Verify `system_configs` schema hydration via `await list_collection_documents_rows(conn, timeout, "system_configs")` inside `verify_seed_table_counts_rows` in `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L220-L260]` whenever `expected` requires `system_configs` or `system_config` `>= 1`. | Step 1 | [x] Completed |
| REQ-003 | Add idempotent `DELETE FROM system_configs WHERE name IS NULL;`, `ALTER TABLE system_configs ALTER COLUMN name DROP DEFAULT;`, and `ALTER TABLE system_configs ALTER COLUMN name SET NOT NULL;` evolution statements to `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L82-L108]`, re-apply migrations after seeding in `@[backend_v2/seed/run_seed.py#L276-L340]`, and update `test_pg19_iam_schema_evolution_and_startup_preflight_migrations` in `@[backend_v2/tests/unit/database/test_postgres.py#L1983-L2080]`. | Step 1 | [x] Completed |
| REQ-004 | Execute `uv run --no-sync --offline python backend_v2/seed/run_seed.py local` to synchronize the live PostgreSQL 19 `system_configs` table (`sys_0195f3a00000700080008172bda70c86` with `name = 'Tavily MCP Gateway'`) and verify `test_hydrate_system_config_null_name_and_preflight_verification_raises_app_exception` passes in `@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py#L583-L658]`. | Step 1 | [x] Completed |

# Session Handover Context

## Achieved
- Implemented and committed Step 1 of `@[docs/implementationplans/IMPLEMENTATION_PLAN_SYSTEM_CONFIG_HYDRATION_FIX.md]` (commit `80aec1196`):
  1. Wrapped `SystemConfigMCPGateways.model_validate` and `SystemConfigModelRegistry.model_validate` in `hydrate_system_config_row` (`@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py#L912-L970]`) with `try...except ValidationError as exc:` logging RFC 7807 `logger.error` (`ErrorCodes.VALIDATION_FAILED`) and raising `AppException`.
  2. Extended `verify_seed_table_counts_rows` (`@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py#L220-L260]`) to invoke `await list_collection_documents_rows(conn, timeout, "system_configs")` whenever `expected` requires `system_configs` or `system_config` `>= 1`.
  3. Added `DELETE FROM system_configs WHERE name IS NULL;`, `ALTER TABLE system_configs ALTER COLUMN name DROP DEFAULT;`, and `ALTER TABLE system_configs ALTER COLUMN name SET NOT NULL;` to `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L82-L108]`, and invoked `await resolved_uow.pool_manager.apply_migrations()` after `seed_collection_batch` in `@[backend_v2/seed/run_seed.py#L276-L340]`.
  4. Executed `uv run --no-sync --offline python backend_v2/seed/run_seed.py local`, purging an orphaned pre-migration draft row (`sys_01a18adecd8e723d87a53fe3fee83fd3` with `name = NULL`), updating all 4 canonical `system_configs` rows (including `sys_0195f3a00000700080008172bda70c86` with `name = 'Tavily MCP Gateway'`), and locking `system_configs.name SET NOT NULL` on the live local PostgreSQL 19 database.
  5. Verified 100% quality gate pass via `scripts/backend_audit_loop.py --test --ast-strict` across all modified production and unit test files (`@[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py#L583-L658]` and `@[backend_v2/tests/unit/database/test_postgres.py#L1983-L2080]`).
- Synchronized `@[ki_god_code_prevention.md]` and timeless present-tense architecture narratives in `@[docs/architecture/02_data_seeding_and_ontology.md]` and `@[docs/architecture/05_resilience_and_observability.md]` via `/tier7-describe-architecture @[docs/implementationplans/TRACKER_SYSTEM_CONFIG_HYDRATION_FIX.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_SYSTEM_CONFIG_HYDRATION_FIX.md] @[ki_god_code_prevention.md]`.
- Executed `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_SYSTEM_CONFIG_HYDRATION_FIX.md] @[docs/implementationplans/TRACKER_SYSTEM_CONFIG_HYDRATION_FIX.md]`: verified 100% implementation fidelity across REQ-001 through REQ-004, exact AST definition bounds (`#L912-L970` in `iam_and_system_stage.py`, `#L220-L260` in `seed_and_collection_stage.py`, `#L276-L340` in `run_seed.py`), 0 technical debt findings (`audit_technical_debt.py`), 0 ZORM violations (`audit_zero_orm_strictness.py`), 100% DTO parity (81/81 models), and 10/10 stages of `backend_audit_loop.py --test --ast-strict`.
- Completed `Tier 2 Hardening (Backend)` via `scripts/auto_hardening_runner.py` across all 3 production targets (`@[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`, `@[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]`, and `@[backend_v2/seed/run_seed.py]`, commits `ed20c88cb`, `d95c3cd46`, `41189a82b`) and passed the Final Macro-Audit Completion Gate (`10/10` stages).

## Learned
- Our new `verify_seed_table_counts_rows` schema hydration check immediately caught an additional orphaned pre-migration draft row (`sys_01a18adecd8e723d87a53fe3fee83fd3` with `name = NULL`) in the live PostgreSQL 19 `system_configs` table that was not part of `seed_data.json`.
- Adding `DELETE FROM system_configs WHERE name IS NULL;` prior to `ALTER TABLE system_configs ALTER COLUMN name DROP DEFAULT;` and `ALTER TABLE system_configs ALTER COLUMN name SET NOT NULL;` in `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L100-L103]` deterministically purges any corrupt pre-migration `NULL`-name row before seeding and locks the `NOT NULL` constraint immediately.

## Remaining
- None — all implementation, Tier 2 hardening, Tier 7 architectural documentation sync, and Tier 8 red-team audit gates are 100% complete.

## Resume Command
```powershell
/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_SYSTEM_CONFIG_HYDRATION_FIX.md] @[docs/implementationplans/TRACKER_SYSTEM_CONFIG_HYDRATION_FIX.md]
```
