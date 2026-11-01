<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Master Decomposition Tracker: `backend_v2/database/postgres/entity_adapter.py` (`PostgresEntityAdapter`, `CANONICAL_SEED_TABLES`)

- **Target Monolith**: `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]` (`2,515` lines, `48` AST symbols)
- **Target Domain Package**: `backend_v2/database/postgres/entity_adapter/` (`< 450` lines per sub-module, `< 280` lines for `__init__.py` facade)
- **Symbol & Blast-Radius Map**: `@[docs/epic/tasks_entity_adapter/symbol_migration_map.md]`
- **Monolith Archetype**: **Archetype C — Ingress / Persistence Anti-Corruption Layer (ACL) & Zero-ORM Reconstitution Firewall** (PostgreSQL 19 Native UUIDv7/BYTEA/JSONB SQL Parameter Binding, Deterministic Pydantic V2 `model_validate(strict=False)` Row Hydration, RFC 7807 `STORAGE_ACCESS_FAILED` / `VALIDATION_FAILED` Dual-Reporting, and `ZORM001`–`ZORM006` Zero-ORM Strictness Compliance)
- **Pre-Flight Test Baseline (`[BASELINE]`)**: **18 passed unit tests, 97% line coverage** (`538` statements, `15` missed: lines `849, 869, 1456, 1566, 1758, 1864, 1969, 2045, 2107, 2193, 2303, 2381, 2449, 2474, 2490` in `@[backend_v2/tests/unit/database/test_postgres.py#L837-L1174]`). Exceeds the `75%` minimum coverage gate (`Phase 0` skipped).

---

## Phase Execution Status

