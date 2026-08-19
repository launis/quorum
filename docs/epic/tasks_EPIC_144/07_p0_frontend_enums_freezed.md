# Phase 0-G: Frontend Enum & Freezed Synchronization

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 0, Section 2 "Frontend Enums" (L289-L295) and Section 5 "Frontend Freezed & Code Gen Synchronisation" (L319-L329) and 6-Step Pipeline Step 4 (L251-L255)
**Scope:** Frontend Flutter/Dart only

**Overview:** Synchronize Dart enums with Python enums (add `DisplayScale`, add 4 missing `TargetBlockType` members, add `SystemUiConstraints`), eradicate `unknownEnumValue` fallback parameters from Freezed models, remove `includeDiagnosticScorecard`, strictly type `maxExtensionItems` and `targetBlockOrder`, and run Freezed code generation.

**Target Files:**
- `[MODIFY]` `@[client_app_v2/lib/core/models/enums.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/models/output_profile.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/models/blueprint_config.dart]`

**Context Files (Read-Only):**
- `@[backend_v2/models/enums.py]` — Python enum definitions (SSOT for parity)
- `@[backend_v2/models/v2_core.py]` — Updated OutputProfile schema
- `@[backend_v2/models/dtos/output_profile.py]` — Updated DTOs

```xml
<execution_protocol>
  <step id="0" name="STRATEGIC ALIGNMENT CHECK">
    <action>Look backward: Verify Plan 06 (OpenAPI Sync Gate) is complete — full backend test suite passes green.</action>
    <action>Look forward: Verify @[client_app_v2/lib/core/models/enums.dart] does NOT contain `DisplayScale` yet, TargetBlockType has only 9 members (missing 4), and `SystemUiConstraints` does not exist.</action>
    <constraint>If alignment is broken, STOP and request Course Correction.</constraint>
    <directive>EPIC SYNC MANDATE: If this plan is mutated during Tier 0 analysis, you MUST simultaneously open the parent Epic document and synchronize the architectural corrections back into the Epic.</directive>
  </step>

  <required_context_rules>
    <rule>@[.agents\rules\00-antigravity-core.md]</rule>
    <rule>@[.agents\rules\02_flutter_desktop.md]</rule>
    <rule>@[.agents\rules\04_directory_reference.md]</rule>
    <ki>@[ki_strict_sdui_serialization.md]</ki>
    <ki>@[ki_dual_axis_localization_architecture.md]</ki>
    <ki>@[ki_global_config_sovereignty.md]</ki>
    <ki>@[ki_god_code_prevention.md]</ki>
    <ki>@[ki_sdui_adapter_pattern.md]</ki>
    <ki>@[ki_tripartite_pipeline_architecture.md]</ki>
    <ki>@[ki_flat_polymorphic_pipeline.md]</ki>
    <ki>@[ki_sdui_matrix_synthesis.md]</ki>
    <ki>@[ki_python_314_concurrency_strictness.md]</ki>
    <ki>@[ki_ai_testing_standards.md]</ki>
    <ki>@[ki_ast_guardrail_testing.md]</ki>
    <ki>@[ki_epic_lifecycle_workflow.md]</ki>
    <ki>@[ki_synthesis_payload_compression.md]</ki>
    <ki>@[ki_dag_engine_dto_projection_rules.md]</ki>
    <ki>@[ki_matrix_boolean_evaluation_strictness.md]</ki>
  </required_context_rules>

  <anti_targets>
    <file>backend_v2/ — Do NOT touch any Python files</file>
    <file>client_app_v2/lib/features/studio/views/ — Do NOT touch views yet (Phase 1)</file>
    <file>client_app_v2/lib/features/studio/controllers/ — Do NOT touch controllers yet</file>
    <file>client_app_v2/test/ — Do NOT touch test files yet (Plan 08)</file>
  </anti_targets>

  <dod_checklist>
    <item>@JsonEnum() enum DisplayScale defined in enums.dart with @JsonValue annotations matching Python DisplayScale.</item>
    <item>TargetBlockType enum in enums.dart has all 13 members matching Python TargetBlockType (4 new: matrixGraphsBlock, matrixSummaryTableBlock, varianceValidationBlock, authenticityEvaluationBlock).</item>
    <item>SystemUiConstraints enum defined with maxExtensionItemsSliderMin(1), maxExtensionItemsSliderMax(20), maxExtensionItemsAbsoluteMax(100), maxExtensionItemsDefault(3).</item>
    <item>includeDiagnosticScorecard removed from output_profile.dart Freezed model.</item>
    <item>displayScale typed as DisplayScale (not String).</item>
    <item>targetBlockOrder typed as List&lt;TargetBlockType&gt; (not List&lt;String&gt;).</item>
    <item>maxExtensionItems typed as @Default(3) int (non-nullable).</item>
    <item>ALL unknownEnumValue fallback parameters eradicated from output_profile.dart and blueprint_config.dart.</item>
    <item>Freezed code generation passes cleanly.</item>
  </dod_checklist>

  <step id="1" name="ADD DisplayScale ENUM TO enums.dart">
    <action>In @[client_app_v2/lib/core/models/enums.dart], add:
```dart
@JsonEnum()
enum DisplayScale {
  @JsonValue('original')
  original,
  @JsonValue('custom')
  custom,
  @JsonValue('normalized_100')
  normalized100,
}
```</action>
    <constraint invariant="polymorphic_sdui_serialization">Dart @JsonValue annotations MUST match Python StrEnum member values character-for-character.</constraint>
  </step>

  <step id="2" name="ADD MISSING TargetBlockType MEMBERS">
    <action>In @[client_app_v2/lib/core/models/enums.dart], add the 4 missing members to the existing `TargetBlockType` enum (currently at L366-L385, has 9 members):
```dart
  @JsonValue('matrix_graphs_block')
  matrixGraphsBlock,
  @JsonValue('matrix_summary_table_block')
  matrixSummaryTableBlock,
  @JsonValue('variance_validation_block')
  varianceValidationBlock,
  @JsonValue('authenticity_evaluation_block')
  authenticityEvaluationBlock,
