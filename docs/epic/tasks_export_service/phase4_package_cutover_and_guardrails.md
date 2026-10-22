# Phase 4 Implementation Plan: Atomic Package Cutover & Guardrails Lockdown

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Objective
Execute the Atomic Package Cutover for `ExportService`: atomically replace external proxy `[DELETE] @[backend_v2/services/export_service.py]` with canonical package facade `[NEW] @[backend_v2/services/export/__init__.py]`, rewire 1-hop consumer imports per `symbol_migration_map.md`, modularize the test suite into per-submodule test files, register the retired monolith path under AST Guardrail `QGR017` in `@[scripts/_ast_guardrails.py#L1879-L1935]`, and synchronize `@[.agents/rules/04_directory_reference.md]`.

## Scope & Target Boundaries
- `[NEW] @[backend_v2/services/export/__init__.py]` (Canonical package facade)
- `[DELETE] @[backend_v2/services/export_service.py]` (External proxy deleted)
- `[MODIFY] @[backend_v2/services/report_service.py#L42-L749]` (Rewire import to `backend_v2.services.export`)
- `[MODIFY] @[backend_v2/api/dependencies.py#L462-L473]` (Rewire import to `backend_v2.services.export`)
- `[MODIFY] @[scripts/_ast_guardrails.py#L1879-L1935]` (Register `backend_v2/services/export_service.py` under `QGR017`)
- `[MODIFY] @[.agents/rules/04_directory_reference.md]` (Update directory reference documentation)

```xml
<execution_protocol>
  <step id="1" name="CONSUMER_IMPORT_REWIRING">
    <action>In `@[backend_v2/services/report_service.py#L42-L749]`, update import from `backend_v2.services.export_service` to `backend_v2.services.export`.</action>
    <action>In `@[backend_v2/api/dependencies.py#L462-L473]`, update import from `backend_v2.services.export_service` to `backend_v2.services.export`.</action>
    <action>In `@[backend_v2/tests/unit/test_report_headers_l10n_parity.py]`, update import to `backend_v2.services.export`.</action>
    <constraint invariant="zero_behavioral_change">Maintain identical public signatures and return types on all consumers.</constraint>
  </step>

  <step id="2" name="MODULARIZE_TEST_SUITE">
    <action>Decompose monolithic `backend_v2/tests/unit/services/test_export_service.py` (2,194 lines) into 7 focused sub-module test files under `backend_v2/tests/unit/services/export/`: `test_metadata_resolver.py`, `test_excel_styler.py`, `test_summary_builder.py`, `test_atom_row_builder.py`, `test_excel_exporter.py`, `test_csv_exporter.py`, and `test_export_facade.py`.</action>
    <action>Delete monolithic `backend_v2/tests/unit/services/test_export_service.py` once tests are redistributed.</action>
    <constraint invariant="test_coverage_preservation">Maintain minimum 90% test coverage across all newly created sub-modules.</constraint>
  </step>

  <step id="3" name="ATOMIC_PACKAGE_CUTOVER">
    <action>Atomically create `[NEW] @[backend_v2/services/export/__init__.py]` declaring `ExportService` package facade wiring sub-modules via dependency injection, exporting canonical `__all__` list with explicit redundant aliases.</action>
    <action>Physically delete `[DELETE] @[backend_v2/services/export_service.py]` in the same atomic step.</action>
    <action>Verify zero remaining imports of `backend_v2.services.export_service` across the codebase.</action>
    <constraint invariant="two_phase_package_strangler">Deleting export_service.py and creating export/__init__.py MUST occur in a single atomic step to prevent duplicate module collisions in Python/MyPy.</constraint>
  </step>

  <step id="4" name="GUARDRAIL_LOCKDOWN_AND_SMOKE_TEST">
    <action>Register `backend_v2/services/export_service.py` in `@[scripts/_ast_guardrails.py#L1879-L1935]` under `QGR017` banning future proxy regressions.</action>
    <action>Update directory reference in `@[.agents/rules/04_directory_reference.md]`.</action>
    <action>Execute `uv run python backend_v2/seed/run_seed.py local` to verify clean database boot and seed integrity.</action>
    <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/export/ --test`.</action>
    <constraint invariant="qgr017_lockdown">QGR017 MUST flag any future import from backend_v2.services.export_service at unconditional FATAL severity.</constraint>
  </step>
</execution_protocol>
```

<test_contracts>
  <regression>
    - `test_package_facade_export_excel_parity`: Verify `ExportService.export_excel` via package facade matches original output.
    - `test_package_facade_export_flat_csv_parity`: Verify `ExportService.export_flat_csv` via package facade matches original output.
    - `test_report_service_integration_parity`: Verify `ReportService` consumes new `ExportService` package without regressions.
  </regression>
  <positive>
    - `test_qgr017_flags_legacy_import`: Verify `_ast_guardrails.py` raises fatal `QGR017` on any import from `backend_v2.services.export_service`.
    - `test_all_submodules_clean_imports`: Verify `metadata_resolver`, `excel_styler`, `summary_builder`, `atom_row_builder`, `excel_exporter`, `csv_exporter`, and `__init__` import cleanly without circular dependencies.
  </positive>
  <negative>
    - `test_export_facade_invalid_params_raises_validation_error`: Verify package facade preserves fail-fast exception handling on missing parameters.
  </negative>
</test_contracts>
