# PostgreSQL 19 Sovereign Cutover & TinyDB Eradication Requirements

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

## Executive Summary (Johdon Yhteenveto)

This document defines the strict, non-negotiable architectural requirements for executing the **Final Cutover (Lopullinen Cutover)** from the legacy file-locked TinyDB database (`data/db_v2.json`) to the sovereign **All-in-PostgreSQL 19 Zero-ORM Architecture** (`@[docs/epic/EPIC_151_PostgreSQL_Clean_Slate_Migration_and_TinyDB_Eradication.md]`).

Upon completion of Phase 1 (`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`), the core PostgreSQL 19 database infrastructure, 12-table DDL schema (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]`), `asyncpg` + `pydantic_core` binary `\x01` JSONB connection pool (`@[backend_v2/database/postgres/pool.py]`), CQRS ports (`@[backend_v2/database/interfaces.py#L393-L400]`, `@[backend_v2/database/interfaces.py#L403-L443]`), and Unit of Work (`@[backend_v2/database/postgres/uow.py]`) are 100% operational and verified.

The Cutover phase completes the migration by:
1. Re-pointing local development and production startup (`@[run_local.bat]`) exclusively to PostgreSQL 19.
2. Ingesting the authoritative seed vault (`@[backend_v2/seed/seed_data.json]`) directly into PostgreSQL 19 via `@[backend_v2/seed/run_seed.py#L429-L459]`, `@[backend_v2/seed/run_seed.py#L462-L504]`, `@[backend_v2/database/postgres/entity_adapter.py#L306-L627]`, and `[NEW] @[backend_v2/database/postgres/storage_driver.py]`.
3. Physically deleting legacy TinyDB drivers, OS file-locking code, legacy TinyDB utility scripts, and database JSON files.
4. Purging the `tinydb` package from `@[pyproject.toml]`, adding `asyncpg>=0.30.0`, and locking the codebase with AST guardrail `QGR017` in `@[scripts/_ast_guardrails.py#L523-L2455]`.

---

## 1. Scope & Inventory Matrix (Kohde- ja Poistoalueet)

### 1.1 Files to Create or Modify (`[NEW]` / `[MODIFY]`)

| Target File & AST Boundaries | Architectural Responsibility in Cutover |
| :--- | :--- |
| `[MODIFY] @[run_local.bat]` | Start `docker compose up -d redis postgres`, set `STORAGE_BACKEND=POSTGRES`, and remove all `db_v2.json` references. |
| `[MODIFY] @[pyproject.toml]` | Permanently remove `"tinydb"` and add `"asyncpg>=0.30.0"` in project dependencies. |
| `[NEW] @[backend_v2/database/postgres/storage_driver.py]` | Implement `PostgresStorageDriver` conforming to `StorageDriver` over `PostgresPoolManager` so all 16 repositories in `backend_v2/database/repositories/` execute 100% against PostgreSQL 19 without bifurcated pipelines. |
| `[MODIFY] @[backend_v2/database/interfaces.py#L393-L400]` | Expand `EntityPersistencePort` with `seed_collection_batch` and `verify_seed_table_counts` contracts for the 10 core PostgreSQL 19 tables. |
| `[MODIFY] @[backend_v2/database/postgres/entity_adapter.py#L306-L627]` | Implement `seed_collection_batch` and `verify_seed_table_counts` in `PostgresEntityAdapter` using parameterized SQL (`$1, $2`) and binary `\x01` JSONB codecs. |
| `[MODIFY] @[backend_v2/database/factory.py#L33-L110]`, `@[backend_v2/database/factory.py#L113-L147]` | Wire `StorageBackend.POSTGRES` as the sole valid backend in `get_driver` (`#L33-L110`) and `create_unit_of_work` (`#L113-L147`); raise Fail-Fast `ConfigurationError` on `LOCAL`, `TINYDB`, or `FIRESTORE`. |
| `[MODIFY] @[backend_v2/settings.py#L47-L1088]` | Default `settings.storage_backend` to `StorageBackend.POSTGRES` in `active_backend` (`#L773-L804`), update `is_cloud_storage` (`#L806-L814`), and update `allow_mock_tokens` (`#L986-L1001`) to permit local mock tokens under `StorageBackend.POSTGRES` when `not self.use_firebase_auth`. |
| `[MODIFY] @[backend_v2/services/storage.py#L19-L66]` | Update `get_storage_driver` (`#L19-L66`) to route `StorageBackend.POSTGRES` to `LocalFileDriver` in local development (or `GCSFileDriver` when `settings.storage_bucket_name` is set). |
| `[MODIFY] @[backend_v2/models/core_base.py#L189-L214]`, `@[backend_v2/models/core_base.py#L324-L377]` | Route `generate_opaque_id` (`#L189-L214`) to `generate_uuid7_opaque_id` (`#L324-L377`) for UUIDv7-mandated prefixes (`EntityPrefix.EXECUTION`, `EntityPrefix.REPORT`, `EntityPrefix.NODE`, `EntityPrefix.EDGE`). |
| `[MODIFY] @[backend_v2/seed/run_seed.py#L429-L459]`, `@[backend_v2/seed/run_seed.py#L462-L504]` | Replace `_seed_tinydb` (`#L222-L340`) and `_seed_firestore` (`#L343-L410`) with `_seed_postgres` in `seed_database` (`#L429-L459`) and `main` (`#L462-L504`); verify non-zero counts via `SELECT count(*) FROM ...`. |
| `[MODIFY] @[backend_v2/main.py#L57-L112]`, `@[backend_v2/main.py#L115-L160]`, `@[backend_v2/main.py#L163-L218]` | Remove top-level `from tinydb import TinyDB` and refactor `_audit_storage_and_database_sync` (`#L57-L112`), `_validate_database_preflight` (`#L115-L160`), and `lifespan` (`#L163-L218`) to execute PostgreSQL 19 preflight checks. |
| `[MODIFY] @[scripts/_ast_guardrails.py#L523-L2455]` | Expand `QGR017` (Severity: `FATAL`) in `visit_Module` (`#L621-L689`), `visit_Import` (`#L1905-L2016`), and `visit_ImportFrom` (`#L2018-L2265`) to ban `tinydb`, `tinydb_driver`, `firestore_driver`, `wrapper`, `TinyDBClient`, and `db_v2.json`, and remove deleted driver paths from `BOUNDARY_EXEMPTION_FILES`. |
| `[MODIFY] @[scripts/audit_zero_orm_strictness.py#L226-L397]`, `@[scripts/audit_zero_orm_strictness.py#L460-L512]` | Register `backend_v2/database/postgres/storage_driver.py` in `_ZeroOrmAstVisitor` (`#L226-L397`) and `run_zero_orm_audit` (`#L460-L512`) so `ZORM001`–`ZORM006` enforce Zero-ORM strictness across all PostgreSQL modules. |
| `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L548-L632]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L693-L1110]` | Implement `seed_collection_batch` and `verify_seed_table_counts` in `InMemoryEntityAdapter` (`#L548-L632`) and `InMemoryAsyncPgConnection` (`#L693-L1110`). |
| `[MODIFY] @[backend_v2/tests/unit/test_factory.py#L32-L42]`, `@[backend_v2/tests/unit/test_factory.py#L64-L69]`, `@[backend_v2/tests/unit/test_factory.py#L100-L109]`, `@[backend_v2/tests/unit/test_factory.py#L112-L117]` | Update factory unit tests (`#L32-L42`, `#L64-L69`, `#L100-L109`, `#L112-L117`) to assert `PostgresStorageDriver` and `PostgresUnitOfWork` creation on `POSTGRES` and `ConfigurationError` on `LOCAL`, `TINYDB`, and `FIRESTORE`. |
| `[MODIFY] @[backend_v2/tests/unit/test_settings.py#L95-L131]`, `@[backend_v2/tests/unit/test_settings.py#L146-L171]`, `@[backend_v2/tests/unit/test_settings.py#L174-L219]`, `@[backend_v2/tests/unit/test_settings.py#L450-L492]` | Update settings unit tests (`#L95-L131`, `#L146-L171`, `#L174-L219`, `#L450-L492`) to assert `Settings.active_backend == StorageBackend.POSTGRES` by default and verify `allow_mock_tokens` boundary invariants. |
| `[MODIFY] @[backend_v2/tests/unit/seed/test_run_seed.py#L38-L45]`, `@[backend_v2/tests/unit/seed/test_run_seed.py#L500-L508]` | Update seed unit tests (`#L38-L45`, `#L500-L508`) to verify PostgreSQL 19 seeding and Fail-Fast `AppException` when any required table count is 0. |
| `[MODIFY] @[backend_v2/tests/unit/database/test_postgres.py#L440-L563]`, `@[backend_v2/tests/unit/database/test_postgres.py#L571-L708]`, `@[backend_v2/tests/unit/database/test_postgres.py#L1405-L1450]` | Expand PostgreSQL unit tests (`#L440-L563`, `#L571-L708`, `#L1405-L1450`) to cover `PostgresStorageDriver` CRUD roundtrips, 10-table seed verification, and `QGR017` AST enforcement. |

### 1.2 Files to Delete Permanently (`[DELETE]`)

| File to Delete | Obsolete Component & Reason for Eradication |
| :--- | :--- |
| `[DELETE] @[backend_v2/database/tinydb_driver.py]` | Legacy TinyDB document driver; superseded by `PostgresStorageDriver`, `PostgresEntityAdapter`, and `PostgresUnitOfWork`. |
| `[DELETE] @[backend_v2/database/wrapper.py]` | Legacy OS-level file locking (`msvcrt.locking` on Windows, `fcntl` on POSIX) and `TinyDBClient`. |
| `[DELETE] @[backend_v2/database/firestore_driver.py]` | Archived Firestore driver; zero production usage. |
| `[DELETE] @[backend_v2/database/exporter.py]` | Obsolete V1 TinyDB export script (`from tinydb import TinyDB` mutating legacy `components` table). |
| `[DELETE] @[backend_v2/seed/wipe_user_data.py]` | Obsolete TinyDB JSON file scrubber directly reading and mutating `data/db_v2.json`. |
| `[DELETE] @[data/db_v2.json]` | Legacy file-based database JSON blob. |
| `[DELETE] @[data/db_v2.json.lock]` | Legacy file locking artifact. |
| `[DELETE] @[data/app.db]` | Legacy SQLite/mock database file. |

---

## 2. Phase 1: Pre-Implementation Cleanups & Red-Team Falsification Matrix

### 2.1 Phase 1: Pre-Implementation Cleanups (Touched-Scope Technical Debt)
1. **TD-01 (`backend_v2/main.py` Top-Level `TinyDB` Import & Startup Preflight Coupling)**:
   - `@[backend_v2/main.py#L57-L112]` (`_audit_storage_and_database_sync`) and `@[backend_v2/main.py#L115-L160]` (`_validate_database_preflight`) import `from tinydb import TinyDB` at module load time and open `Settings.prod_db_path` (`data/db_v2.json`). These functions must be refactored to validate PostgreSQL 19 connectivity and table counts via `PostgresPoolManager` before `tinydb` is removed from `pyproject.toml`.
2. **TD-02 (`backend_v2/settings.py` `allow_mock_tokens` Hardcoded `StorageBackend.LOCAL` Check)**:
   - `@[backend_v2/settings.py#L986-L1001]` (`allow_mock_tokens`) returns `False` whenever `self.active_backend != StorageBackend.LOCAL`. Switching the default backend to `StorageBackend.POSTGRES` breaks local authentication (`USE_FIREBASE_AUTH=false` in `run_local.bat`) unless `allow_mock_tokens` permits `StorageBackend.POSTGRES` in local development when `not self.use_firebase_auth` and `not self.is_cloud_environment`.
3. **TD-03 (`backend_v2/services/storage.py` `get_storage_driver` Missing `StorageBackend.POSTGRES` Routing)**:
   - `@[backend_v2/services/storage.py#L19-L66]` (`get_storage_driver`) only handles `StorageBackend.FIRESTORE` and `StorageBackend.LOCAL`, raising `ConfigurationError` on `StorageBackend.POSTGRES`. It must route `StorageBackend.POSTGRES` to `LocalFileDriver` when `not settings.storage_bucket_name` and `GCSFileDriver` when `settings.storage_bucket_name` is configured.
4. **TD-04 (`scripts/_ast_guardrails.py` Legacy `BOUNDARY_EXEMPTION_FILES` & Dead TinyDB Scripts)**:
   - `BOUNDARY_EXEMPTION_FILES` in `@[scripts/_ast_guardrails.py#L523-L2455]` still exempts `backend_v2/database/tinydb_driver.py`, `backend_v2/database/firestore_driver.py`, and `backend_v2/database/wrapper.py`. Furthermore, `[DELETE] @[backend_v2/database/exporter.py]` and `[DELETE] @[backend_v2/seed/wipe_user_data.py]` must be deleted so `QGR017` passes with 0 violations across the repository.

### 2.2 System 2 Red-Team Falsification Matrix (`RT-01` – `RT-07`)

| ID | Falsified Assumption / Failure Mode | Root Cause in Physical Codebase | Deterministic Sovereign Remediation |
| :--- | :--- | :--- | :--- |
| **RT-01** | `get_driver(settings)` can raise `ConfigurationError` for all backends once `PostgresUnitOfWork` exists. | FastAPI `DriverDep` (`backend_v2/api/dependencies.py`) and Arq background workers (`worker.py`, `report_worker.py`, `synthesis_worker.py`) call `await get_driver(settings)` to instantiate all 16 repositories in `backend_v2/database/repositories/`. | Implement `[NEW] @[backend_v2/database/postgres/storage_driver.py]` (`PostgresStorageDriver`) over `PostgresPoolManager` and return it from `@[backend_v2/database/factory.py#L33-L110]` (`get_driver`) when `Settings.active_backend == StorageBackend.POSTGRES`. |
| **RT-02** | `PostgresEntityAdapter` already supports seeding all 10 PostgreSQL 19 tables. | `@[backend_v2/database/postgres/entity_adapter.py#L306-L627]` currently implements only `save_report_binary`, `get_report_binary`, `save_execution`, and `get_execution`. Also, `seed_data.json` uses key `"system_config"` whereas `001_pg19_uuidv7_schema.sql` defines table `"system_configs"`. | Add `seed_collection_batch` and `verify_seed_table_counts` to `EntityPersistencePort`, `PostgresEntityAdapter`, and `InMemoryEntityAdapter`, mapping `"system_config"` to `"system_configs"` and enforcing `SELECT count(*) FROM ...` verification. |
| **RT-03** | Defaulting `settings.storage_backend` to `StorageBackend.POSTGRES` preserves local auth and file storage automatically. | `@[backend_v2/settings.py#L986-L1001]` (`allow_mock_tokens`) checks `self.active_backend != StorageBackend.LOCAL`, and `@[backend_v2/services/storage.py#L19-L66]` (`get_storage_driver`) rejects `StorageBackend.POSTGRES`. | Update `allow_mock_tokens` in `@[backend_v2/settings.py#L986-L1001]` and `get_storage_driver` in `@[backend_v2/services/storage.py#L19-L66]` to support `StorageBackend.POSTGRES`. |
| **RT-04** | Deleting `tinydb` from `pyproject.toml` only affects `backend_v2/database/`. | `@[backend_v2/main.py#L57-L112]` and `@[backend_v2/main.py#L115-L160]` import `from tinydb import TinyDB` at top level and open `data/db_v2.json` during FastAPI `lifespan` (`@[backend_v2/main.py#L163-L218]`) startup. | Replace TinyDB imports and `db_v2.json` file checks in `@[backend_v2/main.py#L57-L112]`, `@[backend_v2/main.py#L115-L160]`, and `@[backend_v2/main.py#L163-L218]` with asynchronous PostgreSQL 19 preflight verification. |
| **RT-05** | `asyncpg` is already declared in `pyproject.toml`. | `@[pyproject.toml]` still lists `"tinydb"` at line 10 and omits `"asyncpg>=0.30.0"`. | Remove `"tinydb"` and add `"asyncpg>=0.30.0"` in `@[pyproject.toml]`, then synchronize `uv.lock`. |
| **RT-06** | `QGR017` is an unused rule code in `scripts/_ast_guardrails.py`. | `@[scripts/_ast_guardrails.py#L621-L689]` already uses `QGR017` to ban resurrected legacy modules (`v2_core.py`, `report_service.py`, `auth.py`, `export_service.py`, `llm/provider.py`). | Extend the existing `QGR017` checks in `visit_Module` (`#L621-L689`), `visit_Import` (`#L1905-L2016`), and `visit_ImportFrom` (`#L2018-L2265`) to ban `tinydb`, `tinydb_driver`, `firestore_driver`, `wrapper`, `TinyDBClient`, and `db_v2.json`. |
| **RT-07** | Legacy 16-hex UUIDv4 IDs from `generate_opaque_id` can be inserted into all PostgreSQL 19 tables. | `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` enforces `UUID PRIMARY KEY DEFAULT uuidv7()` and `CHECK (uuid_extract_version(id) = 7)` on `executions`, `report_artifacts`, `report_binaries`, `quorum_nodes`, and `quorum_edges`. | Update `@[backend_v2/models/core_base.py#L189-L214]` (`generate_opaque_id`) to delegate to `generate_uuid7_opaque_id` (`@[backend_v2/models/core_base.py#L324-L377]`) when `prefix` is in `{EntityPrefix.EXECUTION, EntityPrefix.REPORT, EntityPrefix.NODE, EntityPrefix.EDGE}`. |

---

## 3. Concrete Cutover Requirements & 5-Column Architectural Directives Table

### REQ-01: Container & Launch Orchestration (`run_local.bat`)
* **Mandate:** Running `.\run_local.bat` MUST start both Redis and PostgreSQL containers:
  ```cmd
  docker compose up -d redis postgres
  ```
* **Mandate:** `@[run_local.bat]` MUST set `set STORAGE_BACKEND=POSTGRES` for both FastAPI backend (`uvicorn`) and background worker (`run_worker`).
* **Banned:** `set STORAGE_BACKEND=LOCAL` is strictly prohibited.
* **Banned:** Any deletion, cleaning, or verification of `data\db_v2.json` in `@[run_local.bat]` is strictly prohibited.

### REQ-02: Authoritative Database Seeding (`backend_v2/seed/run_seed.py`)
* **Mandate:** `uv run python backend_v2/seed/run_seed.py` MUST populate the 10 core tables in PostgreSQL 19:
  1. `users`
  2. `organizations`
  3. `workflows`
  4. `steps`
  5. `prompt_blocks`
  6. `output_profiles`
  7. `system_configs`
  8. `executions` (clean-slate, 0 rows)
  9. `report_artifacts` (clean-slate, 0 rows)
  10. `report_binaries` (clean-slate, 0 rows)
* **Prompt Preservation Mandate:** 100% of human-authored prompt texts, coaching philosophy, bilingual `I18nText` translations, and criteria configurations in `@[backend_v2/seed/seed_data.json]` MUST be preserved verbatim without modification.
* **Fail-Fast Assertion:** `@[backend_v2/seed/run_seed.py#L429-L459]` MUST verify with `SELECT count(*) FROM ...` that all 7 seeded collections (`organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`) have non-zero record counts and crash with `AppException` (`ErrorCodes.STORAGE_ACCESS_FAILED` or `ErrorCodes.VALIDATION_FAILED`) if any collection fails to materialize.

### REQ-03: Zero-Fallback Service & Factory Layer (`factory.py` & `settings.py`)
* **Mandate:** `settings.storage_backend` in `@[backend_v2/settings.py#L47-L1088]` MUST default to `StorageBackend.POSTGRES`.
* **Zero Backward Compatibility:** In accordance with `zero_backward_compatibility_planning_ban`, `@[backend_v2/database/factory.py#L33-L110]` (`get_driver`) and `@[backend_v2/database/factory.py#L113-L147]` (`create_unit_of_work`) MUST NOT provide fallback chains to TinyDB or local JSON files if PostgreSQL fails.
* **Fail-Fast Error:** Requesting `StorageBackend.LOCAL`, `TINYDB`, `StorageBackend.FIRESTORE`, or an invalid backend MUST immediately log a structured error and raise `ConfigurationError("STORAGE_BACKEND 'LOCAL' has been permanently decommissioned. Quorum requires PostgreSQL 19.")`.

### REQ-04: Physical Eradication of TinyDB and OS File Locks
* **Mandate:** Physically delete `[DELETE] @[backend_v2/database/tinydb_driver.py]`, `[DELETE] @[backend_v2/database/wrapper.py]`, `[DELETE] @[backend_v2/database/firestore_driver.py]`, `[DELETE] @[backend_v2/database/exporter.py]`, and `[DELETE] @[backend_v2/seed/wipe_user_data.py]`.
* **Mandate:** Delete `[DELETE] @[data/db_v2.json]`, `[DELETE] @[data/db_v2.json.lock]`, and `[DELETE] @[data/app.db]`.
* **Prohibition:** Keeping deprecated adapter classes, hollow proxy shells, or `@deprecated` shims is strictly banned per `the_no_legacy_mandate`.

### REQ-05: Dependency Purge
* **Mandate:** Remove `"tinydb"` and add `"asyncpg>=0.30.0"` in `@[pyproject.toml]`.
* **Mandate:** Run `uv lock` to synchronize `uv.lock`.
* **Verification:** `uv run python -c "import tinydb"` MUST fail with `ModuleNotFoundError`.

### REQ-06: Permanent AST Guardrail Lockdown (`QGR017`)
* **Mandate:** In `@[scripts/_ast_guardrails.py#L523-L2455]`, codify rule `QGR017` (Severity: `FATAL`):
  * Prohibits AST `Import` (`#L1905-L2016`) or `ImportFrom` (`#L2018-L2265`) referencing `tinydb`, `tinydb_driver`, `firestore_driver`, or `backend_v2.database.wrapper`.
  * Prohibits AST string constants or variable/class names referencing `db_v2.json` or `TinyDBClient`, and bans physical resurrection of `tinydb_driver.py`, `firestore_driver.py`, or `wrapper.py` in `visit_Module` (`#L621-L689`).
* **Verification:** Running `uv run python scripts/_ast_guardrails.py` MUST pass with 0 fatal violations across the entire codebase.

### 3.1 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`[MODIFY] @[run_local.bat]` & `[MODIFY] @[pyproject.toml]`** | Ban `STORAGE_BACKEND=LOCAL`, `db_v2.json` existence checks in batch scripts, and lingering `"tinydb"` package dependencies. | Launch `docker compose up -d redis postgres`, export `STORAGE_BACKEND=POSTGRES`, remove `"tinydb"`, and declare `"asyncpg>=0.30.0"` in `@[pyproject.toml]`. | Prune multi-mode batch flags switching between TinyDB and PostgreSQL; enforce a single sovereign PostgreSQL launch pipeline. | `uv run python -c "import tinydb"` raises `ModuleNotFoundError`; `.\run_local.bat --no-client` starts cleanly with 0 TinyDB references. |
| **`[NEW] @[backend_v2/database/postgres/storage_driver.py]`, `[MODIFY] @[scripts/audit_zero_orm_strictness.py#L226-L397]`, & `[MODIFY] @[scripts/audit_zero_orm_strictness.py#L460-L512]`** | Ban rewriting 16 repositories with ad-hoc inline SQL or keeping TinyDB fallback drivers for `DriverDep` consumers. | Implement Zero-ORM `PostgresStorageDriver(StorageDriver)` over `PostgresPoolManager` with strict table allowlisting (`CLOSED_POSTGRES_TABLES`), mapping `"system_config"` to `"system_configs"` and translating UUIDv7 PKs for `executions` and `report_artifacts`. Register `storage_driver.py` in `audit_zero_orm_strictness.py`. | Prune parallel V2 repository classes; all 16 existing repositories in `backend_v2/database/repositories/` consume `PostgresStorageDriver` through the single `StorageDriver` protocol. | `uv run python scripts/audit_zero_orm_strictness.py` passes `ZORM001`–`ZORM006` with 0 findings; `test_postgres.py` verifies stateful CRUD roundtrips. |
| **`[MODIFY] @[backend_v2/database/interfaces.py#L393-L400]` & `[MODIFY] @[backend_v2/database/postgres/entity_adapter.py#L306-L627]`** | Ban `json.dumps` / `json.loads` string serialization (`ZORM004`), unparameterized SQL f-strings (`ZORM003`), and unallowlisted `Record` subscripts (`ZORM006`). | Expand `EntityPersistencePort` (`#L393-L400`) and `PostgresEntityAdapter` (`#L306-L627`) with `seed_collection_batch` and `verify_seed_table_counts` across all 10 core PostgreSQL 19 tables using parameterized `$1, $2` queries and binary `\x01` JSONB codecs. | Prune per-table custom seeder classes; execute batch upserts and `SELECT count(*) AS row_count FROM ...` checks through a single deterministic table mapping. | `uv run pytest backend_v2/tests/unit/database/test_postgres.py` verifies positive and negative (>=2 ISTQB boundary cases) seed persistence and count assertions. |
| **`[MODIFY] @[backend_v2/database/factory.py#L33-L110]` & `[MODIFY] @[backend_v2/database/factory.py#L113-L147]`** | Ban fallback chains from PostgreSQL to TinyDB, lazy imports of `tinydb_driver` or `firestore_driver`, and `client` duck-typing parameters. | `get_driver` (`#L33-L110`) returns `PostgresStorageDriver` and `create_unit_of_work` (`#L113-L147`) returns `PostgresUnitOfWork` exclusively when `Settings.active_backend == StorageBackend.POSTGRES`. Any `LOCAL`, `TINYDB`, or `FIRESTORE` value raises `ConfigurationError`. | Prune multi-backend factory branching; maintain a single sovereign PostgreSQL 19 factory path. | `uv run pytest backend_v2/tests/unit/test_factory.py` asserts `ConfigurationError` (`ErrorCodes.CONFIGURATION_ERROR`) on `LOCAL`, `TINYDB`, and `FIRESTORE`. |
| **`[MODIFY] @[backend_v2/settings.py#L47-L1088]` & `[MODIFY] @[backend_v2/services/storage.py#L19-L66]`** | Ban defaulting `storage_backend` to `"LOCAL"` or blocking local mock tokens when `Settings.active_backend == StorageBackend.POSTGRES`. | Default `settings.storage_backend` to `StorageBackend.POSTGRES` in `Settings` (`#L47-L1088`), update `active_backend` (`#L773-L804`) and `allow_mock_tokens` (`#L986-L1001`), and route `StorageBackend.POSTGRES` in `get_storage_driver` (`#L19-L66`) to `LocalFileDriver` (or `GCSFileDriver` when `settings.storage_bucket_name` is set). | Prune legacy `TINYDB` alias translation shims in `Settings.active_backend`; fail-fast on unsupported backend strings. | `uv run pytest backend_v2/tests/unit/test_settings.py` verifies `Settings.active_backend == StorageBackend.POSTGRES` by default and tests `allow_mock_tokens` defense-in-depth partitions. |
| **`[MODIFY] @[backend_v2/models/core_base.py#L189-L214]` & `[MODIFY] @[backend_v2/models/core_base.py#L324-L377]`** | Ban generating 16-hex UUIDv4 IDs for entities stored in PostgreSQL 19 `UUID PRIMARY KEY` tables enforcing `CHECK (uuid_extract_version(id) = 7)`. | Update `generate_opaque_id` (`#L189-L214`) to delegate to `generate_uuid7_opaque_id` (`#L324-L377`) when `prefix` is in `{EntityPrefix.EXECUTION, EntityPrefix.REPORT, EntityPrefix.NODE, EntityPrefix.EDGE}`. | Prune duplicate ID generator functions in services; keep `generate_opaque_id` as the single entry point delegating to RFC 9562 UUIDv7 generation. | `parse_prefixed_uuid7` (`#L217-L274`) validates all generated execution, report, node, and edge IDs with 0 `VALIDATION_FAILED` errors. |
| **`[MODIFY] @[backend_v2/seed/run_seed.py#L429-L459]`, `[MODIFY] @[backend_v2/seed/run_seed.py#L462-L504]`, `[MODIFY] @[backend_v2/main.py#L57-L112]`, `[MODIFY] @[backend_v2/main.py#L115-L160]`, & `[MODIFY] @[backend_v2/main.py#L163-L218]`** | Ban `from tinydb import TinyDB`, `_seed_tinydb`, `_seed_firestore`, and `Settings.prod_db_path` (`data/db_v2.json`) file inspection during FastAPI startup or seeding. | Refactor `seed_database` (`#L429-L459`) and `main` (`#L462-L504`) in `run_seed.py` to ingest `ValidatedSeedBufferDTO` (`#L111-L162`) into PostgreSQL 19 and assert non-zero row counts across all 7 seed tables (and 0 rows on clean-slate tables). Refactor `_audit_storage_and_database_sync` (`#L57-L112`), `_validate_database_preflight` (`#L115-L160`), and `lifespan` (`#L163-L218`) in `main.py` to verify PostgreSQL 19 readiness. | Prune CLI target choices `local` and `firestore` that dispatch to TinyDB or Firestore; route seeding deterministically to PostgreSQL 19 (with `--dry-run` preflight support). | `uv run pytest backend_v2/tests/unit/seed/test_run_seed.py` and `uv run python backend_v2/seed/run_seed.py` pass 100%. |
| **`[MODIFY] @[scripts/_ast_guardrails.py#L523-L2455]`** | Ban any future re-introduction of `tinydb` imports, `TinyDBClient`, `db_v2.json` path literals, or exempted legacy driver files in `BOUNDARY_EXEMPTION_FILES`. | Extend `QGR017` (`FATAL`) in `QuorumGuardrailVisitor` (`#L523-L2455`: `visit_Module` `#L621-L689`, `visit_Import` `#L1905-L2016`, `visit_ImportFrom` `#L2018-L2265`) to flag `tinydb`, `tinydb_driver`, `firestore_driver`, `wrapper`, `TinyDBClient`, and `db_v2.json`, and remove deleted driver files from `BOUNDARY_EXEMPTION_FILES`. | Prune separate one-off lint scripts for TinyDB detection; consolidate enforcement directly into `QGR017` in `_ast_guardrails.py`. | `uv run python scripts/_ast_guardrails.py` exits with code 0 and catches synthetic `import tinydb` / `"db_v2.json"` AST nodes with `QGR017`. |
| **`[DELETE] @[backend_v2/database/tinydb_driver.py]`, `[DELETE] @[backend_v2/database/wrapper.py]`, `[DELETE] @[backend_v2/database/firestore_driver.py]`, `[DELETE] @[backend_v2/database/exporter.py]`, `[DELETE] @[backend_v2/seed/wipe_user_data.py]`, `[DELETE] @[data/db_v2.json]`, `[DELETE] @[data/db_v2.json.lock]`, `[DELETE] @[data/app.db]`** | Ban keeping dead TinyDB drivers, OS file-locking wrappers (`msvcrt`/`fcntl`), V1 TinyDB export/wipe scripts, or legacy `.json`/`.lock`/`.db` files in the repository. | Physically delete all 8 legacy files from disk and version control. | Prune 100% of legacy file-locking and document-emulation code. | Physical file existence check confirms all 8 paths do not exist; `QGR017` blocks their resurrection. |
| **`[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L548-L632]`, `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L693-L1110]`, `[MODIFY] @[backend_v2/tests/unit/test_factory.py#L32-L42]`, `[MODIFY] @[backend_v2/tests/unit/test_settings.py#L95-L131]`, `[MODIFY] @[backend_v2/tests/unit/seed/test_run_seed.py#L38-L45]`, `[MODIFY] @[backend_v2/tests/unit/database/test_postgres.py#L440-L563]`** | Ban deceptive `AsyncMock` persistence tests (`deceptive_persistence_mocking_ban`) and outdated unit tests asserting `StorageBackend.LOCAL` as default. | Synchronize `InMemoryEntityAdapter` (`#L548-L632`) and `InMemoryAsyncPgConnection` (`#L693-L1110`) with 10-table seed/CRUD support, and update unit test suites with >=2 negative ISTQB boundary tests per feature. | Prune obsolete TinyDB driver unit test fixtures. | `uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict` passes with >90% coverage and 0 warnings. |

---

## 4. Verification & Quality Gates (Laatuportit & Todennus)

The Cutover is declared mathematically verified and complete ONLY when all of the following commands exit with code 0:

```powershell
# 1. Container healthcheck: verify PostgreSQL 19 is healthy and listening on port 5432
docker compose exec postgres pg_isready -U quorum -d quorum

# 2. Database seeding: ingest authoritative seed vault into PostgreSQL 19
uv run python backend_v2/seed/run_seed.py

# 3. Database atom count audit: verify all seed collections exist in PostgreSQL
uv run python scripts/audit_database_atoms.py --strict

# 4. AST Guardrail audit: assert zero tinydb imports or db_v2.json references
uv run python scripts/_ast_guardrails.py

# 5. Zero-ORM strictness audit: assert 100% adherence to Zero-ORM invariants (ZORM001-ZORM006)
uv run python scripts/audit_zero_orm_strictness.py

# 6. Full backend audit loop: format, typing, clean imports, and test suite pass 100%
uv run python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict

# 7. Local Launcher dry-run: start run_local.bat and verify zero TinyDB logs
.\run_local.bat --no-client

# 8. Full Live E2E Workflow Execution & Parity Verification (Gate 8):
# Execute a full live end-to-end production workflow run against PostgreSQL 19 to assert 100% parity
# against the pre-PostgreSQL verified baseline (exe_2af2f7665e7c477b):
# - DAG Heavy LLM execution, asynchronous synthesis, and multi-channel artifact exports.
# - Zero healing cost events (healing_cost_events = 0) and zero transient HTTP errors.
# - Materialize verified physical artifacts: report.pdf, report.sdui.json, report.xlsx, and report.csv.
# - Validate append-only audit trail in PostgreSQL table trace_events.
# - Validate Flutter Desktop and Web HTTP 200 responses on /reports/{id}/sdui and /rows.
```

---

## 5. Deterministic Execution Protocol

<execution_protocol>
  <step id="1" name="Phase 1: Pre-Implementation Cleanups, Dependency Purge &amp; Physical TinyDB Eradication">
    <targets>
      <target>[MODIFY] @[run_local.bat]</target>
      <target>[MODIFY] @[pyproject.toml]</target>
      <target>[DELETE] @[backend_v2/database/tinydb_driver.py]</target>
      <target>[DELETE] @[backend_v2/database/wrapper.py]</target>
      <target>[DELETE] @[backend_v2/database/firestore_driver.py]</target>
      <target>[DELETE] @[backend_v2/database/exporter.py]</target>
      <target>[DELETE] @[backend_v2/seed/wipe_user_data.py]</target>
      <target>[DELETE] @[data/db_v2.json]</target>
      <target>[DELETE] @[data/db_v2.json.lock]</target>
      <target>[DELETE] @[data/app.db]</target>
    </targets>
    <action>
      Update @[run_local.bat] to start `docker compose up -d redis postgres`, set `STORAGE_BACKEND=POSTGRES` for both FastAPI and Arq worker processes, and remove all `db_v2.json` references. Update @[pyproject.toml] to remove `"tinydb"` and add `"asyncpg>=0.30.0"`, then run `uv lock`. Physically delete [DELETE] @[backend_v2/database/tinydb_driver.py], [DELETE] @[backend_v2/database/wrapper.py], [DELETE] @[backend_v2/database/firestore_driver.py], [DELETE] @[backend_v2/database/exporter.py], [DELETE] @[backend_v2/seed/wipe_user_data.py], [DELETE] @[data/db_v2.json], [DELETE] @[data/db_v2.json.lock], and [DELETE] @[data/app.db].
    </action>
  </step>

  <step id="2" name="Phase 2: Sovereign Settings, UUIDv7 ID Routing &amp; Storage Driver Cutover">
    <targets>
      <target>[MODIFY] @[backend_v2/settings.py#L47-L1088]</target>
      <target>[MODIFY] @[backend_v2/services/storage.py#L19-L66]</target>
      <target>[MODIFY] @[backend_v2/models/core_base.py#L189-L214]</target>
      <target>[MODIFY] @[backend_v2/models/core_base.py#L324-L377]</target>
      <target>[NEW] @[backend_v2/database/postgres/storage_driver.py]</target>
      <target>[MODIFY] @[backend_v2/database/factory.py#L33-L110]</target>
      <target>[MODIFY] @[backend_v2/database/factory.py#L113-L147]</target>
      <target>[MODIFY] @[scripts/audit_zero_orm_strictness.py#L226-L397]</target>
      <target>[MODIFY] @[scripts/audit_zero_orm_strictness.py#L460-L512]</target>
    </targets>
    <action>
      Update @[backend_v2/settings.py#L47-L1088] to default `storage_backend` to `StorageBackend.POSTGRES` in `active_backend` (@[backend_v2/settings.py#L773-L804]), update `is_cloud_storage` (@[backend_v2/settings.py#L806-L814]), and update `allow_mock_tokens` (@[backend_v2/settings.py#L986-L1001]) to permit local mock tokens under `StorageBackend.POSTGRES` when `not self.use_firebase_auth`. Update `get_storage_driver` in @[backend_v2/services/storage.py#L19-L66] to route `StorageBackend.POSTGRES` to `LocalFileDriver` when `not settings.storage_bucket_name` and `GCSFileDriver` when `settings.storage_bucket_name` is set. Update `generate_opaque_id` in @[backend_v2/models/core_base.py#L189-L214] to delegate to `generate_uuid7_opaque_id` (@[backend_v2/models/core_base.py#L324-L377]) for `EntityPrefix.EXECUTION`, `EntityPrefix.REPORT`, `EntityPrefix.NODE`, and `EntityPrefix.EDGE`. Create [NEW] @[backend_v2/database/postgres/storage_driver.py] implementing `PostgresStorageDriver(StorageDriver)` over `PostgresPoolManager` and register it in @[scripts/audit_zero_orm_strictness.py#L226-L397] and @[scripts/audit_zero_orm_strictness.py#L460-L512]. Update `get_driver` (@[backend_v2/database/factory.py#L33-L110]) and `create_unit_of_work` (@[backend_v2/database/factory.py#L113-L147]) to wire `StorageBackend.POSTGRES` exclusively and raise `ConfigurationError` on `LOCAL`, `TINYDB`, or `FIRESTORE`.
    </action>
  </step>

  <step id="3" name="Phase 3: Authoritative PostgreSQL 19 Seeding &amp; FastAPI Preflight Cutover">
    <targets>
      <target>[MODIFY] @[backend_v2/database/interfaces.py#L393-L400]</target>
      <target>[MODIFY] @[backend_v2/database/postgres/entity_adapter.py#L306-L627]</target>
      <target>[MODIFY] @[backend_v2/seed/run_seed.py#L429-L459]</target>
      <target>[MODIFY] @[backend_v2/seed/run_seed.py#L462-L504]</target>
      <target>[MODIFY] @[backend_v2/main.py#L57-L112]</target>
      <target>[MODIFY] @[backend_v2/main.py#L115-L160]</target>
      <target>[MODIFY] @[backend_v2/main.py#L163-L218]</target>
    </targets>
    <action>
      Expand `EntityPersistencePort` in @[backend_v2/database/interfaces.py#L393-L400] and `PostgresEntityAdapter` in @[backend_v2/database/postgres/entity_adapter.py#L306-L627] with `seed_collection_batch` and `verify_seed_table_counts` supporting all 10 core PostgreSQL 19 tables (`organizations`, `users`, `system_configs`, `prompt_blocks`, `steps`, `workflows`, `output_profiles`, `executions`, `report_artifacts`, `report_binaries`). Refactor `seed_database` (@[backend_v2/seed/run_seed.py#L429-L459]) and `main` (@[backend_v2/seed/run_seed.py#L462-L504]) to delete `_seed_tinydb` and `_seed_firestore`, ingest `ValidatedSeedBufferDTO` (@[backend_v2/seed/run_seed.py#L111-L162]) into PostgreSQL 19, and verify non-zero row counts via `SELECT count(*) FROM ...`. Refactor `_audit_storage_and_database_sync` (@[backend_v2/main.py#L57-L112]), `_validate_database_preflight` (@[backend_v2/main.py#L115-L160]), and `lifespan` (@[backend_v2/main.py#L163-L218]) to remove `from tinydb import TinyDB` and validate PostgreSQL 19 readiness.
    </action>
  </step>

  <step id="4" name="Phase 4: AST Guardrail QGR017 Lockdown &amp; Unit Test Suite Synchronization">
    <targets>
      <target>[MODIFY] @[scripts/_ast_guardrails.py#L523-L2455]</target>
      <target>[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L548-L632]</target>
      <target>[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L693-L1110]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/test_factory.py#L32-L42]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/test_settings.py#L95-L131]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/seed/test_run_seed.py#L38-L45]</target>
      <target>[MODIFY] @[backend_v2/tests/unit/database/test_postgres.py#L440-L563]</target>
    </targets>
    <action>
      Update `QuorumGuardrailVisitor` in @[scripts/_ast_guardrails.py#L523-L2455] (`visit_Module` @[scripts/_ast_guardrails.py#L621-L689], `visit_Import` @[scripts/_ast_guardrails.py#L1905-L2016], `visit_ImportFrom` @[scripts/_ast_guardrails.py#L2018-L2265]) to enforce `QGR017` (`FATAL`) against `tinydb`, `tinydb_driver`, `firestore_driver`, `wrapper`, `TinyDBClient`, and `db_v2.json`, and remove deleted driver paths from `BOUNDARY_EXEMPTION_FILES`. Update `InMemoryEntityAdapter` (@[backend_v2/tests/fakes/in_memory_uow.py#L548-L632]) and `InMemoryAsyncPgConnection` (@[backend_v2/tests/fakes/in_memory_uow.py#L693-L1110]), and synchronize unit tests in @[backend_v2/tests/unit/test_factory.py#L32-L42], @[backend_v2/tests/unit/test_settings.py#L95-L131], @[backend_v2/tests/unit/seed/test_run_seed.py#L38-L45], and @[backend_v2/tests/unit/database/test_postgres.py#L440-L563] with >=2 negative ISTQB boundary tests per feature.
    </action>
  </step>
</execution_protocol>

---

## 6. Transition to Plan & Autonomous Execution Lifecycle

The Final Cutover proceeds systematically through Quorum's sovereign project lifecycle once the Phase 1 hardening queue completes:

1. **Tier 0 Research & Impact Analysis (Completed):**
   Executed `/tier0-research-plan @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md]` to verify Phase 1 artifacts (`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]` and `@[docs/implementationplans/TRACKER_PostgreSQL.md]`), AST boundaries, 1-hop caller blast radius, and the 5-Column Directives Table.
2. **Tier 1 Implementation Plan & Tracker Generation:**
   Generate the formal implementation plan and tracker artifacts:
   * Plan: `[NEW] @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL_Final_Cutover.md]`
   * Tracker: `[NEW] @[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]`
3. **Tier 2 Autonomous Execution:**
   Execute the Cutover autonomously:
   ```powershell
   uv run python scripts/auto_phase_runner.py --tracker docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md --model gemini-4-argon-high
   ```
4. **Tier 2 Autonomous Hardening:**
   Execute file-granular hardening with subagent architectural audits across all modified cutover files:
   ```powershell
   uv run python scripts/auto_hardening_runner.py --tracker docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md --gate backend --model gemini-4-argon-medium
   ```
5. **Full Live E2E Production Verification:**
   Launch the system via `@[run_local.bat]` and run a full live workflow execution to achieve 100% parity with baseline `exe_2af2f7665e7c477b`.
6. **Tier 7 Architecture Synchronization & Tier 8 Audit:**
   Synchronize architectural documentation via parameterized `/tier7-describe-architecture` and verify completion via `/tier8-audit-plan`.

