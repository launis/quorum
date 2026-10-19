# Phase 3: Report Format Reader Service Extraction

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## 1. Objective & Scope

Extract artifact storage retrieval, byte streaming, and tabular rows parsing from `@[backend_v2/services/report_service.py#L495-L534]` (specifically: `_read_artifact`, `get_report_sdui`, `get_report_pdf_bytes`, `get_report_excel_bytes`, `get_report_csv_bytes`, `get_report_rows`, `_dlq_log_absent_storage_artifact`) into [NEW] `@[backend_v2/services/report/format_reader_service.py]`.

<test_contracts>
  <contract name="test_get_report_sdui_success">
    <input>Existing report_id with stored SDUI payload</input>
    <expected>ReportDataDTO hydrated and returned fail-fast.</expected>
    <category>regression</category>
  </contract>
  <contract name="test_get_report_pdf_bytes_success">
    <input>Existing report_id with stored PDF artifact</input>
    <expected>Raw bytes returned matching PDF file contents.</expected>
    <category>regression</category>
  </contract>
</test_contracts>

## 2. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="CREATE_FORMAT_READER_SUBMODULE">
    <action>Create target domain file [NEW] `@[backend_v2/services/report/format_reader_service.py]` defining `ReportFormatReaderService`.</action>
    <action>Transplant `_read_artifact`, `get_report_sdui`, `get_report_pdf_bytes`, `get_report_excel_bytes`, `get_report_csv_bytes`, `get_report_rows`, and `_dlq_log_absent_storage_artifact` verbatim.</action>
  </step>

  <step id="2" name="UPDATE_PROXY_REEXPORTS">
    <action>In `@[backend_v2/services/report_service.py]`, delegate format retrieval operations to `ReportFormatReaderService`.</action>
    <action>Run `uv run pytest backend_v2/tests/unit/services/test_report_service.py` to verify green baseline.</action>
  </step>
</execution_protocol>
```
