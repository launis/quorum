# Implementation Plan: All-in-PostgreSQL 18 Sovereign Zero-ORM Architecture, CQRS Ports & Kahn Wave Unit of Work

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## 1. Objective & Architectural Sovereignty ("All-in-PostgreSQL 18 Zero-ORM")

This plan establishes Quorum's sovereign **All-in-PostgreSQL 18 Zero-ORM Architecture**, replacing legacy document-store drivers (`TinyDBDriver`, `FirestoreDriver`, and file-based `db_v2.json.lock` synchronization) and superseding heavy stateful ORM layers (SQLAlchemy 2.0 `DeclarativeBase` / `AsyncSession` identity maps) with a deterministic, high-throughput persistence architecture built on five foundational pillars:

1. **Zero-ORM & Direct Binary `asyncpg` + Pydantic V2 `pydantic_core` Rust Boundary**:
   - Eliminates ORM session state tracking, `MissingGreenlet` concurrency traps inside `asyncio.TaskGroup`, and double JSON deserialization.
   - Registers binary `pydantic_core` (`to_json` / `from_json`) JSONB codecs directly on the `asyncpg` connection pool (`conn.set_type_codec("jsonb", encoder=encode_jsonb_binary, decoder=decode_jsonb_binary, schema="pg_catalog", format="binary")`), explicitly handling PostgreSQL's 1-byte `\x01` binary JSONB wire version header without requiring external `orjson` packages outside `uv.lock`.
   - Encapsulates `asyncpg` driver interactions behind `@runtime_checkable` structural protocols (`AsyncPgPoolProtocol`, `AsyncPgConnectionProtocol`, `AsyncPgTransactionProtocol`, `AsyncPgRecordProtocol`) with lazy driver loading inside `PostgresPoolManager.connect()`, ensuring `scripts/audit_clean_imports.py` and `mypy --strict` pass 100% in zero-trust environments.
   - Reconstitutes database records at the repository adapter edge directly into immutable (`ConfigDict(strict=True, extra="forbid", frozen=True)`) Pydantic V2 domain models and DTOs with zero naked dictionaries (`dict[str, Any]`).
2. **PostgreSQL 18 Native UUIDv7 (RFC 9562) Toolkit & `PrefixedUUID7` Bridge**:
   - Leverages PostgreSQL 18 native `uuidv7()` (48-bit Unix epoch milliseconds + 12-bit sub-millisecond monotonic counter `rand_a` + 62-bit cryptographic randomness `rand_b`) as the Single Source of Truth for temporal and B-Tree index locality.
   - Uses zero-byte virtual generated columns (`created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(id)) VIRTUAL` on PostgreSQL 18+, with automatic `STORED` fallback on PostgreSQL 17) and kernel-level version guardrails (`CHECK (uuid_extract_version(id) = 7)`).
   - Preserves 100% cross-language Opaque Stripe ID parity (`pattern=r"^([a-z]{2,5})_[a-fA-F0-9]{16,32}$"`) with Flutter Freezed models via the `PrefixedUUID7` type bridge (`nod_<hex32>`, `edg_<hex32>`, `exe_<hex32>`), mapping 16-byte native PostgreSQL `UUID` columns to canonical prefixed string identifiers at the Python boundary and providing monotonic RFC 9562 `generate_uuid7_opaque_id` generation for in-memory test parity.
   - Enforces a Clean-Slate Cutover: zero legacy ETL migration from TinyDB; execution and report tables start completely clean with zero backward-compatibility shims.
3. **Draft vs. Persisted Entity Pattern & Single-Round Multi-CTE Wave Ingestion**:
   - Solves the distributed "Two Clocks" problem: parallel agents in Kahn topological waves produce in-memory symbolic drafts (`NodeDraft` with `local_key` and `EdgeDraft` with `source_key` / `target_key`).
   - Materializes an entire wave's nodes and edges in **one atomic SQL Multi-CTE statement** (`materialize_wave`) over a single network roundtrip (< 5 ms), where PostgreSQL generates `uuidv7()` keys, binds edges via `INNER JOIN input_nodes ON local_key`, and returns hydrated `PropositionNode` entities via `RETURNING`.
4. **Hexagonal CQRS Ports (`typing.Protocol`) & Post-Wave Unit of Work (`QuorumUnitOfWork`)**:
   - Segregates persistence into narrow structural protocols: `GraphMutationPort`, `TopologyResolutionPort`, `CausalReasoningPort`, and `EntityPersistencePort`.
   - Enforces the **Post-Wave Atomic Commit Invariant**: LLM inference and agent execution inside `asyncio.TaskGroup` run 100% in memory without holding database connections; `PostgresUnitOfWork` acquires an `asyncpg` connection in `repeatable_read` isolation strictly after wave completion, flushes the batch in milliseconds, and releases the connection immediately.
   - Implements `CteReasoningStrategy` (ANSI SQL `WITH RECURSIVE ... CYCLE`) as the production reasoning engine and `PgqReasoningStrategy` (`GRAPH_TABLE` SQL/PGQ) as a configurable strategy controlled by `postgres_enable_pgq_graph_table` on `Settings`.
5. **Closed 12-Table All-in-PostgreSQL Topology & Flat FinOps Columns**:
   - Models all 10 core Quorum system collections (`users`, `organizations`, `workflows`, `steps`, `prompt_blocks`, `output_profiles`, `system_configs`, `executions`, `report_artifacts`, `report_binaries`) alongside the 2 causal/Toulmin graph tables (`quorum_nodes`, `quorum_edges`).
   - Stores FinOps telemetry (`prompt_tokens`, `completion_tokens`, `cached_tokens`, `reasoning_tokens`, `cumulative_synthesis_tokens`, `total_cost_usd`, `dag_cost_usd`, `cumulative_synthesis_cost`, `duration_ms`) as flat `BIGINT` and `NUMERIC(10,6)` columns.
   - Isolates heavy PDF binaries (`BYTEA`) in `report_binaries` (TOAST-compressed with `ON DELETE CASCADE`) to protect `shared_buffers` during list and SDUI queries.

---

## 2. Scope & Target Boundaries

### TARGET Files (Authorized for Modification/Creation)

