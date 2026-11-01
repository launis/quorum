<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

# Phase 2: IAM, System Config & Studio Entities Stage Extraction (`phase2_iam_and_studio_entities_extraction.md`)

## 1. Objective
Execute Phase 2 of the Two-Epoch Strangler Fig decomposition for `@[backend_v2/database/postgres/entity_adapter.py]`:
1. Extract IAM (`organizations`, `users`) and `system_configs` SQL constants (`#L352-L441`) and row hydration, upsert, and get functions (`_hydrate_organization_row` `@[backend_v2/database/postgres/entity_adapter.py#L1302-L1327]`, `upsert_organization` `@[backend_v2/database/postgres/entity_adapter.py#L1329-L1361]`, `get_organization` `@[backend_v2/database/postgres/entity_adapter.py#L1363-L1383]`, `_hydrate_user_row` `@[backend_v2/database/postgres/entity_adapter.py#L1385-L1409]`, `upsert_user` `@[backend_v2/database/postgres/entity_adapter.py#L1411-L1439]`, `get_user` `@[backend_v2/database/postgres/entity_adapter.py#L1441-L1457]`, `_hydrate_system_config_row` `@[backend_v2/database/postgres/entity_adapter.py#L1459-L1497]`, `upsert_system_config` `@[backend_v2/database/postgres/entity_adapter.py#L1499-L1549]`, `get_system_config` `@[backend_v2/database/postgres/entity_adapter.py#L1551-L1567]`) into `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` (`< 380` lines).
2. Extract Studio `prompt_blocks` and `steps` SQL constants (`#L443-L552`) and row hydration, upsert, and get functions (`_hydrate_prompt_block_row` `@[backend_v2/database/postgres/entity_adapter.py#L1569-L1666]`, `upsert_prompt_block` `@[backend_v2/database/postgres/entity_adapter.py#L1668-L1741]`, `get_prompt_block` `@[backend_v2/database/postgres/entity_adapter.py#L1743-L1759]`, `_hydrate_step_row` `@[backend_v2/database/postgres/entity_adapter.py#L1761-L1799]`, `upsert_step` `@[backend_v2/database/postgres/entity_adapter.py#L1801-L1847]`, `get_step` `@[backend_v2/database/postgres/entity_adapter.py#L1849-L1865]`) into `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` (`< 400` lines).
3. Extract Studio `workflows` and `output_profiles` SQL constants (`#L554-L721`) and row hydration, upsert, and get functions (`_hydrate_workflow_row` `@[backend_v2/database/postgres/entity_adapter.py#L1867-L1905]`, `upsert_workflow` `@[backend_v2/database/postgres/entity_adapter.py#L1907-L1952]`, `get_workflow` `@[backend_v2/database/postgres/entity_adapter.py#L1954-L1970]`, `_hydrate_output_profile_row` `@[backend_v2/database/postgres/entity_adapter.py#L1972-L2025]`, `upsert_output_profile` `@[backend_v2/database/postgres/entity_adapter.py#L2027-L2090]`, `get_output_profile` `@[backend_v2/database/postgres/entity_adapter.py#L2092-L2108]`) into `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` (`< 430` lines).
4. Wire explicit redundant re-exports and method delegation in `@[backend_v2/database/postgres/entity_adapter.py]`, and create unit test suites `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`, `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`, and `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]`.

## 2. Scope & Target Boundaries

