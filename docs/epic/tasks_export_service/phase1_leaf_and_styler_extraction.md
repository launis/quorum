# Phase 1 Implementation Plan: Leaf Metadata Resolver & Excel Styler Extraction

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Objective
Extract depth-0 leaf metadata resolution functions and openpyxl corporate styling routines from monolithic `@[backend_v2/services/export_service.py#L62-L1123]` into dedicated single-responsibility sub-modules `[NEW] @[backend_v2/services/export/metadata_resolver.py]` and `[NEW] @[backend_v2/services/export/excel_styler.py]` under Epoch 1 (Pure Structural Lift-and-Shift) with zero behavioral changes.

## Scope & Target Boundaries
- `[NEW] @[backend_v2/services/export/metadata_resolver.py]` (Extract `_build_matrix_atom_maps`, `_build_scale_metadata`, `_resolve_matrix_label`, `_resolve_context_target`, `_extract_causal_result`, `_resolve_causal_meta`)
- `[NEW] @[backend_v2/services/export/excel_styler.py]` (Extract `_apply_corporate_excel_styling`)
- `[MODIFY] @[backend_v2/services/export_service.py#L73-L91]` (Delegate `_build_matrix_atom_maps` to `metadata_resolver`)
- `[MODIFY] @[backend_v2/services/export_service.py#L93-L125]` (Delegate `_build_scale_metadata` to `metadata_resolver`)
- `[MODIFY] @[backend_v2/services/export_service.py#L127-L203]` (Delegate `_resolve_matrix_label` to `metadata_resolver`)
- `[MODIFY] @[backend_v2/services/export_service.py#L205-L222]` (Delegate `_resolve_context_target` to `metadata_resolver`)
- `[MODIFY] @[backend_v2/services/export_service.py#L224-L266]` (Delegate `_extract_causal_result` to `metadata_resolver`)
- `[MODIFY] @[backend_v2/services/export_service.py#L268-L306]` (Delegate `_resolve_causal_meta` to `metadata_resolver`)
- `[MODIFY] @[backend_v2/services/export_service.py#L308-L366]` (Delegate `_apply_corporate_excel_styling` to `excel_styler`)

```xml
<execution_protocol>
  <step id="1" name="CREATE_METADATA_RESOLVER_SUBMODULE">
    <action>Create `[NEW] @[backend_v2/services/export/metadata_resolver.py]` containing the 6 pure metadata resolution functions lifted verbatim from `export_service.py`.</action>
    <action>Export public functions: `build_matrix_atom_maps`, `build_scale_metadata`, `resolve_matrix_label`, `resolve_context_target`, `extract_causal_result`, and `resolve_causal_meta`.</action>
    <action>Preserve exact parameter types, return annotations, logging statements, and `AppException` error codes with zero signature mutations.</action>
    <constraint invariant="pure_compute_leaf">`metadata_resolver.py` MUST remain a stateless compute module without database session mutations or external network calls.</constraint>
  </step>

  <step id="2" name="CREATE_EXCEL_STYLER_SUBMODULE">
    <action>Create `[NEW] @[backend_v2/services/export/excel_styler.py]` containing `apply_corporate_excel_styling` lifted verbatim from `@[backend_v2/services/export_service.py#L308-L366]`.</action>
    <action>Isolate openpyxl styles: `PatternFill`, `Font`, `Side`, `Border`, `Alignment`, and `get_column_letter`.</action>
    <constraint invariant="presentation_styling_isolation">`excel_styler.py` MUST depend exclusively on `openpyxl` without importing other export domain modules.</constraint>
  </step>

  <step id="3" name="PROXY_DELEGATION_IN_EXPORT_SERVICE">
    <action>In `@[backend_v2/services/export_service.py#L62-L1123]`, replace method bodies of `_build_matrix_atom_maps`, `_build_scale_metadata`, `_resolve_matrix_label`, `_resolve_context_target`, `_extract_causal_result`, `_resolve_causal_meta`, and `_apply_corporate_excel_styling` with direct 1-line delegations to the newly extracted sub-modules.</action>
    <action>Maintain identical `@staticmethod` and `@classmethod` signatures on `ExportService` to guarantee existing unit tests remain 100% green.</action>
    <constraint invariant="strangler_fig_proxy">DO NOT create `backend_v2/services/export/__init__.py` in Phase 1 to prevent Python duplicate module collisions while `export_service.py` exists.</constraint>
  </step>

  <step id="4" name="VERIFY_QUALITY_GATES">
    <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/export_service.py --test`.</action>
    <action>Verify all 39 unit tests pass and all 10 audit stages remain 100% green.</action>
  </step>
</execution_protocol>
```

<test_contracts>
  <regression>
    - `test_build_matrix_atom_maps_existing_parity`: Verify atom-to-matrix and atom-to-scorecard lookup returns identical dictionaries.
    - `test_resolve_matrix_label_existing_parity`: Verify localized matrix label resolution matches authoritative scorecard names.
    - `test_resolve_context_target_existing_parity`: Verify context target fallback string resolution.
    - `test_extract_causal_result_existing_parity`: Verify extraction of `CausalTdaFusionResultDTO` and `CausalGraphPayloadDTO` from trace and step states.
    - `test_resolve_causal_meta_existing_parity`: Verify causal status tagging ('orphan', 'validated', 'cascading_fault', 'root_cause').
    - `test_apply_corporate_excel_styling_existing_parity`: Verify header fill, zebra fill, borders, and column auto-width calculation on openpyxl workbook.
  </regression>
  <positive>
    - `test_metadata_resolver_direct_import`: Verify direct import and invocation of `build_matrix_atom_maps` from `backend_v2.services.export.metadata_resolver`.
    - `test_excel_styler_direct_import`: Verify direct import and invocation of `apply_corporate_excel_styling` from `backend_v2.services.export.excel_styler`.
  </positive>
  <negative>
    - `test_resolve_matrix_label_missing_block_raises_not_found`: Verify `resolve_matrix_label` raises `AppException` with `ErrorCodes.RESOURCE_NOT_FOUND` (status 404) when matrix definition is missing.
    - `test_extract_causal_result_none_input_returns_none`: Verify `extract_causal_result` safely returns `None` when `ExecutionRecord` is `None` or contains no causal nodes.
  </negative>
</test_contracts>
