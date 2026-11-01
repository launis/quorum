<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 3: Execution, Report Artifact/Binary & Seed/Collection Stage Extraction (`phase3_execution_report_and_collection_extraction.md`)

## 1. Objective
Execute Phase 3 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/database/postgres/entity_adapter.py]`:
1. Extract `report_binaries`, `executions`, and `report_artifacts` SQL constants (`#L114-L350`, `#L723-L760`) and persistence methods (`save_report_binary` `@[backend_v2/database/postgres/entity_adapter.py#L947-L1005]`, `get_report_binary` `@[backend_v2/database/postgres/entity_adapter.py#L1007-L1066]`, `_hydrate_execution_row` `@[backend_v2/database/postgres/entity_adapter.py#L1068-L1121]`, `save_execution` `@[backend_v2/database/postgres/entity_adapter.py#L1123-L1217]`, `get_execution` `@[backend_v2/database/postgres/entity_adapter.py#L1219-L1259]`, `_hydrate_report_artifact_row` `@[backend_v2/database/postgres/entity_adapter.py#L2110-L2138]`, `upsert_report_artifact` `@[backend_v2/database/postgres/entity_adapter.py#L2140-L2176]`, `get_report_artifact` `@[backend_v2/database/postgres/entity_adapter.py#L2178-L2194]`) into `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` (`< 450` lines).
2. Extract seed batching, table count verification, and generic collection CRUD methods (`seed_collection_batch` `@[backend_v2/database/postgres/entity_adapter.py#L2196-L2265]`, `verify_seed_table_counts` `@[backend_v2/database/postgres/entity_adapter.py#L2267-L2340]`, `list_collection_documents` `@[backend_v2/database/postgres/entity_adapter.py#L2342-L2381]`, `get_collection_document` `@[backend_v2/database/postgres/entity_adapter.py#L2383-L2420]`, `upsert_collection_document` `@[backend_v2/database/postgres/entity_adapter.py#L2422-L2474]`, `delete_collection_document` `@[backend_v2/database/postgres/entity_adapter.py#L2476-L2504]`, `clear_collection_documents` `@[backend_v2/database/postgres/entity_adapter.py#L2506-L2515]`) into `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` (`< 360` lines).
3. Reduce `@[backend_v2/database/postgres/entity_adapter.py]` to a thin delegating facade (`< 280` lines) with explicit redundant re-exports (`Symbol as Symbol`) and create unit test suites `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]` and `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` | SQL constants, hydration, and persistence functions for `report_binaries`, `executions`, and `report_artifacts` (`< 450` lines) |
| `[NEW]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` | Seed batch routing (`seed_collection_batch_rows`), table count verification (`verify_seed_table_counts_rows`), and collection document CRUD (`list_collection_documents_rows`, `get_collection_document_row`, `upsert_collection_document_row`, `delete_collection_document_row`, `clear_collection_documents_rows`) (`< 360` lines) |
| `[MODIFY]` | `@[backend_v2/database/postgres/entity_adapter.py]` | Replace execution, report binary, report artifact, seed batch, and collection CRUD SQL constants and methods (`@[backend_v2/database/postgres/entity_adapter.py#L1123-L1217]`, `@[backend_v2/database/postgres/entity_adapter.py#L2267-L2340]`) with explicit redundant re-exports and 1-line delegation (`< 280` lines) |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]` | Unit and negative boundary tests for `execution_and_report_stage.py` (`ExecutionRecord`, `ReportArtifact`, `ReportBinaryPayloadDTO` persistence, hydration, and fault translation) |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]` | Unit and negative boundary tests for `seed_and_collection_stage.py` (`seed_collection_batch_rows`, `verify_seed_table_counts_rows`, collection CRUD, and driver fault translation) |

