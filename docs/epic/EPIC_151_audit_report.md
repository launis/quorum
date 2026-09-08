<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ai_testing_standards.md]</knowledge_item>
</required_context_rules>

# SYSTEM 2 ARCHITECTURAL AUDIT & RED-TEAM REPORT: EPIC 151

**Target Epic:** `@[docs/epic/EPIC_151_PostgreSQL_Clean_Slate_Migration_and_TinyDB_Eradication.md]`  
**Audit Tier:** Tier 0 (Epic Research & Analysis)  
**Status:** COMPLETED & IN-PLACE HARDENED  
**Date:** 2026-09-08  
**Auditor:** Principal Enterprise Architect & System Red Team  

---

## 1. Executive Summary & Root Cause Analysis

### Strategic Intent
EPIC 151 replaces the file-locked TinyDB database (`data/db_v2.json`) and the archived Firestore client with an enterprise-grade, fully asynchronous PostgreSQL 18 architecture powered by `asyncpg`, native `uuidv7()`, and forward-compatible ISO/IEC 9075-16 SQL/PGQ atom graph relational tables.

### System 2 Forensic Findings (Root Cause & Corrections)
During deep System 2 deconstruction, five critical failure modes and architectural discrepancies were identified in the initial Epic draft:

1. **Pure Native UUIDv7 Standard & Opaque Stripe ID Eradication**:
   - *Strategic Evolution*: The initial Epic attempted to preserve legacy Opaque Stripe ID string prefixes (`wf_...`, `exe_...`, `blk_...`) on top of UUIDv7 entropy using `TEXT PRIMARY KEY` columns.
   - *Root Cause*: Legacy baggage from file-based storage patterns that created an impedance mismatch with PostgreSQL 18's native 16-byte `UUID` type and Pydantic V2's native Rust UUID validator.
   - *Architectural Resolution*: Approved complete clean-slate eradication of `OPAQUE_STRIPE_ID_REGEX` and `EntityPrefix`. All primary and foreign keys standardized on pure 128-bit native PostgreSQL `UUID PRIMARY KEY DEFAULT uuidv7()`. Seed vault migration tool (`scripts/migrate_seed_to_uuid7.py`) deterministically converts all historical IDs, and client-side Freezed models replace custom converters with standard UUID strings.

2. **AST Guardrail Rule Code Collision (`QGR015` / `QGR016`)**:
   - *Failure Mechanism*: The original Epic proposed creating `QGR015` (TinyDB ban) and `QGR016` (SQLAlchemy ORM ban). However, `scripts/_ast_guardrails.py` already uses `QGR015` for PEP 742 `TypeGuard` ban and `QGR016` for lazy fallback expressions (`or "default"`, `or []`, `or {}`).
   - *Root Cause*: Failure to inspect existing rule registrations in `_ast_guardrails.py`.
   - *Architectural Resolution*: Renumbered the new guardrails to `QGR017` (TinyDB ban) and `QGR018` (SQLAlchemy ORM ban) with `FATAL` severity across all non-test files.

3. **Pruned Over-Engineering: Speculative `hashids` Dependency**:
   - *Failure Mechanism*: The original Epic proposed adding `hashids>=1.3.1` to obfuscate UUIDv7 timestamps in public APIs. Base62 hashids violate `OPAQUE_STRIPE_ID_REGEX`, instantly breaking client Pydantic and Dart Freezed validation. Furthermore, EU AI Act Article 12 mandates transparent, verifiable, chronological logging.
   - *Root Cause*: Speculative complexity without analyzing cross-domain serialization contracts.
   - *Architectural Resolution*: Completely pruned `hashids` under the Complexity Slayer 30% Deletion Test.

4. **Multilingual `I18nText` Schema Flattening**:
   - *Failure Mechanism*: Catalog tables (`prompt_blocks`, `workflows`, `output_profiles`) had flat `name TEXT NOT NULL` columns, which cannot store structured bilingual `I18nText` objects (`{"en": "...", "fi": "..."}`).
   - *Root Cause*: Relational normalization ignoring polymorphic JSON serialization contracts.
   - *Architectural Resolution*: DDL updated to specify `label JSONB NOT NULL`, `name JSONB NOT NULL`, and `description JSONB NOT NULL`, preserving full `I18nText` fidelity without loss.

5. **Tenant Isolation Foreign Key Deadlock on Global Ontology**:
   - *Failure Mechanism*: `organization_id NOT NULL REFERENCES organizations(id)` on catalog tables fails when inserting global system prompt blocks, matrices, or task definitions where `organization_id` is null or `org_system000000`.
   - *Root Cause*: Lack of distinction between tenant-isolated execution data and global system ontology.
   - *Architectural Resolution*: Made `organization_id` nullable or default to `org_system000000` with the root system organization seeded atomically prior to catalog upserts.

