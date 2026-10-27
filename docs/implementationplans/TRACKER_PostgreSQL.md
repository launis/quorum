# Tracker: All-in-PostgreSQL 19 Sovereign Zero-ORM Architecture, CQRS Ports & Kahn Wave Unit of Work

@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]

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

**Plan:** @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]

- [ ] **[NOK] Execution:** `/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md] @[docs/implementationplans/TRACKER_PostgreSQL.md]`
  - [x] Step 1: PHASE_1_CLEANUPS_AST_GUARDRAIL_AND_ENUM_FOUNDATION
  - [x] Step 2: PROPOSITION_GRAPH_DOMAIN_MODELS_AND_HEXAGONAL_CQRS_PORTS
  - [ ] Step 3: POSTGRESQL_19_UUIDV7_SCHEMA_AND_POOL_INFRASTRUCTURE
  - [ ] Step 4: ZERO_ORM_GRAPH_ENTITY_ADAPTERS_AND_WAVE_UOW
  - [ ] Step 5: CONTRACT_TEST_SUITE_AND_ISTQB_NEGATIVE_VERIFICATION
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md] @[docs/implementationplans/TRACKER_PostgreSQL.md]`

### Post-Implementation Gates

- [ ] **[NOK] Golden Master & Test Restoration Audit**: Ensure no `@pytest.mark.skip` or commented-out tests remain in modified domains.
- [ ] **[NOK] Tier 2 Hardening (Backend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_PostgreSQL.md]" --gate backend --model gemini-4-argon-medium`.
  - [ ] @[backend_v2/database/factory.py]
  - [ ] @[backend_v2/database/interfaces.py]
  - [ ] [NEW] @[backend_v2/database/postgres/__init__.py]
  - [ ] [NEW] @[backend_v2/database/postgres/entity_adapter.py]
  - [ ] [NEW] @[backend_v2/database/postgres/graph_adapter.py]
  - [ ] [NEW] @[backend_v2/database/postgres/pool.py]
  - [ ] [NEW] @[backend_v2/database/postgres/uow.py]
  - [ ] @[backend_v2/models/core_base.py]
  - [ ] [NEW] @[backend_v2/models/domain/proposition_graph.py]
  - [ ] @[backend_v2/models/enums.py]
  - [ ] @[backend_v2/settings.py]
  - [ ] [NEW] @[scripts/audit_zero_orm_strictness.py]
- [ ] **[SKIPPED] Tier 2 Hardening (Frontend)**: Run `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_PostgreSQL.md]" --gate frontend --model gemini-4-argon-medium`. (Zero frontend `.dart` production targets in this plan).
- [ ] **[NOK] Pre-Delete Audit**: Verify no orphaned symbols or dependencies remain.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Mathematically verify line coverage >90% for modified business logic.

### Documentation & Knowledge Item Update

