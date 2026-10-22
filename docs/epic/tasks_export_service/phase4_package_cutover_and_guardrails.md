# Phase 4 Implementation Plan: Atomic Package Cutover & Guardrails Lockdown (Header Placeholder)

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
</required_context_rules>

## Objective
Execute the Atomic Package Cutover for `ExportService`: atomically replace external proxy `[DELETE] @[backend_v2/services/export_service.py]` with canonical package facade `[NEW] @[backend_v2/services/export/__init__.py]`, rewire 1-hop consumer imports per `symbol_migration_map.md`, modularize the test suite into per-submodule test files, register the retired monolith path under AST Guardrail `QGR017` in `@[scripts/_ast_guardrails.py#L1879-L1935]`, and synchronize `@[.agents/rules/04_directory_reference.md]`. Detailed execution steps will be fully expanded by re-invoking `/tier3-god-code-decomposition` after Phase 2 completes.

## Scope & Target Boundaries
- `[NEW] @[backend_v2/services/export/__init__.py]` (Canonical package facade)
- `[DELETE] @[backend_v2/services/export_service.py]` (External proxy deleted)
- `[MODIFY] @[backend_v2/services/report_service.py#L42-L749]` (Rewire import to `backend_v2.services.export`)
- `[MODIFY] @[backend_v2/api/dependencies.py#L462-L473]` (Rewire import to `backend_v2.services.export`)
- `[MODIFY] @[scripts/_ast_guardrails.py#L1879-L1935]` (Register `backend_v2/services/export_service.py` under `QGR017`)
- `[MODIFY] @[.agents/rules/04_directory_reference.md]` (Update directory reference documentation)

```xml
<execution_protocol>
  <step id="1" name="FULL_STRANGLER_REINVOCATION_GATE">
    <action>Re-invoke `/tier3-god-code-decomposition backend_v2/services/export_service.py` upon completion of Phase 2 to hydrate detailed execution instructions for Phase 3 and Phase 4.</action>
    <constraint invariant="context_preservation">Do not execute cutover before Phase 1, Phase 2, and Phase 3 are 100% verified.</constraint>
  </step>

  <step id="2" name="CONSUMER_IMPORT_REWIRING">
    <action>Rewire 1-hop consumer imports in `backend_v2/services/report_service.py` and `backend_v2/api/dependencies.py` from `backend_v2.services.export_service` to `backend_v2.services.export`.</action>
    <constraint invariant="zero_behavioral_change">Maintain identical public signatures and return types on all consumers.</constraint>
  </step>

  <step id="3" name="MODULARIZE_TEST_SUITE">
    <action>Decompose monolithic `backend_v2/tests/unit/services/test_export_service.py` into focused sub-module test files under `backend_v2/tests/unit/services/export/`.</action>
    <constraint invariant="test_coverage_preservation">Maintain minimum 90% test coverage across all newly created sub-modules.</constraint>
  </step>

  <step id="4" name="ATOMIC_PACKAGE_CUTOVER">
    <action>Atomically create `backend_v2/services/export/__init__.py` and delete `backend_v2/services/export_service.py` in a single step.</action>
    <action>Verify zero remaining imports of `backend_v2.services.export_service` across the codebase.</action>
  </step>

  <step id="5" name="GUARDRAIL_LOCKDOWN_AND_SMOKE_TEST">
    <action>Register `backend_v2/services/export_service.py` in `scripts/_ast_guardrails.py` under `QGR017` banning future proxy regressions.</action>
    <action>Update directory reference in `.agents/rules/04_directory_reference.md`.</action>
    <action>Execute `uv run python scripts/backend_audit_loop.py backend_v2/services/export/ --test`.</action>
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
