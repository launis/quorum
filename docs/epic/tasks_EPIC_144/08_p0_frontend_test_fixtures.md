# Phase 0-H: Frontend Test Fixtures & Negative Tests

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 0, Section 6 "Frontend Tests" (L341-L346) and Phase 5 Negative Tests (L664-L666)
**Scope:** Frontend Flutter/Dart test files only

**Overview:** Update frontend Freezed deserialization tests to match the new strictly typed models, and add negative tests verifying that unmapped enum values, unrecognized JSON keys, and legacy fields throw `CheckedFromJsonException`.

**Target Files:**
- `[MODIFY]` `@[client_app_v2/test/features/studio/models/output_profile_test.dart]`
- `[MODIFY]` `@[client_app_v2/test/features/studio/controllers/output_profile_controller_test.dart]`
- `[MODIFY]` `@[client_app_v2/test/features/studio/views/widgets/profile/layout_editor_card_test.dart]`
- `[NEW]` `@[client_app_v2/test/features/studio/models/blueprint_config_test.dart]`

**Context Files (Read-Only):**
- `@[client_app_v2/lib/features/studio/models/output_profile.dart]` — Updated Freezed model (Plan 07)
- `@[client_app_v2/lib/features/studio/models/blueprint_config.dart]` — Updated Freezed model (Plan 07)
- `@[client_app_v2/lib/core/models/enums.dart]` — Updated enums (Plan 07)

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Plan 07 (Frontend Enum & Freezed Sync) is complete — Freezed code generation passed, unknownEnumValue eradicated, enum parity tests pass.</action>
    <action>Look forward: Verify that test files still reference old fixtures with include_diagnostic_scorecard or string-typed targetBlockOrder.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\02_flutter_desktop.md]</rule>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
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
    <file>backend_v2/ — Do NOT touch any Python files</file>
    <file>client_app_v2/lib/ — Do NOT modify source files (already done in Plan 07)</file>
  </anti_targets>

  <dod_checklist>
    <item>output_profile_test.dart fixtures updated with DisplayScale, typed targetBlockOrder, no includeDiagnosticScorecard.</item>
    <item>output_profile_test.dart has negative tests: unmapped PresetView, TextDeliveryMode, HistoricalContextMode, DisplayScale, TargetBlockType strings throw CheckedFromJsonException. Unrecognized JSON keys at root and nested levels throw CheckedFromJsonException.</item>
    <item>[NEW] blueprint_config_test.dart asserts CheckedFromJsonException on unmapped preset_view strings.</item>
    <item>output_profile_controller_test.dart fixtures aligned.</item>
    <item>layout_editor_card_test.dart fixtures aligned.</item>
  </dod_checklist>

  <step id="1" name="UPDATE output_profile_test.dart">
    <action>In @[client_app_v2/test/features/studio/models/output_profile_test.dart]:
1. Update all positive test fixtures to use DisplayScale enum values and typed targetBlockOrder with valid TargetBlockType values.
2. Remove any includeDiagnosticScorecard from test fixtures.
3. Add comprehensive negative deserialization tests.</action>
    <test_contracts>
      <test name="test_output_layout_block_unknown_preset_view_throws" category="negative">
        <input>JSON with preset_view: "unknown_preset"</input>
        <expected>throws CheckedFromJsonException</expected>
      </test>
      <test name="test_output_layout_block_unknown_text_delivery_mode_throws" category="negative">
        <input>JSON with text_delivery_mode: "invalid_mode"</input>
        <expected>throws CheckedFromJsonException</expected>
      </test>
      <test name="test_synthesis_config_dto_unknown_historical_context_mode_throws" category="negative">
        <input>JSON with historical_context_mode: "invalid"</input>
        <expected>throws CheckedFromJsonException</expected>
      </test>
      <test name="test_output_profile_unknown_display_scale_throws" category="negative">
        <input>JSON with display_scale: "invalid_scale"</input>
        <expected>throws CheckedFromJsonException</expected>
      </test>
      <test name="test_output_profile_unknown_target_block_type_throws" category="negative">
        <input>JSON with target_block_order containing "invalid_block"</input>
        <expected>throws CheckedFromJsonException</expected>
      </test>
      <test name="test_output_profile_extra_root_key_throws" category="negative">
        <input>Valid JSON + "include_diagnostic_scorecard": true at root</input>
        <expected>throws CheckedFromJsonException (disallowUnrecognizedKeys)</expected>
      </test>
      <test name="test_output_profile_extra_key_in_synthesis_config_throws" category="negative">
        <input>Valid JSON with synthesis object containing "ghost_key": true</input>
        <expected>throws CheckedFromJsonException (nested disallowUnrecognizedKeys)</expected>
      </test>
      <test name="test_output_profile_extra_key_in_layout_throws" category="negative">
        <input>Valid JSON with layouts[] entry containing "ghost_key": true</input>
        <expected>throws CheckedFromJsonException (nested disallowUnrecognizedKeys)</expected>
      </test>
      <test name="test_output_profile_valid_deserialization" category="positive">
        <input>Complete valid JSON with all required fields</input>
        <expected>Deserializes successfully with correct types</expected>
      </test>
    </test_contracts>
  </step>

  <step id="2" name="CREATE blueprint_config_test.dart">
    <action>Create [NEW] @[client_app_v2/test/features/studio/models/blueprint_config_test.dart].</action>
    <test_contracts>
      <test name="test_blueprint_config_unknown_preset_view_throws" category="negative">
        <input>JSON with preset_view: "invalid_preset"</input>
        <expected>throws CheckedFromJsonException</expected>
      </test>
      <test name="test_blueprint_config_valid_preset_view" category="positive">
        <input>JSON with preset_view: "1d_metrics"</input>
        <expected>Deserializes to BlueprintConfig with PresetView.metrics1d</expected>
      </test>
      <test name="test_blueprint_config_extra_key_throws" category="negative">
        <input>JSON with valid preset_view + "extra_field": true</input>
        <expected>throws CheckedFromJsonException (disallowUnrecognizedKeys)</expected>
      </test>
    </test_contracts>
  </step>

  <step id="3" name="UPDATE output_profile_controller_test.dart">
    <action>In @[client_app_v2/test/features/studio/controllers/output_profile_controller_test.dart]:
1. Update mock OutputProfile fixtures to match the new schema.
2. Remove includeDiagnosticScorecard from mocks.
3. Ensure maxExtensionItems is non-nullable int (default 3).</action>
  </step>

  <step id="4" name="UPDATE layout_editor_card_test.dart">
    <action>In @[client_app_v2/test/features/studio/views/widgets/profile/layout_editor_card_test.dart]:
1. Update OutputLayoutBlock test fixtures.
2. Remove any unknownEnumValue fallback assumptions.</action>
  </step>

  <validation_gate>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/models/output_profile_test.dart --test</check>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/models/blueprint_config_test.dart --test</check>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/controllers/output_profile_controller_test.dart --test</check>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/test/features/studio/views/widgets/profile/layout_editor_card_test.dart --test</check>
  </validation_gate>
</execution_protocol>
```
