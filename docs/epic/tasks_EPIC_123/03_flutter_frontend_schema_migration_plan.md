# Phase 3: Flutter Frontend Schema, Enum & Mock Migration Plan

This plan migrates the Dart Freezed models and Enums to perfectly mirror the Python backend changes from Phase 2.

### Human Overview
- **Target Files**: `client_app_v2/lib/core/models/enums.dart`, `client_app_v2/lib/shared/models/sdui_block_dto.dart`, `client_app_v2/lib/features/execution/models/matrix_scorecard_dto.dart`, `client_app_v2/lib/features/execution/models/report_data_v2_dto.dart`.
- **Test Files**: `client_app_v2/test/features/execution/models/matrix_scorecard_dto_test.dart`, `client_app_v2/test/features/execution/models/report_data_v2_dto_test.dart`.
- **Goals**: Implement strict typing (removing `List<dynamic>`), delete `GlobalSynthesisDto`, sync `AlertSeverity` and `UiVariant`, and migrate legacy fields in matrices to `innerSduiBlocks`.

```xml
<system_prompt>
  <objective>Atomically mirror Python schema changes in Dart Freezed models and update Dart mock fixtures.</objective>
  <role>Principal Solutions Architect</role>
  
  <execution_protocol level="2_execute">
    <step id="1" name="ENUM SYNCHRONIZATION">
      <action>Modify @[c:\src\quorum\client_app_v2\lib\core\models\enums.dart] to match the backend exactly.</action>
      <action>Add `error` to the existing `@JsonEnum() enum VisualIntent` with `@JsonValue('error')`.</action>
      <action>Create a NEW `@JsonEnum() enum AlertSeverity` with explicit `@JsonValue` mappings: `info` ('info'), `warning` ('warning'), `criticalOverride` ('critical_override'), `success` ('success'), `error` ('error').</action>
      <action>Create a NEW `@JsonEnum() enum UiVariant` with explicit `@JsonValue` mappings: `defaultVariant` ('default' - avoid reserved keyword), `success` ('success'), `warning` ('warning'), `error` ('error'), `neutral` ('neutral').</action>
      <constraint invariant="cross_language_enum_parity">Enums must perfectly mirror Python `VisualIntent` and `UiVariant` without fallback duct-tape. Map Python's `AlertBlock.severity` Literal strictly.</constraint>
    </step>

    <step id="2" name="SDUI BLOCK DTO MIGRATION">
      <action>Modify @[c:\src\quorum\client_app_v2\lib\shared\models\sdui_block_dto.dart].</action>
      <action>Update `SduiAlertBoxBlock.severity` to use the new `AlertSeverity` enum instead of a raw String.</action>
      <action>Update `SduiGridBlock.items` to strictly `List<SduiBlockDTO>` (as grid items can contain complex blocks, per the Polymorphic Serialization KI).</action>
      <action>Update `SduiQuoteCard.citations` to strictly `List<int>`.</action>
      <constraint invariant="the_no_legacy_mandate">Ensure `List<dynamic>` is eradicated in these SDUI blocks to enforce type safety. If the backend passes unstructured `list[Any]`, this will intentionally trigger the Fail-Fast parser constraint.</constraint>
    </step>

    <step id="3" name="REPORT DATA V2 DTO MIGRATION">
      <action>Modify @[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart].</action>
      <demolish>REMOVE: `globalSynthesis` field from `ReportDataDto`.</demolish>
      <action>Delete the file @[c:\src\quorum\client_app_v2\lib\features\execution\models\global_synthesis_dto.dart] to entirely remove `GlobalSynthesisDto`.</action>
      <constraint invariant="sdui_contract_fracture_prevention">Verify these changes mirror Phase 2 exactly.</constraint>
    </step>

    <step id="4" name="MATRIX SCORECARD DTO MIGRATION">
      <action>Modify @[c:\src\quorum\client_app_v2\lib\features\execution\models\matrix_scorecard_dto.dart].</action>
      <demolish>REMOVE: legacy string fields (`coaching`, `falsification`, `missingContext`, `riskFlag`, `remediationSteps`, `emotionalSentiment`, `theoryLink`) from `MatrixScorecardRowDto`. REMOVE: `// Epic 6:` and `// Epic 88:` comments.</demolish>
      <action>Add `innerSduiBlocks` typed as `List<SduiBlockDTO>` (defaulting to empty list `[]`) to `MatrixScorecardRowDto`.</action>
      <action>Retain the `confidence` numeric field (double?).</action>
    </step>

    <step id="5" name="TEST FIXTURE SYNC">
      <action>Update test files to align with the new schema constraints.</action>
      <action>Modify @[c:\src\quorum\client_app_v2\test\features\execution\models\matrix_scorecard_dto_test.dart] and @[c:\src\quorum\client_app_v2\test\features\execution\models\report_data_v2_dto_test.dart] to remove all deleted fields from mock JSON structures and use valid enum strings.</action>
      <constraint invariant="anti_tdd_trap">Do not patch the domain code if a test fails. Rewrite the mock JSON fixtures to comply with the new Phase 9 architecture.</constraint>
    </step>

    <step id="6" name="QUALITY GATE &amp; COMMIT">
      <action>Run the flutter audit script targeting the modified domain directories:</action>
      <action>`uv run python scripts/flutter_audit_loop.py client_app_v2/lib/features/execution/models client_app_v2/lib/core/models client_app_v2/lib/shared/models --build`</action>
      <constraint invariant="atomic_checkpoint_mandate">If the audit script passes, explicitly instruct the user to atomic commit these frontend DTO changes before proceeding to Phase 4.</constraint>
    </step>
  </execution_protocol>
</system_prompt>
```
