# Phase 4: Atomic Cutover, Mechanical Consumer Rewiring & Proxy Deletion

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## 1. Objective & Scope

Rewire 1-hop consumer imports deterministically per `@[docs/epic/tasks_report_service/symbol_migration_map.md]`, create package facade [NEW] `@[backend_v2/services/report/__init__.py]`, atomically delete external proxy [DELETE] `@[backend_v2/services/report_service.py]`, and register AST Guardrail `QGR017`.

<test_contracts>
  <contract name="test_zero_legacy_report_service_imports">
    <input>Codebase-wide grep for `backend_v2.services.report_service`</input>
    <expected>0 remaining imports found.</expected>
    <category>regression</category>
  </contract>
  <contract name="test_package_facade_instantiation">
    <input>Import `from backend_v2.services.report import ReportService`</input>
    <expected>Successfully instantiates and routes to sub-services.</expected>
    <category>positive</category>
  </contract>
</test_contracts>

## 2. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="MECHANICAL_CONSUMER_IMPORT_REWIRING">
    <action>Rewire imports in `backend_v2/api/routers/execution/reports.py`, `backend_v2/workers/report_worker.py`, `backend_v2/workers/synthesis_worker.py`, and `backend_v2/workers/synthesis_reducers.py` to import from `backend_v2.services.report`.</action>
    <action>Split `backend_v2/tests/unit/services/test_report_service.py` into modular test suites: `test_report_lifecycle_service.py`, `test_report_compilation_service.py`, `test_report_format_reader_service.py`.</action>
  </step>

  <step id="2" name="ATOMIC_PACKAGE_CUTOVER_AND_PROXY_DELETION">
    <action>Create package aggregator facade [NEW] `@[backend_v2/services/report/__init__.py]` exposing `ReportService` with explicit `__all__ = ["ReportService"]`.</action>
    <action>Atomically delete external proxy [DELETE] `@[backend_v2/services/report_service.py]` from disk.</action>
    <action>Register retired path `backend_v2/services/report_service.py` in `@[scripts/_ast_guardrails.py]` under rule `QGR017`.</action>
    <action>Run `uv run python scripts/backend_audit_loop.py backend_v2/services/report/ --test` to confirm 100% green compilable state.</action>
  </step>
</execution_protocol>
```
