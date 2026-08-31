<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
  <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_provider_agnostic_caching.md]</knowledge_item>
  <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
</required_context_rules>

# Phase 2A: Service Layer & Progress Tracking DTO Modernization

## Overview

Eliminate all `dict[str, Any]` annotations from internal service progress tracking, task registries, and core services. Refine `ProgressState` in `backend_v2/services/progress.py` to eliminate raw dictionaries while ensuring that database updates strictly adhere to `ExecutionRecord` field contracts to preserve 1:1 cross-domain serialization parity with Flutter client's SSE streaming consumer. Define co-located `TaskMetadataDTO` in `backend_v2/core/registry.py` and modernize coupled service test suites.

## Target Files

- `[MODIFY]` `@[backend_v2/services/progress.py]`
- `[MODIFY]` `@[backend_v2/core/registry.py]`
- `[MODIFY]` `@[backend_v2/services/execution.py]`
- `[MODIFY]` `@[backend_v2/services/llm_task_executor.py]`
- `[MODIFY]` `@[backend_v2/services/flattener.py]`
- `[MODIFY]` `@[backend_v2/services/mcp/mcp_tool_loop.py]`
- `[MODIFY]` `@[backend_v2/utils/redis_patcher.py]`
- `[MODIFY]` `@[backend_v2/utils/dict_utils.py]`
- `[MODIFY]` `@[backend_v2/models/dtos/system.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_progress.py]`
- `[MODIFY]` `@[backend_v2/tests/unit/core/test_registry.py]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 2: Service & Studio Layer DTO Elimination]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/services/progress.py]</backend>
      <backend>@[backend_v2/core/registry.py]</backend>
      <backend>@[backend_v2/services/execution.py]</backend>
      <backend>@[backend_v2/services/llm_task_executor.py]</backend>
      <backend>@[backend_v2/services/flattener.py]</backend>
      <backend>@[backend_v2/services/mcp/mcp_tool_loop.py]</backend>
      <backend>@[backend_v2/utils/redis_patcher.py]</backend>
      <backend>@[backend_v2/utils/dict_utils.py]</backend>
      <backend>@[backend_v2/models/dtos/system.py]</backend>
    </touched_artifacts>
  </metadata>

  <contract_freeze>
    <interface id="ProgressState">
      class ProgressState(BaseModel):
          model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
          status: str
          timestamp: str
          current_step: str | None = None
          progress: int | None = None
          error: str | None = None
    </interface>
    <interface id="TaskMetadataDTO">
      class TaskMetadataDTO(BaseModel):
          model_config = ConfigDict(strict=True, extra="forbid", frozen=True)
          category: str | None = None
          description: str | None = None
          timeout_seconds: int | None = None
          tags: list[str] | None = None
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/hooks/]</file>
    <file>@[backend_v2/services/orchestrator/]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item>ProgressState refined with ConfigDict(strict=True, extra="forbid", frozen=True), zero raw dict[str, Any] fields</item>
    <item>DatabaseProgressTracker updates conform strictly to ExecutionRecord schema</item>
    <item>TaskMetadataDTO defined in registry.py and TaskDefinition.metadata typed strictly</item>
    <item>redis_patcher.py hasattr reflection eliminated via typed FakeRedis class</item>
    <item>All unit tests in test_progress.py and test_registry.py pass with 100% green coverage</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify that Phase 1 quality gates pass cleanly across models and LLM adapters.</action>
    <action>Inspect backend_v2/services/progress.py and backend_v2/core/registry.py.</action>
  </step>

  <step id="1" name="PRE-IMPLEMENTATION CLEANUPS">
    <action>In @[backend_v2/utils/redis_patcher.py], eliminate 7 hasattr() reflection calls by creating a strongly typed FakeRedis mock class.</action>
    <action>In @[backend_v2/utils/dict_utils.py], verify callers and mark internal persistence helper boundaries.</action>
    <action>In @[backend_v2/models/dtos/system.py#L49], add explicit transport boundary classification comment to ClientErrorPayload.context_data: dict[str, Any].</action>
  </step>

  <step id="2" name="MODERNIZE PROGRESS STATE & TRACKER INTERFACES">
    <action>In @[backend_v2/services/progress.py], refine ProgressState to eliminate 30 dict[str, Any] annotations (result: dict[str, Any] and details: dict[str, Any]).</action>
    <action>Refactor ProgressTracker ABC, DatabaseProgressTracker, and InMemoryProgressTracker to use typed ProgressState contracts.</action>
    <action>Ensure DatabaseProgressTracker database updates strictly adhere to ExecutionRecord fields (status, current_step, progress, error).</action>
    <action>In @[backend_v2/services/execution.py], eliminate remaining 6 dict[str, Any] annotations while locking stream_status SSE generator to canonical ExecutionRecord.</action>
    <action>In @[backend_v2/services/llm_task_executor.py], @[backend_v2/services/flattener.py], and @[backend_v2/services/mcp/mcp_tool_loop.py], eliminate remaining dict[str, Any] annotations.</action>
  </step>

  <step id="3" name="MODERNIZE TASK REGISTRY & UNIT TESTS">
    <action>In @[backend_v2/core/registry.py], define TaskMetadataDTO co-located and type TaskDefinition.metadata as TaskMetadataDTO | None, eliminating 10 dict[str, Any] annotations.</action>
    <action>In @[backend_v2/tests/unit/test_progress.py], finalize migration to typed ProgressState and add ISTQB boundary tests.</action>
    <action>In @[backend_v2/tests/unit/core/test_registry.py], migrate task registry tests to TaskMetadataDTO.</action>
  </step>

  <test_contracts>
    <contract id="1" name="test_progress_state_extra_field_forbidden">
      <input>ProgressState(status="running", timestamp="2026-08-31T00:00:00Z", extra_key=123)</input>
      <expected>raises pydantic.ValidationError</expected>
      <category>negative</category>
    </contract>
    <contract id="2" name="test_progress_state_strict_types">
      <input>ProgressState(status=123, timestamp="2026-08-31T00:00:00Z")</input>
      <expected>raises pydantic.ValidationError</expected>
      <category>boundary</category>
    </contract>
    <contract id="3" name="test_database_progress_tracker_payload_conformity">
      <input>DatabaseProgressTracker.update(execution_id="exe_1", state=ProgressState(status="completed", timestamp="...", progress=100))</input>
      <expected>emits payload strictly adhering to ExecutionRecord schema</expected>
      <category>positive</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run backend audit loop on Phase 2A targets:</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/services/progress.py backend_v2/core/registry.py backend_v2/services/execution.py backend_v2/tests/unit/test_progress.py backend_v2/tests/unit/core/test_registry.py --test</command>
  </validation_gate>
</execution_protocol>
