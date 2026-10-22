# Symbol Migration Map: ExportService Decomposition

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Overview
This document tracks the physical symbol mappings for decomposing monolithic `@[backend_v2/services/export_service.py#L62-L1123]` (1,124 lines) into the cohesive domain package `backend_v2/services/export/` following the Two-Epoch Strangler Fig Protocol.

---

## 1. Symbol-to-Target Sub-Module Inventory

| Original Symbol | Original Line Bound | Target Sub-Module | Public vs Private | Phase |
| :--- | :--- | :--- | :--- | :--- |
| `_build_matrix_atom_maps` | `@[backend_v2/services/export_service.py#L73-L91]` | `[NEW] @[backend_v2/services/export/metadata_resolver.py]` | `build_matrix_atom_maps` (Public helper) | Phase 1 |
| `_build_scale_metadata` | `@[backend_v2/services/export_service.py#L93-L125]` | `[NEW] @[backend_v2/services/export/metadata_resolver.py]` | `build_scale_metadata` (Public helper) | Phase 1 |
| `_resolve_matrix_label` | `@[backend_v2/services/export_service.py#L127-L203]` | `[NEW] @[backend_v2/services/export/metadata_resolver.py]` | `resolve_matrix_label` (Public helper) | Phase 1 |
| `_resolve_context_target` | `@[backend_v2/services/export_service.py#L205-L222]` | `[NEW] @[backend_v2/services/export/metadata_resolver.py]` | `resolve_context_target` (Public helper) | Phase 1 |
| `_extract_causal_result` | `@[backend_v2/services/export_service.py#L224-L266]` | `[NEW] @[backend_v2/services/export/metadata_resolver.py]` | `extract_causal_result` (Public helper) | Phase 1 |
| `_resolve_causal_meta` | `@[backend_v2/services/export_service.py#L268-L306]` | `[NEW] @[backend_v2/services/export/metadata_resolver.py]` | `resolve_causal_meta` (Public helper) | Phase 1 |
| `_apply_corporate_excel_styling` | `@[backend_v2/services/export_service.py#L308-L366]` | `[NEW] @[backend_v2/services/export/excel_styler.py]` | `apply_corporate_excel_styling` (Public helper) | Phase 1 |
| `_build_summary_dtos` | `@[backend_v2/services/export_service.py#L368-L446]` | `[NEW] @[backend_v2/services/export/summary_builder.py]` | `build_summary_dtos` (Public helper) | Phase 2 |
| `_build_atom_rows` | `@[backend_v2/services/export_service.py#L448-L618]` | `[NEW] @[backend_v2/services/export/atom_row_builder.py]` | `build_atom_rows` (Public helper) | Phase 2 |
| `_build_denormalized_rows` | `@[backend_v2/services/export_service.py#L620-L834]` | `[NEW] @[backend_v2/services/export/atom_row_builder.py]` | `build_denormalized_rows` (Public helper) | Phase 2 |
| `export_excel` | `@[backend_v2/services/export_service.py#L836-L999]` | `[NEW] @[backend_v2/services/export/excel_exporter.py]` | `ExcelExporter.export_excel` | Phase 3 |
| `export_flat_csv` | `@[backend_v2/services/export_service.py#L1001-L1123]` | `[NEW] @[backend_v2/services/export/csv_exporter.py]` | `CsvExporter.export_flat_csv` | Phase 3 |
| `ExportService` | `@[backend_v2/services/export_service.py#L62-L1123]` | `[NEW] @[backend_v2/services/export/__init__.py]` | `ExportService` (Package Facade) | Phase 4 |
| `export_service.py` | `@[backend_v2/services/export_service.py#L62-L1123]` | `[DELETE] @[backend_v2/services/export_service.py]` | Retired Monolith | Phase 4 |

---

## 2. 1-Hop Consumer Import Rewiring Plan

### Production Consumers

1. `@[backend_v2/services/report_service.py#L31]`
   - Current Import: `from backend_v2.services.export_service import ExportService`
   - Migrated Import: `from backend_v2.services.export import ExportService`
   - Usage:
     - `self.export_service.export_excel(...)`
     - `self.export_service.export_flat_csv(...)`
   - Action: Update import statement in Phase 4 Cutover Step 1.

2. `@[backend_v2/api/dependencies.py#L58]`
   - Current Import: `from backend_v2.services.export_service import ExportService`
   - Migrated Import: `from backend_v2.services.export import ExportService`
   - Usage:
     - `get_export_service(...) -> ExportService`
     - `ExportServiceDep = Annotated[ExportService, Depends(get_export_service)]`
   - Action: Update import statement in Phase 4 Cutover Step 1.

### Test Consumers

1. `@[backend_v2/tests/unit/test_report_headers_l10n_parity.py#L28]`
   - Current Import: `from backend_v2.services.export_service import ExportService`
   - Migrated Import: `from backend_v2.services.export import ExportService`
   - Usage: Instantiate `ExportService()` to verify header parity.
   - Action: Update import statement in Phase 4 Cutover Step 1.

2. `@[backend_v2/tests/unit/services/test_export_service.py]` (2,194 lines monolithic test file)
   - Current Import: `from backend_v2.services.export_service import ExportService`
   - Modularization Plan: Decompose into 7 focused unit test suites:
     - `[NEW] @[backend_v2/tests/unit/services/export/test_metadata_resolver.py]`
     - `[NEW] @[backend_v2/tests/unit/services/export/test_excel_styler.py]`
     - `[NEW] @[backend_v2/tests/unit/services/export/test_summary_builder.py]`
     - `[NEW] @[backend_v2/tests/unit/services/export/test_atom_row_builder.py]`
     - `[NEW] @[backend_v2/tests/unit/services/export/test_excel_exporter.py]`
     - `[NEW] @[backend_v2/tests/unit/services/export/test_csv_exporter.py]`
     - `[NEW] @[backend_v2/tests/unit/services/export/test_export_facade.py]`
   - Action: Execute modularization in Phase 4 Cutover Step 1 while preserving 100% test coverage.
