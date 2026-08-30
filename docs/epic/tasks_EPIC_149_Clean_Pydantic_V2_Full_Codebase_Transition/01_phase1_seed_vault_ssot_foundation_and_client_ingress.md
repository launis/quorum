# Phase 1: Seed Vault Sanitization, Pre-Implementation Cleanups & SSOT Foundation

**Overview:** Sanitize Seed Vault data upfront, lock foundational data models, modernize baseline models and core test fixtures, purge vestigial database files, add FastAPI Lifespan pre-flight schema validation, and synchronize Flutter client execution DTOs and API clients to eliminate 422 ingress errors and SSE stream deserialization crashes.
**Target Files:**
- `[MODIFY]` @[backend_v2/seed/seed_data.json]
- `[MODIFY]` @[backend_v2/seed/run_seed.py]
- `[DELETE]` @[data/app.db]
- `[DELETE]` @[data/app.sqlite]
- `[MODIFY]` @[backend_v2/main.py]
- `[MODIFY]` @[backend_v2/models/v2_core.py#L1368-L1431]
- `[MODIFY]` @[backend_v2/models/execution_core.py#L22-L82]
- `[MODIFY]` @[backend_v2/core/hook_registry.py#L68-L79]
- `[MODIFY]` @[backend_v2/core/hook_registry.py#L82-L86]
- `[MODIFY]` @[backend_v2/core/registry.py#L33-L52]
- `[NEW]` @[backend_v2/models/dtos/hook_state.py]
- `[NEW]` @[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/execution_record.dart]
- `[MODIFY]` @[client_app_v2/lib/core/api/execution_client.dart#L26-L43]
- `[MODIFY]` @[client_app_v2/lib/features/execution/controllers/execution_controller.dart#L40-L61]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/new_execution_view.dart#L44-L65]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]
- `[MODIFY]` @[backend_v2/tests/unit/models/test_v2_core.py]
- `[MODIFY]` @[backend_v2/tests/unit/models/test_execution_core.py]
- `[MODIFY]` @[backend_v2/tests/unit/core/test_registry.py]
- `[MODIFY]` @[backend_v2/tests/unit/core/test_hook_registry.py]
- `[MODIFY]` @[backend_v2/tests/unit/seed/test_run_seed.py]
- `[MODIFY]` @[client_app_v2/test/features/execution/controllers/execution_controller_test.dart]

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| **Seed Vault Sanitization & Seeder Lifecycle**<br>@[backend_v2/seed/seed_data.json]<br>@[backend_v2/seed/run_seed.py]<br>@[data/app.db]<br>@[data/app.sqlite] | Banned: Hardcoded database paths (`PROJECT_ROOT / "data" / "db_v2.json"`), leaving orphaned files (`app.db`, `app.sqlite`), and unvalidated JSON seeds. | Mandatory: Dynamic DB path resolution via `get_settings().prod_db_path` (@[backend_v2/settings.py#L473-L481]), clean-slate table drop, wipe of `data/files/executions/`, permanent purge of 0-byte vestigial files, and upfront seed sanitization via `sanitize_seed_vault.py`. | Pruned: Complex schema migration engines or backwards compatibility data shims; clean-slate reset is sovereign for local development. | `uv run python scripts/audit_database_atoms.py --strict`<br>`uv run python backend_v2/seed/run_seed.py local`<br>`uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/seed/test_run_seed.py --test` |
| **FastAPI Lifespan Schema Gate**<br>@[backend_v2/main.py] | Banned: Silent boot with unmigrated/dirty database records causing runtime 500 crashes downstream. | Mandatory: Pre-flight schema validation during lifespan startup validating root collections (`system_config`, `workflows`, `output_profiles`) against strict Pydantic V2 models, cleanly aborting with instructions to re-seed. | Pruned: In-flight automated database repair scripts inside FastAPI application thread. | Lifespan startup unit tests verifying clean abort on corrupted DB records.<br>`uv run python scripts/backend_audit_loop.py backend_v2/main.py --test` |
| **Backend Core Models & Hook DTOs**<br>@[backend_v2/models/v2_core.py#L1368-L1431]<br>@[backend_v2/models/execution_core.py#L22-L82]<br>@[backend_v2/core/hook_registry.py#L68-L79]<br>@[backend_v2/core/hook_registry.py#L82-L86]<br>@[backend_v2/core/registry.py#L33-L52]<br>[NEW] @[backend_v2/models/dtos/hook_state.py] | Banned: `target_locale="en"` default factories (@[backend_v2/models/v2_core.py#L1375,L1421]), loose `dict[str, Any]` fields in `HookState` and `HookResult`, ad-hoc worker telemetry dictionaries, and reflection via `getattr`/`hasattr`. | Mandatory: Strict mandatory `target_locale`, new typed `ExecutionInputsDTO` [NEW], `GlobalContextVarsDTO` [NEW], `HookDeltaDTO` [NEW] with `ConfigDict(strict=True, extra="forbid", frozen=True)`, and strict `ExecutionMetadata` SSOT. | Pruned: Speculative generic visitor patterns, legacy wrapper types, and chameleon `BaseModel` classes. | Unit tests in `test_v2_core.py`, `test_execution_core.py`, `test_hook_registry.py`, `test_registry.py` passing 100%.<br>`uv run python scripts/backend_audit_loop.py backend_v2/models/ --test` |
| **Flutter Client Execution Ingress & Freezed Parity**<br>[NEW] @[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]<br>@[client_app_v2/lib/features/execution/models/execution_record.dart]<br>@[client_app_v2/lib/core/api/execution_client.dart#L26-L43]<br>@[client_app_v2/lib/features/execution/controllers/execution_controller.dart#L40-L61]<br>@[client_app_v2/lib/features/execution/views/new_execution_view.dart#L44-L65]<br>@[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart] | Banned: Naked Dart `Map<String, dynamic>` API calls, `allowedKeys` duct-tape filter, legacy parameters (`strictness_level`, `scoring_strategy`), duplicate `dio.post` calls, and silent error swallowing in SSE stream. | Mandatory: Freezed `ExecutionCreateRequestDto` [NEW] (`disallowUnrecognizedKeys: true`), complete 1:1 Freezed `ExecutionRecord` schema matching backend, unified `executionClientProvider` ingress, and active locale propagation from `Localizations.localeOf(context)`. | Pruned: Legacy fallback parameter mappings and client-side dictionary filtering. | Flutter test suite & Freezed build passing.<br>`uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build`<br>`uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py` |

## Phase 1: Pre-Implementation Cleanups

1. **Backend Tech Debt**:
   - `target_locale="en"` default factories in @[backend_v2/models/v2_core.py#L1375,L1421] removed; `target_locale` converted to mandatory `str = Field(...)`.
   - `inputs: dict[str, Any]` and `global_context_vars: dict[str, Any]` in @[backend_v2/core/hook_registry.py#L68-L79] replaced with typed DTOs.
   - `state_delta: dict[str, Any] | None` in @[backend_v2/core/hook_registry.py#L82-L86] replaced with typed `HookDeltaDTO | None`.
   - `TaskDefinition.metadata: dict[str, Any] | None` in @[backend_v2/core/registry.py#L33-L52] audited and strictly typed.
   - Hardcoded paths in @[backend_v2/seed/run_seed.py] updated to resolve dynamically from `get_settings().prod_db_path` (@[backend_v2/settings.py#L473-L481]).
2. **Frontend Tech Debt**:
   - `allowedKeys` duct-tape dictionary filter in `executionList` (@[client_app_v2/lib/features/execution/controllers/execution_controller.dart#L40-L61]) removed.
   - Silent error catching in `_connectToStream` (@[client_app_v2/lib/features/execution/controllers/execution_controller.dart]) replaced with structured `LoggerServiceProvider` error logging and error state emission.
   - Legacy parameters (`strictness_level`, `scoring_strategy`) in `ExecutionClient.startExecution` (@[client_app_v2/lib/core/api/execution_client.dart#L26-L43]) purged and replaced with `ExecutionCreateRequestDto`.
   - Duplicate `dio.post` in `NewExecutionController` (@[client_app_v2/lib/features/execution/views/new_execution_view.dart#L44-L65]) deleted and unified via `executionClientProvider`.
3. **ISTQB Negative Partitions**:
   - Missing required `target_locale` throws `ValidationError` Fail-Fast.
   - Unrecognized key on `ExecutionCreateRequestDto` or `ExecutionRecord` throws `CheckedFromJsonException` / `FormatException`.
   - Raw dictionary input to `HookState` rejected by strict Pydantic V2 validation.

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Read the actual codebase state left by previous epics. Verify that current models, seed data, and Flutter clients are ready for clean Pydantic V2 / Freezed strictness locking.</action>
    <action>Look forward: Verify if the current plan's assumptions still hold true in @[backend_v2/seed/seed_data.json], @[backend_v2/seed/run_seed.py], @[backend_v2/main.py], @[backend_v2/models/v2_core.py#L1368-L1431], @[backend_v2/core/hook_registry.py#L68-L79], @[client_app_v2/lib/features/execution/models/execution_record.dart], and @[client_app_v2/lib/core/api/execution_client.dart#L26-L43].</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_149_Clean_Pydantic_V2_Full_Codebase_Transition.md]) and the Tracker document if available, and synchronize the architectural corrections back into them to maintain them as the true SSOT.</directive>
  </step>

  <dod_checklist>
    - [ ] Pre-flight audit and backfill of explicit `target_locale` for all executions and seed templates in @[backend_v2/seed/seed_data.json] via `sanitize_seed_vault.py`.
    - [ ] `run_seed.py` in @[backend_v2/seed/run_seed.py] modernized to dynamically resolve database path from `get_settings().prod_db_path` (@[backend_v2/settings.py#L473-L481]), unconditionally drop all tables, wipe `data/files/executions/`, and ensure clean lifecycle without hardcoded relative paths.
    - [ ] Legacy 0-byte vestigial database files (`data/app.db`, `data/app.sqlite`) permanently deleted from disk.
    - [ ] FastAPI lifespan startup in @[backend_v2/main.py] updated with pre-flight schema check validating `system_config` and `workflows` against strict models, cleanly aborting with instructions to run `run_seed.py local` if dirty records are detected.
    - [ ] `target_locale="en"` default_factory removed from `ExecutionRecord.metadata` (@[backend_v2/models/v2_core.py#L1421]) and `ExecutionCoreFields.target_locale` (@[backend_v2/models/v2_core.py#L1375]); `target_locale` is mandatory without default.
    - [ ] `ExecutionMetadata` verified in @[backend_v2/models/execution_core.py#L22-L82] to cover all telemetry fields (`organization_id`, `user_id`) currently written as ad-hoc dict keys in `worker.py`.
    - [ ] `HookState.inputs: dict[str, Any]`, `HookState.global_context_vars: dict[str, Any]` in @[backend_v2/core/hook_registry.py#L68-L79], and `HookResult.state_delta: dict[str, Any] | None` in @[backend_v2/core/hook_registry.py#L82-L86] replaced with typed `ExecutionInputsDTO`, `GlobalContextVarsDTO`, and `HookDeltaDTO | None`.
    - [ ] `TaskDefinition.metadata: dict[str, Any] | None` in @[backend_v2/core/registry.py#L33-L52] audited with explicit `noqa: QGR001` justification or typed metadata DTO.
    - [ ] New DTO models `HookDeltaDTO`, `ExecutionInputsDTO`, `GlobalContextVarsDTO` created in @[backend_v2/models/dtos/hook_state.py] [NEW].
    - [ ] `ExecutionCreateRequestDto` created in @[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart] [NEW] with `workflow_id`, `target_locale`, `raw_inputs`, optional `profile_id`, and `@JsonSerializable(disallowUnrecognizedKeys: true)`.
    - [ ] `ExecutionRecord` in @[client_app_v2/lib/features/execution/models/execution_record.dart] updated to 1:1 schema parity with backend `ExecutionRecord`, adding missing fields (`activeProfileId`, `rawInputs`, `durationMs`, `updatedAt`, `completedAt`, `createdBy`, `organizationId`, `cumulativeSynthesisTokens`, `cumulativeSynthesisCost`, `modelsUsed`).
    - [ ] `ExecutionClient.startExecution` in @[client_app_v2/lib/core/api/execution_client.dart#L26-L43] refactored to accept `ExecutionCreateRequestDto`, send `target_locale`, and eliminate obsolete legacy parameters (`strictness_level`, `scoring_strategy`).
    - [ ] `allowedKeys` duct-tape dictionary filter in `executionList` (@[client_app_v2/lib/features/execution/controllers/execution_controller.dart#L40-L61]) and silent error swallowing in `_connectToStream` deleted in @[client_app_v2/lib/features/execution/controllers/execution_controller.dart].
    - [ ] Duplicate `dio.post` in `NewExecutionController` deleted in @[client_app_v2/lib/features/execution/views/new_execution_view.dart#L44-L65] and unified through `executionClientProvider`.
    - [ ] Active `target_locale` resolved from `Localizations.localeOf(context).languageCode` in @[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart].
    - [ ] All atomic tests in @[backend_v2/tests/unit/models/test_v2_core.py], @[backend_v2/tests/unit/models/test_execution_core.py], @[backend_v2/tests/unit/core/test_registry.py], @[backend_v2/tests/unit/core/test_hook_registry.py], @[backend_v2/tests/unit/seed/test_run_seed.py], and @[client_app_v2/test/features/execution/controllers/execution_controller_test.dart] modernized and passing.
    - [ ] Backend and Flutter quality gates pass: `uv run python scripts/audit_database_atoms.py --strict`, `uv run python backend_v2/seed/run_seed.py local`, `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build`, and `uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py`.
  </dod_checklist>

  <required_context_rules>
    <rule>@[.agents/rules/00-antigravity-core.md]</rule>
    <rule>@[.agents/rules/01-python-backend.md]</rule>
    <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
    <rule>@[.agents/rules/03_seed_vault.md]</rule>
    <rule>@[.agents/rules/04_directory_reference.md]</rule>
    <rule>@[.agents/rules/05_llm_architecture.md]</rule>
    <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
    <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
    <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
    <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
    <knowledge_item>@[ki_global_config_sovereignty.md]</knowledge_item>
    <knowledge_item>@[ki_seed_vault_verification_and_sanitization.md]</knowledge_item>
    <knowledge_item>@[ki_domain_model_prompt_separation.md]</knowledge_item>
    <knowledge_item>@[ki_neuro_symbolic_agentic_workflow.md]</knowledge_item>
    <knowledge_item>@[ki_ast_guardrail_engine.md]</knowledge_item>
    <knowledge_item>@[ki_app_error_boundary.md]</knowledge_item>
  </required_context_rules>

  <touched_artifacts>
    <backend>@[backend_v2/seed/seed_data.json]</backend>
    <backend>@[backend_v2/seed/run_seed.py]</backend>
    <backend>@[backend_v2/main.py]</backend>
    <backend>@[backend_v2/models/v2_core.py]</backend>
    <backend>@[backend_v2/models/execution_core.py]</backend>
    <backend>@[backend_v2/core/hook_registry.py]</backend>
    <backend>@[backend_v2/core/registry.py]</backend>
    <backend>[NEW] @[backend_v2/models/dtos/hook_state.py]</backend>
    <frontend>[NEW] @[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/models/execution_record.dart]</frontend>
    <frontend>@[client_app_v2/lib/core/api/execution_client.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/controllers/execution_controller.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/new_execution_view.dart]</frontend>
    <frontend>@[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]</frontend>
  </touched_artifacts>

  <anti_targets>
    - Do NOT modify `database/repositories/` in Phase 1 (strictly reserved for Phase 2).
    - Do NOT modify `backend_v2/hooks/scoring.py` or decompose hooks in Phase 1 (strictly reserved for Phase 3).
    - Do NOT modify `backend_v2/services/orchestrator/` in Phase 1 (strictly reserved for Phase 4).
    - Do NOT alter the qualitative prompt texts in `seed_data.json` per `prompt_preservation_mandate`.
    - Do NOT introduce temporary `Union[NewModel, dict]` bridge types or fallback parsers (`the_no_legacy_mandate`).
  </anti_targets>

  <step id="1" name="SEED VAULT SANITIZATION & SEEDER LIFECYCLE HARDENING">
    <action>Execute `sanitize_seed_vault.py` on @[backend_v2/seed/seed_data.json] to backfill explicit `target_locale` on all execution seeds and prompt templates.</action>
    <action>Modernize @[backend_v2/seed/run_seed.py] to dynamically resolve database path from `get_settings().prod_db_path` (@[backend_v2/settings.py#L473-L481]), unconditionally drop all tables, wipe `data/files/executions/`, and eliminate hardcoded relative paths.</action>
    <action>Permanently delete legacy 0-byte database files @[data/app.db] and @[data/app.sqlite] from disk.</action>
    <action>Add pre-flight schema validation in @[backend_v2/main.py] lifespan startup to validate database root documents on boot and cleanly abort if unmigrated records exist.</action>
    <constraint invariant="the_no_legacy_mandate">Clean-slate database reset is authoritative. Abandon historical local traces.</constraint>
  </step>

  <step id="2" name="FOUNDATIONAL BACKEND MODEL & DTO MODERNIZATION">
    <action>Create @[backend_v2/models/dtos/hook_state.py] [NEW] defining `ExecutionInputsDTO`, `GlobalContextVarsDTO`, and `HookDeltaDTO` with `ConfigDict(strict=True, extra="forbid", frozen=True)`.</action>
    <action>Update @[backend_v2/models/v2_core.py#L1368-L1431] to remove `target_locale="en"` default factories and make `target_locale` strictly mandatory.</action>
    <action>Verify @[backend_v2/models/execution_core.py#L22-L82] contains all telemetry fields (`organization_id`, `user_id`) required for background worker executions.</action>
    <action>Update @[backend_v2/core/hook_registry.py#L68-L79] to type `inputs: ExecutionInputsDTO`, `global_context_vars: GlobalContextVarsDTO`, and @[backend_v2/core/hook_registry.py#L82-L86] `state_delta: HookDeltaDTO | None`.</action>
    <action>Audit @[backend_v2/core/registry.py#L33-L52] for strict metadata typing and add `noqa` markers where appropriate.</action>
    <demolish>REMOVE: `target_locale: str = Field(default="en")` and `default_factory=lambda: ExecutionMetadata(target_locale="en")` at @[backend_v2/models/v2_core.py#L1375,L1421]. REPLACE WITH: Mandatory `target_locale: str = Field(...)`.</demolish>
    <demolish>REMOVE: `inputs: dict[str, Any]` and `global_context_vars: dict[str, Any]` and `state_delta: dict[str, Any] | None` at @[backend_v2/core/hook_registry.py#L68-L79,L82-L86]. REPLACE WITH: `ExecutionInputsDTO`, `GlobalContextVarsDTO`, `HookDeltaDTO | None`.</demolish>
  </step>

  <step id="3" name="FLUTTER CLIENT EXECUTION INGRESS & FREEZED PARITY">
    <action>Create @[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart] [NEW] matching `ExecutionCreate` DTO with `@JsonSerializable(disallowUnrecognizedKeys: true)`.</action>
    <action>Update @[client_app_v2/lib/features/execution/models/execution_record.dart] to full 1:1 schema parity with backend `ExecutionRecord`.</action>
    <action>Refactor @[client_app_v2/lib/core/api/execution_client.dart#L26-L43] `startExecution` to accept `ExecutionCreateRequestDto` and eliminate obsolete parameters (`strictness_level`, `scoring_strategy`).</action>
    <action>Update @[client_app_v2/lib/features/execution/controllers/execution_controller.dart#L40-L61] to delete `allowedKeys` dictionary filter and remove silent error catching in `_connectToStream`.</action>
    <action>Update @[client_app_v2/lib/features/execution/views/new_execution_view.dart#L44-L65] and @[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart] to pass active `target_locale` through `executionClientProvider`.</action>
    <demolish>REMOVE: `const allowedKeys = { ... }` key stripping in @[client_app_v2/lib/features/execution/controllers/execution_controller.dart#L40-L61]. REPLACE WITH: Direct `ExecutionRecord.fromJson(map)` deserialization.</demolish>
    <demolish>REMOVE: `strictness_level` and `scoring_strategy` parameters in @[client_app_v2/lib/core/api/execution_client.dart#L26-L43]. REPLACE WITH: `ExecutionCreateRequestDto` payload.</demolish>
  </step>

  <step id="4" name="ATOMIC TEST SUITE MODERNIZATION & QUALITY GATES">
    <action>Modernize unit tests in @[backend_v2/tests/unit/models/test_v2_core.py], @[backend_v2/tests/unit/models/test_execution_core.py], @[backend_v2/tests/unit/core/test_registry.py], @[backend_v2/tests/unit/core/test_hook_registry.py], @[backend_v2/tests/unit/seed/test_run_seed.py], and @[client_app_v2/test/features/execution/controllers/execution_controller_test.dart] to validate strict Pydantic V2 and Freezed models.</action>
    <action>Execute the complete Phase 1 validation suite: `audit_database_atoms.py`, `run_seed.py local`, `flutter_audit_loop.py --build`, and `test_sdui_semantic_parity.py`.</action>
  </step>

  <test_contracts>
    <test name="test_execution_record_missing_target_locale_raises_validation_error" category="negative">
      <input>Raw dictionary without `target_locale` field</input>
      <expected>raises pydantic_core.ValidationError (Fail-Fast on missing locale)</expected>
    </test>
    <test name="test_hook_state_typed_inputs_instantiation" category="positive">
      <input>HookState instantiated with ExecutionInputsDTO and GlobalContextVarsDTO</input>
      <expected>instantiation succeeds; attributes access via typed dot-notation</expected>
    </test>
    <test name="test_hook_state_rejects_raw_dict_inputs" category="negative">
      <input>HookState(inputs={"raw": "value"})</input>
      <expected>raises ValidationError (strict type validation)</expected>
    </test>
    <test name="test_run_seed_clean_reset_local" category="positive">
      <input>run_seed.py executed with 'local' target</input>
      <expected>database tables recreated cleanly; execution directory purged</expected>
    </test>
    <test name="test_flutter_execution_record_full_schema_deserialization" category="positive">
      <input>Backend ExecutionRecord JSON payload with all telemetry fields</input>
      <expected>ExecutionRecord parses successfully with disallowUnrecognizedKeys: true</expected>
    </test>
    <test name="test_flutter_execution_record_unexpected_key_throws" category="negative">
      <input>JSON payload containing unmapped key `unknown_legacy_field`</input>
      <expected>throws CheckedFromJsonException / FormatException</expected>
    </test>
  </test_contracts>

  <validation_gate>
    <!-- Backend Quality Gate & Database Verification -->
    uv run python scripts/audit_database_atoms.py --strict
    uv run python backend_v2/seed/run_seed.py local
    uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/test_v2_core.py --test
    uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/models/test_execution_core.py --test
    uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/core/test_registry.py --test
    uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/core/test_hook_registry.py --test
    uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/seed/test_run_seed.py --test

    <!-- Flutter Quality Gate & Freezed Code Generation -->
    uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/ --build

    <!-- SDUI Cross-Domain Semantic Parity -->
    uv run pytest backend_v2/tests/integration/test_sdui_semantic_parity.py
  </validation_gate>
</execution_protocol>
```
