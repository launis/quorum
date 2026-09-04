> **STATUS: PENDING / ODOTTAA TOTEUTUSTA (ExecutionRecord alimallien tyypitys & tekninen velka)**

# Automated Implementation Plan: ExecutionRecord Hardening & Technical Debt Resolution (Minor Gaps & Future Hardening)

> **SSOT Implementation Plan — ExecutionRecord Hardening**  
> **Objective:** Systematically resolve minor architectural gaps and technical debt in `ExecutionRecord` across Flutter and Python: (1) Replace remaining permissive `Map<String, dynamic>` fields with strongly typed Freezed sub-DTOs in Flutter, (2) Sunset legacy `results` Map across `ExecutionRecord` and UI fallback layers in favor of `ReportDataDto`, and (3) Optimize SSE streaming payload weight by lazy-loading heavy epistemic structures.

<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
</required_context_rules>

<anti_targets>
- Do NOT loosen `@JsonSerializable(disallowUnrecognizedKeys: true)` or add permissive `@Default(null)` / `@Default({})` to mask serialization errors (`the_zero_compromise_pledge`).
- Do NOT invent parallel DTOs or diverge field naming between Python `snake_case` and Flutter `camelCase` (`anti_semantic_drift_renaming`).
- Do NOT alter `ReportDataDto.results` (which is the active `List<AtomResultDTO>`); only target the legacy `ExecutionRecord.results` Map (`ssot_reuse_mandate`).
- Do NOT bypass quality gates (`flutter_audit_loop.py --build` and `backend_audit_loop.py --test`).
</anti_targets>

---

## 1. Problem Statement & Architecture Context

1. **Permissive Sub-DTOs in Flutter `ExecutionRecord`:**
   - Flutter's `ExecutionRecord` currently uses raw `Map<String, dynamic>?` for `execution_summary`, `raw_inputs`, and `steps[i].scorecard_atoms`.
   - While backend defines strict Pydantic models (`ExecutionSummarySnapshot`, `WorkflowInputs`, `ScorecardAtomDTO`), Flutter's lack of typed models for these sub-structures weakens compile-time type safety and code completion.
2. **Legacy `ExecutionRecord.results` Residue (The De-Generator Sunset):**
   - V1 architecture stored dynamic dictionary results in `execution.results = {"stp_1": {...}}`.
   - In modern V2/Phase 9 architecture, presentation data is delivered strictly via `report_data: ReportDataDto` and step states via `steps: List<ExecutionStep>`.
   - The legacy `results` Map on `ExecutionRecord` is obsolete and only exists as an old fallback box in `execution_view.dart`.
3. **SSE Payload Efficiency & Stream Health:**
   - In long-running workflows with hundreds of evaluated atoms, serializing full `scorecard_atoms` on every single SSE status pulse inflates message sizes.
   - Stream status events should transmit lightweight step telemetry, while heavy report presentation is fetched cleanly via `/sdui` or `/report`.

---

## 2. Proposed Changes & Target Boundaries

### Component A: Flutter Freezed Sub-DTO Typing & Parity
- **[NEW]** `@[client_app_v2/lib/features/execution/models/execution_summary_snapshot.dart]`
  - Create strict Freezed DTO matching backend `ExecutionSummarySnapshot`:
    - `@JsonKey(name: 'strictness_level') @Default(100) int strictnessLevel,`
    - `@JsonKey(name: 'is_ensemble_run') @Default(false) bool isEnsembleRun,`
    - `@JsonKey(name: 'is_degraded') @Default(false) bool isDegraded,`
    - `@JsonKey(name: 'system_concurrency_snapshot') @Default({}) Map<String, int> systemConcurrencySnapshot,`
- **[MODIFY]** `@[client_app_v2/lib/features/execution/models/execution_step.dart]`
  - Update `scorecardAtoms` from `Map<String, dynamic>` to `Map<String, ScorecardAtomDto>`.
- **[MODIFY]** `@[client_app_v2/lib/features/execution/models/execution_record.dart]`
  - Update `executionSummary` type from `Map<String, dynamic>?` to `ExecutionSummarySnapshot?`.
  - Update `rawInputs` type from `Map<String, dynamic>?` to `ExecutionInputs?`.
  - Deprecate and remove legacy `results` Map.