### Multi-Phase Decomposition Context (Epoch 1 Surviving Targets)
Across Phases 1–4 of the `entity_adapter.py` decomposition, the complete set of surviving production `.py` files (`[NEW]` sub-modules, package facade, and `[MODIFY]` 1-hop production callers) registered for Epoch 2 Tier 2 Hardening is:
- `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` (Phase 1)
- `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` (Phase 2)
- `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` (Phase 2)
- `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` (Phase 2)
- `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` (Phase 3)
- `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` (Phase 3)
- `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` (Phase 4)
- `[MODIFY] @[backend_v2/database/postgres/uow.py#L218-L233]` (Phase 4)
- `[MODIFY] @[backend_v2/database/postgres/storage_driver.py#L218-L246]` (Phase 4)

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Extract execution_and_report_stage.py and seed_and_collection_stage.py">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/database/postgres/entity_adapter/__init__.py during Phase 3 while backend_v2/database/postgres/entity_adapter.py exists on disk.</constraint>
    <constraint invariant="topological_leaf_first_extraction_mandate">Phase 3 stage modules may import ONLY from coercion_and_constants.py, iam_and_system_stage.py, prompt_block_and_step_stage.py, workflow_and_profile_stage.py, and external domain/database modules, NEVER from backend_v2.database.postgres.entity_adapter.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` (`< 450` lines, all lines `<= 120` chars) with explicit `__all__`:
         - Relocate `_SAVE_REPORT_BINARY_SQL`, `_MARK_REPORT_ARTIFACT_PDF_SQL`, `_GET_REPORT_BINARY_SQL` (`#L114-L134`), `_SAVE_EXECUTION_SQL`, `_GET_EXECUTION_SQL`, `_LIST_EXECUTIONS_SQL` (`#L136-L350`), and `_UPSERT_REPORT_ARTIFACT_SQL`, `_GET_REPORT_ARTIFACT_SQL`, `_LIST_REPORT_ARTIFACTS_SQL` (`#L723-L760`).
         - Extract `save_report_binary_row`, `get_report_binary_row` (`@[backend_v2/database/postgres/entity_adapter.py#L1007-L1066]`), `hydrate_execution_row`, `save_execution_row`, `get_execution_row` (`@[backend_v2/database/postgres/entity_adapter.py#L1123-L1217]`), and `hydrate_report_artifact_row`, `upsert_report_artifact_row`, `get_report_artifact_row` (`@[backend_v2/database/postgres/entity_adapter.py#L2140-L2176]`).
      2. Create `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` (`< 360` lines, all lines `<= 120` chars) with explicit `__all__`:
         - Extract `seed_collection_batch_rows` (`@[backend_v2/database/postgres/entity_adapter.py#L2196-L2265]`), `verify_seed_table_counts_rows` (`@[backend_v2/database/postgres/entity_adapter.py#L2267-L2340]`), `list_collection_documents_rows` (`@[backend_v2/database/postgres/entity_adapter.py#L2342-L2381]`), `get_collection_document_row` (`@[backend_v2/database/postgres/entity_adapter.py#L2383-L2420]`), `upsert_collection_document_row` (`@[backend_v2/database/postgres/entity_adapter.py#L2422-L2474]`), `delete_collection_document_row` (`@[backend_v2/database/postgres/entity_adapter.py#L2476-L2504]`), and `clear_collection_documents_rows` (`@[backend_v2/database/postgres/entity_adapter.py#L2506-L2515]`).
    </action>
  </step>

  <step id="2" name="Reduce entity_adapter.py to Delegating Facade and Add Unit Tests">
    <constraint invariant="explicit_reexport_mandate">Use explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/database/postgres/entity_adapter.py and keep entity_adapter.py under 280 lines.</constraint>
    <action>
      1. Update `@[backend_v2/database/postgres/entity_adapter.py]` (`< 280` lines) to re-export all Phase 3 SQL constants and stage functions using explicit redundant aliases (`Symbol as Symbol`) and delegate all remaining `PostgresEntityAdapter` methods to `execution_and_report_stage.py` and `seed_and_collection_stage.py` while resolving `get_settings` dynamically from `sys.modules["backend_v2.database.postgres.entity_adapter"]` when patched by tests.
      2. Create `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]` and `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_seed_and_collection_stage.py]` covering positive and negative cases (including missed baseline lines `2193, 2303, 2381, 2449, 2474, 2490`).
    </action>
  </step>

  <step id="3" name="Run Phase 3 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on execution_and_report_stage.py, seed_and_collection_stage.py, and backend_v2/database/postgres/entity_adapter.py.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py --test --ast-strict`.
      2. Execute `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py --test --ast-strict`.
      3. Execute `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter.py --test --ast-strict` to verify all 18 baseline tests pass with `>= 90%` coverage.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_execution_report_and_seed_collection_roundtrip_parity">
      Verifies that save_execution, get_execution, save_report_binary, get_report_binary, upsert_report_artifact, get_report_artifact, seed_collection_batch, verify_seed_table_counts, and collection CRUD behave identically to pre-extraction behavior.
    </contract>
    <contract type="positive" name="test_collection_crud_across_all_canonical_tables">
      Verifies list_collection_documents_rows, get_collection_document_row, upsert_collection_document_row, delete_collection_document_row, and clear_collection_documents_rows across canonical collections.
    </contract>
    <contract type="negative" name="test_collection_crud_and_report_artifact_fault_translation">
      Verifies that driver faults in get_report_artifact_row, list_collection_documents_rows, upsert_collection_document_row, and delete_collection_document_row raise AppException(STORAGE_ACCESS_FAILED) or AppException(VALIDATION_FAILED).
    </contract>
  </test_contracts>
</execution_protocol>
```
