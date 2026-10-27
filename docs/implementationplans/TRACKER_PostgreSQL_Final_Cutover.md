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
</required_context_rules>

## Step Execution Status

**Plan:** @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md] @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]`
  - [ ] Step 1: Phase 1: Pre-Implementation Cleanups, Dependency Purge & Physical TinyDB Eradication
  - [ ] Step 2: Phase 2: Sovereign Settings, UUIDv7 ID Routing & Storage Driver Cutover
  - [ ] Step 3: Phase 3: Authoritative PostgreSQL 19 Seeding & FastAPI Preflight Cutover
  - [ ] Step 4: Phase 4: AST Guardrail QGR017 Lockdown & Unit Test Suite Synchronization
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md] @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]" --gate backend --model gemini-4-argon-medium`.
  - [ ] @[backend_v2/database/factory.py]
  - [ ] @[backend_v2/database/interfaces.py]
  - [ ] @[backend_v2/database/postgres/entity_adapter.py]
  - [ ] [NEW] @[backend_v2/database/postgres/storage_driver.py]
  - [ ] @[backend_v2/main.py]
  - [ ] @[backend_v2/models/core_base.py]
  - [ ] @[backend_v2/seed/run_seed.py]
  - [ ] @[backend_v2/services/storage.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] @[scripts/_ast_guardrails.py]
  - [ ] @[scripts/audit_zero_orm_strictness.py]
