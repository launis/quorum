# Phase 3 Implementation Plan: Excel & CSV Exporters Extraction (Header Placeholder)

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Objective
Extract Excel and CSV binary streaming exporter routines from monolithic `@[backend_v2/services/export_service.py#L62-L1123]` into dedicated sub-modules `[NEW] @[backend_v2/services/export/excel_exporter.py]` and `[NEW] @[backend_v2/services/export/csv_exporter.py]` under Epoch 1 (Pure Structural Lift-and-Shift) with zero behavioral changes. Detailed execution steps will be fully expanded by re-invoking `/tier3-god-code-decomposition` after Phase 2 completes.

## Scope & Target Boundaries
- `[NEW] @[backend_v2/services/export/excel_exporter.py]` (Extract `export_excel`)
- `[NEW] @[backend_v2/services/export/csv_exporter.py]` (Extract `export_flat_csv`)
- `[MODIFY] @[backend_v2/services/export_service.py#L836-L999]` (Delegate `export_excel` to `excel_exporter`)
- `[MODIFY] @[backend_v2/services/export_service.py#L1001-L1123]` (Delegate `export_flat_csv` to `csv_exporter`)

```xml
<execution_protocol>
  <step id="1" name="FULL_STRANGLER_REINVOCATION_GATE">
    <action>Re-invoke `/tier3-god-code-decomposition backend_v2/services/export_service.py` upon completion of Phase 2 to hydrate detailed execution instructions for Phase 3 and Phase 4.</action>
    <constraint invariant="context_preservation">Do not manually guess implementation details before Phase 1 and Phase 2 are verified.</constraint>
  </step>

  <step id="2" name="CREATE_EXCEL_EXPORTER_SUBMODULE">
    <action>Create `[NEW] @[backend_v2/services/export/excel_exporter.py]` encapsulating `ExcelExporter.export_excel` with openpyxl workbook creation and RFC 7807 error logging.</action>
    <constraint invariant="zero_behavioral_change">Preserve exact error codes, MIME types, and return DTO schema.</constraint>
  </step>

  <step id="3" name="CREATE_CSV_EXPORTER_SUBMODULE">
    <action>Create `[NEW] @[backend_v2/services/export/csv_exporter.py]` encapsulating `CsvExporter.export_flat_csv` streaming UTF-8-SIG CSV content.</action>
    <constraint invariant="zero_behavioral_change">Preserve exact 22-column denormalized ordering and MIME type.</constraint>
  </step>

  <step id="4" name="PROXY_DELEGATION_AND_QUALITY_GATE">
    <action>In `@[backend_v2/services/export_service.py#L62-L1123]`, delegate `export_excel` and `export_flat_csv` to the new exporter sub-modules.</action>
    <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/export_service.py --test`.</action>
  </step>
</execution_protocol>
```

<test_contracts>
  <regression>
    - `test_export_excel_existing_contract_parity`: Verify workbook sheets, summary rows, and raw data atoms match baseline output.
    - `test_export_flat_csv_existing_contract_parity`: Verify 22-column CSV stream matches baseline byte content.
  </regression>
  <positive>
    - `test_excel_exporter_direct_call`: Verify `ExcelExporter` generates valid `.xlsx` payload.
    - `test_csv_exporter_direct_call`: Verify `CsvExporter` generates valid `.csv` payload.
  </positive>
  <negative>
    - `test_export_excel_unpassed_execution_fails`: Verify `export_excel` raises 400 `AppException` when execution status is not PASSED.
    - `test_export_flat_csv_unpassed_execution_fails`: Verify `export_flat_csv` raises 400 `AppException` when execution status is not PASSED.
  </negative>
</test_contracts>