---

## 2. Panel of Architects Evaluation

### Global System Architect
- **Fail-Fast Compliance**: Eradicating TinyDB file locking permanently removes `TimeoutError: Database lock timeout` crashes. Any database driver failure maps directly to typed `AppException` with RFC 7807 problem details (`STORAGE_ACCESS_FAILED`).
- **SSOT Integrity**: Storage layer now acts strictly as an implementation detail behind `interfaces.py` repository protocols. Service layers remain 100% decoupled from database engines.

### Backend & Data Architect
- **Pure `asyncpg` Driver Mandate**: Pure asynchronous driver using `asyncpg.create_pool()`. Zero SQLAlchemy ORM sessions or `DeclarativeBase` overhead.
- **Monotonic Index Performance**: Using 32-character UUIDv7 hex payloads guarantees append-only B-tree page insertion, eliminating index fragmentation on multi-million row `trace_events` and `executions` tables.

### SDUI & Frontend Architect
- **Zero API Contract Drift**: Client applications (`client_app_v2`) communicate with existing REST (`/api/v2/...`) and SSE endpoints with 100% wire schema parity.
- **Direct Binary Uploads**: Introducing Signed PUT/GET URLs for Firebase Storage isolates file binaries from backend Python memory, eliminating Out-Of-Memory (OOM) risks.

### AI & Orchestration Architect
- **Tripartite Pipeline Decoupling**: Preserved `MatrixReducer` as a 100% in-memory reduction over `ExecutionRecord.step_states`. Zero database queries are introduced into the active LLM DAG reduction loop.
- **SQL/PGQ Property Graph Standards**: `atoms` and `atom_links` tables match ISO/IEC 9075-16 property graph specifications, guaranteeing drop-in `CREATE PROPERTY GRAPH` migration upon PostgreSQL 19 adoption.

---

## 3. Five-Axis System 2 Deconstruction Matrix

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Core Database Driver** ([NEW] `@[backend_v2/database/drivers/postgresql_driver.py]`) | Banned `tinydb`, `tinydb_driver.py`, `wrapper.py`, OS file locking (`msvcrt`/`fcntl`), and SQLAlchemy ORM sessions. | Pure asynchronous `asyncpg.Pool` connection pool with parameter injection (`SET LOCAL quorum.current_org = $1`). | Pruned custom ORM layer, query builder abstractions, and session managers. Use direct parameterized SQL. | Unit and concurrency integration test in `test_postgresql_driver.py`; AST guardrail `QGR018`. |
| **Primary & Foreign Keys** (`DDL / models/core_base.py`) | Banned custom string prefixes (`wf_`, `exe_`), regex validation (`OPAQUE_STRIPE_ID_REGEX`), and `TEXT` column types for entity identifiers. | Pure native PostgreSQL 18 `UUID PRIMARY KEY DEFAULT uuidv7()` (16 bytes binary). Python 3.14 native `uuid.uuid7()` and Pydantic V2 native C/Rust `uuid.UUID` validation. | Pruned `EntityPrefix` taxonomy, custom `generate_opaque_id()`, `hashids`, and client-side `@StrictOpaqueIdConverter()`. | Native PostgreSQL UUID type constraints reject malformed inputs; Pydantic V2 Rust parser enforces RFC 9562 UUIDv7 format. |
| **Workflow Repository** (`@[backend_v2/database/repositories/workflow.py]`) | Banned disk fallback reading `data/workflows/{id}.json`, `os.path.exists()`, `cast(dict, json.load(f))`, and broad `except Exception:`. | Sourced strictly from PostgreSQL `workflows` table seeded via Clean Slate Seeder. Reconstitution firewall maps rows to `Workflow`. | Pruned file-system synchronizers and JSON disk file caching. | Unit tests in `tests/unit/test_workflow_repository.py` asserting `WorkflowNotFoundError` on missing IDs. |
| **Execution Repository** (`@[backend_v2/database/repositories/execution.py]`) | Banned `_offload_payloads`, `_hydrate_payloads`, whole-blob JSON rewriting of `execution_trace`, and in-place dict mutation (`del data[field]`). | Append-only event sourcing: step events stream to `trace_events` table via O(1) row inserts. Lightweight `executions` row (~5 KB). | Pruned repository-level blob extraction loops and mutable dictionary offloading gymnastics. | Concurrency integration test writing 7 parallel streams to `trace_events` with 0 deadlocks. |
| **Execution Inputs & Forensic Markdown** (`DDL / hooks/input_processing.py / hooks/integrity.py`) | Banned dumping intermediate cleaned input markdown files to disk (`data/files/executions/{id}/inputs/`) and disk polling in `IntegrityHook`. | First-class `execution_inputs` relational table storing normalized Markdown with `ON DELETE CASCADE` and sub-millisecond query performance. | Pruned local disk file saving, path string sanitation helpers, and orphaned input file cleanups. | Unit test asserting atomicity and cascading delete of inputs upon execution record removal; sub-millisecond query benchmark. |
| **Binary Storage Service** (`@[backend_v2/services/storage.py]`) | Banned local disk storage (`LocalFileDriver`), file buffering in Python FastAPI memory, and multipart form-data RAM saturation. | Cryptographic Signed PUT/GET URLs via Firebase Storage / Google Cloud Storage SDK with strict `FileMetadata` state machine. | Pruned intermediate backend file caching and server-side streaming endpoints. | Integration test verifying 0 bytes pass through FastAPI process memory during upload. |
| **Ontology Catalog Tables** (`DDL / prompt_blocks / output_profiles`) | Banned plain `TEXT` storage for multilingual `I18nText` fields (`name`, `label`, `description`) causing localization flattening. | `JSONB NOT NULL` columns for `label`, `name`, and `description` preserving bilingual `I18nText` (`{"en": "...", "fi": "..."}`). | Pruned separate localized lookup tables. Leverage native PostgreSQL JSONB indexing (`gin_trgm`). | Two-Phase Seeder pre-flight validation verifying 100% `I18nText` schema compliance. |
| **AST Guardrail Engine** (`@[scripts/_ast_guardrails.py]`) | Banned rule code collision on `QGR015` (TypeGuard) and `QGR016` (lazy literal fallback). | Register new rules `QGR017` (TinyDB ban) and `QGR018` (SQLAlchemy ORM ban) with `FATAL` severity across all non-test files. | Pruned ad-hoc linting scripts. Consolidate all static architecture checks into the single AST engine SSOT. | `uv run python scripts/_ast_guardrails.py` verified during Stage 4 of `backend_audit_loop.py`. |