- [ ] **[NOK] Physical Eradication Verification (Backend Targets)**: Confirm physical deletion and zero remaining references for `[DELETE] @[backend_v2/database/exporter.py]`, `[DELETE] @[backend_v2/database/firestore_driver.py]`, `[DELETE] @[backend_v2/database/tinydb_driver.py]`, `[DELETE] @[backend_v2/database/wrapper.py]`, and `[DELETE] @[backend_v2/seed/wipe_user_data.py]`.
- [ ] **[SKIPPED] Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]" --gate frontend --model gemini-4-argon-medium`. (Zero frontend `.dart` production targets in this plan).
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md] @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md] @[ki_god_code_prevention.md] @[ki_python_314_concurrency_strictness.md] @[ki_zero_permissive_typing.md] @[ki_mcp_tool_protocol.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document `PostgresStorageDriver` (`[NEW] @[backend_v2/database/postgres/storage_driver.py]`) implementing the `StorageDriver` protocol over `PostgresPoolManager` for all 16 repositories in `backend_v2/database/repositories/`, the `EntityPersistencePort` seeding contracts (`seed_collection_batch` and `verify_seed_table_counts`), the single-pipeline factory enforcement in `@[backend_v2/database/factory.py#L33-L110]` and `@[backend_v2/database/factory.py#L113-L147]`, and the `QGR017` AST guardrail lockdown in `@[scripts/_ast_guardrails.py#L523-L2455]`.
     - `@[ki_python_314_concurrency_strictness.md]`: Document the asynchronous PostgreSQL 19 preflight verification in `@[backend_v2/main.py#L57-L112]`, `@[backend_v2/main.py#L115-L160]`, and `@[backend_v2/main.py#L163-L218]`, deterministic `generate_opaque_id` routing (`@[backend_v2/models/core_base.py#L189-L214]`) to `generate_uuid7_opaque_id` (`@[backend_v2/models/core_base.py#L324-L377]`) for `EntityPrefix.EXECUTION`, `EntityPrefix.REPORT`, `EntityPrefix.NODE`, and `EntityPrefix.EDGE`, and the eradication of OS-level file locks (`msvcrt.locking` and `fcntl`).
     - `@[ki_zero_permissive_typing.md]`: Document the Zero-ORM `PostgresStorageDriver` and `PostgresEntityAdapter` parameterized `$1, $2` batch upserts with binary `\x01` JSONB codecs (`pydantic_core.to_json` / `from_json`) and `ZORM001`–`ZORM006` AST enforcement across `storage_driver.py` in `@[scripts/audit_zero_orm_strictness.py#L226-L397]` and `@[scripts/audit_zero_orm_strictness.py#L460-L512]`.
     - `@[ki_mcp_tool_protocol.md]`: Document authoritative PostgreSQL 19 seeding of `system_configs` (including `SystemConfigMCPGateways`) via `@[backend_v2/seed/run_seed.py#L429-L459]` and `@[backend_v2/seed/run_seed.py#L462-L504]` and `PostgresEntityAdapter.seed_collection_batch`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register newly created `backend_v2/database/postgres/storage_driver.py` and remove deleted modules, specifically and exhaustively: `backend_v2/database/tinydb_driver.py`, `backend_v2/database/wrapper.py`, `backend_v2/database/firestore_driver.py`, `backend_v2/database/exporter.py`, and `backend_v2/seed/wipe_user_data.py`.
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
| **REQ-001** | Update `@[run_local.bat]` to launch `docker compose up -d redis postgres`, set `STORAGE_BACKEND=POSTGRES` for both FastAPI (`uvicorn`) and background worker (`run_worker`), and remove all `db_v2.json` and `STORAGE_BACKEND=LOCAL` references (`REQ-01`). | Step 1 | `[ ]` |
| **REQ-002** | Remove `"tinydb"` and add `"asyncpg>=0.30.0"` in `@[pyproject.toml]`, synchronize `uv.lock`, and verify `uv run python -c "import tinydb"` raises `ModuleNotFoundError` (`REQ-05`, `RT-05`). | Step 1 | `[ ]` |
| **REQ-003** | Physically delete all 8 legacy files from disk and version control, specifically and exhaustively: `[DELETE] @[backend_v2/database/tinydb_driver.py]`, `[DELETE] @[backend_v2/database/wrapper.py]`, `[DELETE] @[backend_v2/database/firestore_driver.py]`, `[DELETE] @[backend_v2/database/exporter.py]`, `[DELETE] @[backend_v2/seed/wipe_user_data.py]`, `[DELETE] @[data/db_v2.json]`, `[DELETE] @[data/db_v2.json.lock]`, and `[DELETE] @[data/app.db]` (`REQ-04`, `TD-04`). | Step 1 | `[ ]` |
| **REQ-004** | Default `settings.storage_backend` to `StorageBackend.POSTGRES` in `@[backend_v2/settings.py#L47-L1088]`, update `active_backend` (`#L773-L804`) and `is_cloud_storage` (`#L806-L814`), and update `allow_mock_tokens` (`#L986-L1001`) to permit local mock tokens under `StorageBackend.POSTGRES` when `not self.use_firebase_auth` and `not self.is_cloud_environment` (`REQ-03`, `TD-02`, `RT-03`). | Step 2 | `[ ]` |
| **REQ-005** | Update `get_storage_driver` in `@[backend_v2/services/storage.py#L19-L66]` to route `StorageBackend.POSTGRES` to `LocalFileDriver` when `not settings.storage_bucket_name` and `GCSFileDriver` when `settings.storage_bucket_name` is configured (`TD-03`, `RT-03`). | Step 2 | `[ ]` |
| **REQ-006** | Update `generate_opaque_id` in `@[backend_v2/models/core_base.py#L189-L214]` to delegate to `generate_uuid7_opaque_id` (`@[backend_v2/models/core_base.py#L324-L377]`) when `prefix` is in `{EntityPrefix.EXECUTION, EntityPrefix.REPORT, EntityPrefix.NODE, EntityPrefix.EDGE}` (`RT-07`). | Step 2 | `[ ]` |
| **REQ-007** | Implement `[NEW] @[backend_v2/database/postgres/storage_driver.py]` (`PostgresStorageDriver` conforming to `StorageDriver` over `PostgresPoolManager` for all 16 repositories in `backend_v2/database/repositories/`), register it in `@[scripts/audit_zero_orm_strictness.py#L226-L397]` and `@[scripts/audit_zero_orm_strictness.py#L460-L512]`, and wire `StorageBackend.POSTGRES` as the sole valid backend in `@[backend_v2/database/factory.py#L33-L110]` (`get_driver`) and `@[backend_v2/database/factory.py#L113-L147]` (`create_unit_of_work`), raising `ConfigurationError` on `LOCAL`, `TINYDB`, or `FIRESTORE` (`REQ-03`, `RT-01`). | Step 2 | `[ ]` |
| **REQ-008** | Expand `EntityPersistencePort` in `@[backend_v2/database/interfaces.py#L393-L400]` and `PostgresEntityAdapter` in `@[backend_v2/database/postgres/entity_adapter.py#L306-L627]` with `seed_collection_batch` and `verify_seed_table_counts` across all 10 core PostgreSQL 19 tables (`organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`, `executions`, `report_artifacts`, `report_binaries`) using parameterized SQL (`$1, $2`) and binary `\x01` JSONB codecs (`REQ-02`, `RT-02`). | Step 3 | `[ ]` |
| **REQ-009** | Refactor `seed_database` (`@[backend_v2/seed/run_seed.py#L429-L459]`) and `main` (`@[backend_v2/seed/run_seed.py#L462-L504]`) to remove `_seed_tinydb` (`#L222-L340`) and `_seed_firestore` (`#L343-L410`), ingest `ValidatedSeedBufferDTO` (`#L111-L162`) into PostgreSQL 19 while preserving 100% of `@[backend_v2/seed/seed_data.json]` prompts verbatim, and fail-fast with `AppException` if any of the 7 seeded tables has count 0 (`REQ-02`, `RT-02`). | Step 3 | `[ ]` |
| **REQ-010** | Remove top-level `from tinydb import TinyDB` in `@[backend_v2/main.py]` and refactor `_audit_storage_and_database_sync` (`@[backend_v2/main.py#L57-L112]`), `_validate_database_preflight` (`@[backend_v2/main.py#L115-L160]`), and `lifespan` (`@[backend_v2/main.py#L163-L218]`) to execute asynchronous PostgreSQL 19 preflight checks (`TD-01`, `RT-04`). | Step 3 | `[ ]` |
| **REQ-011** | Expand `QGR017` (`FATAL`) in `@[scripts/_ast_guardrails.py#L523-L2455]` (`visit_Module` `#L621-L689`, `visit_Import` `#L1905-L2016`, `visit_ImportFrom` `#L2018-L2265`) to ban `tinydb`, `tinydb_driver`, `firestore_driver`, `wrapper`, `TinyDBClient`, and `db_v2.json`, and remove deleted driver paths from `BOUNDARY_EXEMPTION_FILES` (`REQ-06`, `TD-04`, `RT-06`). | Step 4 | `[ ]` |
| **REQ-012** | Synchronize `InMemoryEntityAdapter` (`@[backend_v2/tests/fakes/in_memory_uow.py#L548-L632]`) and `InMemoryAsyncPgConnection` (`@[backend_v2/tests/fakes/in_memory_uow.py#L693-L1110]`), and update unit tests in `@[backend_v2/tests/unit/test_factory.py#L32-L42]`, `@[backend_v2/tests/unit/test_settings.py#L95-L131]`, `@[backend_v2/tests/unit/seed/test_run_seed.py#L38-L45]`, and `@[backend_v2/tests/unit/database/test_postgres.py#L440-L563]` with >=2 negative ISTQB boundary cases per feature. | Step 4 | `[ ]` |

# Session Handover Context

## Achieved
- Completed Phase 1 PostgreSQL 19 Sovereign Zero-ORM infrastructure (`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]` and `@[docs/implementationplans/TRACKER_PostgreSQL.md]`), including the 12-table DDL schema (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`), `PostgresPoolManager` (`@[backend_v2/database/postgres/pool.py]`), `PostgresGraphAdapter` (`@[backend_v2/database/postgres/graph_adapter.py]`), `PostgresEntityAdapter` (`@[backend_v2/database/postgres/entity_adapter.py]`), `PostgresUnitOfWork` (`@[backend_v2/database/postgres/uow.py]`), `InMemoryUnitOfWork` (`@[backend_v2/tests/fakes/in_memory_uow.py]`), and `audit_zero_orm_strictness.py` (`@[scripts/audit_zero_orm_strictness.py]`).
- Completed Tier 0 System 2 Research & Red-Team Falsification (`/tier0-research-plan @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md]`), establishing exact AST `#Lstart-Lend` boundaries, touched-scope technical debt (`TD-01`–`TD-04`), the 7-point Red-Team Falsification Matrix (`RT-01`–`RT-07`), the 5-Column Architectural Directives Table, and the 4-step `execution_protocol` XML block in `@[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md]`.
- Generated standalone execution tracker `@[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]` with 1:1 step tracking (`Step 1` through `Step 4`), granular file-level hardening checklists, parameterized Tier 7 directives, and bidirectional Requirements Traceability Matrix (`REQ-001`–`REQ-012`).

## Learned
- All 16 repositories in `backend_v2/database/repositories/` resolve their persistence backend through `get_driver(settings)` (`@[backend_v2/database/factory.py#L33-L110]`), requiring `[NEW] @[backend_v2/database/postgres/storage_driver.py]` (`PostgresStorageDriver`) over `PostgresPoolManager` so the entire application operates on a single sovereign PostgreSQL 19 pipeline without bifurcated fallback branches.
- Local development authentication (`USE_FIREBASE_AUTH=false` in `@[run_local.bat]`) and file storage require updating `Settings.allow_mock_tokens` (`@[backend_v2/settings.py#L986-L1001]`) and `get_storage_driver` (`@[backend_v2/services/storage.py#L19-L66]`) to support `StorageBackend.POSTGRES`.
- PostgreSQL 19 tables `executions`, `report_artifacts`, `report_binaries`, `quorum_nodes`, and `quorum_edges` enforce `CHECK (uuid_extract_version(id) = 7)`, requiring `generate_opaque_id` (`@[backend_v2/models/core_base.py#L189-L214]`) to delegate to `generate_uuid7_opaque_id` (`@[backend_v2/models/core_base.py#L324-L377]`) for `EntityPrefix.EXECUTION`, `EntityPrefix.REPORT`, `EntityPrefix.NODE`, and `EntityPrefix.EDGE`.

## Remaining
- Execute Steps 1 through 4 of `@[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md]` via `/tier2-execute --full-auto @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md] @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]`.
- Complete `### Post-Implementation Gates` (including `Tier 2 Hardening (Backend)` across all 11 surviving production `.py` files), `### Documentation & Knowledge Item Update` (`/tier7-describe-architecture`), and `### Final Plan Audit` (`/tier8-audit-plan`).

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md] @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]
```
