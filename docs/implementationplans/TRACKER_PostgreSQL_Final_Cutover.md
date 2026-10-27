# Tracker: PostgreSQL 19 Sovereign Cutover & TinyDB Eradication Requirements

@[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md]

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_mcp_tool_protocol.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md]

- [x] **[OK] Execution:** `/tier2-execute --full-auto @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md] @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]`
  - [x] Step 1: Phase 1: Pre-Implementation Cleanups, Dependency Purge & Physical TinyDB Eradication
  - [x] Step 2: Phase 2: Sovereign Settings, UUIDv7 ID Routing & Storage Driver Cutover
  - [x] Step 3: Phase 3: Authoritative PostgreSQL 19 Seeding & FastAPI Preflight Cutover
  - [x] Step 4: Phase 4: AST Guardrail QGR017 Lockdown & Unit Test Suite Synchronization
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md] @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]`

### Post-Implementation Gates

- [x] **[OK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]" --gate backend --model gemini-4-argon-medium`.
  - [ ] @[backend_v2/database/driver.py]
  - [ ] @[backend_v2/database/factory.py]
  - [ ] @[backend_v2/database/interfaces.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter.py]
  - [ ] @[backend_v2/database/postgres/pool.py]
  - [ ] [NEW] @[backend_v2/database/postgres/storage_driver.py]
  - [ ] @[backend_v2/main.py]
  - [ ] @[backend_v2/models/core_base.py]
  - [ ] @[backend_v2/seed/run_seed.py]
  - [ ] @[backend_v2/services/storage.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/audit_zero_orm_strictness.py]
  - [ ] @[scripts/reconcile_storage.py]
  - [ ] @[scripts/run_e2e_variance_test.py]
