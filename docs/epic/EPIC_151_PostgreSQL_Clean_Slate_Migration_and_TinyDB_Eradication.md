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

# EPIC 151: PostgreSQL 18/19 Clean Slate Data Layer Migration and Complete TinyDB Eradication

> [!NOTE]
> **Scientific & Industrial Validation (2025-2026)**
> 1. **PostgreSQL 18 Native UUIDv7 (RFC 9562)**: PostgreSQL 18 incorporates native core engine support for `uuidv7()` and `uuid_extract_timestamp()`. Time-ordered UUIDv7 identifiers provide strict monotonically increasing entropy within 1-millisecond resolution, preventing B-tree page splits and index fragmentation on multi-million row tables while maintaining global uniqueness.
> 2. **PostgreSQL 18 Asynchronous I/O (AIO `io_method=io_uring`)**: PostgreSQL 18 introduces native kernel-level asynchronous I/O via `io_uring` on Linux platforms (with fallback to worker pools). This overlaps concurrent I/O operations and compute cycles, eliminating file-system serialization bottlenecks for high-throughput cloud database instances.
> 3. **ISO/IEC 9075-16:2023 SQL/PGQ Property Graph Standards**: PostgreSQL 19 implements SQL/PGQ property graph querying (`CREATE PROPERTY GRAPH`, `GRAPH_TABLE`) as an open standard semantic layer directly over relational tables without requiring graph database engines. Designing vertex tables (`atoms`) and edge tables (`atom_links`) with standard foreign keys guarantees a 100% zero-rewrite drop-in migration to `CREATE PROPERTY GRAPH` upon PostgreSQL 19 adoption.
> 4. **Append-Only Event Sourcing for Multi-Agent Tracing**: Industrial distributed tracing patterns demonstrate that appending immutable events to an indexed table (`trace_events`) yields O(1) write complexity and zero row-lock contention across concurrent asynchronous workers, compared to O(N) whole-blob serialization rewrites.
> 5. **High-Throughput Zero-ORM Driver (`asyncpg`)**: Benchmarks establish that `asyncpg` outperforms Python ORM abstraction layers by 3x to 5x throughput with zero memory allocation overhead by directly mapping binary wire protocols to strict Pydantic V2 schemas at repository boundaries.

---

## 1. Goal Description & Background (Objective & Problem Statement)

### Business & Architectural Objective

The objective of this Epic is to decommission and permanently eradicate the file-locked TinyDB development database (`data/db_v2.json`) and the archived Firestore client, replacing them with an enterprise-grade, fully asynchronous PostgreSQL 18 architecture powered by `asyncpg`, native `uuidv7()`, and forward-compatible ISO/IEC 9075-16 SQL/PGQ atom graph schema.

This migration establishes **absolute storage sovereignty**, full ACID transaction guarantees, multi-version concurrency control (MVCC), append-only execution event streaming, and Google Cloud SQL enterprise topology (VPC Private IP, PgBouncer transaction pooling, and `io_method=io_uring`). It introduces cryptographic Signed URLs for binary storage isolation in Firebase Storage with automated orphaned file cleanup, while strictly preserving the in-memory Tripartite Pipeline reduction engine (`MatrixReducer`).

### Problem Statement & Forensic Technical Debt Analysis

Quorum currently operates against a file-based storage architecture that exhibits severe concurrency and architectural bottlenecks:

| Domain Bottleneck | Current Implementation | Root Cause & Failure Mechanism | Production Consequence |
| :--- | :--- | :--- | :--- |
| **Concurrency & File Locks** | `@[backend_v2/database/wrapper.py]` | OS-level file locking via `msvcrt.locking` (Windows) and `fcntl` (POSIX) on a single JSON file (`db_v2.json`). | Simultaneous execution runs or parallel Arq worker jobs block each other, triggering `TimeoutError: Database lock timeout`. |
| **Execution Trace Rewrites** | `@[backend_v2/database/repositories/execution.py]` | Whole-array JSON serialization of `execution_trace` on every step progress update or audit log event. | Multi-megabyte disk I/O per event, table rewrite thrashing, and high latency during multi-agent DAG evaluation. |
| **Index Fragmentation** | Random UUIDv4 / string IDs | Random identifiers scatter across B-tree leaves without temporal locality. | Cache page thrashing, bloated indexes, and query latency degradation as dataset size grows. |
| **RAM Saturation from Files** | `@[backend_v2/services/storage.py]` | Local disk file buffering and direct binary streaming through FastAPI Python application memory. | Large PDF or DOCX uploads consume worker RAM, risking Out-Of-Memory (OOM) process termination during heavy load. |
| **Split-Brain IAM & Storage** | Ad-hoc user deletion | Deleting a user row leaves unmanaged files in storage and unlinked accounts in Firebase Auth. | GDPR compliance violation and unbounded storage cost accumulation from abandoned files. |
| **Layer Bleed Risk** | Proposed graph querying in active loops | Coupling database graph traversal directly into active LLM cognitive DAG reduction loops. | Network roundtrip storms, uncommitted transaction race conditions, and violation of the Tripartite Pipeline Architecture. |

---

## 2. Architectural Impact & Compliance Matrix

