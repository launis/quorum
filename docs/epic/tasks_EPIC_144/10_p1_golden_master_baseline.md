# Phase 1-A: Golden Master Test Baseline

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 1, "Pre-Refactoring Golden Master Test Baseline" (L365-L367) and God Code Prevention KI `remedial_refactoring_coverage`
**Scope:** Frontend Flutter/Dart test only

**Overview:** Create a Golden Master (Characterization Test) baseline for `output_profile_crud_view.dart` (897 lines) to lock existing form behavior BEFORE the 3-tab decomposition in Plan 11. This is mandatory per `remedial_refactoring_coverage` in `@[ki_god_code_prevention.md]`.

**Target Files:**
- `[NEW]` `@[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart]`

**Context Files (Read-Only):**
- `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` — 897-line monolithic view to be characterized
- `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]` — Form state controller

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Plan 09 (Phase 0 Integration Checkpoint) passed completely — all cross-stack quality gates green.</action>
    <action>Look forward: Verify @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart] exists at ~897 lines and has NOT been decomposed yet.</action>
    <constraint>If Phase 0 integration checkpoint did not pass, STOP. Do NOT begin Phase 1.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\02_flutter_desktop.md]</rule>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_ast_guardrail_testing.md]</ki>
    <ki>@[ki_epic_lifecycle_workflow.md]</ki>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>client_app_v2/lib/features/studio/views/output_profile_crud_view.dart — Do NOT modify the view yet (Plan 11)</file>
    <file>backend_v2/ — Do NOT touch any Python files</file>
  </anti_targets>

  <dod_checklist>
    <item>[NEW] output_profile_crud_view_test.dart exists with widget tests locking current form behavior across loading, error, and data states.</item>
    <item>Tests verify: form renders without overflow in wide (3-pane Row) and narrow (ListView) layouts, key form fields are present (profile ID, slug, name, description, custom preface, workflow selector, display scale, strictness level, scoring strategy, visible metadata, max extension items, block/workflow extensions, layout editor card, target block order), save and delete buttons are accessible.</item>
    <item>Anti-Happy-Path test coverage: at least 2 negative test cases (AsyncError state rendering, empty workflowId warning, invalid maxExtensionItems input validation, save action exception handling).</item>
    <item>Test baseline passes green: uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart --test</item>
  </dod_checklist>

  <step id="1" name="ANALYZE CURRENT VIEW STRUCTURE">
    <action>Read @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart] to understand:
1. Widget tree structure and key form elements.
2. Provider dependencies (Riverpod providers used).
3. State management pattern (form key, controllers).
4. Critical user interaction paths (save, cancel, dropdown selections).</action>
    <constraint>Do NOT modify the view. Only read and analyze.</constraint>
  </step>

  <step id="2" name="CREATE GOLDEN MASTER WIDGET TESTS">
    <action>Create [NEW] @[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart] with Characterization Tests that lock the CURRENT behavior:
1. Define Mock classes using mocktail: `MockStudioClient`, `MockLoggerService`, `MockOutputProfilesController`, `TestOutputProfileForm`.
2. Construct helper widget builder `createWidgetUnderTest({WidgetRef? ref, AsyncValue<OutputProfile>? formStateOverride, ...})` with complete `ProviderScope` overrides and `MaterialApp` localizations.
3. Test that the form renders `CircularProgressIndicator` when `formState` is `AsyncLoading`.
4. Test that the form renders `ErrorView` when `formState` is `AsyncError`.
5. Test that the form renders without assertion crashes on wide screen (3-pane Row layout) and narrow screen (ListView layout) when given a valid `OutputProfile`.
6. Test that all identity, scoring, and metadata fields are findable in the widget tree.
7. Test that the workflow selector dropdown displays available workflows and populates extension checkboxes.
8. Test that an empty `workflowId` renders the `workflowSelectWarning` Card instead of `LayoutEditorCard`.
9. Test that invalid `maxExtensionItems` input triggers validation error on form save.
10. Test that tapping the save button triggers `submit` on `OutputProfileForm`.
11. Test that save failures display an error SnackBar via `ScaffoldMessenger`.

The goal is establishing a comprehensive characterization BASELINE that will catch any unintended behavior drift during Plan 11's 3-tab decomposition.</action>
    <test_contracts>
      <test name="test_crud_view_renders_loading_state" category="positive">
        <input>outputProfileFormProvider overridden with AsyncLoading</input>
        <expected>finds CircularProgressIndicator widget in AppBar body</expected>
      </test>
      <test name="test_crud_view_renders_error_state" category="negative">
        <input>outputProfileFormProvider overridden with AsyncError</input>
        <expected>finds ErrorView widget displaying the error message</expected>
      </test>
      <test name="test_crud_view_renders_data_state_wide_screen" category="positive">
        <input>Valid OutputProfile with 1920x1080 viewport</input>
        <expected>renders 3-pane Row layout (Identity, Layout, TargetBlockOrder) without assertion or overflow errors</expected>
      </test>
      <test name="test_crud_view_renders_data_state_narrow_screen" category="positive">
        <input>Valid OutputProfile with 800x600 viewport</input>
        <expected>renders single-column ListView layout without assertion or overflow errors</expected>
      </test>
      <test name="test_crud_view_displays_identity_and_scoring_fields" category="positive">
        <input>OutputProfile with name "Executive Summary Profile", slug "exec-summary", strictness balanced</input>
        <expected>finds TextFormField containing ID and slug, finds display name, finds strictness and scoring strategy dropdowns</expected>
      </test>
      <test name="test_crud_view_displays_workflow_selector_and_extensions" category="positive">
        <input>Valid OutputProfile with workflowId "wf_test" and available extensions ["citation", "justification"]</input>
        <expected>finds DropdownButtonFormField with "wf_test", finds CheckboxListTile for citation and justification</expected>
      </test>
      <test name="test_crud_view_displays_workflow_warning_when_unselected" category="negative">
        <input>OutputProfile with empty workflowId ""</input>
        <expected>finds workflowSelectWarning text inside Layout pane</expected>
      </test>
      <test name="test_crud_view_validates_max_extension_items" category="negative">
        <input>OutputProfile with maxExtensionItems set to invalid string "-5" or "abc"</input>
        <expected>Form validation fails and displays extensionItemsMustBeIntError</expected>
      </test>
      <test name="test_crud_view_triggers_save_action" category="positive">
        <input>Valid OutputProfile, tap save button</input>
        <expected>Form submits updated payload to OutputProfileForm notifier</expected>
      </test>
      <test name="test_crud_view_handles_save_failure_gracefully" category="negative">
        <input>OutputProfileForm submit throws AppException</input>
        <expected>ScaffoldMessenger displays error SnackBar, widget tree does not crash</expected>
      </test>
    </test_contracts>
  </step>

  <validation_gate>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart --test — passes green</check>
  </validation_gate>
</execution_protocol>
```