- [x] **[OK] Physical Eradication Verification (Backend Targets)**: Confirm physical deletion and zero remaining references for `[DELETE] @[backend_v2/database/exporter.py]`, `[DELETE] @[backend_v2/database/firestore_driver.py]`, `[DELETE] @[backend_v2/database/tinydb_driver.py]`, `[DELETE] @[backend_v2/database/wrapper.py]`, and `[DELETE] @[backend_v2/seed/wipe_user_data.py]`.
- [x] **[SKIPPED] Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]" --gate frontend --model gemini-4-argon-medium`. (Zero frontend `.dart` production targets in this plan).
- [x] **[OK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [x] **[OK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [x] **[OK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md] @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md] @[ki_god_code_prevention.md] @[ki_python_314_concurrency_strictness.md] @[ki_zero_permissive_typing.md] @[ki_mcp_tool_protocol.md] @[ki_seed_vault_verification_and_sanitization.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document `PostgresStorageDriver` (`[NEW] @[backend_v2/database/postgres/storage_driver.py]`) implementing the `StorageDriver` protocol over `PostgresPoolManager` for all 16 repositories in `backend_v2/database/repositories/` (specifically and exhaustively: `AgentRepository`, `AuditRepository`, `ComponentRepository`, `ExecutionPersonaRepository`, `ExecutionRepository`, `ExtractionProtocolRepository`, `IdentityRepository`, `KnowledgeRepository`, `MatrixRepository`, `OutputProfileRepository`, `PromptBlockRepository`, `ReportArtifactRepository`, `RoleRepository`, `SystemRepository`, `TaskBlueprintRepository`, `WorkflowRepository`), the `EntityPersistencePort` seeding contracts (`seed_collection_batch` and `verify_seed_table_counts`), the single-pipeline factory invariant in `@[backend_v2/database/factory.py]` rejecting non-Postgres backends with `ConfigurationError`, the `QGR017` AST guardrail lockdown in `@[scripts/_ast_guardrails.py]` banning legacy drivers (`tinydb_driver`, `wrapper`, `firestore_driver`, `exporter`, `wipe_user_data`, `TinyDBClient`) and database artifacts (`db_v2.json`, `db_v2.json.lock`, `app.db`), and the migration of `@[scripts/reconcile_storage.py]` and `@[scripts/run_e2e_variance_test.py]` away from legacy `db_v2.json` to typed snapshot and SSOT seed paths.
     - `@[ki_python_314_concurrency_strictness.md]`: Document the asynchronous PostgreSQL 19 preflight verification in `@[backend_v2/main.py]` lifespan (`_validate_database_preflight` verifying row counts for all 7 seeded tables via `QuorumUnitOfWork.entities.verify_seed_table_counts()`), thread-safe monotonic sub-millisecond RFC 9562 UUIDv7 ID generation (`generate_opaque_id` in `@[backend_v2/models/core_base.py]` delegating to `generate_uuid7_opaque_id` specifically and exhaustively for `EntityPrefix.EXECUTION`, `EntityPrefix.REPORT`, `EntityPrefix.NODE`, and `EntityPrefix.EDGE`), the eradication of OS-level file locks (`msvcrt.locking` and `fcntl`) in favor of PostgreSQL 19 ACID transactions and MVCC, and forward reference resolution in Pydantic models (`ExecutionRecord.model_rebuild` resolving `ErrorTraceEvent`, `TombstoneEvent`, `TraceEvent` for standalone CLI scripts).
     - `@[ki_zero_permissive_typing.md]`: Document the Zero-ORM `PostgresStorageDriver` and `PostgresEntityAdapter` parameterized `$1, $2` batch upserts with binary `\x01` JSONB codecs (`pydantic_core.to_json` / `from_json`), `ZORM001`–`ZORM006` AST enforcement across `storage_driver.py` in `@[scripts/audit_zero_orm_strictness.py]`, strict `ExecutionRecord` snapshot container (`ConfigDict(strict=True, extra="forbid", frozen=True)`) and canonical hexadecimal ID validation (`^([a-z]{2,5})_[a-fA-F0-9]{16,32}$`) in `@[scripts/reconcile_storage.py]`, and the complete eradication of naked dicts in state transit verified by `@[scripts/audit_dict_eradication.py]`.
     - `@[ki_mcp_tool_protocol.md]`: Document authoritative PostgreSQL 19 seeding of `system_configs` (specifically and exhaustively: `SystemConfigMCPGateways`, `SystemConfigModelRegistry`, `SystemSettingsDTO`) via `@[backend_v2/seed/run_seed.py]` and `PostgresEntityAdapter.seed_collection_batch` into the PostgreSQL 19 `system_configs` table with canonical opaque stripe ID `sys_...`.
     - `@[ki_seed_vault_verification_and_sanitization.md]`: Document the authoritative PostgreSQL 19 database seeding pipeline in `@[backend_v2/seed/run_seed.py]` ingesting `ValidatedSeedBufferDTO` directly into PostgreSQL 19 across all 7 seeded tables (`organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`) via `PostgresEntityAdapter.seed_collection_batch`, the eradication of legacy `_seed_tinydb`, `_seed_firestore`, and `wipe_user_data.py`, and the purge of legacy `db_v2.json` references in favor of transactional relational upserts and row count assertions.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register `backend_v2/database/postgres/storage_driver.py`, verify `backend_v2/database/postgres/pool.py` and `backend_v2/database/postgres/entity_adapter.py`, and remove deleted modules, specifically and exhaustively: `backend_v2/database/tinydb_driver.py`, `backend_v2/database/wrapper.py`, `backend_v2/database/firestore_driver.py`, `backend_v2/database/exporter.py`, and `backend_v2/seed/wipe_user_data.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` (specifically and exhaustively: `01_system_context_and_invariants.md`, `02_data_seeding_and_ontology.md`, and `05_resilience_and_observability.md`) describing the sovereign PostgreSQL 19 storage driver, authoritative 10-table PostgreSQL seeding pipeline, and FastAPI startup preflight verification in present tense without historical language or plan IDs.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md] @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

1. **Execution Mode**:
   - **Step-by-Step Mode** (`/tier2-execute @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md] @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]`): Execute a single unchecked step, run all step-level quality gates, update this tracker (`[x]`) and the `# Session Handover Context`, instruct the user to perform an atomic `git commit`, and STOP.
   - **Continuous Full-Auto Mode** (`/tier2-execute --full-auto @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md] @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]`): Proceed autonomously across all steps in sequence as long as quality gates pass 100%, halting immediately if any quality gate fails or when `context_amnesia_prevention` handover thresholds are reached.
2. **Quality Gate Mandate**:
   - After modifying any `.py` file, run `uv run python scripts/backend_audit_loop.py <target_path> --test --ast-strict` and `uv run python scripts/audit_zero_orm_strictness.py`.
   - Before closing the final step, run the global completion gates: `uv run python scripts/backend_audit_loop.py backend_v2/ --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.
3. **Atomic Commit Mandate**:
   - Provide an atomic `git commit` instruction using strict Conventional Commits syntax (`<type>(<scope>): <imperative summary in lowercase, max 72 chars, no trailing period>`) with explicit `git add` file paths and a concise, factual bulleted list of physical changes.
4. **Workspace Path Normalization**:
   - Exclusively use workspace-relative `@[...]` paths across all documentation, trackers, and handover blocks.
5. **Post-Implementation Hardening Execution Options**:
   - Run interactive file-by-file hardening in chat via `/tier2-hardening-backend @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]`, OR
   - Run autonomous unattended CLI hardening via `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]" --gate backend --model gemini-4-argon-medium`.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| **REQ-001** | Update `@[run_local.bat]` to launch `docker compose up -d redis postgres`, set `STORAGE_BACKEND=POSTGRES` for both FastAPI (`uvicorn`) and background worker (`run_worker`), and remove all `db_v2.json` and `STORAGE_BACKEND=LOCAL` references (`REQ-01`). | Step 1 | `[x]` |