### 2.1. Deprecations & Sunset List (`What We Will REMOVE`)

The following files, classes, fields, and dependencies are marked for permanent removal:

```
DESTRUCTIVE OPERATION INVENTORY:
- [DELETE] backend_v2/database/tinydb_driver.py (TinyDBDriver implementation) -> INTENTIONALLY DROPPED
- [DELETE] backend_v2/database/wrapper.py (Legacy OS file locking, TinyDBClient, TinyDBTable) -> INTENTIONALLY DROPPED
- [DELETE] backend_v2/database/firestore_driver.py (Archived Firestore implementation) -> INTENTIONALLY DROPPED
- [DELETE] backend_v2/services/drivers/local_file_driver.py (Local disk binary driver) -> INTENTIONALLY DROPPED
- [DELETE] data/db_v2.json & data/app.db & *.lock (Local database files) -> INTENTIONALLY DROPPED
- [DELETE] Disk fallback logic in backend_v2/database/repositories/workflow.py (reading data/workflows/{id}.json) -> INTENTIONALLY DROPPED
- [DELETE] Unbounded dictionary offload logic in backend_v2/database/repositories/execution.py -> Replaced by trace_events table
- [DELETE] Intermediate disk-based forensic input dumping in backend_v2/hooks/input_processing.py (_save_forensic_input) -> Replaced by execution_inputs table
- [DELETE] Disk-based forensic reading in backend_v2/hooks/integrity.py -> Replaced by execution_inputs repository query
- [PURGE] Dependency 'tinydb' in pyproject.toml and uv.lock -> Permanently removed
```

### 2.2. Retained SSOT Invariants (`What We Will RETAIN`)

The following architectural components are strictly preserved and validated:

1. **Repository Interface Sovereignty (`@[backend_v2/database/interfaces.py]`)**:
   - `IUnifiedWorkflowRepository` and component repository protocols remain the Single Source of Truth (SSOT) for domain data access.
   - Caller service modules across `backend_v2/services/` interact exclusively with repository protocols, never with raw SQL strings or driver sessions.
2. **Tripartite Pipeline & In-Memory `MatrixReducer` (`@[backend_v2/services/orchestrator/matrix_reducer.py]`)**:
   - `MatrixReducer` remains a 100% pure, deterministic in-memory reduction operating synchronously over `ExecutionRecord.step_states`.
   - Zero SQL queries or database transactions are introduced into the active LLM DAG reduction loop. Graph tables (`atoms`, `atom_links`) are queried strictly during post-hoc forensic XAI auditing, visualization, and reporting (Tripartite Phase 2 & 3).
3. **Pydantic V2 Domain Reconstitution Firewall**:
   - Internal database driver layers return raw records, which repository methods immediately map into frozen, strictly typed Pydantic V2 Domain Models (`ConfigDict(frozen=True, strict=True)`).
   - Zero raw dictionaries or database driver record objects leak past the repository layer into Service or Router layers.
4. **Client API Contract Immutability**:
   - All REST and SSE API endpoint contracts (`/api/v2/...`) consumed by `client_app_v2` maintain 100% wire parity.

### 2.3. Compliance & Modernity Gates

| Gate ID | Mandatory Constraint | Enforcement Mechanism | Failure Mode Remediation |
| :--- | :--- | :--- | :--- |
| **GATE-01: Pure Driver** | Pure `asyncpg` connection pool driver without SQLAlchemy ORM. | Direct `asyncpg.Pool` usage in `PostgreSQLDriver`. AST check `QGR018` forbids `sqlalchemy.orm`. | Reject PRs or builds importing SQLAlchemy ORM sessions or DeclarativeBase. |
| **GATE-02: Pure Native UUIDv7 (RFC 9562)** | Primary and foreign keys use pure 128-bit native PostgreSQL `UUID PRIMARY KEY DEFAULT uuidv7()`. Python models use `uuid.UUID` generated via Python 3.14 `uuid.uuid7()`. | DDL column specification `id UUID PRIMARY KEY DEFAULT uuidv7()`, foreign keys `UUID REFERENCES ...`, and Pydantic V2 native C/Rust `uuid.UUID` type validation. | Reject custom string prefixes (`wf_`, `exe_`), custom regex validations (`OPAQUE_STRIPE_ID_REGEX`), and random UUIDv4 identifiers. |
| **GATE-03: SQL/PGQ Parity** | `atoms` and `atom_links` tables match ISO/IEC 9075-16 property graph specifications. | Relational schema with explicit `source_id` / `target_id` foreign keys and properties. | DDL test verifies drop-in `CREATE PROPERTY GRAPH` execution on PG 19. |
| **GATE-04: Zero Binary RAM** | Backend RAM never buffers uploaded files. Uploads use signed URLs. | `FileMetadata` table and Firebase Storage Signed URL generation. | Direct binary upload endpoints in backend FastAPI routers are rejected. |
| **GATE-05: Clean Slate** | Zero migration of legacy TinyDB JSON files. Fresh UUIDv7 generation. | `run_seed.py` seeds freshly generated UUIDv7 entities into PostgreSQL. | Decommission and delete all `db_v2.json` files and legacy ID arrays. |
| **GATE-06: Tenant Isolation** | Multi-organization isolation enforced via session-level parameters. | `SET LOCAL quorum.current_org = $1` on transactional operations. | Connections without explicit organization scope fail with `AppException`. |
| **GATE-07: AST Lockdown** | Zero TinyDB imports and zero SQLAlchemy ORM references codebase-wide. | AST Guardrail rules `QGR017` (TinyDB ban) and `QGR018` (SQLAlchemy ORM ban) in `_ast_guardrails.py`. | Any commit or PR violating AST rules fails `backend_audit_loop.py` with FATAL exit code. |