- [ ] **[NOK]** As-Built Architectural Sync: Run:
  ```powershell
  /tier7-describe-architecture @[docs/implementationplans/TRACKER_PostgreSQL.md] @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md] @[ki_god_code_prevention.md] @[ki_python_314_concurrency_strictness.md] @[ki_zero_permissive_typing.md] @[ki_mcp_tool_protocol.md]
  ```

  #### Directives for Tier 7 Agent:
  1. **Target KIs to Synchronize:**
     - `@[ki_god_code_prevention.md]`: Document the Hexagonal CQRS Port segregation (`GraphMutationPort`, `TopologyResolutionPort`, `CausalReasoningPort`, `EntityPersistencePort`, `QuorumUnitOfWork`), the `PostgresPoolManager` / `PostgresGraphAdapter` / `PostgresEntityAdapter` / `PostgresUnitOfWork` boundary isolation, and the `audit_zero_orm_strictness.py` AST guardrail rules (`ZORM001`–`ZORM006`).
     - `@[ki_python_314_concurrency_strictness.md]`: Document the Post-Wave Atomic Commit Invariant (executing LLM inference 100% in memory inside `asyncio.TaskGroup` and committing wave batches atomically via `PostgresUnitOfWork` in `repeatable_read` isolation with PEP 765 pure `finally` connection cleanup) and thread-safe RFC 9562 monotonic sub-millisecond `rand_a` counter state in `generate_uuid7_opaque_id`.
     - `@[ki_zero_permissive_typing.md]`: Document the Zero-ORM binary `pydantic_core` (`to_json` / `from_json`) `\x01`-prefixed JSONB codec on `asyncpg`, standalone `AsyncPgRecordProtocol` (`__getitem__` without `Mapping` inheritance), direct subscript row projection into immutable `ConfigDict(strict=True, extra="forbid", frozen=True)` Pydantic V2 models (`PropositionNode`, `DependencyEdge`, `NodeDraft`, `EdgeDraft`, `FalsifiedClaimMatch`, `ReportBinaryPayloadDTO`), and the 1:1 Schema vs. Domain DTO Column Naming Parity gate (`test_schema_dto_naming_parity` and `ZORM006`).
     - `@[ki_mcp_tool_protocol.md]`: Document lossless PostgreSQL 19 `lz4`-compressed JSONB persistence of dynamic MCP gateway configurations (`SystemConfigMCPGateways` with `AllowedMCPTool`, `MCPServerInfoDTO`, `MCPToolExecutionDTO`), step-level `Step.mcp_tool_params`, and `MCPAuditTrace` telemetry inside `executions.trace_events`.
  2. **Directory Reference Sync:**
     - Update `@[.agents/rules/04_directory_reference.md]` to register newly created modules and scripts from this plan, specifically and exhaustively: `backend_v2/models/domain/proposition_graph.py`, `backend_v2/database/migrations/001_pg19_uuidv7_schema.sql`, `backend_v2/database/postgres/__init__.py`, `backend_v2/database/postgres/pool.py`, `backend_v2/database/postgres/graph_adapter.py`, `backend_v2/database/postgres/entity_adapter.py`, `backend_v2/database/postgres/uow.py`, `backend_v2/tests/fakes/in_memory_uow.py`, `scripts/audit_zero_orm_strictness.py`, `backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py`, `backend_v2/tests/unit/models/domain/test_proposition_graph.py`, and `backend_v2/tests/unit/database/test_postgres.py`.
  3. **Pillar Documentation Sync:**
     - Update timeless narratives in `docs/architecture/` (specifically and exhaustively: `01_system_context_and_invariants.md`, `02_data_seeding_and_ontology.md`, `03_cognitive_orchestration_engine.md`, and `05_resilience_and_observability.md`) describing the All-in-PostgreSQL 19 Zero-ORM persistence topology, RFC 9562 `uuidv7()` + `PrefixedUUID7` bridge, Single-Round Multi-CTE wave ingestion with `ON CONFLICT DO SELECT`, `lz4` TOAST compression, and Post-Wave `QuorumUnitOfWork` invariants in present tense without historical language or plan IDs.

### Final Plan Audit

- [ ] **[NOK]** System 2 Red-Team Audit: Run `/tier8-audit-plan @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md] @[docs/implementationplans/TRACKER_PostgreSQL.md]` to verify all requirements and Quorum 2026 invariants were physically implemented across the codebase with 0 fatal errors.

## Instructions for the Execution Agent

1. **Execution Mode**:
   - **Step-by-Step Mode** (`/tier2-execute @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md] @[docs/implementationplans/TRACKER_PostgreSQL.md]`): Execute a single unchecked step, run all step-level quality gates, update this tracker (`[x]`) and the `# Session Handover Context`, instruct the user to perform an atomic `git commit`, and STOP.
   - **Continuous Full-Auto Mode** (`/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md] @[docs/implementationplans/TRACKER_PostgreSQL.md]`): Proceed autonomously across all steps in sequence as long as quality gates pass 100%, halting immediately if any quality gate fails or when `context_amnesia_prevention` handover thresholds are reached.