| **REQ-002** | Remove `"tinydb"` and add `"asyncpg>=0.30.0"` in `@[pyproject.toml]`, synchronize `uv.lock`, and verify `uv run python -c "import tinydb"` raises `ModuleNotFoundError` (`REQ-05`, `RT-05`). | Step 1 | `[x]` |
| **REQ-003** | Physically delete all 8 legacy files from disk and version control, specifically and exhaustively: `[DELETE] @[backend_v2/database/tinydb_driver.py]`, `[DELETE] @[backend_v2/database/wrapper.py]`, `[DELETE] @[backend_v2/database/firestore_driver.py]`, `[DELETE] @[backend_v2/database/exporter.py]`, `[DELETE] @[backend_v2/seed/wipe_user_data.py]`, `[DELETE] @[data/db_v2.json]`, `[DELETE] @[data/db_v2.json.lock]`, and `[DELETE] @[data/app.db]` (`REQ-04`, `TD-04`). | Step 1 | `[x]` |
| **REQ-004** | Default `settings.storage_backend` to `StorageBackend.POSTGRES` in `@[backend_v2/settings.py#L47-L1087]`, update `active_backend` (`#L775-L801`) and `is_cloud_storage` (`#L805-L811`), and update `allow_mock_tokens` (`#L985-L1000`) to permit local mock tokens under `StorageBackend.POSTGRES` when `not self.use_firebase_auth` and `not self.is_cloud_environment` (`REQ-03`, `TD-02`, `RT-03`). | Step 2 | `[x]` |
| **REQ-005** | Update `get_storage_driver` in `@[backend_v2/services/storage.py#L20-L56]` to route `StorageBackend.POSTGRES` to `LocalFileDriver` when `not settings.storage_bucket_name` and `GCSFileDriver` when `settings.storage_bucket_name` is configured (`TD-03`, `RT-03`). | Step 2 | `[x]` |
| **REQ-006** | Update `generate_opaque_id` in `@[backend_v2/models/core_base.py#L199-L229]` to delegate to `generate_uuid7_opaque_id` (`@[backend_v2/models/core_base.py#L339-L392]`) when `prefix` is in `{EntityPrefix.EXECUTION, EntityPrefix.REPORT, EntityPrefix.NODE, EntityPrefix.EDGE}` (`RT-07`). | Step 2 | `[x]` |
| **REQ-007** | Implement `[NEW] @[backend_v2/database/postgres/storage_driver.py]` (`PostgresStorageDriver` conforming to `StorageDriver` over `PostgresPoolManager` for all 16 repositories in `backend_v2/database/repositories/`), register it in `@[scripts/audit_zero_orm_strictness.py#L226-L397]` and `@[scripts/audit_zero_orm_strictness.py#L460-L512]`, and wire `StorageBackend.POSTGRES` as the sole valid backend in `@[backend_v2/database/factory.py#L33-L110]` (`get_driver`) and `@[backend_v2/database/factory.py#L113-L147]` (`create_unit_of_work`), raising `ConfigurationError` on `LOCAL`, `TINYDB`, or `FIRESTORE` (`REQ-03`, `RT-01`). | Step 2 | `[x]` |
| **REQ-008** | Expand `EntityPersistencePort` in `@[backend_v2/database/interfaces.py#L397-L405]` and `PostgresEntityAdapter` in `@[backend_v2/database/postgres/entity_adapter.py#L827-L2113]` with `seed_collection_batch` and `verify_seed_table_counts` across all 10 core PostgreSQL 19 tables (`organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`, `executions`, `report_artifacts`, `report_binaries`) using parameterized SQL (`$1, $2`) and binary `\x01` JSONB codecs (`REQ-02`, `RT-02`). | Step 3 | `[x]` |
| **REQ-009** | Refactor `seed_database` (`@[backend_v2/seed/run_seed.py#L267-L305]`) and `main` (`@[backend_v2/seed/run_seed.py#L308-L348]`) to remove `_seed_tinydb` and `_seed_firestore`, ingest `ValidatedSeedBufferDTO` (`@[backend_v2/seed/run_seed.py#L82-L134]`) into PostgreSQL 19 while preserving 100% of `@[backend_v2/seed/seed_data.json]` prompts verbatim, and fail-fast with `AppException` if any of the 7 seeded tables has count 0 (`REQ-02`, `RT-02`). | Step 3 | `[x]` |
| **REQ-010** | Remove top-level `from tinydb import TinyDB` in `@[backend_v2/main.py]` and refactor `_audit_storage_and_database_sync` (`@[backend_v2/main.py#L58-L116]`), `_validate_database_preflight` (`@[backend_v2/main.py#L119-L161]`), and `lifespan` (`@[backend_v2/main.py#L165-L219]`) to execute asynchronous PostgreSQL 19 preflight checks (`TD-01`, `RT-04`). | Step 3 | `[x]` |
| **REQ-011** | Expand `QGR017` (`FATAL`) in `@[scripts/_ast_guardrails.py#L523-L2576]` (`visit_Module` `#L621-L706`, `visit_Import` `#L1922-L2056`, `visit_ImportFrom` `#L2058-L2357`) to ban `tinydb`, `tinydb_driver`, `firestore_driver`, `wrapper`, `TinyDBClient`, and `db_v2.json`, and remove deleted driver paths from `BOUNDARY_EXEMPTION_FILES` (`REQ-06`, `TD-04`, `RT-06`). | Step 4 | `[x]` |
| **REQ-012** | Synchronize `InMemoryEntityAdapter` (`@[backend_v2/tests/fakes/in_memory_uow.py#L585-L824]`) and `InMemoryAsyncPgConnection` (`@[backend_v2/tests/fakes/in_memory_uow.py#L885-L1444]`), and update unit tests in `@[backend_v2/tests/unit/test_factory.py#L32-L42]`, `@[backend_v2/tests/unit/test_settings.py#L95-L130]`, `@[backend_v2/tests/unit/seed/test_run_seed.py#L165-L180]`, and `@[backend_v2/tests/unit/database/test_postgres.py#L440-L563]` with >=2 negative ISTQB boundary cases per feature. | Step 4 | `[x]` |