```
These MUST be added before the closing brace. Final count MUST be 13 members matching Python exactly.</action>
  </step>

  <step id="3" name="ADD SystemUiConstraints ENUM">
    <action>In @[client_app_v2/lib/core/models/enums.dart], add:
```dart
enum SystemUiConstraints {
  maxExtensionItemsSliderMin(1),
  maxExtensionItemsSliderMax(20),
  maxExtensionItemsAbsoluteMax(100),
  maxExtensionItemsDefault(3);

  const SystemUiConstraints(this.value);
  final int value;
}
```</action>
    <constraint invariant="frontend_enum_parity_mandate">All systemic UI constraints MUST be centralized in enums.dart. NO raw magic numbers in widget trees.</constraint>
  </step>

  <step id="4" name="MODIFY output_profile.dart FREEZED MODEL">
    <action>In @[client_app_v2/lib/features/studio/models/output_profile.dart]:

For `OutputLayoutBlock` Freezed class:
1. DELETE: `@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView)` → REPLACE WITH: `@JsonKey(name: 'preset_view')` (remove unknownEnumValue).
2. DELETE: `unknownEnumValue: TextDeliveryMode.full` from the text_delivery_mode @JsonKey → REPLACE WITH just `@JsonKey(name: 'text_delivery_mode')`.

For `SynthesisConfigDTO` Freezed class:
3. DELETE: `unknownEnumValue: HistoricalContextMode.disabled` from the historical_context_mode @JsonKey → REPLACE WITH just `@JsonKey(name: 'historical_context_mode')`.

For the main `OutputProfile` Freezed class (if it exists in this file):
4. DELETE: `includeDiagnosticScorecard` field entirely.
5. CHANGE: `displayScale` type to `DisplayScale` (import from enums.dart).
6. CHANGE: `targetBlockOrder` type to `List<TargetBlockType>` (import from enums.dart).
7. CHANGE: `maxExtensionItems` to `@Default(3) @JsonKey(name: 'max_extension_items') int maxExtensionItems` (non-nullable, remove `int?`).</action>
    <demolish>REMOVE: ALL `unknownEnumValue` parameters from @JsonKey annotations in output_profile.dart (currently at L18, L27, L63). REMOVE: `includeDiagnosticScorecard` field. REPLACE: nullable `int? maxExtensionItems` with non-nullable `@Default(3) int maxExtensionItems`.</demolish>
    <constraint invariant="discriminator_fail_fast_mandate">Freezed models MUST NOT define fallbackUnion or unknownEnumValue. Unrecognized values MUST crash via CheckedFromJsonException.</constraint>
  </step>

  <step id="5" name="MODIFY blueprint_config.dart FREEZED MODEL">
    <action>In @[client_app_v2/lib/features/studio/models/blueprint_config.dart]:
1. DELETE: `unknownEnumValue: PresetView.metrics1d` from the @JsonKey at L13 → REPLACE WITH just `@JsonKey(name: 'preset_view')`.</action>
    <demolish>REMOVE: `unknownEnumValue: PresetView.metrics1d` at @[client_app_v2/lib/features/studio/models/blueprint_config.dart#L13].</demolish>
  </step>

  <step id="6" name="RUN FREEZED CODE GENERATION">
    <action>Execute: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build`</action>
    <constraint>Code generation MUST complete without errors. The generated .freezed.dart and .g.dart files MUST NOT contain any `unknownEnumValue` annotations.</constraint>
  </step>

  <validation_gate>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models/output_profile.dart --build — passes</check>
    <check>grep_search for "unknownEnumValue" in @[client_app_v2/lib/features/studio/models/output_profile.dart] — MUST return zero results</check>
    <check>grep_search for "unknownEnumValue" in @[client_app_v2/lib/features/studio/models/blueprint_config.dart] — MUST return zero results</check>
    <check>grep_search for "includeDiagnosticScorecard" in @[client_app_v2/lib/features/studio/models/output_profile.dart] — MUST return zero results</check>
    <check>grep_search for "DisplayScale" in @[client_app_v2/lib/core/models/enums.dart] — MUST find the enum definition</check>
    <check>grep_search for "SystemUiConstraints" in @[client_app_v2/lib/core/models/enums.dart] — MUST find the enum definition</check>
    <check>Count TargetBlockType members in @[client_app_v2/lib/core/models/enums.dart] — MUST be 13</check>
    <check>Unskip test_display_scale_parity and test_target_block_type_parity in [NEW from Plan 01] backend_v2/tests/unit/test_enum_parity.py and re-run: uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test — MUST pass green</check>
  </validation_gate>
</execution_protocol>
```
