<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Symbol & Blast-Radius Migration Map: `backend_v2/database/postgres/entity_adapter.py`

## 1. Source Monolith Summary
- **Monolith Path**: `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]` (`2,515` lines, `48` AST symbol definitions)
- **Target Domain Package**: `backend_v2/database/postgres/entity_adapter/` (`6` sub-modules + `__init__.py` facade, all `< 450` lines, facade `< 280` lines)
- **Monolith Archetype**: **Archetype C — Ingress / Persistence Anti-Corruption Layer (ACL) & Zero-ORM Reconstitution Firewall** (PostgreSQL 19 Native UUIDv7/BYTEA/JSONB SQL Parameter Binding, Deterministic Pydantic V2 `model_validate(strict=False)` Row Hydration, RFC 7807 `STORAGE_ACCESS_FAILED` / `VALIDATION_FAILED` Dual-Reporting, and `ZORM001`–`ZORM006` Zero-ORM Strictness Compliance)
- **Pre-Flight Baseline (`[BASELINE]`)**: **18 passed unit tests, 97% line coverage** (`538` statements, `15` missed: lines `849, 869, 1456, 1566, 1758, 1864, 1969, 2045, 2107, 2193, 2303, 2381, 2449, 2474, 2490` across `@[backend_v2/tests/unit/database/test_postgres.py#L837-L1174]`).

---

## 2. Complete AST Symbol-to-Submodule Mapping ($\mathcal{I}_{orig} \subseteq \bigcup \mathcal{I}_{sub}$)