# Session Handover Context

## Achieved
- Executed Steps 1 through 4 of `@[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md]` in Continuous Full-Auto Mode:
  - **Step 1**: Updated `@[run_local.bat]` to launch `docker compose up -d redis postgres` and set `STORAGE_BACKEND=POSTGRES`; removed `"tinydb"` and added `"asyncpg>=0.30.0"` in `@[pyproject.toml]` and `@[uv.lock]`; physically deleted all 8 legacy files (`tinydb_driver.py`, `wrapper.py`, `firestore_driver.py`, `exporter.py`, `wipe_user_data.py`, `data/db_v2.json`, `data/db_v2.json.lock`, `data/app.db`).
  - **Step 2**: Defaulted `Settings.storage_backend` to `StorageBackend.POSTGRES` in `@[backend_v2/settings.py]`, updated `get_storage_driver` in `@[backend_v2/services/storage.py]` and `generate_opaque_id` in `@[backend_v2/models/core_base.py]`, implemented `[NEW] @[backend_v2/database/postgres/storage_driver.py]` (`PostgresStorageDriver`), registered it in `@[scripts/audit_zero_orm_strictness.py]`, and wired `@[backend_v2/database/factory.py]` (`get_driver` and `create_unit_of_work`) exclusively to PostgreSQL 19.
  - **Step 3**: Expanded `EntityPersistencePort` (`@[backend_v2/database/interfaces.py]`) and `PostgresEntityAdapter` (`@[backend_v2/database/postgres/entity_adapter.py]`) with `seed_collection_batch` and `verify_seed_table_counts` across all 10 core PostgreSQL 19 tables, refactored `@[backend_v2/seed/run_seed.py]` and `@[backend_v2/main.py]` preflight checks, and verified live seeding against `quorum-postgres` (130 rows across the 7 seeded tables).
  - **Step 4**: Locked down `QGR017` (`FATAL`) in `@[scripts/_ast_guardrails.py]`, synchronized `@[backend_v2/tests/fakes/in_memory_uow.py]` and the unit test suites (`test_factory.py`, `test_settings.py`, `test_run_seed.py`, `test_postgres.py`, `test_storage.py`, `test_storage_audit.py`, `test_token_service.py`, `test_interfaces.py`, `test_ast_guardrails.py`, `test_audit_dict_eradication.py`, `test_reconcile_storage.py`, `test_scripts_cli_help.py`), eradicated legacy `db_v2.json` references in `@[scripts/reconcile_storage.py]` and `@[scripts/run_e2e_variance_test.py]`, updated `@[.agents/rules/04_directory_reference.md]`, and validated all 7 Quality Gates with 100% pass (6,229 passed tests, 96.90% coverage).