### Phase 1: Leaf Constants, Column Coercion Helpers & Upsert Executor Extraction (Epoch 1 Leaf & Coercion)
- **Plan:** @[docs/epic/tasks_entity_adapter/phase1_leaf_constants_and_coercion_extraction.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [x] **[OK] Execution:** `/tier2-execute @[docs/epic/tasks_entity_adapter/phase1_leaf_constants_and_coercion_extraction.md] @[docs/epic/entity_adapter_decomposition_tracker.md]`
  - [x] Step 1: Create `[NEW] @[backend_v2/tests/unit/database/postgres/__init__.py]` and `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/__init__.py]`, extend `is_boundary_exempt` in `@[scripts/_ast_guardrails.py#L114-L133]` and `audit_python_file` in `@[scripts/audit_zero_orm_strictness.py#L536-L566]` to cover `backend_v2/database/postgres/entity_adapter/`, and create `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` (`CANONICAL_SEED_TABLES`, `_COLLECTION_TO_TABLE_MAP`, `_TABLE_TO_ENTITY_PREFIX`, `_SYSTEM_ORG_UUID7`, `_ROOT_SYSTEM_ORG_UUID7`, `_ReportBinaryRowDTO`, `_coerce_uuid_or_str`, `_parse_optional_uuid7`, `_format_optional_uuid7`, `_parse_org_uuid7`, `_format_org_uuid7`, `_decode_jsonb_column`, `_encode_optional_jsonb`, `_coerce_float`, `execute_entity_upsert`) without creating `backend_v2/database/postgres/entity_adapter/__init__.py`.
  - [x] Step 2: Update `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]` to declare `__path__`, re-export all Phase 1 symbols using explicit redundant aliases (`Symbol as Symbol`), and delegate `_execute_upsert` to `execute_entity_upsert`, and create `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`.
  - [x] Step 3: Run `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/coercion_and_constants.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py scripts/audit_zero_orm_strictness.py --test --ast-strict`, and `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter.py --test --ast-strict`.
- [x] **[OK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_entity_adapter/phase1_leaf_constants_and_coercion_extraction.md] @[docs/epic/entity_adapter_decomposition_tracker.md]`

### Phase 2: IAM, System Config & Studio Entities Stage Extraction (Epoch 1 Domain Entities)
- **Plan:** @[docs/epic/tasks_entity_adapter/phase2_iam_and_studio_entities_extraction.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_entity_adapter/phase2_iam_and_studio_entities_extraction.md] @[docs/epic/entity_adapter_decomposition_tracker.md]`
  - [ ] Step 1: Create `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` (`organizations`, `users`, `system_configs`), `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` (`prompt_blocks`, `steps`), and `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` (`workflows`, `output_profiles`).
  - [ ] Step 2: Update `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]` to re-export all Phase 2 SQL constants and stage functions using explicit redundant aliases (`Symbol as Symbol`) and delegate IAM, SystemConfig, PromptBlock, Step, Workflow, and OutputProfile methods, and create `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`, `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`, and `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]`.
  - [ ] Step 3: Run `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py --test --ast-strict`, and `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter.py --test --ast-strict`.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_entity_adapter/phase2_iam_and_studio_entities_extraction.md] @[docs/epic/entity_adapter_decomposition_tracker.md]`

### Phase 3: Execution, Report Artifact/Binary & Seed/Collection Stage Extraction (Epoch 1 Execution & Collection Core)
- **Plan:** @[docs/epic/tasks_entity_adapter/phase3_execution_report_and_collection_extraction.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_entity_adapter/phase3_execution_report_and_collection_extraction.md] @[docs/epic/entity_adapter_decomposition_tracker.md]`
  - [ ] Step 1: Create `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` (`report_binaries`, `executions`, `report_artifacts`) and `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` (`seed_collection_batch_rows`, `verify_seed_table_counts_rows`, `list_collection_documents_rows`, `get_collection_document_row`, `upsert_collection_document_row`, `delete_collection_document_row`, `clear_collection_documents_rows`).
  - [ ] Step 2: Update `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]` (`< 280` lines) to re-export all Phase 3 SQL constants and stage functions using explicit redundant aliases (`Symbol as Symbol`) and delegate all remaining `PostgresEntityAdapter` methods, and create `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]` and `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`.
  - [ ] Step 3: Run `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py --test --ast-strict`, and `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter.py --test --ast-strict`.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_entity_adapter/phase3_execution_report_and_collection_extraction.md] @[docs/epic/entity_adapter_decomposition_tracker.md]`

### Phase 4: Atomic Package Cutover, Facade Test Suite, Caller Synchronization & QGR017 Lockdown (Epoch 1 Cutover)
- **Plan:** @[docs/epic/tasks_entity_adapter/phase4_package_cutover_and_guardrails.md]
- [x] **[SKIPPED] Research:** Complete 4-Phase Strangler Fig Decomposition pre-researched in Tier 3
- [ ] **[NOK] Execution:** `/tier2-execute @[docs/epic/tasks_entity_adapter/phase4_package_cutover_and_guardrails.md] @[docs/epic/entity_adapter_decomposition_tracker.md]`
  - [ ] Step 1: Create `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]` testing `PostgresEntityAdapter`, `EntityPersistencePort` protocol conformance, `get_settings` monkeypatch propagation, and full re-export parity across `backend_v2.database.postgres.entity_adapter`.
  - [ ] Step 2: Atomically create `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` (`< 280` lines), physically delete `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]`, and synchronize 1-hop production callers (`@[backend_v2/database/postgres/uow.py#L218-L233]`, `@[backend_v2/database/postgres/storage_driver.py#L218-L246]`).
  - [ ] Step 3: Lock retired path `backend_v2/database/postgres/entity_adapter.py` in `@[scripts/_ast_guardrails.py#L898-L1026]` (`QGR017`), update `BOUNDARY_EXEMPTION_FILES` in `@[scripts/_ast_guardrails.py#L114-L133]` and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1277-L1312]` to `"backend_v2/database/postgres/entity_adapter/__init__.py"`, and synchronize `@[.agents/rules/04_directory_reference.md]`.
- [ ] **[NOK] Audit:** `/tier8-audit-plan @[docs/epic/tasks_entity_adapter/phase4_package_cutover_and_guardrails.md] @[docs/epic/entity_adapter_decomposition_tracker.md]`

### Post-Implementation Gates

- [ ] **[NOK] Tier 2 Hardening (Backend)** (`[NEW]` sub-modules & 1-hop callers): Run `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/auto_hardening_runner.py --tracker "@[docs/epic/entity_adapter_decomposition_tracker.md]" --gate all --model gemini-4-argon-medium --continue-on-failure --agent-cmd "agy --model {model} --dangerously-skip-permissions --print '/tier2-hardening-backend @[{target}]'"`
  - [ ] [NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]
  - [ ] [NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]
  - [ ] [NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]
  - [ ] [NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]
  - [ ] [NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]
  - [ ] [NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]
  - [ ] [NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]
  - [ ] `@[backend_v2/database/postgres/uow.py#L218-L233]`
  - [ ] `@[backend_v2/database/postgres/storage_driver.py#L218-L246]`
- [x] **[SKIPPED] Tier 2 Hardening (Frontend)**: Pure backend Python decomposition with zero `.dart` changes.
- [ ] **[NOK] Pre-Delete Audit**: Verify `git status` and `grep_search` confirm physical removal of `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]`, with `QGR017` blocking re-creation of `backend_v2/database/postgres/entity_adapter.py`.
- [ ] **[NOK] Golden Master & Test Restoration Audit**: Verify all 18 baseline unit tests in `@[backend_v2/tests/unit/database/test_postgres.py#L837-L1174]` and all modularized unit tests (`[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`, `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`, `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`, `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]`, `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`, `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`, and `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]`) pass with `>= 97%` line coverage.
- [ ] **[NOK] Semantic Coverage & Zero-Loss Audit**: Verify 100% symbol parity ($\mathcal{I}_{orig} \subseteq \bigcup \mathcal{I}_{sub}$) and execute `uv run pytest backend_v2/tests/unit/scripts/test_ast_guardrails.py`, `uv run pytest backend_v2/tests/unit/scripts/test_audit_zero_orm_strictness.py`, `uv run python scripts/audit_dict_eradication.py`, and `uv run python scripts/audit_clean_imports.py`.

#### Epoch 2: 12-Item Technical Debt Inventory (Target Scope for Tier 2 Hardening)
1. **Item 1 (`no_naked_dicts_in_state` & `QGR012` / `QGR018` Boundary Verification)**: Audit `seed_collection_batch_rows`, `list_collection_documents_rows`, `get_collection_document_row`, and `upsert_collection_document_row` in `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` to ensure raw `dict[str, object]` payloads remain strictly confined to the `EntityPersistencePort` persistence boundary and are validated via Pydantic V2 `model_validate(strict=False)` before any SQL execution.
2. **Item 4 (`the_duct_tape_ban` / `QGR003` & `ZORM003` Exception Handling Audit)**: Audit all `except Exception as exc:` blocks across `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]`, `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`, `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]`, `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]`, `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]`, and `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` to verify `AppException` passthrough (`except AppException: raise`) and structured `logger.error` + `AppException(ErrorCodes.STORAGE_ACCESS_FAILED)` dual-reporting on every database boundary.
3. **Item 6 (`python_314_modern_syntax`)**: Verify PEP 695 type aliases, `X | None` union annotations, and modern `except (ValueError, TypeError) as exc:` / `except ValueError, TypeError:` syntax across all 6 stage sub-modules and `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]`.
4. **Item 7 (`strict_configuration_segregation` & `unbounded_io_timeout_mandate`)**: Verify that `PostgresEntityAdapter.__init__` in `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` resolves default `command_timeout_seconds` strictly from `get_settings().postgres_command_timeout_seconds` (`> 0`) and passes explicit `timeout=self._timeout` to every `AsyncPgConnectionProtocol` call (`execute`, `fetch`, `fetchrow`).
5. **Item 8 (`docstring_fail_fast_ban` & `pep257_google_style_docstrings`)**: Ensure all classes, methods, and functions across `backend_v2/database/postgres/entity_adapter/` include complete PEP 257 Google-style docstrings with `Args:`, `Returns:`, and explicit `Raises:` error codes (`ErrorCodes.STORAGE_ACCESS_FAILED`, `ErrorCodes.VALIDATION_FAILED`, `ErrorCodes.RESOURCE_NOT_FOUND`).
6. **Item 10 (`anti_happy_path_mandate` — ISTQB Negative & Boundary Partitions)**: Add negative and boundary unit tests covering the 15 missed statements from baseline (`lines 849, 869, 1456, 1566, 1758, 1864, 1969, 2045, 2107, 2193, 2303, 2381, 2449, 2474, 2490` of `entity_adapter.py`) across `backend_v2/tests/unit/database/postgres/entity_adapter/` to achieve `>= 99%` line coverage.

#### Architectural Documentation Synchronization
- [ ] **[NOK] As-Built Architectural Sync**: Run `/tier7-describe-architecture @[docs/epic/entity_adapter_decomposition_tracker.md] @[ki_god_code_prevention.md] @[ki_deterministic_hardening_state.md]`
  - **Target KIs to Synchronize**: `@[ki_god_code_prevention.md]`, `@[ki_deterministic_hardening_state.md]`
  - **Directory Reference Sync**: Verify `@[.agents/rules/04_directory_reference.md]` reflects `backend_v2/database/postgres/entity_adapter/` and `backend_v2/tests/unit/database/postgres/entity_adapter/`
  - **Pillar Documentation Sync**: Update Database & Persistence documentation in `docs/architecture/` to reflect the modular `backend_v2/database/postgres/entity_adapter/` package

### Final Epic Audit
- [ ] **[NOK] System 2 Red-Team Audit**: Run `/tier8-audit-plan @[docs/epic/tasks_entity_adapter/phase4_package_cutover_and_guardrails.md] @[docs/epic/entity_adapter_decomposition_tracker.md]` and verify 100% completion across all phases and gates.

## Instructions for the Execution Agent
1. **Strict Two-Epoch Firewall**: During Epoch 1 (Phases 1–4), perform ONLY pure structural lift-and-shift extraction, consumer import verification, test suite modularization, and atomic package cutover with **zero behavioral changes**. Do NOT mix Epoch 2 tech debt fixes into Epoch 1.
2. **Two-Phase Package Strangler Protocol**: Do NOT create `backend_v2/database/postgres/entity_adapter/__init__.py` during Phases 1, 2, or 3 while `backend_v2/database/postgres/entity_adapter.py` exists on disk. Create `__init__.py` and delete `entity_adapter.py` atomically in Phase 4 Step 2.
3. **Quality Gate Enforcement**: Run `uv run python scripts/backend_audit_loop.py <target> --test --ast-strict` after every phase step and create an atomic Conventional Commit before advancing to the next phase.

## Requirements Traceability Matrix

| Requirement ID | Architectural Requirement | Phase & Step Mapping | Verification Target |
| :--- | :--- | :--- | :--- |
| `REQ-EAD-01` | Create test package markers, extend `is_boundary_exempt` and `audit_zero_orm_strictness.py` for `backend_v2/database/postgres/entity_adapter/`, and extract leaf constants, `_ReportBinaryRowDTO`, coercion helpers, and `execute_entity_upsert` into `coercion_and_constants.py` | Phase 1, Step 1 | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` |
| `REQ-EAD-02` | Declare `__path__`, rewire Phase 1 explicit redundant re-exports in `entity_adapter.py`, and add unit tests for `coercion_and_constants.py` | Phase 1, Step 2 | `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]` |
| `REQ-EAD-03` | Verify Phase 1 extraction passes 10/10 backend audit gates and all 18 baseline unit tests | Phase 1, Step 3 | `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]` |
| `REQ-EAD-04` | Extract IAM (`organizations`, `users`) and `system_configs` into `iam_and_system_stage.py`, `prompt_blocks` and `steps` into `prompt_block_and_step_stage.py`, and `workflows` and `output_profiles` into `workflow_and_profile_stage.py` | Phase 2, Step 1 | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]`, `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]`, `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` |
| `REQ-EAD-05` | Rewire Phase 2 explicit redundant re-exports and method delegation in `entity_adapter.py` and add unit tests for all three Phase 2 stage modules | Phase 2, Step 2 | `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`, `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`, `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]` |
| `REQ-EAD-06` | Verify Phase 2 extraction passes 10/10 backend audit gates and all 18 baseline unit tests | Phase 2, Step 3 | `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]` |
| `REQ-EAD-07` | Extract `report_binaries`, `executions`, and `report_artifacts` into `execution_and_report_stage.py` and `seed_collection_batch`, `verify_seed_table_counts`, and collection CRUD into `seed_and_collection_stage.py` | Phase 3, Step 1 | `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]`, `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` |
| `REQ-EAD-08` | Reduce `entity_adapter.py` to `< 280` lines with explicit redundant re-exports and add unit tests for `execution_and_report_stage.py` and `seed_and_collection_stage.py` | Phase 3, Step 2 | `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]`, `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]` |
| `REQ-EAD-09` | Verify Phase 3 extraction passes 10/10 backend audit gates and all 18 baseline unit tests | Phase 3, Step 3 | `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]` |
| `REQ-EAD-10` | Create package facade unit test suite `test_entity_adapter_facade.py` verifying `EntityPersistencePort` conformance and symbol re-exports | Phase 4, Step 1 | `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]` |
| `REQ-EAD-11` | Atomically replace `entity_adapter.py` with `entity_adapter/__init__.py` (`< 280` lines) and synchronize 1-hop callers (`uow.py`, `storage_driver.py`) | Phase 4, Step 2 | `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` |
| `REQ-EAD-12` | Lock retired `backend_v2/database/postgres/entity_adapter.py` in `QGR017`, update `BOUNDARY_EXEMPTION_FILES` to `backend_v2/database/postgres/entity_adapter/__init__.py`, and synchronize `04_directory_reference.md` | Phase 4, Step 3 | `@[scripts/_ast_guardrails.py#L898-L1026]`, `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1277-L1312]` |

