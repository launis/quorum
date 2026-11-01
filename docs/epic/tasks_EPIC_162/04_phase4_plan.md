<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
  <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
</required_context_rules>

# Phase 4: Cross-Process Optimistic Concurrency Control (`state_version` OCC) on PostgreSQL 19 `executions`, Full-Duplex Flutter DTO Parity & Verification Gate

**Overview:** Resolve Chapter 8.2 of `@[docs/arkkitehtuurin_parannuskohteet.md#L232-329]` (`@[docs/arkkitehtuurin_parannuskohteet.md#L307-317]`). Add `state_version: int = 1` to `ExecutionRecord` (`@[backend_v2/models/domain/execution.py#L189-L356]`), `expected_state_version` and `state_version` to `ExecutionUpdateDTO` (`@[backend_v2/models/dtos/trace.py#L65-L118]`) and `NodeExecutionUpdateDTO` (`@[backend_v2/models/dtos/node_execution.py#L30-L72]`), and `@JsonKey(name: 'state_version') @Default(1) int stateVersion` to Flutter `ExecutionRecord` (`@[client_app_v2/lib/features/execution/models/execution_record.dart#L17-84]`). Add `state_version INTEGER NOT NULL DEFAULT 1` to PostgreSQL 19 DDL (`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L233-279]`), register `"state_version"` in `@[scripts/audit_zero_orm_strictness.py]`, and enforce conditional optimistic concurrency control (`state_version` check + atomic increment raising `AppException(ErrorCodes.CONFLICT, status_code=409)` on mismatch) across `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L299-L366]` (`@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L299-366]`), `@[backend_v2/database/postgres/storage_driver.py#L326-353]`, `@[backend_v2/database/repositories/execution.py#L28-L442]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L941-L996]`, `@[backend_v2/tests/fakes/in_memory_uow.py#L1356-L1412]`, `@[backend_v2/tests/fakes/in_memory_repositories.py#L206-226]`, `ExecutionOverrideService` (`@[backend_v2/services/execution/override_service.py#L35-L425]`), and `ExecutionCommitter` (`@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L59-107]` / `@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L107]`). Conclude with the global Backend and Flutter quality gates, Zero-ORM strictness audit, Cross-Language DTO parity audit, SDUI semantic parity suite, and the mandatory live E2E REST API verification gate.

**Source:** `@[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md]` Phase 4: Cross-Process Optimistic Concurrency Control (`state_version` OCC) on PostgreSQL 19 `executions`, Full-Duplex Flutter DTO Parity & Verification Gate