- Executed `/tier7-describe-architecture`:
  - Synchronized all 5 Target Knowledge Items (`@[ki_god_code_prevention.md]`, `@[ki_python_314_concurrency_strictness.md]`, `@[ki_zero_permissive_typing.md]`, `@[ki_mcp_tool_protocol.md]`, and `@[ki_seed_vault_verification_and_sanitization.md]`) and their `metadata.json` manifests.
  - Synchronized `@[.agents/rules/04_directory_reference.md]` (`backend_v2/database/postgres/storage_driver.py`, `backend_v2/main.py`, `scripts/reconcile_storage.py`) with zero references to deleted persistence modules.
  - Synchronized the timeless architecture pillar documents (`@[docs/architecture/01_system_context_and_invariants.md]`, `@[docs/architecture/02_data_seeding_and_ontology.md]`, and `@[docs/architecture/05_resilience_and_observability.md]`).

## Learned
- `PostgresStorageDriver(auto_initialize_pool=False)` serves as a 0 ms hermetic `StorageDriver` implementation for unit tests while delegating to `PostgresEntityAdapter` over `PostgresPoolManager` in live PostgreSQL 19 runtime.
- `QGR017` AST enforcement across `visit_Module`, `visit_Import`, `visit_ImportFrom`, `visit_Name`, and `visit_Constant` guarantees that any future attempt to import `tinydb` or reference `db_v2.json` fails fast at the static AST gate.

## Remaining
- Execute `Tier 2 Hardening (Backend)` via `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]" --gate backend --model gemini-4-argon-medium`.
- Execute `### Final Plan Audit` (`/tier8-audit-plan @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md] @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]`).

## Resume Command
```powershell
/tier5-resume --target="@[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]" --workflow=/tier8-audit-plan
```