### 2.4. Five-Column Architectural Directives Table

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

### 2.5. Producer-Consumer Integration Check

```
[Producer: Client Browser / Desktop App]
   │
   ├─► 1. POST /api/v2/files/upload-url (FileName, SizeBytes, MimeType)
   │        │
   │        ▼
   │   [FastAPI Backend & PostgreSQL]
   │   - Insert FileMetadata (id=UUIDv7, status='pending', expires_at=now()+15m)
   │   - Generate GCS/Firebase Signed PUT URL with strict Content-Length & Content-Type
   │   - Return {file_id, upload_url}
   │
   ├─► 2. Direct HTTP PUT to Signed URL ──► [Google Cloud Storage / Firebase Storage]
   │        (Binary payload streams directly to Cloud Storage; 0 bytes pass through Backend RAM)
   │
   ├─► 3. POST /api/v2/files/{file_id}/confirm
   │        │
   │        ▼
   │   [FastAPI Backend & PostgreSQL]
   │   - Verify blob existence and size via GCS client metadata check
   │   - Update FileMetadata (status='uploaded', uploaded_at=now())
   │
   └─► 4. Background Cron Job (Every 24 Hours)
            │
            ▼
       [Async Worker Task: cleanup_orphaned_files]
       - Query FileMetadata WHERE status='pending' AND created_at < now() - INTERVAL '24 hours'
       - Delete orphaned blobs from Cloud Storage via SDK
       - Delete orphaned FileMetadata rows from PostgreSQL
```

---

## 3. Database Schema Specification (DDL)

The schema utilizes PostgreSQL 18 native features, specifically `uuidv7()`, Virtual Generated Columns, JSONB indexing, engine-level triggers, Row-Level Security (RLS), and ISO/IEC 9075-16 relational property graph alignment:

```sql
-- ============================================================================
-- QUORUM POSTGRESQL 18 CORE RELATIONAL DDL (SSOT)
-- Pure Native RFC 9562 UUIDv7 Primary & Foreign Keys (16-Byte Binary)
-- ============================================================================

-- Ensure required extension for cryptographic operations
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Engine-Level Automated Updated-At Trigger Function
CREATE OR REPLACE FUNCTION set_updated_at() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 1. Organizations (IAM Multi-Tenancy)
CREATE TABLE organizations (
    id                  UUID PRIMARY KEY DEFAULT uuidv7(),
    name                TEXT NOT NULL,
    config              JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_organizations_updated_at BEFORE UPDATE ON organizations FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 2. Users (IAM)
CREATE TABLE users (
    id                  UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    firebase_uid        TEXT NOT NULL UNIQUE,
    email               TEXT NOT NULL UNIQUE,
    role                TEXT NOT NULL DEFAULT 'USER',
    deleted_at          TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 3. File Metadata & Binary Storage Isolation
CREATE TABLE file_metadata (
    id                  UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id     UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename            TEXT NOT NULL,
    mime_type           TEXT NOT NULL,
    size_bytes          BIGINT NOT NULL,
    size_mb             DOUBLE PRECISION GENERATED ALWAYS AS (size_bytes / 1048576.0) STORED,
    storage_path        TEXT NOT NULL UNIQUE,
    status              TEXT NOT NULL DEFAULT 'pending', -- 'pending', 'uploaded', 'quarantined'
    expires_at          TIMESTAMPTZ NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_file_metadata_updated_at BEFORE UPDATE ON file_metadata FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 4. Workflows (Blueprints)
CREATE TABLE workflows (
    id                  UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id     UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name                JSONB NOT NULL, -- I18nText bilingual dictionary
    slug                TEXT NOT NULL,
    description         JSONB NOT NULL, -- I18nText bilingual dictionary
    status              TEXT NOT NULL DEFAULT 'draft',
    version             INTEGER NOT NULL DEFAULT 1,
    is_public           BOOLEAN NOT NULL DEFAULT FALSE,
    is_system_core      BOOLEAN NOT NULL DEFAULT FALSE,
    config              JSONB NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_workflows_updated_at BEFORE UPDATE ON workflows FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 5. Steps (Task Definitions)
CREATE TABLE steps (
    id                  UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id     UUID REFERENCES organizations(id) ON DELETE CASCADE,
    slug                TEXT NOT NULL,
    type                TEXT NOT NULL,
    is_system_core      BOOLEAN NOT NULL DEFAULT FALSE,
    config              JSONB NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_steps_updated_at BEFORE UPDATE ON steps FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 6. Prompt Blocks (Matrices, Personas, Evaluation Criteria)
CREATE TABLE prompt_blocks (
    id                  UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id     UUID REFERENCES organizations(id) ON DELETE CASCADE,
    label               JSONB NOT NULL, -- I18nText bilingual dictionary
    slug                TEXT NOT NULL,
    category_id         TEXT NOT NULL,
    type                TEXT NOT NULL,
    is_system_core      BOOLEAN NOT NULL DEFAULT FALSE,
    description         JSONB NOT NULL, -- I18nText bilingual dictionary
    config              JSONB NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_prompt_blocks_updated_at BEFORE UPDATE ON prompt_blocks FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 7. Output Profiles (SDUI Presentation Specifications)
CREATE TABLE output_profiles (
    id                  UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id     UUID REFERENCES organizations(id) ON DELETE CASCADE,
    workflow_id         UUID NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    name                JSONB NOT NULL, -- I18nText bilingual dictionary
    slug                TEXT NOT NULL,
    description         JSONB,          -- I18nText bilingual dictionary
    strictness_level    INTEGER NOT NULL DEFAULT 3,
    scoring_strategy    TEXT NOT NULL DEFAULT 'CARTESIAN_STRICT',
    is_system_core      BOOLEAN NOT NULL DEFAULT FALSE,
    config              JSONB NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_output_profiles_updated_at BEFORE UPDATE ON output_profiles FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 8. Executions (Execution Record SSOT)
CREATE TABLE executions (
    id                              UUID PRIMARY KEY DEFAULT uuidv7(),
    organization_id                 UUID REFERENCES organizations(id) ON DELETE CASCADE,
    workflow_id                     UUID NOT NULL REFERENCES workflows(id) ON DELETE RESTRICT,
    workflow_version                INTEGER NOT NULL DEFAULT 1,
    status                          TEXT NOT NULL DEFAULT 'pending',
    error                           TEXT,
    target_locale                   TEXT NOT NULL DEFAULT 'fi',
    active_profile_id               UUID REFERENCES output_profiles(id) ON DELETE SET NULL,
    output_profile_id               UUID NOT NULL REFERENCES output_profiles(id) ON DELETE RESTRICT,
    pdf_report_path                 TEXT,
    is_resumable                    BOOLEAN NOT NULL DEFAULT FALSE,
    prompt_tokens                   INTEGER NOT NULL DEFAULT 0,
    completion_tokens               INTEGER NOT NULL DEFAULT 0,
    cached_tokens                   INTEGER NOT NULL DEFAULT 0,
    reasoning_tokens                INTEGER NOT NULL DEFAULT 0,
    cumulative_synthesis_tokens     INTEGER NOT NULL DEFAULT 0,
    dag_cost_usd                    DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    cumulative_synthesis_cost       DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    cost_estimate                   DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    duration_ms                     INTEGER NOT NULL DEFAULT 0,
    metadata                        JSONB NOT NULL DEFAULT '{}',
    raw_inputs                      JSONB NOT NULL DEFAULT '{}',
    frozen_context                  JSONB,
    frozen_context_storage_path     TEXT,
    context_variables_storage_path  TEXT,
    step_states                     JSONB NOT NULL DEFAULT '{}',
    steps                           JSONB NOT NULL DEFAULT '[]',
    profile_syntheses               JSONB NOT NULL DEFAULT '{}',
    source_identity_manifest        JSONB NOT NULL DEFAULT '{}',
    models_used                     JSONB NOT NULL DEFAULT '{}',
    execution_summary               JSONB,
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at                    TIMESTAMPTZ
);

-- 9. Execution Inputs (Normalized Forensic Markdown & Cleaned Inputs SSOT)
CREATE TABLE execution_inputs (
    id                  UUID PRIMARY KEY DEFAULT uuidv7(),
    execution_id        UUID NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    input_key           TEXT NOT NULL, -- Specifically dynamic input key: 'chat_log', 'product_text', or 'reflection_text'
    content             TEXT NOT NULL, -- Cleaned and normalized Markdown text
    char_count          INTEGER NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_execution_inputs_key UNIQUE (execution_id, input_key)
);

-- 10. Append-Only Execution Trace Events (O(1) Event Sourcing)
CREATE TABLE trace_events (
    id                  BIGSERIAL PRIMARY KEY,
    exec_id             UUID NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    seq                 INTEGER NOT NULL,
    step_name           TEXT NOT NULL,
    event_type          TEXT NOT NULL,
    content             JSONB NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_trace_events_exec_seq UNIQUE (exec_id, seq)
);

-- 11. Enriched Atom Graph: Vertices (Atoms conforming to ISO/IEC 9075-16)
CREATE TABLE atoms (
    id                  UUID PRIMARY KEY DEFAULT uuidv7(),
    execution_id        UUID NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    step_id             UUID NOT NULL REFERENCES steps(id) ON DELETE RESTRICT,
    claim_text          TEXT NOT NULL,
    atom_type           TEXT NOT NULL,
    status              TEXT NOT NULL,
    source_quote        TEXT,
    source_id           TEXT,
    reasoning           TEXT,
    extracted_facts     JSONB NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 12. Enriched Atom Graph: Edges (Atom Links conforming to ISO/IEC 9075-16)
CREATE TABLE atom_links (
    id                  UUID PRIMARY KEY DEFAULT uuidv7(),
    execution_id        UUID NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    source_id           UUID NOT NULL REFERENCES atoms(id) ON DELETE CASCADE,
    target_id           UUID NOT NULL REFERENCES atoms(id) ON DELETE CASCADE,
    relation_type       TEXT NOT NULL,
    edge_reasoning      TEXT,
    weight              DOUBLE PRECISION NOT NULL DEFAULT 1.0,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- 13. System Configuration (Taxonomies, Model Strategies, Gateway Limits)
CREATE TABLE system_config (
    id                  UUID PRIMARY KEY DEFAULT uuidv7(),
    type                TEXT NOT NULL UNIQUE,
    config              JSONB NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE TRIGGER trg_system_config_updated_at BEFORE UPDATE ON system_config FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- 14. Audit Log (Append-Only Administrative Actions)
CREATE TABLE audit_log (
    id                  BIGSERIAL PRIMARY KEY,
    organization_id     UUID REFERENCES organizations(id) ON DELETE SET NULL,
    user_id             UUID REFERENCES users(id) ON DELETE SET NULL,
    action              TEXT NOT NULL,
    payload             JSONB NOT NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ============================================================================
-- PERFORMANCE & INTEGRITY INDEXES
-- ============================================================================
CREATE INDEX idx_users_org ON users (organization_id);
CREATE INDEX idx_users_firebase_uid ON users (firebase_uid);
CREATE INDEX idx_file_metadata_pending ON file_metadata (status, created_at) WHERE status = 'pending';
CREATE INDEX idx_workflows_org ON workflows (organization_id);
CREATE INDEX idx_workflows_slug ON workflows (organization_id, slug);
CREATE INDEX idx_steps_org ON steps (organization_id);
CREATE INDEX idx_prompt_blocks_category ON prompt_blocks (organization_id, category_id);
CREATE INDEX idx_output_profiles_wf ON output_profiles (workflow_id);
CREATE INDEX idx_executions_workflow ON executions (workflow_id);
CREATE INDEX idx_executions_status ON executions (status);
CREATE INDEX idx_executions_metadata ON executions USING GIN (metadata);
CREATE INDEX idx_execution_inputs_exec ON execution_inputs (execution_id);
CREATE INDEX idx_trace_events_exec_seq ON trace_events (exec_id, seq ASC);
CREATE INDEX idx_atoms_execution ON atoms (execution_id);
CREATE INDEX idx_atoms_step ON atoms (step_id);
CREATE INDEX idx_atom_links_execution ON atom_links (execution_id);
CREATE INDEX idx_atom_links_source_target ON atom_links (source_id, target_id);

-- Full-Text Search GIN Indexes (Sub-millisecond prompt and workflow search)
CREATE INDEX idx_prompt_blocks_fts ON prompt_blocks USING GIN (to_tsvector('english', coalesce(description->>'en', '') || ' ' || slug));
CREATE INDEX idx_workflows_fts ON workflows USING GIN (to_tsvector('english', coalesce(description->>'en', '') || ' ' || slug));

-- ============================================================================
-- ROW-LEVEL SECURITY (RLS) ZERO-TRUST MULTI-TENANCY POLICIES
-- ============================================================================
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_workflows ON workflows
    FOR ALL
    USING (organization_id = NULLIF(current_setting('quorum.current_org', true), '')::uuid OR is_public = true);

ALTER TABLE steps ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_steps ON steps
    FOR ALL
    USING (organization_id = NULLIF(current_setting('quorum.current_org', true), '')::uuid OR is_system_core = true);

ALTER TABLE prompt_blocks ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_prompt_blocks ON prompt_blocks
    FOR ALL
    USING (organization_id = NULLIF(current_setting('quorum.current_org', true), '')::uuid OR is_system_core = true);

ALTER TABLE output_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_output_profiles ON output_profiles
    FOR ALL
    USING (organization_id = NULLIF(current_setting('quorum.current_org', true), '')::uuid OR is_system_core = true);

ALTER TABLE executions ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_executions ON executions
    FOR ALL
    USING (organization_id = NULLIF(current_setting('quorum.current_org', true), '')::uuid);

ALTER TABLE execution_inputs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation_execution_inputs ON execution_inputs
    FOR ALL
    USING (execution_id IN (SELECT id FROM executions WHERE organization_id = NULLIF(current_setting('quorum.current_org', true), '')::uuid));
```

