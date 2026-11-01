<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 1: Leaf Constants, Column Coercion Helpers & Upsert Executor Extraction (`phase1_leaf_constants_and_coercion_extraction.md`)

## 1. Objective
Execute Phase 1 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/database/postgres/entity_adapter.py]`:
1. Create the test package markers `[NEW] @[backend_v2/tests/unit/database/postgres/__init__.py]` and `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/__init__.py]` (`strangler_fig_mandate` rule 2: test subpackages require `__init__.py` from Step 1 to prevent Pytest flat-namespace collisions, while the source domain sub-directory `backend_v2/database/postgres/entity_adapter/` MUST NOT contain `__init__.py` while `backend_v2/database/postgres/entity_adapter.py` exists on disk).
2. Extend `is_boundary_exempt` (`@[scripts/_ast_guardrails.py#L114-L133]`) so sub-modules inside `backend_v2/database/postgres/entity_adapter/` inherit the boundary exemption of `backend_v2/database/postgres/entity_adapter.py` during Epoch 1 pure structural lift-and-shift, and extend `audit_python_file` (`@[scripts/audit_zero_orm_strictness.py#L536-L566]`) so `ZORM006` 1:1 DDL column subscript validation covers all files inside `backend_v2/database/postgres/entity_adapter/`.
3. Extract depth-0 table/prefix constants (`CANONICAL_SEED_TABLES` `#L67-L78`, `_COLLECTION_TO_TABLE_MAP` `#L80-L95`, `_TABLE_TO_ENTITY_PREFIX` `#L98-L109`, `_SYSTEM_ORG_UUID7` `#L111`, `_ROOT_SYSTEM_ORG_UUID7` `#L112`), `_ReportBinaryRowDTO` (`@[backend_v2/database/postgres/entity_adapter.py#L763-L780]`), column coercion helpers (`_coerce_uuid_or_str` `@[backend_v2/database/postgres/entity_adapter.py#L783-L794]`, `_parse_optional_uuid7` `@[backend_v2/database/postgres/entity_adapter.py#L797-L812]`, `_format_optional_uuid7` `@[backend_v2/database/postgres/entity_adapter.py#L815-L830]`, `_parse_org_uuid7` `@[backend_v2/database/postgres/entity_adapter.py#L833-L849]`, `_format_org_uuid7` `@[backend_v2/database/postgres/entity_adapter.py#L852-L872]`, `_decode_jsonb_column` `@[backend_v2/database/postgres/entity_adapter.py#L875-L890]`, `_encode_optional_jsonb` `@[backend_v2/database/postgres/entity_adapter.py#L893-L904]`, `_coerce_float` `@[backend_v2/database/postgres/entity_adapter.py#L907-L918]`), and `execute_entity_upsert` (extracted from `PostgresEntityAdapter._execute_upsert` `@[backend_v2/database/postgres/entity_adapter.py#L1261-L1300]`) into `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` (`< 260` lines).
4. Wire explicit redundant re-exports (`Symbol as Symbol`) and `__path__` resolution in `@[backend_v2/database/postgres/entity_adapter.py]` and create `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` | Canonical seed table constants, `_ReportBinaryRowDTO`, UUIDv7/JSONB/float column coercion helpers, `resolve_effective_timeout`, and `execute_entity_upsert` (`< 260` lines, without `__init__.py` in `backend_v2/database/postgres/entity_adapter/`) |
| `[MODIFY]` | `@[backend_v2/database/postgres/entity_adapter.py]` | Declare `__path__`, replace extracted constants, `_ReportBinaryRowDTO` (`@[backend_v2/database/postgres/entity_adapter.py#L763-L780]`), coercion helpers (`@[backend_v2/database/postgres/entity_adapter.py#L763-L780]`), and `_execute_upsert` (`@[backend_v2/database/postgres/entity_adapter.py#L1261-L1300]`) with explicit redundant re-exports (`Symbol as Symbol`) and delegation to `coercion_and_constants.py` |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py#L114-L133]` | Extend `is_boundary_exempt` so files under `backend_v2/database/postgres/entity_adapter/` inherit boundary exemption during Epoch 1 lift-and-shift |
| `[MODIFY]` | `@[scripts/audit_zero_orm_strictness.py#L536-L566]` | Extend `audit_python_file` `is_adapter` predicate so `"entity_adapter" in filepath.parts` enforces `ZORM006` column subscript parity across `backend_v2/database/postgres/entity_adapter/` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/database/postgres/__init__.py]` | Mandatory Pytest test package marker for `database/postgres/` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/__init__.py]` | Mandatory Pytest test package marker for `database/postgres/entity_adapter/` |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]` | Unit and negative boundary tests for `coercion_and_constants.py` (`CANONICAL_SEED_TABLES`, `_ReportBinaryRowDTO`, UUIDv7/org/JSONB/float coercion helpers, and `execute_entity_upsert`) |

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
  <step id="1" name="Create Test Package Markers, Extend Guardrails, and Extract coercion_and_constants.py">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/database/postgres/entity_adapter/__init__.py during Phase 1 while backend_v2/database/postgres/entity_adapter.py exists on disk. Create backend_v2/tests/unit/database/postgres/__init__.py and backend_v2/tests/unit/database/postgres/entity_adapter/__init__.py immediately.</constraint>
    <constraint invariant="topological_leaf_first_extraction_mandate">coercion_and_constants.py MUST NOT import from backend_v2.database.postgres.entity_adapter and MUST remain under 260 lines with all lines <= 120 characters.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/tests/unit/database/postgres/__init__.py]` and `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/__init__.py]` containing module docstrings.
      2. Update `is_boundary_exempt` (`@[scripts/_ast_guardrails.py#L114-L133]`) so `rel_posix.startswith(("backend_v2/llm/provider/", "backend_v2/database/postgres/entity_adapter/"))` (and `"backend_v2/database/postgres/entity_adapter/" in posix_str` in the fallback branch) returns `True`.
      3. Update `audit_python_file` (`@[scripts/audit_zero_orm_strictness.py#L536-L566]`) so `is_adapter = filepath.name in {"graph_adapter.py", "entity_adapter.py"} or "entity_adapter" in filepath.parts`.
      4. Create `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` (`< 260` lines, all lines `<= 120` chars) with explicit `__all__`:
         - Relocate `CANONICAL_SEED_TABLES` (`#L67-L78`), `_COLLECTION_TO_TABLE_MAP` (`#L80-L95`), `_TABLE_TO_ENTITY_PREFIX` (`#L98-L109`), `_SYSTEM_ORG_UUID7` (`#L111`), and `_ROOT_SYSTEM_ORG_UUID7` (`#L112`).
         - Relocate `_ReportBinaryRowDTO` verbatim from `@[backend_v2/database/postgres/entity_adapter.py#L763-L780]`.
         - Relocate `_coerce_uuid_or_str` (`@[backend_v2/database/postgres/entity_adapter.py#L783-L794]`), `_parse_optional_uuid7` (`@[backend_v2/database/postgres/entity_adapter.py#L797-L812]`), `_format_optional_uuid7` (`@[backend_v2/database/postgres/entity_adapter.py#L815-L830]`), `_parse_org_uuid7` (`@[backend_v2/database/postgres/entity_adapter.py#L833-L849]`), `_format_org_uuid7` (`@[backend_v2/database/postgres/entity_adapter.py#L852-L872]`), `_decode_jsonb_column` (`@[backend_v2/database/postgres/entity_adapter.py#L875-L890]`), `_encode_optional_jsonb` (`@[backend_v2/database/postgres/entity_adapter.py#L893-L904]`), and `_coerce_float` (`@[backend_v2/database/postgres/entity_adapter.py#L907-L918]`).
         - Extract `execute_entity_upsert(conn: AsyncPgConnectionProtocol, timeout: float, sql: str, *args: object, entity_id: str, table: str) -> None` from `PostgresEntityAdapter._execute_upsert` (`@[backend_v2/database/postgres/entity_adapter.py#L1261-L1300]`).
    </action>
  </step>

  <step id="2" name="Rewire Re-Exports in entity_adapter.py and Add Unit Tests">
    <constraint invariant="explicit_reexport_mandate">Use explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/database/postgres/entity_adapter.py.</constraint>
    <action>
      1. Update `@[backend_v2/database/postgres/entity_adapter.py]` to declare `__path__: list[str] = [str(Path(__file__).resolve().with_suffix(""))]`, replace extracted constants, `_ReportBinaryRowDTO` (`@[backend_v2/database/postgres/entity_adapter.py#L763-L780]`), and coercion functions (`@[backend_v2/database/postgres/entity_adapter.py#L763-L780]`) with explicit redundant re-exports from `backend_v2.database.postgres.entity_adapter.coercion_and_constants`, and delegate `PostgresEntityAdapter._execute_upsert` (`@[backend_v2/database/postgres/entity_adapter.py#L1261-L1300]`) to `execute_entity_upsert`.
      2. Create `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_coercion_and_constants.py]` covering positive and negative boundary cases for `_ReportBinaryRowDTO` (`size_bytes` mismatch rejection), `_coerce_uuid_or_str`, `_parse_optional_uuid7`, `_format_optional_uuid7`, `_parse_org_uuid7` (`system`, `org_system_root`, prefixed UUIDv7, invalid string), `_format_org_uuid7`, `_decode_jsonb_column`, `_encode_optional_jsonb`, `_coerce_float`, and `execute_entity_upsert` (driver fault translation vs direct `AppException` passthrough).
    </action>
  </step>

  <step id="3" name="Run Phase 1 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on coercion_and_constants.py, scripts/_ast_guardrails.py, scripts/audit_zero_orm_strictness.py, and backend_v2/database/postgres/entity_adapter.py.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/coercion_and_constants.py --test --ast-strict`.
      2. Execute `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict` and `uv run python scripts/backend_audit_loop.py scripts/audit_zero_orm_strictness.py --test --ast-strict`.
      3. Execute `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter.py --test --ast-strict` to verify all 18 baseline tests in `test_postgres.py` pass with `>= 90%` coverage.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_coercion_helpers_and_canonical_seed_tables_parity">
      Verifies that CANONICAL_SEED_TABLES, _parse_org_uuid7, _format_org_uuid7, _decode_jsonb_column, and _coerce_float behave identically to pre-extraction behavior.
    </contract>
    <contract type="positive" name="test_execute_entity_upsert_executes_parameterized_sql">
      Verifies that execute_entity_upsert forwards SQL, parameters, and command_timeout_seconds to AsyncPgConnectionProtocol.execute.
    </contract>
    <contract type="negative" name="test_report_binary_row_dto_size_mismatch_and_upsert_driver_fault">
      Verifies that _ReportBinaryRowDTO rejects mismatched size_bytes and execute_entity_upsert translates driver exceptions into AppException(STORAGE_ACCESS_FAILED).
    </contract>
  </test_contracts>
</execution_protocol>
```