# Session Handover Context

## Achieved
- Completed and audited Phase 1 (`@[docs/epic/tasks_entity_adapter/phase1_leaf_constants_and_coercion_extraction.md]`): created test package markers `[NEW] @[backend_v2/tests/unit/database/postgres/__init__.py]` and `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/__init__.py]`, extended `is_boundary_exempt` in `@[scripts/_ast_guardrails.py#L114-L138]` and `audit_python_file` in `@[scripts/audit_zero_orm_strictness.py#L536-L567]`, extracted `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` (`255` lines, `100%` line coverage), rewired explicit redundant re-exports and `__path__` in `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]`, and created `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]` (`4 passed, 100% coverage`).
- Passed Tier 8 Post-Implementation Audit (`/tier8-audit-plan @[docs/epic/tasks_entity_adapter/phase1_leaf_constants_and_coercion_extraction.md] @[docs/epic/entity_adapter_decomposition_tracker.md]`): verified 10/10 backend quality gates, `0` technical debt findings across 5 targets and 3 1-hop callers, `100%` Plan-Tracker AST parity, and `18/18` baseline unit tests passing (`97%` coverage).

## Learned
- In Python 3.14, setting both `__path__: list[str] = [str(Path(__file__).resolve().with_suffix(""))]` and `if __spec__ is not None: __spec__.submodule_search_locations = __path__` at the top of `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]` enables submodule imports (`backend_v2.database.postgres.entity_adapter.coercion_and_constants`) while `entity_adapter.py` remains a `.py` file on disk without `entity_adapter/__init__.py`.
- `InMemoryAsyncPgPool.acquire()` in `@[backend_v2/tests/fakes/in_memory_uow.py]` is an async coroutine returning `AsyncPgConnectionProtocol` (`conn = await pool.acquire()`, paired with `await pool.release(conn)` in `finally:`).

## Resume Command
`/tier2-execute @[docs/epic/tasks_entity_adapter/phase2_iam_and_studio_entities_extraction.md] @[docs/epic/entity_adapter_decomposition_tracker.md]`

## Remaining
- Execute Phase 2 (`@[docs/epic/tasks_entity_adapter/phase2_iam_and_studio_entities_extraction.md]`), Phase 3 (`@[docs/epic/tasks_entity_adapter/phase3_execution_report_and_collection_extraction.md]`), and Phase 4 (`@[docs/epic/tasks_entity_adapter/phase4_package_cutover_and_guardrails.md]`), followed by Epoch 2 Tier 2 Backend Hardening and `/tier7-describe-architecture`.
