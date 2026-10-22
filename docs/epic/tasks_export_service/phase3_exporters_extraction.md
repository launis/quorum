# Phase 3 Implementation Plan: Excel & CSV Exporters Extraction

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Objective
Extract Excel and CSV binary streaming exporter routines from monolithic `@[backend_v2/services/export_service.py#L65-L589]` into dedicated single-responsibility sub-modules `[NEW] @[backend_v2/services/export/excel_exporter.py]` and `[NEW] @[backend_v2/services/export/csv_exporter.py]` under Epoch 1 (Pure Structural Lift-and-Shift) with zero behavioral changes, maintaining 100% green unit test coverage across the temporary proxy.

## Scope & Target Boundaries
- `[NEW] @[backend_v2/services/export/excel_exporter.py]` (Extract `ExcelExporter.export_excel`)
- `[NEW] @[backend_v2/services/export/csv_exporter.py]` (Extract `CsvExporter.export_flat_csv`)
- `[MODIFY] @[backend_v2/services/export_service.py#L302-L465]` (Delegate `export_excel` to `excel_exporter`)
- `[MODIFY] @[backend_v2/services/export_service.py#L467-L589]` (Delegate `export_flat_csv` to `csv_exporter`)

```xml
<execution_protocol>
  <step id="1" name="CREATE_EXCEL_EXPORTER_SUBMODULE">
    <action>Create `[NEW] @[backend_v2/services/export/excel_exporter.py]` encapsulating `ExcelExporter.export_excel` lifted verbatim from `@[backend_v2/services/export_service.py#L302-L465]`.</action>
    <action>Implement `__init__(self, prompt_block_repo: IPromptBlockRepository | None = None) -> None:` storing repository reference.</action>
    <action>Import collaborating builders: `build_summary_dtos` from `backend_v2.services.export.summary_builder`, `build_atom_rows` from `backend_v2.services.export.atom_row_builder`, `apply_corporate_excel_styling` from `backend_v2.services.export.excel_styler`, and `extract_causal_result` from `backend_v2.services.export.metadata_resolver`.</action>
    <action>Preserve exact openpyxl workbook creation, 13-column summary rows, 14-column atom rows, RFC 7807 error logging, and `ExportPayloadDTO` return with MIME type `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`.</action>
    <constraint invariant="binary_streaming_purity">Excel export output MUST be strictly typed ExportPayloadDTO containing valid openpyxl bytes and canonical filename.</constraint>
    <constraint invariant="zero_behavioral_change">Preserve exact error codes (400 on unpassed/empty, 500 on write failure), sheet names, and column headers.</constraint>
  </step>

  <step id="2" name="CREATE_CSV_EXPORTER_SUBMODULE">
    <action>Create `[NEW] @[backend_v2/services/export/csv_exporter.py]` encapsulating `CsvExporter.export_flat_csv` lifted verbatim from `@[backend_v2/services/export_service.py#L467-L589]`.</action>
    <action>Implement `__init__(self, prompt_block_repo: IPromptBlockRepository | None = None) -> None:` storing repository reference.</action>
    <action>Import collaborating builders: `build_denormalized_rows` from `backend_v2.services.export.atom_row_builder`, `extract_causal_result` from `backend_v2.services.export.metadata_resolver`, and `ReportHeaderResolver` from `backend_v2.services.localization`.</action>
    <action>Preserve exact 22 denormalized CSV column ordering, UTF-8-SIG byte encoding, RFC 7807 error logging, and `ExportPayloadDTO` return with MIME type `text/csv`.</action>
    <constraint invariant="single_pipeline_streaming">CSV streaming MUST consume rectangular flat rows directly from atom_row_builder without duplicating traversal or projection logic.</constraint>
    <constraint invariant="zero_behavioral_change">Preserve exact 22-column denormalized ordering, utf-8-sig encoding, and MIME type.</constraint>
  </step>

  <step id="3" name="PROXY_DELEGATION_IN_EXPORT_SERVICE">
    <action>In `@[backend_v2/services/export_service.py#L65-L589]`, import `ExcelExporter` from `backend_v2.services.export.excel_exporter` and `CsvExporter` from `backend_v2.services.export.csv_exporter`.</action>
    <action>Replace `export_excel` method body at lines 302-465 with 1-line delegation: `return await ExcelExporter(self.prompt_block_repo).export_excel(...)`.</action>
    <action>Replace `export_flat_csv` method body at lines 467-589 with 1-line delegation: `return await CsvExporter(self.prompt_block_repo).export_flat_csv(...)`.</action>
    <action>Maintain identical public method signatures and docstrings on `ExportService` to guarantee existing unit tests remain 100% green.</action>
    <constraint invariant="strangler_fig_proxy">DO NOT delete export_service.py or create backend_v2/services/export/__init__.py in Phase 3 to prevent duplicate module collisions while export_service.py is active.</constraint>
  </step>

  <step id="4" name="VERIFY_QUALITY_GATES">
    <action>Create dedicated unit test files: `[NEW] @[backend_v2/tests/unit/services/export/test_excel_exporter.py]` and `[NEW] @[backend_v2/tests/unit/services/export/test_csv_exporter.py]`.</action>
    <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/export_service.py --test`.</action>
    <action>Verify all 39 existing unit tests in `test_export_service.py` pass and all 10 audit stages remain 100% green.</action>
    <constraint invariant="coverage_and_quality_gate">Test coverage across export_service.py and all extracted sub-modules MUST remain >= 90% with 0 warnings.</constraint>
  </step>
</execution_protocol>
```

<test_contracts>
  <regression>
    - `test_export_excel_existing_contract_parity`: Verify workbook sheets, summary rows, and raw data atoms match baseline output.
    - `test_export_flat_csv_existing_contract_parity`: Verify 22-column CSV stream matches baseline byte content.
    - `test_export_excel_includes_causal_propositions`: Verify dynamic causal graph propositions stream into Tab 2 with metrics.
    - `test_export_csv_includes_causal_and_ml_columns`: Verify CSV flat stream includes causal metadata and ML indicators.
  </regression>
  <positive>
    - `test_excel_exporter_direct_call`: Verify `ExcelExporter` generates valid `.xlsx` payload directly.
    - `test_csv_exporter_direct_call`: Verify `CsvExporter` generates valid `.csv` payload directly.
  </positive>
  <negative>
    - `test_export_excel_unpassed_execution_fails`: Verify `export_excel` raises 400 `AppException` when execution status is not PASSED.
    - `test_export_excel_no_scoreable_atoms_fails`: Verify `export_excel` raises 400 `AppException` when report_dto has no scoreable atoms.
    - `test_export_excel_no_matrices_fails`: Verify `export_excel` raises 400 `AppException` when matrices list is empty.
    - `test_export_flat_csv_unpassed_execution_fails`: Verify `export_flat_csv` raises 400 `AppException` when execution status is not PASSED.
    - `test_export_flat_csv_no_scoreable_atoms_fails`: Verify `export_flat_csv` raises 400 `AppException` when report_dto has no scoreable atoms.
  </negative>
</test_contracts>
