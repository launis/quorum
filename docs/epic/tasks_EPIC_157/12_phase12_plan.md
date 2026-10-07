<required_context_rules>
  <rule>@[.agents/rules/00-antigravity-core.md]</rule>
  <rule>@[.agents/rules/01-python-backend.md]</rule>
  <rule>@[.agents/rules/02_flutter_desktop.md]</rule>
  <rule>@[.agents/rules/03_seed_vault.md]</rule>
  <rule>@[.agents/rules/04_directory_reference.md]</rule>
  <rule>@[.agents/rules/05_llm_architecture.md]</rule>
  <knowledge_item>@[ki_zero_permissive_typing.md]</knowledge_item>
  <knowledge_item>@[ki_god_code_prevention.md]</knowledge_item>
  <knowledge_item>@[ki_python_314_concurrency_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_epic_lifecycle_workflow.md]</knowledge_item>
  <knowledge_item>@[ki_execution_record_ssot.md]</knowledge_item>
  <knowledge_item>@[ki_dag_engine_dto_projection_rules.md]</knowledge_item>
  <knowledge_item>@[ki_tripartite_pipeline_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_opentelemetry_logfire_observability.md]</knowledge_item>
  <knowledge_item>@[ki_shared_storage_driver_architecture.md]</knowledge_item>
  <knowledge_item>@[ki_desktop_pro_tool_studio_ux.md]</knowledge_item>
  <knowledge_item>@[ki_dumb_painter_sdui.md]</knowledge_item>
  <knowledge_item>@[ki_unified_matrix_scoring_strictness.md]</knowledge_item>
  <knowledge_item>@[ki_workflow_context_governance.md]</knowledge_item>
  <knowledge_item>@[ki_execution_engine_protocol.md]</knowledge_item>
</required_context_rules>

# Phase 12: Client Permissive Map Eradication (Dart)

**Overview:** Eradicate Census R (186 non-codec `Map<String, dynamic>` occurrences across 45 hand-written Dart files in `client_app_v2/lib/`, ratcheted down from 193 in 48 files) by retyping closed models to strongly typed Freezed DTOs mirroring backend Pydantic V2 definitions and retyping open dynamic dictionaries to `Map<String, Object?>`. Implement rule `DGR005` in `scripts/_dart_guardrails.py` banning non-codec `Map<String, dynamic>`; promote `DGR001` (loose Map returns), `DGR004` (Dart lint suppressions), and `DGR005` to unconditional FATAL severity in `scripts/_dart_guardrails.py` and `scripts/flutter_audit_loop.py`; eliminate all 25 `// ignore:` suppressions across 23 Dart files (specifically: 18 redundant `invalid_annotation_target` comments across Freezed and core models, 1 `deprecated_member_use` on `DropdownButtonFormField.initialValue` in `schema_mapper.dart`, and grant generated file immunity in `_dart_guardrails.py` to `firebase_options.dart` and `l10n/gen/` files containing 6 tooling comments); ensure `ExecutionRecord.contextVariables` and `ExecutionRecord.executionTrace` mirror backend `context_variables: ContextVariablesDTO` and `execution_trace: list[ErrorTraceEvent | TombstoneEvent | TraceEvent]` with `Map<String, Object?>?` and `List<Map<String, Object?>>?`; strictly preserve the 67 serialization codec signatures matching `fromJson(\s*Map<String,\s*dynamic>\s+\w+\s*)|Map<String,\s*dynamic>\s+toJson(`; enforce 100% pass on `scripts/flutter_audit_loop.py client_app_v2/ --build` and `scripts/audit_dto_parity.py`; and lock `CURRENT_RESIDUAL_CEILINGS.r = 0` in `scripts/audit_warning_baseline.py`.