| Category | File Path & AST Boundaries | Responsibility |
| :--- | :--- | :--- |
| `[NEW]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` | SQL constants, row hydration, upsert, and get functions for `organizations`, `users`, and `system_configs` (`< 380` lines) |
| `[NEW]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` | SQL constants, row hydration, upsert, and get functions for `prompt_blocks` and `steps` (`< 400` lines) |
| `[NEW]` | `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` | SQL constants, row hydration, upsert, and get functions for `workflows` and `output_profiles` (`< 430` lines) |
| `[MODIFY]` | `@[backend_v2/database/postgres/entity_adapter.py]` | Replace IAM, SystemConfig, PromptBlock, Step, Workflow, and OutputProfile SQL constants (`#L352-L721`) and methods (`@[backend_v2/database/postgres/entity_adapter.py#L1569-L1666]`) with explicit redundant re-exports and delegation to the Phase 2 stage modules |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]` | Unit and negative boundary tests for `iam_and_system_stage.py` (`Organization`, `User`, `SystemConfig` upsert/get/hydration and driver error paths) |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]` | Unit and negative boundary tests for `prompt_block_and_step_stage.py` (`AnyPromptBlock`, `Step` upsert/get/hydration and driver error paths) |
| `[NEW]` | `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]` | Unit and negative boundary tests for `workflow_and_profile_stage.py` (`Workflow`, `OutputProfile` upsert/get/hydration, empty `variance_target_block`, and driver error paths) |

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
  <step id="1" name="Extract iam_and_system_stage.py, prompt_block_and_step_stage.py, and workflow_and_profile_stage.py">
    <constraint invariant="strangler_fig_mandate">Do NOT create backend_v2/database/postgres/entity_adapter/__init__.py during Phase 2 while backend_v2/database/postgres/entity_adapter.py exists on disk.</constraint>
    <constraint invariant="topological_leaf_first_extraction_mandate">Phase 2 stage modules may import ONLY from coercion_and_constants.py and external domain/database modules, NEVER from backend_v2.database.postgres.entity_adapter, and each MUST remain under 450 lines.</constraint>
    <action>
      1. Create `[NEW] @[backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py]` (`< 380` lines, all lines `<= 120` chars) with explicit `__all__`:
         - Relocate `_UPSERT_ORGANIZATION_SQL`, `_GET_ORGANIZATION_SQL`, `_LIST_ORGANIZATIONS_SQL` (`#L352-L381`), `_UPSERT_USER_SQL`, `_GET_USER_SQL`, `_LIST_USERS_SQL` (`#L383-L408`), and `_UPSERT_SYSTEM_CONFIG_SQL`, `_GET_SYSTEM_CONFIG_SQL`, `_LIST_SYSTEM_CONFIGS_SQL` (`#L410-L441`).
         - Extract `hydrate_organization_row`, `upsert_organization_row`, `get_organization_row` (`@[backend_v2/database/postgres/entity_adapter.py#L1329-L1361]`), `hydrate_user_row`, `upsert_user_row`, `get_user_row` (`@[backend_v2/database/postgres/entity_adapter.py#L1411-L1439]`), and `hydrate_system_config_row`, `upsert_system_config_row`, `get_system_config_row` (`@[backend_v2/database/postgres/entity_adapter.py#L1499-L1549]`).
      2. Create `[NEW] @[backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py]` (`< 400` lines, all lines `<= 120` chars) with explicit `__all__`:
         - Relocate `_UPSERT_PROMPT_BLOCK_SQL`, `_GET_PROMPT_BLOCK_SQL`, `_LIST_PROMPT_BLOCKS_SQL` (`#L443-L500`) and `_UPSERT_STEP_SQL`, `_GET_STEP_SQL`, `_LIST_STEPS_SQL` (`#L502-L552`).
         - Extract `hydrate_prompt_block_row`, `upsert_prompt_block_row`, `get_prompt_block_row` (`@[backend_v2/database/postgres/entity_adapter.py#L1569-L1666]`) and `hydrate_step_row`, `upsert_step_row`, `get_step_row` (`@[backend_v2/database/postgres/entity_adapter.py#L1801-L1847]`).
      3. Create `[NEW] @[backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py]` (`< 430` lines, all lines `<= 120` chars) with explicit `__all__`:
         - Relocate `_UPSERT_WORKFLOW_SQL`, `_GET_WORKFLOW_SQL`, `_LIST_WORKFLOWS_SQL` (`#L554-L614`) and `_UPSERT_OUTPUT_PROFILE_SQL`, `_GET_OUTPUT_PROFILE_SQL`, `_LIST_OUTPUT_PROFILES_SQL` (`#L616-L721`).
         - Extract `hydrate_workflow_row`, `upsert_workflow_row`, `get_workflow_row` (`@[backend_v2/database/postgres/entity_adapter.py#L1907-L1952]`) and `hydrate_output_profile_row`, `upsert_output_profile_row`, `get_output_profile_row` (`@[backend_v2/database/postgres/entity_adapter.py#L2027-L2090]`).
    </action>
  </step>

  <step id="2" name="Rewire Re-Exports and Delegation in entity_adapter.py and Add Unit Tests">
    <constraint invariant="explicit_reexport_mandate">Use explicit redundant import aliases (from module import Symbol as Symbol) in backend_v2/database/postgres/entity_adapter.py.</constraint>
    <action>
      1. Update `@[backend_v2/database/postgres/entity_adapter.py]` to re-export all Phase 2 SQL constants and stage functions using explicit redundant aliases (`Symbol as Symbol`) and delegate the 21 IAM, SystemConfig, PromptBlock, Step, Workflow, and OutputProfile methods on `PostgresEntityAdapter` (`@[backend_v2/database/postgres/entity_adapter.py#L921-L2515]`) to the Phase 2 stage modules.
      2. Create `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_iam_and_system_stage.py]`, `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_prompt_block_and_step_stage.py]`, and `[NEW] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_workflow_and_profile_stage.py]` covering positive CRUD roundtrips and negative `fetchrow` / `execute` fault and invalid prefix boundaries (including missed baseline lines `1456, 1566, 1758, 1864, 1969, 2045, 2107`).
    </action>
  </step>

  <step id="3" name="Run Phase 2 Verification and Quality Gate">
    <constraint invariant="zero_tolerance_audit_loop">Run backend_audit_loop.py with --test --ast-strict on all three Phase 2 stage modules and backend_v2/database/postgres/entity_adapter.py.</constraint>
    <action>
      1. Execute `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/iam_and_system_stage.py --test --ast-strict`.
      2. Execute `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/prompt_block_and_step_stage.py --test --ast-strict`.
      3. Execute `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/workflow_and_profile_stage.py --test --ast-strict`.
      4. Execute `uv run python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter.py --test --ast-strict` to verify all 18 baseline tests pass with `>= 90%` coverage.
    </action>
  </step>

  <test_contracts>
    <contract type="regression" name="test_iam_system_and_studio_entities_roundtrip_parity">
      Verifies that Organization, User, SystemConfig, AnyPromptBlock, Step, Workflow, and OutputProfile upsert and get roundtrips preserve 100% field parity.
    </contract>
    <contract type="positive" name="test_output_profile_empty_variance_target_block_hydration">
      Verifies that upsert_output_profile_row and hydrate_output_profile_row handle empty variance_target_block and null target_block_id columns accurately.
    </contract>
    <contract type="negative" name="test_stage_get_methods_translate_fetchrow_faults_to_app_exception">
      Verifies that get_user_row, get_system_config_row, get_prompt_block_row, get_step_row, get_workflow_row, and get_output_profile_row translate connection fetchrow errors into AppException(STORAGE_ACCESS_FAILED).
    </contract>
  </test_contracts>
</execution_protocol>
```
