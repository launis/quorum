# Phase 1-A: Golden Master Test Baseline

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 1, "Pre-Refactoring Golden Master Test Baseline" (L365-L367) and God Code Prevention KI `remedial_refactoring_coverage`
**Scope:** Frontend Flutter/Dart test only

**Overview:** Create a Golden Master (Characterization Test) baseline for `output_profile_crud_view.dart` (856 lines) to lock existing form behavior BEFORE the 3-tab decomposition in Plan 11. This is mandatory per `remedial_refactoring_coverage` in `@[ki_god_code_prevention.md]`.

**Target Files:**
- `[NEW]` `@[client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart]`

**Context Files (Read-Only):**
- `@[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart]` — 856-line monolithic view to be characterized
- `@[client_app_v2/lib/features/studio/controllers/output_profile_controller.dart]` — Form state controller

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Plan 09 (Phase 0 Integration Checkpoint) passed completely — all cross-stack quality gates green.</action>
    <action>Look forward: Verify @[client_app_v2/lib/features/studio/views/output_profile_crud_view.dart] exists at ~856 lines and has NOT been decomposed yet.</action>
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
    <item>[NEW] output_profile_crud_view_test.dart exists with widget tests locking current form behavior.</item>
    <item>Tests verify: form renders without overflow, key form fields are present (profile name, description, workflow selector), save button is accessible.</item>
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
1. Test that the form renders without assertion errors when given a valid OutputProfile.
2. Test that key form fields (profile name TextField, description TextField, workflow dropdown) are findable in the widget tree.
3. Test that the form validates required fields.
4. Test that the save action triggers the correct provider method.

Use `ProviderScope` overrides and mock providers as needed. The goal is NOT comprehensive UI testing — it is establishing a BASELINE that will break if Plan 11's decomposition changes behavior unexpectedly.</action>
    <test_contracts>
      <test name="test_crud_view_renders_without_errors" category="positive">
        <input>Valid OutputProfile with mocked providers</input>
        <expected>Widget tree renders without assertion crashes</expected>
      </test>
      <test name="test_crud_view_displays_profile_name" category="positive">
        <input>OutputProfile with name "Test Profile"</input>
        <expected>finds TextFormField containing "Test Profile"</expected>
      </test>
      <test name="test_crud_view_displays_workflow_selector" category="positive">
        <input>Valid OutputProfile with mocked workflow list</input>
        <expected>finds DropdownButtonFormField widget</expected>
      </test>
    </test_contracts>
  </step>

  <validation_gate>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/output_profile_crud_view_test.dart --test — passes green</check>
  </validation_gate>
</execution_protocol>
```
