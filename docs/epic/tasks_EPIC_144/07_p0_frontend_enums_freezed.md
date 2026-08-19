# Phase 0-G: Frontend Enum & Freezed Synchronization

**Epic:** `@[docs\epic\EPIC_144_Output_Profile_Studio_UI_Modernization.md]`
**Source:** Epic Phase 0, Section 2 "Frontend Enums" (L289-L295) and Section 5 "Frontend Freezed & Code Gen Synchronisation" (L319-L329) and 6-Step Pipeline Step 4 (L251-L255)
**Scope:** Frontend Flutter/Dart and Cross-Language Enum Parity Verification

**Overview:** Synchronize Dart enums with Python enums (add `DisplayScale`, add 4 missing `TargetBlockType` members, add `SystemUiConstraints`), eradicate `unknownEnumValue` fallback parameters from Freezed models, remove `includeDiagnosticScorecard`, strictly type `maxExtensionItems`, `displayScale`, and `targetBlockOrder` with enum defaults, run Freezed code generation, and unskip Python cross-language enum parity tests.

**Target Files:**
- `[MODIFY]` `@[client_app_v2/lib/core/models/enums.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/models/output_profile.dart]`
- `[MODIFY]` `@[client_app_v2/lib/features/studio/models/blueprint_config.dart]`
- `[MODIFY]` `@[backend_v2/tests/unit/test_enum_parity.py]`

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
    <file>backend_v2/ — Do NOT touch any Python domain, service, or model files (ONLY backend_v2/tests/unit/test_enum_parity.py for unskipping parity tests)</file>
    <file>client_app_v2/lib/features/studio/views/ — Do NOT touch views yet (Phase 1)</file>
    <file>client_app_v2/lib/features/studio/controllers/ — Do NOT touch controllers yet</file>
    <file>client_app_v2/test/ — Do NOT touch test files yet (Plan 08)</file>
  </anti_targets>

  <dod_checklist>
    <item>@JsonEnum() enum DisplayScale defined in enums.dart with @JsonValue annotations matching Python DisplayScale.</item>
    <item>TargetBlockType enum in enums.dart has all 13 members matching Python TargetBlockType (4 new: matrixGraphsBlock, matrixSummaryTableBlock, varianceValidationBlock, authenticityEvaluationBlock).</item>
    <item>SystemUiConstraints enum defined with maxExtensionItemsSliderMin(1), maxExtensionItemsSliderMax(20), maxExtensionItemsAbsoluteMax(100), maxExtensionItemsDefault(3).</item>
    <item>includeDiagnosticScorecard removed from output_profile.dart Freezed model.</item>
    <item>displayScale typed as @Default(DisplayScale.original) @JsonKey(name: 'display_scale') DisplayScale displayScale.</item>
    <item>targetBlockOrder typed as @JsonKey(name: 'target_block_order') @Default([...]) List&lt;TargetBlockType&gt; targetBlockOrder with 12 enum defaults.</item>
    <item>maxExtensionItems typed as @Default(3) @JsonKey(name: 'max_extension_items') int maxExtensionItems (non-nullable).</item>
    <item>ALL unknownEnumValue fallback parameters eradicated from output_profile.dart and blueprint_config.dart.</item>
    <item>Freezed code generation passes cleanly via flutter_audit_loop.py.</item>
    <item>All skips removed from test_enum_parity.py and backend audit loop passes green.</item>
  </dod_checklist>

  <step id="1" name="ADD DisplayScale ENUM TO enums.dart">
    <action>In @[client_app_v2/lib/core/models/enums.dart], add:
```dart
/// Display scale configuration for matrix score rendering.
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
    <action>In @[client_app_v2/lib/core/models/enums.dart], add the 4 missing members to the existing `TargetBlockType` enum:
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
These MUST be added before the closing brace of `TargetBlockType`. Final count MUST be 13 members matching Python exactly.</action>
  </step>

  <step id="3" name="ADD SystemUiConstraints ENUM">
    <action>In @[client_app_v2/lib/core/models/enums.dart], add:
```dart
/// Global systemic UI constraints and bounds.
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
1. REPLACE: `@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.defaultView)` WITH: `@JsonKey(name: 'preset_view')`
2. REPLACE: `@JsonKey(name: 'text_delivery_mode', unknownEnumValue: TextDeliveryMode.full)` WITH: `@JsonKey(name: 'text_delivery_mode')`

For `SynthesisConfigDTO` Freezed class:
3. REPLACE: `@JsonKey(name: 'historical_context_mode', unknownEnumValue: HistoricalContextMode.disabled)` WITH: `@JsonKey(name: 'historical_context_mode')`