**Source:** @[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md#L622-L635] Phase 12: Client Permissive Map Eradication (Dart)

**Execution Pre-Conditions:** None (Standard Tier 2 Execution).

**Target Files (62 files to modify, 2 verified clean):**
- `[MODIFY]` @[scripts/_dart_guardrails.py#L110-L229]
- `[MODIFY]` @[scripts/flutter_audit_loop.py#L25-L170]
- `[MODIFY]` @[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L221-L227]
- `[MODIFY]` @[scripts/audit_dto_parity.py#L175-L233]
- `[MODIFY]` @[scripts/audit_warning_baseline.py#L83-L213]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/execution_record.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/execution_metadata.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/workflow_inputs.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/distilled_evaluation.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/prompt_block.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/workflow.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/model_config.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/workflow_simulation.dart]
- `[VERIFIED_CLEAN]` @[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart] (Pre-verified clean in Phase 8)
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/step_simulation.dart]
- `[VERIFIED_CLEAN]` @[client_app_v2/lib/features/studio/models/mcp_gateway.dart] (Pre-verified clean in Phase 8)
- `[MODIFY]` @[client_app_v2/lib/core/api/studio_client.dart]
- `[MODIFY]` @[client_app_v2/lib/core/api/execution_client.dart]
- `[MODIFY]` @[client_app_v2/lib/core/api/reports_client.dart]
- `[MODIFY]` @[client_app_v2/lib/core/api/sse_client.dart]
- `[MODIFY]` @[client_app_v2/lib/core/api/workflow_client.dart]
- `[MODIFY]` @[client_app_v2/lib/core/network/interceptors/error_interceptor.dart]
- `[MODIFY]` @[client_app_v2/lib/core/error/app_exception.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/widgets/result_dashboard.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/widgets/specialist_section.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/widgets/audit_trail_viewer.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/widgets/dynamic_form.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/widgets/comparison_matrix.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/widgets/workflow_selector.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/widgets/generic_grid.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/widgets/pre_mortem_card.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/widgets/score_card_radar.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/widgets/schema_mapper.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/widgets/validation_timeline_widget.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/dashboard_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/new_execution_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/views/execution_report_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/controllers/execution_controller.dart]
- `[MODIFY]` @[client_app_v2/lib/features/auth/data/auth_repository.dart]
- `[MODIFY]` @[client_app_v2/lib/features/auth/data/repositories/user_repository.dart]
- `[MODIFY]` @[client_app_v2/lib/router/router.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/blueprint_editor_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/matrix_editor_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/model_registry_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/controllers/blueprint_editor_controller.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/atom_result_dto.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/execution_metrics_dto.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/synthesis_config_dto.dart]
- `[MODIFY]` @[client_app_v2/lib/features/execution/models/tda_state.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/blueprint_config.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/gcp_location.dart]
- `[MODIFY]` @[client_app_v2/lib/features/studio/models/output_profile.dart]
- `[MODIFY]` @[client_app_v2/lib/features/reports/models/report_artifact.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/models/i18n_text.dart]
- `[MODIFY]` @[client_app_v2/lib/shared/models/sdui_block_dto.dart]

### Pre-Implementation Cleanups (Discovered Technical Debt)
1. **Redundant `invalid_annotation_target` Lint Suppressions in Freezed Models**:
   - In 18 Freezed and core model files (`atom_result_dto.dart`, `execution_metadata.dart`, `execution_create_request_dto.dart`, `execution_metrics_dto.dart`, `hydrated_atom_dto.dart`, `synthesis_config_dto.dart`, `tda_state.dart`, `blueprint_config.dart`, `gcp_location.dart`, `model_config.dart`, `output_profile.dart`, `prompt_block.dart`, `step_simulation.dart`, `workflow.dart`, `report_artifact.dart`, `i18n_text.dart`, `sdui_block_dto.dart`, `app_exception.dart`), header line 1 contains `// ignore_for_file: invalid_annotation_target`. Because `client_app_v2/analysis_options.yaml` already configures `analyzer: errors: invalid_annotation_target: ignore`, these 18 file-level suppression comments are completely redundant. Removing all 18 comments directly resolves 18 of the 25 DGR004 violations.
2. **Deprecated Parameter Suppression in `schema_mapper.dart`**:
   - In @[client_app_v2/lib/shared/widgets/schema_mapper.dart] line 36, `DropdownButtonFormField` suppresses deprecation via `// ignore: deprecated_member_use` on `initialValue: value?.toString()`. Replacing `initialValue` with `value: value?.toString()` resolves the deprecation cleanly and eliminates the `// ignore` comment.
3. **Generated File Immunity Classification in `_dart_guardrails.py`**:
   - In @[scripts/_dart_guardrails.py#L89-L107], `is_generated_dart_file` detects `.freezed.dart`, `.g.dart`, `.dart_tool/`, and standard build runner headers, but omits FlutterFire CLI generated files (`firebase_options.dart`) and Flutter localization generated files under `lib/l10n/gen/` (`app_localizations.dart`, `app_localizations_en.dart`, `app_localizations_fi.dart`). Adding explicit checks for `firebase_options.dart` and `l10n/gen` path components in `is_generated_dart_file` ensures generated tooling suppressions (`// ignore_for_file: type=lint` and `// ignore: unused_import`) do not produce false-positive violations in handwritten audits.
4. **DGR001 and DGR004 Severity Escalation to Unconditional FATAL**:
   - In @[scripts/_dart_guardrails.py#L110-L229], DGR001 (loose Map returns) and DGR004 (Dart lint suppressions) default to `WARNING` when `--strict` is not supplied. Updating both rules to unconditional FATAL severity guarantees that any loose Map return or lint suppression immediately breaks the build in both local development and CI pipelines.
5. **DGR005 Rule Implementation for Permissive Dart Maps**:
   - In @[scripts/_dart_guardrails.py#L110-L229], implement rule `DGR005` with unconditional FATAL severity matching `Map<String,\s*dynamic>` across handwritten Dart code, while exempting serialization codec signatures matching `fromJson(\s*Map<String,\s*dynamic>\s+\w+\s*)|Map<String,\s*dynamic>\s+toJson(`.
6. **Flutter Audit Loop Guardrail Enforcement**:
   - In @[scripts/flutter_audit_loop.py#L25-L170], ensure step 2 halts execution with exit code 1 if `_dart_guardrails.py` detects any fatal violations, enforcing zero-tolerance static checks before code compilation.
7. **Monotonic Ratchet Lock for Census R**:
   - In @[scripts/audit_warning_baseline.py#L83-L213], ratchet down `CURRENT_RESIDUAL_CEILINGS.r` from 186 to 0, locking client-side typing strictness in automated Stage 10 testing.

## 5-Column Architectural Directives Table

| 1. Target Scope & Boundaries | 2. Eradicated Duct-Tape (Under-Engineering Ban) | 3. Approved Best Practice (Target Invariant) | 4. Pruned Over-Engineering (Complexity Slayer) | 5. Verification & Fail-Fast (Proof Anchor) |
| :--- | :--- | :--- | :--- | :--- |
| `@[scripts/_dart_guardrails.py#L110-L229]` | Banned permissive Map usage in Dart client; banned non-fatal severity for DGR001 and DGR004; banned false-positive failures on generated FlutterFire and l10n files. | Implement `DGR005` banning non-codec `Map<String, dynamic>`; promote `DGR001`, `DGR004`, and `DGR005` to unconditional FATAL severity; extend `is_generated_dart_file` to grant immunity to `firebase_options.dart` and files under `l10n/gen/`. | Direct regular expression and path component evaluation; zero reflection. | `uv run pytest backend_v2/tests/unit/scripts/test_dart_guardrails.py` passes 100%. |
| `@[scripts/flutter_audit_loop.py#L25-L170]` | Banned bypassing Dart guardrails when `--strict` flag is omitted. | Unconditionally execute `scripts/_dart_guardrails.py` at Step 2; abort execution with non-zero exit code on any FATAL guardrail violation. | Integrated subprocess execution with direct exit code propagation. | `uv run python scripts/flutter_audit_loop.py client_app_v2/` aborts on fatal guardrail violations. |
| `@[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L221-L227]` | Banned missing unit test coverage for DGR005, unconditional FATAL severity, and generated file exemptions. | Add unit tests asserting: (1) non-codec `Map<String, dynamic>` produces FATAL DGR005 violation; (2) `fromJson` and `toJson` codec signatures produce 0 violations; (3) DGR001 and DGR004 produce FATAL severity without `--strict`; (4) `firebase_options.dart` and `l10n/gen/` files have 0 violations. | In-memory string snippet testing via `scan_dart_source`. | `uv run pytest backend_v2/tests/unit/scripts/test_dart_guardrails.py` passes 100%. |
| `@[scripts/audit_dto_parity.py#L175-L233]` | Banned drift between Python Pydantic DTOs and Flutter Freezed DTOs. | Maintain 1:1 bidirectional field name parity across shared backend and frontend models. | AST field name extraction comparing snake_case to camelCase; zero manual mapping dictionaries. | `uv run python scripts/audit_dto_parity.py` reports all 46 shared models aligned. |
| `@[scripts/audit_warning_baseline.py#L83-L213]` | Banned lingering residual debt ceiling `r > 0`. | Monotonically ratchet `CURRENT_RESIDUAL_CEILINGS.r = 0`. | Integer ceiling assertion matching live census count. | `uv run python scripts/audit_warning_baseline.py --verify-zero` passes with exit code 0. |
| 7 Models Files: `@[client_app_v2/lib/features/execution/models/execution_record.dart]`, `@[client_app_v2/lib/features/execution/models/execution_metadata.dart]`, `@[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]`, `@[client_app_v2/lib/features/execution/models/workflow_inputs.dart]`, `@[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]`, `@[client_app_v2/lib/features/execution/models/distilled_evaluation.dart]`, `@[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]` | Banned loose `Map<String, dynamic>` fields in data transfer models; banned open-ended dictionary payloads. | Retype `contextVariables`, `executionTrace`, `profileSyntheses`, `globalContextVars`, `rawInputs`, and metadata dictionaries to `Map<String, Object?>` or `List<Map<String, Object?>>`; retain `fromJson`/`toJson` codec signatures. | Direct Freezed model field retyping; regenerate serialization code via `build_runner`. | `flutter_audit_loop.py client_app_v2/ --build` compiles cleanly; DGR005 reports 0 violations. |
| 7 Studio Models & Utilities Files: `@[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]`, `@[client_app_v2/lib/features/studio/models/prompt_block.dart]`, `@[client_app_v2/lib/features/studio/models/workflow.dart]`, `@[client_app_v2/lib/features/studio/models/model_config.dart]`, `@[client_app_v2/lib/features/studio/models/workflow_simulation.dart]`, `@[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]`, `@[client_app_v2/lib/features/studio/models/mcp_gateway.dart]` | Banned loose `Map<String, dynamic>` in simulation state and workflow cloning algorithms. | Retype simulation inputs, environment maps, and cloned workflow data bags to `Map<String, Object?>`; verify `prompt_block_simulation.dart` and `mcp_gateway.dart` remain clean. | Direct typing alignment; eliminate dynamic casting. | `flutter_audit_loop.py client_app_v2/ --build` passes; unit tests verify simulation behavior. |
| 7 API Clients & Core Network Files: `@[client_app_v2/lib/core/api/studio_client.dart]`, `@[client_app_v2/lib/core/api/execution_client.dart]`, `@[client_app_v2/lib/core/api/reports_client.dart]`, `@[client_app_v2/lib/core/api/sse_client.dart]`, `@[client_app_v2/lib/core/api/workflow_client.dart]`, `@[client_app_v2/lib/core/network/interceptors/error_interceptor.dart]`, `@[client_app_v2/lib/core/error/app_exception.dart]` | Banned untyped JSON maps in HTTP client payloads, SSE event streams, and error interceptors. | Retype HTTP request bodies and JSON envelopes to `Map<String, Object?>`; decode SSE and error payload fields using typed accessors. | Direct network boundary retyping; eliminate dynamic map laundering. | DGR001 and DGR005 report 0 violations across `core/api/` and `core/network/`. |
| 11 Shared Widgets Files: `@[client_app_v2/lib/shared/widgets/result_dashboard.dart]`, `@[client_app_v2/lib/shared/widgets/specialist_section.dart]`, `@[client_app_v2/lib/shared/widgets/audit_trail_viewer.dart]`, `@[client_app_v2/lib/shared/widgets/dynamic_form.dart]`, `@[client_app_v2/lib/shared/widgets/comparison_matrix.dart]`, `@[client_app_v2/lib/shared/widgets/workflow_selector.dart]`, `@[client_app_v2/lib/shared/widgets/generic_grid.dart]`, `@[client_app_v2/lib/shared/widgets/pre_mortem_card.dart]`, `@[client_app_v2/lib/shared/widgets/score_card_radar.dart]`, `@[client_app_v2/lib/shared/widgets/schema_mapper.dart]`, `@[client_app_v2/lib/shared/widgets/validation_timeline_widget.dart]` | Banned untyped `Map<String, dynamic>` parameters, state bags, and data grids in presentation widgets; banned deprecated `initialValue` in `schema_mapper.dart`. | Retype widget data inputs to `Map<String, Object?>` or concrete domain models; update `schema_mapper.dart` to use `value: value?.toString()`; eliminate `// ignore: deprecated_member_use`. | Clean presentation typing with explicit type checks; eliminate UI duck-typing. | DGR004 and DGR005 report 0 violations across `shared/widgets/`. |
| 15 Presentation Views, Controllers & Repositories: `@[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]`, `@[client_app_v2/lib/features/execution/views/dashboard_view.dart]`, `@[client_app_v2/lib/features/execution/views/new_execution_view.dart]`, `@[client_app_v2/lib/features/execution/views/execution_report_view.dart]`, `@[client_app_v2/lib/features/execution/controllers/execution_controller.dart]`, `@[client_app_v2/lib/features/auth/data/auth_repository.dart]`, `@[client_app_v2/lib/features/auth/data/repositories/user_repository.dart]`, `@[client_app_v2/lib/router/router.dart]`, `@[client_app_v2/lib/features/studio/views/blueprint_editor_view.dart]`, `@[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]`, `@[client_app_v2/lib/features/studio/views/matrix_editor_view.dart]`, `@[client_app_v2/lib/features/studio/views/model_registry_view.dart]`, `@[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart]`, `@[client_app_v2/lib/features/studio/controllers/blueprint_editor_controller.dart]`, `@[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]` | Banned loose Map arguments in route navigation, controller state, auth payload storage, and studio editor views. | Retype controller parameters, router query maps, and studio editor dictionaries to `Map<String, Object?>` or dedicated domain models. | Single sovereign typed pipeline across presentation and state management. | DGR005 reports 0 violations across all views and controllers. |
| 12 Cleaned Freezed Models Files: `@[client_app_v2/lib/features/execution/models/atom_result_dto.dart]`, `@[client_app_v2/lib/features/execution/models/execution_metrics_dto.dart]`, `@[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart]`, `@[client_app_v2/lib/features/execution/models/synthesis_config_dto.dart]`, `@[client_app_v2/lib/features/execution/models/tda_state.dart]`, `@[client_app_v2/lib/features/studio/models/blueprint_config.dart]`, `@[client_app_v2/lib/features/studio/models/gcp_location.dart]`, `@[client_app_v2/lib/features/studio/models/output_profile.dart]`, `@[client_app_v2/lib/features/studio/models/step_simulation.dart]`, `@[client_app_v2/lib/features/reports/models/report_artifact.dart]`, `@[client_app_v2/lib/shared/models/i18n_text.dart]`, `@[client_app_v2/lib/shared/models/sdui_block_dto.dart]` | Banned redundant `// ignore_for_file: invalid_annotation_target` comments in Freezed models. | Delete the file-level suppression comment from line 1 of each file, relying on `analysis_options.yaml` SSOT configuration. | Clean model source files without lint suppressions. | DGR004 reports 0 violations across all Freezed model directories. |

```xml
<execution_protocol>
  <step id="12.0" name="STRATEGIC ALIGNMENT CHECK &amp; CENSUS R BASELINE AUDIT">
    <action>Look backward: Verify Phase 11 eradicated all loose dicts across tests, scripts, and Mapping constructs in backend_v2 with Census P=0 and Census M=0.</action>
    <action>Verify current baseline: Run `uv run python scripts/audit_warning_baseline.py --verify-zero` and confirm current ceilings (d=0, f=51, k=0, x=0, n=0, t=0, p=0, m=0, r=186, s=0).</action>
    <action>Verify live Census R count: Run `Get-ChildItem client_app_v2/lib -Recurse -Filter "*.dart" | Select-String -Pattern "Map<String,\s*dynamic>"` and verify exactly 186 non-codec matches across 45 files.</action>
    <action>Verify DGR004 lint suppressions: Count `// ignore` comments in handwritten Dart files and confirm exactly 25 occurrences across 23 files.</action>
    <action>Look forward: Verify Dart permissive map eradication locks client-side strictness before the final zero-bypass gate in Phase 13.</action>
    <constraint invariant="universal_fail_fast">If unexpected violations exist outside the residual ledger boundaries, STOP immediately and request Course Correction.</constraint>
    <directive>EPIC &amp; TRACKER SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document (@[docs/epic/EPIC_157_Zero_Permissive_Typing_and_Test_Persistence_Modernization.md]) and the Tracker document (@[docs/epic/EPIC_157_tracker.md]), and synchronize architectural corrections back into them. Update `# Session Handover Context` and set `Resume Command` to `/tier2-execute @[docs/epic/tasks_EPIC_157/12_phase12_plan.md] @[docs/epic/EPIC_157_tracker.md] --full-auto`.</directive>
  </step>

  <step id="12.1" name="DART GUARDRAILS ENGINE MODERNIZATION &amp; SEVERITY ESCALATION">
    <action>In @[scripts/_dart_guardrails.py#L110-L229]: Implement rule `DGR005` banning non-codec `Map<String, dynamic>` occurrences in handwritten Dart files using regular expression matching while exempting codec signatures `fromJson(\s*Map<String,\s*dynamic>\s+\w+\s*)|Map<String,\s*dynamic>\s+toJson(`.</action>
    <action>In @[scripts/_dart_guardrails.py#L110-L229]: Promote `DGR001` (loose Map return types), `DGR004` (Dart lint suppressions), and `DGR005` (loose Map usage) to unconditional FATAL severity, ensuring they produce fatal violations even when `--strict` is not passed.</action>
    <action>In @[scripts/_dart_guardrails.py#L89-L107]: Update `is_generated_dart_file` to grant immunity to `firebase_options.dart` and files under path `client_app_v2/lib/l10n/gen/`.</action>
    <action>In @[scripts/flutter_audit_loop.py#L25-L170]: Verify and enforce that Step 2 unconditionally executes `scripts/_dart_guardrails.py` over `client_app_v2/lib` and halts on any FATAL violation with exit code 1.</action>
    <action>In @[backend_v2/tests/unit/scripts/test_dart_guardrails.py#L221-L227]: Add unit tests asserting: (1) non-codec `Map<String, dynamic>` produces a FATAL DGR005 violation; (2) `fromJson(Map<String, dynamic> json)` and `Map<String, dynamic> toJson()` codec signatures produce 0 violations; (3) DGR001 and DGR004 produce FATAL violations without `--strict`; (4) `firebase_options.dart` and `l10n/gen/` files produce 0 violations.</action>
    <action>Execute localized unit tests: Run `uv run pytest backend_v2/tests/unit/scripts/test_dart_guardrails.py` asserting all unit tests pass 100%.</action>
    <constraint invariant="the_zero_compromise_pledge">Dart guardrails engine must enforce DGR001, DGR004, and DGR005 as unconditional FATAL gates with 100% false-positive immunity for generated files.</constraint>
  </step>

  <step id="12.2" name="DGR004 ERADICATION (LINT SUPPRESSION CLEANUP)">
    <action>In 18 Freezed and core model files (@[client_app_v2/lib/features/execution/models/atom_result_dto.dart], @[client_app_v2/lib/features/execution/models/execution_metadata.dart], @[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart], @[client_app_v2/lib/features/execution/models/execution_metrics_dto.dart], @[client_app_v2/lib/features/execution/models/hydrated_atom_dto.dart], @[client_app_v2/lib/features/execution/models/synthesis_config_dto.dart], @[client_app_v2/lib/features/execution/models/tda_state.dart], @[client_app_v2/lib/features/studio/models/blueprint_config.dart], @[client_app_v2/lib/features/studio/models/gcp_location.dart], @[client_app_v2/lib/features/studio/models/model_config.dart], @[client_app_v2/lib/features/studio/models/output_profile.dart], @[client_app_v2/lib/features/studio/models/prompt_block.dart], @[client_app_v2/lib/features/studio/models/step_simulation.dart], @[client_app_v2/lib/features/studio/models/workflow.dart], @[client_app_v2/lib/features/reports/models/report_artifact.dart], @[client_app_v2/lib/shared/models/i18n_text.dart], @[client_app_v2/lib/shared/models/sdui_block_dto.dart], @[client_app_v2/lib/core/error/app_exception.dart]): Delete the redundant line 1 comment `// ignore_for_file: invalid_annotation_target`.</action>
    <action>In @[client_app_v2/lib/shared/widgets/schema_mapper.dart]: On line 36, update `DropdownButtonFormField` replacing `initialValue: value?.toString()` with `value: value?.toString()`, and delete the comment `// ignore: deprecated_member_use`.</action>
    <action>Verify DGR004 eradication: Execute `uv run python scripts/_dart_guardrails.py client_app_v2/lib` and confirm DGR004 reports exactly 0 violations across all handwritten files.</action>
    <constraint invariant="the_zero_compromise_pledge">All handwritten Dart lint suppressions must be eradicated; analyzer rules must be enforced via analysis_options.yaml SSOT.</constraint>
  </step>

  <step id="12.3" name="BATCH 12.1: EXECUTION MODELS RETYPING">
    <action>In @[client_app_v2/lib/features/execution/models/execution_record.dart]: Retype `contextVariables` to `Map<String, Object?>?`, `executionTrace` to `List<Map<String, Object?>>?`, and `profileSyntheses` to `Map<String, Object?>?`. In `parseInBackground`, retain safe isolate decoding.</action>
    <action>In @[client_app_v2/lib/features/execution/models/execution_metadata.dart]: Retype `globalContextVars` and dynamic metadata fields to `Map<String, Object?>?`.</action>
    <action>In @[client_app_v2/lib/features/execution/models/frozen_context_snapshot.dart]: Retype raw snapshot maps to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/execution/models/workflow_inputs.dart]: Retype dynamic input payload maps to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/execution/models/report_data_v2_dto.dart]: Retype raw report data extension maps to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/execution/models/distilled_evaluation.dart]: Retype dynamic evaluation attributes to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/execution/models/execution_create_request_dto.dart]: Retype request inputs to `Map<String, Object?>`.</action>
    <action>Execute build runner code generation: Run `dart run build_runner build -d` inside `client_app_v2` to regenerate Freezed model files.</action>
    <action>In @[scripts/audit_dto_parity.py#L175-L233]: Verify all 46 shared models remain 1:1 aligned between Python and Dart.</action>
    <constraint invariant="cross_domain_dto_parity">Execution models must strictly mirror backend Pydantic models while eliminating dynamic types.</constraint>
  </step>

  <step id="12.4" name="BATCH 12.2: STUDIO MODELS &amp; UTILITIES RETYPING">
    <action>In @[client_app_v2/lib/features/studio/utils/workflow_cloner.dart]: Retype internal cloning dictionaries and mapping bags from `Map<String, dynamic>` to `Map<String, Object?>` across all 11 occurrences.</action>
    <action>In @[client_app_v2/lib/features/studio/models/prompt_block.dart]: Retype template variable dictionaries and metadata bags to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/studio/models/workflow.dart]: Retype workflow configuration bags and metadata dictionaries to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/studio/models/model_config.dart]: Retype provider configuration parameters to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/studio/models/workflow_simulation.dart]: Retype simulation parameter bags and execution context to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/studio/models/prompt_block_simulation.dart]: Retype block simulation input maps to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/studio/models/step_simulation.dart]: Retype step simulation environment maps to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/studio/models/mcp_gateway.dart]: Retype gateway tool configuration maps to `Map<String, Object?>`.</action>
    <action>Execute build runner code generation: Run `dart run build_runner build -d` inside `client_app_v2` to regenerate studio Freezed models.</action>
    <constraint invariant="the_zero_compromise_pledge">Studio models and workflow utilities must eliminate permissive dynamic maps.</constraint>
  </step>

  <step id="12.5" name="BATCH 12.3: API CLIENTS &amp; CORE NETWORK RETYPING">
    <action>In @[client_app_v2/lib/core/api/studio_client.dart]: Retype request payloads, query parameter maps, and response data envelopes from `Map<String, dynamic>` to `Map<String, Object?>` across all 36 occurrences.</action>
    <action>In @[client_app_v2/lib/core/api/execution_client.dart]: Retype execution start payloads and request body dictionaries from `Map<String, dynamic>` to `Map<String, Object?>` across all 7 occurrences.</action>
    <action>In @[client_app_v2/lib/core/api/reports_client.dart]: Retype report generation parameters and download option maps from `Map<String, dynamic>` to `Map<String, Object?>` across all 6 occurrences.</action>
    <action>In @[client_app_v2/lib/core/api/sse_client.dart]: Retype SSE event data dictionaries and header parameter maps from `Map<String, dynamic>` to `Map<String, Object?>` across all 4 occurrences.</action>
    <action>In @[client_app_v2/lib/core/api/workflow_client.dart]: Retype workflow query parameter maps from `Map<String, dynamic>` to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/core/network/interceptors/error_interceptor.dart]: Retype error response body maps and diagnostic context to `Map<String, Object?>` across all 2 occurrences.</action>
    <action>In @[client_app_v2/lib/core/error/app_exception.dart]: Retype exception detail maps and context parameter dictionaries to `Map<String, Object?>`.</action>
    <action>Verify DGR001 and DGR005 compliance across core API: Run `uv run python scripts/_dart_guardrails.py client_app_v2/lib/core` and assert 0 violations.</action>
    <constraint invariant="rfc7807_dual_reporting_mandate">API clients and network interceptors must handle strictly typed request envelopes and error payloads.</constraint>
  </step>

  <step id="12.6" name="BATCH 12.4: PRESENTATION VIEWS, CONTROLLERS &amp; SHARED WIDGETS RETYPING">
    <action>In @[client_app_v2/lib/shared/widgets/result_dashboard.dart]: Retype dashboard metric maps, breakdown dictionaries, and chart data bags from `Map<String, dynamic>` to `Map<String, Object?>` across all 26 occurrences.</action>
    <action>In @[client_app_v2/lib/shared/widgets/specialist_section.dart]: Retype specialist detail maps and persona parameter dictionaries from `Map<String, dynamic>` to `Map<String, Object?>` across all 10 occurrences.</action>
    <action>In @[client_app_v2/lib/shared/widgets/audit_trail_viewer.dart]: Retype audit event dictionaries and trace entry maps from `Map<String, dynamic>` to `Map<String, Object?>` across all 6 occurrences.</action>
    <action>In @[client_app_v2/lib/shared/widgets/dynamic_form.dart]: Retype form field value dictionaries and validation state maps from `Map<String, dynamic>` to `Map<String, Object?>` across all 6 occurrences.</action>
    <action>In @[client_app_v2/lib/shared/widgets/comparison_matrix.dart]: Retype matrix comparison cell maps and criteria breakdown bags from `Map<String, dynamic>` to `Map<String, Object?>` across all 5 occurrences.</action>
    <action>In @[client_app_v2/lib/shared/widgets/workflow_selector.dart]: Retype selector configuration maps from `Map<String, dynamic>` to `Map<String, Object?>` across all 3 occurrences.</action>
    <action>In @[client_app_v2/lib/shared/widgets/generic_grid.dart]: Retype data grid row dictionaries from `Map<String, dynamic>` to `Map<String, Object?>` across all 2 occurrences.</action>
    <action>In @[client_app_v2/lib/shared/widgets/pre_mortem_card.dart]: Retype risk parameter dictionaries from `Map<String, dynamic>` to `Map<String, Object?>` across all 2 occurrences.</action>
    <action>In @[client_app_v2/lib/shared/widgets/score_card_radar.dart]: Retype radar chart data point dictionaries from `Map<String, dynamic>` to `Map<String, Object?>` across all 2 occurrences.</action>
    <action>In @[client_app_v2/lib/shared/widgets/validation_timeline_widget.dart]: Retype timeline event parameter maps from `Map<String, dynamic>` to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/execution/views/dynamic_start_screen.dart]: Retype execution start configuration dictionaries from `Map<String, dynamic>` to `Map<String, Object?>` across all 7 occurrences.</action>
    <action>In @[client_app_v2/lib/features/execution/views/dashboard_view.dart]: Retype dashboard state bags from `Map<String, dynamic>` to `Map<String, Object?>` across all 3 occurrences.</action>
    <action>In @[client_app_v2/lib/features/execution/views/new_execution_view.dart]: Retype new execution form maps from `Map<String, dynamic>` to `Map<String, Object?>` across all 3 occurrences.</action>
    <action>In @[client_app_v2/lib/features/execution/views/execution_report_view.dart]: Retype report view parameter dictionaries from `Map<String, dynamic>` to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/execution/controllers/execution_controller.dart]: Retype controller state parameter maps from `Map<String, dynamic>` to `Map<String, Object?>` across all 2 occurrences.</action>
    <action>In @[client_app_v2/lib/features/auth/data/auth_repository.dart]: Retype auth storage maps and user credential dictionaries from `Map<String, dynamic>` to `Map<String, Object?>` across all 5 occurrences.</action>
    <action>In @[client_app_v2/lib/features/auth/data/repositories/user_repository.dart]: Retype user profile dictionaries from `Map<String, dynamic>` to `Map<String, Object?>` across all 3 occurrences.</action>
    <action>In @[client_app_v2/lib/router/router.dart]: Retype route parameter maps and extra state bags from `Map<String, dynamic>` to `Map<String, Object?>` across all 4 occurrences.</action>
    <action>In @[client_app_v2/lib/features/studio/views/blueprint_editor_view.dart]: Retype blueprint editor state dictionaries from `Map<String, dynamic>` to `Map<String, Object?>` across all 2 occurrences.</action>
    <action>In @[client_app_v2/lib/features/studio/views/mcp_gateway_view.dart]: Retype gateway view parameter maps from `Map<String, dynamic>` to `Map<String, Object?>` across all 2 occurrences.</action>
    <action>In @[client_app_v2/lib/features/studio/views/matrix_editor_view.dart]: Retype matrix editor parameter maps from `Map<String, dynamic>` to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/studio/views/model_registry_view.dart]: Retype registry view parameter maps from `Map<String, dynamic>` to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/studio/views/studio_dashboard_view.dart]: Retype studio dashboard state maps from `Map<String, dynamic>` to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/studio/controllers/blueprint_editor_controller.dart]: Retype blueprint editor controller dictionaries from `Map<String, dynamic>` to `Map<String, Object?>`.</action>
    <action>In @[client_app_v2/lib/features/studio/controllers/prompt_blocks_controller.dart]: Retype prompt block controller dictionaries from `Map<String, dynamic>` to `Map<String, Object?>`.</action>
    <action>Verify Census R across client_app_v2: Execute `uv run python scripts/_dart_guardrails.py client_app_v2/lib` and confirm 0 violations for DGR001, DGR004, and DGR005.</action>
    <constraint invariant="the_zero_compromise_pledge">Presentation views and controllers must eliminate permissive dynamic maps while preserving UI rendering fidelity.</constraint>
  </step>

  <step id="12.7" name="MONOTONIC RATCHET LOCK &amp; UNIVERSAL VERIFICATION GATE">
    <action>In @[scripts/audit_warning_baseline.py#L83-L213]: Ratchet down `CURRENT_RESIDUAL_CEILINGS.r = 0` to permanently lock Dart permissive map eradication.</action>
    <action>Execute baseline verification: Run `uv run python scripts/audit_warning_baseline.py --verify-zero` and assert that all categories (d, f, k, x, n, t, p, m, r, s) match ceiling 0 (with only f=51 remaining for Phase 13).</action>
    <action>Execute Census R verification: Run `Get-ChildItem client_app_v2/lib -Recurse -Filter "*.dart" | Select-String -Pattern "Map<String,\s*dynamic>"` and assert 0 non-codec matches.</action>
    <action>Execute DTO parity verification: Run `uv run python scripts/audit_dto_parity.py` and assert 100% parity across all 46 shared models.</action>
    <action>Execute universal Flutter audit gate: Run `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` and assert all steps pass cleanly.</action>
    <constraint invariant="universal_quality_gates">Universal audit gate must succeed with zero warnings, zero guardrail violations, and 100% build pass.</constraint>
  </step>

  <dod_checklist>
    <item>Census command R returns 0 matches across client_app_v2/lib/.</item>
    <item>DGR005 implemented in scripts/_dart_guardrails.py banning non-codec Map&lt;String, dynamic&gt;.</item>
    <item>DGR001, DGR004, and DGR005 enforced as unconditional FATAL severity in scripts/_dart_guardrails.py and scripts/flutter_audit_loop.py.</item>
    <item>All 25 Dart lint suppression comments (// ignore:) eradicated across 23 files.</item>
    <item>ExecutionRecord and ExecutionMetadata models retyped with full backend parity.</item>
    <item>uv run python scripts/flutter_audit_loop.py client_app_v2/ --build passes.</item>
    <item>uv run python scripts/audit_dto_parity.py passes with 100% model alignment.</item>
    <item>uv run python scripts/audit_warning_baseline.py --verify-zero passes with ceiling r=0.</item>
  </dod_checklist>

  <anti_targets>
    <anti_target>Do NOT retype codec signatures (fromJson/toJson) to Object? (retained strictly per contract).</anti_target>
    <anti_target>Do NOT introduce dynamic type casts in Flutter presentation widgets.</anti_target>
    <anti_target>Do NOT introduce fallback dictionary parsing chains in API client response handling.</anti_target>
    <anti_target>Do NOT re-introduce // ignore or // ignore_for_file comments to silence Dart analyzer warnings.</anti_target>
  </anti_targets>

  <validation_gate>
    <action>Execute Census R: `Get-ChildItem client_app_v2/lib -Recurse -Filter "*.dart" | Select-String -Pattern "Map<String,\s*dynamic>"` returns 0 non-codec matches.</action>
    <action>Execute DGR004: `uv run python scripts/_dart_guardrails.py client_app_v2/lib` reports 0 lint suppressions.</action>
    <action>Execute Flutter Audit: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` passes.</action>
    <action>Execute DTO Parity: `uv run python scripts/audit_dto_parity.py` passes.</action>
    <action>Execute Baseline Verification: `uv run python scripts/audit_warning_baseline.py --verify-zero` passes.</action>
  </validation_gate>
</execution_protocol>
