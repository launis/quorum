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

Eliminate all `dict[str, Any]` annotations from internal service progress tracking, task registries, and core services. Refine `ProgressState` in `@[backend_v2/services/progress.py]` to eliminate raw dictionaries while ensuring that database updates strictly adhere to `ExecutionRecord` field contracts to preserve 1:1 cross-domain serialization parity with Flutter client's SSE streaming consumer. Define co-located `TaskMetadataDTO` in `@[backend_v2/core/registry.py]`, replace duck-typing monkey-patching in `@[backend_v2/utils/redis_patcher.py]` with a strongly typed `ArqCompatibleFakeRedis` subclass, and modernize coupled service test suites.

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **@[backend_v2/services/progress.py#L24-L393]**<br>`ProgressState`<br>`ProgressTracker`<br>`DatabaseProgressTracker`<br>`InMemoryProgressTracker`<br>`ProgressService` | Eradicate `result: dict[str, Any]` and `details: dict[str, Any]` fields, untyped `details` kwargs, and property-stripping loops. | Strict `ProgressState` with `ConfigDict(strict=True, extra="forbid", frozen=True)`. `DatabaseProgressTracker` updates conform 1:1 to `ExecutionRecord` fields (`status`, `current_step`, `progress`, `error`). | Avoid creating superfluous wrapper DTOs for progress calls; pass scalar `current_step: str, progress: int` directly to match `ExecutionRecord`. | `test_progress_state_extra_field_forbidden`, `test_progress_state_strict_types`, and `backend_audit_loop.py` |
| **@[backend_v2/core/registry.py#L33-L140]**<br>`TaskDefinition`<br>`TaskMetadataDTO`<br>`TaskRegistry` | Eradicate `metadata: dict[str, Any] | None` and `# noqa: QGR001` suppression from `TaskDefinition` and `TaskRegistry.register_task`. | Co-located `TaskMetadataDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)` (`category`, `description`, `timeout_seconds`, `tags`). `TaskDefinition.metadata: TaskMetadataDTO | None = None`. | Prune separate file module creation for task metadata; keep `TaskMetadataDTO` co-located in `registry.py` alongside `TaskDefinition`. | `test_task_definition_strictness`, `test_task_registry_registration`, and AST guardrails (`QGR001` 0 fatal) |
| **@[backend_v2/utils/redis_patcher.py#L43-L160]**<br>`ArqCompatibleFakeRedis`<br>`get_patched_fakeredis_pool` | Eradicate 7 `hasattr()` reflection calls and dynamic monkey-patching of connection methods onto untyped `fake_redis`. | Strongly typed `ArqCompatibleFakeRedis(FakeRedis)` subclass defining native async methods (`get_connection`, `release`, `pack_commands`, `send_packed_command`, `send_command`, `read_response`). | Prune 3 separate monkey-patch helper functions (`_patch_arq_connection_handling`, `_patch_arq_pipelining`, `_patch_arq_command_execution`) in favor of direct subclass implementation. | `test_progress_service` and `uv run pytest backend_v2/tests/unit/test_progress.py` |
| **@[backend_v2/models/dtos/system.py#L26-L51]**<br>`ClientErrorPayload` | Eradicate ambiguity around permissive dictionary on client error ingress. | Add explicit transport boundary classification comment to `ClientErrorPayload.context_data: dict[str, Any]`: `# noqa: QGR001 [REASON: Client error telemetry payload at external HTTP ingress boundary]`. | Retain `dict[str, Any]` strictly at this external client crash dump boundary without polluting internal service layers. | AST guardrail inspection passing strict suppression rationale |
| **@[backend_v2/tests/unit/test_progress.py#L1-L139]**<br>`test_progress.py` | Eradicate legacy dictionary payloads in progress tracker test assertions. | Modernize test suite to assert against typed `ProgressState` objects; add ISTQB negative partition tests for extra fields and type boundaries. | Reuse unified `ProgressState` schema without inventing test-only mock schemas. | `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_progress.py --test` |
| **@[backend_v2/tests/unit/core/test_registry.py#L1-L85]**<br>`test_registry.py` | Eradicate legacy dictionary metadata fixtures in task registry tests. | Update `test_task_definition_strictness` and `test_task_registry_registration` to pass `TaskMetadataDTO(category="test")` and assert extra-field rejection. | Direct instantiation of `TaskMetadataDTO` with zero intermediate helper wrappers. | `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/core/test_registry.py --test` |

## Target Files

- `[MODIFY]` `@[backend_v2/services/progress.py#L24-L393]`
- `[MODIFY]` `@[backend_v2/core/registry.py#L33-L140]`
- `[MODIFY]` `@[backend_v2/utils/redis_patcher.py#L43-L160]`
- `[MODIFY]` `@[backend_v2/models/dtos/system.py#L26-L51]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_progress.py#L1-L139]`
- `[MODIFY]` `@[backend_v2/tests/unit/core/test_registry.py#L1-L85]`

```xml
<execution_protocol>
  <metadata>
    <epic_anchor>@[docs/epic/EPIC_150_Zero_Permissive_Typing_Lockdown.md#Phase 2: Service & Studio Layer DTO Elimination]</epic_anchor>
    <touched_artifacts>
      <backend>@[backend_v2/services/progress.py#L24-L393]</backend>
      <backend>@[backend_v2/core/registry.py#L33-L140]</backend>
      <backend>@[backend_v2/utils/redis_patcher.py#L43-L160]</backend>
      <backend>@[backend_v2/models/dtos/system.py#L26-L51]</backend>
      <backend>@[backend_v2/tests/unit/test_progress.py#L1-L139]</backend>
      <backend>@[backend_v2/tests/unit/core/test_registry.py#L1-L85]</backend>
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
    <interface id="ArqCompatibleFakeRedis">
      class ArqCompatibleFakeRedis(FakeRedis):
          """Strongly typed FakeRedis subclass providing Arq connection pool compatibility."""
          def __init__(self, *args: Any, **kwargs: Any) -> None:
              super().__init__(*args, **kwargs)
              self.retry = MockRetry()
          async def get_connection(self) -> Any:
              return self
          async def release(self, conn: Any) -> None:
              pass
          def pack_commands(self, cmds: Any) -> Any:
              return cmds
          async def send_packed_command(self, cmds: Any) -> None:
              pass
          async def send_command(self, *args: Any, **kwargs: Any) -> Any:
              res = await self.execute_command(*args, **kwargs)
              _last_response_var.set(res)
          async def read_response(self) -> Any:
              return _last_response_var.get()
    </interface>
  </contract_freeze>

  <anti_targets>
    <file>@[backend_v2/hooks/]</file>
    <file>@[backend_v2/services/orchestrator/]</file>
    <file>@[client_app_v2/]</file>
  </anti_targets>

  <dod_checklist>
    <item>ProgressState refined with ConfigDict(strict=True, extra="forbid", frozen=True), zero raw dict[str, Any] fields</item>
    <item>DatabaseProgressTracker updates conform strictly to ExecutionRecord schema (status, current_step, progress, error)</item>
    <item>TaskMetadataDTO defined in registry.py and TaskDefinition.metadata typed strictly as TaskMetadataDTO | None</item>
    <item>redis_patcher.py hasattr reflection eliminated via strongly typed ArqCompatibleFakeRedis subclass</item>
    <item>ClientErrorPayload.context_data classified with explicit external boundary suppression rationale</item>
    <item>All unit tests in test_progress.py and test_registry.py pass with 100% green coverage and ISTQB negative tests</item>
  </dod_checklist>

  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Verify that Phase 1 quality gates pass cleanly across models and LLM adapters.</action>
    <action>Inspect backend_v2/services/progress.py, backend_v2/core/registry.py, and backend_v2/utils/redis_patcher.py.</action>
  </step>

  <step id="1" name="PRE-IMPLEMENTATION CLEANUPS">
    <action>In @[backend_v2/utils/redis_patcher.py#L43-L160], eliminate 7 hasattr() reflection calls by creating a strongly typed ArqCompatibleFakeRedis subclass inheriting from FakeRedis.</action>
    <action>In @[backend_v2/models/dtos/system.py#L49], add explicit transport boundary classification comment to ClientErrorPayload.context_data: dict[str, Any] (# noqa: QGR001 [REASON: Client error telemetry payload at external HTTP ingress boundary]).</action>
  </step>

  <step id="2" name="MODERNIZE PROGRESS STATE & TRACKER INTERFACES">
    <action>In @[backend_v2/services/progress.py#L24-L393], refine ProgressState to eliminate result: dict[str, Any] and details: dict[str, Any], locking status, timestamp, current_step, progress, error with ConfigDict(strict=True, extra="forbid", frozen=True).</action>
    <action>Refactor ProgressTracker ABC, DatabaseProgressTracker, and InMemoryProgressTracker to use typed ProgressState contracts with scalar parameters.</action>
    <action>Ensure DatabaseProgressTracker database updates strictly adhere to ExecutionRecord fields (status, current_step, progress, error, start_time, end_time, last_updated).</action>
    <action>Type redis_client in ProgressService strictly and eliminate loose type annotations.</action>
  </step>

  <step id="3" name="MODERNIZE TASK REGISTRY & UNIT TESTS">
    <action>In @[backend_v2/core/registry.py#L33-L140], define TaskMetadataDTO co-located with ConfigDict(strict=True, extra="forbid", frozen=True) and type TaskDefinition.metadata and TaskRegistry.register_task as TaskMetadataDTO | None = None, eliminating QGR001 suppressions.</action>
    <action>In @[backend_v2/tests/unit/test_progress.py#L1-L139], finalize migration to typed ProgressState, update tracker assertions, and add ISTQB boundary/negative tests.</action>
    <action>In @[backend_v2/tests/unit/core/test_registry.py#L1-L85], migrate task registry tests to TaskMetadataDTO and test extra field rejection.</action>
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
      <input>DatabaseProgressTracker.update(current_step="step_1", progress=50)</input>
      <expected>emits payload strictly adhering to ExecutionRecord schema (status="running", current_step="step_1", current_step_name="step_1", progress=50)</expected>
      <category>positive</category>
    </contract>
    <contract id="4" name="test_task_metadata_dto_extra_field_forbidden">
      <input>TaskMetadataDTO(category="test", extra_key="invalid")</input>
      <expected>raises pydantic.ValidationError</expected>
      <category>negative</category>
    </contract>
    <contract id="5" name="test_in_memory_progress_tracker_typed_emission">
      <input>InMemoryProgressTracker.update(current_step="working", progress=30)</input>
      <expected>callback receives ProgressState(status="running", current_step="working", progress=30)</expected>
      <category>positive</category>
    </contract>
  </test_contracts>

  <validation_gate>
    <action>Run backend audit loop on Phase 2A targets:</action>
    <command>uv run python scripts/backend_audit_loop.py backend_v2/services/progress.py backend_v2/core/registry.py backend_v2/utils/redis_patcher.py backend_v2/models/dtos/system.py backend_v2/tests/unit/test_progress.py backend_v2/tests/unit/core/test_registry.py --test</command>
  </validation_gate>
</execution_protocol>