### 3.1. Zero-Rewrite Drop-In SQL/PGQ Property Graph Migration (PostgreSQL 19 Readiness)

When PostgreSQL 19 is introduced to production infrastructure, the relational table structures above immediately support the ISO/IEC 9075-16 standard with the following drop-in statement without changing any existing table or column:

```sql
-- POSTGRESQL 19 ZERO-REWRITE DROP-IN PROPERTY GRAPH DEFINITION
CREATE PROPERTY GRAPH atom_knowledge_graph
VERTEX TABLES (
    atoms
        LABEL Atom
        PROPERTIES (id, execution_id, step_id, claim_text, atom_type, status, source_quote, source_id, reasoning, extracted_facts, created_at)
)
EDGE TABLES (
    atom_links
        SOURCE KEY (source_id) REFERENCES atoms (id)
        DESTINATION KEY (target_id) REFERENCES atoms (id)
        LABEL ConnectedTo
        PROPERTIES (id, execution_id, relation_type, edge_reasoning, weight, created_at)
);
```

---

## 4. Phased Execution Plan (Implementation Strategy)

### Phase 1: Pre-Implementation Technical Debt Cleanups & Scoped Boy Scout Sweep

Prior to introducing PostgreSQL components, existing technical debt identified during pre-flight analysis must be permanently resolved:

1. **Purge Disk Fallback in `@[backend_v2/database/repositories/workflow.py]`**:
   - Remove the `data/workflows/{workflow_id}.json` reading logic in `get_workflow_definition`.
   - Remove `cast(dict[str, Any], json.load(f))` and broad `except Exception:`.
   - Workflows must be sourced strictly from database storage seeded from the Clean Slate repository.
2. **Eliminate Blob Mutation Duct-Tape in `@[backend_v2/database/repositories/execution.py]`**:
   - Remove `_offload_payloads` and `_hydrate_payloads` dictionary mutations on `execution_trace`.
   - Decouple execution trace writes into the dedicated `trace_events` repository pathway.
3. **Purge Disk-Based Forensic Input Dumping and Reading in `@[backend_v2/hooks/input_processing.py]` and `@[backend_v2/hooks/integrity.py]`**:
   - Deprecate and remove `_save_forensic_input` in `input_processing.py` which writes cleaned Markdown files (`data/files/executions/{id}/inputs/*.md`) to local disk.
   - Deprecate and remove disk reading in `integrity.py` which verifies files from `data/files/executions/{id}/inputs/`.
   - Route cleaned execution inputs directly to the database via `ExecutionRepositoryImpl.save_execution_input` into the `execution_inputs` table.
4. **Harmonize `StorageBackend` Enum in `@[backend_v2/settings.py]`**:
   - Update `StorageBackend` enum to replace `LOCAL` and `FIRESTORE` with `POSTGRESQL` (with backward-compatible migration shim during Phase 1).
   - Add required settings: `database_url`, `postgres_pool_min_size`, `postgres_pool_max_size`, `cloud_sql_instance_connection_name`.
5. **Enforce Unit Test Isolation via Fake Repositories**:
   - Verify that all unit tests continue using `backend_v2/tests/fakes/in_memory_repositories.py`, guaranteeing that unit testing velocity remains decoupled from live database engines.

### Phase 2: Core Database Schema, Asyncpg Driver & Alembic Migration Engine

1. **Add Production Dependencies in `@[pyproject.toml]`**:
   - Add `asyncpg>=0.30.0` (high-performance asynchronous PostgreSQL driver).
   - Add `alembic>=1.14.0` (deterministic schema revision control).
   - *Note: Speculative `hashids` dependency was pruned during System 2 analysis to preserve `OPAQUE_STRIPE_ID_REGEX` parity and EU AI Act Article 12 compliance.*
2. **Establish Local & CI Container Infrastructure**:
   - Configure `docker-compose.dev.yml` and `docker-compose.yml` with `postgres:18-alpine` (listening on port 5432 with health check `pg_isready`).
   - Configure Redis 7 container for Arq background workers.
3. **Initialize Alembic Migration Tree**:
   - Create `backend_v2/database/migrations/alembic.ini`.
   - Create `backend_v2/database/migrations/env.py` configured for asynchronous execution via `asyncpg`.
   - Create `backend_v2/database/migrations/versions/001_initial_schema.py` applying the complete DDL schema defined in Section 3.
4. **Implement Pure `PostgreSQLDriver` in [NEW] `@[backend_v2/database/drivers/postgresql_driver.py]`**:
   - Implement connection pool lifecycle using `asyncpg.create_pool()`.
   - Implement `get`, `upsert`, `update`, `delete`, `query`, `count`, and `clear` conforming to `StorageDriver` protocol.
   - Implement session-level Row-Level Security (RLS) parameter injection (`SET LOCAL quorum.current_org = $1`).
   - Wrap all database and driver exceptions into typed `AppException` instances with RFC 7807 problem details (`ErrorCodes.STORAGE_ACCESS_FAILED`).
5. **Update Factory in `@[backend_v2/database/factory.py]`**:
   - Refactor `get_driver()` to instantiate and return `PostgreSQLDriver` when `settings.storage_backend == StorageBackend.POSTGRESQL`.

### Phase 3: Repository Reconstitution & Storage Layer Modernization

1. **Repository Implementations Modernization**:
   - Update `backend_v2/database/repositories/workflow.py` to execute parameterized SQL against `workflows` table.
   - Update `backend_v2/database/repositories/execution.py` to persist `executions` row and stream step events via `trace_events` table (`INSERT INTO trace_events ...`).
   - Implement `save_execution_input(execution_id, input_key, content)` and `get_execution_inputs(execution_id)` in `ExecutionRepositoryImpl` executing against the `execution_inputs` table, fully replacing disk-based forensic text storage.
   - Update component repositories (`PromptBlockRepositoryImpl`, `StepRepositoryImpl`, `OutputProfileRepositoryImpl`, `SystemConfigRepositoryImpl`) to query dedicated tables.