**Target Files:**
- `[MODIFY] @[backend_v2/models/domain/execution.py#L189-L356]`
- `[MODIFY] @[backend_v2/models/dtos/trace.py#L65-L118]`
- `[MODIFY] @[backend_v2/models/dtos/node_execution.py#L30-L72]`
- `[MODIFY] @[client_app_v2/lib/features/execution/models/execution_record.dart#L17-84]`
- `[MODIFY] @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L233-279]`
- `[MODIFY] @[scripts/audit_zero_orm_strictness.py]`
- `[MODIFY] @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L299-L366]`
- `[MODIFY] @[backend_v2/database/postgres/storage_driver.py#L326-353]`
- `[MODIFY] @[backend_v2/database/repositories/execution.py#L28-L442]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_uow.py#L1356-L1412]`
- `[MODIFY] @[backend_v2/tests/fakes/in_memory_repositories.py#L206-226]`
- `[MODIFY] @[backend_v2/services/execution/override_service.py#L35-L425]`
- `[MODIFY] @[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L107]`
- `[MODIFY] @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py#L153-L225]`
- `[MODIFY] @[backend_v2/tests/unit/services/execution/test_override_service.py#L267-L295]`
- `[MODIFY] @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_execution_committer.py#L26-L89]`

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **`@[backend_v2/models/domain/execution.py#L189-L356]`**<br>**`@[backend_v2/models/dtos/trace.py#L65-L118]`**<br>**`@[backend_v2/models/dtos/node_execution.py#L30-L72]`**<br>**`@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L233-279]`**<br>**`@[scripts/audit_zero_orm_strictness.py]`**<br>**`@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L299-L366]`**<br>**`@[backend_v2/database/postgres/storage_driver.py#L326-353]`**<br>**`@[backend_v2/database/repositories/execution.py#L28-L442]`** | Blindly overwriting `executions` rows across API and worker processes without version checking. | Add `state_version: int = 1` to `ExecutionRecord`, `001_pg19_uuidv7_schema.sql`, and `APPROVED_ADAPTER_RECORD_COLUMNS` in `audit_zero_orm_strictness.py`, and enforce conditional `expected_state_version` OCC check + increment raising `AppException(ErrorCodes.CONFLICT, status_code=409)`. | Zero distributed Redis locks (`Redlock`); rely 100% on native PostgreSQL 19 atomic `state_version` OCC. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py backend_v2/database/postgres/storage_driver.py backend_v2/database/repositories/execution.py --test --ast-strict` |
| **`@[backend_v2/tests/fakes/in_memory_uow.py#L1577-L1650]`**<br>**`@[backend_v2/tests/fakes/in_memory_repositories.py#L206-226]`**<br>**`@[backend_v2/services/execution/override_service.py#L35-L425]`**<br>**`@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L107]`**<br>**`@[client_app_v2/lib/features/execution/models/execution_record.dart#L17-84]`** | Silent lost updates when `ExecutionOverrideService` and `ExecutionCommitter` mutate `ExecutionRecord` concurrently across processes, and missing `state_version` on Flutter `ExecutionRecord`. | Pass `expected_state_version=record.state_version` in `ExecutionOverrideService`, merge concurrent overrides/syntheses and advance `state_version` in `ExecutionCommitter`, enforce OCC in `InMemoryUnitOfWork` / `InMemoryExecutionRepository`, and add `@JsonKey(name: 'state_version') @Default(1) int stateVersion` to Flutter `ExecutionRecord`. | Zero multi-table lock tables; keep OCC self-contained on the `executions` row and `ExecutionRecord` DTO. | `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/execution_record.dart --build` |

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Phases 1, 2, and 3 completion in `@[docs/epic/EPIC_162_tracker.md]` and read `@[backend_v2/models/domain/execution.py#L189-L356]`, `@[backend_v2/models/dtos/trace.py#L65-L118]`, `@[backend_v2/models/dtos/node_execution.py#L30-L72]`, `@[client_app_v2/lib/features/execution/models/execution_record.dart#L17-84]`, `@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L233-279]`, `@[scripts/audit_zero_orm_strictness.py]`, `@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L299-L366]`, `@[backend_v2/database/postgres/storage_driver.py#L326-353]`, `@[backend_v2/database/repositories/execution.py#L28-L442]`, `@[backend_v2/services/execution/override_service.py#L35-L425]`, and `@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L107]`.</action>
    <action>Look forward: Verify Step 4.1 adds `state_version` across the domain/DTO models, PostgreSQL 19 schema, `audit_zero_orm_strictness.py`, and Zero-ORM entity adapter/storage driver/repository, Step 4.2 wires `expected_state_version` into `ExecutionOverrideService`, `ExecutionCommitter`, in-memory fakes, and Flutter `ExecutionRecord`, and Step 4.3 executes the full-stack completion and live E2E gates.</action>
    <constraint invariant="full_duplex_serialization_parity_mandate">Adding `state_version` to `ExecutionRecord` in Python MUST be synchronized 1:1 with `@JsonKey(name: 'state_version')` in Flutter `execution_record.dart` and `APPROVED_ADAPTER_RECORD_COLUMNS` in `scripts/audit_zero_orm_strictness.py`.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, synchronize architectural corrections back into @[docs/epic/EPIC_162_studio_target_sync_cognitive_tier_and_dag_occ_resilience.md] and @[docs/epic/EPIC_162_tracker.md]. Update # Session Handover Context and set Resume Command to /tier2-execute --full-auto @[docs/epic/tasks_EPIC_162/04_phase4_plan.md] @[docs/epic/EPIC_162_tracker.md].</directive>
  </step>

  <touched_artifacts>
    <backend>@[backend_v2/models/domain/execution.py]</backend>
    <backend>@[backend_v2/models/dtos/trace.py]</backend>
    <backend>@[backend_v2/models/dtos/node_execution.py]</backend>
    <backend>@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql]</backend>
    <backend>@[scripts/audit_zero_orm_strictness.py]</backend>
    <backend>@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py]</backend>
    <backend>@[backend_v2/database/postgres/storage_driver.py]</backend>
    <backend>@[backend_v2/database/repositories/execution.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_uow.py]</backend>
    <backend>@[backend_v2/tests/fakes/in_memory_repositories.py]</backend>
    <backend>@[backend_v2/services/execution/override_service.py]</backend>
    <backend>@[backend_v2/services/orchestrator/dag_executor/execution_committer.py]</backend>
    <backend>@[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py]</backend>
    <backend>@[backend_v2/tests/unit/services/execution/test_override_service.py]</backend>
    <backend>@[backend_v2/tests/unit/services/orchestrator/dag_executor/test_execution_committer.py]</backend>
    <frontend>@[client_app_v2/lib/features/execution/models/execution_record.dart]</frontend>
  </touched_artifacts>

  <dod_checklist>
    <item>`ExecutionRecord` (@[backend_v2/models/domain/execution.py#L189-L356]) defines `state_version: Annotated[int, Field(ge=1, default=1, description="Monotonically increasing optimistic concurrency control version")] = 1`, and `ExecutionUpdateDTO` (@[backend_v2/models/dtos/trace.py#L65-L118]) and `NodeExecutionUpdateDTO` (@[backend_v2/models/dtos/node_execution.py#L30-L72]) define `expected_state_version: int | None = None` and `state_version: int | None = None`.</item>
    <item>PostgreSQL 19 DDL (@[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L233-279]) includes `state_version INTEGER NOT NULL DEFAULT 1` on `executions`, and `@[scripts/audit_zero_orm_strictness.py]` includes `"state_version"` in `APPROVED_ADAPTER_RECORD_COLUMNS`.</item>
    <item>`save_execution_row` and `hydrate_execution_row` in @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L299-L366], `PostgresStorageDriver.update` in @[backend_v2/database/postgres/storage_driver.py#L326-353], and `ExecutionRepositoryImpl.update_execution` in @[backend_v2/database/repositories/execution.py#L28-L442] enforce `expected_state_version` OCC conflict detection, logging an RFC 7807 `logger.error` with `ErrorCodes.CONFLICT.name` and raising `AppException(ErrorCodes.CONFLICT, status_code=409)` on version mismatch and incrementing `state_version` on success.</item>
    <item>`InMemoryUnitOfWork` (@[backend_v2/tests/fakes/in_memory_uow.py#L1577-L1650]), `InMemoryExecutionRepository` (@[backend_v2/tests/fakes/in_memory_repositories.py#L206-226]), `ExecutionOverrideService` (@[backend_v2/services/execution/override_service.py#L35-L425]), `ExecutionCommitter` (@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L107]), and Flutter `ExecutionRecord` (@[client_app_v2/lib/features/execution/models/execution_record.dart#L17-84]) synchronized with 100% OCC and Full-Duplex Serialization Parity.</item>
    <item>Global Backend Quality Gate, Global Flutter Quality Gate, `audit_zero_orm_strictness.py`, `audit_dto_parity.py`, `test_sdui_semantic_parity.py`, and Live E2E REST API verification gate (`test_integration_real_llm.py`) pass 100%.</item>
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
    <knowledge_item>@[ki_router_ssot_and_crud_clone_lifecycle.md]</knowledge_item>
    <knowledge_item>@[ki_deterministic_hardening_state.md]</knowledge_item>
  </required_context_rules>

  <anti_targets>
    <anti_target>Do NOT add a 13th table to PostgreSQL 19 DDL; `state_version` MUST be a native integer column on the existing `executions` table (`001_pg19_uuidv7_schema.sql#L233-279`).</anti_target>
    <anti_target>Do NOT mock repository persistence with static `AsyncMock` return values (`deceptive_persistence_mocking_ban`); verify stateful roundtrip OCC increments and HTTP 409 conflict rejection against `InMemoryUnitOfWork` / `InMemoryExecutionRepository`.</anti_target>
  </anti_targets>

  <step id="4.1" name="ExecutionRecord.state_version Schema, PostgreSQL 19 DDL, Zero-ORM Strictness &amp; Entity Adapter OCC Enforcement">
    <action>In @[backend_v2/models/domain/execution.py#L189-L356], add `state_version: Annotated[int, Field(ge=1, default=1, description="Monotonically increasing optimistic concurrency control version")] = 1` to `ExecutionRecord`. In @[backend_v2/models/dtos/trace.py#L65-L118] (`ExecutionUpdateDTO`) and @[backend_v2/models/dtos/node_execution.py#L30-L72] (`NodeExecutionUpdateDTO`), add `expected_state_version: Annotated[int | None, Field(ge=1, default=None, description="Expected OCC state_version for conditional update")] = None` and `state_version: Annotated[int | None, Field(ge=1, default=None, description="Updated OCC state_version")] = None`.</action>
    <action>In @[backend_v2/database/migrations/001_pg19_uuidv7_schema.sql#L233-279], add `state_version INTEGER NOT NULL DEFAULT 1` to `CREATE TABLE IF NOT EXISTS executions`. In @[scripts/audit_zero_orm_strictness.py], add `"state_version"` to `APPROVED_ADAPTER_RECORD_COLUMNS`.</action>
    <action>In @[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L299-L366] (`@[backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py#L299-366]`), @[backend_v2/database/postgres/storage_driver.py#L326-353], and @[backend_v2/database/repositories/execution.py#L28-L442], add `state_version` as column `$41` in `_EXECUTION_COLS` and `_SAVE_EXECUTION_SQL`, hydrate `state_version=int(row["state_version"])` in `hydrate_execution_row`, and enforce OCC in `save_execution_row`, `PostgresStorageDriver.update`, and `ExecutionRepositoryImpl.update_execution`: when `expected_state_version` is provided and does not match the stored `state_version`, log a structured `logger.error` with `ErrorCodes.CONFLICT.name` and raise `AppException(message=..., status_code=409, details={"error_code": ErrorCodes.CONFLICT})`, otherwise increment `state_version = existing_state_version + 1`.</action>
    <action>In @[backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py#L153-L225], add positive, boundary, and negative unit tests verifying `state_version` persistence, atomic increment on matching `expected_state_version`, and `AppException(ErrorCodes.CONFLICT, status_code=409)` on stale `expected_state_version`.</action>
    <constraint invariant="rfc7807_dual_reporting_mandate">Every `AppException(ErrorCodes.CONFLICT, status_code=409)` MUST be preceded by a structured `logger.error` logging the execution ID, `expected_state_version`, and actual `state_version`.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py</audit_command>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/models/domain/execution.py backend_v2/models/dtos/trace.py backend_v2/models/dtos/node_execution.py scripts/audit_zero_orm_strictness.py backend_v2/database/postgres/entity_adapter/execution_and_report_stage.py backend_v2/database/postgres/storage_driver.py backend_v2/database/repositories/execution.py backend_v2/tests/unit/database/postgres/entity_adapter/test_execution_and_report_stage.py --test --ast-strict</audit_command>
  </step>

  <step id="4.2" name="Cross-Process OCC Wiring in ExecutionOverrideService, ExecutionCommitter, In-Memory Fakes &amp; Flutter ExecutionRecord Parity">
    <action>In @[backend_v2/tests/fakes/in_memory_uow.py#L999-L1511] (`@[backend_v2/tests/fakes/in_memory_uow.py#L999-L1511]`) and @[backend_v2/tests/fakes/in_memory_repositories.py#L206-226], synchronize `state_version` storage, increment, and `expected_state_version` OCC conflict detection (`ErrorCodes.CONFLICT`, HTTP 409) in `InMemoryAsyncPgConnection` and `InMemoryExecutionRepository.update_execution`.</action>
    <action>In @[backend_v2/services/execution/override_service.py#L35-L425], pass `expected_state_version=record.state_version` in `ExecutionUpdateDTO` inside `clear_profile_synthesis`, `override_atom`, and `reject_evidence_quote` so concurrent worker writes trigger deterministic HTTP 409 `ErrorCodes.CONFLICT` instead of silent lost updates.</action>
    <action>In @[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L41-L107] (`@[backend_v2/services/orchestrator/dag_executor/execution_committer.py#L59-107]`), preserve concurrent human overrides and profile syntheses when committing trace updates and synchronize `state.record` with the incremented `state_version`.</action>
    <action>In @[client_app_v2/lib/features/execution/models/execution_record.dart#L17-84], add `@JsonKey(name: 'state_version') @Default(1) int stateVersion` to `ExecutionRecord` and run Freezed code generation.</action>
    <action>In @[backend_v2/tests/unit/services/execution/test_override_service.py#L267-L295] and @[backend_v2/tests/unit/services/orchestrator/dag_executor/test_execution_committer.py#L26-L89], add positive and negative unit tests verifying `expected_state_version` propagation, HTTP 409 `ErrorCodes.CONFLICT` when a concurrent update advances `state_version` mid-override, and preservation of human overrides during `ExecutionCommitter.commit_trace`.</action>
    <constraint invariant="deceptive_persistence_mocking_ban">All OCC unit tests in `test_override_service.py` and `test_execution_committer.py` MUST verify stateful roundtrip `state_version` increments and conflict detection.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/tests/fakes/in_memory_uow.py backend_v2/tests/fakes/in_memory_repositories.py backend_v2/services/execution/override_service.py backend_v2/services/orchestrator/dag_executor/execution_committer.py backend_v2/tests/unit/services/execution/test_override_service.py backend_v2/tests/unit/services/orchestrator/dag_executor/test_execution_committer.py --test --ast-strict</audit_command>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models/execution_record.dart --build</audit_command>
  </step>

  <step id="4.3" name="Global Backend &amp; Frontend Quality Gates, DTO/SDUI Parity &amp; Mandatory Live E2E REST API Verification Gate">
    <action>Execute the Cross-Language DTO Parity Verifier (`@[scripts/audit_dto_parity.py]`), Zero-ORM Strictness Verifier (`@[scripts/audit_zero_orm_strictness.py]`), and Cross-Domain SDUI Semantic Parity suite (`@[backend_v2/tests/integration/test_sdui_semantic_parity.py]`).</action>
    <action>Execute the Global Backend Audit Loop (`scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`), Global Flutter Audit Loop (`scripts/flutter_audit_loop.py client_app_v2/ --build`), and the Mandatory Live E2E REST API Verification Gate (`$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`).</action>
    <constraint invariant="fragmented_quality_gates_prevention">Both global audit loops and the live E2E integration suite MUST pass 100% before closing Phase 4.</constraint>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py</audit_command>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_dto_parity.py</audit_command>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline pytest backend_v2/tests/integration/test_sdui_semantic_parity.py</audit_command>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict</audit_command>
    <audit_command>$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build</audit_command>
    <audit_command>$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py</audit_command>
  </step>

  <test_contracts>
    <test name="test_save_execution_row_increments_state_version_on_matching_expected_state_version" category="positive">
      <input>ExecutionRecord initially saved at state_version=1, then updated with expected_state_version=1</input>
      <expected>Persisted ExecutionRecord has state_version=2 on roundtrip fetch</expected>
    </test>
    <test name="test_save_execution_row_raises_conflict_409_on_stale_expected_state_version" category="negative">
      <input>ExecutionRecord at state_version=2 updated with stale expected_state_version=1</input>
      <expected>Raises AppException with ErrorCodes.CONFLICT and status_code=409 while preserving state_version=2</expected>
    </test>
    <test name="test_execution_record_rejects_state_version_less_than_one" category="boundary">
      <input>ExecutionRecord instantiated with state_version=0 (boundary min-1 for ge=1)</input>
      <expected>Raises pydantic.ValidationError</expected>
    </test>
    <test name="test_override_service_raises_conflict_409_when_worker_advances_state_version_concurrently" category="negative">
      <input>ExecutionOverrideService.override_atom reads record at state_version=1; concurrent worker commit advances stored state_version to 2 before override_atom calls update_execution</input>
      <expected>Raises AppException with ErrorCodes.CONFLICT (status_code=409) without overwriting the concurrent worker update</expected>
    </test>
    <test name="test_execution_committer_preserves_concurrent_human_overrides_and_increments_state_version" category="positive">
      <input>ExecutionCommitter.commit_trace executes after human override mutated step_states and advanced state_version in repository</input>
      <expected>Committed record preserves the human override and increments state_version cleanly</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <action>Run Zero-ORM Strictness, DTO Parity, and SDUI Semantic Parity gates: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_zero_orm_strictness.py`, `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/audit_dto_parity.py`, and `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.</action>
    <action>Run Global Backend Audit Loop: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/backend_audit_loop.py backend_v2/ --test --ast-strict`.</action>
    <action>Run Global Flutter Audit Loop: `$env:UV_NO_SYNC="1"; $env:UV_OFFLINE="1"; uv run --no-sync --offline python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
    <action>Run Live E2E REST API Verification Gate: `$env:RUN_LIVE_E2E="true"; uv run pytest backend_v2/tests/integration/test_integration_real_llm.py`.</action>
  </validation_gate>
</execution_protocol>