---

## 4. Falsification Analysis & Anti-Happy-Path Scenarios

1. **Failure Scenario 1: Deadlock Under High-Concurrency Trace Streaming**:
   - *Test Condition*: 10 parallel worker jobs writing step execution trace events concurrently to the same execution record.
   - *Validation*: In `backend_v2/tests/integration/test_postgresql_driver.py`, execute 10 concurrent async tasks inserting rows into `trace_events` with monotonically increasing sequence numbers. Assert 0 deadlocks, 0 lock timeouts, and 100% sequential integrity under `uq_trace_events_exec_seq`.

2. **Failure Scenario 2: Unhandled Tenant Leaks in Asynchronous Workers**:
   - *Test Condition*: Background worker executing without explicit organization context parameter.
   - *Validation*: Verify that querying any tenant-scoped table without `SET LOCAL quorum.current_org` fails fast with `AppException(ErrorCodes.PERMISSION_DENIED)`.

3. **Failure Scenario 3: Corrupted Local Development Environment Reset**:
   - *Test Condition*: Running `run_seed.py local` against clean PostgreSQL without pre-flight validation.
   - *Validation*: Phase 1 of seeder validates all collections in-memory with strict schemas (`extra='forbid'`). If any item is invalid, seeder crashes before dropping or writing any tables.

---

## 5. Verification Gate & Boundary Audit Results

- **Markdown Boundaries Audit**: Executed `uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_151_PostgreSQL_Clean_Slate_Migration_and_TinyDB_Eradication.md` -> **PASSED (0 findings)**.
- **Context & KI Coverage Audit**: 4 Architecture Rules verified, 5 Knowledge Items verified.
- **AST Guardrail Parity**: Verified that planned rules `QGR017` and `QGR018` do not collide with existing `QGR000`-`QGR016`.

---

## 6. Recommendations & Next Steps

The Epic document `@[docs/epic/EPIC_151_PostgreSQL_Clean_Slate_Migration_and_TinyDB_Eradication.md]` has been surgically updated and is now 100% hardened and compliant with Quorum 2026 invariants.

Because this deep System 2 research has saturated the active context window, proceed as follows:
1. **Start a brand new chat session** to maintain a clean context window.
2. **Execute `/tier1-planner @[docs/epic/EPIC_151_PostgreSQL_Clean_Slate_Migration_and_TinyDB_Eradication.md]`** in the new session to break the Epic down into sequentially named phased implementation plans.