| Category | File Reference | Architectural Responsibility |
| :--- | :--- | :--- |
| `[MODIFY]` | `@[backend_v2/models/enums.py#L209-L222]` | Add `NODE = "nod"` and `EDGE = "edg"` to `EntityPrefix`; add `PropositionNodeType`, `DependencyRelationType`, and `StorageBackend` StrEnums. |
| `[MODIFY]` | `@[backend_v2/models/core_base.py#L165-L190]` | Add `PrefixedUUID7` validation/serialization bridge (`parse_prefixed_uuid7`, `format_prefixed_uuid7`, `generate_uuid7_opaque_id`) mapping 16-byte `UUID` to 32-hex Opaque Stripe IDs with RFC 9562 monotonic sub-millisecond ordering. |
| `[NEW]` | `[NEW] @[backend_v2/models/domain/proposition_graph.py]` | Immutable Pydantic V2 models (`ConfigDict(strict=True, extra="forbid", frozen=True)`): `PropositionPayloadDTO`, `NodeDraft`, `EdgeDraft`, `PropositionNode`, `DependencyEdge`, `FalsifiedClaimMatch`, `ReportBinaryPayloadDTO`, and `CycleDetectedError`. |
| `[MODIFY]` | `@[backend_v2/database/interfaces.py#L314-L335]` | Define `@runtime_checkable` Hexagonal CQRS Ports: `GraphMutationPort`, `TopologyResolutionPort`, `CausalReasoningPort`, `EntityPersistencePort`, and `QuorumUnitOfWork`. |
| `[MODIFY]` | `@[backend_v2/settings.py#L47-L51]` | Re-export `StorageBackend` from `backend_v2.models.enums` and declare separated environment-driven PostgreSQL host, port, pool, timeout, and SQL/PGQ settings in `Settings` (`@[backend_v2/settings.py#L54-L1063]`). |
| `[NEW]` | `[NEW] @[backend_v2/database/migrations/001_pg18_uuidv7_schema.sql]` | Pure SQL DDL for the 12 closed tables (`users`, `organizations`, `workflows`, `steps`, `prompt_blocks`, `output_profiles`, `system_configs`, `executions`, `report_artifacts`, `report_binaries`, `quorum_nodes`, `quorum_edges`) with PG 18 `uuidv7()`, `uuid_extract_timestamp() VIRTUAL` (PG 17 `STORED` compatibility block), and `uuid_extract_version() = 7` constraints. |
| `[NEW]` | `[NEW] @[backend_v2/database/postgres/__init__.py]` | Explicit package facade re-exporting PostgreSQL pool, protocols, adapters, and Unit of Work symbols (`__all__`). |
| `[NEW]` | `[NEW] @[backend_v2/database/postgres/pool.py]` | `PostgresPoolManager`, structural `AsyncPgPoolProtocol` / `AsyncPgConnectionProtocol`, binary `pydantic_core` `\x01`-prefixed JSONB codec registration, explicit timeouts from `settings.py`, and idempotent SQL migration runner. |
| `[NEW]` | `[NEW] @[backend_v2/database/postgres/graph_adapter.py]` | `PostgresGraphAdapter` implementing single-round Multi-CTE `materialize_wave`, `upsert_wave_batch`, `assert_acyclic` (`WITH RECURSIVE ... CYCLE`), `fetch_next_kahn_wave`, `CteReasoningStrategy`, and `PgqReasoningStrategy`. |
| `[NEW]` | `[NEW] @[backend_v2/database/postgres/entity_adapter.py]` | `PostgresEntityAdapter` implementing `EntityPersistencePort` for the 10 core collections and TOAST binary streaming for `report_binaries` (clean-slate, zero legacy migration). |
| `[NEW]` | `[NEW] @[backend_v2/database/postgres/uow.py]` | `PostgresUnitOfWork` implementing `QuorumUnitOfWork` over `asyncpg` `repeatable_read` transactions with RFC 7807 error translation. |
| `[MODIFY]` | `@[backend_v2/database/factory.py#L24-L64]` | Wire `POSTGRES` member of `StorageBackend` factory initialization (`create_unit_of_work`) with Zero-Fallback cutover semantics and RFC 7807 `ConfigurationError` logging. |
| `[NEW]` | `[NEW] @[backend_v2/tests/fakes/in_memory_uow.py]` | Stateful `InMemoryUnitOfWork`, `InMemoryGraphAdapter`, `InMemoryEntityAdapter`, and `InMemoryAsyncPgPool` implementing `QuorumUnitOfWork` and `AsyncPgPoolProtocol` for 0 ms contract and orchestrator testing. |
| `[NEW]` | `[NEW] @[scripts/audit_zero_orm_strictness.py]` | Deterministic AST guardrail verifier enforcing Zero-ORM (`ZORM001`–`ZORM005`) across `backend_v2/database/`. |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]` | Dedicated unit and ISTQB negative test suite for `scripts/audit_zero_orm_strictness.py` (`ZORM001`–`ZORM005`) so Step 1 passes 90% script coverage. |
| `[MODIFY]` | `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L61-L67]` | Register `audit_zero_orm_strictness.py` in `ALL_SCRIPTS` inventory and update exhaustive script count assertion (`36` -> `37`). |
| `[MODIFY]` | `@[backend_v2/tests/unit/models/test_enums.py#L153-L166]` | Add unit tests for `StorageBackend`, `PropositionNodeType`, `DependencyRelationType`, and `EntityPrefix` (`NODE`, `EDGE`). |
| `[MODIFY]` | `@[backend_v2/tests/unit/models/test_core_base.py#L125-L140]` | Add positive and ISTQB negative unit tests for `parse_prefixed_uuid7`, `format_prefixed_uuid7`, and monotonic `generate_uuid7_opaque_id` so Step 1 passes 90% coverage. |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/models/domain/test_proposition_graph.py]` | Unit and ISTQB boundary tests for all 7 models in `proposition_graph.py` and `CycleDetectedError` so Step 2 passes 90% coverage. |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_interfaces.py#L7-L21]` | Verify `GraphMutationPort`, `TopologyResolutionPort`, `CausalReasoningPort`, `EntityPersistencePort`, and `QuorumUnitOfWork` protocol definitions. |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_settings.py#L136-L158]` | Verify PostgreSQL `Settings` fields, `StorageBackend` `POSTGRES` resolution, and pool/timeout `@model_validator` bounds. |
| `[MODIFY]` | `@[backend_v2/tests/unit/test_factory.py#L28-L32]` | Verify `create_unit_of_work` and `get_driver` fail-fast `ConfigurationError` with RFC 7807 logging for `POSTGRES` and invalid backends. |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/database/test_postgres.py]` | Parameterized package contract test suite + ISTQB negative boundary tests for `InMemoryUnitOfWork`, `PostgresUnitOfWork`, `PostgresPoolManager`, Multi-CTE wave ingestion, and cycle detection. |

### CONTEXT Files (Strictly Read-Only)

- `@[backend_v2/models/domain/execution.py]`
- `@[backend_v2/models/domain/system_config.py]`
- `@[backend_v2/models/domain/mcp.py]`
- `@[backend_v2/models/domain/xai.py]`
- `@[backend_v2/models/dtos/atom_evaluation.py]`
- `@[backend_v2/models/state.py]`
- `@[backend_v2/exceptions.py]`

---

## 3. Pre-Implementation Technical Debt, Falsification & Dict Eradication Verification

Pre-flight execution of `uv run python scripts/audit_dict_eradication.py` and `uv run python scripts/audit_technical_debt.py --plan docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md --include-one-hop` confirmed **0 violations** across all direct target files (`interfaces.py`, `factory.py`, `core_base.py`, `enums.py`, `settings.py`). Scanning all 34 1-hop callers surfaced 2 advisory warnings (`TD_DICT_GET` on `self.driver.get(_COLLECTION_NAME, report_id)` at lines 63 and 120 of `backend_v2/database/repositories/report_artifact.py`), which are recorded as read-only out-of-scope technical debt per `ban_drive_by_schema_mutations`.

### Phase 1: Pre-Implementation Cleanups & Boundary Hygiene

1. **Tripartite Configuration Architecture Cleanup (`@[backend_v2/models/enums.py#L209-L222]` & `@[backend_v2/settings.py#L47-L51]`)**:
   - **Root Cause**: `StorageBackend` was previously declared inline inside `backend_v2/settings.py` instead of `backend_v2/models/enums.py`, violating `strict_configuration_segregation` ("1) `enums.py` contains finite constants/taxonomy, 2) `settings.py` contains all global limits/bounds/env config").
   - **Cleanup Action**: Migrate `StorageBackend` (with `FIRESTORE`, `LOCAL`, and `POSTGRES` members) into `backend_v2/models/enums.py` and explicitly re-export `from backend_v2.models.enums import StorageBackend as StorageBackend` in `backend_v2/settings.py`.
2. **Database Factory RFC 7807 Dual-Reporting & Docstring Cleanup (`@[backend_v2/database/factory.py#L24-L64]`)**:
   - **Root Cause**: `get_driver` in `backend_v2/database/factory.py` documented `Raises: ValueError` while actually raising `ConfigurationError` without a preceding structured `logger.error` call, violating `docstring_fail_fast_ban` and `rfc7807_dual_reporting_mandate`.
   - **Cleanup Action**: Synchronize `get_driver` and `create_unit_of_work` docstrings to declare `Raises: ConfigurationError` / `AppException` and log structured `ErrorCodes.CONFIGURATION_ERROR` context before raising.

### System 2 Red-Team Falsification & Proactive Hardening Matrix

| Falsification ID | Discovered Vulnerability / Flawed Assumption | Root Cause Analysis | Proactive Architectural Hardening |
| :--- | :--- | :--- | :--- |
| **RT-01: Binary `jsonb` `\x01` Wire Header & Uninstalled `orjson`/`asyncpg`** | Original plan specified top-level `import orjson` / `import asyncpg` and raw `orjson.dumps` / `orjson.loads` on `format="binary"`. | Neither `orjson` nor `asyncpg` is installed in `uv.lock`, so top-level imports crash `scripts/audit_clean_imports.py` (`ModuleNotFoundError`) and violate `dependency_hallucination_firewall`. Furthermore, PostgreSQL's `jsonb_send`/`jsonb_recv` binary wire format prepends a 1-byte version header (`\x01`); omitting `b"\x01"` raises `DataError: unsupported jsonb version number 123`. | Use Pydantic V2's installed Rust `pydantic_core` (`to_json`, `from_json`) with explicit `b"\x01"` binary header framing (`encode_jsonb_binary`, `decode_jsonb_binary`). Define `@runtime_checkable` `AsyncPgPoolProtocol` / `AsyncPgConnectionProtocol` in `pool.py` and lazily import `asyncpg` inside `PostgresPoolManager.connect()`. |
| **RT-02: Hardcoded Credentials in Default DSN** | Original Step 3 proposed `default="postgresql://quorum:quorum@127.0.0.1:5432/quorum"`. | Embedding `quorum:quorum` credentials and a hardcoded URL in source code violates `credential_hardcoding_ban` and `localhost_endpoint_hardcoding_ban`. | Split configuration into `postgres_host`, `postgres_port`, `postgres_user`, `postgres_password: str | None = None`, `postgres_db`, and `postgres_dsn: str | None = None` on `Settings`, resolving credentials strictly from environment injection. |
| **RT-03: `QGR007` AST Failure on `V2CoreBase` Subclasses** | Original Step 2 omitted explicit `model_config = ConfigDict(...)` on 6 of the 7 models in `proposition_graph.py`. | `QuorumGuardrailVisitor.visit_ClassDef` (`QGR007` in `scripts/_ast_guardrails.py`) checks `has_local_base` only within the same file; inheriting `V2CoreBase` from `core_base.py` without an explicit class-level `model_config` triggers a `FATAL` `QGR007` violation. | Mandate explicit `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` inside the class body of every Pydantic model in `proposition_graph.py` and adapter row DTOs. |
| **RT-04: `QGR014` Test Double Location Ban** | Defining fake `asyncpg` or port classes inside `test_uow_contract.py` or using `AsyncMock`. | `scripts/_ast_guardrails.py` populates `INTERFACE_REPOSITORY_METHODS` from `interfaces.py` and fatally bans (`QGR014`) any class outside `backend_v2/tests/fakes/` from implementing interface method names or mocking repository protocols. | Encapsulate `InMemoryUnitOfWork`, `InMemoryGraphAdapter`, `InMemoryEntityAdapter`, and stateful `InMemoryAsyncPgPool` / `InMemoryAsyncPgConnection` strictly inside `[NEW] @[backend_v2/tests/fakes/in_memory_uow.py]`. |
| **RT-05: Monotonic Sub-Millisecond UUIDv7 Ordering** | Generating multiple UUIDv7 IDs within the same millisecond in `InMemoryUnitOfWork` can collide or sort out of order. | Without RFC 9562 Section 6.2 monotonic counter incrementation (`rand_a`) within the same millisecond tick, in-memory `ORDER BY node_id ASC` diverges from PostgreSQL 18 `uuidv7()`. | Implement thread-safe 12-bit monotonic `rand_a` counter state + `secrets.randbits(62)` inside `generate_uuid7_opaque_id` in `backend_v2/models/core_base.py`. |
| **RT-06: `test_scripts_cli_help.py` Inventory Gate & `audit_warning_baseline.py` Census `P` Regex Trap** | Creating `scripts/audit_zero_orm_strictness.py` without registering it in `test_scripts_cli_help.py`, or writing contiguous `dict[str, Any]` tokens inside `scripts/` or `tests/`. | `test_script_count_is_exhaustive()` in `test_scripts_cli_help.py` asserts `ALL_SCRIPTS == physical_scripts` and `len(ALL_SCRIPTS) == 36`. Additionally, Stage 9/10 of `backend_audit_loop.py` (`audit_warning_baseline.py --verify-zero`) runs `re.findall(r"\b[Dd]ict\[\s*str\s*,\s*(?:Any|object)\s*\]", text)` on raw file text across `scripts/` and `backend_v2/tests/` against `CURRENT_RESIDUAL_CEILINGS.p = 0`. | Add `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L61-L67]` to Step 1 `<targets>` (`36` -> `37`), inspect `ast.Subscript` nodes structurally without writing contiguous `dict[str, ...]` tokens in docstrings/comments, and concatenate `"dict" + "[str, Any]"` in synthetic test strings. |
| **RT-07: Step-by-Step 90% TDD Coverage Gate Alignment (`backend_audit_loop.py --test`)** | Deferring unit tests for `core_base.py`, `enums.py`, `proposition_graph.py`, `interfaces.py`, `settings.py`, and `factory.py` until Step 5 (`test_postgres.py`). | `backend_audit_loop.py <target> --test` maps each source file to its dedicated unit test (`test_core_base.py`, `test_proposition_graph.py`, `test_settings.py`, `test_factory.py`) and enforces `--fail-under=90` immediately at the end of Steps 1–4. | Include `@[backend_v2/tests/unit/models/test_enums.py#L153-L166]`, `@[backend_v2/tests/unit/models/test_core_base.py#L125-L140]`, `[NEW] @[backend_v2/tests/unit/models/domain/test_proposition_graph.py]`, `@[backend_v2/tests/unit/test_interfaces.py#L7-L21]`, `@[backend_v2/tests/unit/test_settings.py#L136-L158]`, and `@[backend_v2/tests/unit/test_factory.py#L28-L32]` in their respective steps. |
| **RT-08: `QGR002` `.get()` Lookup Ban & `QGR009` `AppException` Contract** | Calling `row.get(...)` on records/dicts or raising `AppException(ErrorCodes.XXX)` without `details={"error_code": ...}`. | `QGR002` fatally bans `.get()` on variables outside `LEGITIMATE_GET_CALLERS`, and `AppException.error_code` (`backend_v2/exceptions.py`) reads `self.details["error_code"]` while `QGR009` enforces typed `ErrorCodes` in `details`. | Mandate direct subscript indexing (`row["col"]`) and positive membership checks (`if key in store:`) instead of `.get()`, and instantiate `AppException(message=..., status_code=..., details={"error_code": ErrorCodes.<CODE>.value})`. |
| **RT-09: `backend_audit_loop.py` Package Test Discovery Crash on `backend_v2/database/postgres/ --test`** | Naming the Step 5 contract test suite `test_uow_contract.py` instead of `test_postgres.py`. | `run_tests_with_strict_coverage("backend_v2/database/postgres/")` in `scripts/backend_audit_loop.py` checks `test_postgres.py`, `test_postgres*.py`, and exact submodule stems (`test_pool.py`, `test_uow.py`). `test_uow_contract.py` matches none of these, causing `backend_audit_loop.py backend_v2/database/postgres/ --test` to fall back to non-existent `backend_v2/tests/unit/database/postgres` and fail with Pytest Exit Code 4. | Name the contract test suite `[NEW] @[backend_v2/tests/unit/database/test_postgres.py]` so `backend_audit_loop.py --test` automatically discovers it for `backend_v2/database/postgres/`, `backend_v2/database/`, and every individual module inside `backend_v2/database/postgres/`. |
| **RT-10: Dedicated Unit Test Suite for `scripts/audit_zero_orm_strictness.py` (`test_audit_zero_orm_strictness.py`)** | Creating `scripts/audit_zero_orm_strictness.py` in Step 1 without its corresponding `backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py` unit test file. | Running `uv run python scripts/backend_audit_loop.py scripts/audit_zero_orm_strictness.py --test --ast-strict` per `backend_audit_execution` resolves `backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py` and enforces `--fail-under=90` coverage on `scripts.audit_zero_orm_strictness`. | Add `[NEW] @[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]` to Step 1 `<targets>` and `<action>` with positive and ISTQB negative tests for `ZORM001`–`ZORM005`. |
| **RT-11: Non-Exempt `primitive_obsession_nested_dicts` & `QGR023` Tuple Ban in `backend_v2/database/postgres/`** | Annotating variables or parameters in `backend_v2/database/postgres/` with `list[dict[...]]`, `Sequence[Mapping[...]]`, or 3+ element tuples (`tuple[uuid.UUID, str, float]`). | `backend_v2/database/postgres/` is not in `BOUNDARY_EXEMPTION_FILES`. `_find_nested_dict_subscript` (`audit_dict_eradication.py`) fatally rejects any collection of `dict`/`Mapping`, and `QGR023` (`_ast_guardrails.py`) fatally rejects 3+ element tuples or identical-primitive 2-tuples. | Define `AsyncPgRecordProtocol` as a standalone `Protocol` (`def __getitem__(self, key: str) -> object: ...`) without inheriting `Mapping`, serialize `Sequence[NodeDraft]` / `Sequence[EdgeDraft]` directly via `pydantic_core.to_json(list(drafts))` without `list[dict[...]]` annotations, and type `executemany` parameter batches as `Sequence[Sequence[object]]`. |

### Five-Axis System 2 Architectural Directive Matrix

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Zero-ORM AST Guardrail & Enum Taxonomy (`[NEW] @[scripts/audit_zero_orm_strictness.py]`, `[NEW] @[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]`, `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L61-L67]`, `@[backend_v2/models/enums.py#L209-L222]`, `@[backend_v2/models/core_base.py#L165-L190]`, `@[backend_v2/tests/unit/models/test_enums.py#L153-L166]`, `@[backend_v2/tests/unit/models/test_core_base.py#L125-L140]`)** | Application-level UUIDv4 randomness; inline `StorageBackend` in `settings.py`; un-prefixed `UUID` exposure to Flutter; contiguous naked dict tokens in `scripts/` breaking Census `P`. | Static AST verifier (`ZORM001`–`ZORM005`) registered in `ALL_SCRIPTS` with >90% unit coverage in `test_audit_zero_orm_strictness.py`; PostgreSQL 18 native `uuidv7()` + `PrefixedUUID7` bridge (`nod_<hex32>`, `edg_<hex32>`) with RFC 9562 monotonic `rand_a` counter. | Pruned physical `created_at` storage on graph tables and custom timestamp triggers. | `uv run python scripts/backend_audit_loop.py scripts/audit_zero_orm_strictness.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/models/core_base.py --test --ast-strict`. |
| **Proposition Graph Domain Models & Hexagonal CQRS Ports (`[NEW] @[backend_v2/models/domain/proposition_graph.py]`, `[NEW] @[backend_v2/tests/unit/models/domain/test_proposition_graph.py]`, `@[backend_v2/database/interfaces.py#L314-L335]`, `@[backend_v2/tests/unit/test_interfaces.py#L7-L21]`)** | Loose untyped dictionary payloads; implicit `V2CoreBase` config inheritance failing `QGR007`; `Field(ge=..., le=...)` on floats. | Explicit `ConfigDict(strict=True, extra="forbid", frozen=True)` on all 7 models; float `@field_validator` bounds; `@runtime_checkable` `GraphMutationPort`, `TopologyResolutionPort`, `CausalReasoningPort`, `EntityPersistencePort`, `QuorumUnitOfWork`. | Pruned monolithic repository inheritance on graph ports and intermediate mutable builder classes. | `uv run python scripts/backend_audit_loop.py backend_v2/models/domain/proposition_graph.py --test --ast-strict` + ISTQB float boundary tests. |
| **PostgreSQL 18 Schema, Settings & Binary JSONB Pool (`@[backend_v2/settings.py#L47-L51]`, `@[backend_v2/settings.py#L54-L1063]`, `@[backend_v2/tests/unit/test_settings.py#L136-L158]`, `[NEW] @[backend_v2/database/migrations/001_pg18_uuidv7_schema.sql]`, `[NEW] @[backend_v2/database/postgres/__init__.py]`, `[NEW] @[backend_v2/database/postgres/pool.py]`)** | Hardcoded `quorum:quorum@127.0.0.1` DSN credentials; uninstalled `orjson` imports; missing `\x01` binary JSONB wire version byte; `AsyncPgRecordProtocol` inheriting `Mapping`. | Separated environment-injected settings; `pydantic_core` (`to_json`/`from_json`) with `\x01` binary JSONB header; standalone `AsyncPgRecordProtocol` (`__getitem__`) and `AsyncPgPoolProtocol` with lazy `asyncpg` connect. | Pruned SQLAlchemy 2.0 ORM, `DeclarativeBase`, `TypeDecorator`, and Alembic ORM autogenerate complexity. | `uv run python scripts/backend_audit_loop.py backend_v2/settings.py --test --ast-strict` + binary JSONB codec unit tests rejecting version != 1. |
| **Single-Round Wave Adapters & Post-Wave UoW (`[NEW] @[backend_v2/database/postgres/graph_adapter.py]`, `[NEW] @[backend_v2/database/postgres/entity_adapter.py]`, `[NEW] @[backend_v2/database/postgres/uow.py]`, `[NEW] @[backend_v2/tests/fakes/in_memory_uow.py]`, `@[backend_v2/database/factory.py#L24-L64]`, `@[backend_v2/tests/unit/test_factory.py#L28-L32]`, `[NEW] @[backend_v2/tests/unit/database/test_postgres.py]`)** | Two-roundtrip node/edge inserts; `{**dict(r)}` or `.get()` row lookups (`QGR002`); `list[dict[...]]` or 3+ tuple annotations (`QGR023`); holding DB transactions across LLM calls; `AsyncMock` port mocks outside `tests/fakes/`. | Single-Round Multi-CTE `materialize_wave` in 1 RTT using `pydantic_core.to_json(list(drafts))`; direct subscript `row["col"]` + typed row hydration DTOs; `repeatable_read` post-wave `PostgresUnitOfWork`; stateful `InMemoryUnitOfWork` and `InMemoryAsyncPgPool`. | Pruned client-side surrogate ID mapping tables and distributed two-phase commit coordinators. | Parameterized `test_postgres.py` verifying identical behavior on `InMemoryUnitOfWork` and `PostgresUnitOfWork` with >=2 negative cases per feature. |

---

## 4. Canonical Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="PHASE_1_CLEANUPS_AST_GUARDRAIL_AND_ENUM_FOUNDATION">
    <objective>Execute Phase 1 Pre-Implementation Cleanups, create the static AST guardrail verifier for Zero-ORM strictness, and extend EntityPrefix, StorageBackend, and PrefixedUUID7 utilities with full unit test coverage.</objective>
    <constraint invariant="ast_guardrail_mandate">Build AST Guardrail tests first to statically enforce Zero-ORM, zero naked dicts in database adapters, and closed table topology before writing adapter implementations.</constraint>
    <constraint invariant="opaque_stripe_id_ssot_constant_mandate">Bind all entity prefixes in EntityPrefix and validate against OPAQUE_STRIPE_ID_REGEX.</constraint>
    <targets>
      <target action="NEW">[NEW] @[scripts/audit_zero_orm_strictness.py]</target>
      <target action="NEW">[NEW] @[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]</target>
      <target action="MODIFY">@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L61-L67]</target>
      <target action="MODIFY">@[backend_v2/models/enums.py#L209-L222]</target>
      <target action="MODIFY">@[backend_v2/models/core_base.py#L165-L190]</target>
      <target action="MODIFY">@[backend_v2/tests/unit/models/test_enums.py#L153-L166]</target>
      <target action="MODIFY">@[backend_v2/tests/unit/models/test_core_base.py#L125-L140]</target>
    </targets>
    <action>
      1. Create `[NEW] @[scripts/audit_zero_orm_strictness.py]` with a standardized CLI (`argparse.ArgumentParser`, `RawDescriptionHelpFormatter`, PowerShell epilog examples) using Python's `ast` module (zero reflection, and zero contiguous `dict[str, ...]` literal substrings in docstrings/comments/messages to preserve `audit_warning_baseline.py` Census `P == 0`) to scan `backend_v2/database/postgres/`, `backend_v2/models/domain/proposition_graph.py`, and `backend_v2/database/migrations/001_pg18_uuidv7_schema.sql` for five fatal rules:
         - `ZORM001`: Ban imports of `sqlalchemy`, `alembic`, or `orjson` inside `backend_v2/database/postgres/`.
         - `ZORM002`: Ban `ast.Subscript` untyped `dict` annotations targeting `Any`/`object` and `dict(r)` call unpacking inside `backend_v2/database/postgres/` and `proposition_graph.py`.
         - `ZORM003`: Ban `except Exception:` without explicit typed `AppException` re-raise in `backend_v2/database/postgres/`.
         - `ZORM004`: Enforce that SQL `CREATE TABLE` identifiers in `001_pg18_uuidv7_schema.sql` belong strictly to the closed 12-table set (`users`, `organizations`, `workflows`, `steps`, `prompt_blocks`, `output_profiles`, `system_configs`, `executions`, `report_artifacts`, `report_binaries`, `quorum_nodes`, `quorum_edges`).
         - `ZORM005`: Ban calling `llm_client` or `execute_structured_task` inside `PostgresUnitOfWork` or `backend_v2/database/postgres/`.
      2. Create `[NEW] @[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]` testing positive clean modules and >=2 ISTQB negative partitions (`ZORM001`–`ZORM005` violations using concatenated `"dict" + "[str, Any]"`, syntax errors, and CLI exit codes), and update `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L61-L67]` to include `"audit_zero_orm_strictness.py"` in `ALL_SCRIPTS` and update `assert len(ALL_SCRIPTS) == 37`.
      3. In `@[backend_v2/models/enums.py#L209-L222]`, execute Phase 1 cleanup by defining `StorageBackend(StrEnum)` (`FIRESTORE = "FIRESTORE"`, `LOCAL = "LOCAL"`, `POSTGRES = "POSTGRES"`), extending `EntityPrefix` with `NODE = "nod"` and `EDGE = "edg"`, and adding `PropositionNodeType(StrEnum)` (`CLAIM = "claim"`, `GROUND = "ground"`, `WARRANT = "warrant"`, `REBUTTAL = "rebuttal"`, `SCM_VAR = "scm_var"`) and `DependencyRelationType(StrEnum)` (`SUPPORTS = "supports"`, `WARRANTS = "warrants"`, `REBUTS = "rebuts"`, `CAUSES = "causes"`). Export all new symbols in `__all__`.
      4. In `@[backend_v2/models/core_base.py#L165-L190]`, implement and export in `__all__`:
         - `parse_prefixed_uuid7(value: str | uuid.UUID, expected_prefix: EntityPrefix, enforce_v7: bool = True) -> uuid.UUID`: Validates `OPAQUE_STRIPE_ID_REGEX` and `expected_prefix.value`, parses the 32-char hex into `uuid.UUID`, verifies `parsed.version == 7` when `enforce_v7` is `True`, and logs + raises `AppException(message=..., status_code=status.HTTP_400_BAD_REQUEST, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})` on any mismatch.
         - `format_prefixed_uuid7(raw_uuid: uuid.UUID | str, prefix: EntityPrefix, enforce_v7: bool = True) -> str`: Validates `uuid.UUID` version 7 when `enforce_v7` is `True` and returns `f"{prefix.value}_{uuid_obj.hex}"`.
         - `generate_uuid7_opaque_id(prefix: EntityPrefix, timestamp_ms: int | None = None) -> str`: Generates an RFC 9562 version 7 UUID (48-bit Unix epoch ms + thread-safe monotonic 12-bit `rand_a` counter + 62-bit `secrets.randbits(62)` `rand_b` with RFC 9562 variant `0b10`) formatted via `format_prefixed_uuid7`.
      5. Update `@[backend_v2/tests/unit/models/test_enums.py#L153-L166]` and `@[backend_v2/tests/unit/models/test_core_base.py#L125-L140]` with positive and ISTQB negative boundary tests for `StorageBackend`, `PropositionNodeType`, `DependencyRelationType`, `parse_prefixed_uuid7`, `format_prefixed_uuid7`, and monotonic `generate_uuid7_opaque_id`.
      6. Execute `uv run python scripts/backend_audit_loop.py scripts/audit_zero_orm_strictness.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/models/enums.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/models/core_base.py --test --ast-strict`, and `uv run pytest backend_v2/tests/unit/scripts/test_scripts_cli_help.py`.
    </action>
  </step>

  <step id="2" name="PROPOSITION_GRAPH_DOMAIN_MODELS_AND_HEXAGONAL_CQRS_PORTS">
    <objective>Implement immutable Pydantic V2 Draft and Persisted proposition graph models, declare the Hexagonal CQRS Ports in interfaces.py, and verify >90% unit test coverage.</objective>
    <constraint invariant="strict_pydantic_v2_rust">Every Pydantic model class body MUST explicitly declare model_config = ConfigDict(strict=True, extra='forbid', frozen=True) (enforcing QGR007) and PEP 593 Annotated fields.</constraint>
    <constraint invariant="vertex_serving_grammar_fix">Move float ge/le bounds to @field_validator methods rather than Field(ge=..., le=...).</constraint>
    <targets>
      <target action="NEW">[NEW] @[backend_v2/models/domain/proposition_graph.py]</target>
      <target action="NEW">[NEW] @[backend_v2/tests/unit/models/domain/test_proposition_graph.py]</target>
      <target action="MODIFY">@[backend_v2/database/interfaces.py#L314-L335]</target>
      <target action="MODIFY">@[backend_v2/tests/unit/test_interfaces.py#L7-L21]</target>
    </targets>
    <action>
      1. Create `[NEW] @[backend_v2/models/domain/proposition_graph.py]` defining the following classes (each explicitly declaring `model_config = ConfigDict(strict=True, extra="forbid", frozen=True)` in its class body to satisfy `QGR007`):
         - `PropositionPayloadDTO(V2CoreBase)`:
           * `statement: Annotated[str, Field(min_length=1, description="Canonical proposition statement or claim text.")]`
           * `source_atom_id: Annotated[str | None, Field(default=None, pattern=OPAQUE_STRIPE_ID_REGEX, description="Optional originating atom ID.")]`
           * `source_quotes: Annotated[tuple[str, ...], Field(default=(), description="Exact lexical evidence quotes.")]`
           * `metadata: Annotated[dict[str, str | int | float | bool], Field(default_factory=dict, description="Flat typed primitive telemetry attributes.")]`
         - `NodeDraft(V2CoreBase)`:
           * `local_key: Annotated[str, Field(min_length=1, max_length=128, description="Wave-local symbolic identifier.")]`
           * `node_type: Annotated[PropositionNodeType, Field(description="Toulmin or SCM node classification.")]`
           * `confidence: Annotated[float, Field(description="Confidence score in [0.0, 1.0].")]` (validated via `@field_validator("confidence")` enforcing `0.0 <= v <= 1.0`)
           * `payload: Annotated[PropositionPayloadDTO, Field(description="Strictly validated proposition payload DTO.")]`
         - `EdgeDraft(V2CoreBase)`:
           * `source_key: Annotated[str, Field(min_length=1, max_length=128, description="Source NodeDraft local_key.")]`
           * `target_key: Annotated[str, Field(min_length=1, max_length=128, description="Target NodeDraft local_key.")]`
           * `relation_type: Annotated[DependencyRelationType, Field(description="Causal or Toulmin relation type.")]`
           * `causal_weight: Annotated[float, Field(default=1.0, description="Edge weight in [-1.0, 1.0].")]` (validated via `@field_validator("causal_weight")` enforcing `-1.0 <= v <= 1.0` and `@model_validator(mode="after")` rejecting self-loops `source_key == target_key`)
         - `PropositionNode(V2CoreBase)`:
           * `node_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Persisted nod_<uuid7_hex> identifier.")]`
           * `run_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Parent exe_<uuid7_hex> identifier.")]`
           * `node_type: Annotated[PropositionNodeType, Field(description="Toulmin or SCM node classification.")]`
           * `confidence: Annotated[float, Field(description="Confidence score in [0.0, 1.0].")]` (validated via `@field_validator("confidence")` enforcing `0.0 <= v <= 1.0`)
           * `payload: Annotated[PropositionPayloadDTO, Field(description="Validated proposition payload.")]`
           * `created_at: Annotated[datetime, Field(description="Timestamp extracted from PostgreSQL 18 VIRTUAL column.")]`
         - `DependencyEdge(V2CoreBase)`:
           * `edge_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Persisted edg_<uuid7_hex> identifier.")]`
           * `run_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Parent exe_<uuid7_hex> identifier.")]`
           * `source_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Source nod_<uuid7_hex> identifier.")]`
           * `target_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Target nod_<uuid7_hex> identifier.")]`
           * `relation_type: Annotated[DependencyRelationType, Field(description="Relation classification.")]`
           * `causal_weight: Annotated[float, Field(default=1.0, description="Edge weight in [-1.0, 1.0].")]` (validated via `@field_validator("causal_weight")` enforcing `-1.0 <= v <= 1.0` and `@model_validator(mode="after")` rejecting `source_id == target_id`)
           * `created_at: Annotated[datetime, Field(description="Timestamp extracted from PostgreSQL 18 VIRTUAL column.")]`
         - `FalsifiedClaimMatch(V2CoreBase)`:
           * `rebuttal_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Rebuttal nod_<uuid7_hex>.")]`
           * `invalidated_warrant_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Invalidated warrant nod_<uuid7_hex>.")]`
           * `falsified_claim_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Falsified claim nod_<uuid7_hex>.")]`
           * `rebuttal_confidence: Annotated[float, Field(description="Confidence of the rebuttal node.")]` (validated via `@field_validator("rebuttal_confidence")` enforcing `0.0 <= v <= 1.0`)
           * `claim_statement: Annotated[str, Field(min_length=1, description="Statement text of the falsified claim.")]`
         - `ReportBinaryPayloadDTO(V2CoreBase)`:
           * `report_id: Annotated[str, Field(pattern=OPAQUE_STRIPE_ID_REGEX, description="Parent rep_<uuid7_hex> identifier.")]`
           * `mime_type: Annotated[str, Field(default="application/pdf", min_length=1, description="MIME type of binary payload.")]`
           * `pdf_bytes: Annotated[bytes, Field(description="Raw binary PDF bytes stored in TOAST table.")]`
           * `size_bytes: Annotated[int, Field(ge=0, description="Exact byte length.")]`
           * `created_at: Annotated[datetime, Field(description="Creation timestamp.")]`
         - `CycleDetectedError(AppException)`: Typed domain subclass of `AppException` encapsulating `run_id: str` and `cycle_path: tuple[str, ...]` with `details={"error_code": ErrorCodes.VALIDATION_FAILED.value, "run_id": run_id, "cycle_path": list(cycle_path)}`.
      2. Create `[NEW] @[backend_v2/tests/unit/models/domain/test_proposition_graph.py]` covering positive instantiation and >=2 ISTQB negative boundary tests per model (`confidence` `< 0.0` / `> 1.0`, `causal_weight` `< -1.0` / `> 1.0`, self-loop `source_key == target_key` and `source_id == target_id`, `extra="forbid"`, and `CycleDetectedError`).
      3. In `@[backend_v2/database/interfaces.py#L314-L335]`, define `@runtime_checkable` protocols (`GraphMutationPort`, `TopologyResolutionPort`, `CausalReasoningPort`, `EntityPersistencePort`, `QuorumUnitOfWork`), export them in `__all__`, and update `@[backend_v2/tests/unit/test_interfaces.py#L7-L21]` to assert `Protocol` membership for all 5 new ports.
      4. Run `uv run python scripts/backend_audit_loop.py backend_v2/models/domain/proposition_graph.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py backend_v2/database/interfaces.py --test --ast-strict`.
    </action>
  </step>

  <step id="3" name="POSTGRESQL_18_UUIDV7_SCHEMA_AND_POOL_INFRASTRUCTURE">
    <objective>Create the pure SQL DDL schema for PostgreSQL 18 (with PG 17 compatibility block) and implement the asyncpg connection pool manager with binary pydantic_core JSONB codecs.</objective>
    <constraint invariant="unbounded_io_timeout_mandate">All asyncpg pool and connection operations MUST specify explicit timeouts resolved strictly from settings.py and translate transport errors into AppException.</constraint>
    <constraint invariant="credential_hardcoding_ban">Never hardcode database passwords or credential-bearing DSNs in settings.py; resolve credentials exclusively via environment injection.</constraint>
    <targets>
      <target action="MODIFY">@[backend_v2/settings.py#L47-L51]</target>
      <target action="MODIFY">@[backend_v2/settings.py#L54-L1063]</target>
      <target action="MODIFY">@[backend_v2/tests/unit/test_settings.py#L136-L158]</target>
      <target action="NEW">[NEW] @[backend_v2/database/migrations/001_pg18_uuidv7_schema.sql]</target>
      <target action="NEW">[NEW] @[backend_v2/database/postgres/__init__.py]</target>
      <target action="NEW">[NEW] @[backend_v2/database/postgres/pool.py]</target>
    </targets>
    <action>
      1. In `@[backend_v2/settings.py#L47-L51]`, replace the local `StorageBackend` class definition with an explicit re-export `from backend_v2.models.enums import StorageBackend as StorageBackend`. In `Settings` (`@[backend_v2/settings.py#L54-L1063]`), add PEP 593 `Annotated` fields without hardcoded credentials:
         - `postgres_host: Annotated[str, Field(description="PostgreSQL server host address.")] = "127.0.0.1"`
         - `postgres_port: Annotated[int, Field(ge=1, le=65535, description="PostgreSQL server port.")] = 5432`
         - `postgres_user: Annotated[str, Field(min_length=1, description="PostgreSQL role username.")] = "quorum"`
         - `postgres_password: Annotated[str | None, Field(description="PostgreSQL role password injected from environment.")] = None`
         - `postgres_db: Annotated[str, Field(min_length=1, description="PostgreSQL database name.")] = "quorum"`
         - `postgres_dsn: Annotated[str | None, Field(description="Optional environment-injected PostgreSQL DSN override.")] = None`
         - `postgres_min_pool_size: Annotated[int, Field(ge=1, le=50, description="Minimum asyncpg pool connections.")] = 2`
         - `postgres_max_pool_size: Annotated[int, Field(ge=2, le=200, description="Maximum asyncpg pool connections.")] = 20`
         - `postgres_command_timeout_seconds: Annotated[float, Field(description="Command timeout in seconds for PostgreSQL queries.")] = 15.0` (validated in `@model_validator(mode="after")` enforcing `1.0 <= self.postgres_command_timeout_seconds <= 120.0` and `self.postgres_min_pool_size <= self.postgres_max_pool_size`)
         - `postgres_enable_pgq_graph_table: Annotated[bool, Field(description="Enable ISO SQL/PGQ GRAPH_TABLE strategy instead of recursive CTEs.")] = False`
         Update `active_backend` (`@[backend_v2/settings.py#L769-L798]`) to map `"POSTGRES"` and `"POSTGRESQL"` to the `POSTGRES` member of `StorageBackend`, and update `@[backend_v2/tests/unit/test_settings.py#L136-L158]` to test `POSTGRES` resolution and pool/timeout boundary validation.
      2. Create `[NEW] @[backend_v2/database/migrations/001_pg18_uuidv7_schema.sql]` defining the closed 12-table topology:
         - `quorum_nodes` and `quorum_edges` with `UUID PRIMARY KEY DEFAULT uuidv7()`, `CONSTRAINT enforce_node_uuidv7 CHECK (uuid_extract_version(node_id) = 7)`, `CONSTRAINT enforce_run_uuidv7 CHECK (uuid_extract_version(run_id) = 7)`, `CONSTRAINT no_self_loops CHECK (source_id <> target_id)`, and a `DO $$` server_version_num check adding `created_at TIMESTAMPTZ GENERATED ALWAYS AS (uuid_extract_timestamp(...)) VIRTUAL` on PG >= 180000 and `STORED` on PG 17.
         - The 10 system tables (`users`, `organizations`, `workflows`, `steps`, `prompt_blocks`, `output_profiles`, `system_configs`, `executions` with Flat FinOps `BIGINT` and `NUMERIC(10,6)` columns, `report_artifacts` with `ON DELETE CASCADE`, and `report_binaries` with `BYTEA` TOAST storage and `ON DELETE CASCADE`).
      3. Create `[NEW] @[backend_v2/database/postgres/pool.py]` implementing:
         - `@runtime_checkable` protocols `AsyncPgRecordProtocol` (a standalone `Protocol` defining `def __getitem__(self, key: str) -> object: ...` without inheriting `Mapping` so `Sequence[AsyncPgRecordProtocol]` passes `_find_nested_dict_subscript`), `AsyncPgTransactionProtocol`, `AsyncPgConnectionProtocol`, and `AsyncPgPoolProtocol`.
         - `encode_jsonb_binary(value: object) -> bytes` (`b"\x01" + to_json(value)` using `pydantic_core.to_json`) and `decode_jsonb_binary(raw: bytes | bytearray | memoryview) -> object` (verifying `len(raw) >= 1 and raw[0] == 1` fail-fast with `AppException(message=..., status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, details={"error_code": ErrorCodes.STORAGE_ACCESS_FAILED.value})` and calling `from_json(memoryview(raw)[1:])`).
         - `PostgresPoolManager` accepting `settings: Settings` and an optional injected `pool: AsyncPgPoolProtocol | None = None`, lazily importing `asyncpg` inside `connect()` when no pool is injected, registering `init_connection(conn)` binary `jsonb` codec, enforcing `postgres_command_timeout_seconds` in `acquire_connection()`, and executing `001_pg18_uuidv7_schema.sql` in `apply_migrations()`.
      4. Create `[NEW] @[backend_v2/database/postgres/__init__.py]` with explicit `__all__` re-exports.
      5. Run `uv run python scripts/backend_audit_loop.py backend_v2/settings.py --test --ast-strict` and `uv run python scripts/audit_zero_orm_strictness.py`.
    </action>
  </step>

  <step id="4" name="ZERO_ORM_GRAPH_ENTITY_ADAPTERS_AND_WAVE_UOW">
    <objective>Implement PostgresGraphAdapter (Single-Round Multi-CTE materialize_wave, CTE cycle detection, CteReasoningStrategy, PgqReasoningStrategy), PostgresEntityAdapter, PostgresUnitOfWork, and InMemoryUnitOfWork.</objective>
    <constraint invariant="no_naked_dicts_in_state">Never use {**dict(r), ...}, row.get(...), list[dict[...]], 3+ element tuple annotations (QGR023), or untyped dictionaries when hydrating rows. Access record columns via direct subscript indexing (row['col']) and validate through strict Pydantic V2 row DTOs (ConfigDict(strict=True, extra='forbid', frozen=True)) with model_validate(..., strict=False) at the repository boundary.</constraint>
    <constraint invariant="async_io_lock_isolation_mandate">Never hold a database transaction open across LLM generation calls; PostgresUnitOfWork commits wave batches atomically in repeatable_read isolation.</constraint>
    <targets>
      <target action="NEW">[NEW] @[backend_v2/database/postgres/graph_adapter.py]</target>
      <target action="NEW">[NEW] @[backend_v2/database/postgres/entity_adapter.py]</target>
      <target action="NEW">[NEW] @[backend_v2/database/postgres/uow.py]</target>
      <target action="NEW">[NEW] @[backend_v2/tests/fakes/in_memory_uow.py]</target>
      <target action="MODIFY">@[backend_v2/database/factory.py#L24-L64]</target>
      <target action="MODIFY">@[backend_v2/tests/unit/test_factory.py#L28-L32]</target>
    </targets>
    <action>
      1. Create `[NEW] @[backend_v2/database/postgres/graph_adapter.py]` implementing `PostgresGraphAdapter`, `CteReasoningStrategy`, and `PgqReasoningStrategy` (using strictly `row["col"]` subscript indexing with zero `.get()` calls to satisfy `QGR002` and zero `list[dict[...]]` or 3+ element tuple annotations to satisfy `QGR023` and `audit_dict_eradication.py`):
         - `materialize_wave(self, run_id: str, node_drafts: Sequence[NodeDraft], edge_drafts: Sequence[EdgeDraft]) -> Sequence[PropositionNode]`:
           * Parse `run_uuid = parse_prefixed_uuid7(run_id, EntityPrefix.EXECUTION)`.
           * Validate referential integrity pre-flight: every `edge.source_key` and `edge.target_key` in `edge_drafts` MUST exist in `{n.local_key for n in node_drafts}` and `local_key` values MUST be unique across `node_drafts`; if violated, log and raise `AppException(message=..., status_code=status.HTTP_400_BAD_REQUEST, details={"error_code": ErrorCodes.VALIDATION_FAILED.value})`.
           * Serialize `node_drafts` and `edge_drafts` via `pydantic_core.to_json(list(node_drafts)).decode("utf-8")` and `pydantic_core.to_json(list(edge_drafts)).decode("utf-8")` (zero `list[dict[...]]` intermediates) and execute the single-round Multi-CTE query (`WITH input_nodes AS (SELECT uuidv7() AS generated_node_id, ... FROM jsonb_to_recordset($2::jsonb)), inserted_nodes AS (INSERT INTO quorum_nodes ... RETURNING node_id, run_id, node_type, confidence, payload, created_at), input_edges AS (...), inserted_edges AS (INSERT INTO quorum_edges ...) SELECT ... FROM inserted_nodes ORDER BY node_id ASC`).
           * Hydrate each returned record into `PropositionNode` using `format_prefixed_uuid7` and `PropositionPayloadDTO.model_validate(..., strict=False)`.
         - `upsert_wave_batch(self, nodes: Sequence[PropositionNode], edges: Sequence[DependencyEdge]) -> None` using `executemany` with `Sequence[Sequence[object]]` parameter rows.
         - `assert_acyclic(self, run_id: str) -> None` using `WITH RECURSIVE dag_walk AS (...) CYCLE target_id SET is_cycle USING traversal_path SELECT traversal_path FROM dag_walk WHERE is_cycle = TRUE LIMIT 1`, raising `CycleDetectedError` (`ErrorCodes.VALIDATION_FAILED`) if a cycle row is returned.
         - `fetch_next_kahn_wave(self, run_id: str) -> Sequence[PropositionNode]` returning nodes with `in_degree = 0`.
         - `find_falsified_claims(self, run_id: str, min_confidence: float) -> Sequence[FalsifiedClaimMatch]` dispatching to `PgqReasoningStrategy` (`FROM GRAPH_TABLE (quorum_reasoning_graph MATCH ...)` when `enable_pgq_graph_table` is `True`) or default `CteReasoningStrategy` (3-way ANSI SQL join across `quorum_nodes r -> quorum_edges e1 ('rebuts') -> quorum_nodes w -> quorum_edges e2 ('warrants') -> quorum_nodes c`).
      2. Create `[NEW] @[backend_v2/database/postgres/entity_adapter.py]` implementing `PostgresEntityAdapter`:
         - `save_report_binary` and `get_report_binary` against `report_binaries` (`BYTEA`) and updating `report_artifacts.has_pdf = TRUE`.
         - Clean-slate persistence for executions without legacy shims or historical TinyDB ETL adapters.
      3. Create `[NEW] @[backend_v2/database/postgres/uow.py]` implementing `PostgresUnitOfWork`:
         - Acquires connection from `PostgresPoolManager`, opens `conn.transaction(isolation="repeatable_read")`, attaches `PostgresGraphAdapter` and `PostgresEntityAdapter`, commits on clean exit, rolls back on exception, and always releases the connection in `finally` (obeying PEP 765 pure cleanup without control flow jumps).
      4. Create `[NEW] @[backend_v2/tests/fakes/in_memory_uow.py]` implementing `InMemoryUnitOfWork`, `InMemoryGraphAdapter`, `InMemoryEntityAdapter`, and stateful `InMemoryAsyncPgPool` / `InMemoryAsyncPgConnection` (conforming to `AsyncPgPoolProtocol` and `AsyncPgConnectionProtocol` with real in-memory Multi-CTE wave materialization, cycle walk, Toulmin query execution, and transaction snapshot rollback, using positive `if key in store:` checks with zero `.get()` calls) inside `tests/fakes/` per `QGR014`.
      5. Update `@[backend_v2/database/factory.py#L24-L64]` to execute Phase 1 cleanup (fixing `Raises:` docstring and adding RFC 7807 `logger.error`), support the `POSTGRES` member of `StorageBackend`, expose `create_unit_of_work(settings: Settings, pool_manager: PostgresPoolManager | None = None) -> QuorumUnitOfWork`, and update `@[backend_v2/tests/unit/test_factory.py#L28-L32]` to verify `get_driver` and `create_unit_of_work` across `LOCAL`, `FIRESTORE`, and `POSTGRES`.
      6. Run `uv run python scripts/audit_zero_orm_strictness.py`, `uv run python scripts/backend_audit_loop.py backend_v2/database/factory.py --test --ast-strict`, and `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/ backend_v2/tests/fakes/in_memory_uow.py --ast-strict`.
    </action>
  </step>

  <step id="5" name="CONTRACT_TEST_SUITE_AND_ISTQB_NEGATIVE_VERIFICATION">
    <objective>Build the comprehensive contract test suite verifying InMemoryUnitOfWork, PostgresUnitOfWork (backed by InMemoryAsyncPgPool from tests/fakes/in_memory_uow.py), PrefixedUUID7, Multi-CTE wave ingestion, and ISTQB negative boundary partitions.</objective>
    <constraint invariant="anti_happy_path_mandate">Write at least 2 negative test cases for every positive test case covering missing/invalid inputs triggering AppException and boundary values (confidence &lt; 0.0, confidence &gt; 1.0, self-loop edges, cyclic graphs, non-v7 UUIDs, invalid binary JSONB header, transaction rollback on failure).</constraint>
    <constraint invariant="deceptive_persistence_mocking_ban">Verify stateful roundtrip behavior using InMemoryUnitOfWork and InMemoryAsyncPgPool from backend_v2/tests/fakes/in_memory_uow.py with zero AsyncMock usage.</constraint>
    <targets>
      <target action="NEW">[NEW] @[backend_v2/tests/unit/database/test_postgres.py]</target>
    </targets>
    <action>
      1. Create `[NEW] @[backend_v2/tests/unit/database/test_postgres.py]` parameterized across both `InMemoryUnitOfWork` and `PostgresUnitOfWork` (wired to `PostgresPoolManager` + `InMemoryAsyncPgPool`), covering:
         - **Positive Case 1 (Single-Round Wave Materialization & Roundtrip)**: Materializing 3 `NodeDraft` items (`ground_1`, `warrant_1`, `claim_1`) and 2 `EdgeDraft` items (`supports`, `warrants`) generates canonical `nod_<uuid7_hex>` IDs in monotonically increasing order, populates `created_at`, and persists all nodes and edges in 1 atomic operation.
         - **Positive Case 2 (Toulmin Falsification Query Parity)**: Inserting a `rebuttal` (`confidence=0.92`) -> `rebuts` -> `warrant` -> `warrants` -> `claim` chain and calling `find_falsified_claims(run_id, min_confidence=0.80)` returns the exact `FalsifiedClaimMatch` DTO in both `InMemoryUnitOfWork` and `PostgresUnitOfWork` (verifying both `CteReasoningStrategy` and `PgqReasoningStrategy` SQL execution and row hydration).
         - **Positive Case 3 (Report Binary TOAST Roundtrip & Binary JSONB Codec)**: Saving a `ReportBinaryPayloadDTO` and retrieving it returns identical `pdf_bytes` and `size_bytes`; `encode_jsonb_binary` and `decode_jsonb_binary` roundtrip `\x01`-prefixed JSONB bytes.
         - **Negative Case 1 (DAG Cycle Detection Fail-Fast)**: Introducing a 3-node cycle (`A -> B -> C -> A`) and calling `assert_acyclic(run_id)` raises `CycleDetectedError` (`ErrorCodes.VALIDATION_FAILED`).
         - **Negative Case 2 (Transactional Rollback on Dangling Edge Reference & Mid-Wave Fault)**: Calling `materialize_wave` with an `EdgeDraft` referencing an unknown `target_key="nonexistent_node"` or raising an exception inside `async with uow:` rolls back the entire UoW transaction, leaving 0 orphan nodes persisted.
         - **Negative Case 3 (ISTQB Boundary Value Analysis on Draft Models, Binary JSONB Header & PrefixedUUID7)**:
           * `NodeDraft` with `confidence = -0.001` (min - 0.001) and `confidence = 1.001` (max + 0.001) raises `ValidationError`.
           * `EdgeDraft` with `causal_weight = -1.001` and `1.001` or self-loop (`source_key == target_key`) raises `ValidationError`.
           * `parse_prefixed_uuid7` with wrong prefix (`wf_...` when `nod` expected) or UUIDv4 string raises `AppException` with `ErrorCodes.VALIDATION_FAILED`.
           * `decode_jsonb_binary(b"\x02{}")` or `decode_jsonb_binary(b"")` raises `AppException` with `ErrorCodes.STORAGE_ACCESS_FAILED`.
         - **Negative Case 4 (AST Guardrail & Codebase Verification)**: Verify that `audit_zero_orm_strictness.py` passes with exit code 0 on the real `backend_v2/database/postgres/` package and detects synthetic `import sqlalchemy`, `import orjson`, `"dict" + "[str, Any]"` (concatenated so `audit_warning_baseline.py` Census `P` remains `0`), broad `except Exception: pass`, `llm_client` calls, and unknown table names with exit code 1.
      2. Execute localized test gate: `uv run pytest backend_v2/tests/unit/database/test_postgres.py`.
      3. Execute global completion gates:
         - `uv run python scripts/audit_zero_orm_strictness.py`
         - `uv run python scripts/audit_dict_eradication.py backend_v2/database/postgres/ backend_v2/models/domain/proposition_graph.py`
         - `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/ --test --ast-strict`
         - `uv run python scripts/backend_audit_loop.py backend_v2/database/ --test --ast-strict`
         - `uv run python scripts/backend_audit_loop.py backend_v2/models/ --test --ast-strict`
    </action>
  </step>
</execution_protocol>
```

---

## 5. Verification & Quality Gates

1. **Static AST & Dict Eradication Gates**:
   ```powershell
   uv run python scripts/audit_zero_orm_strictness.py
   uv run python scripts/audit_dict_eradication.py backend_v2/database/postgres/ backend_v2/models/domain/proposition_graph.py
   ```
2. **Localized & Module Quality Gates**:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/models/core_base.py --test --ast-strict
   uv run python scripts/backend_audit_loop.py backend_v2/models/domain/proposition_graph.py --test --ast-strict
   uv run python scripts/backend_audit_loop.py backend_v2/database/ --test --ast-strict
   uv run python scripts/backend_audit_loop.py backend_v2/settings.py --test --ast-strict
   ```
3. **Global Completion Gate**:
   ```powershell
   uv run python scripts/backend_audit_loop.py backend_v2/ --test
   uv run python scripts/flutter_audit_loop.py client_app_v2/ --build
   ```
4. **Final Live E2E REST API Verification Gate**:
   ```powershell
   $env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py
   ```