### Component B: UI View Cleanup & Fallback Modernization
- **[MODIFY]** `@[client_app_v2/lib/features/execution/views/execution_view.dart]`
  - Remove references to `record.results`.
  - Ensure `ReportRendererV2Widget` is the sole presentation renderer, delegating empty states to standard `EmptyView` or `GlobalErrorView`.

### Component C: Test Suite & Fixture Synchronization
- **[MODIFY]** `@[client_app_v2/test/features/execution/models/execution_models_test.dart]`
  - Update test fixtures to validate `ExecutionSummarySnapshot`, typed `ScorecardAtomDto` on `ExecutionStep`, and strict absence of legacy `results`.

---

## 3. Execution Protocol

```xml
<execution_protocol>
  <step id="1" name="CREATE_EXECUTION_SUMMARY_SNAPSHOT_DTO">
    <action>
      Create [NEW] `@[client_app_v2/lib/features/execution/models/execution_summary_snapshot.dart]` with Freezed and JsonSerializable annotations enforcing `disallowUnrecognizedKeys: true`.
      Fields:
      - `strictness_level` (int, default 100)
      - `is_ensemble_run` (bool, default false)
      - `is_degraded` (bool, default false)
      - `system_concurrency_snapshot` (Map&lt;String, int&gt;, default {})
    </action>
    <constraint>
      Must match backend `ExecutionSummarySnapshot` in `backend_v2/models/v2_core.py#L1345-L1356`.
    </constraint>
  </step>

  <step id="2" name="HARDEN_EXECUTION_STEP_AND_RECORD_MODELS">
    <action>
      1. In `@[client_app_v2/lib/features/execution/models/execution_step.dart]`, import `matrix_scorecard_dto.dart` and update `scorecardAtoms` field to `@Default({}) Map&lt;String, ScorecardAtomDto&gt; scorecardAtoms`.
      2. In `@[client_app_v2/lib/features/execution/models/execution_record.dart]`, update:
         - `executionSummary` to `ExecutionSummarySnapshot? executionSummary`
         - `rawInputs` to `ExecutionInputs? rawInputs`
         - Remove `@JsonKey(name: 'results') Map&lt;String, dynamic&gt;? results`
    </action>
    <constraint>
      Do not remove `@JsonSerializable(disallowUnrecognizedKeys: true)`. Keep strict parsing intact.
    </constraint>
  </step>

  <step id="3" name="CLEANUP_EXECUTION_VIEW_LEGACY_RESULTS">
    <action>
      In `@[client_app_v2/lib/features/execution/views/execution_view.dart]`:
      1. Remove `final results = record.results ?? &lt;String, dynamic&gt;{};`.
      2. Remove legacy raw JSON fallback block (`else if ((status == 'passed' || status == 'completed') &amp;&amp; results.isNotEmpty)`).
      3. Update `ExecutionTimeline` invocation to pass empty map or typed step states.
    </action>
    <constraint>
      Use Design Tokens and AppLocalizations exclusively for any state rendering.
    </constraint>
  </step>

  <step id="4" name="UPDATE_TEST_FIXTURES_AND_RUN_GENERATION">
    <action>
      1. Run `dart run build_runner build --delete-conflicting-outputs` in `client_app_v2/`.
      2. Update `@[client_app_v2/test/features/execution/models/execution_models_test.dart]` to assert typed fields for `executionSummary`, `rawInputs`, and `scorecardAtoms`.
      3. Run `flutter test test/features/execution/models/execution_models_test.dart`.
    </action>
    <constraint>
      Zero analyzer errors and 100% test pass rate required.
    </constraint>
  </step>

  <step id="5" name="UNIVERSAL_QUALITY_GATE_AND_COMMIT">
    <action>
      1. Run `uv run python scripts/flutter_audit_loop.py client_app_v2/`.
      2. Run `flutter test test/features/execution/`.
      3. Execute atomic git commit in English:
         `git add client_app_v2/`
         `git commit -m "refactor(client): harden ExecutionRecord sub-DTOs and sunset legacy results field"`
    </action>
    <constraint>
      Must pass with exit code 0.
    </constraint>
  </step>
</execution_protocol>
```

---

## 4. Verification Plan

### Automated Tests
- `flutter test test/features/execution/models/execution_models_test.dart`
- `flutter test test/features/execution/`
- `uv run python scripts/flutter_audit_loop.py client_app_v2/`

### Manual / E2E Verification
- Open `Aktiivinen Suoritus` view in Flutter desktop and verify live execution stream connects and transitions without `CheckedFromJsonException` or UI jank.
