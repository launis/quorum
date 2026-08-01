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
        <action>Modify @[c:\src\quorum\client_app_v2\lib\shared\models\sdui_block_dto.dart]. Add necessary imports (`MatrixScorecardRowDto`, `I18nText`).</action>
        <action>Ensure `@Freezed(unionKey: 'block_type')` is strictly enforcing fail-fast and no `fallbackUnion` is present.</action>
        <action>Add `SduiRadarChartBlock`, `SduiScatterPlotBlock`, `SduiMatrixTableBlock`, and `SduiMetrics1DBlock` variants matching the Python schema exact discriminators.</action>
    </step>
    
    <step id="3.8" name="Regenerate Freezed Files">
        <action>Run the `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build` command to regenerate the Freezed and JsonSerializable files.</action>
    </step>
</execution_protocol>
```
