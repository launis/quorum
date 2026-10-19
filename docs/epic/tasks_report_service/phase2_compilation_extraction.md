# Phase 2: Report Compilation Service Extraction

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## 1. Objective & Scope

Extract multi-format compilation and synthesis orchestration from `@[backend_v2/services/report_service.py#L272-L298]` (specifically: `compile_and_persist_artifact`, `process_artifact_compilation`, `_dispatch_report_compilation_dlq`) into [NEW] `@[backend_v2/services/report/compilation_service.py]`.

<test_contracts>
  <contract name="test_compile_and_persist_artifact_success">
    <input>Completed ExecutionRecord with valid blueprint</input>
    <expected>Compiles SDUI, PDF, XLSX, and CSV payloads, stores in FileDriver, and updates report status to COMPLETED.</expected>
    <category>regression</category>
  </contract>
  <contract name="test_compile_execution_not_ready">
    <input>ExecutionRecord in RUNNING status</input>
    <expected>ExecutionNotReadyError raised.</expected>
    <category>negative</category>
  </contract>
</test_contracts>

## 2. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="CREATE_COMPILATION_SUBMODULE">
    <action>Create target domain file [NEW] `@[backend_v2/services/report/compilation_service.py]` defining `ReportCompilationService` with dependencies `repo`, `storage_driver`, `export_service`, `pdf_service`, and `synthesis_runner`.</action>
    <action>Transplant `compile_and_persist_artifact`, `process_artifact_compilation`, and `_dispatch_report_compilation_dlq` verbatim.</action>
  </step>

  <step id="2" name="UPDATE_PROXY_REEXPORTS">
    <action>In `@[backend_v2/services/report_service.py]`, delegate compilation calls to `ReportCompilationService`.</action>
    <action>Run `uv run pytest backend_v2/tests/unit/services/test_report_service.py` to verify green baseline.</action>
  </step>
</execution_protocol>
```
