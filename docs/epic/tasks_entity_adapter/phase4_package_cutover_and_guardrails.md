<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 4: Atomic Package Cutover, Facade Test Suite, Caller Synchronization & QGR017 Lockdown (`phase4_package_cutover_and_guardrails.md`)

## 1. Objective
Execute the final Epoch 1 Cutover of the `backend_v2/database/postgres/entity_adapter.py` decomposition:
1. Create `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]` testing `PostgresEntityAdapter` via the `backend_v2.database.postgres.entity_adapter` package facade (`__init__.py`), `EntityPersistencePort` protocol conformance, default timeout resolution from `get_settings()`, and full symbol re-export parity across all 6 stage sub-modules.
2. Atomically replace `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]` with the domain package facade `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` (`< 280` lines), physically delete `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]`, and verify 1-hop production callers (`@[backend_v2/database/postgres/uow.py#L218-L234]`, `@[backend_v2/database/postgres/storage_driver.py#L218-L246]`, and `@[backend_v2/database/postgres/__init__.py]`).
3. Update `BOUNDARY_EXEMPTION_FILES` in `@[scripts/_ast_guardrails.py#L903-L1042]` from `"backend_v2/database/postgres/entity_adapter.py"` to `"backend_v2/database/postgres/entity_adapter/__init__.py"`, register the retired file path `"backend_v2/database/postgres/entity_adapter.py"` under `QGR017` in `visit_Module` (`@[scripts/_ast_guardrails.py#L903-L1042]`), update `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1277-L1312]` and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1799-L1804]`, and synchronize `@[.agents/rules/04_directory_reference.md]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` | Canonical package facade (`< 280` lines) defining `PostgresEntityAdapter` and re-exporting `CANONICAL_SEED_TABLES` and all stage symbols with explicit `__all__` and redundant aliases (`Symbol as Symbol`) |
| `[DELETE]` | `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]` | Delete legacy monolith/proxy file atomically when creating `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` |
| `[MODIFY]` | `@[backend_v2/database/postgres/uow.py#L218-L234]` | Verify `PostgresEntityAdapter` binding in `PostgresUnitOfWork._bind_unbound_adapters` (`#L218-L234`) against the `backend_v2.database.postgres.entity_adapter` package facade |
| `[MODIFY]` | `@[backend_v2/database/postgres/storage_driver.py#L218-L246]` | Verify `PostgresEntityAdapter` binding in `PostgresStorageDriver._optional_adapter` (`#L218-L246`) against the `backend_v2.database.postgres.entity_adapter` package facade |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]` | Unit tests for `backend_v2.database.postgres.entity_adapter` package facade (`__init__.py`), `EntityPersistencePort` conformance, and re-export parity |
| `[MODIFY]` | `@[scripts/_ast_guardrails.py#L903-L1042]` | Replace `"backend_v2/database/postgres/entity_adapter.py"` with `"backend_v2/database/postgres/entity_adapter/__init__.py"` in `BOUNDARY_EXEMPTION_FILES` and register `backend_v2/database/postgres/entity_adapter.py` under `QGR017` in `visit_Module` |
| `[MODIFY]` | `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1277-L1312]` | Update `test_purged_boundary_exemption_files` (`#L1277-L1312`) and `test_boundary_exemption_files_preserved` (`@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1799-L1804]`) to `"backend_v2/database/postgres/entity_adapter/__init__.py"`, and add `QGR017` test for banned `backend_v2/database/postgres/entity_adapter.py` |
| `[MODIFY]` | `@[.agents/rules/04_directory_reference.md]` | Update `backend_v2/database/` and `backend_v2/tests/unit/` directory references to list `entity_adapter/ (coercion_and_constants.py, iam_and_system_stage.py, prompt_block_and_step_stage.py, workflow_and_profile_stage.py, execution_and_report_stage.py, seed_and_collection_stage.py, __init__.py facade)` |

### Multi-Phase Decomposition Context (Epoch 1 Surviving Targets)
Across Phases 1–4 of the `entity_adapter.py` decomposition, the complete set of surviving production `.py` files (`[NEW]` sub-modules, package facade, and `[MODIFY]` 1-hop production callers) registered for Epoch 2 Tier 2 Hardening is:
- `[NEW] @[backend_v2/database/postgres/entity_adapter/coercion_and_constants.py]` (Phase 1)
- `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` (Phase 2)
- `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` (Phase 2)
- `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` (Phase 2)
- `[NEW] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]` (Phase 3)
- `[NEW] @[backend_v2/database/postgres/entity_adapter/seed_and_collection_stage.py]` (Phase 3)
- `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` (Phase 4)
- `[MODIFY] @[backend_v2/database/postgres/uow.py#L218-L234]` (Phase 4)
- `[MODIFY] @[backend_v2/database/postgres/storage_driver.py#L218-L246]` (Phase 4)

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="Create Package Facade Unit Test Suite under tests/unit/database/postgres/entity_adapter/">
    <constraint invariant="test_directory_isolation">All unit tests for the entity_adapter package facade MUST reside under backend_v2/tests/unit/database/postgres/entity_adapter/ and remain under 450 lines.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_entity_adapter_facade.py]` testing `PostgresEntityAdapter` instantiation, `isinstance(adapter, EntityPersistencePort)`, `get_settings` monkeypatch propagation on `backend_v2.database.postgres.entity_adapter`, and full end-to-end facade delegation across all 26 `EntityPersistencePort` methods and 9 `_hydrate_*_row` static bindings.
    </action>
  </step>

  <step id="2" name="Execute Atomic Package Cutover and Synchronize 1-Hop Callers">
    <constraint invariant="strangler_fig_mandate">Delete backend_v2/database/postgres/entity_adapter.py and create backend_v2/database/postgres/entity_adapter/__init__.py in a single atomic step, keeping __init__.py under 280 lines.</constraint>
    <constraint invariant="explicit_reexport_mandate">Declare __all__ and explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/database/postgres/entity_adapter/__init__.py.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/database/postgres/entity_adapter/__init__.py]` (`< 280` lines) defining `PostgresEntityAdapter` and declaring `__all__` with explicit redundant re-exports (`Symbol as Symbol`) for `CANONICAL_SEED_TABLES`, `_ReportBinaryRowDTO`, all coercion helpers, all SQL constants, and all stage functions across `coercion_and_constants.py`, `iam_and_system_stage.py`, `prompt_block_and_step_stage.py`, `workflow_and_profile_stage.py`, `execution_and_report_stage.py`, and `seed_and_collection_stage.py`.
      2. Physically delete `[DELETE] @[backend_v2/database/postgres/entity_adapter.py]`.
      3. Synchronize and verify 1-hop production callers `@[backend_v2/database/postgres/uow.py#L218-L234]` and `@[backend_v2/database/postgres/storage_driver.py#L218-L246]` against the new `backend_v2.database.postgres.entity_adapter` package facade.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/ --test --ast-strict`, `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/uow.py --test --ast-strict`, and `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/storage_driver.py --test --ast-strict`.</verification>
  </step>

  <step id="3" name="Lock Retired Path in QGR017 AST Guardrails and Synchronize Directory Reference">
    <constraint invariant="ast_guardrail_mandate">Retired monolith paths MUST be permanently banned under QGR017 in scripts/_ast_guardrails.py.</constraint>
    <action>
      1. Modify `@[scripts/_ast_guardrails.py#L903-L1042]` (`visit_Module`) to emit a FATAL `QGR017` violation if `norm_path == "backend_v2/database/postgres/entity_adapter.py" or norm_path.endswith("/backend_v2/database/postgres/entity_adapter.py")`, and update `BOUNDARY_EXEMPTION_FILES` in `@[scripts/_ast_guardrails.py#L903-L1042]` from `"backend_v2/database/postgres/entity_adapter.py"` to `"backend_v2/database/postgres/entity_adapter/__init__.py"`.
      2. Update `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1277-L1312]` (`test_purged_boundary_exemption_files`) and `@[backend_v2/tests/unit/scripts/test_ast_guardrails.py#L1799-L1804]` (`test_boundary_exemption_files_preserved`) to reference `"backend_v2/database/postgres/entity_adapter/__init__.py"`, and add `test_qgr017_banned_entity_adapter_god_file_path_fatal` and `test_qgr017_modular_entity_adapter_package_allowed`.
      3. Modify `@[.agents/rules/04_directory_reference.md]` under `backend_v2/database/` and `backend_v2/tests/unit/` to replace `entity_adapter.py [PostgresEntityAdapter]` with `entity_adapter/ (coercion_and_constants.py, iam_and_system_stage.py, prompt_block_and_step_stage.py, workflow_and_profile_stage.py, execution_and_report_stage.py, seed_and_collection_stage.py, __init__.py facade [PostgresEntityAdapter])` and register the new unit test suite directory.
    </action>
    <verification>Run `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/ --test --ast-strict`, `uv run python scripts/backend_audit_loop.py scripts/_ast_guardrails.py --test --ast-strict`, and `uv run python backend_v2/seed/run_seed.py local`.</verification>
  </step>

  <test_contracts>
    <contract type="regression" name="test_entity_adapter_package_facade_reexports_all_symbols">
      Verifies that importing PostgresEntityAdapter, CANONICAL_SEED_TABLES, coercion helpers, and stage functions from backend_v2.database.postgres.entity_adapter works identically after replacing entity_adapter.py with entity_adapter/__init__.py.
    </contract>
    <contract type="positive" name="test_qgr017_modular_entity_adapter_package_allowed">
      Verifies that scanning backend_v2/database/postgres/entity_adapter/__init__.py and its 6 submodules produces zero QGR017 violations.
    </contract>
    <contract type="negative" name="test_qgr017_banned_entity_adapter_god_file_path_fatal">
      Verifies that scanning retired path backend_v2/database/postgres/entity_adapter.py triggers a FATAL QGR017 violation in QuorumGuardrailVisitor.
    </contract>
  </test_contracts>
</execution_protocol>
```