2. **Reconstitution Firewall Assertion**:
   - Ensure all repository fetch methods hydrate database records into frozen Pydantic V2 Domain Models (`Model.model_validate(row_dict, strict=False)`).
   - Ensure serialization passes JSON-safe payloads (`Model.model_dump(mode='json')`).
3. **Firebase Storage Signed URL Modernization in `@[backend_v2/services/storage.py]`**:
   - Refactor `storage.py` to remove direct disk writing (`LocalFileDriver`).
   - Implement `generate_signed_upload_url(organization_id, user_id, filename, mime_type, size_bytes)` returning short-lived PUT URL and recording `FileMetadata` in `pending` state.
   - Implement `confirm_file_upload(file_id)` verifying Cloud Storage blob metadata and updating state to `uploaded`.
   - Implement `generate_signed_download_url(file_id)` returning time-limited GET URL.
4. **Automated Orphaned File Cleanup Task**:
   - Implement Arq background worker task `cleanup_orphaned_files_task` in `backend_v2/worker.py` scheduled to run every 24 hours.
   - Task queries `file_metadata` for `pending` files older than 24 hours, invokes Google Cloud Storage SDK to delete orphaned blobs, and deletes corresponding database rows.
5. **Transactional Split-Brain GDPR Deletion**:
   - Implement `delete_user_account(user_id)`:
     - Step 1: Query all `file_metadata` records belonging to `user_id`.
     - Step 2: Delete all physical blobs from Cloud Storage via SDK.
     - Step 3: Delete user from Firebase Auth via `firebase_admin.auth.delete_user()`.
     - Step 4: Execute database transaction deleting `users` row (cascading to `file_metadata` rows).

### Phase 4: Clean Slate Seeder & Pure UUIDv7 Deterministic Migration

1. **Clean Slate ID Generation in `@[backend_v2/models/core_base.py]`**:
   - Deprecate and remove `generate_opaque_id` and `OPAQUE_STRIPE_ID_REGEX`.
   - Standardize entity primary keys on native Python 3.14 `uuid.uuid7()` and Pydantic V2 native C/Rust `uuid.UUID` validation.
   - Update domain models (`Workflow`, `Step`, `PromptBlock`, `OutputProfile`, `ExecutionRecord`) to declare `id: uuid.UUID`.
2. **Deterministic Seed Vault UUIDv7 Ingestion & Migration Tool ([NEW] `@[scripts/migrate_seed_to_uuid7.py]`)**:
   - Implement idempotent migration script that parses `backend_v2/seed/seed_data.json` as authoritative input data.
   - All qualitative prompt texts, evaluation criteria, matrix scales, bilingual `I18nText` translations, and task blueprint configurations are ingested 100% as-is.
   - Build a bidirectional deterministic lookup mapping every legacy prefixed string ID (`sys_...`, `blk_...`, `stp_...`, `wor_...`, `prf_...`, `usr_...`, `org_...`) to a pristine RFC 9562 UUIDv7. Historical IDs do not need to be preserved in the target database.
   - Rewrite all primary keys and cross-table foreign key references (`workflow_id`, `criteria_block_ids`, `role_block_id`, `default_profile_id`, `extraction_protocol_block_id`) atomically, maintaining 100% relational integrity.
   - Validate 100% preservation of all qualitative human-authored prompt texts, coaching philosophy, and matrix assertion scales per `prompt_preservation_mandate`.
3. **Flutter Client Freezed Model Modernization (`client_app_v2`)**:
   - Remove legacy `StrictOpaqueIdConverter` from `client_app_v2/lib/utils/json_converters.dart`.
   - Remove `@StrictOpaqueIdConverter()` decorators from Freezed models in `client_app_v2/lib/features/studio/models/` and `client_app_v2/lib/features/execution/models/`.
   - Execute `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/workflow.dart --build` to regenerate Freezed models with 100% type parity.
4. **Two-Phase Seeder Modernization in `@[backend_v2/seed/run_seed.py]`**:
   - Decommission `db_v2.json` and Firestore writing.
   - Update `run_seed.py` to ingest `seed_data.json` as its primary input payload:
     - Phase 1: In-memory pre-flight validation of all collections in `backend_v2/seed/seed_data.json` against strict Pydantic V2 schemas (`extra='forbid'`).
     - Phase 2: Atomic transactional upsert of system organizations, admin users, core prompt blocks, task blueprints, workflows, and output profiles into PostgreSQL 18 with freshly mapped UUIDv7 primary keys and foreign keys.
     - Verify zero legacy prefix strings exist in PostgreSQL seeded state while 100% of seed content is fully materialized in the database.
5. **Update Seed Registry & Audit Tooling**:
   - Update `backend_v2/seed/seed_registry.py` to match PostgreSQL table mappings.
   - Verify `scripts/audit_database_atoms.py --strict` executes cleanly against PostgreSQL seeded state.

### Phase 5: Complete TinyDB Eradication & AST Guardrail Lockdown