For the main `OutputProfile` Freezed class:
4. DELETE: `includeDiagnosticScorecard` field and its `@JsonKey` annotation entirely:
```dart
    @Default(false)
    @JsonKey(name: 'include_diagnostic_scorecard')
    bool includeDiagnosticScorecard,
```
5. REPLACE: `@Default('original') String displayScale,` WITH:
```dart
    @Default(DisplayScale.original)
    @JsonKey(name: 'display_scale')
    DisplayScale displayScale,
```
6. REPLACE: `targetBlockOrder` field WITH strictly typed enum list and enum defaults:
```dart
    @JsonKey(name: 'target_block_order')
    @Default([
      TargetBlockType.metadataBlock,
      TargetBlockType.executiveSummaryBlock,
      TargetBlockType.synthesisTextBlock,
      TargetBlockType.matrixGraphsBlock,
      TargetBlockType.groupedExtensionsBlock,
      TargetBlockType.penaltiesBlock,
      TargetBlockType.matrixSummaryTableBlock,
      TargetBlockType.varianceValidationBlock,
      TargetBlockType.authenticityEvaluationBlock,
      TargetBlockType.printableSourcesBlock,
      TargetBlockType.globalScoreBlock,
      TargetBlockType.auditTrailBlock,
    ])
    List<TargetBlockType> targetBlockOrder,
```
7. REPLACE: `@JsonKey(name: 'max_extension_items') int? maxExtensionItems,` WITH:
```dart
    @Default(3)
    @JsonKey(name: 'max_extension_items')
    int maxExtensionItems,
```</action>
    <demolish>REMOVE: ALL `unknownEnumValue` parameters from @JsonKey annotations in output_profile.dart (lines 18, 27, 63). REMOVE: `includeDiagnosticScorecard` field. REPLACE: nullable `int? maxExtensionItems` with non-nullable `@Default(3) @JsonKey(name: 'max_extension_items') int maxExtensionItems`.</demolish>
    <constraint invariant="discriminator_fail_fast_mandate">Freezed models MUST NOT define fallbackUnion or unknownEnumValue. Unrecognized values MUST crash via CheckedFromJsonException.</constraint>
  </step>

  <step id="5" name="MODIFY blueprint_config.dart FREEZED MODEL">
    <action>In @[client_app_v2/lib/features/studio/models/blueprint_config.dart]:
1. REPLACE: `@JsonKey(name: 'preset_view', unknownEnumValue: PresetView.metrics1d)` WITH just `@JsonKey(name: 'preset_view')`.</action>
    <demolish>REMOVE: `unknownEnumValue: PresetView.metrics1d` at @[client_app_v2/lib/features/studio/models/blueprint_config.dart#L13].</demolish>
  </step>

  <step id="6" name="RUN FREEZED CODE GENERATION">
    <action>Execute: `uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models --build`</action>
    <constraint>Code generation MUST complete without errors. The generated .freezed.dart and .g.dart files MUST NOT contain any `unknownEnumValue` annotations.</constraint>
  </step>

  <step id="7" name="UNSKIP PYTHON CROSS-LANGUAGE ENUM PARITY TESTS">
    <action>In @[backend_v2/tests/unit/test_enum_parity.py]:
1. Remove `@pytest.mark.skip(reason="Awaiting Plan 07: Frontend Enum Sync")` from `test_display_scale_parity()`.
2. Remove `@pytest.mark.skip(reason="Awaiting Plan 07: Frontend Enum Sync")` from `test_target_block_type_parity()`.
3. Execute quality audit loop: `uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test`.</action>
    <constraint>All enum parity tests MUST execute and pass 100% green with zero skips.</constraint>
  </step>

  <validation_gate>
    <check>uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/studio/models --build — passes</check>
    <check>grep_search for "unknownEnumValue" in @[client_app_v2/lib/features/studio/models/output_profile.dart] — MUST return zero results</check>
    <check>grep_search for "unknownEnumValue" in @[client_app_v2/lib/features/studio/models/blueprint_config.dart] — MUST return zero results</check>
    <check>grep_search for "includeDiagnosticScorecard" in @[client_app_v2/lib/features/studio/models/output_profile.dart] — MUST return zero results</check>
    <check>grep_search for "DisplayScale" in @[client_app_v2/lib/core/models/enums.dart] — MUST find the enum definition</check>
    <check>grep_search for "SystemUiConstraints" in @[client_app_v2/lib/core/models/enums.dart] — MUST find the enum definition</check>
    <check>Count TargetBlockType members in @[client_app_v2/lib/core/models/enums.dart] — MUST be 13</check>
    <check>uv run python scripts/backend_audit_loop.py backend_v2/tests/unit/test_enum_parity.py --test — MUST pass green with 0 skipped</check>
  </validation_gate>
</execution_protocol>
```