| Original AST Symbol | Original Line Span (`entity_adapter.py`) | Target Sub-Module (`backend_v2/database/postgres/entity_adapter/`) | Extraction Phase |
| :--- | :--- | :--- | :--- |
| `CANONICAL_SEED_TABLES` | `#L67-L78` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `_COLLECTION_TO_TABLE_MAP` | `#L80-L95` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `_TABLE_TO_ENTITY_PREFIX` | `#L98-L109` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `_SYSTEM_ORG_UUID7`, `_ROOT_SYSTEM_ORG_UUID7` | `#L111-L112` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `_ReportBinaryRowDTO` | `@[backend_v2/database/postgres/entity_adapter.py#L763-L780]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `_coerce_uuid_or_str` | `@[backend_v2/database/postgres/entity_adapter.py#L783-L794]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `_parse_optional_uuid7` | `@[backend_v2/database/postgres/entity_adapter.py#L797-L812]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `_format_optional_uuid7` | `@[backend_v2/database/postgres/entity_adapter.py#L815-L830]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `_parse_org_uuid7` | `@[backend_v2/database/postgres/entity_adapter.py#L833-L849]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `_format_org_uuid7` | `@[backend_v2/database/postgres/entity_adapter.py#L852-L872]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `_decode_jsonb_column` | `@[backend_v2/database/postgres/entity_adapter.py#L875-L890]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `_encode_optional_jsonb` | `@[backend_v2/database/postgres/entity_adapter.py#L893-L904]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `_coerce_float` | `@[backend_v2/database/postgres/entity_adapter.py#L907-L918]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `PostgresEntityAdapter._execute_upsert` (`execute_entity_upsert`) | `@[backend_v2/database/postgres/entity_adapter.py#L1261-L1300]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Phase 1 |
| `_UPSERT_ORGANIZATION_SQL`, `_GET_ORGANIZATION_SQL`, `_LIST_ORGANIZATIONS_SQL` | `#L352-L381` | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` | Phase 2 |
| `PostgresEntityAdapter._hydrate_organization_row` (`hydrate_organization_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1302-L1327]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.upsert_organization` (`upsert_organization_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1329-L1361]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.get_organization` (`get_organization_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1363-L1383]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` | Phase 2 |
| `_UPSERT_USER_SQL`, `_GET_USER_SQL`, `_LIST_USERS_SQL` | `#L383-L408` | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` | Phase 2 |
| `PostgresEntityAdapter._hydrate_user_row` (`hydrate_user_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1385-L1409]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.upsert_user` (`upsert_user_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1411-L1439]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.get_user` (`get_user_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1441-L1457]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` | Phase 2 |
| `_UPSERT_SYSTEM_CONFIG_SQL`, `_GET_SYSTEM_CONFIG_SQL`, `_LIST_SYSTEM_CONFIGS_SQL` | `#L410-L441` | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` | Phase 2 |
| `PostgresEntityAdapter._hydrate_system_config_row` (`hydrate_system_config_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1459-L1497]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.upsert_system_config` (`upsert_system_config_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1499-L1549]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.get_system_config` (`get_system_config_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1551-L1567]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` | Phase 2 |
| `_UPSERT_PROMPT_BLOCK_SQL`, `_GET_PROMPT_BLOCK_SQL`, `_LIST_PROMPT_BLOCKS_SQL` | `#L443-L500` | `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` | Phase 2 |
| `PostgresEntityAdapter._hydrate_prompt_block_row` (`hydrate_prompt_block_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1569-L1666]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.upsert_prompt_block` (`upsert_prompt_block_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1668-L1741]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.get_prompt_block` (`get_prompt_block_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1743-L1759]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` | Phase 2 |
| `_UPSERT_STEP_SQL`, `_GET_STEP_SQL`, `_LIST_STEPS_SQL` | `#L502-L552` | `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` | Phase 2 |
| `PostgresEntityAdapter._hydrate_step_row` (`hydrate_step_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1761-L1799]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.upsert_step` (`upsert_step_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1801-L1847]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.get_step` (`get_step_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1849-L1865]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` | Phase 2 |
| `_UPSERT_WORKFLOW_SQL`, `_GET_WORKFLOW_SQL`, `_LIST_WORKFLOWS_SQL` | `#L554-L614` | `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` | Phase 2 |
| `PostgresEntityAdapter._hydrate_workflow_row` (`hydrate_workflow_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1867-L1905]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.upsert_workflow` (`upsert_workflow_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1907-L1952]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.get_workflow` (`get_workflow_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1954-L1970]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` | Phase 2 |
| `_UPSERT_OUTPUT_PROFILE_SQL`, `_GET_OUTPUT_PROFILE_SQL`, `_LIST_OUTPUT_PROFILES_SQL` | `#L616-L721` | `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` | Phase 2 |
| `PostgresEntityAdapter._hydrate_output_profile_row` (`hydrate_output_profile_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1972-L2025]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.upsert_output_profile` (`upsert_output_profile_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L2027-L2090]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` | Phase 2 |
| `PostgresEntityAdapter.get_output_profile` (`get_output_profile_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L2092-L2108]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` | Phase 2 |
| `_SAVE_REPORT_BINARY_SQL`, `_MARK_REPORT_ARTIFACT_PDF_SQL`, `_GET_REPORT_BINARY_SQL` | `#L114-L134` | `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` | Phase 3 |
| `_SAVE_EXECUTION_SQL`, `_GET_EXECUTION_SQL`, `_LIST_EXECUTIONS_SQL` | `#L136-L350` | `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` | Phase 3 |
| `_UPSERT_REPORT_ARTIFACT_SQL`, `_GET_REPORT_ARTIFACT_SQL`, `_LIST_REPORT_ARTIFACTS_SQL` | `#L723-L760` | `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` | Phase 3 |
| `PostgresEntityAdapter.save_report_binary` (`save_report_binary_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L947-L1005]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` | Phase 3 |
| `PostgresEntityAdapter.get_report_binary` (`get_report_binary_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1007-L1066]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` | Phase 3 |
| `PostgresEntityAdapter._hydrate_execution_row` (`hydrate_execution_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1068-L1121]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` | Phase 3 |
| `PostgresEntityAdapter.save_execution` (`save_execution_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1123-L1217]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` | Phase 3 |
| `PostgresEntityAdapter.get_execution` (`get_execution_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L1219-L1259]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` | Phase 3 |
| `PostgresEntityAdapter._hydrate_report_artifact_row` (`hydrate_report_artifact_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L2110-L2138]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` | Phase 3 |
| `PostgresEntityAdapter.upsert_report_artifact` (`upsert_report_artifact_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L2140-L2176]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` | Phase 3 |
| `PostgresEntityAdapter.get_report_artifact` (`get_report_artifact_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L2178-L2194]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` | Phase 3 |
| `PostgresEntityAdapter.seed_collection_batch` (`seed_collection_batch_rows`) | `@[backend_v2/database/postgres/entity_adapter.py#L2196-L2265]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` | Phase 3 |
| `PostgresEntityAdapter.verify_seed_table_counts` (`verify_seed_table_counts_rows`) | `@[backend_v2/database/postgres/entity_adapter.py#L2267-L2340]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` | Phase 3 |
| `PostgresEntityAdapter.list_collection_documents` (`list_collection_documents_rows`) | `@[backend_v2/database/postgres/entity_adapter.py#L2342-L2381]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` | Phase 3 |
| `PostgresEntityAdapter.get_collection_document` (`get_collection_document_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L2383-L2420]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` | Phase 3 |
| `PostgresEntityAdapter.upsert_collection_document` (`upsert_collection_document_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L2422-L2474]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` | Phase 3 |
| `PostgresEntityAdapter.delete_collection_document` (`delete_collection_document_row`) | `@[backend_v2/database/postgres/entity_adapter.py#L2476-L2504]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` | Phase 3 |
| `PostgresEntityAdapter.clear_collection_documents` (`clear_collection_documents_rows`) | `@[backend_v2/database/postgres/entity_adapter.py#L2506-L2515]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` | Phase 3 |
| `PostgresEntityAdapter` (Class & `__init__`) | `@[backend_v2/database/postgres/entity_adapter.py#L921-L2515]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` | Phase 4 |

---

## 3. 1-Hop Callers & Guardrail Blast-Radius Inventory

| Caller / Guardrail File | Symbol Imported / Referenced | Action Required |
| :--- | :--- | :--- |
| `@[backend_v2/database/postgres/uow.py#L218-L233]` & `@[backend_v2/database/postgres/uow.py#L235-L306]` | `from backend_v2.database.postgres.entity_adapter import PostgresEntityAdapter` | Preserved seamlessly via `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` package facade; verified in Phase 4 |
| `@[backend_v2/database/postgres/storage_driver.py#L218-L246]` | `from backend_v2.database.postgres.entity_adapter import PostgresEntityAdapter` | Preserved seamlessly via `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` package facade; verified in Phase 4 |
| `@[backend_v2/database/postgres/__init__.py]` | `from backend_v2.database.postgres.entity_adapter import CANONICAL_SEED_TABLES, PostgresEntityAdapter` | Preserved seamlessly via `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` package facade |
| `@[backend_v2/tests/unit/database/test_postgres.py#L1178-L1438]` & `@[backend_v2/tests/unit/database/test_postgres.py#L1655-L1793]` | `PostgresEntityAdapter`, `_coerce_float`, `_coerce_uuid_or_str`, `_decode_jsonb_column`, `monkeypatch.setattr(entity_adapter_mod, "get_settings", ...)` | Preserved via explicit redundant re-exports in `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` and dynamic `get_settings` resolution |
| `@[scripts/_ast_guardrails.py#L114-L133]` & `@[scripts/_ast_guardrails.py#L898-L1026]` | `BOUNDARY_EXEMPTION_FILES`, `is_boundary_exempt`, `visit_Module` (`QGR017`) | Phase 1: Extend `is_boundary_exempt` for `backend_v2/database/postgres/entity_adapter/`. Phase 4: Replace `"backend_v2/database/postgres/entity_adapter.py"` with `"backend_v2/database/postgres/entity_adapter/__init__.py"` in `BOUNDARY_EXEMPTION_FILES` and register `"backend_v2/database/postgres/entity_adapter.py"` under `QGR017` |
| `@[scripts/audit_zero_orm_strictness.py#L536-L566]` | `audit_python_file` (`is_adapter` check for `ZORM006` column subscript validation) | Phase 1: Extend `is_adapter` check so `"entity_adapter" in filepath.parts` enforces `ZORM006` across all sub-modules in `backend_v2/database/postgres/entity_adapter/` |
| `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1277-L1312]` & `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1771-L1776]` | `test_purged_boundary_exemption_files`, `test_boundary_exemption_files_preserved` | Phase 4: Update `"backend_v2/database/postgres/entity_adapter.py"` to `"backend_v2/database/postgres/entity_adapter/__init__.py"` and add `QGR017` test for banned `backend_v2/database/postgres/entity_adapter.py` |