1. **Physical Deletion of Obsolete Code & Files**:
   - Delete `backend_v2/database/tinydb_driver.py`.
   - Delete `backend_v2/database/wrapper.py`.
   - Delete `backend_v2/database/firestore_driver.py`.
   - Delete `backend_v2/services/drivers/local_file_driver.py`.
   - Delete `data/db_v2.json`, `data/app.db`, and all lockfiles.
2. **Purge Dependency from Build Configurations**:
   - Remove `tinydb` from `pyproject.toml`.
   - Run `uv sync` to update `uv.lock`.
3. **Hardened AST Guardrails in `@[scripts/_ast_guardrails.py]`**:
   - Add new rule `QGR017` (Severity: `FATAL`): Prohibits importing `tinydb`, referencing `tinydb_driver`, or instantiating `TinyDBClient`.
   - Add new rule `QGR018` (Severity: `FATAL`): Prohibits importing `sqlalchemy.orm` (guaranteeing pure `asyncpg` driver architecture).
   - Add new rule `QGR019` (Severity: `FATAL`): Prohibits importing or referencing legacy `OPAQUE_STRIPE_ID_REGEX` or `EntityPrefix` in domain models.
   - Run `uv run python scripts/_ast_guardrails.py` to mathematically verify zero violations.

### Phase 6: Concurrency Hardening, Testcontainers Verification & E2E Quality Gate

1. **Integration Concurrency Testing via Testcontainers**:
   - Implement `backend_v2/tests/integration/test_postgresql_driver.py` utilizing `testcontainers-postgres`.
   - Test 7 concurrent worker coroutines writing to `trace_events` simultaneously: assert 100% completion with zero deadlocks, zero lock contention, and sequential ordering.
2. **Full Quality Gate Execution**:
   - Execute `uv run python scripts/backend_audit_loop.py backend_v2 --test`.
   - Verify Ruff formatting, MyPy strict type checking, and Pytest suites pass 100%.
3. **Live E2E Verification**:
   - Execute mandatory live integration test: `RUN_LIVE_E2E=true uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.

---

## 5. Definition of Done (DoD) & Verification Plan

### Definition of Done (DoD)

- [ ] **DDL Applied**: All 14 relational tables (including `execution_inputs`) and associated indexes created via Alembic migrations on PostgreSQL 18.
- [ ] **Execution Inputs Sourced via DB**: Cleaned forensic Markdown texts are stored directly in `execution_inputs` with `ON DELETE CASCADE`; disk-based dumping in `data/files/executions/.../inputs/` is eradicated.
- [ ] **Pure `asyncpg` Driver**: `PostgreSQLDriver` fully implements `StorageDriver` without SQLAlchemy ORM.
- [ ] **Clean Slate Seeder**: `uv run python backend_v2/seed/run_seed.py local` seeds PostgreSQL directly with pristine UUIDv7 identifiers.
- [ ] **Trace Events Sourcing**: `trace_events` table handles execution event streaming with O(1) row inserts; multi-megabyte `execution_trace` whole-table rewrites are eradicated.
- [ ] **Binary Storage Isolation**: File upload and download operate via Firebase Storage Signed URLs; backend RAM never buffers uploaded file bytes.
- [ ] **Orphaned File Cleaner**: Background cleanup task purges pending files older than 24 hours.
- [ ] **In-Memory Reducer Preserved**: `MatrixReducer` executes in-memory reductions without database queries; Tripartite Pipeline decoupling is maintained.
- [ ] **TinyDB Completely Eradicated**: `tinydb` is removed from `pyproject.toml`; `tinydb_driver.py`, `wrapper.py`, and `db_v2.json` are deleted.
- [ ] **AST Guardrails Active**: `_ast_guardrails.py` enforces `QGR017` (TinyDB ban) and `QGR018` (SQLAlchemy ORM ban) with 0 FATAL violations.
- [ ] **100% Quality Gate Pass**: `backend_audit_loop.py` passes 100% on Ruff, MyPy, and Pytest.

### Automated Verification Commands

```powershell
# 1. Run Alembic migration against local PostgreSQL 18
uv run alembic upgrade head

# 2. Execute Clean Slate database seeding
uv run python backend_v2/seed/run_seed.py local

# 3. Verify database atoms integrity
uv run python scripts/audit_database_atoms.py --strict

# 4. Execute PostgreSQL driver and concurrent trace events integration tests
uv run pytest backend_v2/tests/integration/test_postgresql_driver.py -v

# 5. Run AST Guardrails (enforcing TinyDB and SQLAlchemy ORM bans)
uv run python scripts/_ast_guardrails.py

# 6. Run markdown boundaries audit on the Epic
uv run python scripts/audit_markdown_boundaries.py --file docs/epic/EPIC_151_PostgreSQL_Clean_Slate_Migration_and_TinyDB_Eradication.md

# 7. Complete backend audit loop (Ruff + MyPy + Pytest)
uv run python scripts/backend_audit_loop.py backend_v2 --test

# 8. Mandatory Live E2E Verification Gate
$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
```

---

## 6. Required Context & Governance (Rules & KI Registry)

See the canonical `<required_context_rules>` XML block at the top of this document for the authoritative registry of active rules and Knowledge Items.
