# Phase 0: Frontend DTO Parity (Cross-Domain Serialization Mandate)

## Targets
- `@[c:\src\quorum\client_app_v2\lib\features\studio\models\output_profile.dart]`
- `@[c:\src\quorum\client_app_v2\lib\features\execution\models\report_layout_dto.dart]`
- `@[c:\src\quorum\client_app_v2\lib\features\execution\models\synthesis_config_dto.dart]`
- `@[c:\src\quorum\client_app_v2\lib\features\execution\models\report_data_v2_dto.dart]`
- `@[c:\src\quorum\client_app_v2\lib\features\execution\models\global_synthesis_dto.dart]`

```xml
<execution_protocol>
  <constraint invariant="sdui_contract_fracture_prevention">Frontend MUST mirror backend DTO changes identically to avoid disallowUnrecognizedKeys failures.</constraint>
  <constraint invariant="zero_deprecation_mandate">Resolve all typing and syntax errors before completion.</constraint>

  <step id="1_1" name="OutputLayoutBlock and ReportLayoutDto Parity">
    <action>Add `@JsonKey(name: 'matrix_visible_columns') @Default([]) List<String> matrixVisibleColumns,` to `OutputLayoutBlock` (in `output_profile.dart`) and `ReportLayoutDto`.</action>
  </step>

  <step id="1_2" name="SynthesisConfigDto and ReportDataDto Cleanup">
    <action>Remove `matrixVisibleColumns` from `SynthesisConfigDTO`.</action>
    <action>Remove `matrixVisibleColumns` from `ReportDataDto`.</action>
    <demolish>REMOVE: `matrixVisibleColumns` fields from old locations.</demolish>
  </step>

  <step id="1_3" name="GlobalSynthesisDto and OutputProfile Updates">
    <action>Add `@JsonKey(name: 'user_role') String? userRole,` and `@JsonKey(name: 'user_role_justification') String? userRoleJustification,` to `GlobalSynthesisDto`.</action>
    <action>Add `@JsonKey(name: 'user_role_label') I18nText? userRoleLabel,` to `OutputProfile` AND `EmbeddedOutputProfile` in `output_profile.dart`.</action>
  </step>

  <step id="1_4" name="Testing &amp; Quality Gate Plan">
    <action>Run flutter build runner: `uv run python scripts/flutter_audit_loop.py client_app_v2/ --build`.</action>
  </step>
</execution_protocol>
```
