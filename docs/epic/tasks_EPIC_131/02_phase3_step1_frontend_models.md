# Phase 3 Step 3.1: Frontend Models (Cross-Domain Dependency)

**Source**: @[c:\src\quorum\docs\epic\EPIC_131_sdui_layout_unification.md#L343-L390]

This plan satisfies the cross-domain requirement by adding the new SduiBlockDTO variants to the Flutter frontend before the backend begins emitting them.

## Target Files
- @[c:\src\quorum\client_app_v2\lib\shared\models\sdui_block_dto.dart]

```xml
<execution_protocol>
    <constraint invariant="universal_fail_fast">The Fail-Fast Client Firewall requires proactive UI crashes on bad server DTOs.</constraint>
    <constraint invariant="sdui_contract_fracture_prevention">Enforce Cross-Domain DTO Parity.</constraint>
    <constraint invariant="automated_code_generation_mandate">Autonomously execute the generation using the run_command tool.</constraint>
    
    <step id="3.1" name="Add 4 New Variants to SduiBlockDTO">
        <action>Modify @[c:\src\quorum\client_app_v2\lib\shared\models\sdui_block_dto.dart]. Add the following exact imports to the top of the file:
        - `import 'package:client_app/shared/models/i18n_text.dart';`
        - `import 'package:client_app/features/execution/models/matrix_scorecard_dto.dart';`
        </action>
        <action>Add 4 new Freezed union variants (`matrix3d`, `compare2d`, `metrics1d`, and `matrixSummary`). You MUST strictly use the following exact fields and annotations to match the Python backend perfectly:
        - For `matrix3d` (Class: `SduiRadarChartBlock`), `compare2d` (Class: `SduiScatterPlotBlock`), and `metrics1d` (Class: `SduiMetrics1DBlock`), the fields MUST BE:
            - `String? id`
            - `I18nText? title`
            - `I18nText? description`
            - `@Default([]) List<MatrixScorecardRowDto> axes`
            - `@JsonKey(name: 'text_delivery_mode') @Default(TextDeliveryMode.full) TextDeliveryMode textDeliveryMode`
            - `@JsonKey(name: 'synthesis_blocks') List<SduiBlockDTO>? synthesisBlocks`
        - For `matrixSummary` (Class: `SduiMatrixTableBlock`), the fields MUST BE the exact same 6 fields above, PLUS:
            - `@JsonKey(name: 'matrix_column_labels') @Default({}) Map<String, I18nText> matrixColumnLabels`
            - `@JsonKey(name: 'extension_labels') @Default({}) Map<XaiExtensionType, I18nText> extensionLabels`
            - `@JsonKey(name: 'matrix_visible_columns') @Default([]) List<String> matrixVisibleColumns`
        </action>
        <action>Ensure each variant is annotated with `@JsonSerializable(disallowUnrecognizedKeys: true)` and the correct `@FreezedUnionValue('...')` matching the Python discriminator string (e.g., `@FreezedUnionValue('3d_matrix')`, `@FreezedUnionValue('2d_compare')`, `@FreezedUnionValue('1d_metrics')`, `@FreezedUnionValue('matrix_summary')`). Do NOT use the dart constructor names as the union values.</action>
    </step>
    
    <step id="3.2" name="Add Unit Tests for New Variants">
        <action>Modify @[c:\src\quorum\client_app_v2\test\shared\models\sdui_block_dto_test.dart]. Add explicit test blocks for `3d_matrix`, `2d_compare`, `matrix_summary`, and `1d_metrics`.</action>
        <action>For each variant, implement 1 Positive Test (parsing a valid JSON dictionary into the Dart DTO) and 1 Negative Test (asserting that `throwsException` occurs when a field not defined in the schema is provided, verifying the `disallowUnrecognizedKeys` behavior per the anti-happy-path mandate).</action>
    </step>

    <step id="3.8" name="Regenerate Freezed Files">
        <action>Run the `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` command to regenerate the Freezed and JsonSerializable files.</action>
    </step>
</execution_protocol>
```
