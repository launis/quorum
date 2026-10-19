# Phase 1: Report Lifecycle Service Extraction

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

## 1. Objective & Scope

Extract CRUD and lifecycle operations from `@[backend_v2/services/report_service.py#L70-L91]` (specifically: `get_report`, `list_reports_for_execution`, `create_report_artifact`, `get_or_create_default_artifact`, `delete_report_artifact`, `regenerate_report_artifact`, `get_public_report`) into a dedicated sub-module [NEW] `@[backend_v2/services/report/lifecycle_service.py]` with 100% behavioral invariance and zero signature mutations.

<test_contracts>
  <contract name="test_get_report_success">
    <input>Existing report_id "rep_1234567890abcdef"</input>
    <expected>ReportArtifact instance returned matching repository state.</expected>
    <category>regression</category>
  </contract>
  <contract name="test_get_report_not_found">
    <input>Non-existent report_id "rep_0000000000000000"</input>
    <expected>ResourceNotFoundError raised with ErrorCodes.RESOURCE_NOT_FOUND.</expected>
    <category>negative</category>
  </contract>
  <contract name="test_create_report_artifact_persists_model">
    <input>Valid ReportArtifactCreateDTO payload</input>
    <expected>ReportArtifact created, saved in repository, and returned with Opaque Stripe ID.</expected>
    <category>positive</category>
  </contract>
</test_contracts>

## 2. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="CREATE_LIFECYCLE_SUBMODULE">
    <action>Create target domain file [NEW] `@[backend_v2/services/report/lifecycle_service.py]` defining `ReportLifecycleService` with dependencies `repo: IUnifiedWorkflowRepository`.</action>
    <action>Transplant `get_report`, `list_reports_for_execution`, `create_report_artifact`, `get_or_create_default_artifact`, `delete_report_artifact`, `regenerate_report_artifact`, and `get_public_report` with verbatim signatures and logic.</action>
  </step>

  <step id="2" name="UPDATE_PROXY_REEXPORTS">
    <action>In `@[backend_v2/services/report_service.py]`, instantiate `ReportLifecycleService` inside `ReportService.__init__` and delegate the extracted methods as 1-line proxy delegations.</action>
    <action>Verify zero duplicate module collisions and run `uv run pytest backend_v2/tests/unit/services/test_report_service.py` to ensure 100% green baseline.</action>
  </step>
</execution_protocol>
```
