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

This document defines the strict, non-negotiable architectural requirements for executing the **Final Cutover (Lopullinen Cutover)** from the legacy file-locked TinyDB database (`data/db_v2.json`) to the sovereign **All-in-PostgreSQL 19 Zero-ORM Architecture** ([EPIC 151](file:///c:/src/quorum/docs/epic/EPIC_151_PostgreSQL_Clean_Slate_Migration_and_TinyDB_Eradication.md)).

Upon completion of Phase 1 ([IMPLEMENTATION_PLAN_PostgreSQL.md](file:///c:/src/quorum/docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md)), the core PostgreSQL 19 database infrastructure, 12-table DDL schema ([001_pg19_uuidv7_schema.sql](file:///c:/src/quorum/backend_v2/database/migrations/001_pg19_uuidv7_schema.sql)), `asyncpg` + `pydantic_core` binary `\x01` JSONB connection pool ([PostgresPoolManager](file:///c:/src/quorum/backend_v2/database/postgres/pool.py)), CQRS ports, and Unit of Work ([PostgresUnitOfWork](file:///c:/src/quorum/backend_v2/database/postgres/uow.py)) are 100% operational and verified.

The Cutover phase completes the migration by:
1. Re-pointing local development and production startup ([run_local.bat](file:///c:/src/quorum/run_local.bat)) exclusively to PostgreSQL 19.
2. Ingesting the authoritative seed vault ([seed_data.json](file:///c:/src/quorum/backend_v2/seed/seed_data.json)) directly into PostgreSQL via [run_seed.py](file:///c:/src/quorum/backend_v2/seed/run_seed.py) and [PostgresEntityAdapter](file:///c:/src/quorum/backend_v2/database/postgres/entity_adapter.py).
3. Physically deleting legacy TinyDB drivers, OS file-locking code, and database JSON files.
4. Purging the `tinydb` package from `pyproject.toml` and locking the codebase with AST guardrail `QGR017`.

---

## 1. Scope & Inventory Matrix (Kohde- ja Poistoalueet)

### 1.1 Files to Modify (`[MODIFY]`)

| Target File | Architectural Responsibility in Cutover |
| :--- | :--- |
| `@[run_local.bat]` | Start `docker compose up -d redis postgres`, set `STORAGE_BACKEND=POSTGRES`, remove `db_v2.json` references. |
| `@[backend_v2/seed/run_seed.py]` | Ingest `seed_data.json` directly into PostgreSQL 19 using `PostgresEntityAdapter`; delete all TinyDB writing. |
| `@[backend_v2/database/factory.py]` | Wire `POSTGRES` as sole primary storage backend; raise Fail-Fast `ConfigurationError` on `LOCAL` or `TINYDB`. |
| `@[backend_v2/settings.py]` | Default `storage_backend: StorageBackend = StorageBackend.POSTGRES`; remove legacy `LOCAL`/`TINYDB` mappings. |
| `@[scripts/_ast_guardrails.py]` | Enforce AST rule `QGR017` (Severity: `FATAL`) prohibiting imports of `tinydb` or references to `db_v2.json`. |
| `@[pyproject.toml]` | Permanently remove `tinydb = "^4.8.0"` from dependencies. |
| `@[backend_v2/tests/unit/test_factory.py]` | Assert `ConfigurationError` when attempting to request deprecated `LOCAL` or `TINYDB` storage backends. |
| `@[backend_v2/tests/unit/test_settings.py]` | Assert `settings.storage_backend == "POSTGRES"` by default. |

### 1.2 Files to Delete Permanently (`[DELETE]`)

| File to Delete | Obsolete Component & Reason for Eradication |
| :--- | :--- |
| `[DELETE] @[backend_v2/database/tinydb_driver.py]` | Legacy TinyDB document driver; superseded by `PostgresEntityAdapter` and `PostgresUnitOfWork`. |
| `[DELETE] @[backend_v2/database/wrapper.py]` | Legacy OS-level file locking (`msvcrt.locking` on Windows, `fcntl` on POSIX) and `TinyDBClient`. |
| `[DELETE] @[backend_v2/database/firestore_driver.py]` | Archived Firestore driver; zero production usage. |
| `[DELETE] @[data/db_v2.json]` | Legacy file-based database JSON blob. |
| `[DELETE] @[data/db_v2.json.lock]` | Legacy file locking artifact. |
| `[DELETE] @[data/app.db]` | Legacy SQLite/mock database file. |

---

## 2. Concrete Cutover Requirements (Yksityiskohtaiset Vaatimukset)

### REQ-01: Container & Launch Orchestration (`run_local.bat`)
* **Mandate:** Running `.\run_local.bat` MUST start both Redis and PostgreSQL containers:
  ```cmd
  docker compose up -d redis postgres
  ```
* **Mandate:** `run_local.bat` MUST set `set STORAGE_BACKEND=POSTGRES` for both FastAPI backend (`uvicorn`) and background worker (`run_worker`).
* **Banned:** `set STORAGE_BACKEND=LOCAL` is strictly prohibited.
* **Banned:** Any deletion, cleaning, or verification of `data\db_v2.json` in `run_local.bat` is strictly prohibited.

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
* **Prompt Preservation Mandate:** 100% of human-authored prompt texts, coaching philosophy, bilingual `I18nText` translations, and criteria configurations in `seed_data.json` MUST be preserved verbatim without modification.
* **Fail-Fast Assertion:** `run_seed.py` MUST verify with `SELECT count(*) FROM ...` that all 6 seed collections have non-zero record counts and crash with `AppException` if any collection fails to materialize.

### REQ-03: Zero-Fallback Service & Factory Layer (`factory.py` & `settings.py`)
* **Mandate:** `Settings.storage_backend` MUST default to `"POSTGRES"`.
* **Zero Backward Compatibility:** In accordance with the `zero_backward_compatibility_planning_ban`, `get_driver()` and `create_unit_of_work()` MUST NOT provide fallback chains (specifically: falling back to TinyDB if PostgreSQL fails).
* **Fail-Fast Error:** Requesting `LOCAL`, `TINYDB`, or an invalid backend MUST immediately raise:
  ```python
  raise ConfigurationError("STORAGE_BACKEND 'LOCAL' has been permanently decommissioned. Quorum requires PostgreSQL 19.")
  ```

### REQ-04: Physical Eradication of TinyDB and OS File Locks
* **Mandate:** Physically delete `backend_v2/database/tinydb_driver.py` and `backend_v2/database/wrapper.py`.
* **Mandate:** Delete `data/db_v2.json` and any lingering `.lock` files.
* **Prohibition:** Keeping deprecated adapter classes, hollow proxy shells, or `@deprecated` shims is strictly banned per `the_no_legacy_mandate`.

### REQ-05: Dependency Purge
* **Mandate:** Remove `tinydb = "^4.8.0"` from `pyproject.toml`.
* **Mandate:** Run `uv lock` to synchronize `uv.lock`.
* **Verification:** `uv run python -c "import tinydb"` MUST fail with `ModuleNotFoundError`.

### REQ-06: Permanent AST Guardrail Lockdown (`QGR017`)
* **Mandate:** In `scripts/_ast_guardrails.py`, codify rule `QGR017` (Severity: `FATAL`):
  * Prohibits AST `Import` or `ImportFrom` referencing `tinydb`.
  * Prohibits AST string constants or variable names referencing `db_v2.json` or `TinyDBClient`.
* **Verification:** Running `uv run python scripts/_ast_guardrails.py` MUST pass with 0 fatal violations across the entire codebase.

---

## 3. Verification & Quality Gates (Laatuportit & Todennus)

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

## 4. Execution Protocol & Transition to Plan

The Final Cutover proceeds systematically through Quorum's sovereign project lifecycle once the Phase 1 hardening queue completes:

1. **Tier 0 Research & Impact Analysis:**
   Run `/tier0-research-plan @[docs/POSTGRESQL_CUTOVER_REQUIREMENTS.md]` to evaluate how Phase 1 artifacts (`@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]` and `@[docs/implementationplans/TRACKER_PostgreSQL.md]`) have prepared the target state (verified DDL schema, binary JSONB pool, entity and graph adapters, wave uow).
2. **Tier 1 Implementation Plan & Tracker Generation:**
   Generate the formal implementation plan and tracker artifacts:
   * Plan: `@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL_Final_Cutover.md]`
   * Tracker: `@[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]`
3. **Tier 2 Autonomous Execution:**
   Execute the Cutover autonomously:
   ```powershell
   uv run python scripts/auto_phase_runner.py --tracker docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md --model gemini-4-argon-high
   ```
4. **Tier 2 Autonomous Hardening:**
   Execute file-granular hardening with subagent architectural audits across all modified cutover files:
   ```powershell
   uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_PostgreSQL_Final_Cutover.md]" --gate backend --model gemini-4-argon-medium --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"
   ```
5. **Full Live E2E Production Verification:**
   Launch the system via `run_local.bat` and run a full live workflow execution to achieve 100% parity with baseline `exe_2af2f7665e7c477b`.
6. **Tier 7 Architecture Synchronization & Tier 8 Audit:**
   Synchronize architectural documentation via `/tier7-describe-architecture` and verify completion via `/tier8-audit-plan`.