2. **Quality Gate Mandate**:
   - After modifying any `.py` file, run `uv run python scripts/backend_audit_loop.py <target_path> --test --ast-strict` and `uv run python scripts/audit_zero_orm_strictness.py`.
   - Before closing the final step, run the global completion gates: `uv run python scripts/backend_audit_loop.py backend_v2/ --test` and `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.
3. **Atomic Commit Mandate**:
   - Provide an atomic `git commit` instruction using strict Conventional Commits syntax (`<type>(<scope>): <imperative summary in lowercase, max 72 chars, no trailing period>`) with explicit `git add` file paths and a concise, factual bulleted list of physical changes.
4. **Workspace Path Normalization**:
   - Exclusively use workspace-relative `@[...]` paths across all documentation, trackers, and handover blocks.
5. **Post-Implementation Hardening Execution Options**:
   - Run interactive file-by-file hardening in chat via `/tier2-hardening-backend @[docs/implementationplans/TRACKER_PostgreSQL.md]`, OR
   - Run autonomous unattended CLI hardening via `uv run python scripts/auto_hardening_runner.py --tracker "@[docs/implementationplans/TRACKER_PostgreSQL.md]" --gate backend --model gemini-4-argon-medium`.

## Requirements Traceability Matrix

| Requirement | Description | Plan Step | Status |
| :--- | :--- | :--- | :--- |
| **REQ-001** | Implement `[NEW] @[scripts/audit_zero_orm_strictness.py]` enforcing AST rules `ZORM001`–`ZORM006` (banning SQLAlchemy/Alembic/orjson imports, naked dict subscripts/unpacking, untyped `except Exception:`, unapproved SQL tables outside the closed 12-table topology, LLM calls inside database/UoW modules, and SQL-to-DTO column drift) with zero contiguous naked dict literal tokens. | Step 1 | `[x]` |
| **REQ-002** | Create `[NEW] @[backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py]` covering positive and >=2 ISTQB negative partitions for `ZORM001`–`ZORM006`, and register `audit_zero_orm_strictness.py` in `@[backend_v2/tests/unit/scripts/test_scripts_cli_help.py#L61-L67]` (`36` -> `37`). | Step 1 | `[x]` |
| **REQ-003** | Execute Phase 1 Tripartite Configuration cleanup in `@[backend_v2/models/enums.py#L222-L235]` by migrating `StorageBackend(StrEnum)` (`FIRESTORE`, `LOCAL`, `POSTGRES`), extending `EntityPrefix` (`NODE = "nod"`, `EDGE = "edg"`), and adding `PropositionNodeType` and `DependencyRelationType` with unit tests in `@[backend_v2/tests/unit/models/test_enums.py#L253-L266]`. | Step 1 | `[x]` |
| **REQ-004** | Implement RFC 9562 UUIDv7 Opaque Stripe ID bridge functions (`parse_prefixed_uuid7`, `format_prefixed_uuid7`, and monotonic `generate_uuid7_opaque_id` with thread-safe 12-bit `rand_a` counter) in `@[backend_v2/models/core_base.py#L165-L190]` and verify >90% coverage in `@[backend_v2/tests/unit/models/test_core_base.py#L125-L140]`. | Step 1 | `[x]` |
| **REQ-005** | Create `[NEW] @[backend_v2/models/domain/proposition_graph.py]` defining immutable Pydantic V2 models (`PropositionPayloadDTO`, `NodeDraft`, `EdgeDraft`, `PropositionNode`, `DependencyEdge`, `FalsifiedClaimMatch`, `ReportBinaryPayloadDTO`) with explicit class-level `ConfigDict(strict=True, extra="forbid", frozen=True)`, float `@field_validator` bounds, self-loop `@model_validator` checks, and `CycleDetectedError(AppException)`, verified in `[NEW] @[backend_v2/tests/unit/models/domain/test_proposition_graph.py]`. | Step 2 | `[x]` |
| **REQ-006** | Define `@runtime_checkable` Hexagonal CQRS Ports (`GraphMutationPort`, `TopologyResolutionPort`, `CausalReasoningPort`, `EntityPersistencePort`, `QuorumUnitOfWork`) in `@[backend_v2/database/interfaces.py#L315-L336]` and verify protocol contracts in `@[backend_v2/tests/unit/test_interfaces.py#L7-L21]`. | Step 2 | `[x]` |
| **REQ-007** | Re-export `StorageBackend` in `@[backend_v2/settings.py#L47-L51]` and declare environment-injected PostgreSQL connection, pool, timeout (`postgres_command_timeout_seconds`), and `lz4` TOAST settings in `@[backend_v2/settings.py#L54-L1053]` with zero hardcoded credentials, verified in `@[backend_v2/tests/unit/test_settings.py#L136-L158]`. | Step 3 | `[ ]` |
| **REQ-008** | Create pure SQL DDL migration `[NEW] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]` for the closed 12-table topology with `SET default_toast_compression = 'lz4'`, PostgreSQL 19 `uuidv7()`, `uuid_extract_version() = 7` checks, `uuid_extract_timestamp() VIRTUAL` columns, `CREATE STATISTICS` on virtual columns, Flat FinOps columns, and lossless MCP JSONB schemas, and wire `postgres:19-rc1` in `@[docker-compose.yml]`. | Step 3 | `[ ]` |
| **REQ-009** | Implement `[NEW] @[backend_v2/database/postgres/pool.py]` and `[NEW] @[backend_v2/database/postgres/__init__.py]` with standalone `AsyncPgRecordProtocol` (`__getitem__`), `AsyncPgPoolProtocol`, binary `pydantic_core` `\x01`-prefixed JSONB codecs (`encode_jsonb_binary`, `decode_jsonb_binary`), lazy `asyncpg` connection initialization, explicit command timeouts, and idempotent migration runner. | Step 3 | `[ ]` |
| **REQ-010** | Implement `[NEW] @[backend_v2/database/postgres/graph_adapter.py]` (`PostgresGraphAdapter` and `CteReasoningStrategy`) featuring Single-Round Multi-CTE `materialize_wave` with PostgreSQL 19 `ON CONFLICT (run_id, local_key) DO SELECT RETURNING`, `upsert_wave_batch`, `assert_acyclic` (`WITH RECURSIVE ... CYCLE`), `fetch_next_kahn_wave`, and `find_falsified_claims`. | Step 4 | `[ ]` |
| **REQ-011** | Implement `[NEW] @[backend_v2/database/postgres/entity_adapter.py]` (`PostgresEntityAdapter`), `[NEW] @[backend_v2/database/postgres/uow.py]` (`PostgresUnitOfWork` with `repeatable_read` isolation and PEP 765 pure `finally` cleanup), `[NEW] @[backend_v2/tests/fakes/in_memory_uow.py]` (`InMemoryUnitOfWork` and `InMemoryAsyncPgPool`), and wire `POSTGRES` in `@[backend_v2/database/factory.py#L24-L64]` with unit tests in `@[backend_v2/tests/unit/test_factory.py#L28-L32]`. | Step 4 | `[ ]` |
| **REQ-012** | Build `[NEW] @[backend_v2/tests/unit/database/test_postgres.py]` parameterized across `InMemoryUnitOfWork` and `PostgresUnitOfWork`, verifying Single-Round Multi-CTE wave materialization, Toulmin falsification query parity, `ReportBinaryPayloadDTO` TOAST roundtrip, 1:1 DDL Schema vs. Domain DTO Column Naming Parity across all 12 tables (including MCP JSONB structures), and >=2 ISTQB negative boundary cases per feature. | Step 5 | `[ ]` |

# Session Handover Context

## Achieved
- Generated the standalone execution tracker `@[docs/implementationplans/TRACKER_PostgreSQL.md]` for `@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]`.
- Synchronized `<required_context_rules>`, 1:1 step checkboxes (`Step 1` through `Step 5`), the 12 production backend Python files under `Tier 2 Hardening (Backend)`, the parameterized `/tier7-describe-architecture` command with structured directives, and the 12-row `Requirements Traceability Matrix` (`REQ-001` through `REQ-012`).
- Executed Tier 0 System 2 Research & Red-Team Analysis (`/tier0-research-plan`) on `@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]` and `@[docs/implementationplans/TRACKER_PostgreSQL.md]`, verifying `CONVERGENCE ACHIEVED: 0 architectural defects found` across `audit_markdown_boundaries.py`, `audit_technical_debt.py`, `audit_plan_tracker_parity.py`, and `audit_tracker_output.py` with zero mutations required on the converged plan.

## Learned
- `@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]` passes `audit_markdown_boundaries.py` (`MBD001`–`MBD009`) with 0 findings and already embeds the complete Pre-Implementation Technical Debt audit, System 2 Red-Team Falsification Matrix (`RT-01` through `RT-12`), and Five-Axis Architectural Directive Matrix with 100% bidirectional Table-to-Protocol parity (`MBD008`).
- All 12 production Python target files (`factory.py`, `interfaces.py`, `postgres/__init__.py`, `postgres/entity_adapter.py`, `postgres/graph_adapter.py`, `postgres/pool.py`, `postgres/uow.py`, `models/core_base.py`, `models/domain/proposition_graph.py`, `models/enums.py`, `settings.py`, and `scripts/audit_zero_orm_strictness.py`) are tracked in `Tier 2 Hardening (Backend)`, while `.sql`, `.yml`, and test/fake files are strictly excluded per `TPR004`.

## Remaining
- Execute Steps 1 through 5 of `@[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md]` via `/tier2-execute`.
- Complete Post-Implementation Gates (`Tier 2 Hardening (Backend)`, `Golden Master & Test Restoration Audit`, `Pre-Delete Audit`, `Semantic Coverage & Zero-Loss Audit`), `As-Built Architectural Sync` (`/tier7-describe-architecture`), and `System 2 Red-Team Audit` (`/tier8-audit-plan`).

## Resume Command
```powershell
/tier2-execute --full-auto @[docs/implementationplans/IMPLEMENTATION_PLAN_PostgreSQL.md] @[docs/implementationplans/TRACKER_PostgreSQL.md]
```
